import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

uri = os.getenv("MEMGRAPH_URL")
username = os.getenv("MEMGRAPH_USERNAME")
password = os.getenv("MEMGRAPH_PASSWORD")

print("=== MEMGRAPH CONNECTION TEST ===")
print("URI:", uri)
print("Username:", username)

if not uri or not username or not password:
    raise RuntimeError(
        "MEMGRAPH_URL, MEMGRAPH_USERNAME or MEMGRAPH_PASSWORD "
        "is missing from .env"
    )

driver = GraphDatabase.driver(
    uri,
    auth=(username, password)
)

try:
    driver.verify_connectivity()
    print("Connection: SUCCESS")

    with driver.session() as session:
        result = session.run("RETURN 1 AS test")
        print("Query result:", result.single()["test"])

    print("Memgraph connection is working.")

finally:
    driver.close()