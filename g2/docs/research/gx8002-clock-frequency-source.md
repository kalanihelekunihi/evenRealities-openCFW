# Upstream clock-frequency candidate

The pinned NationalChip clk_priv.h implements the retained frequency routine
at package17224/runtime10025210, used by RTC and SPI. The adapter authenticates
its SDK dependencies and compiles natively on macOS. Initial single-caller
inlining yielded544bytes. Exposing the module lookup's public NULL-capable
contract yields a separate160-byte lookup and468-byte frequency routine, still
24bytes larger than the444-byte stock envelope. A separate8-byte public lookup
adapter is analysis-only. No candidate code is admitted or integrated yet.

The next placement work is to retain shared helper boundaries rather than
inline already-qualified lookup behavior. Switch data, divider/DTO behavior,
PLL arithmetic, volatile read order and target ABI require qualification before
source admission. Existing SDK source and license provenance remain pinned.

A public divider adapter alone did not prevent inlining. A targeted noinline
annotation caused GCC to specialize the helper's argument structure (.isra.0),
so the adapter now declares the existing static helper with noinline/noclone/
noipa attributes. Upstream helper behavior remains unchanged. This produces a
separate40-byte __module_get_div with its original argument contract; frequency
remains468bytes. Both public helper adapters are analysis-only and must be
excluded from firmware placement. The24-byte overrun remains unresolved.

A fixed-address analysis link now places lookup at10024a44, divider at10024ae8
and frequency at10025210, resolving source-defined clock-table pointers. Lookup
160/164 fits. The divider is40bytes against a corrected28-byte envelope. Frequency468/444 overlaps the following gate jump
table, so the analysis ELF moves the frequency's own switch table to11000000.
This is explicitly not a firmware provider. All relocations resolve, and the
linked disassembly is available for decoded behavior/layout comparison. Public
analysis adapters are discarded. A production placement solution remains open.

Direct stock disassembly corrects the divider boundary: __module_get_div ends
at package16b18 (28bytes), where the PLL routine begins. The prior40-byte slot
assumption was wrong. The linked report now rejects the40-byte divider as well
as the468-byte frequency routine. Compiler-generated aggregate argument spills
account for the divider expansion; stock only uses the parameter and base
arguments in r0/r1. No oversized candidate has been admitted into firmware.

The separate stock-ABI divider reconstruction now passes12,800 decoded stock/C
cases and three focused tests. It checks absent descriptors, exact descriptor
and register read order/width, valid shifts, masked zero versus incremented
values, and preserved registers. The28-byte candidate fits but remains
unregistered pending admission/export. Its narrower two-argument interface is
based on the actual stock calling convention; the generic upstream aggregate
helper remains a distinct analysis artifact.

The stock-ABI divider admission verifier now pins source-builder/decoder
evidence, exports its linked artifact, and declares the corrected28-byte SRAM
placement. Fresh12,800-case qualification and the integration builder's own
reviewed_replacements validation pass against the saved report and exported ELF.
It remains unregistered while the current RTC integration is active.

The current analysis link now binds the qualified two-register divider at
10024ae8 rather than emitting the oversized aggregate helper. The frequency
text is480bytes (36over444), lookup160bytes, switch table at11000000 for analysis.
The checked generated-header adaptation changes only the divider call/declaration;
upstream frequency arithmetic is unchanged. This supersedes earlier468-byte
aggregate-call analysis artifacts. No frequency code is admitted.

Decoded dispatch verification passes259stock/C cases: module IDs0..255 and
large unsigned boundaries. It walks each actual switch table and checks the
module supplied to lookup or immediate zero result. UART/I2C/timer aliases and
DMA-to-SCPU remapping match stock; ADC/PDM returnzero. This proof stops at lookup
and does not qualify frequency arithmetic, MMIO or the full function ABI.

Four focused decoded-dispatch tests now pass: aliases/zero-return paths, large
unsigned input bypass, wrong lookup-target mutation, and switch-target mutation.
These tests exercise the compiled analysis code and table, rather than only the
independent mapping oracle. Frequency arithmetic and final placement remain open.

An independent integer PLL model now records source-input quantization with
ordered overlapping bands,32-bit multiplication/addition wrap, and integer
division order. Five model tests pass, including threshold endpoints, subbands,
output division, overflow and a zero feedback divisor outside the valid contract.
The model is not decoded-equivalence evidence; it will serve as an oracle for
that next check. No frequency code or model is admitted into firmware yet.

