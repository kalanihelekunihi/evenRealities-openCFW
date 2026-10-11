
## Command0x2019 dispatch source reduction (2026-10-11)

Native330568..3305ac is now selected typed C: it decodes two little-endian
16-bit values, passes the two payload regions to controller operation30e054,
emits the returned status through existing331bf8, and returns1. Other commands
retain the true332278 child. Native3305ac..3305b0 is an unconditional branch
adapter to332394; its source preserves both arguments and the child return.
Both callbacks and their dispatch children now have qualified two-argument
prototypes. The controller operation30e054 remains a genuine unresolved lower.

The ARC candidate target compile and relocatable link pass in
`g2/build/c-firmware/20261011/em-command-2019-round/receipt.json`.
`verify_dispatch_command_2019.py` compiles the actual selected bodies in an
isolated host harness with controlled children and passes6 source-contract
cases (four command payloads/statuses, fallback and branch adapter). This checks
C call/decode behavior against the recorded native reading; it is not a native
emulator oracle or hardware qualification. No source-complete image claim.

## Feature event conversion and fallback (2026-10-11)

Selected C now implements native332394..33248e feature-gated event maps for
request types11/12/13/17, including extended type11's request+9 mutation,
type13 fallback on either feature disable or allocation failure, and payload
header adjustment before sending. ARC compile/link passed530 definitions/74
imports in `em-feature-events-round`. Actual selected C with host fixed-address
binding and controlled genuine children passes18 source-contract cases.
These tests validate the C against the recorded native reading, not native
emulator equality or hardware behavior.

Native30c2e0..30c33a is also now C: it checks maximum slot id, active/state/flag,
allocates a four-byte task command0x1a01, writes id before queue send, and
preserves the native success return0 even on allocation failure. Seven isolated
C contract cases pass. The three slot accessors30731c/306fdc/307480 remain
honest typed unresolved children; their native custom multiply instruction
semantics are not replaced by an unqualified arithmetic guess. Its target
build `em-controller-fallback-round` is terminal PASS, selected531 definitions/
76 unresolved contracts. Full EM image remains incomplete.

## Slot accessor source closure

Native306fdc/30731c/307480 now have selected C bodies preserving MPYUW by
its named inline ISA mnemonic. The pinned GNU ARC opcode table identifies
major4/minor0x1f MPYUW for ARCv2 EM/HS; these are distinct from major6 private
products. `em-slot-accessors-round` target compile/link passes534 definitions/
73 genuine imports. The three compiled bodies all emit `209f 040e mpyuw
r0,r0,912`, the identical native multiply encoding, while retaining native
pointer-load order, byte0/2/13 access and masked boolean conversion. Captured
compiled disassembly is `slot-accessors-compiled-disassembly.txt`. This is an
instruction-preservation/source closure check; full runtime equivalence and
image layout are not claimed. Earlier fallback's three unresolved contracts
are closed in this newer snapshot.

## Command controller and final slot children

Native30e054..30e0d4 now has a true C body: pending/callback rejection,
maximum/active/state validation, thirty-byte command0x1801 with id, two source
payloads and a 16-bit value, followed by task send. The original id is saved in
the native first BL delay slot; it is not the child return. Seven controlled
C contract cases pass across every error/allocate/send path, including data
and child order. `em-command-controller-round` target compile/link passes.

The two exposed children3072f0/307434 are now also selected source. Optional
slot callback uses native scaled word offset204→816 bytes and original-id
ABI. Pending check bounds operation-21 to0..14, tests sparse mask0x7ccf,
then the source-owned fifteen-byte operation map, slot code635 or flag word644.
The product table matches authenticated ROM334479..334488, with image/table
hashes in `slot-pending-map-receipt.json`. Neither is a fabricated stub or
executable byte array. `em-command-slot-closure-round` is terminal target compile/link PASS,
selected537 definitions/72 genuine imports. ISA and
callback/whole-image runtime qualification remain distinct open work.

## Response dispatcher round

Native332490 private0xfff7 command and332278 five-command dispatcher are now
selected C. Private flags normalize input bytes2/3 to nonzero/equal-one,
forward the controller status, and send a one-byte response. Main dispatcher
preserves early private handling, lengths3/5/17, five distinct child/data maps,
allocation failure handled-return1, command reload after allocation, zeroed
query halfword, and response send at payload-5.19 controlled C contract cases
pass, including allocator command mutation. Target `em-response-dispatch-round`
compile/link PASS539 definitions/76 genuine imports; newly exposed native
lowers are not fabricated. These are source-reading contract tests, not stock
runtime/hardware comparison.

Native30c33c payload task command,30e350 pair setter,306ea8 slot-time getter,
and30c6d4 query converter now also have C bodies in the newer build. MPYUW10
and MPYDU outputR2/R3 retain named native ISA; no private instruction arithmetic
is invented. The pair setter exposes true308708 lower. `em-slot-command-lowers-round` is terminal ARC compile/link PASS,543
definitions/74 genuine imports. Captured compiled disassembly confirms named
MPYUW10, word123→492-byte load, MPYDU pairedR2/R3 outputs with constant66667,
then low>>22|high<<10 and halfword destination. Those ISA operations are
preserved without a mathematical substitution. Full native runtime/whole
image qualification remains open. Complete EM image false.

## Flags, cipher and timer apply round

Native30b644 data wrapper now forwards to existing source cipher30ff0c with
output/input alias and returns native zero; its ABI is corrected to uint32.
Native30d54c flags command validates max/active and maps the child boolean to
0/12;308b74 atomically in native statement order reads busy byte514, reads
input bytes only if clear, sets busy1 and writes combined halfword512.
23 isolated controlled C contract cases pass, including no input access while
busy and exact cipher argument/return behavior. Target
`em-flags-cipher-closure-round` PASS546 definitions/72 genuine imports.

Native317c10 slot adjustment and308708 application now have selected C bodies.
The adjustment preserves private major6/minor1e product through the existing
named ISA adapter, signed-shift bit pattern, remainder rounding and min-ten
clamp. Application preserves MPYUW_S/MPY_S, private clock products, threshold,
fields472/492 and conditional timers496/476, including field reload after
first timer call. Target `em-slot-timer-apply-round` PASS548 definitions/71
imports. Compiled disassembly emits native compact words7a6a and7a2c exactly,
and scaled stores at native word offsets118/123. Private product semantics
and complete runtime composition remain unqualified; no mathematical guess or
runtime proof is asserted for this newest timer scope.

## Mask and stream dispatch round

Native304648 full64 byte packing,30cf88 masked-command validation and message,
33052c private0xfff8 response,3305b0 stream dispatch are selected C. Parser
preserves header sentinel bytes9/10, pointer field4, mask8, zeroed36-byte
control storage, three-entry cap, four-byte pair records, twelve-byte control
stride and decoder returned-length cursor advance. LDB.AB in private dispatch
leaves input+2 for the mask child.11 controlled selected-C cases pass, including
mask0/255/sparse/high-bit selection, child-variable lengths, allocation failure,
fallback and status call contracts. `em-stream-mask-dispatch-round` is terminal
ARC target compile/link PASS552 definitions/73 genuine imports. Native mask
count30c414 uses DSP accumulator operations; it remains unresolved rather than
being replaced with an unqualified mathematical popcount. Stream decode332a78
and operation30b7ec also remain genuine lower contracts. Full image false.

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

## Runtime descriptor and signed request validator

Native303290..30329c now has a selected C body copying 28 runtime bytes from RAM8016dc; the connected private-dispatch harness passes 52 controlled cases. Its descriptor initialization remains an independent runtime data ownership gate. The all-six captured snapshot records 580 definitions/83 genuine imports.

Post-capture native30cef0..30cf24 now has C implementing critical-section entry/exit, max-slot validation, active-slot check, ignored apply-child return, and exact status0/2 policy. All 2,560 controlled byte/slot/active cases pass; dedicated `em-private-signed-round/receipt.json` target compile/link passes with581 definitions/83 imports. Native309aa4 remains genuine; its substantive callbacks and ambiguous decoded multiply require evidence before reduction. These contracts use actual selected C with normalized RAM and controlled children, and are not native-runtime equality or hardware qualification.

## Private three-byte query and signed pair reduction

Selected native306f44..306f6e reads three slot bytes at598..600, recomputing the named MPYUW stride and reloading the runtime slot base each iteration. Native30bde0..30be2a now validates max-slot, active-slot, feature bit0 and slot-state0, preserves invalid output, and implements exact status2/12/0 policy with critical exit. Actual selected C passes30,720 controlled cases. `em-private-query-round/receipt.json` target compile/link PASS has583 definitions/82 genuine imports.

