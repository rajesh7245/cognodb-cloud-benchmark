import os

from dotenv import load_dotenv
from falkordb import FalkorDB


load_dotenv()

host = os.getenv("FALKORDB_HOST")
port = int(os.getenv("FALKORDB_PORT"))
username = os.getenv("FALKORDB_USERNAME")
password = os.getenv("FALKORDB_PASSWORD")


db = FalkorDB(
    host=host,
    port=port,
    username=username,
    password=password
)

graph = db.select_graph("wiki_vote")

print("Checking FalkorDB data...")


result = graph.query("""
MATCH (u:User)
RETURN count(u) AS nodes
""")

for record in result.result_set:
    print("User nodes:", record[0])


result = graph.query("""
MATCH ()-[r:VOTED]->()
RETURN count(r) AS relationships
""")

for record in result.result_set:
    print("VOTED relationships:", record[0])


print("FalkorDB data verification completed!")