from bottle import get
import x

########################## DANGER ZONE ##########################
# Define a route to truncate all collections in the database

@get("/truncate-collections")
def truncate_collections():
    try:
        # Attempt to truncate the collections within a transaction
        truncate_transaction()
        return "Collections truncated successfully!"
    except Exception as e:
        # Return an error message if truncation fails
        return f"Error truncating collections: {str(e)}"

def truncate_transaction():
    # JavaScript actions to truncate each collection
    actions = [
        "function() { const db = require('@arangodb').db;",
        "db.crimes.truncate();",
        "db.people.truncate();",
        "db.people_friends_with_people.truncate();",
        "db.crimes_committed_by_people.truncate();",
        "db.crimes_witnessed_by_people.truncate();",
        "}"
    ]

    # Join the actions into a single JavaScript function string
    transaction_js = "\n".join(actions)
    
    # Define the transaction body with collections to be written to
    transaction_body = {
        "action": transaction_js,
        "collections": {
            "write": [
                "crimes", 
                "people", 
                "people_friends_with_people", 
                "crimes_committed_by_people", 
                "crimes_witnessed_by_people"
            ]
        }
    }
    
    # Execute the constructed transaction
    execute_transaction(transaction_body)

def execute_transaction(transaction_body):
    try:
        # Perform the transaction using the database connection
        result = x.db(transaction_body, type="transaction")
        
        # Check for errors in the transaction result
        if result.get('error', False):
            raise Exception("Transaction failed: " + result.get('errorMessage', 'Unknown error'))
    except Exception as e:
        # Raise an exception if the database operation fails
        raise Exception(f"Database operation failed: {str(e)}")
    
################################################################