Native30dd94..30ddd2 now implements signed-pair request validation, selector0..4, ignored apply-child return, exact status2/18/0 and critical entry/exit. Actual selected C passes17,920 controlled cases; native309910 is a genuine retained import. Dedicated target build pending at report time. RAM and stride normalization/controlled children establish bounded native-reading contracts, not native-runtime equality.

Signed-pair dedicated target build terminal PASS:584 selected definitions/82 genuine imports. This postdates the frozen all-six580/83 snapshot.

## Private mask validator and connected native slot update

Native30d378..30d3c0 now has C for max/active-slot checks and exact low mask0xfff7fb41/high BMSK26 mask0x07ffffff validation with status2/18/0. It has no critical section in the native body. Native308b20..308b48 now has a selected C body preserving named MPYUW912 stride, runtime slot-base read, low/high load order, low-before-high stores, enable OR/disable BIC semantics and updated low-word return. All4,020 connected validator/direct-child boundary cases PASS; independent validator2,010 cases PASS. Dedicated `em-private-mask-update-round/receipt.json` target compile/link PASS:586 definitions/81 genuine imports. Actual C RAM/stride normalized contract evidence is distinct from native-runtime equality.

## Signed request clamp graph

Native310230..31025e now has selected C preserving fresh radio_status_311a00(1), signed product upper byte8012b8, signed MIN upper/query, strict upper branch and lower byte8012b9 read only when the upper branch is not taken. All2,949,120 controlled combinations of signed product bounds, query values and input edge values pass actual selected-C contracts. No invented product limits are used. Dedicated target build `em-signed-clamp-round` is in progress. This supports reduction of substantive309910/309aa4, which remain genuine imports. Native31b374 classification has been inspected: it calls31026c with lower at stack+3 and upper at stack+2, returns twice(upper<=value), overridden to1 when lower>=value. No classifier implementation is claimed yet.

Signed-clamp dedicated target build terminal PASS:587 definitions/81 genuine imports.

## Signed pair update and bound graph

Native309910..3099c8 now has C preserving saved runtime base, selector0/current-selection semantics, clamp child, byte-modulo delta early exit, conditional slot66 update, mode/feature-gated five-argument callback, per-selector slot331+selector write, and post-update seven-argument notification with fresh current-byte classification. Native31026c bound reader and31b374 classifier are C-backed with aliased-output/read-before-write and signed comparisons. The genuine parent ignores the apply routine's incidental R0, so its semantic interface is void. Native-reading actual-C contracts pass122,880 update/callback/whole-record cases and720,896 signed bounds/classification cases. Dedicated `em-signed-pair-apply-round/receipt.json` target compile/link PASS:590 definitions/80 imports. Product limits and live callbacks remain runtime data inputs; no fabricated defaults.

## Signed default update body

Native309aa4..309b74 is now selected C: four selector bytes saved before clamp; current byte and replicated selector word written; mode/feature-gated first callback; notification per changed saved byte; callback pointer reloaded after every notification. Native MPYWHL is preserved as named inline ISA, with primary local binutils opcode-table receipt and explicit DSP decode removing the earlier guessed-class warning. Actual-C controlled host contracts pass49,152 cases including whole-record comparison and callback removal after first notification. Host byte replication stands in for MPYWHL only; no native ISA arithmetic equality is inferred. Dedicated `em-signed-default-apply-round/receipt.json` target compile/link PASS:591 definitions/79 imports. Parent ignores incidental R0, so semantic apply interface is void. Signed-request bodies309910 and309aa4 are now C-backed; runtime product bytes/slots/callbacks remain genuine data contracts.

## Private radio masked update and slot fanout

Native30d8fc..30d9b0 now has selected C with exact feature/status12 gate, mask1..7 gate, EXTBU channel expression with unsignedLO rejection, gain/channel byte writes per mask, per-iteration reloaded slot count, active/state1/pending33 checks, allocation failure continuation, six-byte type0x2101 messages and handler load/write/send order. All69,120 controlled cases PASS; dedicated `em-private-radio-round/receipt.json` target compile/link PASS:592 definitions/78 genuine imports. This postdates the frozen all-six591/79 snapshot. Primary condition alias and runtime data contracts are explicit; bounded actual-C contracts are not native-runtime equality.

## Connection limit setter and feature query

Native30e38c..30e3e8 now has selected C for exact conditional carry/unsignedLO gates, size27..251, timing minimum328, version-dependent maxima2120/17040, clamped product maximum, status48/17, and timing-before-size runtime halfword stores. Native307044 reads paired slot words544/548; native30cb28 validates max/active-slot, low-word bit26, allocation failure status0, type0x2301 query message, and untouched final payload byte. All14,680,064 size/timing/version/max-bound cases and2,560 connected64-bit feature/query/message cases PASS. Dedicated `em-connection-value-query-round/receipt.json` target compile/link PASS:595 definitions/76 imports. Actual-C normalized-RAM controlled contracts are distinct from native-runtime/hardware equality.

## Connection mode/modify and parameter validation

Native30c944 and30c998 now implement max/active-slot/flag gates, six-byte mode messages, copied12-byte controls in16-byte modify messages, validator status propagation, exact header/copy/handler ordering and allocation-failure status0. Their61,440 controlled actual-C cases PASS. Native30a6b4 parameter validator is now C-backed with bounds minimum6, maximum3200, latency499, timeout10..3200 and authentic named MPYWHUL/MPYWHL/MPYUW products. Explicit DSP decode removes guessed-class warnings. Actual connected C validator/modify checks pass276,808 exhaustive field and product-boundary cases; host products are controlled stand-ins while target retains native ISA, so no native arithmetic/runtime equality is inferred. Dedicated `em-connection-parameters-validator-round/receipt.json` target compile/link PASS:598 definitions/74 imports.

## Connection read/action and slot helpers

Native30c860 now has selected C preserving pending-operation27 before max-slot validation: pending path requires active and byte636 bit2 readiness then full word636 bit2 set; ordinary path validates max/active and emits4-byte type0x1b01. Native30c8c8 validates max/active then operation28 pending and emits4-byte type0x1c01. Native3073ec and309030 are actual selected named-stride C helpers; full word636 upper bytes are preserved. Actual connected-C contracts pass122,880 cases covering every byte636 value, pending-path IDs beyond configured max, exact status/allocation gates, message contents and direct helper effects. Dedicated `em-connection-read-action-round/receipt.json` target compile/link PASS:602 definitions/72 imports. RAM/stride normalization and controlled child evidence does not establish native-runtime or hardware equality.

## Primary/extra-slot disconnect graph

Native30b570 now has selected C for primary+extra count validation, primary active check or optional extra active callback, extra pending/lookup fallback, callback-driven configuration reload before6/8-byte allocation selection, exact type0x1701/0x170f/0x2701 messages, handler load ordering and allocation-failure status0. Native3072e0/30730c/306e54 callback-query bodies are actual selected C with authentic missing-callback0/0xffff results and genuine live RAM pointers. Actual connected-C contracts pass331,776 cases including callback-induced primary-count mutations, every reason byte, null/nonzero query callbacks and all untouched message bytes. Dedicated `em-connection-disconnect-round/receipt.json` target compile/link PASS:606 definitions/71 imports. Native-reading normalized-RAM contracts do not establish hardware or native-runtime equality.

## Connection timing and legacy parameter request

Native30d3c4 is selected C with max/active and operation31 pending gates, exact interval/timing validation, fresh product pointer/version reload after pending child, signed MIN size251,8-byte type0x1f01 message and allocation-failure status0. Actual-C controlled checks pass4,203,264 exhaustive size/boundary/config-mutation/message cases. Native30b1b0 is selected C with operation21 pending gate, state1-only feature bit1 requirement, reuse of actual C parameter validator,16-byte type0x1501 controls message, header-before-copy and handler-after-copy order. Its368,640 controlled actual-C cases pass. Dedicated `em-connection-legacy-parameters-round/receipt.json` target compile/link PASS:608 definitions/69 genuine imports. Bounded RAM-normalized/native-reading contracts do not establish whole-image or hardware proof.

## Controls and event relay source round

Completed bounded C bodies: event33 relay `32f70c` (262,144 controlled cases), paired controls dispatcher `32f64c` and response formatter `32f770` (94,206 controlled cases). ARC candidate compile/link PASS at `em-controls-dispatch-round`: 611 definitions, 69 genuine imports. Native command reload, five decoded halfwords, allocation failure, output byte preservation and relay alias cases retained. Runtime masks, deeper controls implementations, image layout and native/hardware equality remain open; full EM component incomplete.

