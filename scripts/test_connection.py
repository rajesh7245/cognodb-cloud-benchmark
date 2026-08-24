import os
from dotenv import load_dotenv
from falkordb import FalkorDB

load_dotenv()

host = os.getenv("FALKORDB_HOST")
port = int(os.getenv("FALKORDB_PORT"))
username = os.getenv("FALKORDB_USERNAME")
password = os.getenv("FALKORDB_PASSWORD")

print("Connecting to FalkorDB...")

db = FalkorDB(
    host=host,
    port=port,
    username=username,
    password=password
)

graph = db.select_graph("test_connection")

result = graph.query("""
CREATE (:TestNode {message: 'Hello FalkorDB'})
RETURN 'Connection successful' AS message
""")

for record in result.result_set:
    print(record)

print("Connected successfully!")