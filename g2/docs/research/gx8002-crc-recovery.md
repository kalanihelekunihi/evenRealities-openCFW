# GX8002 CRC source and table recovery

The UART CRC wrapper at package `0x12E34` complements its input, calls the
uncomplemented core at `0x12D80`, then complements the result. This matches
`base/src/crc32.c` in the pinned NationalChip SDK, whose source identifies
its origin as zlib 1.1.3. The core performs byte alignment, word processing,
and a byte tail using a single reflected CRC table. Upstream pointer arithmetic
and aliasing assumptions require review before reuse in a reconstructed build.

The table at runtime `0x1020B908`, package `0x14E94`, is exactly the 256-entry
table generated from reflected polynomial `0xEDB88320`. The generator emits C
from the polynomial before reading stock for comparison. It does not turn
extracted firmware bytes into an array. Identical tables occur at package
`0x86D8` and `0x4C698`, giving three 1,024-byte data recovery candidates.
The [table record](gx8002-crc-table-recovery.json) pins their identities.

The generated table recurrence passes the standard `123456789` CRC check and
1,025 comparisons against Python zlib with varying data lengths and initial
CRC values. Each case also checks incremental update equivalence. These tests
qualify the mathematical table, not the stock executable's access behavior.
Table placement and executable integration remain pending; no retained-byte
count changes yet. CRC code and logging still block admission of the complete
UART dispatcher, while other reconstruction work remains possible.

`runtime_gx8002_crc32.c` now reconstructs the aligned word algorithm with a
GCC `may_alias` word type and forward-only pointer arithmetic. It avoids the
upstream pre-decremented pointer that can temporarily precede the buffer.
2,052 host cases pass against zlib across all four alignments and lengths
0 through 512, including seeded, uncomplemented and incremental updates and
input preservation. This is ordinary little-endian memory code, not MMIO.

The [target candidate record](gx8002-crc-source-candidate.json) records native
macOS C-SKY compilation variants. The wrapper emits 12 bytes; the core and
its table reference still require linking and instruction-level comparison.
Size-oriented compilation can outline a 20-byte helper, which must be accounted
for rather than omitted when evaluating whether the implementation fits.
No new bytes have been admitted to firmware in this step.

The CRC candidate now links at original runtime addresses: core `0x102097F4`,
wrapper `0x102098A8`, and generated table `0x1020B908`. The placement tool rejects
unexpected allocated sections, wrong addresses, oversized bodies and unresolved
symbols/relocations. The 160-byte core fits its 180-byte envelope; the 12-byte
wrapper and 1,024-byte generated table match stock exactly. See the
[placement record](gx8002-crc-placement.json). Core control flow and input/table
accesses still require a target execution comparison before firmware admission.
The linker emits an analysis candidate only, not a firmware container.

The linked CRC core now passes 1,028 restricted instruction comparisons over
all four pointer alignments, lengths 0 through 256 and seeded CRC inputs.
Stock and source match the result and the complete ordered sequence of input
and lookup-table reads; every result also matches zlib. This includes empty
inputs, the alignment prefix, word groups and byte tails. The
[target comparison](gx8002-crc-target-comparison.json) records the outcome.
Three focused interpreter tests cover little-endian post-increment word loads,
decrement branches, wraparound and rejection of unsupported/out-of-bounds
operations. Five relevant tests pass including host C and table checks.
These finite comparisons do not qualify hardware timing or arbitrary processor
behavior. Integration and source-data accounting are still pending.

The experimental builder now supports a distinct `generated_source_data`
ownership class. ELF executable flags must agree with the declared ownership;
data cannot claim unreachable-code fill. Six container/ownership tests pass,
including separation of generated data from compiled C. The CRC table itself
is not admitted by this infrastructure change; it will require its reviewed
generator, linked section and placement evidence when integrated.

## Experimental integration

The CRC core and wrapper plus the table at package `0x14E94` are now integrated.
The builder regenerates and links the table and C code, replays the 1,028-case
comparison, and requires equality with the reviewed report before emission.
It removes 1,216 retained bytes: 172 become compiled C, 1,024 become generated
source data, and 20 become separately counted unreachable fill. Eleven relevant
tests pass. The other two identical stock table occurrences remain retained;
their eventual replacement must be separately accounted. Hardware timing and
the rest of the source-only objective remain unqualified.