Decoded PLL arithmetic slice verification now passes480stock/C cases against
the independent integer model. The interpreter starts at each PLL block and
stops before DTO processing or at its invalid-frequency exit, checking all five
register reads in order. Subbands, feedback fields, input/output divisors and
32-bit overflow are exercised. This is slice evidence only; whole-function ABI,
source selection, DTO/divider composition and placement remain unqualified.

Four decoded PLL-slice tests now pass: nominal/overflow results, exact read
sequence, invalid register-offset mutation, and input-mask mutation. They run
the compiled instruction slice and detect changed behavior; model tests remain
separate. Next qualification is DTO scaling and complete frequency execution.

The DTO arithmetic slice now passes 72 decoded stock/source comparisons using
absent/present descriptors, bypass-bit and numerator boundaries, and frequencies
through UINT32_MAX. Both instruction streams preserve the frequency when the
DTO is absent or bit 27 is set; otherwise they compute the full 64-bit product
of the low 25 bits and frequency, then shift by 25. Ordered descriptor and MMIO
reads agree. Four tests cover absent-descriptor MMIO avoidance, full-width
products/bypass, and rejected mask/address mutations. This is a fixed-entry
slice qualification, not whole-function ABI or hardware qualification. The
480-byte frequency candidate still exceeds its 444-byte envelope and is not
admitted into the firmware.

Clock-source selection passes 26,624 decoded stock/source comparisons across
26 module values, four valid bit offsets, all combinations of the two source
bits, and 64 three-read sequences. Unlike a constant-register model, this
checks selection values that change between volatile reads. The ordered source
and selection reads, 32 kHz shortcut, low-frequency early return, and routing
to PLL/DTO/divider agree. A set-then-cleared selection bit produces zero on the
divider path; caching a prior read would not preserve this behavior. Four tests
cover this transition, the 32 kHz shortcut, low-frequency module routing and a
mutation that removes the second read. This is a fixed-entry slice with offsets
0..30; lookup/ABI and complete function composition remain outstanding. No
additional firmware bytes are admitted by these analysis checks.

An isolated size probe now compiles to 452 bytes, eight over the 444-byte stock
envelope. Replacing the four masked PLL subband cases with
`61440000u + vco_subband * 12288000u` reduced 480 to 460 bytes. Expressing the
low-frequency return predicate as `module >= 9 || (module & ~4u) == 2` reduced
that to 452. The masked subband domain and unsigned predicate equivalence have
two focused tests. These are local source adaptations, not claimed upstream
commits or fixes. The probe lives in its own build directory, is unlinked and
unadmitted, and does not replace the previously decoded 480-byte candidate.
Its generated instructions still need decoded qualification before admission.

The isolated 452-byte probe is now linked at analysis addresses and passes 480
PLL and 72 DTO instruction-level cases against the same arithmetic/read-order
models previously checked against stock. This specifically checks the generated
multiply/add subband implementation, rather than relying only on the algebraic
rewrite. Source selection and whole-function ABI remain unqualified for this
probe. Factoring the expression as `(subband + 5) * 12288000`, with and without
reassociation disabled, produced no size benefit; both experiments were reverted.
The baseline firmware provider and qualification code remain unchanged.

The 452-byte probe additionally passes 26,624 decoded source-selection cases,
including changing volatile values. Six selection/algebra tests pass. The shared
selection interpreter accepts explicit analysis stop points and handles the
probe's AND-NOT instruction; stock/baseline defaults remain unchanged. Disabling
jump threading to avoid duplicated branch loads increased the candidate to 504
bytes, so that flag was reverted and the 452-byte probe qualification rerun.
Eight bytes of size reduction and whole-function qualification remain required.

The smaller probe now passes 259 decoded dispatch cases using its own linked
jump table, including unsigned boundary values, aliases and immediate zero
returns. Four inherited dispatch tests run against this probe ELF and detect
changed helper targets and swapped jump-table destinations. The combined report
records the analysis ELF SHA-256, linking the dispatch/selection/PLL/DTO evidence
to one generated artifact. Lookup body composition, full ABI and the final
size reduction remain outstanding; no firmware admission is implied.

Separate 32 kHz selection size experiments did not improve the qualified probe.
Computing `offs_w` as `(offs + 1)` times a bounded module-bitmap predicate gave
460 bytes. Using the predicate as a presence flag and calculating `offs + 1`
only for the register read gave 456 bytes. These experiments have their own
script/build directory/report and are unqualified; neither replaces the 452-byte
candidate. The bounded right shift is guarded by `module < 10`. Further code
size work must retain the exact source/selection volatile read behavior.

