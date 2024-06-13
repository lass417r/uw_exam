from bottle import get, template, response, redirect
import requests
from icecream import ic # type: ignore
import x
import json
import random

#####################################
# Route to update crimes from an external server

@get("/update-crimes")
def update_crimes():
    try:
        # Fetch crime data from an external server
        external_response = requests.get("http://lass417r.pythonanywhere.com/crimes-server", params={'token': '1234'})
        if external_response.status_code != 200:
            raise Exception("Failed to fetch crime data")
        crimes = external_response.json()

        # Process and insert crimes and related people
        split_crimes_data_transaction(crimes)

        # Create suspect and witness relationships to crimes
        create_suspect_witness_relationships(crimes)

        # Create friend relationships among people
        create_friend_relationships()

        return ""
    except Exception as e:
        ic(e)  # Log the error for debugging
        response.status = 500
        return f"Error processing crime: {str(e)}"

# Function to process and insert crimes and related people into the database
def split_crimes_data_transaction(crimes):
    try:
        actions = ["function() { const db = require('@arangodb').db;"]
        query_collections = []

        # Loop through each crime and prepare queries for upserting crime and person documents
        for crime in crimes:
            crime_document = {
                "_key": crime['id'],
                "crime_type": crime['crime_type'],
                "crime_severity": crime['crime_severity'],
                "address": crime['address'],
                "report_date": crime['report_date'],
                "latitude": crime['latitude'],
                "longitude": crime['longitude']
            }
            crime_query = """
                UPSERT {_key: @crime._key}
                INSERT @crime
                REPLACE @crime IN crimes
            """
            query_collections.append({"query": crime_query, "bindVars": {"crime": crime_document}})

            # Prepare queries for upserting suspect and witness documents
            for role in ['suspects', 'witnesses']:
                for person in crime.get(role, []):
                    person_document = {
                        "_key": person['cpr_number'],
                        "first_name": person['first_name'],
                        "last_name": person['last_name'],
                        "gender": person['gender'],
                        "age": person['age'],
                        "address": person['address']
                    }
                    person_query = f"""
                        UPSERT {{_key: @person._key}}
                        INSERT @person
                        REPLACE @person IN people
                    """
                    query_collections.append({"query": person_query, "bindVars": {"person": person_document}})

        # Add queries to the transaction
        for query in query_collections:
            actions.append(f"db._query(`{query['query']}`, {json.dumps(query['bindVars'])});")
        actions.append("}")

        # Prepare and execute the transaction
        transaction_js = "\n".join(actions)
        transaction_body = {
            "action": transaction_js,
            "collections": {
                "write": ["crimes", "people"]
            }
        }
        execute_transaction(transaction_body)
    except Exception as e:
        raise Exception(f"Error in split_crimes_data_transaction: {str(e)}")

# Function to create suspect and witness relationships to crimes
def create_suspect_witness_relationships(crimes):
    try:
        actions = ["function() { const db = require('@arangodb').db;"]
        query_collections = []

        # Loop through each crime and prepare queries for upserting relationships
        for crime in crimes:
            crime_id = crime['id']
            for role, edge_collection in [('suspects', 'crimes_committed_by_people'), ('witnesses', 'crimes_witnessed_by_people')]:
                for person in crime.get(role, []):
                    relationship_doc = {
                        "_from": f"people/{person['cpr_number']}",
                        "_to": f"crimes/{crime_id}",
                        "relationship": 'suspect' if role == 'suspects' else 'witness'
                    }
                    relationship_query = f"""
                        UPSERT {{_from: @doc._from, _to: @doc._to, relationship: @doc.relationship}}
                        INSERT @doc
                        REPLACE @doc IN {edge_collection}
                    """
                    query_collections.append({"query": relationship_query, "bindVars": {"doc": relationship_doc}})

        # Add queries to the transaction
        for query in query_collections:
            actions.append(f"db._query(`{query['query']}`, {json.dumps(query['bindVars'])});")
        actions.append("}")

        # Prepare and execute the transaction
        transaction_js = "\n".join(actions)
        transaction_body = {
            "action": transaction_js,
            "collections": {
                "write": ["crimes_committed_by_people", "crimes_witnessed_by_people"]
            }
        }
        execute_transaction(transaction_body)
    except Exception as e:
        raise Exception(f"Error in create_suspect_witness_relationships: {str(e)}")

# Function to create friend relationships among people  
def create_friend_relationships():
    try:
        # Query to get all people IDs
        people_ids_query = {"query": "FOR person IN people RETURN person._id"}
        people_ids_result = x.db(people_ids_query)

        # Check if there's an error in the result
        if 'error' in people_ids_result and people_ids_result['error']:
            raise Exception(f"Database query error: {people_ids_result.get('errorMessage', 'Unknown error')}")

        people_ids = people_ids_result['result']
        actions = ["function() { const db = require('@arangodb').db;"]
        max_friends = 5  # Set a limit for the maximum number of friends per person

        # Loop through each person to create friend relationships
        for person_id in people_ids:
            # Query to get the current number of friends for the person
            current_friends_query = {
                "query": """
                    FOR friend IN people_friends_with_people
                    FILTER friend._from == @person_id
                    RETURN friend._to
                """,
                "bindVars": {"person_id": person_id}
            }
            current_friends_result = x.db(current_friends_query)

            if 'error' in current_friends_result and current_friends_result['error']:
                raise Exception(f"Database query error: {current_friends_result.get('errorMessage', 'Unknown error')}")

            current_friends = current_friends_result['result']
            num_current_friends = len(current_friends)
            num_new_friends = random.randint(0, 3)
            num_friends_to_add = max(0, min(num_new_friends, max_friends - num_current_friends))

            if num_friends_to_add > 0:
                possible_friends = [id for id in people_ids if id != person_id and id not in current_friends]
                friends = random.sample(possible_friends, min(num_friends_to_add, len(possible_friends)))
                for friend_id in friends:
                    friend_rel_doc = {"_from": person_id, "_to": friend_id, "relationship": "Friend"}
                    friend_query = f"""
                        UPSERT {{_from: @doc._from, _to: @doc._to, relationship: @doc.relationship}}
                        INSERT @doc
                        REPLACE @doc IN people_friends_with_people
                    """
                    actions.append(f"db._query(`{friend_query}`, {json.dumps({'doc': friend_rel_doc})});")

        actions.append("}")
        # Prepare and execute the transaction
        transaction_js = "\n".join(actions)
        transaction_body = {
            "action": transaction_js,
            "collections": {
                "write": ["people_friends_with_people"]
            }
        }
        execute_transaction(transaction_body)
    except Exception as e:
        raise Exception(f"Failed to create friend relationships: {str(e)}")

# Function to execute a transaction in the database
def execute_transaction(transaction_body):
    try:
        result = x.db(transaction_body, type="transaction")
        if result.get('error', False):
            raise Exception("Transaction failed: " + result.get('errorMessage', 'Unknown error'))
    except Exception as e:
        raise Exception(f"Database operation failed: {str(e)}")