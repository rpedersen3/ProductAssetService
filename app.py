# Importing Flask to be our HTTP server
from flask import Flask

# Importing GraphQLView
from graphql_server.flask import GraphQLView
from api_schema import schema

# Importing this view so Flask can delegate to Graphene
app=Flask(__name__)

print("add app routes")
# Adding a single route for /
@app.route("/")
def young_ben():
    return "go to http://127.0.0.1:5000/graphql"

print("add url rule")

# Adding another route for GraphQL at /graphql
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True
    )
)

print("done")
