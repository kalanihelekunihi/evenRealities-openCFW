# P4 planner: derive C work only from the frozen corpus

First validate the whole-artifact G3 freeze receipt, target identity, corpus
manifest and all six component review summaries. If missing, stale, revoked or
incomplete, return `blocked` and emit **no C assignments or interfaces**.

Using the frozen pseudocode, graphs and data records, derive cohesive C units
and a dependency DAG. Give each function/body, shared tail, mutable global,
type, data table and generated asset one explicit implementation owner. Group
tightly connected state/functions; identify cycles and resolve interface
ownership before issuing parallel tasks. Preserve original symbol/address and
layout obligations needed for exact reproduction.

Propose common headers and ABI/layout contracts for the contract owner to review
and freeze. Include dependency source pins, required compiler/ABI profiles,
startup/linker/layout tasks, deterministic data generation and outer container
serialization. Distinguish recoverable requirements from unresolved toolchain
or signing blockers. Do not assume arbitrary C will yield the original bytes.

Prepare small GPT 6 Luna Low task contracts with minimal sufficient evidence,
frozen input hashes, exclusive private outputs, required semantic/ABI checks,
eventual linked-byte comparison, dependencies and stop conditions. Include
acceptance criteria for data/container work as well as executable code. Validate
the ownership union against the complete frozen inventory, without overlaps
or omitted bytes. Do not copy the old AM/CD/etc. queue as this decomposition.

Required outputs: ownership map, dependency DAG, proposed contract snapshot,
task definitions and validation receipts. No C implementation or worker launch
occurs in this planning assignment. The coordinator opens G4 only after review.
