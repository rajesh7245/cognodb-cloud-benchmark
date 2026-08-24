import os
import time

from dotenv import load_dotenv
from falkordb import FalkorDB


load_dotenv()


HOST = os.getenv("FALKORDB_HOST")
PORT = int(os.getenv("FALKORDB_PORT"))
USERNAME = os.getenv("FALKORDB_USERNAME")
PASSWORD = os.getenv("FALKORDB_PASSWORD")

DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "Wiki-Vote.txt"
)


def load_data():

    print("Connecting to FalkorDB...")

    db = FalkorDB(
        host=HOST,
        port=PORT,
        username=USERNAME,
        password=PASSWORD
    )

    graph = db.select_graph("wiki_vote")

    print("Connected to FalkorDB.")
    print("Loading Wiki-Vote dataset...")

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

    # Clear the graph before loading
    graph.query("""
        MATCH (n)
        DETACH DELETE n
    """)

    # Load data in batches
    batch_size = 500

    for i in range(0, len(edges), batch_size):

        batch = edges[i:i + batch_size]

        query = """
        UNWIND $rows AS row

        MERGE (a:User {id: row.source})
        MERGE (b:User {id: row.target})

        MERGE (a)-[:VOTED]->(b)
        """

        graph.query(
            query,
            params={"rows": batch}
        )

        print(
            f"Loaded {min(i + batch_size, len(edges))}"
            f"/{len(edges)} edges"
        )

    end_time = time.perf_counter()

    elapsed = end_time - start_time

    print()
    print("===================================")
    print("FalkorDB data loading completed!")
    print("===================================")
    print(f"Total edges: {len(edges)}")
    print(f"Load time: {elapsed:.2f} seconds")

    if elapsed > 0:
        print(
            f"Throughput: "
            f"{len(edges) / elapsed:.2f} edges/second"
        )


if __name__ == "__main__":
    load_data()