Shared controls apply `30d524` (native tail branch to `308b4c..308b72`) completed as C; 6,144 controlled validator/overlap cases PASS. ARC candidate build `em-controls-apply-round` PASS: 612 definitions/69 genuine imports. Real validator `32e378` remains unresolved; full image remains incomplete.

## Validated controls and slot controls source round

Completed full C bodies: validator `32e378..32e3b8` and native slot-controls tail branch `30e0e0 -> 30a39c..30a482`. Validator: 1,235,044 controlled cases PASS. Connected validator/slot updater: 20,160 controlled cases PASS covering maximum/active gates, timing boundary, features, busy/state, allocator failure, shared controls update and selected message/copy children. Target ARC compile/link PASS at `em-slot-controls-round`: 614 definitions/67 genuine imports. Authenticated named MPYUW/MPYWHUL/MPY instructions remain in target source; host products are normalized and do not establish ISA/native equality. Runtime cells, image data/layout and whole-image qualification remain open.

## Full test command dispatcher and first connected providers

Completed native dispatcher `32f85c..32fc86`: 251,891 controlled C cases PASS, target ARC compile/link PASS at `em-test-dispatch-round` (615 definitions/83 genuine imports). Includes all 13 supported selectors, unsupported full command domain, preliminary handler, exact decoding, allocator failure, post-allocation command reload to unsupported command, response data and flag contracts. Child scratch remains provider-owned; no default outputs invented.

Completed four independent fresh product getters (`30bb14`, `30bb20`, `30bdc4`, `30bdd0`) plus test interval setter `308b14` and modulo-halfword validation `30d35c`: 197,120 controlled cases PASS. Product target build621/78 PASS.

Completed link/stream quality helper `306f0c` and slot fallback wrapper `30bd18`: 2,097,152 controlled cases PASS. Native source-find children and slot quality are selected real C; host harness controls them and normalizes the runtime state pointer. Final `em-test-quality-round` target compile/link PASS: 623 definitions/77 imports. Full EM component remains incomplete; controlled cases do not establish native ISA/runtime equality.

## Response formatter and interval reader

After unified checkpoint EM phase completed, selected full bodies `330f08..330f46` and `30bc3c -> 306ed4..306ee6`. Actual selected C formatter passes1,474,560 controlled source/output alias cases; interval reader passes393,216 exhaustive halfword/alias cases. Native mixed-width source reloads and intervening writes retained. Target build `em-test-response-interval-round` running; do not claim terminal compilation until receipt confirms. Draft snippets retained as evidence, harnesses now extract actual selected source.

Response/interval target build terminal PASS: 625 definitions/75 genuine imports at `em-test-response-interval-round`. Source bodies and controlled contracts complete; full EM image source/data/layout/equality remain open.

## Connected counter query/enable/disable round

Seven full native C bodies selected: stream counters306a9c,link counters306ae0,lookup query307498, status-discard wrapper30c2bc,stream enable317654,link/stream enable30c2d4->3074c0,disable30c2d8->307504. Actual connected C contracts PASS7,680 cases covering all lookup presence, nonboolean flag values, full-word controls, overlapping counter/output/flag records, status propagation/discard and complete record contents. Native stream flag bit0 toggle, snapshots and post-output reloads retained. ARC compile/link PASS `em-test-counters-round`:632 definitions/72 genuine imports. Full EM image remains incomplete.

## Test mode and complete snapshot providers

Completed full channel lookup31ab50,stream test-mode317a10,and paired mode request30c2dc->307564 bodies. Target `em-test-mode-round` PASS635 definitions/71 imports; actual connectedC8,193casesPASS for channel count/stride/match/full-word IDs, link state/value gates and stream busy/product gates. Authenticated native success requires channel lookup match before dereference; no invented null guard added.

Completed full snapshot30c724->3081a4, exactly28bytes from link+584 or stream+60 only when stream state marker3zero. Failures leave scratch untouched. ActualC262,144 controlledcasesPASS, target `em-test-snapshot-round` PASS636 definitions/70 genuine imports. Controlled cells/find/copy providers do not prove native runtime equality. Full component remains incomplete.

## Complete timing query and mask/role action dispatcher

Completed full timing query30c728->3081dc..3082ac. Native named MPYW/MPYWHL retained; stream phase-specific store order and channel timing reload after first output preserved. ActualC98,304 controlled normalized-address/product casesPASS with link/stream state gates, output aliases and untouched error outputs. Target ARC compile/link PASS637 definitions/69 genuine imports.

Completed mask/role dispatcher30cb24->30843c..308538. ActualC99,072 controlledcasesPASS for masks/sentinels/roles, callback order and callback-induced id/marker/context mutation. Stack scratch id/+16pointer only native-owned fields initialized; genuine31b7e4/31b8a8 remain code imports. Target `em-test-actions-round` PASS638 definitions/70imports. Full EM source/data/layout/equality open; no native ISA/runtime proof inferred from controlled contracts.

## Required action callbacks source round

Completed31b7e4..31b7f8 marker/callback forwarder and31b8a8..31b914 shifted queue drain. Exact native slot+4 advance, id+10 read, required callback modes0/1, passthrough non-one marker returns, event release before protected byte-count increment retained. Actual selectedC4,718,592 controlledcasesPASS across all marker/count bytes, queue lengths0..8, callback/critical-induced cell mutation and complete child order. Target ARC compile/link PASS `em-test-action-callbacks-round`:640 definitions/68 genuine imports. Callback presence/native product state remains required; no fake provider or invented guard introduced. Full image/source/data/layout/equality remain open.

## Pending packet scans round

Completed native bodies 32385c, 3252dc, 30853c, 317624, 30858c in selected controller_init.c. Header stores retain metadata reloads for overlapping buffers; primary reverse scan reloads its base only after active child returns empty; forward link/stream scans reread limits and reload config after empty children. Required MPYWHL stays named ISA assembly. No zero-count guard invented for primary native underflow.

Target receipt `g2/build/c-firmware/20261011/em-pending-scans-round/receipt.json`: compile/link PASS, 645 definitions / 66 genuine imports. Actual C bounded checks: header/primary queue 33,603,584 cases, scan/stream take 70,784 cases. Host address and arithmetic normalization is explicitly recorded; these are not native ISA/hardware equality. Full component remains incomplete.

Marker validator 30b1ac->306b70 also completed: all256byte inputs PASS, including native wrap of255 tozero. Latest `em-test-marker-round` target compile/link PASS: 646definitions/65imports. Full source remains incomplete.

## Native test descriptor round

Completed 30e050 tail309b84..309cb6: zeroed36B descriptor, native validation gates, link/stream field ordering, timer/primary pair ordering and explicit third submit context argument (channel+36 or stream-state+304). Child31bb20 consumes R2 for its eventual31b7fc call, so the context is retained rather than discarded. Initial647/65 target receipt is superseded by context-aware target build (session38049 pending at report write). Actual C controlled524288cases PASS exact36Bdescriptor and forwardedcontext; nativeISA/runtime equality remains open. Genuine submit31bb20 and its31b7fc/31b918 scheduling children require source reduction.

Correctedcontext target terminalPASS: `g2/build/c-firmware/20261011/em-test-descriptor-context-round/receipt.json` 647definitions/65genuineimports, sourcehashstableandmatchescurrent. Descriptorchunkcompleted; child31bb20stillgenuineimport.

## Native submit and second-role scheduling round

Completed31bb20..31bbac native submit and31b918..31b9aa second scheduler. Submit preserves sentinel gates, role-specific action callbacks, protected805cb0 lifetime, request/slot pointer reloads and the first-role R2 context. Second scheduler preserves marker0 queue resets, marker255 no-effect, marker1 pre-callback queue/id writes, authenticated52B scratch fields (padding unspecified), missingcallback18 and failure13/marker255.

ActualC controlled checks: submit1,048,576 cases, second scheduler262,144 cases, bothPASS. Latesttarget `g2/build/c-firmware/20261011/em-test-second-schedule-round/receipt.json` compile/linkPASS 649definitions/65genuineimports;sourcehashstableandmatchescurrent. Remaining first scheduler31b7fc has real scheduling callback31bad0 and timing child31c490; source recovery remains open. Native/wholeimage/runtime equality not implied.

## Native first-role scheduling chain

Completed31b7fc..31b8a4 scheduling52Bcallback,31bad0..31bb1c completion and31c490..31c4fc timer. Source-relocated callback pointer, cached slot/freshdescriptorid aftercallback, ignoredtimerlowerstatus, six-entryring20Bstride withoverlapping+24halfword, pre-postindexwrite, capturedcallbacklength/freshallocationconfig and required callback semantics retained.