Divider-call/return slice qualification passes 56 stock/probe cases. It verifies
the two-register helper arguments and target, zero-divider bypass, unsigned
nonzero division, and restoration of r4/r5/return address from an explicitly
modeled saved frame after caller-register clobbering. Three tests cover zero/
nonzero behavior and reject incorrect helper and stack-adjustment mutations.
This assumes the saved frame is valid; it does not establish that all preceding
paths construct and preserve that frame. Divider-body composition and whole
function ABI remain outstanding. The probe remains eight bytes oversized.

Decoded epilogue/divider composition passes 864 scenarios across stock/source
outer and inner selections, null/present descriptors, shifts, masks, MMIO words
and frequencies. Actual decoded leaf results now drive the outer division;
ordered descriptor/MMIO reads agree with the divider oracle. The three existing
return tests still pass after adding the composition hook. The helper executes
with its own modeled register frame, while the outer check models caller clobbers;
this does not prove a shared whole-function frame or hardware behavior. Full
frequency integration and eight-byte size reduction remain pending.

A separate source-authored table probe now links exactly 444 text bytes, fitting
the original function envelope. It defines the four PLL frequencies as typed
C constants (61,440,000; 73,728,000; 86,016,000; 98,304,000 Hz), adding 16 bytes
of rodata. Both text and table resolve without relocations in an analysis ELF;
the table is currently at an analysis-only address. This is not a firmware
placement or net-size win: placement of the additional data is still required.
The current ownership ledger contains several sufficiently large generated
unreachable-fill intervals, but carving one requires explicit ownership/builder
support and review of the host interval. No retained binary data was repackaged
as source, and neither the new table nor the function is admitted. The 452-byte
arithmetic probe and its qualification remain independently available.

The 444-byte table candidate's PLL slice passes 480 decoded cases against the
stock-qualified arithmetic model. The verifier loads and checks all four typed
constants from the linked source table, permits only in-range indexed table
accesses, and separately checks the exact five MMIO reads. Four existing PLL
regression tests pass after adding optional table-load interpretation. This is
not a complete function or placement qualification; table data still resides
at an analysis-only address and has not been admitted to firmware.

The fitting 444-byte table candidate now passes its own 259 dispatch, 26,624
source-selection, 72 DTO and 56 divider/return cases, in addition to 480 PLL
cases. These checks use the table candidate's linked instructions and switch
rather than the previous arithmetic probe. Each remains a fixed-entry slice;
the return check models the helper result and saved frame. Complete function
composition, real table placement and hardware qualification remain pending.

An isolated proposed placement links the 16-byte table at runtime 0x10025e38
(package 97868), the exact aligned generated-fill tail of the reviewed 196-byte
platform-config C function's 212-byte envelope. The analyzer authenticates the
current candidate image, compiled host prefix and zero-fill ownership. Frequency
text remains 444 bytes at its original entry, and its 76-byte switch table links
at the original 0x10025460 address; no relocations remain in these sections.
This is a proposed placement only. The firmware composer currently rejects the
nested envelope overlap, and host/control-flow qualification plus explicit
ownership support are required before admission. No firmware bytes were changed.

The proposed actual-address ELF passes 259 dispatch, 26,624 selection, 480 PLL,
72 DTO and 56 epilogue cases. These runs read the linked switch at 0x10025460
and the linked source table at 0x10025e38, rather than analysis addresses. The
changed literal/jump-table values are therefore covered by decoded execution.
The cases still initialize slices separately; host-tail control-flow safety,
shared frame/whole-function execution and composer integration remain pending.

A conservative local CFG walk of the authenticated source-built platform-config
host reaches 82 instructions. It explores both sides of conditional branches
and all ten qualified dispatch-table destinations; all paths remain inside the
196-byte compiled text and terminate without falling into the proposed table
tail. This supports local tail reuse, but does not rule out external entry into
the tail, arbitrary caller-directed writes, or startup/ownership issues. It
therefore does not admit the placement or relax the composer overlap checks.

The all-byte-alignment 32-bit little-endian pointer scan finds one stock literal
into the proposed interval: package 92624 points to runtime 0x10025e3c. It is
inside the original platform-config dispatch table, whose entire 40-byte region
is already replaced by authenticated generated source data. The current hybrid
candidate has no such literal hits. This records and resolves that stock direct
reference within the existing source replacement; it is not proof that computed
addresses or external control flow cannot reach the interval.

