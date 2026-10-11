# G2 C firmware implementation checkpoint

The source-completion goal remains active. **Zero of six full firmware images
are complete.** This round adds executable C bodies, genuine register entry
adapters, and a reproducible six-image candidate build. Successful candidate
compilation and relocatable linking do not establish complete payload coverage,
stock equivalence or operation on G2 hardware.

## Current whole-candidate build

From the repository root:

```sh
python3 g2/firmware_c/build.py --include-experimental --require-complete \
  --output g2/build/c-firmware/20261011/final-checkpoint
```

The command completed with expected status **2** because complete-source gates
remain open. All six architectures now compile and link their available C
candidate graphs. EM9305 coverage is a single queue unit compiled to ARC EM,
not a complete controller image. Its portable layout check also passes.
`g2/build/c-firmware/20261011/final-checkpoint/receipt.json` records the exact selected
and experimental inputs, commands, hashes and symbol lists.

Main and Audio belong to **one Apollo MAIN image**, not separate firmware
images. Bootloader is a separate image. The coordinator does not consume the
official payload or a prebuilt executable library, and emits relocatables,
not a flashable image.

| Image | Current compiled graph | Remaining minimum work | Full component complete |
| --- | --- | --- | --- |
| Apollo Bootloader | 318 selected members, 868 providers/five imports; experimental printf/floating-log composition has 870 providers/three resident imports | Three ROM interfaces; broad body attribution, product data, whole-path composition and final layout | No |
| Apollo Main, including Audio | 739 defined symbols, zero duplicate strong symbols; experimental logger/UART/power/delay/classifier/transport helpers compose | 77 imports; product FAL/FlashDB/log/power state, broad body/data coverage and image layout | No |
| CASE | Selected graph 70 providers/three imports; distinct full-command graph 70 C units/23 imports; selected+candidate whole-archive graph has 14 imports, zero duplicates | Fourteen classified flash/control/task lowers, full reset/layout, data and composed execution | No |
| Touch | Selected graph 210 symbols/zero imports | Source ownership for 939 of 964 reset-copy bytes, generated product configuration and final absolute map | No |
| EM9305 BLE | Queue C source passes field assertions and compiles/links to ARC EM ELF32, one provider/zero imports | Producing QP/C port, EM7D configuration/qualification, controller/product source and record placement | No |
| GX8002 codec | Ten DSP C units plus application-helper C unit compile and link with qualified C-SKY compiler; 19 symbols/four imports | Private application/driver/speech source, product globals/configuration, startup/map and execution qualification | No |

Import counts are a bounded estimate of known linkage work. They do not count
all unreconstructed functions or absent initialized data. No defensible
percentage or duration for full image completion follows from these counts.
`checkpoint.json` records the final whole-build receipt hash and bounded
root/numerical oracle receipt hashes. `next-round.json` records three separate
remaining source chunks; the goal has not been marked complete or paused.

## Bodies reduced and checked in this round

* Boot startup uses the genuine raw-register entry and reconstructed C core,
  preserving ambient R5/R7 and saved R1–R3. A fresh current-provider oracle
  passes 1,376 cases and visits all 810 root bytes. Two helpers execute
  natively; nine root and ten clock children remain controlled. The oracle
  recompiles two sources for M33 emulation and does not prove M55/device use.
* Boot `__aeabi_d2f` comes from pinned LLVM compiler-rt 20.1.8 C source.
  100,127 double encodings match the host hardware conversion. The added
  files retain hashes and provenance; this is numerical evidence rather than
  proof of the original producing runtime.
* Main's 1,026-byte extended logger outer flow is C with twelve selected
  helper bindings. Product state, general formatting, fatal and output
  contracts remain explicit.
* Audio UART IRQ and all six named children have experimental C bodies.
  Namespaced RX/TX bridges permit composition with the admitted 160-member
  archive without duplicate public definitions. Full original IRQ and
  physical interrupt behavior remain unproved.
* Audio's full generic power branch graph compiles as C with fifteen lower
  and product contracts. Thirteen stock branch families remain unqualified.
* Scheduler delay passes 64 bounded stock/source cases. Delayed-list/resume
  and fatal paths retain explicit limits. Classification and its ABI adapter
  each pass 24 boundary/NaN comparisons.
* Five Main logger register, privilege, nonreturning reset-request and mutex
  helpers compile and compose. Bounded register, first reset write and mutex
  argument checks pass 24/4/24 cases; reset completion, full mutex state and
  output transport remain open.
* CASE legacy and binary routing bodies, formatter, memcpy, variadic logger
  tails and checked event/flash/sensor aliases compile as 70 C units, with
  source C arithmetic replacing the earlier libgcc dependency.
  Formatter passes 180 stock comparisons, including 25 retained caller
  formats. Legacy returning-route comparisons pass 2,540 cases; bounded
  reader/fill/A3 checks pass 216/72/96 cases. These are not a complete
  hardware command-handler oracle.
* Two GX8002 application helpers compile for ck804ef hard-float with their
  observed 28-byte request layout. Four product/lower contracts remain.

## Tools, provenance and remaining work

The additional transport C covers submit/signal, getter/setters, waiter removal,
atomic node queue, failure wrapper/message and the actual 256-node pool setup.
Bounded checks cover 34 submit, eight signal, 16 getter, four queue, four waiter,
three failure and two initialization fixtures. Full pool/global hashes are
compared; concurrent delivery is unverified. The three-argument formatter and
FlashDB print now bind to selected C; four-argument bounded formatting is open.

CASE full flash-apply success/failure flow passes 96 cases at controlled lowers;
mode, unlock/lock and elapsed-tick wait pass six/eight/six. Full sensor transaction
passes 48 cases, transport helpers 120 and MMIO sampling 15. Boot mount's ten
logging callsites now pass recovered metadata to selected EasyLogger C. Their
host test passes; original-byte caller composition remains open.

