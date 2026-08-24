# CognoDB Cloud Benchmark

Reproducible benchmarking of CognoDB Cloud against Neo4j, Memgraph, ArangoDB, and FalkorDB using the Wiki-Vote graph dataset.

## Dataset

Dataset: Wiki-Vote

Nodes: 7,115

Relationships: 103,689

The same dataset and benchmark workload structure were used across all five databases.

## Benchmark Workloads

The benchmark measures:

- 1-hop graph traversal
- 2-hop graph traversal
- 3-hop graph traversal
- Point lookup
- Filtered lookup
- Aggregation
- Mixed read/write workload

Latency is reported using p50 and p95 values.

The mixed read/write workload uses:

- Clients: 10
- Operations: 1000

---

## Benchmark Results

### Neo4j

| Workload | p50 | p95 |
|---|---:|---:|
| 1-hop traversal | 102.469 ms | 122.273 ms |
| 2-hop traversal | 102.464 ms | 138.746 ms |
| 3-hop traversal | 102.405 ms | 144.347 ms |
| Point lookup | 102.357 ms | 104.512 ms |
| Filtered lookup | 102.576 ms | 205.677 ms |
| Aggregation | 102.619 ms | 205.006 ms |

Mixed read/write workload:

- Clients: 10
- Operations: 1000
- Time: 8.16 seconds
- Throughput: 122.51 operations/second

Neo4j load time: 273.92 seconds.

Neo4j relationships/second during loading: 378.53.

---

### Memgraph

| Workload | p50 | p95 |
|---|---:|---:|
| 1-hop traversal | 148.636 ms | 198.708 ms |
| 2-hop traversal | 147.271 ms | 161.373 ms |
| 3-hop traversal | 147.275 ms | 155.367 ms |
| Point lookup | 146.769 ms | 151.711 ms |
| Filtered lookup | 149.490 ms | 153.638 ms |
| Aggregation | 146.076 ms | 147.369 ms |

Mixed read/write workload:

- Clients: 10
- Operations: 1000
- Time: 15.70 seconds
- Throughput: 63.68 operations/second

---

### CognoDB

| Workload | p50 | p95 |
|---|---:|---:|
| 1-hop traversal | 307.896 ms | 409.606 ms |
| 2-hop traversal | 307.464 ms | 491.078 ms |
| 3-hop traversal | 308.227 ms | 620.458 ms |
| Point lookup | 307.650 ms | 410.608 ms |
| Filtered lookup | 307.442 ms | 411.327 ms |
| Aggregation | 376.017 ms | 452.646 ms |

Mixed read/write workload:

- Clients: 10
- Operations: 1000
- Time: 35.89 seconds
- Throughput: 27.86 operations/second

---

### ArangoDB

| Workload | p50 | p95 |
|---|---:|---:|
| 1-hop traversal | 306.736 ms | 310.177 ms |
| 2-hop traversal | 308.217 ms | 510.578 ms |
| 3-hop traversal | 7685.703 ms | 8297.400 ms |
| Point lookup | 307.112 ms | 393.173 ms |
| Filtered lookup | 305.879 ms | 448.861 ms |
| Aggregation | 423.526 ms | 714.337 ms |

Mixed read/write workload:

- Clients: 10
- Operations: 1000
- Time: 99.97 seconds
- Throughput: 10.00 operations/second

ArangoDB load time was not measured as part of the benchmark.

---

### FalkorDB

| Workload | p50 | p95 |
|---|---:|---:|
| 1-hop traversal | 17.012 ms | 50.925 ms |
| 2-hop traversal | 17.388 ms | 19.185 ms |
| 3-hop traversal | 17.049 ms | 17.664 ms |
| Point lookup | 16.828 ms | 85.482 ms |
| Filtered lookup | 17.148 ms | 86.224 ms |
| Aggregation | 102.817 ms | 204.899 ms |

Mixed read/write workload:

- Clients: 10
- Operations: 1000
- Time: 4.08 seconds
- Throughput: 245.33 operations/second

FalkorDB load time: 350.40 seconds.

FalkorDB relationships/second during loading: 295.91.

---

## Overall Comparison

| Database | 1-hop p50 | 2-hop p50 | 3-hop p50 | Point lookup p50 | Mixed workload |
|---|---:|---:|---:|---:|---:|
| Neo4j | 102.469 ms | 102.464 ms | 102.405 ms | 102.357 ms | 122.51 ops/s |
| Memgraph | 148.636 ms | 147.271 ms | 147.275 ms | 146.769 ms | 63.68 ops/s |
| CognoDB | 307.896 ms | 307.464 ms | 308.227 ms | 307.650 ms | 27.86 ops/s |
| ArangoDB | 306.736 ms | 308.217 ms | 7685.703 ms | 307.112 ms | 10.00 ops/s |
| FalkorDB | 17.012 ms | 17.388 ms | 17.049 ms | 16.828 ms | 245.33 ops/s |

---

## Observations

Based on the measured benchmark results:

- FalkorDB produced the lowest measured p50 latency across the tested traversal workloads.
- FalkorDB produced the lowest measured p50 latency for point lookup.
- FalkorDB achieved the highest mixed read/write throughput at 245.33 operations/second in this benchmark.
- Neo4j produced lower latency than Memgraph, CognoDB, and ArangoDB in the measured workloads.
- Memgraph was the second fastest database in the measured traversal and lookup workloads after FalkorDB.
- CognoDB showed similar latency to ArangoDB for 1-hop, 2-hop, and lookup workloads.
- ArangoDB showed a significantly higher 3-hop traversal latency in this benchmark.
- Neo4j achieved 122.51 operations/second in the mixed read/write workload.
- Memgraph achieved 63.68 operations/second.
- CognoDB achieved 27.86 operations/second.
- ArangoDB achieved 10.00 operations/second.
- FalkorDB achieved 245.33 operations/second.

These observations are specific to this benchmark configuration, dataset, workload implementation, and test environment.

---

## FalkorDB Load Performance

FalkorDB loaded the complete Wiki-Vote dataset containing 103,689 relationships.

| Metric | Result |
|---|---:|
| Nodes | 7,115 |
| Relationships | 103,689 |
| Load time | 350.40 seconds |
| Loading throughput | 295.91 relationships/second |

The dataset was successfully verified after loading:

- User nodes: 7,115
- VOTED relationships: 103,689

---

## Repository Structure

```text
cognodb-benchmark/
|
|-- benchmark/
|   |-- load_data.py
|   |-- load_cognodb.py
|   |-- load_memgraph.py
|   |-- load_arango.py
|   |-- load_falkordb.py
|   |-- neo4j_queries.py
|   |-- cognodb_queries.py
|   |-- memgraph_queries.py
|   |-- arango_queries.py
|   |-- falkordb_queries.py
|
|-- data/
|   |-- Wiki-Vote.txt
|
|-- scripts/
|   |-- test_neo4j.py
|   |-- test_cognodb.py
|   |-- test_memgraph.py
|   |-- test_arango.py
|   |-- test_connection.py
|   |-- test_falkordb_data.py
|
|-- results/
|   |-- neo4j_results.txt
|   |-- cognodb_results.txt
|   |-- memgraph_results.txt
|   |-- arango_results.txt
|   |-- falkordb_results.txt
|
|-- .env
|-- .gitignore
|-- README.md