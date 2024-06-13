from bottle import get, template, response
from icecream import ic
import x
import json

#######################################
# Define a route to get crimes by a person's CPR number/key

@get('/get_crimes_cpr/<key>')
def get_crime_cpr(key):
    # Define the AQL query to fetch the person, their friends, and their related crimes
    query = {
        "query": """
            LET person = FIRST(FOR p IN people FILTER p._key == @key RETURN p)
                LET person_friends = (
                    FOR friend, friendship_edge IN 1..1 OUTBOUND person._id people_friends_with_people
                    RETURN friend
                )
            LET crimes_committed = (
                FOR crime, crime_edge IN 1..1 OUTBOUND person._id crimes_committed_by_people
                LET suspects = (
                    FOR suspect, suspect_edge IN 1..1 INBOUND crime._id crimes_committed_by_people
                    LET friends = (
                        FOR friend, friendship_edge IN 1..1 OUTBOUND suspect._id people_friends_with_people
                        RETURN friend
                    )
                    RETURN {suspect: suspect, friends}
                )
                LET witnesses = (
                    FOR witness, witness_edge IN 1..1 INBOUND crime._id crimes_witnessed_by_people
                    LET friends = (
                        FOR friend, friendship_edge IN 1..1 OUTBOUND witness._id people_friends_with_people
                        RETURN friend
                    )
                    RETURN {witness: witness, friends}
                )
                RETURN {crime: crime, suspects: suspects, witnesses: witnesses}
            )
            RETURN {person: person, friends: person_friends, crimes_committed: crimes_committed}
        """,
        "bindVars": {"key": key}
    }

    # Execute the query against the database
    result = x.db(query)
    data = result['result']
    ic(data)  # Debugging: log the data using icecream

    # Check if data is returned
    if data:
        crimes = data
    else:
        # Set the response content type to JSON and return an error message
        response.content_type = 'application/json'
        return json.dumps({"error": "No crime found"})

    # Return the result rendered using the '_crimes-list-cpr' template
    return template("_crimes-list-cpr", result=crimes)

#######################################