Controlled actualC checks: firstschedule262144cases,completion36864cases,timer32768casesPASS. Target `g2/build/c-firmware/20261011/em-test-timer-round/receipt.json` terminal compile/linkPASS 652definitions/64genuineimports; compile sourcehashstableandmatchescurrent. Sourcechunkcompletion does not establish nativeISA/runtime/wholeimage equality. Continue true unresolved providers; no fabricatedproviders or executableblobs.

## Pending packet and event dispatch round

Completed331a8c,331aa4 packet accounting wrappers;331abc credit tail;331cbc notificationbyte gate/event8;331a40types0/1/3queue router withunsupportedrelease. Corrected historical voidcallback declarations to authenticatednativeargument/return contracts. Native fullwordunchangedpendingreturns, lowbytewrites, handlerreloadafterenqueue andaccountstatus-to-pointerdecision retained.

ActualC checks: fourdispatches16,843,776casesPASS;router262,144casesPASS. `g2/build/c-firmware/20261011/em-event-route-round/receipt.json` targetcompile/linkPASS 657definitions/59imports;sourcehashstableandmatchescurrent. Controlledchildren/normalizedRAM do not prove nativeISA/runtime/wholeimage equality.

## Native gated data-event builder

Completed331b3c..331bb6 with actual19/20event selectors, productmask bits,66/34B allocation, exact header/copy ordering andtwo32Bpayloads versusone. Send statusignoredforhandledreturn1 asnative. Native callbacksignature correctedfromunqualifiedvoid. ActualC524542controlledcasesPASS includingfullbytemasks, allocationmiss/success, inputchangesduringallocator/firstcopy andunsupportedtypebytes. Target `g2/build/c-firmware/20261011/em-data-events-round/receipt.json` terminalPASS 658definitions/58genuineimports;sourcehashstableandmatchescurrent. Fullcomponent/native/runtime/layoutgatesremain.

## Native receive-release dispatch

Completed331c20..331cba, correctedR0type/R1event ABI. Retains type1release/credit1; type3optionalpresencecheck thenrelease andfreshrequiredcallbackreload; type2specificsubtypecounterwrapping thenrelease; unknowntypesstillpostwithoutrelease. Alwaysreload handlerafterchildren andpostevent4 withforwardedlowerreturn.

ActualC3,932,160controlledcasesPASS withfullsubtype/counterbytes, codes0/62/255, types0/1/2/3/255, callbackreplacementbyrelease andchildorder/counts. Target `g2/build/c-firmware/20261011/em-receive-release-round/receipt.json` compile/linkPASS 659definitions/57imports,sourcehashstableandmatchescurrent. Native/wholeimage/runtimeequalitynotimplied. Next331cdc nativequeuebridge threeoutputcontracts andoptionalpacketproviders.

## Native queue bridge

Completed331cdc..331d5c threeoutputABI: queued-event priority, thenoptional linkprovider, thenfreshprimaryprovider. Busyflagtestedonce, headerscapturedbeforealiasedoutputstores, byte/word/halfwordwriteorder preserved, empty/busyoutputsuntouched. ActualC32768controlledcasesPASS includingproviderpermutations, pointerreplacement/busymutationbychildren andtypeoutputaliasingheader. `g2/build/c-firmware/20261011/em-queue-bridge-round/receipt.json` terminaltargetPASS 660definitions/56imports,sourcehashstableandmatchescurrent. NativeISA/runtime/wholeimagequalification remainsopen.

## Vendor command dispatcher and key/mode leaves

Completed331aec,331bb8,30d9f4,30e040/309b78. Native32bytekeynonzeroscan, preservekeyonallzero, fullwordmode0/1validation, commandreloadafterchild, responseprefix/send handling andthreecommanddispatch preserved. Threegenuinechildren30bb10,30baa0,30bad4 remainexplicit. Native331aecdelaystoresoriginalrequestbefor331bb8child; no erroneousreturn-pointerinterpretation. ActualC336128controlledcasesPASS: full16bitcommand/modefixtures, scanpositions/values, requestmutationduringcopy andallocatorfailure. `g2/build/c-firmware/20261011/em-vendor-dispatch-round/receipt.json` targetPASS 664definitions/58imports;sourcehashstableandmatchescurrent. Wholeimage/runtime/ISAqualificationopen.

## Vendor application/query descendants and wake leaf

Completed30baa0,30bad4,306dcc,30bb10->306e2c,313fc0. Source96Bscratch layout containskey32followedbytwo32Binputs; exactcount1defaultsbranch andallotherfullwordcountapplication preserved. Busy gate, capturedmode acrossvalidator, fullwordvalidbranchversuslowbytestatusrecord, ordered64/32Bproductcopies andwakecellpointeroverwrite2/1 retained. Native313fc0ignoresincomingaddressandreturns80606d; source doesnotinventincomingqueueuse.

ActualC18688controlledcasesPASS. `g2/build/c-firmware/20261011/em-vendor-start-round/receipt.json` terminaltargetPASS 669definitions/57genuineimports;sourcehashstableandmatchescurrent. Genuine32e328validator and306d7cdefaults remain. Wholeimage/ISA/runtime/layoutnotqualified.

## Vendor defaults and point validation

Completed four native C bodies:306d7c defaults,3333d0 word conversion,3100c8 point wrapper,32e328 validation/event wrapper. Authenticated nonexecutable32/64B default data is attributed to native memcpy consumers. Original input pointer is preserved through the dead volatile reversal scratch, with explicit resident ROM108260 dependency. Actual C5632 controlled cases PASS, including overlap, busy bytes, ROM returns and fresh handler reload. Repaired target build `g2/build/c-firmware/20261011/em-vendor-validation-repair-round/receipt.json` PASS673 definitions/56 genuine imports; compile snapshot stable and matches current source. Whole image, resident ROM body, ISA equality, final layout and hardware qualification remain open.

## Packet subtype3 dispatcher

Completed native331ec0..331efe C with ordered two genuine gate calls, subtype3 check, event14/length4 allocation, native prefix/header writes and fresh input byte after allocation. Actual C2048 controlled cases PASS. `g2/build/c-firmware/20261011/em-packet-subtype-round/receipt.json` target compile/link PASS 674 definitions/57 genuine imports; source snapshot coherent. New3329b0/304ac4 children remain explicit. Native ISA, full image, data/layout/runtime/hardware gates remain open.

## Vendor packet serializer

Completed3329b0..332a78 with three authenticated subtype branches21/34/49,255 event allocations15/15/10, exact ordered reads/stores, two6B address serializers and untouched event gap for subtype49. Actual C8192 controlled cases PASS including allocator subtype mutation and fresh payload reads. `g2/build/c-firmware/20261011/em-vendor-packet-round/receipt.json` target PASS 675 definitions/56 imports; current source snapshot coherent. Full source/layout/ISA/runtime/hardware gates remain open.

## Status event packet gate

Completed304ac4..304af8 subtype64 gate, event255/length3 allocation, FE82 halfword pack and true returned offset, fresh byte after pack child, send at event-2. Actual C2048 controlled cases PASS with allocation misses and offset propagation. `g2/build/c-firmware/20261011/em-status-event-round/receipt.json` target PASS 676 definitions/55 genuine imports; current source snapshot coherent. Full source/layout/ISA/runtime/hardware gates remain open.

## Product-gated packet events39/40

Completed332200..332278 with exact product mask bits at8056fb/8056ef, lengths29/7 and event62, explicit genuine fill330e78 and ordered type40 six-byte reads/stores. Actual C262144 controlled cases PASS. `g2/build/c-firmware/20261011/em-product-event-round/receipt.json` target PASS 677 definitions/55 genuine imports; current compile snapshot coherent. Fullsource/data/layout/ISA/runtime/hardware gates remain open.

## Native event projection

Completed330e78..330f08 real29-byte field projection retaining repeated volatile word/halfword reads, skipped input31 and returned29. Actual C12288 field/overlap cases PASS; consumer262144 controlled cases remain PASS after corrected uint32 return ABI. `g2/build/c-firmware/20261011/em-event-projection-round/receipt.json` target PASS 678 definitions/54 imports; current snapshot coherent. Native ISA/read timing, fullsource/data/layout/runtime/hardware remain unqualified.

## Link query/mode command dispatcher

Completed332194..332200 commands2066/2067, exact low/high input loads, preserved full query status, mode/status response layout and fresh command reloads after provider/allocator. Actual C393216 controlled cases PASS. `g2/build/c-firmware/20261011/em-link-command-round/receipt.json` target PASS 679 definitions/55 genuine imports; current source snapshot coherent. Real30aec4->306a20 and30c940->308308 tail providers remain explicit. Fullsource/data/layout/ISA/runtime/hardware gates remain open.

