from bottle import get, static_file
 
#######################################
import routes.index 
import routes.get_crime
import routes.get_crime_cpr
import routes.truncate_collections
import routes.api_crimes
import routes.update_crimes
import routes.filtered_crimes

#import routes.get_common_connections
 
######################################
 
""" @route('<any:path>', method='OPTIONS')
def handle_options(path):
    # Handle CORS preflight requests
    # Allow requests from any origin
    response.headers['Access-Control-Allow-Origin'] = '*'
    # Allow specific HTTP methods
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
    # Allow specific headers in the actual request
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token' """
    
################# STATIC FILES ######################
 
@get("/app.css")
def _():
    return static_file("app.css", ".")

#####################################################
 
@get("/app.js")
def _():
    return static_file("app.js", ".")
 
#####################################################
 
@get("/mixhtml.js")
def _():
    return static_file("mixhtml.js", ".")
 
#######################################