A standalone source-tail partition helper now supports an explicit exact-tail
allocation. It authenticates the original parent envelope, compiled prefix,
zero fill and new data payload; permits only aligned source-data ownership;
and returns disjoint intervals for the existing composer. Seven tests pass,
including checksum/ownership composition and rejected code overlap, changed
identities, nonzero fill and executable tail payload. It is not wired into the
firmware provider yet; placement qualification is a separate prerequisite.

The partition helper now passes an actual-artifact check using the authenticated
platform-config ELF and proposed linked PLL table. It yields disjoint regions:
196 source-code bytes at package 97672 and 16 source-data bytes at package 97868.
Both compiled payloads are preserved exactly, and the original parent envelope
and data subrange are authenticated against stock. The resulting report excludes
payload bytes and emits no firmware. Full clock qualification and provider
integration still precede admission.

The lookup-result gate passes 1,280 decoded stock/placed-source cases across
five helper return values and every signed-byte representation. Any nonzero
lookup result returns zero without reading the parameter. A successful lookup
reads the signed clock offset; exactly -1 returns zero, while other values pass
to selection. This explicitly covers sign extension, but negative offsets other
than -1 are not qualified for later shifting. The lookup body is still modeled
at this boundary; whole-function execution remains pending.

Lookup-to-result-gate composition passes 1,028 stock/source combinations with
authenticated clock parameter records. Decoded lookup output chooses the actual
record's offset byte, which is then passed to the decoded gate. Observed offsets
are 0,1,2,3,4,5,6,7,9,10,11,12,24; none introduces a negative shift in the stock
record domain. Dispatch mapping is modeled and the gate uses a translated fixed
entry state, so this remains separate-frame composition rather than a complete
function execution or concurrency proof.

Continuous candidate entry-to-return execution now passes 777 early-path cases,
covering immediate audio zero returns, failed lookup and successful lookup with
sentinel -1 offset. The interpreter uses one register/memory state: the prologue
saves registers, allocates the info record, calls the modeled lookup with its
actual stack address, and restores the original frame after caller clobbers.
Three tests reject incorrect allocation/restoration. Successful MMIO paths are
not yet covered by this continuous-frame check, and lookup remains modeled.

Continuous entry-to-return candidate execution now also passes 156 low-frequency
scenarios across 26 input modules, 1.024/12.288 MHz source choices, and divider
results 0,2,65536. One register/stack state spans prologue, dispatch, modeled
lookup, parameter load, actual selection instructions, optional modeled divider
call and epilogue. Helper argument and callee-register restoration checks pass.
Lookup/descriptor and divider bodies are modeled; PLL/DTO and changing register
values are not yet covered by this continuous-frame check.

The continuous-frame interpreter now covers the 32 kHz shortcut: 192 cases
pass across RTC/PMU/SRAM/OSC modules, offsets through 30, both source-selector
bits, and zero/nonzero divider results. Every case preserves a single saved
frame and validates lookup/divider arguments through return. The 156 previous
low-frequency cases still pass after adding configurable selection words.
Lookup/divider bodies and descriptors remain modeled; high-frequency PLL/DTO
paths still need continuous-frame qualification.

Continuous 24.576 MHz/DTO/divider execution passes 150 candidate cases covering
absent/present DTO descriptors, bypass, low/full numerators, aliases and zero/
nonzero divisors. The same frame persists across lookup, selection, 64-bit
scaling, divider call and return. The 156 low-frequency and 192 32 kHz cases
still pass after interpreter extension. Helper bodies and valid descriptors
remain modeled; PLL continuous execution remains outstanding.

Continuous PLL/table/DTO/divider candidate execution passes 72 cases, including
nominal PLL, overflow-sensitive arithmetic, invalid input-frequency rejection,
DTO bypass/scaling and divider zero/nonzero results. One saved frame persists
through all instructions and modeled calls. The 156 low, 192 32 kHz and 150 DTO
continuous cases still pass after adding the PLL instructions and bounded table
read. Lookup/divider bodies and fixed descriptors remain modeled; continuous
stock comparison, changing MMIO and hardware behavior are not established.

Continuous candidate execution with changing selection values passes 1,664 cases
and checks ordered source/selection MMIO reads. The result and divider-call
routing agree with the previously stock-qualified selection model, including a
bit clearing on its second read. Memory interpretation now rejects a word read
of the byte DTO offset and byte reads of word locations. PLL (72) and DTO (150)
continuous regressions pass. Descriptors/helpers remain modeled; this does not
establish whole-device or hardware behavior.