## Link query/mode providers

Completed native306a20/308308 with existing lookup, nativeMPYUW offset, fullword status2/12/0, allocation-miss success0, fresh id/handler reads and event2501/2601. Actual C32768 controlled cases PASS (normalized arithmetic and globals), consumer393216casesPASS. Target em-link-provider-round PASS681definitions/53imports; source snapshot stable and current. ISA/runtime/fullsource/layout/hardware gates open.

## Subtype-five event dispatcher

Completed3319bc..331a40 native gated event62/31bytes. Preserved three6Bcopy order and explicit nativeR1 advancement for secondsourcepacket+16; final seven input bytes reload after children. Actual C262144 controlled cases PASS. `g2/build/c-firmware/20261011/em-subtype-five-round/receipt.json` target PASS 682 definitions/52 genuine imports; current snapshot coherent. Native ABI trace atsubtype-five-native-contract.md. Fullsource/data/layout/ISA/runtime/hardware gates remain open.

## Subtype22 event dispatcher

Completed331814..331868 real gated event62/6Bpayload, maskbit3, native post-update finalstore/sendpointer preserved. Actual C262144 controlledcasesPASS. `g2/build/c-firmware/20261011/em-subtype-twenty-two-round/receipt.json` targetPASS 683definitions/51 genuineimports; current source snapshot coherent. Fullsource/data/layout/ISA/runtime/hardwaregatesopen.

## Address command dispatcher

Completed33194c..3319bc native202b/202c scratch six-byte response and fallback331868. Preserves child input postincrement, zero scratch, status byte beforecopy, fresh command rechecks, sendresponse-5 and fullfallbackreturn. Actual C393216 controlledcasesPASS. `g2/build/c-firmware/20261011/em-address-dispatch-round/receipt.json` targetPASS 684definitions/52 imports; current source snapshot coherent. Genuine30c7d0/30c72c address providers remain explicit. Fullsource/data/layout/ISA/runtime/hardwaregatesopen.

## Address pair providers

Completed30c72c/30c7d0 wrappers through authentic pack304624, peer/identity pair303a40/303a60, serializer3045e8. Fullword selector>1return18; zero lookup2; success0; zeroed pair scratch retained. Actual C1536 controlledcases and393216consumercasesPASS. `g2/build/c-firmware/20261011/em-address-provider-round/receipt.json` targetPASS 686definitions/50 imports; current snapshot coherent. Fullsource/data/layout/ISA/runtime/hardwaregatesopen.

## Generic link command dispatcher

Completed331868..33194c eight native commands2027/2028/2029/202a/202d/202e/204e/207c, explicit8genuinechildren, length2specialresponse, freshcommand bitmaskc7 and specialoutputbyte. Actual C262144 controlledcasesPASS. `g2/build/c-firmware/20261011/em-generic-link-dispatch-round/receipt.json` targetPASS 687definitions/57 imports; current snapshotcoherent. Importincrease reflects realchildgraph. Fullsource/data/layout/ISA/runtime/hardwaregatesopen.

## Busy-gated mode/reset providers

Completed30cd94/30b150 preserving fourorderedflags, installedcallback withnativeR0forwarded, modevalidation18, busy12, resetonlynativebranch. Actual C130560controlledcasesPASS;genericconsumer262144PASS. `g2/build/c-firmware/20261011/em-command-busy-round/receipt.json` targetPASS 689definitions/56 imports/currenthashcoherent. Genuine30390cresetremains. Fullsource/layout/ISA/runtime/hardwaregatesopen.

## Radio reset leaf

Completed30390c..303918 native bytezero at801610 and retainedR0address return; corrected precedingvoid declaration. Consumer130560controlledcasesPASS. `g2/build/c-firmware/20261011/em-radio-reset-round/receipt.json` targetPASS 690definitions/55 imports/currenthashcoherent. Fullsource/data/layout/ISA/runtime/hardwaregatesopen.

## Identity status output wrapper

Completed30c918..30c928 original pointer preserved through nativeBLdelay slot, selected30396cgetter byte store andreturn0. Actual C512controlledcases and262144consumercasesPASS. `g2/build/c-firmware/20261011/em-status-output-round/receipt.json` targetPASS 691definitions/54 imports/currenthashcoherent. Fullsource/data/layout/ISA/runtime/hardwaregatesopen.

## Time-setting command chain

Completed30deec/308198/325268 native wrappinghalfword validation, fullwordtimecell store, freshhandler/time read, timerhandlerbyte then secondsstart tail. Actual C196608 controlledcasesPASS. `g2/build/c-firmware/20261011/em-command-time-round/receipt.json` targetPASS 694definitions/53 imports/currenthashcoherent. Fullsource/data/layout/ISA/runtime/hardwaregatesopen.

## Mode command provider

Completed30d45c/306a90 with fullwordmode>=4return18, authenticconnectiongate, localbytestore0 or installedtwoargprovider fullreturn. Actual C393216controlledcasesPASS. `g2/build/c-firmware/20261011/em-mode-provider-round/receipt.json` targetPASS 696definitions/52 imports/currenthashcoherent. Fullsource/data/layout/ISA/runtime/hardwaregatesopen.

## Identity-setting command provider

Completed30ddd4..30de38 BooleanselectorORvalidation, nativebusy/modegate, packedaddress and selected303ca8setter, lookup0->2/nonzero->0. Actual C524288controlledcasesPASS. `g2/build/c-firmware/20261011/em-identity-command-round/receipt.json` targetPASS 697definitions/51 imports/currenthashcoherent. Fullsource/data/layout/ISA/runtime/hardwaregatesopen.

## Address-update adapter

Completed30ca68..30cac4 fullwordkindvalidation, nativebusy/modegate, packedaddress and genuine303b40update, zeroresult18/nonzero0. Actual C2048distinctcontrolledcasesPASS. `g2/build/c-firmware/20261011/em-address-update-command-round/receipt.json` targetPASS 698definitions/51 imports/currenthashcoherent. Genuine303b40remains. Fullsource/data/layout/ISA/runtime/hardwaregatesopen.

## Address record removal

Completed303b40..303b7c authenticidentitylookup, last72Brow replacementforcount>=2, capturedcountdecrementbyte(includingzero wrap), Booleanmatchedreturn. NativeMPYUWretained. Actual C512controlledcases and2048consumercasesPASS. `g2/build/c-firmware/20261011/em-address-record-round/receipt.json` targetPASS 699definitions/50 imports/currenthashcoherent. Fullsource/data/layout/ISA/runtime/hardwaregatesopen.

## Identity insertion command adapter

Completed30af30..30af98 with fullkindvalidation,busy/modegate, packedaddress and explicitfivearg303788child, zeroresult7/nonzero0. Actual C2048controlledcasesPASS. `g2/build/c-firmware/20261011/em-identity-add-adapter-round/receipt.json` targetPASS 700definitions/50 imports/currenthashcoherent. Real303788providerremains. Fullsource/data/layout/ISA/runtime/hardwaregatesopen.

## Identity row insertion

Completed native303788..303844 record insertion/update: capacity and null-base ordering,72B stride, key-zero flags, cleared projection state and conditional private-address projection. Actual selected C passed4624 controlled cases; adapter2048 cases passed. Initial target receipt `g2/build/c-firmware/20261011/em-identity-insertion-round/receipt.json` passed701 definitions/50 imports with coherent source hash. Connected31467c to the previously reconstructed private-address C provider; binding build settled PASS: 701 definitions/49 genuine imports, current source hash coherent (`g2/build/c-firmware/20261011/em-identity-provider-binding-round/receipt.json`). Host fixtures normalize RAM, children and MPYUW and do not establish native ISA/hardware execution. Full component remains incomplete.

## Variable pair event dispatcher

Completed native331f5c..332036 event41/42 as C, replacing the unqualified void import with its packet/Boolean ABI. Retained mask gates, byte-truncated allocation length, repeated wide packet reads and fresh pair-count reads. Actual C65536 controlled cases PASS, including count255/wrapped allocation length; fixtures provide enough storage to observe native writes without asserting allocator safety. Target receipt `g2/build/c-firmware/20261011/em-variable-pair-event-round/receipt.json` PASS: 702 definitions/48 genuine imports, current source hash coherent. Full-source, placement, native execution and hardware qualification remain open. Next3327f4 event26..29 native body inspected, not yet implemented.

## Quota and status event dispatcher

