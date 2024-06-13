from bottle import get, response
import x
import json

################################
# Define a minimal route to get all crimes to be used in javascript to show markers on the map
 
@get('/api/crimes')
def get_crimes():
    # AQL query to retrieve crimes
    query = {
        "query": """
        FOR crime IN crimes
            RETURN {crime}
        """
    }

    #ic(crimes_and_suspects)

    # Execute the query
    crimes= x.db(query)

    # Make sure to set the appropriate content type
    response.content_type = 'application/json'

    # Convert the results to JSON
    return json.dumps(crimes['result'])