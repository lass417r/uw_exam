from bottle import get, template
from icecream import ic 
import x

#######################################
# Define a route to the index page

@get("/")
def index():
    query = {
        "query": """
        FOR crime IN crimes
            LET suspects = (
                FOR suspect, edge IN 1..1 INBOUND crime._id crimes_committed_by_people
                RETURN suspect
            )
            LET witnesses = (
                FOR witness, edge IN 1..1 INBOUND crime._id crimes_witnessed_by_people
                RETURN witness
            )
            RETURN {crime, suspects, witnesses}
        """
    }
    try:
        crimes_and_suspects = x.db(query)
        if 'error' in crimes_and_suspects and crimes_and_suspects['error']:
            raise Exception(f"Database query error: {crimes_and_suspects.get('errorMessage', 'Unknown error')}")
        return template("index", crimes=crimes_and_suspects["result"], show_all="all")
    except Exception as e:
        ic(e)
        return f"Error fetching crimes: {str(e)}"
    
#######################################