Completed native3327f4..3328c6 event26 quota/address payload, event27/29 ungated status payloads and event28 gated fields. Corrected callback declaration to packet/Boolean ABI. Preserved native state-pointer dereference before masks and fresh count reread after address-copy child. Actual C32768 controlled cases PASS; variable-pair consumer regression65536 cases PASS. Target `g2/build/c-firmware/20261011/em-quota-event-round/receipt.json` PASS 703 definitions/47 genuine imports/currenthash coherent. Remaining imports are not a full missing-body count; full source/data/layout/native execution/hardware gates remain open.

## Packed command dispatcher

Completed native332038..332192 for2068/2069 native stack records and206a two-byte command. Explicit native input read order, padding left unwritten,16B copy and full status forwarding retained.262144 actualC command/input cases PASS, prior quota32768 regression cases PASS. Target `g2/build/c-firmware/20261011/em-packed-command-round/receipt.json` PASS 704 definitions/49 genuine imports/current source hash coherent. Three exposed real children30b230/30b2d8/30e0e4 remain imports; lower implementation, full source/data/layout/ISA/runtime/hardware gates remain open.

## Record option command child

Completed30e0e4 tail30a100..30a132 using selected31aa98 record lookup. Native byte3/byte1 state guards, flags read before option290 write, bit1 update at273 and66/12/0 statuses retained.1179648 actualC cases and262144 dispatcher regression cases PASS. Target `g2/build/c-firmware/20261011/em-record-option-round/receipt.json` PASS 705 definitions/48 genuine imports/currenthash coherent.30b230 and30b2d8 validation/lower chains remain, alongside fullsource/data/layout/native/runtime/hardware gates.

## Packed parameter validation child

Completed native30b230..30b2d8 with native ordered state capability reads, unsigned/wrapped bounds, requested capability mask, parameter guards and real existence/apply children3072d0/309cfc. Actual C327680 capability/timing cases and1179648 option regression cases PASS. Target `g2/build/c-firmware/20261011/em-packed-validation-round/receipt.json` PASS 706 definitions/49 genuine imports/currenthash coherent. Other bounds source-inspected; native ISA/hardware unproved. Next3072d0/31aa64 lookup chain and309cfc apply, then30b2d8; full component gates remain open.

## Record existence lookup chain

Completed native31aa64..31aa98 and3072d0..3072e0 as C: count fromconfig12,2824Bstride, fullwidth id compare before active byte and Boolean wrapper.132096 actualC count/id/active cases and327680 validation regression cases PASS. Target `g2/build/c-firmware/20261011/em-record-existence-round/receipt.json` PASS 708 definitions/48 genuine imports/currenthash.309cfc apply native body inspected throughallocation/callback/queue paths but not yet reduced. Full component gates remain open.

## Extended packed validation

Completed native30b2d8..30b3f8 with48/17/66 error precedence, native multiply/remainder instructions and real307410/309e60 children. Actual C71168 byte/interval boundary cases PASS; arithmetic normalized in host fixtures, native ISA/hardware remain unproved. Target `g2/build/c-firmware/20261011/em-extended-validation-round/receipt.json` PASS 709 definitions/49 genuine imports/currenthash coherent. Both packed adapters now have validation bodies; their apply chains remain genuine imports. Fullsource/data/layout/runtime/hardware gates remain.

## Record availability provider

Completed307410..307434 native lookup/byte369nonzero/byte368equals1 predicates using real selected31aa64 C. Actual C131072 allbytepair/lookup cases plus71168 extended validation regression cases PASS. Target `g2/build/c-firmware/20261011/em-record-availability-round/receipt.json` PASS 710 definitions/48 genuine imports/currenthash coherent. Native309cfc direct call and callback frontier recorded in `record-apply-native-frontier.json`; source mentions only discovery cues.309cfc/309e60 apply bodies and full image gates remain open.

## Active association scan

Completed317280..3172c8 native active512Brow/state3equals1/nonnullassociation/id scan as C.528384 actualC count/id/flag/pointer cases and131072 availability regression cases PASS. Target `g2/build/c-firmware/20261011/em-association-scan-round/receipt.json` PASS 711 definitions/48 genuine imports/currenthash coherent. Extended apply309e60..30a0a8 native listing regenerated with explicit EM/DSP decode in `extended-apply-native.arcem.txt`; arithmetic/control graph remains to reduce. Fullcomponent/source/data/layout/runtime/hardware gates open.

## Full record apply body

Completed native309cfc..309e60 as C: capacity/free slots/existing association checks, allocate/configure, input maximum clamp, native MPYUW timing guard, timing child return validation, stream allocations/cleanup, association flags and callback installation, optional message allocation and submission. Forty actualC controlled scenarios PASS across tenfailure/success cuts and association/mode branches. Target `g2/build/c-firmware/20261011/em-record-apply-round/receipt.json` PASS 712 definitions/56 genuine imports/currenthash; timing-return correction included in coherent snapshot. Genuine configure/release/finish/timing/stream/callback children remain; full source/data/layout/native/runtime/hardware gates open.

## Stream allocation child

Completed316ad4..316b5c native firstfree256B stream search, clear/init, record-slot publication and mode defaults.36864 actualC cases plus40 apply regression cases PASS. Target `g2/build/c-firmware/20261011/em-stream-allocation-round/receipt.json` PASS 713 definitions/55 genuine imports/currenthash coherent. Native no invented base guard preserved. Timing30c40c tails unsigned division30c3a4; exact native arithmetic still to reduce, alongside release/setup/configure children and fullimage gates.

## Record cleanup provider

Completed native31ac84..31ace0 as void C (native no defined result; selected callers discard it). Deactivates record, rereads slot count each iteration, invokes native30843c via selected30cb24 tail, releases each nonnull stream and drains mode1 queue with genuine317320 child.49152 actualC cases and40 apply regression cases PASS. Target `g2/build/c-firmware/20261011/em-record-cleanup-round/receipt.json` PASS 714 definitions/56 genuine imports/currenthash. Stream release31ace0/queue317320 still real imports, alongside other apply children and full component gates.

## Stream cleanup and record queue step

Completed native31ace0..31ad64 and317320..317334 as void C: parent-mode drains, receive release, tx release/counter byte increment under critical enter/exit, mode1 event queue cleanup, flush and raw queued-node pool release.770 actualC controlled cases and49152 record cleanup regression cases PASS. Target `g2/build/c-firmware/20261011/em-stream-cleanup-round/receipt.json` PASS 716 definitions/57 genuine imports/currenthash coherent. New real317508 receive-take/317980 queue-step/31bd48 flush bodies remain, alongside configure/setup/timing/extendedapply and fullimage gates.

## Receive take and stream flush

Completed native317508..317524 and31bd48..31bd78 C: event removal/private ten-byte prefix, nonzero-mode buffered-event release/clear and zero-mode queue drain, halfwordcount reset.4096 actualC cases and770 streamcleanup regression cases PASS. Target `g2/build/c-firmware/20261011/em-receive-flush-round/receipt.json` PASS 718 definitions/55 genuine imports/currenthash coherent.317980 nativebody fully inspected; timing child return and post-release packet reads remain exact contracts to preserve when reducing it. Other applychildren/extendedapply and fullimage gates remain.

## Stream queue step

Completed native317980..317a10 as C with byte-budget gate, full timing return, fresh progress/unit/length reads, native MPYUW, progress store before branch, event removal/release/completion and counter critical region.262144 actualC budget/length/flags/childmutation cases and4096 receiveflush regression cases PASS. Target `g2/build/c-firmware/20261011/em-stream-queue-step-round/receipt.json` PASS 719 definitions/55 genuine imports/currenthash coherent.31ae74 completion remains real child; arithmetic normalized only in host fixtures. Fullsource/data/layout/native/runtime/hardware gates remain open.

## Packet recycle completion

Completed native31ae74..31ae84 using selected31416c queueappend with authentic8028c8 queue and packetminus8.1024 actualC forwarding cases and262144 queue-step regression cases PASS. Target `g2/build/c-firmware/20261011/em-packet-recycle-round/receipt.json` PASS 720 definitions/54 genuine imports/currenthash. Authenticated seven-byte334488 data table [2,1,3,1,1,1,4] from exact indexed consumers recorded in `phy-projection-data.json` with binarySHA; not yet source-selected.3183d4 bit-priority native helper inspected for configuration reduction. Fullimage gates remain open.

## Configuration PHY projection and data

