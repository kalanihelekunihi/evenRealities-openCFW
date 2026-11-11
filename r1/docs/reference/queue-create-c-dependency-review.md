# Static and dynamic queue creation in C

The selected queue/mutex provider now includes pinned FreeRTOS 10.5.1
`xQueueGenericCreate`, `xQueueGenericCreateStatic` and their shared private
initializer. They use the existing 80-byte native Queue_t and selected reset/list
providers, without enabling the duplicate full upstream queue unit. Stock
instruction evidence is captured through REA for entries `0x97b0e`, `0x97b62`
and initializer `0x85094`.

Dynamic creation checks nonzero capacity, multiplication overflow and addition
of the 80-byte descriptor before allocation. Allocation failure returns null;
success records dynamic ownership and initializes storage immediately after the
descriptor. Static creation requires the descriptor and exactly the permitted
storage/item-size combinations, records static ownership and uses supplied
storage. Zero-size semaphore queues use their own descriptor as a nonnull head.
Both initialize capacity/item size, call reset as a new queue and store the type
byte after reset returns. Invalid arguments retain the configured logical
assertion fault.

Verification:

- 8,248 paired native/C creation cases (16,496 executions) cover static/dynamic
  paths, allocation failure, capacity/item-size combinations and overflow
  boundaries, null descriptors, storage rules, all 256 type bytes, starting
  interrupt masks and critical callbacks that mutate descriptor fields.
  Actual initialization, reset and list routines execute; heap and critical
  boundaries are modeled. Descriptor bytes, boundary snapshots, guard bytes,
  call order, return, SP, callee-saved registers and interrupt masks agree.
- 12,288 additional paired cases exercise actual dynamic/static mutex wrappers
  through creation, reset, list and mutex initialization, with the final generic
  send boundary modeled. The compiler changed the existing static-mutex wrapper
  from 34 to 36 bytes after inferring that successful static creation returns
  the supplied descriptor. These integrated comparisons cover that change.
  All eleven other existing function bodies remain byte-unchanged.
- All 6,944 queue-reset regression cases pass with the expanded provider.
- Negative controls reject wrong allocation size, incorrect static ownership
  and writing the type before reset rather than after it.

All 573 R1 units compile and compose without failures or duplicate strong symbols.
Application imports fall from 196 to 194, removing only the two creation imports;
bootloader imports remain 34. `make sources-check` and `git diff --check` pass.
Five official qualifier configurations compiled; only two already-covered
BASEPRI helper copies matched. The new recorded C bodies are 82 bytes dynamic,
98 bytes static and 32 bytes initializer versus stock 84/66/34; they are not
byte-qualified.

The unchanged canonical plan still builds a stock-identical hybrid application,
SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`,
with 3,833 source-built and 642,327 unclassified binary-pull-through bytes.
Source completeness remains false.

Tests compare observable descriptor state and boundary snapshots rather than
private frames or every ordinary internal access. Assertions cover mask, fault
address, width and value, without full processor exception-state proof. Heap
metadata/fragmentation, physical scheduling, interrupts and concurrency remain
unverified. No G2 gate advances. Exact source, REA, test, qualifier and build
hashes are bound in `queue-create-c-dependency-review.json`.
