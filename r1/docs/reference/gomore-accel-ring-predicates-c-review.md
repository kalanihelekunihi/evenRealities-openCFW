# R1 accelerometer circular predicates and history in C

`native_gomore_accel_ring_predicates.c` provides four native-ABI C candidates
under the still-unresolved accelerometer classifier at `0x67e4c`:

- `0x569bc`: strict signed band count, one wrapped index correction and signed
  eight-bit index narrowing; modes 62/60 implement signed >= / < tests.
- `0x56ba8`: three signed-halfword recent means. Output addresses and window
  are captured before initial clears; the incoming cursor remains live across
  aliased output writes. The early guard tests the sign bit of wrapped
  `length - window`, and sums wrap to 32 bits before signed division. Initial
  and final halfword writes retain native order and raw R0 behavior.
- `0x58256`: independent range > 200 and three-axis sum > 180 counts. Loads
  occur x/y/z/range; each counter narrows to signed eight bits after a hit.
- `0x583c8`: shift five history halfwords at state offsets 612..620 and append
  the low sample halfword. All five discarded reads remain volatile. The
  decision uses the full incoming signed 32-bit sample and strict thresholds.

REA instruction evidence resolves details obscured in the pseudocode: signed
index narrowing, subtraction flags, load order and the otherwise discarded
read loop. A write-only first history slot tests the read loop: both stock
and C fault at that read after the same five history writes.

Verification passes:

- 12,598 direct stock/C pairs: 5,192 band, 3,291 mean, 3,295 activity and 820
  recent-decision cases, including 55 logical faults. Cases include signed
  count/index wrap, large wrapped sums, equality, input/output/argument aliases,
  alignments, malformed addresses and independently wrapping counters.
- 5,816 actual accelerometer-stage pairs, including 66 fault cases. The four
  new providers execute 4,428 / 2,214 / 2,214 / 2,214 times respectively.
- 216 focused classifier pairs with all four providers executing 432 / 216 /
  216 / 216 times. C preprocessing, collector, statistics, conversion, square
  root and previously reviewed classifier leaves remain in the replay chain.
- 805 checked-wrapper comparisons. Four generic duplicate implementations
  now delegate to the shared native providers and are explicitly `_checked`.
  Mean's boolean success API differs from raw R0; output memory/writes agree.
  Typed bridge argument-slot rewrites are excluded from ordered-write comparison;
  final caller argument memory is still compared.
- Twelve rejected defects: modulo indexing, ordinary signed length comparison,
  cached cursor, missing initial clears, wide activity counter, inclusive range
  and sum thresholds, omitted discarded reads, narrowed sample decision,
  inclusive -500/history thresholds and omitted append.

Tests compare integer results, external memory, ordered public writes, logical
fault access/width, FPSCR, preserved registers, SP and masks. Integration also
compares callee arguments, entry depths and public buffer addresses. Private
save bytes, unexposed C frames, caller-clobbered register residue, APSR and full
exception frames remain outside the proof. Nonreturning count domains and
physical/concurrent sensors are not validated.

The normal source build passes with 713 units (639 application, 74 bootloader),
no failures or duplicate strong symbols, and unchanged 178/34 import sets.
`make sources-check` passes. Exact qualification rejects all four bodies;
canonical coverage stays at 4,381 source-built executable bytes, 641,779 stock
executable bytes and 248 resource bytes. The fresh hybrid matches stock.
Compilation, relocatable composition and hybrid assembly do not establish a
complete source-only link or C byte identity.

The classifier remains unresolved. Its four remaining direct dependencies are
`0x56a0c`, `0x56cf4`, `0x56d78` and `0x582c4`; their transitive spectral closure
also remains unfinished. No executable blobs or opcode arrays were introduced.
The [machine receipt](gomore-accel-ring-predicates-c-review.json) records current
source/object hashes, REA evidence, fixtures and qualification results.