Completed native3183d4..3183ec bitpriority helper and selected exact seven nonexecutable334488 bytes [2,1,3,1,1,1,4].262144 actualC projection cases and7 exact stockdata comparisons PASS,1024 recycle regression cases PASS. Target `g2/build/c-firmware/20261011/em-phy-projection-round/receipt.json` PASS 722 definitions/54 genuine imports/currenthash. Full32c3bc..32c4fc configure body native listing regenerated with EM/DSP decode in `record-configure-native.arcem.txt`; still to reduce, preserving MPYWHL and flags. Fullimage gates remain open.

## Full record configuration body

Completed native32c3bc..32c4fc as void C using selected3183d4 projection and authenticated334488 data, native MPYWHL inlineassembly, encryption/random/seed children, period alignment and size adjustment, timing-return fields, repeated native writes, mode-dependent span/total branches.288 actualC controlled scenarios plus40 apply and262144 projection regression cases PASS. Host MPYWHL fixture scalar replacement only qualifies the small-operand branch model, not native DSP semantics. Target `g2/build/c-firmware/20261011/em-record-configuration-round/receipt.json` PASS 723 definitions/55 genuine imports/currenthash coherent.317334 encryptionseed/31737c duration remain real children; finish/setup/timing/extendedapply and fullimage gates remain.

## PHY duration and ordered seed projection

Completed31737c..3173ac and317334..31737c as C, with fullword encrypted addition, PHY duration branches and four ordered keyedmessage30fdb8 calls using48B scratch. Selected24 authenticated nonexecutable key/message bytes334b80..334b98.2097152 actualC duration cases, four ordered childcall checks and24 exactdata byte comparisons PASS;288 configure regression cases PASS. Target `g2/build/c-firmware/20261011/em-duration-seed-round/receipt.json` PASS 725 definitions/54 genuine imports/currenthash coherent.30fdb8 native body inspected throughinput/key reversal andcipher setup; not yet reduced. Crypto/nativeexecution/fullimage gates remain open.

## Keyed-message complete native body and block helpers

Completed30fdb8..30ff0c,333584..3335a4 and3335d8..3335f4 as C. Preserves native reversal/scratch layout, initial zero-block resident cipher before key installation, two subkey shift/reduction branches, padding, critical-region order and result reversal. Reduction helper ignores R1 and uses native immediate0x87000000; no invented3357c0 data dependency. Non16 input reversal always reads four bytes; unsupported lengths above4 retain native undefined scratch state rather than fabricated initialization.1536 actualC bounded cases PASS for lengths0..4/16 and256 initial leading bytes, resident cipher responses controlled.2097152 duration/four seedcalls/24 authenticated bytes and288 configuration regression cases PASS. Target `g2/build/c-firmware/20261011/em-keyed-message-round/receipt.json` PASS728 definitions/53 genuine imports, source snapshot stable and hash current. Native incidental integer stack return is retained; host fixture suppresses only its stack-address warning. Cryptographic/native execution, remaining child bodies, data/layout and hardware gates remain open.

## Record finalization body

Completed32c2b0..32c3bc as C: ordered access/CRC seed storage, channel transform, mode/PHY fields, secure material copy/XOR, record identifier computation and optional callback. Four genuine native seed/channel children remain imports; callback address remains live RAM contract.512 actualC controlled cases cover every secure byte and callback present/absent, children/order/output effects; globals and callback pointer normalized for host.1536 keyedmessage and40 apply regression cases PASS. Target `g2/build/c-firmware/20261011/em-record-finish-round/receipt.json` PASS729 definitions/56 genuine imports; source snapshot stable/currentSHA19a4d0f08b3e1f4529930cb5339a6879bcd9bf180f430769c55f12e6f1c0ed6d. Fullimage/native-child/crypto/layout/hardware gates remain open.

## Access seed and channel children

Completed318878/3189cc/318960/3188b8/30e3fc as C, selected64 authenticated nonexecutable334c6c..334cac tablebytes from two upper-five-bit bounded consumers. PRNG uses existing selected310850 via native30c478 tail. Mix retains native MPYUW inlineassembly; channel transform rereads two maskwords each iteration, preserves37-channel ordering and incidental result.131072 bounded actualC seedcases,65536 normalized MPYUW mixcases,65536 channel masks and64 exactdata bytes PASS;512 finish/40 apply regressions PASS. Target `g2/build/c-firmware/20261011/em-access-seed-round/receipt.json` PASS734/52 stable/current sourceSHA879806ce512feae1a4a8955fbaba83e1a0746b34dd49a45b30108ea6fd4da427. Host fixtures do not prove native ISA, entropy, crypto, layout or hardware. Next connected327718 native body inspected; audit parent return/callback consumption against native before reduction.

## Full stream setup and native caller correction

Completed327718..32780c native stream setup in C: parent mode byte, selected accessmix, channel transform, fresh parent/id reads, packed CRC/id, PHY/mode fields, secure copies/XOR and optional callback. Native incidental return preserved as integer/callback result. Native309dc4/309e00 proves recordapply modebit6 association write targets record410; corrected prior erroneous return-pointer dereference and strengthened40-case regression. Earlier apply fixture superseded for this destination; evidence in `record-apply-return-audit.json`.1536 actualC setupcases and512 finish/131072seed/65536mix/65536channel/40apply regressions PASS. Host children/global pointers normalized; no crypto/nativeISA/layout/hardware proof. Target `g2/build/c-firmware/20261011/em-stream-setup-round/receipt.json` PASS735/51; snapshot stable/currentSHA8cbedc339d761a2c79c8aa1cdb067d5519dda1c2277734870b810ce5f07285e7. Remaining timing/extendedapply/full-image bodies and data/layout gates open.

## Native timing and unsigned division

Completed30c3a4..30c40c and30c40c..30c414 as C with native two-word restoring division, quotient-mask overflow0 behavior and wrapping add-minus-one. Zero divisor retains nonterminating native scale loop via compiler barrier; inspected, not executed.1044570 bounded actualC cases for ordinary/arithmetic and overflowing boundary models PASS,1536 setup/288 configure/40 apply regressions PASS. Target `g2/build/c-firmware/20261011/em-native-timing-round/receipt.json` PASS737/50, stable/current sourceSHA332997c14070bdc5b7d769210d178efbc1e0debf2943de033f425c7409e6da88. Nativeinstruction listing/contract recorded; no live nativeISA/layout/hardware proof. Next309e60 extendedapply still genuine incomplete body, native entrance inspected. Fullimage gates remain open.

## Full extended record apply

Completed309e60..30a0a4 in C: free/existence/association gates, record allocation, PHY/encryption, extended timing/count adjustment, native DIV/DIVU/MPYW/MPYUW/MPYWHL arithmetic, mode spans/totals, finish, stream allocation/setup, callback association, task event. Native timing failure returns original requested stream count without release (preserved), unlike stream allocation failure release/13. Final size-before-length volatile loads made explicit.384 actualC controlled cases cover eight failures/success cuts and association/secure/options/single/alignment branches;71,168 validator/40 apply/1,044,570 timing regressions PASS. Host ISA arithmetic normalized only for tested small operands; native assembly retained in target. Final `g2/build/c-firmware/20261011/em-extended-apply-ordered-round/receipt.json` PASS738/49, stable/current sourceSHA0382631d43856f16f0e5da904e22472f512af332d9e1c45e7a47ce9b88bfa124; earlier un-ordered receipt superseded for finalsource.49 unresolved symbols include genuine resident ROM contracts/data/whole dispatch bodies, not49 missing functions total. Next association callbacks3290c4/3291d0/3291e4 or streamprocess317680. Fullimage/layout/crypto/hardware gates remain.

## Association cleanup callbacks

Completed3291d0..3291e4,3291e4..32922c and327a4c..327a54 in C. Callback prototypes now accept native fullwidth incoming id, find selected association and clear96 bytes at+176, or first mode1 record matching association word180. Native noactive/null guards preserved; zero association can match zero field.2048 actualC count/mode/match cases and exact96-byte clear extent PASS;40 apply/384 extendedapply regressions updated to correct callback ABI and PASS. Target `g2/build/c-firmware/20261011/em-association-cleanup-round/receipt.json` PASS741/47, stable/current sourceSHAd1f222d45b2949f1ac2c706ef83cd3b2b1a11788d984113932b4dac4e3875dc6. Globals/find/memset normalized for host; no native/runtime/layout/hardware proof.3290c4 larger fullcallback inspected; native MPYDU pair outputs need genuine ISA preservation, nextbody. Fullimage gates remain open.

## Full association update callback

