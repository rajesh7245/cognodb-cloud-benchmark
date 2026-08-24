import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE")

print("URI:", URI)
print("USERNAME:", USERNAME)
print("DATABASE:", DATABASE)
print("PASSWORD LOADED:", PASSWORD is not None)
print("PASSWORD LENGTH:", len(PASSWORD) if PASSWORD else 0)

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

try:
    driver.verify_connectivity()
    print("\nNeo4j server connection successful!")

    with driver.session(database=DATABASE) as session:
        result = session.run(
            "RETURN 'Neo4j query successful!' AS message"
        )

        print(result.single()["message"])

finally:
    driver.close()