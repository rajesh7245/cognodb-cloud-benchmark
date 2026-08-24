import os
from pathlib import Path

from dotenv import load_dotenv
from arango import ArangoClient


# --------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

load_dotenv()

ARANGO_URL = os.getenv("ARANGO_URL")
ARANGO_USERNAME = os.getenv("ARANGO_USERNAME")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD")
ARANGO_DATABASE = os.getenv("ARANGO_DATABASE", "_system")


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "Wiki-Vote.txt"

VERTEX_COLLECTION = "wiki_nodes"
EDGE_COLLECTION = "wiki_edges"
GRAPH_NAME = "wiki_vote_graph"

BATCH_SIZE = 5000


# --------------------------------------------------
# VALIDATE ENVIRONMENT
# --------------------------------------------------

if not ARANGO_URL:
    raise RuntimeError("ARANGO_URL is missing from .env")

if not ARANGO_USERNAME:
    raise RuntimeError("ARANGO_USERNAME is missing from .env")

if not ARANGO_PASSWORD:
    raise RuntimeError("ARANGO_PASSWORD is missing from .env")

if not DATA_FILE.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")


# --------------------------------------------------
# CONNECT TO ARANGODB
# --------------------------------------------------

print("=== ARANGODB DATA LOADER ===")
print(f"URL: {ARANGO_URL}")
print(f"Database: {ARANGO_DATABASE}")
print(f"Dataset: {DATA_FILE}")

client = ArangoClient(hosts=ARANGO_URL)

db = client.db(
    ARANGO_DATABASE,
    username=ARANGO_USERNAME,
    password=ARANGO_PASSWORD
)

print("Connection: SUCCESS")


# --------------------------------------------------
# CREATE COLLECTIONS
# --------------------------------------------------

if not db.has_collection(VERTEX_COLLECTION):
    print(f"Creating vertex collection: {VERTEX_COLLECTION}")
    db.create_collection(VERTEX_COLLECTION)

if not db.has_collection(EDGE_COLLECTION):
    print(f"Creating edge collection: {EDGE_COLLECTION}")
    db.create_collection(
        EDGE_COLLECTION,
        edge=True
    )


vertices = db.collection(VERTEX_COLLECTION)
edges = db.collection(EDGE_COLLECTION)


# --------------------------------------------------
# CREATE GRAPH
# --------------------------------------------------

if not db.has_graph(GRAPH_NAME):
    print(f"Creating graph: {GRAPH_NAME}")

    db.create_graph(
        GRAPH_NAME,
        edge_definitions=[
            {
                "edge_collection": EDGE_COLLECTION,
                "from_vertex_collections": [VERTEX_COLLECTION],
                "to_vertex_collections": [VERTEX_COLLECTION],
            }
        ],
    )

else:
    print(f"Graph already exists: {GRAPH_NAME}")


# --------------------------------------------------
# READ WIKI-VOTE DATASET
# --------------------------------------------------

print()
print("Reading Wiki-Vote dataset...")

node_ids = set()
edge_pairs = []

with open(DATA_FILE, "r", encoding="utf-8") as file:

    for line in file:

        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Skip comment/header lines
        if line.startswith("#"):
            continue

        parts = line.split()

        if len(parts) < 2:
            continue

        source = parts[0]
        target = parts[1]

        node_ids.add(source)
        node_ids.add(target)

        edge_pairs.append((source, target))


print(f"Nodes discovered: {len(node_ids)}")
print(f"Relationships discovered: {len(edge_pairs)}")


# --------------------------------------------------
# INSERT NODES
# --------------------------------------------------

print()
print("Loading nodes...")

node_documents = []

for node_id in sorted(node_ids, key=lambda x: int(x)):

    node_documents.append(
        {
            "_key": node_id
        }
    )

    if len(node_documents) >= BATCH_SIZE:

        vertices.insert_many(
            node_documents,
            overwrite=True,
            raise_on_document_error=True
        )

        print(f"Inserted nodes: {len(node_documents)}")

        node_documents.clear()


# Insert remaining nodes

if node_documents:

    vertices.insert_many(
        node_documents,
        overwrite=True,
        raise_on_document_error=True
    )

    print(f"Inserted final nodes: {len(node_documents)}")


# --------------------------------------------------
# INSERT EDGES
# --------------------------------------------------

print()
print("Loading relationships...")

edge_documents = []

for source, target in edge_pairs:

    edge_documents.append(
        {
            "_from": f"{VERTEX_COLLECTION}/{source}",
            "_to": f"{VERTEX_COLLECTION}/{target}"
        }
    )

    if len(edge_documents) >= BATCH_SIZE:

        edges.insert_many(
            edge_documents,
            raise_on_document_error=True
        )

        print(f"Inserted relationships: {len(edge_documents)}")

        edge_documents.clear()


# Insert remaining edges

if edge_documents:

    edges.insert_many(
        edge_documents,
        raise_on_document_error=True
    )

    print(f"Inserted final relationships: {len(edge_documents)}")


# --------------------------------------------------
# VERIFY COUNTS
# --------------------------------------------------

print()
print("=== VERIFYING ARANGODB DATA ===")

node_count = vertices.count()
edge_count = edges.count()

print(f"ArangoDB nodes: {node_count}")
print(f"ArangoDB relationships: {edge_count}")


# --------------------------------------------------
# FINAL RESULT
# --------------------------------------------------

print()
print("=== ARANGODB DATA LOAD COMPLETE ===")

if node_count == 7115 and edge_count == 103689:

    print("Dataset verification: SUCCESS")
    print("Wiki-Vote dataset loaded correctly.")

else:

    print("Dataset verification: CHECK REQUIRED")
    print(
        f"Expected 7115 nodes / 103689 relationships, "
        f"but found {node_count} / {edge_count}"
    )