Completed3290c4..3291d0 as C with native fullwidth idR0 ABI, ordered two lookups, secure-copy and post-copy secure reload, record-to-association fields and native MPYDU/MPYWHL product projections. Namedr2/r3 helper preserves genuine low/high outputs; target objectdisassembly confirms twoMPYDU plusoneMPYWHL within selectedcallback.4096 actualC controlled secure/field/carry cases PASS,2048 cleanup/96extent/40apply/384extended regressions updated ABI and PASS. Host product arithmetic normalized; target instruction presence is not nativebehavior equality. Target `g2/build/c-firmware/20261011/em-association-update-round/receipt.json` PASS742/46, stable/current sourceSHA8c92001fdcb0fcfa2fb470732d3e2ad7c8f75303d6103a3c4627b51f104d8c25. Native/target listings retained. Fullimage/ROM/data-layout/crypto/hardware remain open; next317680streamprocess or unresolved dispatchers.

## Full stream-processing C body

Reduced317680..3177e8 complete native body to C, packet-take/exhaustion release/notification/counter/error path, fields andpayload location, zero/nonzero segmentation, native multiply/timingcarry, callback-present flag branches and queue ownership.2080 actualC zero/nonzero length0..64/unit1..16/mode0/1 cases andone exhaustion/counterwrap PASS. Callback-present branches implemented fromlisting but notyet compared; publishedtimingpointer/globalchildren/ISA normalized for host.4096 associationupdate regression PASS. Target `g2/build/c-firmware/20261011/em-stream-process-round/receipt.json` PASS743/45, stable/current sourceSHA82bd7d313dd4d3a63a35b2559fb5a30e19e9263151a9eb4f7c8dffdad785e2ca. Complete body C is not complete nativebehavior proof; next callbacks-present timing/notification fixtures andremaining genuine dispatch bodies. Fullimage/ROM/data-layout/hardware remain open.

## Stream callback branch checks

Extended `verify_stream_process.py` actualC fixture with64 callback-present lengths1..64, native high/low timingcarry from controlled products, payload/header/trailer addresses, alternate zero/nonzero callbackresult flag0/4, andtwo exhaustion callback enabled/blocked cases. AllPASS withexisting2080 segmentcases andone exhaustion-counterwrap. Published ephemeral pointer normalized solely for host inspection; callbackside mutations/nativeISA/crypto/hardware notproved. Selectedsource unchanged: em-stream-process-round snapshot stillcurrenthash,743/45 candidatePASS. Next unresolved native dispatcher/source frontier remains.

## Event47/48 dispatcher

Completed331100..33118c as C with actualinputR0 ABI, ordered eventmask47bit0/eventmask48bit7 andenablebit5 gates, allocation62length9/5, exactnativepayload bytes/code33/32, header-minus2 send andhandledbool.262144 actualC alltype/maskbytes,enable/allocate outcomes andpayload/send pointer cases PASS;stream2080+64timing+2notification regressions PASS. Target `g2/build/c-firmware/20261011/em-event47-48-round/receipt.json` PASS744/44, stable/current sourceSHA7a141b8924e21c34159c7d22cb9a48d943ce222c32796e6b02add7b70b73bcd8. No nativeISA/layout/hardware proof.331204 commanddispatcher first12byte unpack/readorder inspected; next fullnativebody. Fullimage/ROM/data gates remain.

## Command2083/2084/2086 dispatcher

Completed331204..331334 as C preserving native capturedbyte order, six initialized half/byte fields for2086 with uninitializedscratchpadbyte11, little-endian command fields and id/status response layouts, post-allocation command reread and allocation-failure handled1.6144 actualC command/inputpattern/alloc/mutation cases and262144 event47/48 regression PASS. Three genuine childcommand imports added. Target `g2/build/c-firmware/20261011/em-command208x-round/receipt.json` PASS745/46, stable/current sourceSHAbe217a5aee0778726d94a2da83083dfcb4a457ab71b8844cfd2b42a4f63171dd. Targetdisassembly confirms seventh30dc20 argument=input+8 inR6 andfirstsix registerargs; fullchild/native ABI/runtime nototherwise qualified. Native andtarget listings retained. Next30db64/30dc20/30dccc realchild reductions. Fullimage/ROM/data-layout/hardware remain open.

## Command validation children

Completed30db64..30dbd4,30dc20..30dc48 and30dccc..30dd04 in C preserving busy gate/kindstatus, ordered field validation, native unsigned fullword bounds, flagmask0xffbf and list scan, native MPYUW products and signed comparison, genuine applychildren3093a0/309514/3098ac.1124210 actualC bounded validation cases PASS,6144 dispatcher regression PASS. NativeMPYUW retained in target; host scalar products only qualify tested small operands. Target `g2/build/c-firmware/20261011/em-command-child-round/receipt.json` PASS748/46, stable/current sourceSHA3b93a916651f8394c43044f4515cdb334742837af0368d9962f641076e37e52f. Childimports replace prior wrapperimports; no fullnativeABI/layout/hardware proof. Next three genuine applyproviders. Fullimage/ROM/data gates remain.

## Command mask apply 3098ac round

Completed native body 3098ac..309910 in selected C, preserving pre-validation flags writes, fresh capacity reads, high-before-low mask stores, partial masks on failure, and native six-bit shift masking. MPYUW remains genuine ARC assembly. Host controlled RAM/arithmetic checks pass 1,114,112 cases; prior command wrapper checks pass 1,124,210 cases. Host fixtures do not establish ARC runtime or hardware equivalence.

Settled em-command-mask-round target receipt: 749 definitions / 45 genuine unresolved symbols; stable selected source SHA256 `9d5d2e26d12ebc061be80cfea32bd2d9041cda4a13ec517f82cc49612274464f`. Full image source_complete=false. Next command body frontier: 3093a0 and 309514. Full component completion remains 0/6.

## Command configuration 3093a0 round

Completed native body 3093a0..309514 in selected C. Preserved pool claim/144-byte clearing and buffer reset before busy/duration/flag failures; native unsigned max, eight-argument duration child, callback timing, raw seed, and ordered record/control writes. Three genuine providers are exposed: 31ac08 ready predicate, 312be4 duration, 32d7f4 callback address. No executable native address substituted for callback source.

Eight controlled host scenarios PASS (absent record, exhausted pool, pool claim, busy, duration overflow, flags rejection, successful stores). Native MPYUW normalized and children controlled; actual ARC runtime, initialized data and hardware remain unqualified. Mask regression 1,114,112 cases PASS after bounding extraction.

Target em-command-config-round receipt passes: 750 definitions / 47 unresolved symbols, stable source SHA256 `f3d7432c5c429a6696ff244498e69fd4b9ffd47bcea565dbf03dcbafb2c02b9a`. More unresolved symbols reflect genuine revealed child providers. Next root frontier: 31ac08 and 312be4 complete children, then command309514's DSP multiply/accumulator graph. Full component completion remains 0/6.

## Pool lookup and duration children round

Completed native31ac08..31ac3c (occupied first row with fullword ID equality), 312b88..312bb4 (PHY duration piece), and 312be4..312c5c (segmented duration). Native DIVU/MPYW/MPYWHL/MPYWHUL remain genuine ARC instructions; no guessed generic arithmetic replaces target ISA operations. Native threshold, explicit halfword casts, quotient decrement for zero halfword remainder, tail and timing wrap preserved.

Host normalized arithmetic and controlled RAM checks PASS 262,592 cases; these cover bounded small-word nonzero-divisor arithmetic and pool count0..255/ID0..256. No full ISA, zero-divisor, overflow or hardware qualification claimed. Command config regression eight cases PASS.

Target em-duration-children-round passes: 753 definitions / 45 unresolved symbols. Stable source SHA256 `65924fdb1e687abad0c499237babab8072eea4163a6f8443837fab756bc26e0b`. Remaining command graph: callback32d7f4 and309514 full apply with native DSP accumulator graph; full component completion still0/6.

## Radio callback32d7f4 round

Completed native32d7f4..32d910 both control/payload paths, authenticated five-byte334474 template, fresh control/buffer pointers after children, native MPYUW and modulo64 mask, ordered halfword/mask stores. Replaced callback address-only void declaration with observed record argument/uint32 return ABI. Four real children exposed:3239d4,323c94,31dd88,324594.

Seven host controlled child/fixed-RAM scenarios PASS including control pointer mutation, no slot/empty entry, payload indices1/33/65, mask/payload/state changes. Five template bytes match stock binary. These are scoped host effects; native runtime, complete child semantics, data/layout/hardware remain open. Duration regression262,592 and command configuration8 PASS.

Settled target em-radio-callback-round passes 754 definitions / 48 genuine imports, stable source SHA256 `798f588222db0d423fcaac5b27356d3961b5a5265d4eaf5b4398a0d7a3c696bc`. Next full source frontier: four callback children and command309514 DSP accumulator graph. Full components0/6.