Continuous outer-frame execution with the decoded source divider now passes
162 scenarios across 12.288 MHz, 24.576 MHz and 32 kHz routes, descriptor presence,
shift/mask boundaries and MMIO words. Actual leaf output controls outer division,
and leaf read traces match the divider oracle. The 1,664 changing-selection
regressions still pass. The leaf uses a separate modeled register frame and
lookup remains modeled; this is not shared-machine whole-function validation.

Clock caller and source divider now execute in one decoded register/memory state
for 162 cases. BSR supplies the real simulated return address; the divider reads
its descriptor and MMIO in that state and RTS returns to the caller, whose
original frame is restored. This removes the separate leaf-frame assumption
for those cases. PLL-frame regressions still pass. Lookup and valid descriptors
remain modeled, and stock shared-state comparison remains outstanding.

Shared caller/lookup execution passes 259 missing-record cases, using decoded
lookup instructions, bounded info-record stack writes, and real simulated BSR/
RTS state. The lookup scans synthetic absent IDs or rejects out-of-range modules;
all caller frames restore correctly. The 162 shared-divider cases still pass.
Successful lookup records and continuous stock comparison remain unqualified.

Successful source lookup now runs in the same machine as the caller for 32
low-frequency cases across modules 10..25 and both low source frequencies.
The actual authenticated records determine the parameter pointer/offset and
source selector; decoded lookup writes the caller's info record directly.
All frames restore, and 259 missing-record cases still pass. Divider/PLL routes
with these actual records and continuous stock comparison remain outstanding.

All 26 module inputs pass continuous candidate execution through actual decoded
lookup and divider helpers with authenticated source parameter/divider tables,
under zeroed selection/divider MMIO. No helper return is substituted for these
routes. Typed descriptor reads, shared stack writes, BSR/RTS and final frame
restoration are checked. This is the low-frequency zero-register domain only;
other routes and stock continuous-machine comparison remain pending.

Continuous stock/source comparison now passes all 26 module inputs with actual
clock tables and both decoded helpers under zeroed MMIO. Stock code is decoded
from the authenticated wrapper and only PC-relative branch coordinates are
normalized to SRAM runtime addresses; opcodes and literal values are retained.
Both machines execute entry through return, with shared helper state and checked
frame restoration. This establishes equivalence for the zero-register low-clock
domain, not other source/PLL/DTO states or physical hardware.

Continuous stock/source low-frequency comparison now passes 208 cases: all 26
modules, both low-frequency sources and four divider register patterns. Expected
divisors are independently calculated from each real descriptor and actual
register state, including shared selector/register addresses. Both helper bodies
execute in each machine and restore the original frame. Higher clock selections,
PLL/DTO and hardware behavior still require broader qualification.

Continuous stock/source high-frequency comparison passes 130 cases across all
26 inputs and five register patterns, with actual DTO offsets and divider
records. Both machines execute 24.576 MHz selection, DTO bypass/scaling and
divider return, and match an independent calculation from the same register
state. Selector writes are applied after shared-register initialization so
aliased register addresses are modeled consistently. PLL and hardware remain
outside this check; no firmware admission follows from it alone.

Direct continuous stock/source PLL comparison passes 312 cases across all 26
module inputs, three DTO/divider register patterns and four PLL configurations.
The scenarios include nominal, overflow-sensitive and invalid-PLL calculations;
invalid results skip DTO/divider calls as expected. Real descriptors and both
helpers execute in shared machine state, and results match the independent PLL/
DTO/divider calculation. Hardware, dynamic MMIO and full image integration remain
outside this check; no source-only completion is claimed.

All three direct continuous comparison suites now additionally require exact
ordered MMIO address, access-width and value traces. The 208 low-frequency,
130 high/DTO and 312 PLL cases pass this stronger check with both helpers in
shared state. Source-table RAM reads remain distinct from MMIO. This catches
observable hardware-read differences that equal final frequencies alone would
miss. Physical timing and dynamic register values remain separate limitations.

Placement validation now rebuilds and authenticates the reviewed platform-config
source section and its original stock envelope directly. It no longer requires
the current hybrid output to contain zero fill, removing a circular dependency
that would otherwise invalidate verification after table installation. Actual
host/table partition verification and all 312 PLL stock/source cases pass with
this change. Provider integration is still pending.

A consolidated source-provider evidence generator now reruns the 650 continuous
stock/source cases, host-flow check and actual tail partition, and describes
three authenticated linked sections: 444-byte clock C, 76-byte switch table and
16-byte source-authored PLL table. It pins the principal builder/interpreter/
qualification scripts and supports ELF export. The aggregate run passes on
macOS. It remains explicitly unregistered/unadmitted pending provider wiring and
review; hardware and dynamic-MMIO limits remain in the report.
