from bottle import get, template, response
from icecream import ic
import x
import json

@get('/get_common_connections')
def get_common_connections():
    query = {
        "query": """
            LET all_connections = (
                FOR crime IN crimes
                    LET suspects = (
                        FOR suspect, edge IN 1..1 INBOUND crime._id crimes_committed_by_people
                        RETURN suspect
                    )
                    LET witnesses = (
                        FOR witness, edge IN 1..1 INBOUND crime._id crimes_witnessed_by_people
                        RETURN witness
                    )
                    LET common_connections = (
                        FOR i IN 0..LENGTH(suspects)-1
                        FOR j IN i+1..LENGTH(suspects)
                        LET suspect1 = suspects[i]
                        LET suspect2 = suspects[j]
                        FILTER suspect1._id != suspect2._id
                        LET suspect1_friends = (
                            FOR friend, edge IN 1..1 OUTBOUND suspect1._id people_friends_with_people
                            RETURN friend
                        )
                        LET suspect2_friends = (
                            FOR friend, edge IN 1..1 OUTBOUND suspect2._id people_friends_with_people
                            RETURN friend
                        )
                        LET common_friends = INTERSECTION(suspect1_friends[*]._key, suspect2_friends[*]._key)
                        FILTER LENGTH(common_friends) > 0
                        LET common_crimes = (
                            FOR c IN crimes
                            FILTER c._id != crime._id
                            LET c_suspects = (
                                FOR s, e IN 1..1 INBOUND c._id crimes_committed_by_people
                                RETURN s._id
                            )
                            FILTER suspect1._id IN c_suspects AND suspect2._id IN c_suspects
                            RETURN c
                        )
                        RETURN {
                            crime: crime,
                            suspect1: suspect1,
                            suspect2: suspect2,
                            relationship: "suspect-suspect",
                            common_friends: common_friends,
                            common_crimes: common_crimes
                        }
                    )
                    LET witness_connections = (
                        FOR suspect IN suspects
                        FOR witness IN witnesses
                        LET suspect_friends = (
                            FOR friend, edge IN 1..1 OUTBOUND suspect._id people_friends_with_people
                            RETURN friend
                        )
                        LET witness_friends = (
                            FOR friend, edge IN 1..1 OUTBOUND witness._id people_friends_with_people
                            RETURN friend
                        )
                        LET common_friends = INTERSECTION(suspect_friends[*]._key, witness_friends[*]._key)
                        FILTER LENGTH(common_friends) > 0
                        RETURN {
                            crime: crime,
                            suspect: suspect,
                            witness: witness,
                            relationship: "suspect-witness",
                            common_friends: common_friends,
                            common_crimes: []
                        }
                    )
                    RETURN UNION(common_connections, witness_connections)
            )
            RETURN FLATTEN(all_connections)
        """
    }

    result = x.db(query)
    data = result['result']
    ic(data)  # Debugging output to inspect the data structure

    # Flatten the nested list and ensure it's a list of dictionaries
    crimes = [item for sublist in data for item in sublist] if isinstance(data, list) and data else []

    # Print the final structure of the crimes list
    print("Crimes List:", json.dumps(crimes, indent=2))

    if not crimes:
        response.content_type = 'application/json'
        return json.dumps({"error": "No crime found"})

    return template("_common-connections", result=crimes)
