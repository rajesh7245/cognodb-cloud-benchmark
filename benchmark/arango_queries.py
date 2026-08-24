import os
import time
import statistics
import random

from dotenv import load_dotenv
from arango import ArangoClient


load_dotenv()

ARANGO_URL = os.getenv("ARANGO_URL")
ARANGO_USERNAME = os.getenv("ARANGO_USERNAME")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD")
ARANGO_DATABASE = os.getenv("ARANGO_DATABASE", "_system")

GRAPH_NAME = "wiki_vote_graph"
VERTEX_COLLECTION = "wiki_nodes"
EDGE_COLLECTION = "wiki_edges"


client = ArangoClient(hosts=ARANGO_URL)

db = client.db(
    ARANGO_DATABASE,
    username=ARANGO_USERNAME,
    password=ARANGO_PASSWORD
)


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def percentile(values, percentile):
    values = sorted(values)

    index = int((percentile / 100) * (len(values) - 1))

    return values[index]


def benchmark(name, query, bind_vars=None, runs=50):

    times = []

    for _ in range(runs):

        start = time.perf_counter()

        cursor = db.aql.execute(
            query,
            bind_vars=bind_vars or {}
        )

        list(cursor)

        end = time.perf_counter()

        times.append((end - start) * 1000)

    p50 = statistics.median(times)
    p95 = percentile(times, 95)

    print(
        f"{name}: "
        f"p50={p50:.3f} ms, "
        f"p95={p95:.3f} ms"
    )

    return p50, p95


# --------------------------------------------------
# VERIFY DATABASE
# --------------------------------------------------

print()
print("=== ARANGODB TRAVERSAL BENCHMARK ===")

print("Nodes:", db.collection(VERTEX_COLLECTION).count())
print("Relationships:", db.collection(EDGE_COLLECTION).count())


# --------------------------------------------------
# 1-HOP
# --------------------------------------------------

query_1hop = f"""
FOR v IN 1..1 OUTBOUND @start GRAPH '{GRAPH_NAME}'
    RETURN v._key
"""

benchmark(
    "1-hop",
    query_1hop,
    {"start": f"{VERTEX_COLLECTION}/3"},
)


# --------------------------------------------------
# 2-HOP
# --------------------------------------------------

query_2hop = f"""
FOR v IN 2..2 OUTBOUND @start GRAPH '{GRAPH_NAME}'
    RETURN v._key
"""

benchmark(
    "2-hop",
    query_2hop,
    {"start": f"{VERTEX_COLLECTION}/3"},
)


# --------------------------------------------------
# 3-HOP
# --------------------------------------------------

query_3hop = f"""
FOR v IN 3..3 OUTBOUND @start GRAPH '{GRAPH_NAME}'
    RETURN v._key
"""

benchmark(
    "3-hop",
    query_3hop,
    {"start": f"{VERTEX_COLLECTION}/3"},
)


# --------------------------------------------------
# POINT LOOKUP
# --------------------------------------------------

query_point = f"""
FOR v IN {VERTEX_COLLECTION}
    FILTER v._key == @key
    RETURN v
"""

benchmark(
    "Point lookup",
    query_point,
    {"key": "3"},
)


# --------------------------------------------------
# FILTERED LOOKUP
# --------------------------------------------------

query_filtered = f"""
FOR v IN {VERTEX_COLLECTION}
    FILTER TO_NUMBER(v._key) >= @minimum
    LIMIT 1
    RETURN v
"""

benchmark(
    "Filtered lookup",
    query_filtered,
    {"minimum": 1000},
)


# --------------------------------------------------
# AGGREGATION
# --------------------------------------------------

query_aggregation = f"""
FOR e IN {EDGE_COLLECTION}
    COLLECT source = e._from
    WITH COUNT INTO edge_count
    SORT edge_count DESC
    LIMIT 10
    RETURN {{
        source: source,
        edges: edge_count
    }}
"""

benchmark(
    "Aggregation",
    query_aggregation,
)


# --------------------------------------------------
# MIXED READ/WRITE WORKLOAD
# --------------------------------------------------

print()
print("=== ARANGODB MIXED READ/WRITE WORKLOAD ===")

TEMP_COLLECTION = "benchmark_temp"

if not db.has_collection(TEMP_COLLECTION):
    db.create_collection(TEMP_COLLECTION)

operations = 1000
clients = 10
operations_per_client = operations // clients


def worker(client_id):
    thread_client = ArangoClient(hosts=ARANGO_URL)

    thread_db = thread_client.db(
        ARANGO_DATABASE,
        username=ARANGO_USERNAME,
        password=ARANGO_PASSWORD
    )

    temp = thread_db.collection(TEMP_COLLECTION)

    for i in range(operations_per_client):

        key = f"benchmark_{client_id}_{i}"

        # WRITE
        temp.insert(
            {
                "_key": key,
                "value": i
            },
            overwrite=True
        )

        # READ
        document = temp.get(key)

        if document is None:
            raise RuntimeError("Read-after-write failed")

        # DELETE
        temp.delete(key)


start_time = time.perf_counter()

from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=clients) as executor:

    futures = []

    for client_id in range(clients):
        futures.append(
            executor.submit(worker, client_id)
        )

    for future in futures:
        future.result()


end_time = time.perf_counter()

elapsed = end_time - start_time

throughput = operations / elapsed

print(f"Clients: {clients}")
print(f"Operations: {operations}")
print(f"Time: {elapsed:.2f} seconds")
print(f"Throughput: {throughput:.2f} operations/second")


# --------------------------------------------------
# CLEANUP
# --------------------------------------------------

if db.has_collection(TEMP_COLLECTION):

    db.delete_collection(TEMP_COLLECTION)


print()
print("=== ARANGODB BENCHMARK COMPLETE ===")