from bottle import get, template, response, request
import x

#######################################
# Define a route to all crimes or filtered crimes

@get('/filtered-crimes')
def filtered_crimes():
    # Retrieve query parameters for crime type and severity from the request, defaulting to 'all' if not provided
    crime_type = request.query.type or 'all'
    crime_severity = request.query.severity or 'all'
    
    # Initialize filters and bind variables for the database query

    filters = [] # List of filters to apply to the query
    bind_vars = {} # Dictionary of bind variables for the query

    # Add filter for crime type if it's not 'all'
    if crime_type != 'all':
        filters.append("crime.crime_type == @type")
        bind_vars["type"] = crime_type

    # Add filter for crime severity if it's not 'all'
    if crime_severity != 'all':
        filters.append("crime.crime_severity == @severity")
        bind_vars["severity"] = crime_severity

    # Combine filters into a single query string
    filter_query = " AND ".join(filters)
    
    # Construct the database query based on whether any filters are applied
    if filter_query:
        query = {
            "query": f"""
            FOR crime IN crimes
                FILTER {filter_query}
                LET suspects = (
                    FOR suspect, edge IN 1..1 INBOUND crime._id crimes_committed_by_people
                    RETURN suspect
                )
                LET witnesses = (
                    FOR witness, edge IN 1..1 INBOUND crime._id crimes_witnessed_by_people
                    RETURN witness
                )
                RETURN {{crime, suspects, witnesses}}
            """,
            "bindVars": bind_vars
        }
    else:
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
    
    # Execute the query using the database connection
    crimes_and_suspects = x.db(query)
    
    # Determine if the request is for showing all crimes (no filters applied)
    show_all = (crime_type == 'all' and crime_severity == 'all')
    
    # Set the response content type to JSON
    response.content_type = 'application/json'
    
    # Render the template with the query results and return the response
    return template("_crimes-list", crimes=crimes_and_suspects["result"], show_all=show_all, crime_type=crime_type, crime_severity=crime_severity)

#######################################