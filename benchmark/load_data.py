import os
import time

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

DATASET_PATH = "data/Wiki-Vote.txt"

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE")


def load_data():
    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    edges = []

    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            parts = line.split()

            if len(parts) != 2:
                continue

            source = int(parts[0])
            target = int(parts[1])

            edges.append({
                "source": source,
                "target": target
            })

    print(f"Loaded {len(edges)} edges from dataset.")

    start_time = time.perf_counter()

    with driver.session(database=DATABASE) as session:

        session.run(
            "MATCH (n) DETACH DELETE n"
        ).consume()

        for i in range(0, len(edges), 500):
            batch = edges[i:i + 500]

            session.run(
                """
                UNWIND $rows AS row
                MERGE (a:User {id: row.source})
                MERGE (b:User {id: row.target})
                MERGE (a)-[:VOTED]->(b)
                """,
                rows=batch
            ).consume()

    end_time = time.perf_counter()

    elapsed = end_time - start_time

    print(f"Load time: {elapsed:.2f} seconds")
    print(f"Relationships loaded: {len(edges)}")

    if elapsed > 0:
        print(f"Relationships/second: {len(edges) / elapsed:.2f}")

    driver.close()


if __name__ == "__main__":
    load_data()