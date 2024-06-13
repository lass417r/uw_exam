from bottle import get, template, response
from icecream import ic
import x
import json
 
#######################################
# Define a route to get a specific crime by key
 
@get('/crimes/<key>')
def get_crime(key):
    query = {
        "query": """
        FOR crime IN crimes
        FILTER crime._key == @key
        LET suspects = (
            FOR suspect, edge IN 1..1 INBOUND crime._id crimes_committed_by_people
            LET friends = (
                FOR friend, friendship IN 1..1 OUTBOUND suspect._id people_friends_with_people
                RETURN friend
            )
            RETURN {suspect: suspect, friends}
        )
        LET witnesses = (
            FOR witness, edge IN 1..1 INBOUND crime._id crimes_witnessed_by_people
            LET friends = (
                FOR friend, friendship IN 1..1 OUTBOUND witness._id people_friends_with_people
                RETURN friend
            )
            RETURN {witness: witness, friends}
        )
    RETURN {crime: crime, suspects: suspects, witnesses: witnesses}
 
        """,
        "bindVars": {"key": key}
    }
    result = x.db(query)
    data = result['result']
    ic(data)
 
    if data:
        crime = data[0]
    else:
        response.content_type = 'application/json'
        return json.dumps({"error": "No crime found"})
 
    return template("_crime", crime=crime)

#######################################