The official [ARC GNU 2026.03 release](https://github.com/foss-for-mips-arc-processors/toolchain/releases/tag/arc-2026.03-release)
was downloaded and its published SHA-256 verified. The release repository is
registered as `third-party/tools/arc-gnu-release`, pinned to
`18942eae5509e7aa4f562b82baae86c9017e4a41`. Compiler, source and header hashes,
ELF32/little-endian/ARCv2 header and ARCEM attributes are checked by the build.
This removes the local target compiler absence; it does not recover private
controller source or its producing configuration.

The whole Bootloader crosswalk lists 903 recognized function envelopes, 849
retained raw pseudocodes and 54 absent files. Its 540 unmatched mechanical rows
are attribution gaps, not 540 proven missing C bodies. Several sampled entries
already have selected source implementations under different names. Provider
and import counts cannot establish whole-image body coverage.

`tool-status.json` confirms no running Ghidra bridge instance. REA's headless
Ghidra 12.1.4 provider and JDK 21 are available; lack of a GUI bridge is not an
analysis blocker. Existing Ablation call inventories remain useful only with
reviewed Thumb state, bounded bodies and independent call-site validation;
their whole-image edge count is not source coverage.

Worker reports retain source-address maps, bounded oracles and open contracts:
`apollo/REPORT.md`, `m0/REPORT.md`, and `peripherals/REPORT.md`. Further C
reduction continues on logger runtime helpers, CASE lower/runtime bodies,
and Bootloader remaining contracts. Source-owned configuration, complete
image coverage and final linker/reset layout are required after those bodies.

Canonical campaign state remains `P2_EXECUTING`; G2–G6 remain `not_run`.
No full payload, flash package, hardware validation, commit or push is claimed.

## Subsequent parallel round: EM scheduler and Boot attribution

The experimental EM9305 graph now compiles two C translation units for ARC EM:
queue initialization and the recovered scheduler control flow. It defines three
symbols with two explicit vendor port imports (`opencfw_em9305_log2p1` and
`opencfw_em9305_assert`). Twelve host contract regression cases passed; they
supply the hardware operation and do not execute stock ARC instructions. See
`em9305/scheduler-receipt.json` and `g2/build/c-firmware/20261011/em-scheduler-round/receipt.json`.
The producing custom instruction arithmetic/adapter, controller bodies, source
data/startup and final layout remain open. This completes the recovered
scheduler control-flow C unit, not the EM9305 component.

Bootloader receipt-backed attribution reduced the machine-unmatched catalogue
from 540 to 518 functions. These remain attribution reviews, not a measured
missing-body count. The selected archive remains 318 members / 868 providers /
five imports; the experimental composition removes two of those imports.
Bootloader full-image completion remains false.

Five more retained codec XIP pseudocode bodies now compile to C-SKY C:
board getter, signed gain lookup, DMA burst enumeration, UART put/get. The
experimental codec graph defines 24 symbols with six genuine lower/data
imports. New board constant and gain table storage are explicit source
obligations; no blob or guessed zero initialization replaces them. These five
bodies have compilation evidence only, separate from the prior callback
byte evidence and any stock/source execution. See `codec/board-uart-receipt.json`.

Subsequent independent native review authenticated the codec child against its
pinned parent span and confirmed the signed gain-byte load, both DMA burst
field loads before conditional selection, and one UART register-base load.
The C was corrected to preserve those reads. The board address and nine signed
dB gain values now have explicit C definitions, closing those two data imports;
final placement remains open. Static instruction review is not an execution
oracle. See `codec/board-uart-native-review.json`.

## Latest unified parallel round

`g2/build/c-firmware/20261011/parallel-round-checkpoint/receipt.json` records
PASS for compilation/linking of all six available C candidate graphs. Strict
completion exits2 because no whole source image is complete. Latest experimental
composition: Bootloader872 providers/3 resident imports; Main749/79; CASE79 C
units/10 imports when combined with selected sources; codec26/4; EM9305 three
exports/two port imports; Touch210/0 with939 reset-copy bytes unowned.

Completed C body chunks this round include two Bootloader functions (421 and360
bounded stock/source checks), eight Main/Audio units (thread creation, list and
scheduler, event wait, file close, domain-limited formatter candidate), expanded
CASE flash/controller/transport/task/report routines, EM scheduler control flow,
and five codec board/UART functions. Main's full bounded formatter remains
unresolved; the limited adapter has a distinct candidate export and a returning
real general-format lower contract, not invented fatal behavior.

Remaining work estimates are evidence counts, not percentages: Boot462
attribution reviews plus whole-image data/layout/ROM; CASE10 explicit imports
plus whole-body/data/layout review; Main79 imports plus product data and body
coverage; EM and codec whole-image missing-body counts unknown; Touch939
unowned reset-copy bytes and product configuration/layout. Goal remains active.

Follow-on codec reduction adds event preparation/reply and GPIO C bodies,
correcting the request binding to the actual literal RAM address. The fresh
codec-only build now has29 exports/two imports (timestamp, request consumer),
with no whole-image completeness claim. Native review verifies field/address
contracts; execution and hardware effects remain unproved. Main/Audio's next
pass has additionally supplied two LittleFS C bodies and is ongoing.

## Further source reduction checkpoint

All six candidate graphs compiled in `deeper-provider-final`; this remains
zero complete source firmware images. Corrected Bootloader MSPI source was
rebuilt in `mspi-corrected-round`, superseding the earlier erroneous handle
prefix/status accumulation source. Nine bounded stock/source cases pass,
534/712 instruction bytes visited; callbacks, active CQ and child effects remain.

Main integrates seven additional filesystem/TLSF source units in
`main-deeper-tlsf-round`. CASE progressed past its 102-unit checkpoint; the
`case-102-round` captured deeper scheduler bodies, leaving four linked contracts
(invariant failure, nesting underflow, task delay, tick increment). Directory
labels do not assert a frozen current source count.

Codec now includes request/channel/queue-full C and unchanged pinned CRC
source. All 256 table words match stock; 1,460 host comparisons pass against
zlib. Mixed-width accesses explicitly disable strict aliasing. UART
message-start and queue read/empty source are the next compiled chunk.
Original C-SKY execution remains unproved. EM scheduler custom-instruction
adapter compiles to the exact decoded LOG2P1 instruction and leaves its actual
assertion interface open; this is not arithmetic/controller/device proof.

Remaining work estimates are lower bounds, not percentages: Bootloader
436 attribution reviews plus seven linked contracts and source-owned layout;
CASE four captured contracts plus full body/data/layout crosswalk; Main dozens
of runtime/device/configuration contracts plus nested assets and layout; Codec
private application/resident APIs and producing configuration; EM controller
and QP/C product port/configuration; Touch 939 reset-copy bytes and generated
CapSense configuration/layout. Import counts alone cannot measure complete
firmware coverage.

Codec queue/UART round compiled with 38 exports and six explicit imports.
Main captured seven TLSF/littlefs helper additions at 773 exports/84 imports.
Subsequent worker source adds faithful semihost diagnostics and TLSF absorb;
the stock BKPT is architectural behavior, not a fabricated failure stub.
CASE worker subsequently reached 106 units/two fault contracts, with bounded
list 12 cases and idle scheduler resume 8 cases. These later source additions
require the next coordinated build capture. Goal remains active.

## Unified further-source round and codec runtime

`further-source-round` compiles all six candidates; strict completion exits2,
with zero complete payloads. Captured graphs: codec38/6, EM4/1, Touch210/0,
selected CASE70/3 and combined CASE two fault contracts, Boot877/3, Main775/84
(exports/imports). Boot adds genuine MSPI source lowers, reducing imports.
Main adds actual semihost diagnostic and TLSF absorb behavior.

`codec-channel-runtime-round` then compiles callback-set, channel-stop and
timer-start bodies at41 exports/five imports. Native static listings and
source hashes are in `codec/channel-runtime-receipt.json`. Signed hardware
shift/compare behavior and ordered volatile state/MMIO are preserved;
resident critical save/restore remain external. This is compilation/static
evidence, without original C-SKY execution or final memory ownership.

Remaining lower-bound estimates: CASE two fault contracts plus whole-body,
initialized data/startup/layout crosswalk; Boot three captured ROM contracts,
436 attribution reviews and complete startup/data/layout; Main79 imports in
latest worker graph, many runtime/device/configuration bodies; Codec five
resident contracts and private program/configuration/layout; EM one assertion
import plus controller/product port/data/layout; Touch939 unowned reset-copy
bytes plus generated product configuration/layout. No full component is
marked complete. Three workers continue the larger source-completion goal.

## EM activation C reduction

The entire retained 144-byte QK_activate_ body is now ARC C and compiled in
`em-activation-round`. Hardware IRQ/synchronization and ready-bit operations
remain decoded instruction mnemonics, with actual event-get/GC children
explicit. Five C exports and three imports; no native execution or full
controller completion claim. This expands real source coverage rather than
concealing newly surfaced contracts. Codec resident interface search found
no address-labelled provider in the pinned public source during this pass;
further resident bytes/provider ownership must be checked before source
substitution. Boot attribution count now431/903, not missing-body count.

## EM assertion and event collector C

`em-assert-round` and `em-event-gc-round` compile genuine native returning
assert-dispatch and dynamic event-GC bodies. ARCEM native listings establish
callback-slot null behavior, saved interrupt state and ref-count/pool-index
operations. Wrong default ARC decoder output was rejected and replaced with
ARCEM listings. No invented halt policy or arithmetic substitute is used.
The graph now contains seven exports/two lower contracts: active-get and
pool-put. Source coverage grows, while native execution, controller runtime
configuration, callback/table initialization and final layout remain open.
Main TLSF wrapper build passes with80 imports; deeper list mutation children
remain genuine contracts. No full firmware component is complete.

## EM queue and pool body closure

`em-queue-pool-round` compiles the actual active-get and pool-return bodies,
corroborated by authenticated ARCEM native instructions and pinned QP/C.
The experimental subgraph has nine exports and zero imports. This is a small
queue/scheduler/event subset, not complete controller coverage. Product
callback-slot/pool/active-table state, IRQ profile, startup, all remaining
controller code and four-record layout are unresolved. A new coordinated
build includes explicit no-strict-aliasing for recovered mixed-width RAM.
Boot additionally converts TON-table consumer to source-owned nine-byte C
data; final placement remains open.430/903 unattributed entries remain.
Main mapping/free-list/alignment source is queued for coordinated capture.
No full source component is marked complete.

## Coordinated queue/pool integration and framework initialization

All six candidates compile/link in `queue-pool-integrated-round`; strict
completion exits2. CASE combined graph has zero imports, but its108 source
units leave whole application/reset/parser/transfer/data/layout gaps.
`em-framework-init-round` adds decoded framework reset writes and actual
0/68/8-byte clear calls, then active0/lock16. Compilation passes with a
genuine memory-fill child contract; no unknown product configuration is
zero-filled. This is partial source initialization, not complete startup.
Boot source-owned TON/DFU strings are authenticated to nine table bytes and
452 string/path bytes; absolute image placement remains open.
Full components complete remains0/6. Three workers continue source reduction.

## Native memory-fill and Main block-device flush

EM memory-fill body0x33301c is C with native alignment/byte/word stores and
full32-bit value expansion preserved. ARC build passes;1,820 host contract
cases cover all alignments/counts0..64, unusual high-bit values, return and
untouched guards. These are not original ARC execution. The small graph has
12 exports/zero imports; remaining controller/record/startup/product-state
coverage is still unestablished.

Main integrates cache-drop and actual block-device flush after36 bounded
stock/source cases, with compare/cache-zero/alignment child contracts open.
CASE separately builds46 vector slots and native reset boundary calls;
CRT copy/zero state, interrupt handler bodies and integrated source layout
remain. No full component is marked complete.

## EM peripheral startup-hook body

`em-startup-hook-round` compiles the decoded0x311154 body. Fresh ARCEM
decoding rejects several incorrect retained Ghidra operations, establishing
actual MMIO3/1 writes, callback slots0x80fe10/0x80fe0c and IRQ/nesting sequence.
Source carries explicit incoming residual R0 to the genuine0x302518 lower;
public producing hook/callback ABI remains unqualified. This is one startup
body, not complete reset/controller initialization. Graph13 exports/one
startup lower import; original ARC execution and source record layout open.
Main cache/align/fill leaves are queued after63 bounded stock/source cases.
Full firmware components complete remains0/6.

## EM framework run and CASE initializer progress

`em-framework-run-round` compiles actual startup lower(NOP/return) and
framework-run scheduler/startup/nonreturning idle sequence. No substitute
no-op was invented; the decoded child consumes no R0, superseding the
provisional adapter requirement in startup-hook-receipt.15 exports/one idle
contract; full controller reset/data/configuration/layout remain open.
Main cache/fill integration builds at794 exports/76 imports.
CASE worker reports separate startup source owns vector declarations,
initializer decode and BSS zero; bounded comparison covers11,400 RAM bytes.
Product104-byte initializer and12 handlers/application bodies remain actual
imports, and command/startup source/layout integration is incomplete.
No full component complete.

## EM idle and Main comparison integration

`em-idle-round` compiles hardware ILINK/callback/IRQ/sleep-return sequence
at0x3115e4.16 exports/one actual sleep lower import. Native caller uses
returned R0 as SETI state; source preserves that rather than assuming the
child cannot change it. Producing IRQ/callback profile, sleep/ROM/controller
bodies and complete startup/record ownership remain open.
Main bd_cmp integrates and builds with actual read/memcmp contracts; byte
compare source then passes640 bounded stock/source cases and is queued for
next link. CASE command/startup experiment reproducible scripts live in
`m0/`, with13 startup imports and no duplicate symbols. Complete firmware
components remain0/6, with three workers active.

## Explicit body coverage and startup capture

Main byte-comparison source integrates in `main-byte-compare-round` with
compiler/link PASS. CASE command+startup/IRQ source separately links with
11 real imports in `case-startup-irq-round.receipt.json`; raw object is a
relocatable experiment, not final firmware.
EM `body-coverage-boundary.json` lists14 native envelopes with corresponding
C candidates against211,824 total record payload bytes. This inventory does
not classify all remaining code/data or prove equality; zero imports in a
small graph never establishes full controller completion. Sleep routine
0x3126e0 has real controller and resident-ROM children and remains the next
body. Full firmware source components complete0/6.

## Boot startup/vector and full LittleFS read integration

`boot-startup-vector-round` and `main-bd-read-round` compile/link PASS.
Boot includes real omitted startup/exception source and source vector
declaration; worker vector fixture matches64 authenticated bytes, with11
symbol relocations. Final vector/data/code placement and whole-path execution
remain unproved. Boot crosswalk421 unattributed entries/903.
Main adds full LittleFS read state machine after40 bounded stock/source
cases; actual memcpy lower remains open. Native cache-drop/flush/sync naming
is being normalized to avoid misleading inherited labels.
CASE initialization candidate now spans real full control flow; first
state-setup prefix passes8 cases and corrected two byte-zero stores.
Later self-check/PMIC/secondary paths and40 startup lower/data contracts
remain open. Root EM sleep native listing now covers entire0x3126e0..0x3128e4
function; controller/ROM/typed callback branches need faithful C reduction.
No complete source image:0/6.

## EM resume source bodies

`em-resume-round` compiles native resume hook and nonreturning resume idle
loop, now18 exports/one actual sleep import. Fresh listings are byte-bound
to the pinned package descriptor and original component SHA. Source retains
callback addresses, controller notification, nesting rereads/decrement,
MMIO3/1 writes and decoded IRQ sequence. Original execution, callback/IRQ
producing configuration, sleep/controller/ROM coverage, reset and record
layout remain unqualified. Full components complete0/6.

## Main semantic names, copy and file flush

`main-cache-rename-copy-round` compilation/link PASS after native cache-drop/
block-device-flush/sync names are normalized. Actual copy helper memory
side-effects passed256 stock/source cases; its declaration intentionally
returns void because the stock optimized helper has incidental path-dependent
R0 which its caller ignores. No return-value equality claim.
Full LittleFS file-flush state machine adds C after30 bounded stock/source
cases; lower flushed-read/write/relocate/log children remain explicit, and
its coordinator build is next. REA list-documents check found no active
provider target; this does not prove headless analysis unavailable. Native
ARCEM sleep control-flow listing remains the authoritative decoded input,
with resident/controller child ABI and hardware sleep qualification open.
Source-complete firmware images0/6; goal active.

## Sleep alternate branch and Main file flush

`em-sleep-mode-branch-round` compiles an explicitly synthetic helper for the
complete native mode-not0/not1 sleep branch and common disabled-IRQ return.
It retains callback notifications, volatile MMIO bit updates, ILINK check,
mode3 selection and real ROM/controller children. It is not a new stock
function or full sleep-body implementation; caller composition and remaining
branches remain open.19 exports/three imports in current experimental graph.
Main full file-flush source integrates/compiler-link PASS after30 bounded
stock/source cases. Flushed-read child passed24 cases and its coordinator
build is running. Full source firmware components complete0/6.

## EM outer sleep and Main write/outline

`em-sleep-outer-round` compiles actual outer mode/query branches, readiness,
ILINK and hardware SLEEP paths, plus existing alternate-mode helper. Complex
controller-state branch remains an explicit unimplemented child; no complete
sleep or controller claim. Actual ROM/query producing ABI and original
execution remain unqualified. Main flushed-write/outline/checkpoint graph
compiles after bounded24/4 cases; relocate and source literal debug wrapper
are queued next after12 relocation cases. CASE parser reports50 cases across
valid command paths, with diagnostic/forward effects still open.
Boot reconstructs semantic startup-stream data; full source firmware
components complete remains0/6.

### Source scatter and controller continuation

All six candidates compiled in `source-scatter-relocate-round`; strict completion remains rejected for all six. This snapshot precedes the latest seven Boot initializer relocations. Boot startup installer subsequently passed three bounded native comparisons: ITCM 24 bytes, SSRAM 4096 bytes, SRAM 1371 bytes with 29 callback relocation words normalized. This is startup evidence, not full-image proof.

Main filesystem additions now include program cache, lookahead allocator/scan, CTZ index/find and authenticated no-space logging. Their worker receipts retain bounded native comparisons and genuine child contracts. CASE command/startup composition retains 30 unresolved imports, with product initialization, application, IRQ and layout still incomplete.

EM9305 sleep controller branch has been reduced to a separately compiled C helper from native ARC EM control flow. Metadata outputs, controller action/enable and hardware/ROM lower contracts remain explicit; no ARC runtime equality is claimed. Full source completion is still 0/6. Remaining effort cannot be estimated reliably as a percentage from import counts; each image still requires product bodies/data, final placement and integration qualification.

### Metadata and filesystem continuation

All six candidates compiled in `sleep-controller-ctz-integrated-round`, strict exit 2. Subsequent EM metadata selection and preparation C units compile with the ARC EM toolchain; source hashes and authenticated record identity are captured in `em9305/metadata-source-receipt.json`. The mode branches now share one ROM 0x101d50 contract. Registered timer callback 0x3128e4 is also reduced to source and passed ARC EM compilation in `em-sleep-callback-round`. This is static native correspondence and compile evidence, without ARC execution equivalence.

CASE transfer 0x08005528 now has 28 whole-return immediate cases, 3 controlled-tick timeout cases, and 3 reconfiguration child-boundary comparisons. Its separate combined graph has 31 unresolved contracts, including clock planning. Main settled CTZ extension and directory cache read bodies are admitted to the experimental manifest; directory slicing, commit and traversal remain the filesystem frontier. Full image count remains 0/6; missing code/data/layout is not yet measurable as a dependable percentage.

### Sleep registry and symbolic Boot data

EM source registry now owns list head 0x3108f4, callback registration 0x311848 and timer finalizer 0x3117f8, including the latch/IRQ child 0x311854. ARC EM Werror compilation and relocatable link PASS in `em-sleep-registry-round`; strict completeness still fails. Clock 0x310900 remains open because opcode 0x310910 produces a multiply-class ambiguity in objdump. No arithmetic replacement is admitted until that ambiguity is resolved.

Boot worker selected archive now reports 332 objects / 905 providers / 5 imports, with EasyLogger color/level tables and two task entry fields source-owned. Startup oracle has 19 data table pointers exact, while 31 function relocations are normalized; full placement and data audit remain. Main reverse directory lookup is added to experimental source manifest after 32 bounded stock comparisons. Next integrated build must capture this latest manifest. Source-complete images remain 0/6; counts describe selected graphs and cannot estimate full-image completion.

### Synchronization reduction

EM metadata synchronization 0x310990..0x310a4c now has C source, including native IRQ sleep loop, peripheral slot scan and conditional carry-bit operation retained as inline ARC instructions. Its actual ROM/controller lowers remain explicit. No runtime equality is asserted. The clock opcode remains undecided; binutils maps it to DSP `mpywhl` with an ambiguity warning, and only this default match was found in the retained opcode table. This does not yet establish the producing hardware instruction extension.

CASE clock-plan reduction now has 60 whole-return bounded comparisons, with an explicit missing 32-byte prescaler product table. Boot storage callback fields now use three actual source veneer relocations. Worker traversal candidate is compiling but its native oracle is pending, so it has not yet been admitted to root experimental manifest. Full completion remains 0/6.

### Synchronization query and next component pass

All six candidates compiled in `symbolic-boot-directory-round`, with strict completeness rejected. EM synchronization query 0x310b08..0x310b54 is now source-defined with exact volatile peripheral write order and native SYNC. Its latest partial receipt is `em-sync-query-round`; no hardware or native ARC execution equivalence is claimed. Main state-move helper passed 90 bounded cases; cycle detection passed 20, and both are included in experimental manifest. Traversal oracles remain pending.

CASE clock prescaler source was corrected to use control byte index 2, then derived algorithmically from retained HAL source rather than copying a stock table. Its 320 randomized whole-return comparisons pass. Separate combined graph has 30 imports. Worker chunks now cover Touch initializer/data, CASE application, and Main traversal/directory bodies. Boot remains incomplete after its symbolic scatter pass; no required image is dropped. Full completion remains 0/6 and full remaining percentages remain unquantified.

### Capture restoration and timer update

EM capture restore 0x310cec..0x310d18 is source-defined and ARC EM Werror compile/relocatable link PASS in `em-sync-restore-round`. It preserves native full R0 mask return independently from the byte stored to peripheral control. Timer update 0x310a4c..0x310aa8 now has C source with actual conversion and wide-divide child facades; their register-pair return signatures remain unqualified. No stock ARC execution equivalence or hardware proof is asserted.

Main filesystem traversal is admitted as experimental after six initial-pair/error native comparisons; deeper metadata and open-file paths remain unvalidated. Worker continues the missing directory fetch/commit bodies. Touch and CASE workers continue their full-image gaps. Goal remains active, full completion 0/6.

Timer update source passed ARC EM Werror compilation and relocatable link in `em-sync-update-round`; strict source completion remains false.

### Wide conversion and Touch data ownership

EM conversion 0x30f2d8..0x30f2f0 now has source C for its full unsigned product and tail division facade. Two root/context reads and the actual denominator field are preserved. Division body remains missing; zero denominator behavior is not fabricated. Full six-candidate build `qualified-traversal-round` passed compilation and rejected strict completion.

Touch worker reduced 40 further bytes into sensor descriptor source and two source relocations, checked at authenticated flash load addresses. Independent source-owned reset-copy coverage is now 65 bytes; 899 bytes remain unowned. CASE application startup 0xa598 now has 8 prefix and 32 boundary comparisons, with 48 whole-graph imports. The alleged function 0x7214 is a loop interior under 0x7200; worker is preserving live context rather than assigning it a false C entry ABI. Full images complete remains 0/6.

### Wide division source reduction

Unsigned divider 0x302748/0x302844 now has source bitwise quotient computation. Its zero-divisor return preserves authenticated native R1:R0 0x7fffffff:0xffffffff; unsigned entry sets R4 zero so the sign-adjustment epilogue does not modify it. ARC EM Werror compilation and relocatable link PASS in `em-wide-division-round`. 2112 host arithmetic cases pass against Python arbitrary precision division, with zero behavior checked separately. This is not ARC native execution equivalence or producing-cycle equivalence.

Main directory-fetch integrated build PASS, strict exit 2. Commit wrapper is admitted after 20 bounded stock cases; remaining larger filesystem bodies are orphaning commit and deorphan. CASE boot option controls gained 80 randomized MMIO comparisons, separate whole graph now 42 imports. Three workers remain on Touch, CASE application and Main larger filesystem bodies. Full images complete 0/6.

### Controller queries and finite Touch frontier

EM readiness 0x30f568 and controller predicate 0x30f60c are source-defined and compile/link PASS in `em-controller-query-round`. Controller callback preserves native self-address R0. Host wide-divider verification is now reproducible with `em9305/verify_wide_division_host.py`, 2112 cases PASS; no native ARC execution assertion. Main deorphan source is admitted experimentally after 12 no-orphan/fetch-error/empty-directory native cases; deeper repair remains unverified.

Touch candidate builds 48/48 C units, zero unresolved providers; reset-copy ownership is 93/964 bytes. The remaining 871 bytes need product CapSense configuration/object bounds and final map. Retained generic PDL/MSC headers and examples do not supply product cycfg_capsense or product design. Worker shifts to codec missing providers while this specific Touch gap remains explicit. Full completion remains 0/6.

### State and group-mask providers

EM state predicate 0x302de4 and group-mask update 0x302e64 are source-defined, including dual-group wrapper 0x30f6ec. The wrapper applies group 1 followed by group 0 for selector 1, only group 0 for selector 0, and no update for other selectors. Volatile widths follow native words. Controller mode body 0x30f374 remains open: it contains the same unresolved multiply-class opcode family as the clock; no guessed product arithmetic is admitted.

Main orphaning-commit state machine is included experimentally after 15 initial failure/success/drop/simple-relocation bounded native cases; deeper parent/predecessor/move behavior remains unqualified. CASE idle/standby transitions have 20 and 2 bounded comparisons, respectively, with remaining application branches explicit. Full images complete remains 0/6.

### Native clock port and new vendor evidence

Downloaded the primary EM9305 v4.5.3 datasheet to `g2/research/corpus/em9305/vendor-documents`, with URL/hash/size manifest. Section 5.1.1 confirms DSP pipeline; it does not define the ambiguous multiply operation semantics. Native clock now has C MMIO reads and a named assembler major-6/minor-0x1c three-operand definition, preserving operation without replacing it with guessed arithmetic. ARC EM Werror compile/link PASS (`em-native-clock-port-round`); object disassembly confirms named instruction encoding with register allocation R0/R0/R2. Stock uses R0/R0/R1; operation class and operand values preserved, no byte-identical whole-function or runtime claim.

Codec worker source IRQ save/restore instruction sections match stock 10 and 6 bytes; remaining resident imports reduce from five to three locally. Main parent body is admitted experimentally after 8 bounded dispatch cases, full fetch-match addition after 4 callback cases. Directory relocating-commit is the local filesystem frontier. Full images complete remains 0/6.

### Full controller-mode source body

Controller mode 0x30f374..0x30f468 is reduced to C with explicit real refresh/enter-mode children. Its arithmetic preserves the same named native operation port, and its IRQ wait loop, timer correction fields and root reloads remain source-owned. ARC EM compile/link PASS in `em-controller-mode-round`; no native execution equality claim. Readiness 0x30f57c..0x30f60c likewise has C source with actual XB FU and carry-conditioned selection retained in inline assembler.

Main relocating-commit source is admitted after 18 attr/delete/compact and 12 erased traverse/CRC bounded native cases. It exposes four genuine remaining lowers: directory traverse, commitattr, commitcrc and splittingcompact. Counts are an expanding source graph, not a percentage of full-image completion. Source-complete images remain 0/6.

### Refresh source and resident codec closure

All six candidates compiled in `controller-relocation-integrated-round`, strict exit 2. EM refresh 0x30f9d0..0x30fa08 now has source C for four enabled slot updates and preserved incidental R0 return. Its actual slot updater 0x30f218 remains a contract. ARC EM Werror compile/link PASS in `em-refresh-round`, without native execution equivalence.

Codec resident IRQ/cache/queue/timestamp units compile and close five resident names locally, with startup/layout names remaining. Worker is resolving architecture flags before coordinator integration; only IRQ instructions are presently byte exact. Main commitattr, commitcrc and block CRC units are admitted experimentally after bounded cases; complete successful CRC path remains unqualified. CASE idle/service/OTA source portions still need composition and remaining policy branches. Full image completion remains 0/6.

### Slot update and application policy continuation

EM native slot update 0x30f218, metadata action 0x30f250 and inverse converter 0x30f2b8 now have C source. The slot stores its input before the clock call (native delay slot), converts elapsed input, samples stable timer words, and forwards actual observed timer-program registers to 0x3137b4. Timer programming remains a genuine child contract. Native execution equivalence is not claimed.

CASE full-battery and fake-standby portions have 20 and 96 bounded comparisons; separate graph has 57 genuine imports. Complete task composition, post-service branches and lower/data ownership remain. Main splitting-compact source is admitted after 72 split/dispatch bounded cases; directory traversal, split, compact and filesystem-size children remain. Full firmware completion remains 0/6.

Slot update/inverse/metadata-action units passed ARC EM Werror compilation and relocatable link in `em-slot-update-round`; strict completion remains rejected.

### Timer programming and integrated codec resident sources

EM native slot register helper 0x31377c and timer programmer 0x3137b4 now have C source; exact volatile byte/word write order, clri/sync/seti and incidental wrapper R0=0xf00844 are preserved. ARC EM Werror compilation and relocatable link PASS (`em-timer-program-round`); no native execution or hardware equivalence.

Codec resident builder integrated and architecture attributes retained ck803/ck804ef without warning; candidate nm undefined set is empty. Source timestamp arithmetic has 10007 host vectors, not native emulator proof. This graph covers a subset of multi-stage 318KiB payload and cannot establish whole-source completeness. Worker continues omitted stages/app/data. Main traversal and filesystem-size bodies admitted after 36 and 12 bounded cases; disk/move traversal still unvalidated, split/compact remain source frontier. Full images complete 0/6.

### Enter-mode and omitted codec stage source

EM enter-mode 0x30f468 and lock aggregation 0x302df4 compile from C in `em-enter-mode-round`, retaining separate IRQ-protected state-bit writes and ROM entry contracts. Lock callback dispatcher 0x302d20 is now source-defined for seventeen optional table entries and callback-self R0. Native execution/ROM producing ABI remain unqualified.

Codec UART first-stage added eight previously omitted C bodies, kept as a separate stage candidate in root builder. Fresh stage build PASS; remaining 24 decompiled stage bodies, reset references, UART SRAM base initializer, stage data and layout stay explicit. Main graph now source-defines all filesystem bodies locally, but final split/compact bounded qualification is pending and new sources are not yet admitted by root. CASE changed-status/charging policy has 576 bounded cases; full loop composition and final tail remain. Full images complete 0/6.

### Filesystem graph and resident ROM boundaries

Main LittleFS49-unit source set is admitted experimentally; allocation/split/compact bounded stock comparisons pass80/24/24, while nonempty attribute/global-state behavior remains unqualified. The remaining local imports belong to separately implemented semihost/logger providers. Full Main data/layout/application coverage remains open.

EM generated __udivsi3 import replaced with native DIVU at the recovered synchronization operation; Werror compile/link PASS in `em-native-divu-round`. Eight native IROM destinations now have explicit experimental C address bindings. These consume resident ROM and do not claim ROM body reconstruction or producing SDK ABI qualification. Full payload controller/application coverage and product data/layout remain incomplete. CASE terminal policy gained16 bounded cut cases, whole task composition and diagnostics/standby remain. Full images complete0/6.

### Current coverage audit

EM scheduler/controller candidate with ROM bindings compiles and nm undefined set is empty (`em-rom-contract-round`), but full-source gate stays false. Updated body-coverage-boundary with newly reduced native regions; envelope byte totals are static correspondence only, not execution equality or completion percentage. Wide division mathematical implementation is excluded from envelope totals. Corrected Touch source gate to its current 871 unowned bytes.

Codec first-stage coverage now 12/32 decompiled bodies (20 remain), with source bringup UART-base write; product mode initializer remains open. CASE shared-event/idle-standby gate has192 bounded cases, whole task still needs bridge/composition. Main worker advances full formatter source after filesystem closure, preserving typed full-grammar contract if retained source cannot prove its body. Full images complete0/6.

### Controller initialization source

EM controller initialization 0x30f4b0..0x30f568 is reduced to C with typed product fields, repeated root loads, exact individual field stores and native major6/minor0x1e operation. Actual configure-mode/timer-reset/finish/ROM children remain explicit contracts. Native execution and whole-record data ownership stay unverified. Codec stage1 now14/32 retained bodies,18 remaining, with actual mode initializer/reset references open. Main formatter capacity wrapper and callback admitted experimentally after24 bounded cases; the distinct3256-byte full grammar engine remains unresolved. Full image completion0/6.

### Controller timer initialization children

Controller initialization Werror compile/link PASS (`em-controller-init-round`). Source now defines preparation 0x30f288, config pair setter0x31183c and timer reset0x30fa40, including native MMIO widths/write ordering and incidental return values. Actual timer initialize/enable/IRQ-enable remain explicit children. Controller ROM init0x103c40 bound as resident IROM contract, not ROM source reconstruction.

Provider refresh: Ghidra MCP has no running GUI instance; REA list_documents has no active app target. This does not rule out retained headless providers or native tools. Main nonfloat formatter parser candidate has27 bounded native cases, floating branch remains open and parser is not yet admitted to root manifest. Full images complete0/6.

### Native timer controls and current parallel round

EM preparation/config/reset candidate compilation and partial link PASS in `em-controller-timer-round`; strict completion remains false. Added native IRQ enable 0x313c4c..0x313c74 and timer context initialization 0x313a0c..0x313ae2 as C, preserving byte widths, root reloads, IRQ save/restore, mode-specific store order and incidental returns. Fresh compile pending; source execution equality is not claimed. Timer enable 0x313ae4 and its actual calibration/mode children remain open.

CASE whole 0x7200 task control candidate compiles with75 genuine imports;128 loop and8 actual-entry bounded stock comparisons pass. Remaining work includes sensor effects, OTA product data, lower providers and startup/layout. Codec stage1 has17/32 seeded bodies plus2 recovered unseeded bodies;15 seeded bodies remain, along with missing reset target mapping and product descriptors. Main distinct five-file formatter candidate compiles with only compiler memclr import;27 core and24 outer bounded cases pass, floating equality is unqualified after native VFP execution limitation. This candidate is not yet admitted as a proved formatter implementation.

Completed chunks in this round are the bounded CASE control composition and codec reset/timer/dispatch recovery. Whole-image completion remains0/6; no reliable whole-image percentage can be inferred from these graph/body counts.

### Timer calibration and enable reduction

EM timer context/IRQ build PASS (`em-timer-context-round`). Timer enable/select/apply/threshold flags, dual calibration searches and delay probes, packed protected controller word and product-table dispatcher now have C source. Latest direct ARC EM Werror compile PASS; hardware LP_COUNT and two-no-op loop survive in object disassembly. Four actual ROM calibration addresses are explicit resident-ROM facades. Source receipt `em9305/timer-controls-source-receipt.json` records12 native bodies; bounded stock execution and full image remain unqualified. Strict full graph compile is being refreshed for latest source. CASE sensor refresh removes two real imports (75 to73),160 direct and32 changed-service bounded comparisons pass. Full images complete0/6.

### Controller level-selection chain

Source now defines native controller level selection0x30f794, application0x30f864, finish-init0x30f668 and mode action0x30f9bc. C retains branch-delay subtraction in table selection, signed table bytes, repeated mode/root loads, actual product table pointers and resident ROM addresses. Latest ARC graph compile is running; static native correspondence is not execution equality. Codec stage1 advances to25/32 retained labels plus2 unseeded bodies, one false split leaves6 actual seeded bodies; product descriptors/clock/transfer/reset continuation remain. CASE standby controls pass352 bounded comparisons; graph73imports. Main engine has3188/3256 unchanged native bytes versus Boot,25 BL relocation differences; product slots and lower qualification still required. Full images complete0/6.

Controller level graph compile/link PASS (`em-level-selection-round`), current source hashes match receipt. Three native gaps from controller init are now source-defined; IROM contracts remain resident dependencies. Integrated all-six candidate rebuild is in progress. CASE full service update0xce34 source compiles and passes128 bounded comparisons;77 genuine imports expose the next lower chain, product CRT/layout remains open. Whole images complete0/6.

### Source-owned controller root selection

EM native inverse time conversion0x30f2b8, numeric level map0x30f2f0, mode seed0x30fa78, product table root selection0x30f67c and period setter0x30f998 reduced to C. Table contents remain unowned; known address selection is source-defined, not fabricated initialization data. ARC compile pending. CASE service descendants prepare/sample/divide/delay/cancel pass128/80/128/64/64 bounded native cases;77 genuine imports expose deeper ADC/scheduler bodies and product data/layout still open. Full images complete0/6.

Integrated controller/stage1 rebuild: all six candidate compilation/link checks PASS, strict exit2 because0/6 full images are source complete. Table-seed ARC graph alsoPASS. Newly recovered native available-level/product-halfword queries appended to C; next compile pending. Codec reset continuation mapping corrected:0x10002900 belongs to authenticated stage2 atbase0x10002800, so source ownership is stage2 rather than ROM.

### Main full formatter experimental integration

Nine C units from Main full_formatter_native_candidate admitted experimentally with existing outer wrapper. They provide distinct Main full grammar/core/float/parser/integer/termination/runtime bodies, adapted from pinned native-corresponding IAR source; no duplicate simplified engine admitted. Structural verification reports23 relocated BL instructions (correcting earlier25 count),1270 matching relative instruction offsets,3188/3256 raw bytes exact and110-byte DP helpers exact. Bounded nonfloat27 andouter24 cases pass; floating stock execution remains SKIP due emulator map/VFP limits. Candidate-only partial link zero imports/duplicates, integrated Main build pending. Product handler/locale cells remain external runtime data; full Main completeness staysfalse.

### Startup/IRQ registration and build correction

EM startup0x302ae8, cold startup0x302be4, startup lock preparation0x302e14 and timer IRQ registration0x313904 now reduced to C; actual auxiliary registers, IRQ boundaries, callback arguments, resident ROM polls and MMIO widths retained. Startup and cold-stage ARC graph compile/linkPASS, native/hardware equality remains unqualified. Warm startup and early-lower bodies remain explicit. Main integration initially failed because default SP-only FPU setting rejected seven authenticated DP operations; builder now scopes fpv5-d16 to the exact native helper source, refreshed Main build pending. Codec typed PMU table416bytes and aux72bytes link to exact authenticated bytes;28/32 seeded bodies plus3 unseeded compile, one false split leaves3 actual seeded plusclock-rate body. Full images complete0/6.

Main full formatter integrated compile/link PASS (`main-full-formatter-dp-round`); nine native candidate C units admitted experimentally. Scoped DP assembler setting permits stock instructions, not hardware equality. Worker corrected stale relocation-count comments to23; no symbol/behavior changes. Remaining full Main product data/application/layout and floating runtime qualifications remain open.

### Warm startup and coverage audit

EM warm-start0x302c30, early IRQ setup0x3068c8 and architecture restore0x30690c now source-defined; current-hash ARC graph compile/linkPASS (`em-warm-startup-round`). Native stable timer loops, variable extraction operations, callback-self parameter, actual ST.AB/ST.AS address effects and IRQ transitions retained. Source/native execution equality remains unqualified. Static retained-label crosswalk: 1835 rows, 77 inside currently registered C envelopes, 1758 outside; inferred gaps are included, so these are not actual function counts or completion percentages. Broad remaining controller/application bodies are explicit. CASE deep ADC/scheduler graph now71imports with bounded checks, codec stage1rail-B29/32 labels plus3unseeded compiles, actual rail-A/dispatch/clock remain. Main whole body coverage audit ongoing. Full imagescomplete0/6.

### Boot IRQ source linkage

Native BOOT_IRQHandlerPMLHFColdStart0x302d40 and BOOT_IrqActionRoutine0x302d84 added as C, retaining snapshot mask, protected pending update, mode wake writes and actual callback-mask argument. Timer lower0x310990 was identified as already-recovered sleep_metadata_sync; the IRQ source now directly uses that provider rather than inventing a duplicate unresolved contract. Fresh compilation/link pending for this final naming correction. CASE notify/start/activation chunk compiles with75realimports;96x2wrapper and80x2core comparisons plus192queue/128wake cases pass. Remaining boot13/init18/IRQ9/policy30+ contracts and product bytes/layout remain open. Full imagescomplete0/6.

### Controller stack construction and Main watchdog

EM actual construction0x302a20..0x302ae4 C candidate compiles/links in `em-stack-init-round`, preserving observed20-byte descriptor fields and actual object/table addresses. Stock unassigned reserved byte7 remains an explicit lower contract; no zero-fill was invented. Allocator wrappers0x313f98/0x313fa4/0x313fb8 and config-selector0x30fd70 source-defined; final graph rebuild running. Typed actual Pal/LL/WSF lower contracts remain. IRQ provider graphPASS after reusing existing timer synchronization body0x310990. Main watchdog-start body0x53c2be admitted experimentally after42 native bounded comparisons, integrated build pending; product timer cell and real lower imports remain. Codec stage1 nowall31real seeded+4unseeded C candidates, runtime/data/load-map/final-layout stillopen. CASE deeper boot initialization/start/PSP handoff compiles with77genuineimports; productdata/otherbodies/layout stillopen. Whole imagescomplete0/6.

Main watchdog integrated build exposed duplicate selection: audio source archive automatically includes the new watchdog C unit, and root experimental manifest selected it again. Removed redundant manifest entry; the actual C body remains compiled via the audio archive. Corrected build running.

### Factory and radio configuration providers

EM selector/configuration/allocator graphcompilePASS (`em-stack-config-round`), three actual factory/radio/extended-address helpers source-defined andcompile/linkPASS (`em-config-providers-round`). Actual ROM factory pointer preserved; null fallbackbytes0..5 withfinal197 and radio0..15withbitmasks come from native stores, not guessed product data. Addresspacking0x304624, LlSetBdAddr0x30cf2c, PalBbLoadCfg0x30fd3c and WsfOsSetNextHandler0x3140b4 now C-defined; latest leaf graphbuilding. Whole initialization lower graph/product tables/startup records/runtime remains open. Main watchdog integrated sourcecompile/linkPASS after removing duplicate manifest selection. Auto-selected codec-reboot0x57a816 C passes42 bounded cases, actual power children open. Whole imagescomplete0/6.

Latest EM leaf provider graphcompile/linkPASS, current controller source hash matchescapturedreceipt (`em-stack-leaf-providers-round`). CASE taskframe/registration/reclaim source progress has96/128/48x3bounded checks and75trueimports. Firmware-level completion remains0/6.

### Platform system and timer initialization

EM PalSysInit0x3106e4, current-time0x310104 and WsfTimerInit0x314280 now C; native return/NOP hooks0x3101e4/e8/ec are source-defined from authenticated instructions, not fallback stubs. Actual baseband/timer initialization children0x310088/0x310128 remain typed lower contracts. ARC graph building. Main reboot+power chain three bodies424stockbytes has42/56bounded oracle cases, current integrated source building; actual GPIO child/productstate remain open. Codecstage2 has3/96seeded+7directunseeded, stack-byte0x4428ABI being inspected. CASE scheduler pool/heapfree fivebodies96caseseach,74genuineimports. Whole images0/6.

EM platform system/timer graphcompile/linkPASS (`em-pal-system-round`); source Pal baseband initialization0x310088 now added with exact configuration stores, address query, resident ROM call and nativeTRAP0 error instruction. Actual0x310814/0x310894 children/productbytes remain explicit; fresh graph compiling. Main codec reboot/power chain integratedcompile/linkPASS (`main-codec-power-round`); realGPIOchild/productcells remain. CASE pool-waiter wake96boundedcases and waitaliasreconciliation reduce trueimports74to72. Whole imagescomplete0/6.

Latest Pal baseband graphcompile/linkPASS withcurrentcontrollerhash (`em-pal-baseband-round`). Unassigned productbytes and actuallowerABI/nativeexecution remain unqualified. CASE census72trueimports=policy27/init18/boot16/vector5/IRQ4/CRTdata1/recordlog1, not a wholefirmwarecompletionpercentage. Whole images0/6.

## PAL random state and timer continuation

Completed source reductions: EM9305 native random seed reset 0x310814, state step 0x310850, address-word mixer 0x310894, timer initialization 0x310128 and its register children 0x310b54/0x310b84/0x310b94. Preserved volatile access ordering, architectural shifts, IRQ save/restore and SYNC; ROM 0x103b0c remains an explicit resident ABI facade. Random-state round compiled and linked, strict completeness exit 2; subsequent timer round receipt is separate. These are static native reductions, not ARC runtime or hardware equality.

Parallel completed chunks: codec stage2 reset descendants now six C units, 3/96 seeded plus 14 direct unseeded bodies; CASE physical PMIC primitives PASS 112 register-trace cases, combined graph 68 real imports; Main codec GPIO selector/critical/pin wrappers PASS 240/2/45 bounded cases. Remaining scope: codec 93 seeded labels plus unseeded/data/layout; CASE policy25/init16/boot16/vector5/IRQ4/CRT1/log1 imports; Main GPIO HAL, private application/data/layout; EM LL configuration/init/callback registration and WSF OS initialization plus full body/data classification. Full images complete: 0/6. These counts are scope inventories, not completion percentages.

EM PAL timer/random round receipt `g2/build/c-firmware/20261011/em-pal-timer-random-round/receipt.json` confirms selected graph compilation/link PASS and full-source false (strict exit2). Main GPIO HAL subsequent chunk completed with112 bounded native/source cases; source auto-selected. GPIO function lower now source-owned, product cells remain external.

## WSF pool initialization continuation

Reduced native 0x313dfc..0x313f54 and pointer alignment0x313f84..0x313f98 to C in controller_init.c. Preserved wrapping32-bit arithmetic, volatile pool metadata/free-list stores, caller register argument forwarded to resident allocator queries, optional128/32-byte clears and1024/256-byte region offsets, and failure/size-result behavior. Resident allocator ABI/product descriptor table remain external; native runtime equality unverified. Remaining immediate EM construction imports: LL config0x30bc60, LL init0x30c098, callback install0x30aeb8. Broad image body/data/layout coverage remains incomplete. Codec next console round compiled8 units,5/96 seeded+17 direct unseeded,91 seeded remain. Main osTimerStart now aliases already selected authenticated audio_timer_start;48 bounded native/source cases PASS. Full images complete0/6.

WSF pool round compile/link PASS, strict exit2 full-source false. Callback registration0x30aeb8 now source-owned exact pointer store (12-byte native envelope). Main PCM unregister296-byte body PASS216 bounded cases with product table external. CASE measurement/power/transaction/probe source round combined graph62 real imports; product configuration CRT ownership remains open. Integration build in wsf-main-gpio-integrated-round checks current Main and EM sources. No full-image completion or physical-device claims.

Codec stage2 subsequent wrapper/UART round now10/96 seeded+17 direct unseeded in9 C units;86 seeded still unowned plus unseeded/data/layout. Native formatter engine0x6b40(456 bytes) remains active reduction. Main I2S initialization216-byte outer now C,21 bounded child-cut cases PASS; exposes15 real child/data imports, worker graph92 unresolved. EM latest integrated callback/WSF graph compile PASS; Main integration live until terminal receipt. Scope estimates use actual body/import inventories, not total percentage.

Integrated wsf-main-gpio round terminal: EM9305 and Apollo Main selected candidate compilation/link PASS; strict exit2, both source_complete false. Receipt is hash-bound source snapshot while workers continue; it does not prove subsequently added units or whole-image completeness.

## LL configuration and nested critical sections

Completed sparse native LL defaults0x30bc60..0x30bd18, WSF critical enter/exit0x313f54/0x313f6c, PAL critical enter/exit0x310678/0x31069c. Selected ARC build PASS strict2. Sparse field host test256 cases PASS, includes untouched bytes and return value; independently transcribed native fields, not an ARC execution oracle. Added protected pending consume0x3106bc and authenticated literal-zero status helpers0x3106dc/0x3106e0; subsequent receipt separate. Remaining LL init0x30c098 and descendants require register-output ABI tracking (R2 across0x30c078) rather than guessed ordinary C prototypes. Full EM body/data/layout and producing ROM ABI remain open.

CASE combined graph55 genuine imports, including policy25/boot16/vector5/IRQ4 and bus config/motion/service-start/data/log single contracts. Main I2S IRQ82/start192 bounded comparisons PASS; six I2S code and nine product-data contracts on the current local chain remain. Complete full images0/6; all status gates remain incomplete.

EM critical/status round terminal compile/link PASS, source_complete false strict2. Next LL R2 contract traces through0x304764 to0x3156cc; ordinary scalar return alone does not qualify that native register dependency. Continue exact descendants before closing outer LL init.

## LL dispatch initializer and event callback continuation

Seven authentic LL callback-table initializers are C, with source-symbol relocations for13 callback bodies instead of raw executable byte reuse. Static return/store envelopes retained. First callback0x32eec8 now source-owned: event type0x21, two product flags, four exact payload writes, ST.AB old-base advancement then final -5 adjustment. Its event allocator0x32e454 remains a real import. Event send0x30ae90 reduced to queue/tailkick source contracts. Seed round compile/link PASS strict2; event round is a separate source snapshot. All runtime/producing ABI/full-image gates remain open.

Codec formatter engine/length retry overall compilation PASS after retained prior callbacks compile failure with empty log; numeric0x691c active. Main I2S prepare32 bounded cases PASS; remaining direct code clock_enable/acquire/configure/DMA_configure plus nine product data contracts. Full images complete0/6.

WSF event enqueue0x314008 and queue append0x31416c now source reductions: byte handler at event-4, node event-8, delay-slot next-null store before critical entry, head/tail ordered writes and critical exit return. These subsequent additions require next source build, not covered by earlier event-dispatch receipt. No native runtime equality claimed. Main I2S acquire32 bounded cases PASS; product pool remains source-data import. Three code children clock/config/DMA remain.

## WSF pool allocation continuation

Event queue source build PASS strict2/source_complete false. Native allocation0x32e454/0x313fd8 and full first-fit pool allocation0x313ce0 now C: 16-bit header allocation size, type/length bytes, free-list pop, ordered counters, optional histogram/miss statistics, byte peak and native signed MAX instruction retained. Product pool inputs and physical/native runtime qualifications remain open. Allocation round separate build.

CASE latest47 genuine imports after config/motion bus/service and event wrappers. Codec13/96 seeded +17 unseeded bodies in11 stage2 C units;83 seeded remain plus unseeded/data/layout. Main clock enable20/DMA60 bounded cases PASS; 970-byte I2S configure remains and product pin descriptors stay external. Full images complete0/6.

Pool allocation round terminal compile/link PASS, strict2 source_complete false. Receipt controller source SHA281890be17f1493d38ea626e366673ac3220bb39a949bc3255e53ea0daf1eb70 matches current file after volatile read-order correction. Codec decimal helper0x6774 restored to source call graph; overall codec/stage2 compilation PASS,14/96 seeded+17 unseeded;82 seeded remain. No complete component claim.

## WSF release and dequeue source round

Reduced0x313d98 full reverse-pool release (marker0xfaabd00d, optional stats, free-list prepend and outstanding decrement), event release0x314014, queue head removal0x314134, empty query0x314154, event dequeue0x313ff0 and unprotected peek0x31403c. Retained empty handler-output no-write and native return values, including release no-pool/no-match branches. Source-only native correspondences, ARC runtime equivalence unverified. Current release build checks source snapshot; subsequent additions checked separately if snapshot differs. Full source/data/layout classification remains open,0/6 full images complete.

Release round terminal PASS; current controller_init.c SHA matches recorded source, including six new release/dequeue helpers. Main six direct I2S lower code names now C; configure970-byte body192 nonfloating comparisons PASS, converter15 positive-domain cases PASS, double-path native equality remains open. Root integration build tracks actual common flags and current providers. CASE45 imports policy19/boot16/vector5/IRQ4/CRT1; physical timing and product data/layout remain open. Full components0/6.

Combined queue/I2S integrated round terminal PASS for EM and Main strict2. Audio inventory now applies source-specific DP VFP/core-register ABI flags to I2S configure, preserving native operation class and avoiding artificial soft-double imports; follow-up Main build separate. Codec cache/division round17/96 seeded+18 unseeded source bodies in12 units PASS;79 seeded remain. Full source images0/6.

## Queue insert and Main DP qualification

Main DP configure build terminal candidate compilation/link PASS, strict2/full-source false. EM native queue prepend0x3141c8, nested guarded insertion0x314190 and byte-indexed unguarded event lookup0x31401c reduced to C. No guessed locking simplification; retains nested append/prepend guards and empty handler no-write. Source snapshot build separate. CASE resume0xcb38 PASS96, queue-send0xc686 C opens six real descendants; graph49 imports is frontier expansion, not whole-body completion percentage. Main pin-function2724 bounded cases PASS; 674-byte power reconfigure lower active. Full images0/6.

WSF insert round terminal candidate compilation/link PASS, strict2/full_source false. Main next reconfigure/source-mux full C bodies bounded350/15 comparisons PASS, hardware clock behavior remains open; actual mux request0x539bbc still import. All six whole images remain incomplete.

## Unlink, event post and QP wake allocation

Queue unlink0x3141e4/event post0x314210 source round compile/link PASS strict2. Added wake dispatcher0x333d18 with real QP allocation, virtual dispatch object address and IRQ-protected wake counter; event allocator0x311060 includes first-fitting pool search, native header writes and returning assertions310/320. Pool get0x31166c remains actual lower. Subsequent build separate, static native correspondence only. Full ABI/runtime/data/layout coverage open.

CASE42 imports: policy16/boot16/vector5/IRQ4/CRT1. New scheduler descendants compile from native but bounded queue-send qualification pending. Codec18/96 seeded+22 unseeded C,78 seeded remain. Full firmware0/6.

QP wake/allocation round terminal candidate compilation/link PASS strict2/source_complete false. Next authenticated QP pool get0x31166c..0x3116f4 native inspected: captured IRQ, 16-bit margin/free comparison, returning assertions310/320/330, free count/low-water/link updates and duplicate SETI on assertion paths. Recoverable source remains; no blocker/exhaustion claim.

## QP pool get and initialization

Source-reduced authenticated pool-get0x31166c: captured IRQ, uint16 margin/free comparison, returning assertions310/320/330 and duplicate restore paths, link/free count/low-water updates. Pool initializer0x3116f4 includes observed low16 block threshold, four-byte rounding, returning precondition assertions100/110, exact DIVU arithmetic and volatile free chain. No implicit bounds/fault policy added. Static native reductions only, runtime qualification open. Separate builds retain hashes.

Main direct I2S code names source-defined, fresh worker partial link zero duplicate globals and91 real imports; remaining I2S names product cells. This is completed direct code chunk, not full Main. Worker continues other private bodies. Full images0/6.

## WSF task event and timer queries

QP pool initialization source round terminal PASS strict2. Added native task-handler table0x314250, task event post0x314258 (events in R1, exact wake-on-prior-zero), timer next0x3142a0 (presence byte and first delta) and expired timer dequeue0x3142c8 (zero-delta only, nested queue unlink, running-byte clear). Separate build checks source. Product table and timer engine/data/runtime remain open.

CASE38 true imports after boot/policy GPIO/clock bodies; periodic pulse24 bounded cases PASS. Codec stage2 worker reports24/96 seeded and22 unseeded sources pending fresh compile; linked PMU416+72 byte typed sections exactly match authenticated stage2 data. These data matches do not close whole-image layout. Full firmware0/6.

Task/timer query round terminal PASS strict2. Added authentic timer-stop guarded outer0x314314 and scheduler lock/unlock aliases0x31424c/0x31427c; stop engine0x333e24 remains typed actual lower and new build separate. Main PDM primary/alternate init474 native bytes total reduced42 bounded cases PASS, opens8 children+10 product data contracts. CASE descriptor bus/sensor init10 bounded cases PASS, opens9 true driver children; graph45 imports. All full-image source/data/layout and hardware qualifications remain open.

Codec command-lookup round compiled16 stage2 units PASS;24/96 seeded+22 unseeded,72 seeded remain. PMU488 typed bytes exact retained image match. EM timer-stop build live handle64998, poll same process before any restart. Full components0/6.

## WSF sorted timer engines

Stop outer/scheduler aliases build PASS strict2. Reduced stop engine0x333e24 full pointer search/unlink and running flag; start engine0x333dcc exact restart removal, sorted insertion with equal-tick order, current-time seed when queue empty; wrapping ms wrapper0x3142f8. Native correspondences only, runtime/product/whole-image gates remain open. Codec prospective35/96 seeded+23 unseeded pending compile. CASE43 imports, boot ambient stack selector ABI explicitly unresolved (no arbitrary zero), status leaves96 bounded comparisons PASS. Complete full images0/6.

Timer stop-engine build terminal PASS strict2; sorted-start round live79893. Codec control round19/19 stage2 units PASS,35/96 seeded+23 unseeded,61 seeded remain. Main PDM seven lowers bounded15/48/32/360/32/216/27 cases reported; latter three compilation pending; direct configure/start/clock-select still open plus typed product cells. Full images0/6.

## Periodic timer source continuation

Timer-start/update source rounds terminal PASS strict2. Added PAL elapsed0x3100f0, alarm0x3101c0, alarm callback0x333dc4 and full periodic timer0x333e4c. Preserve native threshold>=11, wrapping arithmetic, source callback relocation, native major6/minor1c product adapters and exact MMIO. No arithmetic/hardware qualification inferred from assembler success. Periodic build separate. Codec prospective40/96 seeded+23 unseeded pending help build. CASE42 imports, cold-reset option selector0 proven via CRT range/stack lifetime; direct entry unqualified. Full images0/6.

## Timer conversion/read helper continuation

Periodic timer source round terminal PASS strict2. Added actual time custom-scale0x3101b8 and seconds-wrapper0x314304 (native opcode adapter), raw elapsed0x3100f8, disarm0x3100fc, channel enabled0x3108d0 (native shift and byte truncation before truth), divisor0x3108e8 and product config read0x3108f4. These remain static/native instruction correspondences with hardware/runtime qualification open. PDM start144/config24 bounded comparisons PASS, whole direct code chain only clock selection still import; product data contracts remain. Full images0/6.

Codec help round terminal21 stage2 units compile/link PASS, no duplicate globals,40/96 seeded+23 unseeded and16 real lower imports. Remaining56 seeded plus unseeded/data/layout/runtime. CASE bus driver96 bounded child-cut cases PASS, reset/wait/apply wrapper source exposes clock setup/apply core;43 imports remains current. Timer conversions build live42085.

## Native label crosswalk refresh and PAL metadata

Timer-conversion build PASS strict2. Reproducible refresh_label_crosswalk.py derives static whole-label containment in individual source envelopes; before metadata additions141/1835 rows within,1694 outside (includes inferred gaps, not function or completion counts). Added metadata reset0x310914 preserving repeated pointer reads and old-base stores, unique linked registration0x310944 preserving IRQ and duplicate return. Subsequent all-six build live48417 may capture these additions; receipt hash determines scope.

PDM direct code chain complete11 units compile/link, remaining PDM imports product cells. CASE41 imports, bus start/frequency96 bounded cases PASS. Codec prospective46/96 seeded+23 unseeded pending builds. Full images0/6.

## Transport callback source continuation

PAL transport resume0x310798 outer reduced with exact mode/config read order, source callback relocations and actual configure lower0x304764. Callback triplet setter0x3047d4 reduced (index<=4, third/second/first volatile order), hook setter0x3047f0. All native correspondence/ABI qualifiers retained. Separate build checks source snapshot. Main PCM register288 bounded original/source cases PASS; full data ownership remains external. All6 integrated build codec/EM/touch/CASE selected PASS so far; bootloader/Main still live. Full images0/6.

All-six timers-pdm-codec integration terminal: selected codec/EM/touch/CASE/bootloader/Main candidate compilation/link PASS. Strict exit2 and all source_complete=false. Receipt hash-bound snapshots do not prove later worker/root source edits. New transport callback build live69569. Full-image completeness0/6; recoverable source remains.

## Controller timer IRQ source continuation

Transport callback round terminal PASS strict2. Added authenticated timer IRQ0x3110f4..0x31114c: MMIO3 store, two callback slots with actual callback-self R0 arguments, optional virtual callback R0=0, protected repeated wake-depth reads/decrement and MMIO1 wake acknowledgement. Runtime producing ABI/IRQ behavior remains unqualified; separate build. Main heap allocation30/pool wrapper48/PCM register288 bounded cases PASS; three TLSF actual lowers inspected against existing selected source corpus next. Full firmware0/6.

Timer IRQ source round terminal PASS strict2. Shared builder diff check clean. Codec prospective50/96 seeded+27 unseeded after IRQ/UART setup bodies, pending fresh compile; earlier irq/apply builds PASS. Main TLSF request adjustment168 bounded cases PASS, locate/prepare genuine lower bodies remain. Full-source components0/6.

## Native copy and transport configure outer

Reduced full native forward copy0x332fc4..0x33301c with matching-alignment prefix/word/tail paths and volatile access widths/order, no memmove substitution. Added transport configure0x304764 object clear, exact halfword/byte fields and16-byte callback record. Bytes13..15 retain native unassigned stack status; stack residue/indirect callback ABI remain unqualified. Real Pal transport initializer0x310730/state engine0x3156cc remain imports. No complete-body runtime claim. CASE bus-write96 bounded comparisons PASS,37 imports. Main TLSF locate312/130 bounded cases PASS, prepare allocation remains next code lower. Codec prospective53/96 seeded+29 unseeded pending full build. Full images0/6.

## Transport and allocation continuation

Main codec heap allocation code chain is completed in the selected graph: request adjustment, bitmap search, block preparation and split all have C providers. Controlled comparisons passed 168, 312, 130, 8, 140 and 112 cases respectively; selected Cortex-M55 partial link has no allocator code imports, while heap mutex/pool product cells remain. This is a completed source chunk, not a complete Main image.

EM9305 adds native transport initialize 0x310730, error hook 0x31585c, packet counters 0x31586c and delivery 0x31588c. The initializer preserves full-word destination and low-byte state selector tests separately. Delivery has an explicit internal register-preservation ABI qualification gap. The retained static crosswalk is now 150 of 1835 label rows inside C envelopes, with 1685 outside; this is not an image completion percentage. Transport state engine 0x3156cc and lower transport callbacks remain source work.

Latest worker snapshots: CASE combined graph 34 imports; codec stage2 prospective 53/96 seeded bodies plus 40 direct unseeded bodies, final build pending. Full-source components remain 0/6; data ownership, complete native census, final layout and runtime qualification remain open.

## Receive state and scheduler continuation

All six selected component compile/link results PASS in `heap-transport-stage2-integrated-round/receipt.json`; strict full-source exit remains 2. Later edits are separate source snapshots.

EM9305 transport completion/transmit/PAL read-write adapters and receive state machine 0x3156cc are now C. Source retains native signed MIN then halfword extraction, header validation, payload limits, first-fit event allocation, callback routing and error codes A0/A1/A2. Platform indirect-call ABI, caller-saved register contracts and product RAM/stack ownership remain unqualified. Fresh ARC build is running. The static label crosswalk now contains 156/1835 rows within C envelopes and 1679 outside; labels are not a complete code census or completion denominator.

Main private Audio source adds the voltage selector (120 controlled cases), pin clock teardown (30), full valid-task notification lower (324) and aliases to existing notification providers. Invalid assertion/fault paths and completed blocking waits remain explicitly unqualified. Latest local graph: 103 imports including newly exposed scheduler/product RAM cells.

CASE latest graph remains 33 imports after source-owned sensor commit, input initialization and system configuration, with true device children and timing tables exposed. Codec latest prospective source scope is 53/96 seeded plus 45 direct unseeded bodies; seeded remainder 43 plus unclassified bodies, data and layout. Full component completion remains 0/6.

EM transport state round reached terminal candidate compile/link PASS, strict full-source exit2. Later worker snapshots CASE32 imports and codec53/96 seeded+48 direct unseeded; these are graph/source counts, not whole-image completion.

## Transmit poll continuation

EM transport poll0x304698, idle query0x3047b0 and LL event kick0x3047c0 now compile/link PASS for ARC in em-transport-poll-round. Poll preserves five attempts, round-robin slot selection, callback output fields, packet indicator/header write and 255-byte send cap. Callback local layout/native internal ABI and platform runtime remain unqualified. Static crosswalk159/1835 rows within C envelopes,1676 outside; no image percentage.

Main adds source-owned message submission (96 cases) and temperature classification (24 cases), plus voltage alias to existing source. Latest local partial graph101 imports. CASE35 genuine source/data imports after bind core exposed callbacks; next worker round reducing those callbacks. Full-source0/6.

## LL dispatch construction continuation

EM source now represents the shared callback-pair installer0x30aec8, seven native LL dispatch initializers0x30a7bc/30a800/30a860/30a884/30a8a8/30a8cc/30a90c, transport handler registration0x30c078 and status wrapper0x3335c8. The native conditional-default tests and volatile store order are preserved; executable callback addresses are relocated C symbols whose unresolved bodies remain explicit. ARC build is running, and source was extended after build start so its receipt must be checked against current source hash. Static retained-label coverage162/1835 inside envelopes,1673 outside; no full census/completion percentage.

CASE four sensor callbacks compile and controlled native comparisons pass96 cases per family; no-effect status leaf authenticated; latest32 true imports. Main queue outer144 and dynamic constructor72 bounded cases pass, with selected static-constructor alias and100 local imports. Whole firmware source/data/layout still0/6.

## Further LL initialization and transaction continuation

Ten additional EM LL defaults/constructors source-owned and selected ARC compile/link PASS in em-ll-defaults-round; later dispatch record initialization, auxiliary callbacks and four native byte/halfword packing bodies await the new integrated build. Callback providers remain relocated source imports and native ABI/product state remain open. Static label envelopes168/1835 inside,1667 outside, not whole-image completion.

Codec watchdog chain checkpoint52compiled C units covers53/96 seeded+54additional native bodies. Remaining local link imports7application bodies and5binary64 compiler helpers; seeded remainder43 and code/data/layout census still open. Main CMSIS queue outer/static alias/dynamic constructor passes144/72 bounded cases; protocol transaction outer passes16cases with true five protocol descendants and product transport root exposed, latest local graph105imports. CASE sensor open sequence sourced with96 controlled child-cut cases and lower providers continuing. All full components0/6.

## LL feature and provider-chain continuation

All six selected components compile/link PASS in ll-construction-queue-codec-integrated-round, strict full-source exit2. EM provider-dependent LL feature-byte constructor0x30aa38..30ac40 is reduced to explicit C reads/branches/stores and separate ARC compile/linkPASS. Later ordered24-provider construction chain0x30c0e8 and WSF registration/handler0x30c0d4/30ac40 are C with current build pending; lower event processing0x30a930/30cd80 remains explicit. No runtime oracle or final ABI/data-layout qualification is implied. Static label crosswalk170within/1665outside of1835 rows remains incomplete, not an image percentage.

Codec55Cunits selected linkPASS with4application+5compiler-helper imports;53/96seeded+57directadditional bodies. Parser1602host cases pass against instruction-derived native character-table model, not C-SKY execution. CASE finish parser192cases, its transfer guard96cases and further source-owned probe/reset/signal reduce graph to34imports. Main UART session16controlled cases and source-defined code providers expose actual product RAM cells, latest107local imports. Full-source components0/6.

## LL command dispatcher continuation

The ordered provider chain/WSF handler source snapshot passed selected ARC compile/link in em-ll-provider-chain-round. Later native LL dispatcher0x30a930 and queue/received message routers0x30cd6c/30cd80 are C and building in em-ll-dispatch-round. The dispatcher retains native queue ordering,35-provider scan, byte/halfword command descriptor, rejected-command event, ST.AB old-base stores, delayed R0 values and wraparound elapsed maximum. Internal callback ABI, descriptor ambient byte and full runtime equivalence remain unqualified; real lower providers0x30a484/30a564/32e5d4 remain imported. Static label rows171inside/1664outside, not full component coverage.

CASE readiness child source and bounded96case oracle pass, with33genuine imports. Main transaction construction9case oracle and UART session16case oracle pass; partial packet pack alias has an explicit diagnostic-path gap and is being replaced with complete native logging branches. Full components0/6; no flash or hardware behavior claim.

## LL memory and initialization entry continuation

EM LL dispatcher selected ARC compile/linkPASS in em-ll-dispatch-round. Two memory construction bodies and base/capability pointer setters compile/linkPASS in em-ll-memory-construction-round. Later descriptor construction0x30bfec and LL entry0x30c098 are C and currently building; native call-delay-slot0x30c0aa supplies first transport halfword before0x30c078, preserved in source. Ten genuine memory children and common/radio initialization bodies remain source imports. Static retained label counts175inside/1660outside, not full census or runtime qualification.

Codec prospective source advances55/96seeded (41uncovered) and64directadditional bodies; terminal updated build awaited. Main packer diagnostics completed with35native cases covering log masks/args/packet bytes, in addition to reused80algorithm cases. CASE sensor validation128 and clock selectors192 controlledcases pass, four product tables remain typed contracts;34local imports. Fullcomponents0/6.

## LL memory-provider continuation

LL initialization entry selected ARC compile/linkPASS in em-ll-init-entry-round. Three concrete12/72/8-byte record memory providers0x303340/303380/3033c0 now source C, preserving failure-time pointer stores, metadata clear order and low-halfword consumed returns; their build is in flight. Three further capability providers0x307158/3071a4/3071f0 are C: optional912-byte region, nine aligned buffers with re-read configuration stride, and aligned lower region preserving original end. Two true lower providers32d524/31bc28 exposed; final native ABI/runtime/layout remain open.

CASE two attributed STM32G0 tables are now typed C constants, source/native bytes matched; bus clock source reduces local imports29. Main completes packet and response diagnostic branches;85fresh controlled cases pass in latest protocol chunk. Full-source components0/6.

The em-ll-base-regions-round receipt is terminal compile/linkPASS and controller_init.c hash matches current source, including all six new memory-provider bodies. Static retained-label crosswalk181inside/1654outside of1835rows. This establishes selected target compilation, not native runtime equivalence or full-source completion.

## Capability-region and codec link continuation

EM region constructors0x30705c/3070fc selected ARC compile/linkPASS; later0x307210/30723c halfword-sized and queued spare regions are source C and awaiting current all-component integration. All native pre-rejection pointer/queue side effects and volatile count re-reads are preserved; runtime, final layout and lower provider qualification remain open. Static label rows185inside/1650outside, not full component percentage.

Codec69Cunits compile/linkPASS with0application imports and5binary64 compiler helpers. Manual body ledger65/96seeded+66additional is superseded for exact symbolic attribution by an observed70/96 address-suffixed defined-symbol crosswalk,26unmapped entries; this is not verified body/native equality. Fresh full-source census worker continues. CASE bounded waiter notification192cases passes, graph28imports;3attributedclock tables exact bytes and2product timing tables unresolved. All full components0/6.

## Lower LL region continuation

EM native0x31bc28 and0x32d524 lower queue-region providers are now C and building in em-ll-lower-regions-round. Source preserves132-byte block sizing, partial queue writes on capacity failure, volatile count re-reads and custom0x06/0x1e opcode through the selected adapter; arithmetic/physical opcode semantics remain unqualified. This closes the two previously imported memory children at source level, pending target build. Static label crosswalk187inside/1648outside; neither label rows nor source envelopes prove full image completion.

Main transaction extraction body now includes all status and diagnostic paths;50fresh stock/C comparisons pass with allocator/log/dump ordering. CASE additional IRQ source passes96bounded cases; redundant waiter provider discovered at link and removed in favor of pre-existing576-case source, latest27true imports. All six full-source components remain0/6; current integration session60740 remains confirmed live.

## Typed Touch channel, indirect CASE and font callback round

Three parallel component workers continue under the active source-reduction goal.
Touch now closes 431/964 initialized reset-copy bytes: the new 28-byte LP channel,
its two ROM electrode descriptors and two pin descriptors use real C relocations.
All channel/ROM bytes match authenticated stock in the bounded fixture; its typed
four-byte MSCLP lock is independently attributed to the pinned PDL header.
Touch's 52 selected units compile with zero imports. Remaining reset-copy bytes:
533; the 426-byte historic zero region still lacks exact allocation ownership.

Codec's settled UART async snapshot compiles 83 inputs with 12 genuine imports
and coherent source hashes. Unique conservative XIP bindings are 39/362;
SRAM attribution is 115/151 raw labels, with at most 20 plausible remaining
body gaps after data/literal exclusions. These counts do not measure all native
behavior or the independent image-B frontier. A later SRAM chunk is in progress.

CASE startup passes 128 boundary cases, and its task-return fault now preserves
both native branches: the first 16 instruction bytes match stock and five
controlled runtime cases pass. The clean experimental ELF has zero undefined
symbols. Indirect callbacks gained bounded tests, while the continuing policy
loop's stack/reentry behavior remains an explicit whole-body gap.

Main's three font callbacks (glyph initialize, bitmap initialize, outline render)
and italic shift are C. The local 140-unit M55 graph compiles and links with zero
duplicates. Compiled-C/stock checks pass 6 glyph, 5 bitmap and 3 outline fixtures;
the stroke path remains unqualified. Its local font/LV graph has 13 deeper code
lowers and 14 data/runtime contracts, separate from the full Main import census.

Full source-complete components remain **0/6**. The fresh all-six
`channel-indirect-font-round` integration is running; its receipt, once terminal,
must be read with source-coherence results before updating aggregate counts.
Ghidra-MCP discovery at 2026-10-11 09:37 UTC found no running instance.

The `channel-indirect-font-round` all-six integration is now terminal: every
selected target candidate compiles and relocatable-links; no complete source
payload is claimed. `all-six-current-build-checkpoint.json` records the exact
receipt and selected symbol counts. Codec's source-coherence guard passed with
no changed paths. Later worker snapshots remain separate from this integration.
CASE's integrated experimental absolute ELF has SHA-256
`9186f562086aa99e22ee72d18c2290d255e2bca28ae7056ff28d3b51d6aa6f09`.

## Native reset, CRT, outline and Boot data fidelity round

Fixed selected Touch reset body: it now performs native DSB/AIRCR/DSB/NOP
sequence rather than the earlier offline infinite-loop boundary. Four actual
compiled-C/stock emulator cases pass. Application PM descriptor/threshold add
30 exact initialized bytes and the callback's four native bytes. Fresh genuine
GCC CRT source rebuilds add 152 exact native code bytes and eight init/fini
pointer bytes to the selected archive. Natural typed uint32 alignment closes
three additional data bytes. Touch initialized reset closure is now472/964,
492remaining; the selected candidate has53 C units plus10 source providers,
zero strong imports and four explicitly reported optional weak references.
The new app history decoder API was removed from firmware-source selection.

Codec progresses to121/151 conservative SRAM body bindings; known data/literal
exclusions leave at most10 plausible genuine SRAM body gaps. XIP41/362 explicit
unique bindings and the independent image-B frontier remain separate.
Main continues FreeType outline storage/transforms/stroker bodies and actual
class-table relocations; bounded call/state oracles pass, deeper geometry and
full-image source/data ownership remain open. Boot gained the genuine native
thread-name getter and corrected two callback-table relocations: three distinct
native BX-LR entries now have three distinct C providers. The bounded 1371-byte
initialized-data oracle compares without pointer normalization, under explicit
symbol bindings; actual final source layout remains open.

`native-reset-crt-outline-boot-round` is terminal all-six candidate compile/link
PASS. Selected defined/strong-unresolved counts: Codec210/12, EM527/75,
Touch227/0 (+4 optional weak), selected CASE70/3, Boot911/3, Main1302/476.
The experimental CASE ELF separately has zero imports. Codec input coherence
passed. `all-six-current-build-checkpoint.json` binds these counts to the exact
receipt; later worker changes remain separate. Source-complete components0/6.
The subsequently proven three alignment bytes reduce current Touch data gate
from495 to492; the captured integration retains its earlier conservative gate.

## Position-history/UART/stroker/dispatch round (2026-10-11)

Completed scopes, not full components: Touch typed position history header
adds eight exact reset-copy bytes with a true pointer relocation; current
initialized closure480/964, remaining484. Touch has54 selected C units and
10 genuine source provider objects, zero strong imports, four optional weak
CRT references. Codec adds audio record callback and ambient-register IRQ
source; latest worker snapshot89 inputs,13 genuine imports, conservative
SRAM123/151 identified body bindings and at most8 plausible residual SRAM
bodies after20 nonbody exclusions. XIP/image-B are independent frontiers.
Boot UART RX/status/dispatch plus DMA leaves compile; selected336 units
combine to919 definitions/3 resident ROM contracts. Bounded RX6/status6/
dispatch14 cases pass; final placement and whole-image census remain open.
Main/Audio adds four stroker source units and32 bounded native/C geometry
cases;173 Audio units compile/link and local font/LV frontier32 remains.
EM command0x2019 and branch adapter are now C; target compile/link529
definitions/74 genuine imports, with six controlled C source-contract cases
(no native emulator qualification). Complete source components remain0/6.

`uart-stroker-position-history-round` is terminal all-six candidate compile/link
PASS. Selected definitions/strong unresolved: Codec216/13 (source-coherent),
EM529/74, Touch229/0 (+4 optional weak), selected CASE70/3, Boot919/3,
Main1322/477. The separate CASE experimental absolute ELF still has zero
imports. `all-six-current-build-checkpoint.json` binds these numbers to the
fresh receipt. Worker followups are active: Codec clock-frequency body is
under a separate build; Boot continues oracle qualification and census;
Main/Audio continues vector angle/length and geometry. Later changes are
separate from this captured source snapshot. Source-complete components0/6.

## Subsequent event/clock/geometry reductions (2026-10-11)

EM332394 event conversion completes another native-derived C scope,18
controlled C cases; ARC530 definitions/74 imports. Child30c2e0 fallback
is separately C with7 controlled cases, three honest slot-accessor imports,
no arithmetic guess for the native custom instruction. Target build receipt
`em-controller-fallback-round` is terminal PASS,531 definitions/76 genuine
imports; it remains separate from all-six integration.
Codec clock routine10025210 is now selected source,90 C-SKY inputs,
coherent link,12 imports (`codec-clock-frequency-round`). Corrected SRAM
census is151 raw labels =27 data +124 code labels, with123 code labels
bound through selected providers or explicit ABI aliases. The sole unbound
code seed10025574 is the compact IRQ/toolchain issue; bindings are not
whole-body equality proof. XIP44/362/image-B288/data relocation remain open.
Main/Audio now178 C units target-compile/link without duplicates; actual
native/C angle/length105 each, anglecore129, arc10, trig68 each, cubic6
bounded cases pass. Local font/LV29 contracts remain (18 code/callback,
5 flash,6 runtimecells), plus full Main graph/data/layout. Boot UART row6/
dispatch16 are qualified bounded oracles, while389 catalogue leads need
semantic source attribution. Full source components0/6; three workers active.

## Slot accessors and memory-copy round

EM three slot accessors now compile from C with named MPYUW inline ISA; all
three compiled multiply encodings match native209f040e. Target graph534/73
in `em-slot-accessors-round`, closing the prior fallback's three child imports.
Codec SRAM catalogue correction remains123/124 code labels bound, plus27 data
labels, independent XIP/image-B/layout work. Boot adds genuinely absent native
4276bc overlap-copy from C,2,016 bounded native/C memory/alignment cases pass;
selected337 units, anticipated combined920/3 (full integration not recaptured).
Main/Audio now180 C units compile/link; outside-join11 native/C cases pass,
local font frontier27 (16 code/callback,5 flash,6 LVcells). Conic/cubic remain
principal stroker geometry gaps. Full source components remain0/6.

## Command/slot graph closure

EM native30e054 command controller and3072f0/307434 children are now C.
Thirty-byte command packing has7 controlled contract cases; all four recent
EM verifier scripts pass38 total controlled source-contract cases. The two
new slot children retain named MPYUW and true indirect callback ABI plus a
hash-bound15-byte nonexecutable operation map. `em-command-slot-closure-round`
is terminal ARC compile/link PASS,537 definitions/72 genuine imports. This
snapshot postdates the last all-six integration; do not substitute its counts
into the older receipt. Full source components remain0/6. Custom final source
images may relocate function bodies within actual flash/RAM/entry constraints;
stock body-envelope size mismatch alone does not preclude a modified firmware.
Boot worker is now constructing actual symbol-based co-placement rather than
only explicit stock-address proof fixtures.

## Response dispatcher, lower commands and co-placement round

Completed EM C scopes:332490 private flags,332278 five-command responses,
30c33c payload task command,30e350 pair setter,306ea8 slot-time getter and
30c6d4 query converter.19 new controlled dispatcher cases pass (57 across
five recent isolated C contract suites). Target `em-slot-command-lowers-round`
compile/link PASS543 definitions/74 real imports; compiled named MPYUW/MPYDU
and the query's paired-register shifts/store inspected. Runtime equality is
not claimed for the newest ISA lowers. Boot338-unit selected source now has
a concrete partial source co-placement ELF at410000, with source-symbol
relocations for all34 initialized callback words and127096B flash LOAD.
External256-word vector table/IRQ frontier and final absolute-reference
consumer proof remain; GC/layout experiment is not full source completion.
Main principal stroker C graph is closed locally with connected8-case oracle;
local font code7/data11 remain after bitmap lifecycle, format, slot-clear,
metric renderer and stride reductions. Latest local build186 units predates
some newer files. Codec XIP57/362 bindings plus newer mode-init build pending;
compact SRAMIRQ, XIP/B,data/layout stay open. Full source components0/6.

## Boot full-vector co-placement followup

Inspected `apollo/boot-coplacement-fullvectors/receipt.json`: bounded linked
source ELF cf370de29e1c0e77757002f575ceea814b0ce4d0113cee3c40f3d02bd2cf55a7
at410000,132912 file bytes vs148599 stock occupied bytes,256 vector words
checked,10 distinct external IRQ source handlers, all34 initialized callbacks
relocated to live source symbols. Source342 units/932 providers. GPIO IRQ
helpers have66 bounded native/C cases. Boot reset now422a75. This is a
concrete partial source layout experiment; GC/whole-source coverage, ISR
composition, absolute initialized words and device behavior remain open.
Main latest188 C units strict target compile/link; localfont7 code/11 data
remain. Full source components remain0/6, goal and3 workers active.

## Flags/cipher/timer and font/Codec round

Completed EM source scopes: cipher wrapper30b644, flags command30d54c,
flags latch308b74, slot adjust317c10 and timer application308708. Flags/cipher
have23 controlled C cases; timer named compact instructions7a6a/7a2c and native
scaled stores were inspected in actual target output. Latest target compile/
link `em-slot-timer-apply-round` PASS548 definitions/71 genuine imports; full
runtime/private-product qualification remains open. Main/Audio latest193 C
units strict target compile/link, localfont2 code +11 typeddata contracts;
new native allocation6, preset36, copy8 bounded cases pass. Codec latest94
primary source inputs coherent target link,20 true imports; XIP64/362 source
bindings, independent image-B/data/layout and SRAMIRQ remain open. Boot now
source-backs ten locale pointers and six stream-mode strings;343 selected
units partial co-placement132940B. GC and true hardware partition capacity
must be audited separately from occupied stock file length. Whole-image
source/placement/device claims remain false; full components0/6, goal active.

## Fresh six-component source snapshot and stream control

All six candidates compile/link PASS in `stream-mask-font-boot-relocation-round`.
Selected definitions/imports: Codec246/22 (source coherent), EM552/73,
Touch229/0 plus4 optional weak CRT refs, CASE70/3, Boot937/3, Main1360/459.
Full components remain0/6. Main flash restore byte correction has7 controlled
native/C cases. Codec XIP70/362 bindings; Boot partial GC layout141248 bytes
and22560 conservative partition headroom, with669/934 providers retained.
Root reduced native332a78 six-halfword stream decoder to C;256 bounded
data-contract cases and11 controlled dispatcher cases PASS. Its target
build is a later separate snapshot, pending. Three workers resumed watchdog,
Boot pointer relocation, and Main flash HAL children. No whole-image or
hardware equivalence claim follows from these selected-source receipts.

Stream decoder332a78 target build `em-stream-control-round` PASS553 selected definitions/72 genuine imports;256 controlled data-contract cases and11 dispatcher cases PASS. Fresh unified snapshot remains552/73 because the decoder was added after EM capture. Codec separately advanced to97 source inputs/19 imports and74/362 XIP bindings via watchdog bodies. Full source components remain0/6; remaining source/data/layout work and three workers continue under the active goal.

## Three-stream command and immediate children

Root reduced native30b7ec command,30e510 gate,318200 active-address scan,
30e4dc kind policy,332f04 header check,30a6b4/332f00 control validation,
307970/307a48 enable/disable and307a28 config copy. The exact12-byte ROM
pointer table3357a8 is source owned; its three RAM records remain open.
Private major6 product operations and named MPYUW remain actual ISA adapters,
not guessed arithmetic. Target `em-stream-command-lowers-ordered-round`
PASS562 definitions/71 genuine imports.82 controlled command cases,898
lower contract cases and256 decoder cases pass; these are actual selected C
with controlled children/normalized host addresses, not native runtime equality.
The first lowers build was deliberately interrupted after a native operation
ordering correction; only the settled ordered-round terminal receipt is used.

Boot separately progressed to345 units/939 providers and partial GC placement
152780 bytes,11028 conservative partition headroom,757 live names;182 absent
names still require classification. Codec99 inputs/23 imports, XIP78/362
bindings;284 raw XIP labels unbound plus image-B/SRAMIRQ/data/layout.
Main/Audio file facade and LittleFS wrappers/operation cores progressed,
connected6 cases with opencfg child controlled; deeper fs descendants remain.
Full source components0/6; goal and three workers remain active.

## Connection dispatcher and begin/cancel source round

Source-reduced native330440..3304f0,30b480..30b53c,30b53c..30b570
and30e524..30e538. Preserved sparse stack/message fields, response command
reloads and exact source child calls; changed32ef10 declaration to its actual
two-argument result ABI. `em-connection-begin-round` target compile/link
PASS566 definitions/71 genuine imports.10 controlled dispatcher cases and21
begin/cancel cases PASS; these are selected C under controlled child contracts,
not native runtime or hardware equality. Genuine30cf40 update and32ef10
fallback, stream processing and other source/data/layout remain.

Codec's connected SNPU and NPU register bodies now101 primary inputs/18
imports coherent target PASS; XIP86/362 source bindings,276 raw labels unbound
(code/data mix), plus SRAMIRQ,image-B/data/layout. Boot platform initializer
now uses authenticated97x12-byte source GPIO table,21 linked diagnostic
strings and16 bytes of ADC/power input data; partial layout154712 bytes,
9096 conservative headroom,782 live names and181 absent needing classification.
Native external descriptor GPIO range boundary is preserved pending evidence.
Main/Audio206-unit archive PASS after opencfg and7 LittleFS helpers;6 connected
file oracle cases still cut real remaining descendants. Full components0/6;
goal and three workers active.

## Connection mask and callback publisher round

Native30cf40 mask update and3087a0 callback publisher reduced to C. Exact
ordered byte loads assemble bounded unsigned five-byte input; genuine count
30c414 remains imported. Publisher captures initial count, stores high before
low, visits real callback pointers, reloads count and retains first nonzero
low-byte result. `em-connection-mask-round` compile/link PASS568 definitions/
70 genuine imports;2056 controlled C cases PASS (normalized fixed RAM/pointer
width, controlled count child; no native-runtime/hardware equality claim).
Pinned primary GCC ARC machine description archived underarc-gcc-semantics,
commit940a1c98e745d6c8100def432655c0165acb6cc1 with content hash receipt.
Its MACU/MACDU unsigned accumulator definitions support the bounded byte
packing derivation; this single compiler reference is not a firmware provider.

Codec102 inputs/22 imports target coherent PASS; XIP88/362 bindings,274
unbound raw code/data labels. KWS loader/task-copy source scope now present;
five model-size getters remain and three native ambient task words remain
unqualified. Boot textual stock-flash refs reach finite frontier: hardware
VTOR plus genericGPIO external-descriptor boundary, preserved pending ABI
evidence. Latest partial GC154720 bytes,9088 headroom,785 live names/181
absent requiring classification; whole catalogue mapping continues. Main
Audio208-unit archive PASS, connected11 file cases;dir_find/demove sourced,
superblock recovery and wider descendants/data remain. Full components0/6;
active goal and three workers continue.

## Legacy connection dispatcher and response formatter

Native32ef10..32f0a0 and32f34c..32f494 are selected C. Dispatcher follows
the18-entry native table and separate status/response paths; formatter reloads
command after allocation, writes exact sparse payload fields and uses genuine
query children.42 controlled routing cases and31 formatter cases pass.
`em-legacy-dispatch-round` target PASS569 definitions/80 true imports;
`em-legacy-response-round` PASS570/84. Genuine import count rose as connected
children were exposed, not as fabricated bodies removed. Full runtime/native
equality unqualified; query outputs and remaining children need source proof.

Codec104 inputs/18 imports coherent target PASS, XIP95/362 source bindings
(267 raw code/data labels unbound); model sizes and audio-input outer pair
source-backed, initialize/exit children remain. Loader native ambient task
words now an explicit unresolved input, not uninitialized scalar reads or
defaults. Boot two no-machine labels matched to selected compiled LittleFS
static lfs_bd_flush/lfs_ctz_traverse: missing attribution368→366, not new
missing body claims; partial placement unchanged154720 bytes/9088 headroom.
Main/Audio209-unit strict target archive PASS; superblock recovery C closes
immediate consistency graph, connected13 bounded cases remain descendant cuts.
Full source components0/6; goal and three workers active.

## Limits and capability query source closure

Native30c714..30c724 and30c78c..30c7b0 now selected C. Preserved two ordered
halfword copies, final return value, ADD1 third-operand shift (+112), and
output reloads needed for destination aliasing. `em-connection-queries-round`
target compile/link PASS572 definitions/82 genuine imports.65552 controlled
C contract cases PASS, including every16-bit input and output alias layouts;
not native runtime/hardware equality. Genuine remaining query/connection
children,32f494,source data/layout and full EM corpus remain open. Boot
another existing source predicate attributed;365/903 native catalogue entries
lack machine crosswalk,181 absent names include inlining. Neither is a count
of proven missing bodies. Full source components0/6; active goal and three
workers continue connected source reductions.

## Quality/version query and signed slot byte round

Source-reduced306ff0/307030 signed byte getters using named MPYUW stride,
quality query30be68 and version query30beb4. Preserved critical-section entry/
exit, link max/active gates, all invalid defaults0x7f/0xe2 and selector1
literal20. `em-version-quality-round` target PASS576 definitions/80 genuine
imports.14848 controlled C cases PASS across all byte values, bounded slots,
active/max/selector/error branches and output-before-critical-exit contract;
not native runtime or hardware equality. Genuine connection queries/ops and
32f494, source data/layout/full corpus remain. Codec105 inputs/18 imports
coherent target PASS, XIP96/362 source bindings; AIN reset is next authentic
MMIO frontier. Boot four existing source providers mapped,364/903 machine
attribution gaps remain;181 absent linked names include inlining. No count
of proven missing bodies claimed. Full source components0/6; goal/three
workers active.

## Remote feature query and paired slot getter

Native306ebc..306ed4 and30bbbc..30bc04 now selected C. Named MPYUW912
stride, word69/70 scaled offsets276/280, paired uint64 ABI, native five-byte
store order and invalid-link untouched output preserved. Target
`em-remote-features-round` PASS578 definitions/79 genuine imports;3584
controlled C cases PASS (normalized RAM/bounded stride and critical/active
children, not native runtime/hardware equality). Broader connection/private
dispatch bodies, data/layout and full EM remain open.
Codec AIN reset native0x10203c88 resolves misleading retained decomp loop: exact
MMIO reset/status-bit8 poll/remaining writes now C;106 coherent inputs,17
imports target PASS,XIP97/362 bindings (265 raw code/data labels unbound).
Hardware status loop remains runtime unqualified; audio initialization and
callback/data ownership continue. Full source components0/6; active goal
and three workers continue.

## Private dispatcher source closure

Native32f494..32f64c now C: sparse20-entry private table, signed byte args,
ordered config writes/reads, command reload after allocation, exact response
suffix pointer and genuine descriptor/query contracts. Target
`em-private-dispatch-round` PASS579 definitions/84 genuine imports;52 controlled
C cases PASS (normalized fixed RAM and controlled children, not native runtime
equality). Additional imports exposed honestly;28-byte descriptor child
output and remaining private operations need source qualification.

Codec107 coherent primary inputs/17 imports target PASS; audio hardware
initializer102047e4 and source callback relocations implemented. True native
no-effect10207020 sourced but absent retained seed catalogue, excluded from
XIP98/362 seed binding count.264 raw seed labels unbound; actual config body
10207234 and broader source/data/layout/hardware remain. Boot reproducible
call-edge frontier identified91 unbound entries with linked selected callers
(before latest mappings) to prioritize attribution; absent/static/inlined
provider cases remain classification, not proven missing C. Full components
0/6; active goal and three workers continue.

Private descriptor303290 is now exact C runtime28-byte copy; em-private-descriptor-round PASS580 definitions/83 imports,52 controlled private cases now include actual descriptor body. RAM descriptor ownership remains runtime/data frontier. Fresh all-six capture held before start for confirmed qsort arbitrary-width gap; Main dir_find callback comparison corrected and focused native/C checked18 connected cases. Codec108 coherent inputs/32 true imports, full audio config body exposes16 children; XIP99/362 bindings. No full component complete; three workers and goal active.

## Fresh all-six snapshot: private descriptor / audio configuration / wide qsort

The receipt `g2/build/c-firmware/20261011/private-descriptor-audio-config-wide-qsort-round/receipt.json` records six candidate compilation/link passes, with **0 complete source payloads**. Selected definition/import counts are recorded in the authoritative checkpoint. Codec source coherence is true; Touch has zero strong imports and four optional weak toolchain references. The standalone CASE experimental ELF is separately qualified. This snapshot contains EM's 28-byte runtime descriptor reader (52 controlled connected dispatch cases), Codec's 108-input configuration graph, Main's corrected filename comparison (18 native/C connected cases), and Boot's arbitrary-width qsort (27 exact whole-record cases). Boot's separate partial co-placement is 153,248 bytes with 10,560 bytes conservative headroom.

After capture, all three workers resumed. Boot is restoring authenticated assertion paths; Codec is resolving configuration children; Main is investigating its wider 452-import graph. Root reduced native30cef0's signed validator to C and verified 2,560 controlled cases; its dedicated target compile is separate from this frozen receipt. Native309aa4 remains a genuine substantive import. Compilation and bounded contracts do not establish whole-image equivalence or hardware operation.

## All-six signed/analog/HUB/assertion/timing snapshot

`g2/build/c-firmware/20261011/signed-analog-hub-assert-timing-round/receipt.json` records six candidate compile/link passes and0 complete source payloads. Authoritative checkpoint refreshed from that terminal receipt. Codec114inputs/19imports snapshot is coherent; EM591definitions/79imports; Main1409definitions/449imports; optional weak Touch references remain distinct from strong imports. CASE standalone ELF remains separately qualified. Boot partial placement158,428 bytes/5,380 conservative headroom is separate from this aggregate link. Boot's qsort record outputs agree but comparator call counts still differ in18/27 wide cases; worker is correcting left-scan side effects after capture. All three workers released after their phase terminal passes.

Postcapture root implemented native30d8fc private radio mask/channel updates and six-byte per-slot message fanout. Primary condition alias receipt establishes carry-set=unsignedLO and the byte channel range2..37; actual-C controlled contracts pass69,120 cases. Its dedicated target build is separate/in progress at this checkpoint. Runtime data and complete-image layout/hardware proof remain open.

## Pending six-image checkpoint after EM test dispatcher round

Dedicated EM target receipt `em-test-quality-round`: 623 definitions/77 genuine imports PASS; full dispatcher, product getters/interval and link/stream quality bodies now C. Codec frozen dedicated snapshot138 inputs6imports PASS/coherent. Main frozen dedicated snapshot1455defs494imports PASS0duplicates. Boot latest supposed new power-transition bodies were found redundant with existing selected pcm22_timer_service.c; worker removing duplicates and retaining new eight-case qualification oracle. These dedicated receipts do not replace the last terminal unified checkpoint; all six full components remain incomplete.

## Six-image test-dispatch/SNPU/event-loop checkpoint

Terminal unified receipt `test-dispatch-snpu-event-loop-round/receipt.json` confirms all six candidate compile/link passes: Codec346 definitions/6 imports (coherent), EM623/77, Touch229/0 strong plus four optional weak runtime references, CASE70/3, Boot973/3, Main1455/494. Full source payloads0; all components source_complete false. This replaces the authoritative unified checkpoint only for its captured sources. Subsequent dedicated EM625/75 build PASS adds the response formatter and interval reader; Codec work also resumed after its own captured phase. Three workers released. Boot redundant power-transition additions removed before capture; its floating scaler is actual new archive source, not a proven live path.

## Current continuation: descriptor and connected firmware rounds

- EM selected C: completed native30e050 descriptor. Context-aware target compile/link PASS (647definitions/65imports), actualC524288controlledcasesPASS. Genuine child31bb20 remains, with downstream31b7fc/31b918.
- Codec image-A: worker terminal UART/board/power148inputs,14genuineimports; subsequentpadmuxbuildpending.
- Codec image-B: eight separate native candidates, pinnedCK804EFcompilePASS;280catalogueentriesoutsidecandidate andfiveexplicitdatacontracts. SeparateimageBbuildintegrationpending. These are not missing-body totals without semanticcrosswalk.
- Main worker terminalWsfOsInit aggregate1510definitions/493imports; connectedBLEstartupnext.
- Fullcomponentscomplete0/6; candidatebuilds andfinitechecks do not provewholeimage source/layout/equality/hardware closure. Threeworkersactive;goalactive.

Latest continuation: EMsubmit+second schedulertargetPASS 649/65;CodecA150inputspadmuxPASS9imports;CodecB21candidatebodiesCK804EFseparaterelocatablePASS267catalogueentriesunreviewedand23datacontracts;Main1511/536BLEstartupbodyPASS44orderednative/Ccalls. Fullcomponents0/6;goalactive. Seepercomponentreceiptsforverificationlimits.

Latest EM continuation targetPASS 652/64 afterthreefirst-rolechainbodies; threeboundedCcheckreceiptsPASS. Mainworker1526/538handlerstagePASS;CodecA196/362rawcrosswalkpendinglatestbuild;CodecBauthenticMMIO21bodiesandnewaudioinitfrontier. Fullcomponentscomplete0/6;threeworkersandgoalactive.

Latestcontinuation: EM5dispatch/routerbodies targetPASS657/59 andboundedCchecksPASS;CodecA153inputsDMAleavesPASS7imports;Main1539/545DMinitPASS;CodecB25candidateswith2genuinecodeimports/unseededIRQ. Componentcountsfull0/6;sourcegraphcountsnotwholeimagecoverage. Goalactive.
