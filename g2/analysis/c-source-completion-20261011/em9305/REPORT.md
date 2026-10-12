
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

## Radio encoding children round

Completed native3239d4..3239fc (unmasked packed header), 323d1c..323d38 (paired six-byte address), 323c94..323d1c (34-byte complete record serialization), reusing source-owned3045e8. Original mixed-width fresh reads and exact output store order retained, including high-before-low header and captured halfword before overlapping output writes.

86,272 host actual C checks PASS:65,536 packed field cases and20,736 record serialization/overlap cases (256seeds,81output offsets, aligned source). Native ordered-read/store reference model qualifies host effects only, not ARC runtime/hardware. Callback seven-case regression PASS.

Settled em-radio-encoding-round target PASS 757 definitions/46 genuine unresolved symbols; stable source SHA256 `ad8840cee2c5dd88c38d8ec7e451280c0931df7091dcebf4307a3bf37f8632ca`. Remaining callback children324594 and31dd88;324594 maps to nine-argument323dc0 with caller stack argument, broader record composition body remains. Full component completion0/6.

## Composition entry324594/3245ec round

Completed native324594..3245ec and3245ec..324628 in selected C, deriving byte flags from authentic global805a98/record716/804 and initializing five-byte event. Nine-argument323dc0 remains true complete-body import. Host2,162,688 cases PASS:32global patterns x256field x256active plus65,536null-record flag cases; fullword count and nine arguments checked with controlled child.

Target324594 object confirms ninth count argument `st_s r3,[sp,0]`, R4=sp+4 template, R5=length,R6=output,R7=7 and genuine R_ARC_S25W_PCREL323dc0 call. These confirm local boundary placement, not full composition runtime or hardware. Serializer86,272 cases regressionPASS.

Settled em-compose-entry-round target passes 759 definitions/46 unresolved symbols; stable selected source SHA256 `c5a637edff1411caf5a76e045363df440bcf653ed04ded65b89f315f4d05bf85`. Full composition323dc0 and transfer31dd88 remain substantive root frontier; full component completion0/6.

## Full transfer31dd88 round

Completed native31dd88..31df6c initialization and optional-source timing path in selected C. Source-owned slot adjust317c10 and duration piece312b88 reused; native MPYUW/DIV/MPYDU retained. Six callback source addresses replace native executable literals; channels317ac0/PHY tables31b6cc/limit317b10/scheduler313424 remain true providers. Original writes, fresh input/PHY reads, null-source incidental slot+64 return and product-derived nonnull return preserved.

Four host fixed-RAM and controlled-child cases PASS covering null/non-null source x PHY mutation. Init ranges, fields, callback address, duration/scheduler args, timing/product masks inspected; ISA arithmetic normalized only in fixtures. Actual children, runtime placement and hardware remain unqualified.

Settled em-transfer-round target PASS 760 definitions/55 unresolved symbols; stable source SHA256 `275cceda94d58b40f57769318324472baca0f1064d81cb1c631699f5432820a8`. Increase in imports is full transferred graph revealing authentic lowers. Remaining root substantive frontier: composition323dc0, command309514, four transfer children and six callback bodies. Full components0/6.

## Transfer children round - target pending

Completed native317ac0 channel-map compaction,31b6cc capability PHY tables and317b10 duration limits in selected C. Preserved fresh low/high map reads, four127/126 table entries with native postincrement extent332..335, exact default-PHY16x size term, PHY3 signed min/max on nonnegative halfword domain, explicit halfword return and incidental pointers.

Host1,769,472 cases PASS (65,536map patterns,65,536capability patterns,1,638,400limit/PHY cases); transfer four-case regressionPASS. Host evidence does not establish native runtime/hardware. Source SHA256 `82cec6edfbac221e66bf9c74ca36474dd524d68dccb0fe86dffecccf87a2dc19`. Target em-transfer-children-round remains live in exec session45337; do not restart on observation timeout and settle this same handle before new selected edits. No settled count claim yet. Ghidra MCP discovery found no running instances; saved authenticated native listings remain available. Full component completion0/6.

Transfer children target settled: same session45337 completed PASS, 763 definitions/52 unresolved; stable snapshot SHA256 `82cec6edfbac221e66bf9c74ca36474dd524d68dccb0fe86dffecccf87a2dc19` matches current source. Supersedes prior target-pending status. Full source_complete=false.

## Transfer callbacks31df6c/31dc68/31e7c8 - target pending

Completed three native callback bodies.31df6c clears pending only when both source bytes nonzero;31dc68 retains event return and clears global bytes before genuine31dfd0 tail call;31e7c8 gates status before dereference and retains halfword counter wraps/untruncated incidental returns. Updated address-only callback declarations to observed argument/return contracts.

197,634 host actual C fixed-RAM cases PASS (pending byte pairs, mode/tail effects, all16bit counter values both modes, invalid/null address status gates). Controlled31dfd0 tail child; no native/runtime/layout/hardware proof. Transfer children1,769,472 regressionPASS. SourceSHA256 `c96fc8f20378a6453b65ca8d2cfadb2766870b1885beebfcb7036f10d7f6e873`. Same target em-transfer-callbacks-round session56678 remains live; settle it before selected source edits. Remaining transfer graph scheduler313424 and callbacks31dca0/31dfd0/31e620. Full components0/6.

Callback target pending status superseded: same session56678 terminal PASS, stable snapshot matches current source. Defined 766, unresolved 49. Full source_complete=false.

## Full reset callback31dca0 - target pending

Completed native31dca0..31dd88 early gates, optional slot-index callback, byte/halfword global reset order, source state writes, genuine prepare32780c/query3253a4, selected auxiliary/request providers and fresh pending length after optional payload callbacks. Native DIV retained. Callback return/source argument now observed typed contract.

Eleven host fixed-RAM actual C/control-child/function-pointer scenarios PASS: type3 early gates, start/query early returns, optional index callback, mode0/mode1/mode2 payload callbacks, pending mutation and16bit request span. Native DIV normalized only in fixture. Transfer callbacks197,634 regressionPASS. No native child/layout/runtime/hardware proof. SourceSHA256 `b170024b6b232a3cca36a525c9adee9e119b0b97950b419ebb132f8052fc8b72`. Build em-callback-reset-round live session19322; settle same handle before selected edits. Remaining transfer branch scheduler313424 and callbacks31dfd0/31e620, plus two exposed prepare/query providers. Full components0/6.

Reset callback target settled: same session19322 terminalPASS 767definitions/50unresolved, stable SHA256 `b170024b6b232a3cca36a525c9adee9e119b0b97950b419ebb132f8052fc8b72` matches current source. Supersedes pending target status; full source_complete=false.

## Reset allocation3253a4 - target pending

Completed native3253a4..3253bc using source-owned WSF event allocator313fd8. Native delay-slot halfword narrowing applies after requested+12, null returns0, nonnull returns native32bit pointer+2 including wrap. This provider is allocation rather than an abstract query; earlier call name retained for existing references.

524,288 host actual C/control-allocator cases PASS across all16bit inputs, highword patterns and null/non-null/overflow pointer returns. Reset callback eleven-case regressionPASS. Child allocator and runtime memory/layout/hardware unqualified by this host test. SourceSHA256 `59bf8b3bd5a92306efa30b6b5b9c8a34889883854ca8bd80791a37acbcb2c0cb`. Target em-reset-allocation-round remains live session8179; settle same handle before selected edits. Remaining reset lower prepare32780c plus scheduler313424/two callbacks31dfd0 and31e620; broader composition323dc0/command309514 remain. Full components0/6.

Reset allocation target settled: same8179 terminalPASS 768definitions/49unresolved; source snapshot matches current hash. Full source_complete=false. Preparation32780c has stack pointer/output state and optional callbacks; full native listing retained for next reduction.

## Full preparation32780c round

Completed native32780c..3279a4 in selected C: force/third-argument early gates, stack state provider contract, empty-data/reinit/transmit paths, optional callbacks, sequential payload flag writes, captured flag and fresh payload length after callbacks. Reuses source-owned segment-header323d70/current-request303d58 and aligned authenticated eight-byte334464 template. Native scratch remains uninitialized before genuine32d694 state writes; no default payload fabricated. Native DIV retained.

Eleven host fixed-RAM actual C and controlled-child cases PASS; covers third gate, forced/pending reinit, optional empty callback earlyzero/nonzero, transmit callback bypass, active flag derivation, mode0/1 payload callbacks and mutated final size/flags. Eight template bytes exact stock match; allocation524,288-case regressionPASS. Host fixture normalizes DIV and controls real children; no native child/runtime/layout/hardware proof.

Settled same62743 target em-prepare-round PASS 769definitions/49unresolved, stable current SHA256 `d027a0b81d98ff7a7ead5fc7996f577639b3381b5e68ba14fa02484b774657a8`. Full source_complete=false. Next state provider32d694, scheduler313424, callbacks31dfd0/31e620, broader composition323dc0/command309514 remain root frontier. Full components0/6.

## Preparation state and short header closure (2026-10-11)

Completed selected C bodies: preparation state32d694..32d738,
queue single-element predicate313fcc, and short-header decoder32dedc..32df24.
The preparation state retains empty/raw/segmented packet paths, native MPYUW,
unsigned underflow/truncation, fresh queue/packet reads, optional field preservation,
and native volatile store ordering (state halfword0 precedes word12).
The selected existing WSF peek is used directly. No placeholder lower provider.

`verify_prepare_state.py` passes139269 scoped host cases, including all256x256
header flag/extra-byte combinations, empty and raw queues, and segmented
length/index/unit/single/extra combinations. MPYUW is normalized to unsigned
multiplication only in the host harness; this is source-contract checking,
not native ARC runtime or hardware validation. The preparation parent regression
continues to pass11 cases.

The first target pass at `em-prepare-state-round/receipt.json` had772 defined
symbols and48 genuine imports. A subsequent native-order audit corrected the
state0/state12 store sequence; the authoritative current snapshot is
`em-prepare-state-ordered-round/receipt.json` once its build settles.
Remaining:48 imports in this selected closure, plus unselected native bodies,
authenticated data ownership, placement and hardware qualification. Import
count is not a whole-component remaining-body count. Full EM component incomplete.

Ordered target build settled PASS: 772 definitions, 48 imports; stable current source SHA256 `99485cab18cdd8dbef6da2c6b992e0d71c5d443e8ff33fcacaecc27a9df9e0e1`. Authoritative receipt: `g2/build/c-firmware/20261011/em-prepare-state-ordered-round/receipt.json`. Full component remains incomplete.

## Packet advancement and duration provider connection (2026-10-11)

Completed selected32d738..32d790 packet advancement: empty, raw and segmented
queues; next-index MPYUW threshold; byte-index wrap; global handler publication;
packet publication before selected WSF event removal; boolean result.
Native32d788 is BL.D's delay slot and therefore runs before313ff0. A temporary
register-residue adapter was removed after this delay-slot audit; it is not part
of the authoritative selected source.

`verify_packet_advance.py` passes9437185 scoped host cases with a controlled
removal child that verifies packet and handler publication already occurred.
All256 handler/index values and representative unit/length thresholds are
covered. MPYUW is normalized only in this host harness. Existing duration
references named channel_timing_312b88 now resolve to the already authenticated
radio_duration_piece_312b88 body with the same three-argument contract, verified
against native312b88. No fake provider or new body inferred from name alone.

Authoritative target round: `em-packet-advance-ordered-round/receipt.json`.
Source completeness, unselected bodies, data ownership, final placement and
hardware qualification remain open. Earlier `em-packet-advance-round` is
superseded because it contained the unnecessary residue adapter.

Packet advance ordered target round settled PASS: 773 definitions, 47 imports. Stable current source SHA256 `317957c56adde921773fb149b45b6e6bcce94190a6ec783178adcbb76d26981f`. Full EM image incomplete.

## Packet completion closure (2026-10-11)

Completed32d790..32d7f4 selected C, connected to real existing WSF release,
queue append, critical entry/exit and event posting providers. Segmented packet
completion releases its referenced payload, enqueues packet-12 in8056dc,
increments global805ab4 under the WSF guard and freshly reads source376 for
its byte increment. Raw completion releases the packet directly. Event handler
805b18 is freshly loaded; saved packet805cd4 is cleared in the native BL.D
delay slot before event posting. Empty completion preserves incoming R0.

`verify_packet_completion.py` passes513 scoped host cases using controlled
children for both ownership paths, all global counter values, child mutation
of the source counter/handler and event-post visibility of the clear. The
packet advance regression passes9437185. Target receipt for this chunk is
`em-packet-completion-round/receipt.json`. Whole-image source/data/placement
and hardware gates remain open.

Packet completion target settled PASS: 774 definitions, 47 unresolved symbols. Stable current source SHA256 `9ee13b3c715d04a1ba5280d66251df439edcd3156a051f2f7bbede3f2cc9885d`. Remaining selected import frontier47 plus unselected bodies/data/placement/hardware; full component incomplete.

## Duration quantization source closure (2026-10-11)

Completed full312c5c..312ca0, preserving both unsigned threshold branches,
wrapped full-word additions, comparisons and native MPYMU/MPYUW/MPYWHUL.
Current coherent target build `em-duration-quantization-round`: 775 definitions/46 imports, candidate compile/link PASS. Native little-endian DSP contract
is saved in `duration-quantization-native-contract.json`. Target object checks
find both reciprocal constants and all original multiplication instructions.
The compiler inlined both reciprocal branches into common_channel_start_314db8;
no call relocation remains. No unverified divide formula was substituted.
This is target instruction/source connection proof, not a native arithmetic
runtime, placement or hardware oracle. Packet completion513 and preparation
state139269 scoped regressions pass.

Stable current source SHA256 `68f7ae44711ca0b0fc83e9667f7a83c70486c5dff37924036d01470d0bf6c156`. Remaining selected import
frontier46 plus unselected bodies, authenticated data, placement and hardware;
full EM component incomplete.

## Full command application309514 source reduction (2026-10-11)

Completed309514..3096a8 with its seven-argument native contract: signed
interval-distance rejection, unsigned position guards, budget/duration checks,
optional timing callback and pointer refresh, buffered copy, immediate-transfer
copy/mandatory prepare callback, native MPYD/MAC scheduling, post-write signed
failure, optional notify callback, and deferred 64-bit mask update. All original
partial effects and explicit fresh reads are retained. Mask helper3027c8 is
expressed as a guarded two-word shift with native six-bit shift masking.
The source buffer and native table aliases remain real typed addresses.

`verify_command_apply.py` passes266 scoped host cases: ten state/callback/copy
cuts plus all256 deferred-position indices. Children are controlled; MPYUW is
normalized and MPYD/MAC output is a fixture. These check selected source
behavior against the recorded native contract, not native DSP arithmetic.
The budget failure fixture respects the native alias between803f7b and
803d78+515 (one production byte, not two independent fields).

`g2/build/c-firmware/20261011/em-command-apply-round/receipt.json` is terminal
PASS with776 definitions/45 unresolved symbols. Current source snapshot is
stable and matches SHA256 `3e0e7783498ee6320a464a1f638396c06fa8496147decf7fe8cafe43818e49ee`.
Target object verification retains MPYD, MAC and MPYUW. Remaining selected
import frontier45 plus unselected native bodies, source-owned data, final
placement and hardware qualification. Full EM image remains incomplete.

## Full receive callback and connected gate source (2026-10-11)

Completed31e620..31e7c8 selected three-argument C callback: pending termination
and optional id callback, all status discard/retry cases, type3 context gates,
real short-header decode, status6 parity rejection, receive counter accounting,
state/gate/check/command providers, prepare/auxiliary handling and finish.
The decoder output pointer is captured before its native BL.D child call;
returned header length indexes the packet. Reception check's low bit guards
the command branch, while its fullword nonzero value guards later failure.
A value2 therefore signals and still enters the eligible command branch.

Connected full324f68 gate,32d5ac advancement,324fb0 completion adapter and
3253bc packet release adapter. Original sequential stores/reads, byte wrap,
64-bit counter carry and incidental R0 returns are retained. The optional
callback pointer in32d5ac is only tested for presence; native does not call it.
Packet release subtracts2 before selected WSF event release's header offset.

`verify_receive_callback.py` passes18 scoped state cuts using the actual
header decoder and controlled lower providers, DIV normalized. Gate children
pass131081 scoped host cases: all256x256 parity pairs in two modes, presence
and mode gates, counter carry and two true child adapters. Target parent round
`em-receive-callback-round/receipt.json` passed777 definitions/52 imports;
its coherent captured source SHA256 was
`cead612761769bfcd717fcd13a0c513dcdae4a05eca18e4d2a06e2de32191463`.
The current gate-children target round is
`em-receive-gate-children-round/receipt.json`. Native/runtime/data/placement
and hardware gates remain open; new parent imports are genuine lower bodies.

Gate-children target round settled PASS: 781 definitions, 49 unresolved symbols; stable current source SHA256 `dc2600629a0a9f74ea765215c00cd7c2796eb23cce6f0dff9303f6ca3666c588`. Remaining selected import frontier49 plus unselected bodies/data/placement/hardware. Full EM component incomplete.

## Receive allocation, publication and finalization (2026-10-11)

Completed324ea4..324f68 receive-state allocation: optional id callback's
allocation bypass, parity/size/kind guards, sentinel failures, fresh allocation
credits, 64-bit packet counter carry and fresh sequence-byte update. Callback
8052cc is tested for presence here, not invoked. Full325374..3253a4 packet
publication writes two-byte metadata then enqueues and posts event2. Full
3253c4..32543c routes data/input ownership, conditional publication, null release,
optional payload callback in modes0/1 and fresh narrowed request size.

`verify_receive_allocation_finish.py` passes20 scoped host cases with controlled
allocation, queue, post, release and request providers. Tests include allocator
mutation of credits/sequence, callback mutation of length, id callback rejection,
64-bit counter wrap and fresh handler reads after queueing. DIV normalized;
no native ARC runtime/layout/hardware claim. Receive callback18 and gate
children131081 regressions pass. Authoritative target round is
`em-receive-allocation-finish-round/receipt.json`; data/layout/hardware remain
open and the full EM image is incomplete.

Allocation/finish target settled PASS: 784 definitions/47 imports. Stable source SHA256 `7f8ddfe9102f4c7cf955038065e0d93adb31baa9ecfd5e726f0a7d45fee43e4b`.

## Receive time check and termination message source (2026-10-11)

Completed319838..319890 and325c08..325c40 selected C. The time check retains
flagbit2 early return, captured clock/guard, native MPYUW period, optional
object elapsed comparison, fresh object pointer/timestamp reload, wrapped
required-time arithmetic and unsigned threshold result. Termination preserves
null allocation and four-byte message construction followed by selected
WSF task message send, with handler capture before the halfword id store.

`verify_receive_time_termination.py` passes521 scoped host cases: nine timing
cuts plus all256 reason low bytes with allocator success/failure. Elapsed
provider mutation checks fresh pointer read. DIV/MPYUW are normalized and
providers controlled; no native ARC runtime/layout/hardware claim.

Current coherent target receipt `em-receive-time-termination-round/receipt.json`
passes 786 definitions/45 imports. Stable current source SHA256
`6bd810007a489da24880d63f5f1ae7a7304fc7c3d7e727ee423cd9883dd8c4f7`. Remaining selected imports45 plus unselected bodies,
data, placement and hardware; full EM component incomplete.

## Radio completion callback and window scheduling closure (2026-10-11)

Completed31b7c8 receive predicate, full3330d8..33322c four-argument radio
callback and full window3122fc/start3103e0/resume310430/base310654 children.
Preserves all status/selector/mode paths, counter increment before validation,
source805d18/root805cf4 alias, optional descriptor pointer refresh after child
calls, native length formulas, window failure and freshly loaded second
mandatory callback. Exact five non-executable status bytes3344c0..3344c5
are typed C and verified directly against native bytes.

`verify_radio_completion.py` passes898 scoped host cases: status/mode/selector/
length/extra combinations, owner-child pointer mutation, mode3 finish mutation,
second callback pointer replacement and all256 receive predicate values.
Hardware/deadline/transform providers are controlled, fixed RAM/MMIO is host
fixture memory. No native ARC runtime/layout/hardware qualification. Prior
time/termination521 and receive callback18 regressions pass.

Current coherent target `em-radio-completion-round/receipt.json` PASS: 793 definitions/43 imports. Stable current source SHA256
`9a3218e693e61f5486c4a45dec20fafc8cce730d7b0da1da06fa4f3e1d9276c9`. Remaining selected import frontier43 plus
unselected bodies, data ownership, placement and hardware; full EM image
incomplete. The six native code bodies and one status table are completed
chunks, not a whole-component completion claim.

## Radio follow-up callback 333268 completed

Full native callback 333268..333338 is selected C. Coherent em-radio-followup-callback-round target receipt passes with 794 definitions and 42 genuine imports; source SHA256 e1abde6a0ce13f2e0bc65f27cb8974a1aa1814627b0ea0d58557765b4eb70970. Scoped host behavior fixture passes 98 cases including counter wrap, fresh owner chains, transform counter mutation, configure time mutation, copy ordering and callback refresh. Children are controlled in this fixture; native ARC execution, image placement and hardware remain unproved. Full EM component incomplete; import count is not a count of all missing native bodies.

## Radio status callback 333480 completed

Full callback333480..33354c and predicates311ddc/311df0 are selected C. Coherent em-radio-status-callback-round receipt passes: 797 definitions, 42 genuine imports; source SHA256 b02ac05de9e25a2640636e94c33d6872faca2171c1f74489377657fe05736d4b. Scoped host fixture PASS1536 event/state/MMIO combinations; signed DIV normalized and measured-level/activation children controlled. Follow-up callback regression PASS98. Measured-level311a40 remains genuine imported FPU body. Full EM component incomplete; native ARC execution, image placement and hardware remain open.

## Two-word mask count30c414 completed

Selected C entry contains genuine native ISA assembly: carry-preserving SUB.F/SBC.F and MPYMU/MAC/MAC accumulator sequence retained exactly. Target compilation and relocatable link PASS, coherent source SHA256 9f4260a64b802cdf92f952a8217b1ef55c2f923b0ee76ed7c923fb5d0e3fc06d; 798 definitions/41 genuine imports. Compiled object inspection confirms all four flagged/accumulator instructions. No inferred software popcount substituted; no native execution proof claimed. Prior radio host regressions PASS1536/98/898. Full component and image placement/hardware gates remain open.

## Scan command-dispatch parent completed

Full330c60 dispatch, shared330e10 handler,30dfd8 byte-setting command and3032b4 live info-copy selected C; coherent em-scan-command-parent-round target compile/link PASS 802 definitions/42 genuine imports; source SHA256 fea134d4d60fc7d98567cd710e99d2b6b5cd4c70d96aa9bae8de08b6bfcc585e. Scoped actual-body host fixture PASS2324 cases, controlled lower command/allocation/send, semantic stack packing and mutable request command. Newly exposed lower30ccf8/30df08 remain genuine; full component/layout/hardware open.

## Scan command children completed

Full30ccf8/30df08 and status30e8c0 selected C; coherent em-scan-command-children-round target PASS 805 definitions/40 genuine imports; source SHA256 8b1df0230c90de7cb769c008466514ff958e371b5696451b60d8d6929c6698b4. Actual-body scoped host PASS303, parent regression PASS2324. Payload/handler reads after allocator, capability/guard/length/mode constraints and allocation-failure returns preserved. Native ARC execution and image/layout/hardware remain open.

## Record requests30fc68/30fcd8 completed

Two full record-request providers and state310260 selected C; genuine MPYWHL retained. Coherent em-record-request-round target PASS 808 definitions/38 genuine imports; source SHA256 60fdd1e2161bd225ae836240acf62d83db3c158d5eb12bf92a87ea1f440ccc5d. Scoped actual-body host PASS40 with controlled MPYWHL result/lower children, proving flattened buffer argument, fresh post-child descriptor lengths and halfword wrap, mode gate, fresh unit/extra/time. Child scan regression PASS303. Native ARC DSP execution/layout/hardware remain open.

## Packet request30faec completed

Full packet request30faec and window31041c/failurecallback310360 selected C. Coherent em-packet-request-round target PASS 811 definitions/37 genuine imports; source SHA256 8e84fc80a46761b69e0411de29d5e793538d938903cbb5cb5e1e96442857d526. Scoped actual-body host PASS20, controlled lower children, full passed length vs stored half, pending writes before window, captured state after exit mutation, fresh mandatory callback/kind. Record-request regression PASS40. Native execution/layout/hardware remain open.

## Address lookup303890 completed

Full303890 C, coherent em-address-resolution-round target PASS 812 definitions/36 imports, source SHA256 2cd7e976888e66be10bb7f1f72cb4777ca806f07525d457fa7c81f329477d22a. Actual-body scoped host PASS257 count/disabled/match/callback cases, translated halfword, alias after kind-byte write. Optional callback return ignored; no native runtime/layout/hardware proof. Full component incomplete.

## Resolving address lookup303bdc completed

Full303bdc selected C; coherent em-resolving-address-round target PASS 813 definitions/36 genuine imports; source SHA256 96cbafa5f1eb4cb396dee090828196ce87a5d1ddb644d8a8da9714ba25ea8e52. Scoped actual-body host PASS1026 with controlled key-match child, dynamic count/table mutation, captured successful row, direct/derived matches, disabled rows, cache-ring writes/wrap. Lookup303890 regression PASS257. New key-match315640 remained genuine at this snapshot; full component/layout/hardware open.

## Address key-match315640 completed

Full315640 selected C connects already selected hash314640. Coherent em-key-match-round target PASS 814 definitions/35 genuine imports; source SHA256 b6543df22e96dbfa5c6435584d75b7afc82f515c74d76af9400ec834511ae609. Scoped actual-body host PASS131073 with controlled hash, six-byte split and full returned-word comparison. Resolving lookup regression PASS1026. Hash/cipher ROM, ARC execution, image placement and hardware remain unproved. Full component incomplete.

## Packet validation303404 completed

Full303404..303650 selected C; authoritative em-packet-validation-ordered-round target compile/link PASS 815 definitions/36 genuine imports, source SHA256 7f7d928fe03b441fabfca581d37cadf00fb3ab2b8bdf2f23f03b0a6aa8027ed2. Scoped actual-body host PASS661 policy/classification/filter cuts using real address-byte pack and controlled children. Native LDB.AB.X accesses original packet header before input advances8; signed flag now read at input0, peer address at input8. Initial em-packet-validation-round is superseded. Descriptor cursor output+8, policy decisions and status output20/21 retained. Two new projection children remain genuine. Native ARC execution/layout/hardware unproved; full component incomplete.

## Address projection/association completed

Full303b7c/303844 selected C; coherent em-address-projection-round target PASS 817 definitions/34 genuine imports; source SHA256 41b189b25bd06a9c1eab603178b3627edbb4aa3936500e897ea7b5ece2064916. Scoped actual-body host PASS256 with controlled identity/key providers, cache matches, disabled/key policy, ring writes/wrap and six-argument callback whose return is ignored. Native identity-find31441c inspected to verify R4/R5 remain unchanged across lookup; these are now explicit callback arguments. Packet-validation regression PASS661. Native runtime/layout/hardware remain open; full component incomplete.

## Five-command dispatch330fa0 completed

Full330fa0..331074 selected C; coherent em-command-2059-dispatch-round target PASS 818 definitions/38 genuine imports, source SHA256 7ad792fd03d0b80265bd75e7175c918be005216bb76556595da2c85edcc58246. Scoped actual-body host PASS65536: five native byte-order vectors/response contracts, every unsupported16-bit opcode with null input. Five lower command bodies newly genuine imports; source frontier grows as parent code closes. Native runtime/layout/hardware remain open.

## Five command providers completed

Full30c5c0/30c5e0/30dbd4/30dc70/30d48c selected C; coherent em-command-2059-provider-round target PASS 823 definitions/38 imports, SHA256 8d0b75132fa22c45659664269e3575695c64932f617c4708f901bacef40ddf6f. Scoped host PASS2621480 capability/mode/halfword-domain checks; exact full input forwarding, lower-return contracts, configuration stores. Lower apply/readiness bodies remain genuine imports. Native runtime/layout/hardware open.

## Command apply/readiness leaf chunk completed

Full307d0c/3213d0/309874 selected C, genuine MPYUW retained. Coherent em-command-2059-apply-round target PASS 826 definitions/35 imports, SHA256 02d1b17f55f02074ea970a12318529e8802b7c5e883b6affe1904ab50ad4d600. Scoped host PASS4256 with bounded ids0..7 and MPYUW normalization; readiness bytes, mode preservation, row count/activity and low-width stores. Provider regression PASS2621480. Native runtime/layout/hardware unproved.

## Association command completion round

Completed native bodies 0x307fcc and 0x30805c, preserving distinct lookup/peer guards, guard order, MPYUW stride, fresh handler capture and 10-byte message policy. Coherent target build `em-command-2059-association-round`: 828 definitions / 33 genuine imports; source SHA256 `1623e1899e8c4a82dc1331b6469f0ab814f1ea606b66d88bcb338dd8d2a1992d`. Controlled host fixture PASS 75,130; native DSP and hardware execution remain unproved. Five-command dispatch/provider association graph now source-selected. Full EM component remains incomplete: remaining imports and independent product data, placement, startup and runtime gates require closure.

## Command 2076 dispatch/response round

Completed 331074 and 33118c from native instructions, including post-increment old-address capture, query output byte order and command reread after allocation. Controlled host PASS65,541. Coherent target build `em-command-2076-dispatch-final` passed: 830 definitions / 37 genuine imports, source SHA `e4e757c50ca108d63a59cf5a382fee2bd885ceda39720066840e1d6fe584ba35`. Initial compile exposed historical void declaration; corrected selected typed declaration. Five newly exposed genuine provider imports remain connected; full source/layout/hardware incomplete.

## Command2076 providers and signed query round

Completed seven native bodies 30c65c/30da2c/30da5c/30e000/30bd34/31b768/306fa8. Named MPYUW preserved; query kind4 selects byte335 while kind3 selects334; 0x7e sentinel and signed extension retained. Native guard priorities, message allocation error7, critical exit and full arguments preserved. Controlled host PASS4,400,550; dispatch regression PASS65,541. Coherent `em-command-2076-providers-round` target build: 837 definitions / 35 genuine imports; SHA `fff879b3542ce6b31d5edc923be889d35151cc6510b0a9e25db2b2038b7b8f9a`. Remaining connected apply32754c/327630/327694 are genuine imports; complete source/data/layout/hardware still open.

## Apply327630/327694 round

Two complete native bodies selected, preserving scaled stores, callback timing, captured/fresh base distinction, native MPYUW and signed DIV. Coherent target build `em-command-2076-apply-round`: 839 definitions/35 genuine imports, SHA `79549d12f1b787237a976a92625cf517c83157298fd3103248d0f3ead00935a5`. Controlled host PASS27,664. Remaining apply32754c and connected derive/refresh bodies identified; full source/data/layout/hardware gates remain.

## Apply32754c and derive/refresh completion

Four full native bodies selected:32754c/317b80/317ba8/323268. Signed delta, native state policy, fallback sentinel, captured/fresh table distinctions, eight-byte event, MPYUW/DIV retained. Controlled host PASS230,337; prior apply regression PASS27,664. Coherent target build `em-command-2076-apply-final`: 843 definitions/32 genuine imports; SHA `31e37833be8435537cf60131c2e6b9583205cbb716798d557723abd278d472a1`. Connected command2076 dispatch/provider/apply/query graph source-selected. Whole EM source/data/layout/hardware gates remain.

## Report dispatch330ce0 completion

Full native legacy/extended/type4 paths compiled coherently. Return asymmetry, low-byte length wrap, fresh counter and data reads preserved. Host PASS24,832. Target `em-report-dispatch-330ce0-round`: 844 definitions/31 genuine imports, SHA `768e36936e01c3a71e32cd29c126407802202c65174b3ea407dd36a5ee601cd5`. Full source/data/layout/runtime gates remain.

## Completion303fb8 source-selected, qualification pending

Full native state0/2/3 callback flow is now C, preserving state2 incoming-pointer comparison, callback-address byte133, R17 numeric8013f0 replacement, template-vs-zero descriptor requests, optional and mandatory callback reloads and flag return. Target build `em-completion-303fb8-round` started; no settled compilation/behavior claim yet. Controlled callback-path fixtures and coherent receipt inspection are required before counting this body completed. Full component still incomplete.

Completion303fb8 controlled fixture PASS20 native path contracts, including state0/2/3 callback traces, return flag, raw callback byte133, changed argument8013f0, descriptor fields and packet routing. Native invalid-pointer edge and optional callback mutation remain unexecuted. Target receipt still pending; no target completion claim yet.

Completion303fb8 fixture expanded to PASS25, covering optional null callbacks108/116/120 and absent initialized packet. Selected source unchanged during live target build. Optional callback mutation and native fault edges remain unexecuted.

## Completion303fb8 target round settled

Coherent target compile/link PASS `em-completion-303fb8-round`: 845 definitions/30 imports, SHA `ce493257365966d52808fd9583e719a41b5a1b35228c68dce970e6b895705fea`. Full C body passes25 controlled native-path contracts. Source/data/layout/runtime/hardware incomplete; optional mutation and invalid-pointer native fault edge remain unexecuted.

## Fragment helpers source-selected, target pending

Completed C bodies32e48c/32e4a8/330f48:246-byte allocator request, old-address header store with2-byte advance, low-byte length, fragment status and exact metadata/copy/return. Controlled host PASS132,096. Selected target build `em-fragment-report-helpers-round` live; no settled target completion claim yet. Parent331334 full authenticated listing saved; native DIVU/MPYW capacity policy and244-byte fragment loops require source translation and verification. Whole component incomplete.

## Fragment helpers target settled

Coherent `em-fragment-report-helpers-round` target PASS 848 definitions/30 imports; SHA `5aa399aebebe2eb565bd1a521ff121653454de9c41f4cf972730a158a2643324`. Controlled host PASS132,096. Full parent331334 prepared from native listing with six paths, named DIVU/MPYW/flag-conditioned capacity sequence and fresh chunk/count guards; target/source-path qualification pending.

Full331334 controlled host PASS26,634 across six paths and real fragment helpers. Native DIVU/MPYW/carry preflight normalized only in host fixture. Target build live. Native reread audit identified configword805cac in type32 must be captured before DSP preflight (native331374); pending source-order repair after current build terminal. Current fixture does not execute interrupts, so it cannot prove that order. No settled target completion claim yet.

Initial fragment parent target build passed 849 definitions/29 imports, SHA `55dce20802599c83f3061a9ca8bcab25abcffcd85b479a8a61e47ddf548c75dc`; superseded for type32 config-pointer/DSP volatile ordering. Source-order repair selected; final coherent target rebuild required.

## Fragment dispatch331334 final round

Full six-path C body target PASS `em-fragment-report-dispatch-final`: 849 definitions/29 imports, SHA `3c099c4367ffe14059088c47ed0d49b769a8dd1ace46aff75d7b34e55a08ec59`. Native type32 config capture before DSP corrected; controlled graph PASS26,634. Target retains named DIVU/MPYW and exact carry-conditioned preflight sequence. Hardware/DSP runtime proof remains open.

## Command2030 dispatch target settled

Complete3316e0 five-command body coherent target PASS `em-command-2030-dispatch-round`: 850 definitions/33 imports, SHA `6fdc8dc32c6bd7f03b18496c6552360945dca2986a13347943b5f5ecef325187`. Controlled host PASS65,541; scratch padding deliberately untouched and unread by fixtures. Fresh command response query/packing and status event verified. Lower providers genuinely imported; whole source/layout/hardware remain incomplete.

PHY providers30d4e4/30dd04 and native policy332f3c/332f80 now C. Capability flags, policy status priorities, disabled-field zeroing, active/pending guard and10-byte message layout preserved. Selected target `em-command-2030-phy-round` live; behavior fixture and coherent receipt pending.

## PHY2030 target settled

Completed four PHY bodies: coherent target PASS854 definitions/31 imports, source SHA `16139b14bf4e5066ecf622e8587fadfbf168563ccc80f1226c41bb73c4cd125d`; controlled host PASS65,560. Native connected30c824 query,307008/30701c reads and310634 pending flag now translated; fresh target qualification pending. Remaining2033/2034 command bodies30cba0/30e120 authenticated but not yet translated. Whole image remains incomplete.

Query/slot/pending host fixture PASS10,242 including invalid count/active guards, byte domains and aliased first-write-before-second-read. Named MPYUW stride normalized for bounded host IDs; target runtime remains unverified. Fresh target query round still live.

## PHY query target settled

Four query/read/pending bodies coherent target PASS858 definitions/30 imports; SHA `38fbc7dbc219043bb691894d5c66c9a1feb9e58e2d5b7a05ee7b2c9b718d6ea9`. Host PASS10,242. Next selected command30cba0 plus332c30 channel map and30e4bc count source complete, target/behavior qualification pending. Full callback and scheduler provider ownership remains explicit.

Command2033 actual-body controlled host PASS30,727 across channel/kind/mode/feature/allocation domains, guards, state/record bytes and scheduling order. Bounded MPYUW scaling normalized only for host fixture. Native callbacks are symbolic genuine imports; no opcode or stock-function jump providers. Target2033 round still live.

## Command2033 target settled

Completed30cba0/channel/count C bodies: coherent target PASS861 definitions/33 genuine imports; SHA `d9402effa9fecc526ef73f5de77417f7ee2096e90a6f8432e4b989d6af5b842d`; controlled host PASS30,727. Explicit callbacks/scheduler imports explain import growth. Command30e120 remains in authenticated native frontier; no complete firmware/layout/hardware claim.

Command2034 complete parent C selected. Controlled host PASS8,640 across modes/features, signed power boundaries/sentinels, existing-state updates, kind3 shortcut, allocation failure and scheduling. Child332be4 DSP accumulator result remains genuine import; native leaf preserves R3 allocator257. Ghidra MCP instance discovery returned none this round. ARC objdump DSP decode leaves332c1c/332c2a unknown; retain native evidence and do not invent computation. Target build em-command-2034-round still live.

## Command2034 target settled

Complete parent30e120 target PASS862 definitions/36 genuine imports; SHA `7ba26783a12c281267049c5328fefcdd10ba4dec5f68b4acadcba9aec16c367a`; controlled host PASS8,640. Both command2033/2034 parents now C. True332be4 DSP arithmetic and332b94 pattern child plus four callbacks/shared scheduling providers remain source frontier. Whole image/layout/hardware incomplete.

Pattern332b94 and PN9 generator332c50 now full C. Controlled host PASS2,562 using actual bodies/real memset, all byte lengths and selectors0..9, known PN9 prefix, zero-length/header overwrite and outer-count truncation. Fresh target em-command-pattern-round live. Genuine DSP332be4 remains undecoded.

## Pattern target settled

Full pattern/PN9 bodies coherent target PASS864 definitions/35 imports; SHA `a07763f68d05305bd2ce7efde25a251b5f760c1fc997c75c5523d43002353cf3`; host PASS2,562. Root native decoder follow-up: pinned binutils arc-tbl.h mask identifies previously unknown332c1c word282f0fbf as ASLACC RC and332c2a word309c0c49 as MPYWHL RB/RBdup/SIMM12_20. Exact operand/assembler roundtrip remains pending; genuine duration import preserved.

Completion332cd0 full C with corrected typed three-register callback ABI selected. Controlled host PASS12,000: signed64 carry/borrow, counter truncation and fresh count/limit/state return. Target completion round live. DSP duration exact named-ISA roundtrip attempted; pinned assembler rejects ASLACC226, receipt records native/table matching and SIMM12 decode625. No DSP numeric equivalence claim.

## Completion332cd0 target settled

Typed callback full C coherent target PASS865 definitions/34 genuine imports; SHA `0f53c4fe033b68cd5d92fba7c184d7614a58899325b64598b2aceffa32778167`; controlled host PASS12,000. Remaining connected callbacks332d2c/332db4/332e2c plus shared scheduling providers and durationDSP genuine imports remain. No complete source/layout/hardware claim.

Continuation332d2c full C selected with actual one-register callback ABI; count-down30e48c source-owned. Controlled child/mutation host PASS1,600; target em-command-continuation-round live. Genuine stop30b654 and common-release304588 imports added, not fabricated. Remaining native2034 callback listing saved in command-2034-callbacks-native.arcem.txt.

## Continuation332d2c target settled

Full continuation/count-down C coherent target PASS867 definitions/35 genuine imports; SHA `b5aabb38d86b79578e9cb41e816aa756e9335cc7c39f2fbe72a07e1ef80a72f4`; controlled host PASS1,600. Callback332db4 full body prepared from native listing, not yet selected;332e2c and genuine stop/common-release/scheduling/DSP remain. Source compilation is not complete firmware proof.

## Policy332db4 target settled

Complete callback target PASS868 definitions/34 imports; SHA `8584660ce5ab9ab6d8486e0a15b5ddf087a4b4f3653db3860a32f2e50c209d02`; host PASS65,280. Last connected332e2c prepared; true DSP and stop/common-release/scheduling providers still open.

Final connected callback332e2c full C selected with actual pointer ABI. Controlled host PASS3,600 across counter limits, child-driven state changes, five mismatch/update cases, packet/header/config fields, duration call and schedule/release/response cleanup. Native duration DSP still a controlled child in host fixture, not numerically proved. Target policy-continuation round live.

## Final connected policy continuation332e2c target settled

Full callback coherent target PASS869 definitions/33 imports; SHA `6586b1ac56b0241f22f5a19919354b8a1bd8fd5e1c0815dfe8d2975d9bc5c462`; host PASS3,600. All four directly imported2033/2034 callbacks now C. Remaining connected source gates are genuine durationDSP332be4, stop30b654, common-release304588, common-request30455c and schedule313220; wider image frontier remains.

Stop30b654 full C selected; controlled host PASS360 across native state1/kind3 fast release, state1/2 report copy+clear, unsupported state and auxiliary child mutation. Target stop round live. Common-release304588 native indirect callback retains own address R0, role R1, slot R2, base R3, offset R12; exact named ISA source planned to preserve ambient register ABI, rather than guessing callback prototype.

## Stop30b654 target settled

Full stop C target PASS870 definitions/32 imports; SHA `72b52ed51d531232dd52308da534d05088c310e389649abfde2b44c229703b8a`; controlled host PASS360.

Shared common-release304588 now complete named ISA assembly in selected C, preserving all native callback arguments/ambient registers and delay-slot store. Standalone assembler produced identical56B native body except 4B external no-op call relocation, source receipt retained. True30fd28 no-op C identity is selected; target common-release round live. Common-request30455c prepared separately while snapshot active.

## Common release target settled

Full native named ISA release304588 and C no-op30fd28 coherent target PASS872 definitions/31 imports; SHA `decd5d84829223b27e736a48ad05b453dafb54ae35359a686a12457b075ff508`. Exact56B standalone native body proof outside call relocation retained. Runtime callback ABI preserved by assembly; no hardware/runtime completion claim.

Common-request30455c and no-op30fd2c full C selected. Controlled host PASS192 with bounded stride normalization, selection guard, child count mutation, 32-bit overflow and slot address return. Target request round live. Full queue scheduler313220 prepared in separate C while snapshot active; exact native queue/current-object timing and guard read order retained, qualification pending.

## Common request target settled

Complete request/no-op C target PASS874 definitions/30 imports; SHA `56753e69e01f77bb9819e89cc5f72cfbb46c4b64e54f39a4d0d8caa1918453e4`; controlled host PASS192. Scheduler313220 now next selected full native body.

Scheduler313220 full C selected. Controlled host PASS11 focused native path cases: empty/prepend/active object tail/gap/two-object traversal/special head timing, reciprocal links and guard read counts. First fixture expected gap case was corrected (next-start15 vs threshold11/17); source was unchanged. Target em-schedule-insert-round live; native wrapping sign-bit order retained.

## Queue scheduler313220 target settled

Complete queue scheduler C coherent target PASS875 definitions/29 genuine imports; SHA `235201af7cb8393e9a8b8f9de438bbe23d98f10ae8e93c7f97350b6c74b30089`; controlled host PASS11 focused paths. Connected2033/2034 source graph now resolved except durationDSP332be4; wider dispatch/radio/ROM/data/layout frontier remains.

## Duration332be4 named DSP source selected

Complete native duration body selected as named ARC ISA inside C. Primary Synopsys ARC EM manual5755-101 establishes ASLACC operand signed low-byte shift and next-byte accumulator selector; register226 replacement retains limited/full accumulator-shift configuration and guard behavior. Standalone72B body matches native74B prefix outside three equivalent short-ASL encodings, and suffix exactly; no opcode payload. Receipt duration-332be4-source-receipt.json. Scheduler fixture extraction bounded before new body, PASS11. Target em-duration-dsp-round live; full component remains incomplete.

Duration target settled: compilation and relocatable link PASS; stable current source SHA c4ea92b592a0f074fd2dc2787753c450efcf187a552172e0719493f0ce51affb. Full source/hardware completion remains false.

## Packet event330400 source complete

Qualified single-packet uintptr_t ABI replaces old unqualified void declaration. Native full guards/type39, feature bits, allocation62/29, existing full projection330e78 and event-minus2 send retained. Actual C with controlled children PASS2048 all packet byte types/gates/failure; child results ignored as native. Target em-event330400-round live; expected877 definitions/27 genuine imports.

Event330400 coherent target settled PASS877 definitions/27 genuine imports/0 duplicates; stable current source SHA 866426868c94a73af3cc47f905a08f338f6cb24cee738895d1a35ec8b0b06b44. Full image completion false. Next3304f0 prepared from full native branch/writeback/delay-slot contract while build ran.

## Event3304f0 complete C selected

Full native type8 allocation14/4 and fallback packet ABI qualified. STB.AB stores payload0 before decrementing send pointer2; native delay-slot writes status at original event+3 before send. Controlled actual C PASS131072 for all type/status bytes, allocation failure, preserved header, fallback argument and full return. Target em-event3304f0-round live; expected878 definitions/26 genuine imports. Full generic fallback32f0a0 native audit retained for next pass.

Event3304f0 target settled PASS878 definitions/26 imports; stable source SHA 96660c54eaa433ab3f87a636c1446a4a1bbeeb3b2dfe9803af6cc107df6bebff. Full image completion false. Generic32f0a0 full native switch projection prepared for source admission.

## Generic event32f0a0 full C selected

All ten supported types5/6/7/9/10/16/18/46/47/48, native feature-byte gates (type18 intentionally lacks LE guard), allocation sizes/subtypes and exact projection stores reconstructed. Type5 address-kind2/3 remaps to1 and source+29; other kinds retained/source+10. Actual C and actual selected forward memcpy/address-copy PASS524288 all packet/kind bytes, gates/failure, expected projections and untouched bytes. Target em-event32f0a0-round live, expected879 definitions/25 imports. No hardware/runtime claim.

Generic event32f0a0 coherent target settled PASS879 definitions/25 imports/0 duplicates; stable source SHA f796bada7253f4d5daf485c4e6bd1f8755cc50a71cfc1bd1e5d50a5050487d1d. Connected3304f0 fallback is now source-owned. Full source/image/data/layout/runtime completion remains false.

## Command330664 parent source selected

Full native parent330664..330848 reconstructed with explicit ten deeper provider imports, native stack field layout and register-observed call ABIs. Unsupported slot2 returns0 without response; slot9 response allocation length2; all other completion responses length1. Native fresh opcode response gating/status mask499 retained. Controlled parent routing PASS262144 all16-bit opcodes/prehandler/allocation failures. Input mask/field branches and real-child graph need further qualification. Target em-command330664-round live; no full image or native runtime claim.

Command330664 additional controlled field/stack ABI PASS68096: all scan masks with256 input seeds, three-row cap and compact6-byte entries; create capability-bit precedence/status62 or17; input pointer/halfword/address/timeout fields. No source correction required; actual child graph remains open.

Command330664 target settled PASS880 definitions/34 genuine imports/0 duplicates; source SHA d0851d3d59d7a9d82a4b21c85d44463ed9669605dca8f394a068cf5bf02e0075. Real deeper child imports exposed by full parent; no image completion claim.

## Native address clear/query graph selected

Five full source providers303700/30370c/307cb8/30b12c/30c80c selected, closing two exposed command imports using actual selected stream gate. Controlled connected PASS196608 with all flag/state/query/capacity byte cases, latch/count/output effects. Target em-command-query-clear-round live; expected885 definitions/32 imports. No native runtime or complete-image proof.

Query/clear target settled PASS885 definitions/32 imports, stable source SHA 9c63989b3d2276ee7b55b49adb229de9cd7c82e710bd300e7a9de17375c1dfc1. Full completion false.

## Disable30c54c and timeout30c600 complete C selected

Native full-width input guards/order, actual stream/busy/readiness helpers and56-byte allocation/message callbacks preserved. Disable permits product state1; timeout rejects state1. Allocation failure returns0. Controlled connected host PASS1179649 with bounded stride-only normalization; message523/525 and current handler validated. Target em-command-disable-timeout-round live, expected887 definitions/30 imports. Full image/target runtime remains incomplete.

Disable/timeout coherent target settled PASS887 definitions/30 imports, stable source SHA 856201f686fb924fc950e2229747a5148ef35d786ade2785bfb545157d8751c5. Full image completion false.

## Address add30aed4 / contains3036b4 / append303674 complete C selected

Actual native bounds/gate/duplicate/capacity guards, captured count, full address comparisons, increment-before-row-writes and high-before-low stores retained. Pack-address actual selected64-bit helper preserves native pair. Byte count bounds make stride12 exact ordinary C. Connected controlled host PASS131088. Target em-command-address-add-round live; expected890 definitions/29 genuine imports. No complete-image/runtime claim.

Address-add coherent target settled PASS890 definitions/29 imports; stable source SHA edfe7d52068826ce5e58791821a575920a810e4ddc05dde2d54167595f1bc2e1. No complete-image/runtime claim.

## Address remove303718 and command30ca1c complete C selected

Native captured base/count and full-word comparison order retained. Last-row swap copies halfword tags before reading/storing address words; destination trailing2 bytes and old tail remain unchanged. Count decrement occurs after stores. Connected host PASS98440 count/match/miss/argument/gate fixtures with full buffer checks. Target em-command-address-remove-round live; expected892 definitions/28 imports.

Address removal target settled PASS892 definitions/28 imports; stable source SHA 72e07dfa20371dc45f959c00f7dfd6b3732b64bc76a133ef88b1811f05178b40. Full prehandler330bdc plus pair-set30c580 and info303270/3032a8 providers prepared separately, not yet selected; native fresh-opcode behavior and52/36-byte payloads audited. Pair apply307fa0 deeper body remains.

## Prehandler330bdc / pair30c580 / information303270,3032a8 complete C selected

Four source-owned providers close prehandler import and expose genuine apply307fa0 child. Native53-byte FFDB /1-byte FFB3 allocation, post-status fresh command,36/52-byte copy contracts retained. Connected controlled host PASS1179656 using actual selected copy/fill/gate/readiness/busy bodies; only bounded stride normalized. Target em-command-prehandle-round live; expected896 definitions/28 imports. Full completion false.

Prehandler coherent target settled PASS896 definitions/28 imports; stable source SHA aa7836eec8752fc3f151e55bff1522b2f9ba7e9adbc4f24bec1667f382d80fae. Native decoder gap307fbe resolved from pinned opcode mask as MPYWHUL r13,r2,r1; named assembly exact321e004d. Synopsys ARC EM manual5755-101 page1523 defines unsigned32×low16→low32 and wide accumulator effects.

## Pair apply307fa0 full C/DSP selected

Original factor read, halfword write, genuine named MPYWHUL wide-accumulator effect, product write and id guards retained. Host PASS125531 arithmetic-normalized cases; target em-command-pair-apply-round live, expected897 definitions/27 imports. Full image/ISA runtime not proved.

Pair apply target settled PASS897 definitions/27 imports; stable source SHA cdee607c67eeb558be71a03a58ea93241f92ff6d905cf9f33403bef2afb5282c. No complete-image/runtime claim.

## Scan parameter30b9f4 full C/DSP selected

Native initial mirror/clear before gate, full-width guards, genuine MPYUW low16 products, message16 fields and callback returns retained. Connected controlled host PASS6912 with boundary/truncation checks. Real availability307b9c and error30e7f8 imported; target em-command-scan-params-round live, expected898 definitions/28 imports because one parent closure exposes two deeper children. Full completion false.

Scan-parent target settled PASS898 definitions/28 imports; stable source SHA 7e35a8f56996889ce99e3bce8991fbfaeb0d32c95040b635ef8044ce90a03c3a. Two exposed children now fully reconstructed.

## Availability307b9c and error30e7f8 complete C selected

Three authenticated literal table entries retained as typed source state-address array; mask reload after successful child validates native mutation order. Error first-latch/byte countdown/5 initialized event bytes and exact callback return retained. Connected actual source host PASS921600. Target em-scan-availability-error-round live; expected900 definitions/26 imports. Full component/image/runtime still incomplete.

Availability/error target settled PASS900 definitions/26 imports/0 duplicates; stable SHA ede03aa4144eebd3c0ef59a5672bbd4bba1ac11c8cdd8dd44e37c56414d66759. Full completion false.

## Create30c488, idle307ca8 and count3213b0 complete C selected

Full native create guards, fresh address and handler reads, packed pair, modulo-byte row count and 24-byte message fields retained. Actual C host PASS66832 with controlled duplicate/allocation/send; all 65536 timing values covered. Target em-command-create-round pending, expected903 definitions/26 imports (duplicate child exposed). Full image and runtime completion remain false.

Create graph target settled PASS903 definitions/26 imports/0 duplicates; stable SHA 2bf03981151428c065bbe2d18e066a1517b1e0ff2578e82162ba70bb3cbd4790. Duplicate307c5c six active row guard/full address graph now selected, connected bounded host PASS132800. Target em-command-duplicate-round pending expected904/25. Full completion remains false.

Duplicate target settled PASS904 definitions/25 imports/0 duplicates; stable SHA faca7552e6c1c6a2dab4dfcf0b607601f9b410b128bebeb0b407db083dd6b9be. Full extended scan parent30d774 and four native children prepared separately; capability guard/row projection qualification in progress.

## Extended scan30d774 and four native helpers selected

Full capability and argument guard order, compact6-byte rows, bit-mask writes, configuration field order and count projection retained. Genuine MPYUW source preserves accumulator effects. Controlled host PASS589824 checks actual graph and full RAM effects, bounded multiplication normalized. Target em-command-scan-extended-round pending expected909 definitions/24 imports. Full component/runtime false.

Scan-row predicate carry/unsigned-lower interpretation independently confirmed by pinned arc-flag.def: CARRY and LOWER both encode condition5. Next full dispatcher330848 native range330848..330bdc saved; fragmented type23 projection, native multiplier/DSP and fresh product capacity must be preserved. No dispatcher source admitted yet.

Extended scan target settled PASS909 definitions/24 imports/0 duplicates, stable SHA 9cfa49a0a92ae267ca4ec50196bb9326e9b838181165c9607abad18346331a48. Full dispatcher330848 and allocator32e470 prepared separately; source qualification pending before admission.

## Dispatcher330848 and allocator32e470 full C selected

Full seven native event families23/24/25/30/31/32/38 reconstructed, including native byte-wrapped ceiling counts, fresh capacity checks, chunked229/247B projection, source truncation writes and exact return. MPYW signed low16 multiply retained as named native assembly. Controlled host PASS8660 checks full output and untouched bytes; no hardware proof. Target em-dispatch330848-round pending expected911 definitions/23 imports.

Dispatcher330848 coherent target settled PASS911 definitions/23 imports/0 duplicates; stable SHA 77992ff68a7bddc8a26f6ac8adfa8c4221ed34d2163e5c66a7468c62da1861e7. Full configuration dispatcher3300c8..330400 separately prepared from native, not selected until opcode/captured-field/stack-layout/fresh-response qualification. Native basic pointer+24 vs extended pointer+20 preserved; three deeper configuration children plus clear child genuinely imported in prepared source.

## Configuration3300c8 full C selected

Four opcodes, basic10B/extended14B rows, pointer offsets24/20, clipped2-row capture, full count, byte252 completion and fresh response opcode retained. Controlled host PASS132096. First integration assertion found differently worded existing declaration; premature unchanged-source build explicitly stopped exit130 before admission. Target em-dispatch3300c8-admitted-round pending expected912/26, genuine deeper children remain. Full completion false.

Configuration parent coherent build settled PASS912 definitions/26 imports/0 duplicates; stable SHA 458a3d921745bdf008ea85a5e30fda24de71b6c475cf3869b47534ec5d3581ba. Pair-validation30b3f8 full C selected, controlled host PASS51200. Real306b80 apply child exposed; target em-config-pairs-round pending expected913/26. No complete-image proof.

Pair-validation target settled PASS913 definitions/26 imports, stable SHA 9bd23fe1a5e4dfd5e47f710ff5f29e5fb1c6be46e90b353fe751352584bd2a51. Full native306b80 apply source selected using existing channel/link/state providers; controlled host PASS1048576. Native first-row mutation survives later error; zero-row stale halfword message retained. Target em-config-pairs-apply-round pending expected914/25. Full completion false.

Pair apply settled PASS914 definitions/25 imports, stable SHA 391b7be6b02f881733c5534b1947f9c1fdd0547ad4cb0298731bc14f1554e5eb. Configurationclear3083a4/30ca18 full C selected: full guard/release flow and native MPYWHL656 source exactly309c040a, host PASS32768. Three authentic clear/busy children exposed; target em-config-clear-round pending expected915/27. No full image completion.

Clear parent target settled PASS915 definitions/27 imports, stable SHA 360ffad0ab93105848621ad3e662c80b693150a67913a5304740f93e5c259b9c. Three native clear/busy leaves selected, host PASS768; target em-config-clear-children-round pending expected918/24. Complete basic configuration30d00c prepared separately with two real deeper children, awaiting guard/clamp/live-state qualification. Full completion false.

Clear helper target settled PASS918 definitions/24 imports, stable SHA bb129bca6bb3f78e1af82defa9035b52c913139d3a2e6d67e4ea066afbb54ddc. Basic configuration30d00c full C selected afterhost PASS329522; actualPHY capability helper332f80 selected PASS262144. Native timing5..4000, one-field clamp precedence and live count semantics retained. Genuine apply3087ec child now imported; target em-config-basic-round pending expected920/24. Full completion false.

Basic configuration target settled PASS920 definitions/24 imports/0 duplicates; stable SHA b29cc1e1a7cbf65be2f9bca4f78554cd28121a7edf3270365288737a8c6c19a8. Full native apply3087ec..308a3c prepared separately; allocator/find/update/count provider imports explicit, existing/new paths and repeated decrement passes need fixture/native-call ABI qualification before selection.

## Basic apply3087ec full C selected

Whole native3087ec..308a3c existing/new link setup, clamp, signed/unsigned capacity checks, repeated decrement/update passes and final readiness retained. Controlled host PASS262154; fixture lookup publication corrected after stub failure, source unchanged. Seven authentic child providers exposed; target em-config-basic-apply-round pending expected921/30. Full completion false.

Three basic-apply children31abc0/31b278/31b2a8 prepared separately and connected host PASS788480: native captured data, byte-sized count and full-width equality retained. Not selected during live em-config-basic-apply-round build.

Basic apply target settled PASS921 definitions/30 imports, stable SHA ad2b6aff7489243fadd8289b7ac2d46ad4664c9bb35aece1a6a3492d9331e0a8. Three lookup/count children selected afterconnectedhost PASS788480; target em-config-link-counts-round pending expected924/27. Full completion false.

Full channel316b5c and link316bbc allocators prepared separately; actual C initializer projections hostPASS4096. Genuine named MPYWHL140/656 retains accumulator effects, host bounded stride normalized. Existing source-owned fill/count/request used in target; no selected edits during lookup/count build.

Lookup/count target settled PASS924 definitions/27 imports, stable SHA 837538f5e92352f192adbdbad90c0a9d6f525b709b1c7d4dabcb008f798d4784. Both native allocators selected afterhostPASS4096; target em-config-allocators-round pending expected926/25. Full completion false.

## Extended configuration validator round

Full native 30d204..30d35a reduced to C; output clear precedes rejection, initial status48, PHY failure17, enabled zero-length failure18, full apply return retained. Native MPY14 preserved. Controlled host boundary oracle PASS393474. Apply308a3c remains a genuine provider import. Prior allocator build settled926 definitions/25 imports, source SHA1fd4657f4ede50d28c16616d73d53b1a3089e720a84b1057ac660a798a2d36d8.

## Full extended apply and existing count

Native308a3c..308b14 and31b2d0..31b2f8 now C providers. Captured count/read sequencing, native ignored clear return, signed existing capacity comparison versus unsigned new capacity, fresh row pointer and live count loops, link state clear before update, halfword output and final channel count retained. Controlled actual-C host PASS196614. Genuine update3272d8 and326d0c remain imports; target build pending. Extended validator prior target settled927/25 stable SHA3a3eb2e3250503d4a43111c6fa7755aaf5ffb827ecaec28591e9f612b0ff05b6.

## Update timing and attachment helpers

3185e8 full two-PHY duration formula and318670 complete two-slot attachment now source-defined. Preserves independently live feature-byte reads, unsigned wrap and final config overhead load; attachment second-slot gate and untouched projection. Actual C/native instruction-reduction host PASS917568. Extended apply build settled929/26/zero duplicate, coherent SHA91c26fd0774a7382508f953aaf9ec18299d199e657bf1d9f14e30820d591d1bc. Full update functions remain open.

## Full basic timing sum

Native3185a8..3185e8 sum now C with captured count/input-ID/row base and native byte-load order. Connected actual timing-provider host PASS32768 across count0..255 and128 patterns including callback count/pointer mutations. Update helpers target settled931/26 coherent; full extended channel326d0c prepared but unselected pending exact native projection qualification. Two MPYWHL register opcodes exactly reproduced by pinned assembler (update-mpywhl.s).

## Complete extended channel update

326d0c..326ed8 reduced fully to C: native attachment, per-link/summed time fields, mode1 prefix subtraction and other-mode suffix accumulation, channel interval/baseline/mode/readiness. Two native delay-slot store/read order corrections applied before selection. Actual-C controlled projection hostPASS69632. Native MPYWHL retained in target source, signed32xsigned16 low32 normalization only host. Readiness3186a0 remains genuine import; target pending. Sum target settled932/26 coherent.

## Full channel readiness

3186a0..318708 now C using existing auxiliary guard provider. Captured policy overhead and signed pointer quotient/low8 index; live preceding active channel guard reads counted twice per active row exactly as native; final unsigned interval1250-overhead versus guard+baseline. Named MPYUW kept in target. Actual-C hostPASS3145728 (all16bit interval boundaries plus indices/active patterns/overflow baselines). Extended-channel target settled933/26 coherent; readiness target pending.

## Full basic limit helper

Native31855c..3185a8 now C; selector chooses input16/18 and link492/496, unsigned wrapped budget/baseline/time, native MPYUW1000/1250, DIVU and lowbyte result retained. Manual DIVU pages1377-1378 establish zero divisor leaves destination unchanged when DZ=0, or hardware exception DZ=1. Corrected asm destination initialized1 and +r (not uninitialized =r) before selection. Controlled hostPASS7077888, DZ0 zero case only. Readiness target settled934/25 coherent; basiclimit target pending.

## Basic rounding provider qualified for admission

Full317efc..317f2c prepared/hostPASS16777559 (all256^3 byte triples and343 fullwidth combinations). Exact30dc0081 is MPYWHL.EQ r0,r0,r2, not unconditional product. Corrected native condition propagation/skip on raw-divisor256 before admission. Named ISA products retained, bytewrapped divisor guaranteed1..255. Await prior basiclimit target completion before selected edit.

## Full basic channel update

326b00..326d0c full C now selected after hostPASS16384, complete channel/link projections with actual timing/sum/attachment/rounding providers and controlled limit/readiness. Native two-slot MACWHL retained; exact341d1083 assembled. Native4700/40e0 reproduces firstlimit byte return passed assecond31855c pointer. Preserved exactly, NOT repaired to same-link; real low-memory mapping/call-ABI qualification remains explicit open gate. Host boundedcases check pointer throughcontrolledlimit only. Target pending. Rounding target settled936/26 coherent.

Integration follow-up identified provider name/signature mismatch in firstbasicchannel admission: caller contract isuint32 opencfw_em9305_config_channel_update_326b00, while initial prepared body wasvoid/basic_channel_update. Corrected prepared source retains nativefullR0 readinessreturn; selectedsource must remain frozen duringlive96910 build, thenrename/requalify and rebuild. Rounding also exposes compiler__udivsi3 fromplainCdivision; substitute existing authentic namedDIVU helper aftercurrentbuild settles. Neither remaining import is declaredclosed yet.

## Basic channel integration correction

Initial target settled937/26 but caller remained unbound due alternate basic_channel_update name. Corrected selected body tocaller contractuint32 opencfw_em9305_config_channel_update_326b00 andnativefullreadinessR0 return; corrected roundingplainCdivision toexisting authentic namedDIVU helper (denominatorprovednonzero). Requalified hostsPASS16384 including return0x123 and16777559. Fresh target pending; do notuseinitialreceiptasboundproviderproof.

## Full extended link update

3272d8..32739c full C selected after hostPASS131072 (allPHYbytepairs andpostseed slot/base/row mutation; entire656B projection). Source-owned33449d table exact7B02010301010104 frompinnednativeblob. Existing PHY projection andaccessseed providers reused; typed data records andMPYUW912 preserved. Corrected basicchannel target settled937/24 coherent, nativecallerbound and__udivsi3 bothverifiedclosed. Extendedlink target pending.

## Remaining basic link native audit

Recovered complete326ed8..3272d8 native routine; priorfull-listing truncated327238 despitecontinuationtargets. SixDSPoperands byte-proved inbasic-link-products.s. IntervalusesMPYDU plusASLACC lowbyte225(-31), configurationfull/limitedshift retained. Pinnedassembler rejects directpositiveASLACC225 immediate; useauthenticregisteroperand loaded225 inpreparedhelper, notrawopcodes orplainCdivision. No fullbasiclinkprovider admittedyet.

## Basic link native ISA slice

326f2a..326f4c wide interval slice extracted to C-hosted namedASM provider; originalMPYDU/ASLACC(-31 selectorbyte225)/MPYWHUL/carryround retained, registeroperand225 replacesunsupportedpositive-immediate spelling only. GenericMPYWHUL andDIVU-with-explicit-prior wrappers support remainingwholebody; no fabricatedzero-divisorreturn. This is a slice provider, not full326ed8 closure or intervalplainCmath/hardware qualification. Target compile next.

## Full basic link prepared reduction

Complete326ed8..3272d8 body now prepared (config-basic-link-prepared.c), unselected/unverified. Keeps mode-dependent length projection, fresh config caps, duplicated quotient reevaluation, byte limits, distinct signed/unsigned ceil products, MAX versusMIN rounding, additional flagged sizing. Register-prior states on zerodivisor andconfig mutation loadorder stillrequire line-by-lineaudit; do nottreatpreparedbodyasqualifiedprovider.

## Full basic link C candidate

Complete326ed8..3272d8 candidate selected after hostPASS196608 complete656B projection, mode0/1/2 andallbyte lengthpairs. Testreferenceinitialoverflow-sensitiveceil corrected (failed0/85/mode1) toquotient+remainder, no sourcechangefor that failure. FirstlargeDIVpriorstates audited/corrected inpreparedsource. Source retains namedISA andDIVUwithexplicitprior; remainingzero-divisor ambient childregister inheritance andlimited/GE accumulator policy NOTqualified. Bounded fullshift/nonzerodivisor fixture is not wholeentry/hardware proof. Candidate/source_complete remainfalse. Target next.

## Basic link build and connected command reduction

The initial basic-link build failed on a stale uint32_t declaration against the selected void provider. Corrected the declaration; em-config-basic-link-abi-round passed with 940 definitions, 22 genuine imports and zero duplicate strong symbols, stable controller source SHA d553ca9c5ac093f151a9ba6b6c0d8fd8b28ac1bbba2177d09c9f1da8e16321fe. Added instruction-derived native R3 tracking from the 30c40c tail into 30c3a4 for the second flagged DIVU destination-preservation path; this removes the earlier small_q guess. This path remains source-inferred, not native ARC runtime tested; accumulator configuration and low-memory basic-channel child pointer gates remain open.

Complete dispatcher32e4c4 selected after 6656 bounded host cases. Its first target attempt failed on branch-target alignment in the named stack-check wrapper; explicit 4-byte wrapper/branch-target alignment corrected before the next build. Complete children30dc48/332abc/30b974 selected after 679936 bounded host cases covering gate/ID/count ordering, all packed-control masks, sparse destination writes and child-call sequencing. Real selected control decoder is reused; child oracle uses controlled providers. Genuine descendants3096a8 and306cec remain imports. em-command-structure-children-round is pending; these additions are not yet target-qualified. No full image complete.

Command structure round settled 945 definitions/23 genuine imports/zero duplicates, stable SHA 7b5ca6e5b98bf0b82b7e1af3e2840d6ed1a452433c9e1619d81e9de9b95bdcd0. Complete selected dispatcher plus three children target compiled; hostPASS6656/679936 remains bounded contract evidence. Full single-stream commit306cec selected after hostPASS4096 including full sparse96B target/20B event projections and callback-induced pointer/header refreshes. Next em-command-struct-commit-round build pending. Full components0/6, goal active. Remaining records commit3096a8 is a substantial native body with per-record checks, timing budget, free-slot masks, partial writes and callbacks; not a trivial wrapper.

Single-stream commit306cec target settled946definitions/22imports/zero duplicate, stable SHA09c5fe05985fc2adec1347c3b393112ffd45de28834e702c955e0a889c7d169c. Full records commit3096a8 now selected after host61440cases covering all IDbytes/count1..15 and16success/failure scenarios, entire4096B slot state and2824B record projection including partial first-slot allocation on exhausted mask. Host fixture initially rejected timing case before budget due maxretry0; corrected fixture row retry0, source unchanged. Full CRC304678 selected with exact authenticated1024B table334550, all256entries independently match reflected polynomial0xedb88320; host262401cases inclstandard123456789 vector. Callback/current-base refresh fidelity and active hardware state still need native qualification. em-command-records-commit-round target next. Fullcomponents0/6, goal active.

Correction: records-commit host did NOT pass at admission; second fixture result was61440cases/3600failures because budget100-150 wraps unsigned and succeeds, while fixture expected69. Source retains native unsigned subtraction. Set fixture budget150 to test insufficiency; currenttarget47896 source heldstable, qualification pending revisedhost. Prior61440PASS claim superseded.

Revised records-commit fixture terminalPASS61440cases/0failures; receipt updated to actual verified result and hostSHA. Source unchanged across fixture corrections. Native unsigned-budget underflow preserved. Target em-command-records-commit-round stilllive47896. Mainsettled2045/785; CodecA real fenv/packed relocation build live; CodecB active-native trace continues. Fullcomponents0/6.

Records commit andCRC target settled948definitions/21 genuineimports/zeroduplicates, stable controller SHA4c1c6624665ce0763bc735e834ccaa931667c1196ba2501b5299ddef1e1e0767. Full advertising/vendor dispatch331dc0 and331f00 selected after hostPASS524288 coveringall65536opcodes/allocationfailures/freshrequestmutation/sparseresponses/parameterprojection. Seven genuine commandchildren remain newimports; target em-advertising-dispatch-round next. CodecA realFPproviders close2semanticimports; ambientKWSstate remains, targetruntimehelpers/packedsize/relocations/layout unqualified. Main2045/785. Fullcomponents0/6, goal active; EM21prior mixedinterfaces plus new advertising descendants remain substantial.

Advertising/vendor dispatch target settled950/27, stableSHA1279f7e4349b1f87398d0e6e5324411f41cf613cc495db3c91fb463e70f0eabb. Five full children30cee4/303258/30cdd8/30df98/30bb50 selected afterhostPASS262400; authenticgate andcritical providers reused, lowernotify306a7c/power310230 remain genuineimports. Versionreads liveRAM8013d0; this is sourcebody closure, not product-data ownership. Nexttargetem-advertising-data-children-round. Fullcomponents0/6. CodecB authenticatedCRTcopy fixesactiveQEMUfixture, threefullactivecalls match observed outputs butvariednumericalqualification remains.

Advertisingdata target settled955definitions/24 genuineimports/zeroduplicates, stableSHA9331ca0cb6761aa063d9c01f1629d775481dc1b22eb13c69f7dd9e0e33eae688. Complete parameters30ce18 selected afterhostPASS61928 (capturedcapability mutation, mode/address/channel/filter validation, interval boundaries, full24B sparseprojection). Complete power310230 selected afterhostPASS100663296 signed requested/upper/lower caps with6measured query values, using existing311a00provider. Targetem-advertising-parameters-power-round next. Livecaps8012b8/b9 andadvertisingRAM remain product-initialization gates; sourcebodies not fullhardware qualification. Main2052/784 settled; CodecB corrected sine/cosine semantics withfour anglewholecall andthreeactiveprocessnative/C passes. Fullcomponents0/6, goalactive.

Parameters/power target settled957/22 withzeroduplicates/stableSHAac0a6cdf2e249062034d77d8540e5d098f3a7b19c0029d1b9e473627d46a205d. Full enable30aff8, notify306a7c/3082dc anderror30e758 selected afterhostPASS196608, existing30e79ceventcallback and31445cidentityprovider reused. Sourcefullcapturedgate/enable/mode/capacity/failurepaths; sparse24B/4Bevents retained. Targetem-advertising-enable-notify-round next. Remaining EMfrontier includes otherfull dispatcher3324e0, primary/initialize/radiopacket/table/schedule/ROM interfaces andliveproduct initialization. Main2052/784; CodecB sixangle/threeactiveprocess matches withnumerical/createcoverage ongoing; CodecA combinedfenv/shift build explicitlycoordinatesBfreeze. Fullcomponents0/6, goalactive.

Enable/notify target settled961/20, stableSHAaf5bc151bb0c61062c80670bf5aa864020ab93e47b679b7ae1c6bb0af4123d39, zeroduplicates. Complete radio scheduler314370..3143f4 selected afterhostPASS373248, existing303f80/303f8c/MPYUW providers reused; capturedparent/now andnative delay-slot initial+incomingguard beforeguardcall preserved, accumulatorfreshload onelapsedshortage retained. Targetem-radio-schedule314370-round next. Full3324e0..3327f4 dispatcher listingrecovered, packedrecord/response reduction remains. Fullcomponents0/6; CodecA233input combinedshift/fenvbuild liveunderBfreeze; MainLV descendants ongoing; CodecB variednonzero/createoracle fixtures ongoing.

## Full packet dispatcher prepared

Recovered native3324e0..3327f4 fullspan. Complete C candidate dispatch3324e0-prepared.c preserves twelve2035..2040commands plus207f, prefix3328c8, variable packed-row projection, branch-specific scratch zeroing, outputstatus writes and fresh response opcode, power/count/size queries. Fifteen lower native children declared genuinely. Candidate is prepared only: bounded ABI/oracle validation andtargetqualification are still pending. Do notclaim source/provider closure from this file.

Radio314370 target settled962/19 genuineimports/zeroduplicates, stablecontrollerSHA08bc43bae19137936fd0f5ec4feda0f6630cb845f9a6f76d7ad1977b1678501e. Complete packetdispatcher3324e0 fullbodypreparednotadmitted/qualified;15lowerchildrenneedcontractproof/oracles. Unknownnative312344instruction382f000e stillhasno matchingpinnedARC opcode pattern, so genuineproviderretained; no guessed arithmetic substitution. Fullcomponents0/6, threeworkersactive, goalactive. Remainingestimate: EM19mixedinterfaces after scheduler pluspacketdispatchchildfrontier, CodecambientKWS/packedlink/layout, CodecBfullnumerical/create qualification and9interfaces, MaindeepLVrender/layout/TLSF/productstate; Touch430unownedresetbytes/9interfaces, CASEfinalformatter/startup/layout/runtimegates unchanged.

Complete packetdispatcher3324e0..3327f4 selected afterhostPASS1576192, fullcommands/prefix/allocation/opcodemutation/packedfields/response projection contracts. Fifteen realchildimports exposed; nofake closures. Targetem-packet-dispatch-round next, targetnotyetqualified. Priorradio target962/19 remainslastcoherent untilnewbuild. Main2062/780 settledwithtransition/list/layoutproviders, nextdeeperevents/render/TLSF genuine. CodecB positivecreatewholecall andvariedactive traces matchbutfinalzerooutputdoesnotqualify nonzero numerical behavior; nativefailureloggertransport unavailable. Fullcomponents0/6, goalactive.

## Packet dispatcher target closure and vendor prefix
Dispatcher3324e0 target receipt: 963 definitions,33 genuine imports,zero duplicates; stable selected SHA b37509ff9daea5359eab71f0168b2dda17410604caea27427efa9ed26f76d939. Vendor prefix3328c8 plus statistics30be3c and snapshot303264 admitted after PASS917504 bounded host cases. Three vendor children remain genuine imports; live RAM ownership remains open. ARC target qualification pending. Full EM9305 component incomplete.

Vendor mask30cf28,mode30d5a8,option30d75c full tail bodies prepared from native308780/308c44/308f28; bounded host PASS2359296. Not admitted during current ARC build. Native mode byte-wrap and option low-byte OR rules retained. No new dependency required.

Vendor prefix target PASS: 966 definitions/35 genuine imports; stable selected SHA 67878fbd72beb1c9d8856a109834f39d96fe4b9b72474e3104ad7060e05324be. Vendor-control bodies now admitted, next target run pending.

Vendor-control target PASS: 969 definitions/32 imports,zero duplicates,stable SHA 7a4bf1312fbb67cf502d0d725acf890afbf3a9850ea1c29d747400debcc2a5d4. Three packet query bodies admitted after bounded host PASS262656, next target qualification pending.

Packet queries target PASS 972/29,zero duplicates,stable SHA 6f59b2994ccbcdc0a9841dca51378969ca8c3efa6418c3575f3be5a938c9eafe. Clear single/all and native release31ac54 admitted after PASS2194 bounded host scenarios; target qualification pending. Callback ownership and actual live pool bounds remain product gates.

Clear target round PASS: 975 definitions/27 imports,zero duplicates,stable SHA 98a5d8be19e1aa14c668c47061d8f6f50dbf306f4e8bff1a9dae7d1b7a812356. Address-field30cee0 admitted after PASS524288 host cases; target run pending. Full component remains incomplete; no inferred zero providers.

Address-field target round settled PASS: 976 definitions/26 genuine imports,zero duplicates; stable selected SHA c6f59843d9934d2f3011ec87fea34be1589064fe73a9db6e30a3bcfe9f623070. Completed bounded packet-address chunk. Full source_complete remains false. Next native command frontier: packet/extended packet, data/response, periodic data/enable, intervals and enable rows; all genuine providers retained.

Intervals command30db34 and full lower3092f8 admitted after bounded host PASS786432; preserves duration callback, freshly reloaded max interval and flags, full saved record stores. Native packet timing dependency already owned, no new imports. Target qualification pending.

Intervals target settled PASS: 978 definitions/25 imports,zero duplicates,stable SHA 13d4f4f6494e715ca52293aeebd2384bcfa6f1fe9877c26843181bcdd4238d91. Periodic enable30daf8 plus full309244/status30e878 admitted after PASS12288 bounded host; return type void reflects native command with ignored R0, preserving actual status callback and both sparse events. Target qualification pending.

Periodic-enable target PASS: 981 definitions/24 genuine imports,zero duplicates; stableSHA 4df028df4eb9ef4d509368251db86c2198ce5a8a50b94e2ed9eaf3ddc0f1a989. Full periodic-data30904c/30dac8 admitted after PASS20480 bounded host scenarios; native partial reset, alternative/static packet and source CRC preserved. Target qualification pending; arbitrary malformed/alias inputs and hardware remain unqualified.

Periodic-data target settled PASS: 983 definitions/23 genuine imports,zero duplicates,stable selected SHA f1ff0abca8acbff237b20403910eace26e29d8ea8b0ff3e99ab196ba426e1477. Full payload state-machine bounded chunk completed. Remaining imports include five command/provider bodies plus primary/dispatch/radio initialization, live table, unknown ISA and ROM interfaces. Full component incomplete.

Packet configuration lower308c70 plus basic30d5ac/extended30d678 admitted after host validation PASS1310722 and bounded full-record/payload lowerPASS280. Native rawDSP words321c208d/319c0c49/329c0c49 map pinned MPYWHL opcode301c/309c and use existing authentic named ISA helper; no invented arithmetic provider. Live product buffer tables remain state-ownership gates. Target qualification pending.

Initial packet-config ARC compile failed solely Werror misleading-indentation on projection declaration following early return; source snapshot stable. Split declaration onto separate line, no contract change or warning suppression. Corrected target rerun pending.

Corrected packet-config target settled PASS: 986 definitions/21 genuine imports,zero duplicates,stable selected SHA eb455a226aad4996c5bf9d1a6d537be622f6b7f56b72b51e52da8409ad42af1d. Basic/extended config bounded chunk completed; product buffer tables and final image gates remain open. Shared payload32739c prepared, hostPASS15360 (including scheduler notify paths), outer data/response and legacy helpers still undergoing qualification before admission.

Data30d580/response30d854 plus complete payload32739c,legacy327510,notify306c8c/3082b0 and head predicate3132f8 admitted: hostPASS15360 payload/PASS147456 wrappers/PASS75266 helpers. Native notify saves original fullword input through lookup; callers pass saved record pointer, preserved exactly without semantic repair. Distinct native legacy payloadoffset22 vs modernalt24 retained. Target qualification pending.

Data/response target round settled PASS: 993 definitions/19 genuine imports,zero duplicates,stable SHA 9f1db0af8ac5bafd7a00ba63c68f9a127805809486d8a964d8237b64742337c3. Seven bounded packet-data providers completed. Remaining command enable_rows30b6cc now has full native continuation and three child contracts captured for next reduction. Full EM image source/layout/hardware remains false.

## Enable-row round

Five full enable-row C routines admitted and target compilation PASS, selected source snapshot stable. Host projections PASS 1,442,241 helper checks and 1,800 controlled-contract outer fixtures. Native collect-all caller two-ID storage contract remains unowned. Full component remains incomplete. Receipt: `g2/build/c-firmware/20261011/em-enable-rows-round/receipt.json`. Dispatcher initializer is prepared only.

## Dispatcher initializer admitted

Native331ac0..331aea translated in full, including 28-byte tail clear, ordered mask stores and native R0=0x1fff return. Host projection PASS 256 sparse-boundary fixtures. Target receipt `g2/build/c-firmware/20261011/em-dispatch-init-round/receipt.json` PASS 999 definitions / 17 genuine imports / zero duplicate strong symbols; source SHA fbdeafa480d593e179bafebf08cca6fbf6163e1b41aa99d7e34ad316d49630e3 stable and verified against current file. Primary command and radio initialization native frontiers recovered; primary candidate is prepared, not yet admitted. Full component remains incomplete.

## Primary command handler admitted

Complete native32e5d4..32e914 C dispatch body, all command cases, signed halfword projections and sparse stock command structures. Controlled host PASS 196,868 routing/argument/projection fixtures. Pinned ARC manual page308 establishes C=unsigned-lower; command0c84 status preserved exactly (values1..16->17, zero or>=17->0). Target `em-primary-round/receipt.json` PASS 1,000 definitions / 28 genuine imports / zero duplicates, stable SHA75618543d8a0c33aa2b3b66d39ea3696ffef96ab410cff967a20233a38cd8f3e. Import increase exposes actual private/vendor/response/control native bodies. Four address/mask children now admitted and target build89157 live, source frozen. Their host projections PASS 8,388,865 cases with existing real address providers. Full component remains incomplete.

## Primary descendants rounds

Address/mask round PASS 1,004 definitions /24 genuine imports /0 duplicates, stable SHA168608998977c87bc77d570da95649311f1b198e61ee26da8be431fc06d3333b. Four native bodies complete; existing authentic address providers used. Control round includes three commands and direct pair-store provider; 73,984 controlled command fixtures PASS. Coherent target receipt `em-primary-control-round/receipt.json` stable and verified. Two timer bodies and exact eight-word threshold/quantum tables now admitted; host PASS71,680. Timer target build pending. Full component gates remain.

Timer round settled: target PASS 1010 definitions /21 genuine imports /zero duplicate strong symbols. Stable source SHA4b237124075c64fcac92d3cfbb24ed1d2174be37e54440f37394875d74778085. Receipt `g2/build/c-firmware/20261011/em-primary-timer-round/receipt.json`. Completed timer selector333bec/value313744 and authenticated source-owned eight-word tables; host71,680 fixtures PASS. Full component remains incomplete; next primary response/private/vendor and radio initialization bodies, ROM/data/ISA/layout/hardware gates remain.

## Response and query closure

Response target PASS1,011 definitions/28 genuine imports/zero duplicates, stable SHA6bafb272c53a6bb262750840d921bd242e6e773cf11d9315f8bd7ebb6a913f7d. Nine full query/lower bodies then target PASS1,020/20/zero duplicates, stable SHAf2e56b04324f84c858358a87f9ea051324ea5b0ff3ed038741d56d4568dcd8e8. Host393,217 response and524,291 query fixtures PASS including config-pointer reload/output alias cases. Private command/provider chain admitted next after132,352 host fixtures; target pending. Full component remains incomplete.

Private round settled: PASS 1030 definitions /19 genuine imports /zero duplicates. Stable verified SHA2ef9a4669e9331c9d338804cd428bb1a860962a64d6dbbdc2d22b6e6b73cc90f. Receipt `g2/build/c-firmware/20261011/em-primary-private-round/receipt.json`. Complete private four-opcode router plus ten connected source functions (four counter getters, reset, mode/data/stat/reset providers and shared field helper); 132,352 controlled host cases. Full source/image completion remains false.

## Vendor dispatcher round

Complete native32eb34..32eec6 and15 genuine native leaves selected. Target receipt `em-primary-vendor-round/receipt.json` PASS1046 definitions/25 genuine imports/0 duplicates; stable source SHA f3a92b81a257218dd3620a23192fb2116923d6da5cd60fd63c4d27bc97c3e94a. Host262145 projections cover allopcodes, allocation failure/success, bothFFF3formats, freshopcode mutation and sparsepacketbytes. Seven additional native command/provider bodies prepared and host590080 projections PASS, target compile in progress. Fullcomponent incomplete; ROM,remaining code/data,layout/startup andhardwaregates remain.

### Vendor command providers settled

Seven authentic native provider bodies target PASS1053 definitions/19 genuine imports/zero duplicates, stable SHA15d37b0c15d3e6185640faf109bbe9a288e9f10eab6cfa538787697cf15ad37b. The new ROMcapacity1030e8 remains external; no guessed provider. Fulladdresscommand30de38, reset310718 andtwo busy leaves prepared/admitted after host69634 projections; next target build pending.

### Address command settled; radio init expansion

Fulladdresscommand30de38/reset310718/two busy leaves target PASS1057/17/0, coherent SHA d173efd32ba587ad31ea427f371b05e6079824024eb2e73a23e927dd243f2202. Fullradioinitializer30c150 and20 complete forwarding entries admitted after256 call-chainprojections; genuine deeperinitializers/callback/finalstate are explicitimports. Targetbuild pending; no componentcompletion claim.

### Radio initializer chain settled

Target PASS1078definitions/48genuineimports/zeroduplicates, stableSHA6c9712d54f88da2edacb8f51bb0df2622619663007f04ff2cdbe24ca78022a3a. Fullnativeinitializer30c150 and20forwardingentries complete; deepertrueinitialization graph exposed. Five fullstateproviders30e42c/30e538/30e564/30e580/30e594 admittedafterhost131842 projections; targetbuild pending.

### Radio state providers settled; callback/final admission

Five native stateproviders target PASS1083definitions/43genuineimports/zeroduplicates; coherent selectedSHA ff5c0f6d7b3453a3fa6cfa8a2de8e862ae96a946af455299fad98c75035d1d0b. Full30bf24callback/30e9a4state reset/30bf6cfinalizer admittedafterhost196608+262144 projections; targetpending. True lowerfeature/event/messageproviders retained; no wholeimagecompleteclaim.

### Radio callback/final-state settled

Native30bf24/30bf6c/30e9a4 target PASS1086definitions/46genuineimports/zeroduplicates; coherentSHA0919abeb0e429b275ef25c16ca4479c7a014dcecb08479e5d68cac957b72ae86. Two fullfeatureproviders3099cc/308ff8 and numericdefaultinitializer30e9e0 admittedafterhost1052672+256; typed24B table3344c8 has exactnative-byte/hash/readerextent receipt. Targetpending, fullcomponentfalse.

### Feature/default round settled; message/reset admission

Two featurebodies and24B typeddefault/initializer target PASS1089definitions/43genuineimports/zeroduplicates, stableSHAcc45619e4287f3cd5c9633d93446245b065939df482c2748cfd0268b05c2eb1a. Fullnative3075ccmessage/reset and3133a0schedulerrootclear admittedafter4096controlled hostprojections; targetpending. RuntimecallbackABI/layout/hardware remainsunqualified; no fullcomponentclaim.

### Message/reset settled; state-machine registrations admitted

Native3075cc and3133a0 target PASS1091definitions/42genuineimports/zeroduplicates, coherentSHA72ee4cd9eaa54ff75aa6a09557f2f239f98ce80f1fc24daa0829b3e79e2872f9. Native329534predicate and307d64/30a37csource-functionregistrations admittedafter65537hostprojections; real321150/32b04cstate-machines remainimports. Targetpending; no executableliteralpublished/no fullcomponentclaim.

### PHY registration settled; master PHY state machine admitted

Registration target PASS 1094 definitions / 42 genuine imports / zero duplicates, stable source SHA 0146aa3b4fbfbc48bf482c369711bea16cb85e79c03bf4d665f57b4c1f627780. Corrected two symbol descriptions from CIS to slave PHY using authenticated native labels. Master PHY 321150..3212ee admitted after native branch audit and 6,291,456 controlled host gate/completion/defer projections. Procedure 21 force path bypasses pending writes exactly as native branch 32123c. Native action/transition tables and five actual children remain genuine providers; callback-mutated state rereads are source-audited but host callback execution is not qualified by this fixture. Target build pending. Full component remains incomplete.

### Master PHY state settled; four children admitted

Target PASS 1095 definitions / 48 imports / 0 duplicates, stable SHA c8b2d31463d99d7b7d10fcfbb1043bcb5edb2dc555c694689e3672a1d9d9ce62. Full master PHY body compiled. Four native children 32c810/32c818/32caa0/32cb48 admitted after 65,536 controlled boundary cases; bound timer stop and termination to existing authenticated C providers instead of introducing aliases. Next target build pending. Tables and reject-message provider remain genuine frontier. Full component incomplete.

### Four master PHY children settled; reject/action admission

Target PASS 1099 definitions / 44 imports / zero duplicates; stable SHA 0544a3c0fc6b7d661520008e1287e6d670c0d970f0353c75326ef9f0530938c0. Four native children complete C; existing timer/termination providers reused. Full reject32698c and action tails31634c/3163a4 admitted after 1,048,576 controlled packet projections. Real allocation/send/event response dependencies remain genuine. Next build pending.

### PHY reject/actions settled; packet and typed tables admitted

Target PASS 1102 definitions / 46 genuine imports / zero duplicates, stable SHA 730738b67680491c2d5b7973d5350437da06a141e23ca3216cadca0a76830032. Full reject and two native action tails complete. Packet allocation32d2f0/send32d32c admitted after393216 controlled projections, reusing selected allocation/header/queue/event/scheduler source providers. Five-state/eight-action native table33522c emitted as160B typed function relocations, transitions3352cc as40B numeric initializer; native binary hashes/reader and finite transition domain retained in master-phy-tables-provenance.json. Remaining genuine action providers unresolved, no literal executable aliases. Next build pending.

### PHY packet/tables settled; five action bodies admitted

Target PASS 1106 definitions / 50 imports / zero duplicates, stable SHA eb2d94521aa02347e963a6d7e5600e6c8e947bafd16e82fb581f5658794ecc23. Typed table providers and packet construction/enqueue compiled. Additional4096 controlled callback-state projections pass. Five action bodies31592c/315a0c/315e60/315e84/315f0c admitted after196608 controlled sequencing/data/return projections. Remaining three table action bodies315c64/3164a8/316550 plus new true children are concrete source frontier. Next target build pending; fullcomponent incomplete.

### Five PHY actions settled; full table action source closure admitted

Target PASS 1111 definitions / 48 imports / zero duplicates, stable SHA efca6f3b8e6d0905d6166e066f77382019e76cec9ab3ec05c101f34dd4e865de. Remaining three genuine table action bodies315c64/3164a8/316550 and feature-mask31b39c admitted after132096+262144 controlled native mode/cache projections. All ten table destination routines now have full selected C bodies. Child325250 return is explicitly ignored: native delay slot captures original record before call. True deeper providers, ROM contracts, layout and runtime qualification remain open. Next target build pending; this is routine-group source closure, not whole component completion.

### Ten master PHY actions settled; four lower providers admitted

Target PASS 1115 definitions / 52 genuine imports / zero duplicates, stable SHA 62ee31237441bab3fb4245963294c9a49063aac263efa5011c814f854dd31347. Routine-group completed: all ten master PHY table destinations have compiled source; full component remains incomplete. Source bodies324680/325250/318278/32c7e4 admitted after262144 controlled child-call/halfword-domain projections, reusing selected queue/timer source. Deeper update/packet/event response and slave PHY remain actionable. Next targetbuild pending.

### Four lower PHY providers settled; preference/update queue admission

Target PASS 1119 definitions / 48 genuine imports / zero duplicates, stable SHA 5b40677627dcda69fc65bd4199ac86899a6831c3bc6c0316b5f969dd96c43624. Full preference selector316610, byte state setter327544 and update queue drain32e220 admitted after1114624 controlled mask and queue projections. Existing selected priority projection, event decode/process and queue APIs reused as authenticated children. Remaining packet constructors326740/326764 and event responses3232dc/32317c plus slave state machine actionable. Next target build pending; whole component incomplete.

### PHY selection/queue settled; packet parent admission

Target PASS 1122 definitions / 45 genuine imports / zero duplicates, stable SHA 4ee5c5666a92e29226893ee77328a2f45a269fb45dfd263030995fe4a5e5f304. Full selector/state setter/update queue source compiled. Four genuine packet providers32671c/326740/326758/326764 admitted after335872 controlled layout/negotiation projections. Numeric transition table target exact40/40 bytes and all18 nonnull action relocation identities PASS. Deeper326814 retains undecoded native instruction301e0054 at32684a as genuine provider; no invented math. Nextbuild pending; event responses/slave PHY remain recoverable code.

### PHY constructors settled; update-message source admission

Target PASS 1126 definitions / 44 genuine imports / zero duplicates, stable SHA a2115a326aa06cc48f110726df83d9ed651faae5657fdf8f9ebeaa4d70a2854e. Previous unknown instruction32684a resolved: exact assembler bytes for MPYWHUL r20,r0,r1 match stock; pinned opcode table and Synopsys manual establish operands/semantics. Native32686c same opcode R15 destination. REA explicitly rejects ARC ELF architecture; no tool decode claim. Full locked queue count314114 and update-message326814 admitted after131073 controlled timing/fresh read/packet projections; uses authentic selected MPYWHUL/MPYW helpers. Nextbuildpending. Nativeevent-response ambient stack fields and slavePHY still source frontier.

### PHY update message settled; slave state machine admission

Target PASS 1128 definitions / 43 genuine imports / zero duplicates, stable SHA c68d9c7568a35b2638a762725841f6bb3f06e8c41a43bb7f3f685855a607c90c. Full native queue count/update message compiled with exact MPYWHUL identity. Full slave PHY32b04c..32b20e admitted after6553600 controlled finite gate/pending/defer projections; preserves strict event112 pending-word equality, fresh state rereads, state5 flag byte634, and slave deferred operation3 cleanup. Genuine seven-action table providers remain open. Nexttargetbuild pending; whole component incomplete.

### Slave PHY state settled; typed table admission

Target PASS 1129 definitions / 44 genuine imports / zero duplicates, stable SHA ec01923be84db02d9aad5d91a5ee9b3d59c0d8e960c76be2f6ce8c88ef0e094f. Full slave state machine compiled; six-state/seven-action table33565c emitted with168B typed source function relocations and42B transition335704, finite transition values0..5. Seven table destinations still genuine open C providers; four reused authenticated master actions. Nexttargetbuild pending.

### Slave PHY tables settled; seven action providers admitted

Target PASS 1131 definitions / 49 genuine imports / zero duplicates, stable SHA 354ce52fecd410740336ade2a8dcdd2247b0161537690276c8d85167fefc89cd. Seven remaining slave table actions315a28/315c30/315e70/315e80/315eac/316354/31644c admitted after66562 controlled projections. Callback-modified second stack byte read after update-complete is explicitly volatile and tested. All eleven slave table targets now selected full C (four reused master actions); deeper32cb58 still genuine import. Nexttargetbuild pending; source group closure is not full image completion.

### Eleven slave action destinations settled; full slave update admission

Target PASS 1138 definitions / 43 genuine imports / zero duplicates, stable SHA 2ea8d9fac9e8ee186a9b5d6e0f64845cff1bcb5f60d8ba577d98989a4a220d8a. Routine-group completed: all eleven slave PHY table targets have compiled full C. Full slave update32cb58..32cbec admitted after1048576 controlled direction/support/wrapping-instant cases, preserving dual reject behavior and native instant/zero return forms. No new child dependency beyond selected supported-mask/termination source. Next target pending. Event response stack ambient fields and broader controller source/data/layout/ROM/runtime remain open; whole component incomplete.

### Full slave update settled; native event-frame source admission

Target PASS 1139 definitions / 42 genuine imports / zero duplicates; stable selected SHA18d3cff29ec3930d06bc7729f2f984831332c8061ef6f312b3e94957b8f312f4. Slave transition table42/42 bytes and all21 genuine function relocation identities PASS. Full event response3232dc and length response32317c admitted as C body plus named authentic ARC entry frame: original16/20B frame reserved before C and unassigned event bytes preserved from native caller stack. Controlled signed-index/event-layout131072 cases PASS. Native frame runtime remains unexecuted; next target build pending. Broader genuine providers/data/layout/ROM/runtime remain open. Whole component incomplete.

### Event frame source settled

Target PASS1143 definitions /40 genuine imports /zero duplicates, stable SHA50f2bd06219c2dac99b8a5a695d4f2919083b566dd99227c9eb815dffc05a86b. Named ARC entry shims verified in target disassembly: original16/20B reserve/release, event pointer originalSP+4, signed DIV912 in C bodies. Controlled slave callback-mutated state/next5/terminal cleanup10752 cases PASS. Full component remains false.

### Associated-row initializer/event/state source admission

Full native30a328 initializer,32b4e4 single/all-row event and32b5ec callback-mutated state transition admitted after69938 controlled version/row/table projections. Tables335328/335368 are typed function relocations and16 exact numeric transitions; five genuine action destinations remain imports. No executable literal aliases added. Next target build pending; full component false.

### Associated state/table settled; three native tail actions admitted

Target PASS1148 definitions /44 genuine imports /zero duplicates, stable SHA61b2319d6cbd14a26970a2a8a42b6b1a25430d1eebb1c50090fc04c2a4b78470. Target numeric transition16/16 bytes and8 action relocation identities PASS. Native324a8c/324aa0/324c60 and release324a60 admitted after196608 controlled signed-index/call-order/return cases. Existing periodic-status30e878 ABI corrected to return its actual native event-callback R0; existing callers still ignore it. Genuine scheduler-drop3136ac remains a provider. Next target pending; whole component incomplete.

### Associated tail actions settled; event-init graph admission

Target PASS1152 definitions /42 genuine imports /zero duplicates, stable SHAfd63660e16333ce50898bd7091d6c81b1fda6d629d3b65031830c9e97d62786f. Three associated action destinations compiled; two full parents and scheduler-drop remain genuine. Native306c7c dynamic dispatch is named ISA source, preserves inherited registers and original R0=callback address; exact16/16 stock bytes proved. Full30e0e8/332c84/332cc0 event-state registration/mode/reset admitted after131328 controlled cases, reusing selected common-init/stop/count providers. Target pending; whole component false.

### Event-init source settled; full associated table parent actions admitted

Target PASS1156 definitions /40 genuine imports /zero duplicates, stable SHA6d1c132ca7963787b5c3873f5f1a6dd5a82f3ca5661628fbbf1be56587c713c6. Native dispatch/register/reset/mode group compiled. Full remaining action parents324aa8 and324b3c admitted after524288+24576 controlled branch/PRNG/CRC/fresh-field/callback/return cases. All five associated table destinations now selected full C bodies; genuine deeper channel-seed324c98/validation32b2d4/cleanup3266d0 and scheduler3136ac remain imports. Next target pending; whole component incomplete.

### Five associated action destinations settled; three lower providers admitted

Target PASS1158 definitions /41 genuine imports /zero duplicates, stable SHA7686f2cc22e20da841e47c4c9f403baed695e5c934a07d411da3b6131b4c3a93. Routine-group complete: five associated action destinations compile. Full channel-seed324c98 admitted after4194304 independent byte-reversal/MAM/mod37/remap projections; unsigned reciprocal37 exact for all65536 input halfwords separately checked. Full scheduler-drop3136ac and cleanup3266d0 admitted after4608 controlled exclude-ID/max/callback-fresh counter/allocation/event cases. Native333bec does not alter R11, preserving zero used by scheduler clear; C variable encodes this native contract. Validation32b2d4 remains genuine provider. Nexttarget pending; full component false.

### Associated lower providers settled; additional unknown instruction resolved

Target PASS1161 definitions /38 genuine imports /zero duplicates, stable SHA6818339cb251fea57c07120c1280e334b4db80e746383dd9468aac09918c6286. Channel seed, scheduler-drop and cleanup-event compile. Validation32b2d4 remains genuine, with deeper scheduling/record callbacks exposed by native. Native32b4d4 word311f03fe resolved as MACWHUL 0,r1,r15 by exact assembler4B and pinned manual page1466; unsigned32×low16 accumulator addition established, not substituted with guessed MAC arithmetic. Broader source/layout/ROM/runtime remain; full component false.

### Full associated validation graph source admission

Full validation32b2d4..32b4e2, true radio-tail32b2d0, random31896c and slot-query31b2fc admitted after393216 controlled whole-parent mode/power/captured-limit/fresh-read/allocation/loop cases. Native31b304 additionally resolved to MPYWHL r3,r0,2824 by exact8B assembler emission. MACWHUL helper preserves named original accumulate instruction and low32 result with publisher semantics. Allocation output is only read on success; authenticated3133b4 success writes the supplied output. Fresh selected-word read stays in original current-time call delay position, before the child. Genuine callback32b538/32c69c, object-init312918, slot-allocate3133b4, schedule-insert312da4 remain source frontier. Targetpending; full component false.

### Associated validation and slot allocator source round

The complete `32b2d4` validation parent, random provider `31896c`, query `31b2fc`, and true tail `32b2d0` compiled coherently (`em-associated-validate-round/receipt.json`): 1165 definitions, 42 imports, zero duplicates; snapshot stable at `3a0f1b4b1a447f857164c79c9bcdd0419dbffcf56184fa797cb2136a07dee703`. Controlled host qualification passed 393216 cases. No native ARC execution claim.

The next prepared group reduces allocator `3133b4`, selector `333948`, occupancy `33382c`, setter `3338f4`, and bitmap `3336d8`. All retain unsigned wrap, truncated lane widths, zero-divisor destination preservation and native volatile order. Occupancy reloads the quantum per bitmap bit as the native loop does. Controlled differential source models passed 133120 cases, receipt `associated-slot-host-receipt.json`; final target receipt pending at time of entry.

Remaining associated frontier: object initializer `312918`, packet callback `32c69c`, scheduler insertion `312da4`; radio callback `32b538` and exact native-frame event reporter `30e89c` are prepared outside selected source pending qualification. Their channel-update child `327af4` remains explicit. Broader init/radio/ROM/data/layout gates remain. Full image incomplete.

### Associated radio callback source round

Full native `32b538` is selected with source-owned retry loop and captured/fresh volatile operands. Its `30e89c` event provider uses named ARC instructions preserving the real 24-byte caller frame and three untouched event bytes; 32/36 instruction bytes match exactly outside the relocatable BL. Controlled host callback cases pass 131072, covering count wrap, optional copy/reporting, cleanup return and callback-mutated counter. Corrected coherent target `em-associated-radio-callback-corrected-round` passes 1172 definitions / 41 imports / zero duplicates, stable source SHA `82df10182016c81dff873034a8783e264c9c73037916a4cc7907cf3f5f14dc56`. Initial target attempt failed on a provider name mismatch; corrected to existing `associated_channel_seed_324c98`.

Next channel-update graph prepared: all six typed action destinations `3279a4/3279b4/3279c4/3279d0/327a04/327a3c`, engine `327aac` and updater `327af4`, with native event maps, genuine function relocations and transitions. Both indirect tails match 32/32 native bytes. Controlled source contract cases pass 131080. Target/table verification pending. Invalid states beyond native reachable0/1 remain unqualified; no invented guard.

### Channel graph settled, object initializer target pending

Channel graph coherent target PASS: 1180 definitions / 40 imports / zero duplicates (`em-associated-channel-pending-round/receipt.json`), stable source SHA `20a32f9833cf9cda1a382f8993395ae2e23e7df6d6c375a795d3c7b51adda352`. Verifier `verify_associated_channel_tables_target.py` proves all 20 event-map/transition bytes and six function relocations equal native meanings. This completes this C source subgroup, not the image.

Full object initializer `312918` now reduces all eight native packet-type branches and stores the computed duration. Existing native piece/duration/quantizer providers are reused. Review preserves type3 zero-popcount wrap, signed low-halfword MPYW in fragmentation, captured kind bits, and extended type6 conditional constants (400 for kind2,492 otherwise). Controlled native-contract golden/argument checks pass4862; fragmentation wider domains and ARC runtime remain unqualified. Target admission is running under `em-associated-object-init-round`. Remaining associated source child frontier after this parent: packet callback `32c69c`, insertion `312da4` and its conflict child, plus broader radio/initializer and ROM gates.

### Object and packet callback settled; insertion graph compiling

Object initializer coherent target PASS: 1181 definitions / 39 imports / zero duplicates, stable selected source `13fab2513262f32fc40e228f1ef353924b0fd1d5d1c817b6f6c2db32337f170f`.

Packet callback `32c69c` coherent target PASS: 1182 definitions / 41 imports / zero duplicates, stable source `af900f05578f859fb3cda3e1b6eb0af1646bfc013c520868e9b52073e0d1be4f`. It preserves saved692 return, count underflow, captured consumed extent, fresh child-written pointers/counts, carry and reciprocal quantization, active-byte restoration. 1620 controlled host cases pass. Newly explicit genuine children `3259fc`, `323ac8`, `3243e0` remain to reduce; provider count growth reflects discovered graph.

Full scheduler insertion `312da4` and priority/tie helper `313310` now have C basic blocks retaining native BP/BN subtraction N-flag decisions and list/callback capture order. 4704 controlled list cases pass empty/before/between/after, rejection, multiple removals and head timer transition. Target receipt `em-associated-schedule-insert-round` pending. Tie-callback/mutated-list and wrapped-time native execution remain unqualified.

### Scheduler and rejection sampler settled

Corrected scheduler/channel target passes1185 definitions /39 imports /zero duplicates, stable source SHA `f78215286f484a9b6978c2207f25558d5e65a7a480338a7c699eaf7fdaf87015` (`em-associated-scheduler-channel-round`). Initial insertion target failed because prior tie argument used uint32_t (ARC unsigned long) while true pointer uses uintptr_t (unsigned int); selected declaration corrected to pointer type. No ABI width change.

Sampler `3259fc` retains full native random+old-byte sum, MPYWHUL reciprocal, signed-halfword MPYW correction, global64 mask, modulo64 shift and low-word return.9472 bounded cases pass all old-byte values and37 single-bit masks with rejection counts. Empty mask intentionally retains native endless rejection.

Prepared/admitted packet wrappers `323ac8` and `3243e0` initialize all five header bytes and preserve nine compositor arguments.196608 captured argument cases pass. Current target `em-associated-packet-builders-round` pending. Source frontier now moves to actual compositor323dc0, rather than fabricated packet children. Whole-image remains incomplete.

## Compositor and typed action round

Completed C source group: full compositor `323dc0..32412a`, coherent target
`em-full-compose-round`:1188 definitions/41 genuine imports/0 duplicates,
stable source SHA537f5e66e0cbe37bb2ce9478fbc53e2b8154ea1680ada8c2c1651f6d10a80921.
Controlled host scope263168 cases passes. Five genuine child providers exposed;
no numeric callback address substitutes. Three native table3352f4 identities
are represented by genuine function relocations, independently verified PASS.

Completed C source group: channel-map3237e8 and PHY-update323820 encoders,
131072 controlled host cases PASS. Settled target1190 definitions/39 imports/0
duplicates. Extended connection-state32366c encoder also completed in C,
65536 controlled encodings PASS; target build pending. Two remaining compositor
children are finalize32412c and auxiliary encoder324438. Target compilation and
controlled host serialization do not qualify native ARC runtime or full image.

Completed C source group: all three compositor actions, full finalizer32412c,
duration guard312bb4/pointer encoder323bac, auxiliary descriptor324438 and
clock class318988. Finalizer isolated host5120 PASS; auxiliary descriptor77824
PASS, includes quantization boundaries, enabled/slot masks and wrap bytes.
Auxiliary target `em-compose-aux-round` PASS1196 definitions/36 genuine imports/0
duplicates, stable source SHAee93358868155fcaaceec3ecc7f3929138c205ecbe2d89cd88b83ff4b61b6f1e.
Compositor immediate source graph is closed. Wider21 initialization lowers,
four radio providers, packet default table and10 resident-ROM contracts remain;
final source-owned data/placement/runtime gates remain separate.

Completed C source group: full radio scheduler313424..31369a, coherent target
`em-radio-schedule-full-round`:1197 definitions/35 imports/0 duplicates, stable
SHA40ff4ad534f8e4dc8304f2c12b32030946ffbbc88d7d1efc60d800d56438c7e5.
584 isolated host cases pass empty/periodless lists, three occupancy policies
and existing-slot/missing-slot behavior. Native DIVU destination prior, DIV,
MACWHUL/MPYWHL retained; arbitrary bitmap, wrap/zero-divisor and native runtime
still unqualified. Selected parent closes the genuine313424 import.

Completed prepared source group: initializer307bdc,404-byte reset3205b4,
state-event dispatcher320580 and native-attributed16-action/16-byte transition
tables.80 isolated host cases PASS. Genuine seven table action providers are
exposed, without absolute stock code-pointer substitutes. Target build pending.
Ghidra-MCP availability rechecked: no running instance. REA ARC architecture
limitation remains; unknown312344 instruction was not guessed or emitted raw.

Scheduler source/host correction: earlier584-case receipt and target source
were superseded after native review identified R8 starts1. Run-end usesbit+1;
corrected host584 PASS, coherent selected source build
`em-init-state-leaf-scheduler-corrected-round`:1201/40/0,
SHA7a01f8b5a5ea2ade3d5f906b8087e9fefcf497ba8cff4989aba32102ed8f4c24.

Initializer307bdc/reset/dispatcher tables compile. Target-native table oracle
PASS11 typed function relocations,5 authenticated null slots and16 exact
transition bytes. Enabled trigger action31b6b0 host512 PASS. Four more complete
actions31b4a4/31b4c8/31b614/31b648 and shared status3257a4/cleanup325740,
countdown30e49c/event-clear322884 are now C;262 isolated host cases PASS.
Cleanup preserves the unusual native second-loop48-byte advancement on every
iteration. Native/source two6-byte status descriptors and38 defined status
bytes are represented semantically; frame padding38/39 remains unqualified.
Target running; two substantive table actions31b4e0 and31b3b8 remain.

State action target settled1209/36/0, SHA0eaa3fe54abc93680f5402f356489f55a489e5515f6e97f16b85af25a1f054c4. Report31b3b8 full C/2050 isolated cases PASS; target1210/35/0. Unwritten bytes48..51/55..59/85 preserved. Creation31b4e0 and query31b21c/count-up30e4cc/start320b08 now C/304 controlled cases PASS. Successful harness expected period corrected after recognizing native report word store overlaps the later fresh period read. Three real new children316c58/31ad90/32074c remain imported. Creation target pending.

Creation action target settled1214/37/0, source SHA0408367f69820d1093e8419bec5a37027c49cd3fe1903afb59458e789fcf044c. All seven action identities now defined in C; latest target table oracle11 relocations/5 nulls/16 transition bytes PASS. Remaining new native connection children316c58/31ad90/32074c are real imports. Broader20 initializer,3 radio,1 default table,10 ROM interfaces remain. No complete firmware/hardware claim.

Channel selector325898 and initializer306ab4 full C target settled1216/36/0, stable SHA30eae218047b8cdc4040398dba65225b388ea1c4d636aa74a9110670cc7cd67e. Isolated canonical reference524544 cases PASS. First target failed existing one-word initializer declaration; corrected body explicitly ignores incoming word, reran host and target. No algorithm alteration. Remaining19 initializer/3 connection/3 radio/1 default table/10 ROM interfaces plus source data, placement, native/runtime/hardware gates.

### Connection release and advertising callback source closure

**Completed EM C source group:** native31ad90 release parent plus3252b8/32d5f4 queue drains and31ae64 recycle adapter. Controlled source/native-CFG harness432 cases PASS; queue counts wrap8bits, handler255 skips nested payload/recycle, timers use exact384/728/476/496 offsets, second callback/event globals reload after first callback. Coherent ARC target `em-init-connection-release-round`: 1220 definitions/35 genuine imports/0 duplicates; stable source SHA479a1b58055a4b4dea07121aa42a3df683ab158683c167d53183dd72d3607410. Genuine connection children316c58 and32074c remain. Indirect callback ambient registers beyond explicitR0/R1 remain an ABI gate; no ARC runtime or hardware qualification. Remaining EM source interfaces19initializers/2connection/3radio/1default table/10ROM =35; these interfaces are not a whole-image missing-body count.


### Allocator, connection parameters and scheduling callbacks

**Completed EM source groups:** full connection allocator316c58, parameter constructor32074c, first-channel helper325708, pending callback31e5ec, scheduling callback320908, full arbitration318b78. Allocator600 and parameter257 isolated cases PASS; parameter host uses explicit XBFU substitution, not native execution. Schedule30 and comparator16 branch cases PASS with controlled children. Final ARC target `em-init-schedule-compare-round` coherent1226/35/0, stable SHAadc92c0dac13d6904a095df9ce8629c1f51da8ce3338ba3fb348582faf2441ca. Native delayed slot320938 captures schedule input, not scheduler result; full318b78 extent continues to318c18. Native parameter flag writes share the record address; initial harness expectation corrected before admission. Both constructors and their genuine relocation callbacks compile.

Remaining EM interfaces:19initialization lowers, callback3205c4, finalizer31ec40,3radio providers,1default table,10ROM contracts =35. These are interfaces, not whole-image missing-body counts. Full31ec40 source draft is prepared outside selection; genuine312f88 adjustment child will remain exposed when admitted. Data/startup/placement/nativeARC/indirectABI/hardware gates remain. Ghidra-MCP rechecked this round: no running instance.

Boot latest369units/996providers/3ROM imports, bounded158420B placement; STIMER raw status native70 cases PASS and startup hook8 cases PASS. Latest21direct-root reachable attribution items (48/903 catalogue labels). Main latest settled2488/799mixed interfaces/0duplicates; six slave pointer cells source-owned, connected production advertising bodies qualified. Next service-discovery aggregate awaits coherent terminal receipt; mixed interfaces are not missing-body estimates.

Codec B separate stage1 now11 C units and layout/typed BINH packaging probe; 0x1734 source load inside0x3000 block, corrected header-adjusted runtime mapping. Direct23targets and105internal dispatch words accounted for. ELFbfde943a07a5702c7151d33717cda34213aaf03c2236f711424539b578bd0949; experimentalBINH64ac7f7006ca7535cfdf8da5dedb461a8ffd8a63a9ca96d6c0054c5aad5e0b6a. Not combined stage2 or hardware proof; stage2 late section remains outside stock0x1408c copy and15address/data contracts remain. Case,Touch,Codec A prior gates remain. Full-image components complete **0/6**. Three workers and goal remain active.

Settled EM schedule-finalizer target receipt: 1228 definitions /35 genuine imports /0 duplicate strong symbols; stable source SHA256 `2301517673cf59401a84276d45e5ae274f2a31dbe63c5ec07fc8044cba222b74`. Full native finalizer and next-channel C bodies target-compile; host 166 cases pass under explicit child cuts. Source completion remains false; adjustment312f88 and callback3205c4 remain genuine bodies to recover.

Corrected full callback3205c4 target snapshot PASS: 1230 definitions /33 genuine imports /0 duplicates; stable source SHA256 713d334dc75e66bb5d372a810e95c15fd4645fcb499160a1ea0ee9877e259186. Host64 cases include pack-child mutation demonstrating capture-before-call delay semantics. Native ARC whole-runtime not proven.

Registration source group COMPLETE: native307c18/307cc8/307d2c/307de8 and getter307cb8 C, host1025 cases PASS. Coherent target snapshot 1235 definitions /38 genuine imports /0 duplicates; stable source SHA256 4923510b0869bb14fab08c820507f58f992967371b623015a5390eaa64484851. Four lower initializer bodies closed (15 lower initializers remain); nine genuine registered callback identities exposed, bodies/signatures remain address-only gates. No literal native executable address substitution.

Settled response callback target: 1238 definitions /37 genuine imports /0 duplicates; stable source SHA256cc43d13831ef509e52faa50ed9811ed6d52712a98eaf97a75f773607230625a5. Full324fb4+326a84 bodies and typed7B response table compiled; host5120PASS. Registered callback bodies remaining8 plus15lower initializers and persistent radio/ROM/data gates.

Secondary dispatcher source/table group COMPLETE: target1243 definitions/40 genuine imports/0 duplicate strong symbols; stable source SHA256f5ff8569040271715388a9723db124187529b925eed40ad70197f19dd6dcfeba; host304PASS. Target native table verifier confirms24exact transition bytes/7 genuine function relocations/17nulls. Four genuine secondary action bodies and ambient callback register ABI remain gates.

Secondary schedule action318fc0 and message helper325d50 source group COMPLETE: host1024PASS; target1245 definitions/39 genuine imports/0 duplicates; stable source SHA256b33b170f01650cab6196f0ec10f5788925cf2514514ad552500bf295a544c635. Three secondary action bodies remain; named child implementations are selected source.

Settled separate initializer target integration PASS: 1255 definitions/51 genuine imports/0 duplicate strong symbols; all four source unit snapshots and monolithic controller stable and match current files. Five initializer lowers closed (10 remain), two callback leaves/two stream children source-owned;15 callback identities +2 actual child bodies exposed by this unit group. Root host256-version PASS. Real child frontier increase is not source completion.

CORRECTION: full native307980/307a68 review finds context+16 stores loop index0/1/2 (native3079ba/307aa0), not zero. Prior selected stream-child source/host qualification is SUPERSEDED. Selected source corrected; stronger per-row/null-pattern fixture and expanded coherent target rebuild required. Compiler receipts remain historical compilation evidence only.

## Corrected nine-unit initializer integration

Target `em-init-corrected-nine-unit-round/receipt.json`: PASS, 1268 definitions, 53 genuine imports, zero duplicate strong symbols. All nine source snapshots were stable during compilation and matched selected hashes on independent receipt review. Both stream context+16 stores now preserve native loop index0/1/2. The old zero-store equivalence receipts are superseded. Independent strengthened host fixture passes256 version states, index bytes and null-entry patterns. This closes the bounded initializer source group, not whole EM source completeness.

Next group: native3213f8 record initialization and3213ec callback wrapper are prepared with512 full-record/callback host fixtures. Three true callbacks321648/321c30/321958 remain; whole-image startup/data/ROM/ABI/runtime gates remain.

### New callback candidates held for correction

Independent native review of prepared31e7fc found scaled ADD3: queue argument is record+360, not record+45. Prepared31f9b0 must reload record mode before second child and final dispatch, as native does; cached mode fails child mutation. Neither candidate has been admitted. Earlier32/36 host fixtures are superseded for behavioral validation; worker tasked to repair and strengthen tests.

## Secondary record initialization complete as bounded C group

`em-init-secondary-start-round`: targetPASS1270 definitions/55 genuine imports/zero duplicates, selected monolithic snapshot stable and independently hash matched. Native3213f8 exact clear/stores plus3213ec original-object forwarding now source-owned.512 full-record/callback host fixturesPASS. Three genuine callback children321648/321c30/321958 remain; no whole-image or hardware completion.

## Corrected two-callback integration underway

31e7fc queue offset corrected to360 (nativeADD3 scaled45);31f9b0 reloads mode before second child and final dispatch. Independent host rerunPASS144 mutation cases and32 queue/loop cases. Both corrected candidates admitted into separate selected units with typed callback identities; target `em-init-two-callbacks-corrected-round` pending. Worker prepared graph callback identity backlog decreases19→17 while four genuine child bodies surface3191dc/319714/32a000/31e4a0. These are graph counts, not missing whole-image source counts.

### Corrected callback target rebuild settled

`em-init-two-callbacks-typed-round`: PASS11 initializer C units,1272 definitions/57 genuine imports/zero duplicate strong symbols. Independently verified all selected compile source snapshots stable and hash-current. A preceding attempt failed typed-function pointer registration checks; selected registration stores now use explicit uintptr_t→uint32_t conversion, preserving genuine linker relocations. Prepared registered callback backlog17; four additional child bodies unresolved. Native3191dc43 opcode rows/35target blocks are mapped as CFG preparation only:32 blocks plus shared interior-register ABI remain, not admitted as fake function coverage.

## Secondary response/action319094 source group completed

Full native319094..3190dc,324768..3247d0,30e928..30e984 bodies source-owned; target `em-init-secondary-action319094-round` PASS1275 definitions/57 genuine imports/zero duplicates. Selected monolithic compile snapshot stable and independently hash-current.96 bounded host field/state cases cover six slots, counter scaling extrema, enabled/disabled event flag and action notify branches. Event stack bytes5/17/25..27 remain unowned; no fabricated fill. Source/native instruction contract only, no ARC runtime/hardware proof.

## Secondary cleanup/action3190e0 group target pending

Prepared full3190e0..3191aa,321450..32148c,30e47c..30e488 source admitted;12304 host fixture cases cover eight-bit decrement wrap, six slots, callback presence, pending release, armed/flag/event/allocation states. Known callback R0/R1/R2 inputs preserved; unknown ambient ABI remains qualification gate. Target `em-init-secondary-cleanup-round` running.

### Secondary cleanup source group settled

`em-init-secondary-cleanup-round`: targetPASS1278 definitions/56 genuine imports/zero duplicate strong symbols; selected compile snapshot stable and independently hash-current. All five unique secondary action identities in typed24-slot table now source-defined. This is bounded action-graph closure; callbacks, product/scatter/startup and runtime gates remain.

### Primary registration source group pending

Full native307d74..307dd4 admitted;256 host cases exercise all version values plus child-driven product pointer/version mutation, exact404-byte clear and callback identities. Target `em-init-primary-registration-round` running. Four genuine callback bodies3228a8/3228f0/3227e0/3227a4 remain imports; direct initializer body backlog10→9 after target acceptance.

### Connected packet dispatcher held for further correction

Prepared3191dc43-route connected candidate has not been admitted. Root review found packet child calls dropped native R1 payload; EXTH/EXTB conversions incorrectly sign-extended instead of zero-extending; simple handler read/store ordering must also be reviewed. Earlier270-fixture behavioral claim superseded. Worker correction and payload/range/alias fixtures required before independent review.

Primary registration target settled: `em-init-primary-registration-round` PASS1279 definitions/59 genuine imports/zero duplicates; selected snapshot stable and independently hash-current. Direct initializer body backlog is9; four real callbacks surfaced, not stubs. Whole image remains incomplete.

## Auxiliary registration group target completed

`em-init-aux-registration-round`: PASS [1281, 68, 0] (definitions/genuine imports/duplicate strong symbols); selected monolithic snapshot stable and hash-current. Full307e30 and3042e8 source bodies own native callback-store order, six584-byte buffer pointers, threshold13 statebit12 and native R0 exits. Host256 version statesPASS; ten true callback imports surfaced. Direct initializer body backlog9→8.

Root independently reran corrected connected packet candidate:280 host casesPASS. This is child-cut/source-native instruction contract evidence only; actual ARC execution, aliasing qualification and ten remaining leaf bodies remain. Connected dispatcher still prepared/unselected.

## Command/identity initializer source group completed

`em-init-command-identity-round` targetPASS [1283, 72, 0] (definitions/genuine imports/duplicate strong symbols); selected snapshot stable/hash-current. Full3080f8 and30814c bodies source-owned;512 bounded host casesPASS, native state read/store order and delay stores retained. Six true callback identities remain. Direct initializer body backlog8→6.

Root independently reran eight prepared packet leaf-body host fixtures:768 leaf,65792 mask,512 word,256 accumulator casesPASS. Native32dba4 accumulator/register read/store order reviewed: packet byte contributions occupy disjoint bits and native carry never exceeds assembled low32 input, high word retains fifth byte. These are native-contract fixtures, not ARC execution/hardware evidence; graph remains prepared while five child bodies are reduced.

## Primary buffer registration source group completed

`em-init-primary-buffer-registration-round`: targetPASS [1285, 75, 0] definitions/genuine imports/duplicate strong symbols; monolithic snapshot stable/hash-current. Full30a0a4 plus31b7d4 clear body source-owned;256 mutation/order/clear/version fixturesPASS. Direct initializer backlog6→5; four genuine callbacks remain new imports.

Connectedpacket3191dc prepared graph now has all43 cases and13 real packet child bodies in ten C units. Targetrelocatable only four selected helper imports remain; graph stays prepared/unselected pending independent root full graph/alias review. Native ARC execution and finalplacement remain explicit external qualification gates.

## Configuration fallthrough group completed as C source

`em-init-config-fallthrough-round`: targetPASS1287 definitions/81 genuine imports/zero duplicate strong symbols; selected monolithic snapshot stable/hash-current. Full30a134 prefix and30a1a0 tail source bodies preserve native conditional callback registration, repeated version-dependent state stores, low-version product-pointer/high-version flag R0 returns. Stronger1024-case host fixture additionally checks prefix writes BEFORE mutation child and passes. Host contract only; not ARC execution. Direct initializer body backlog5→4.

## Experimental connected packet C graph integration

Both connected dispatcher candidates (43 routes and17 routes) plus13 packet decoder bodies copied into experimental selected build inputs. No interior code pointers/fake providers used.618 root connected-source/header fixtures use actual selected header/address/pack64 C, with eight explicitly substituted native-DSP mask calls; these do not claim mask numerical or native runtime equivalence. Individual leaf, read/store/mutation and gate fixtures retained. Target `em-connected-packet-source-round` running. Admission is experimental source-build integration only; native execution, overlap semantics, DSP mask, finalplacement and hardware remain open, so accepted whole-image coverage unchanged.

Experimental connectedpacket target settled: `em-connected-packet-source-round` PASS [1303, 79, 0] definitions/genuine imports/duplicate strong symbols,22 separate initializer/callback/packet C units. All compile source snapshots independently stable/hash-current. Both packet dispatcher body contracts and13 direct packet child bodies now compile in coherent experimental target; transitive selected helper runtime/alias/DSP/image qualification gates unchanged.

## Product clear and registration round

Completed full C bodies for native 30a29c and 30a27c. Native callback registration order, fresh product/version reads, repeated flag stores, captured output and exact count times 2824 clear are preserved. Root host fixture passed 768 cases. Coherent receipt `g2/build/c-firmware/20261011/em-init-product-clear-registration-round/receipt.json` passed target compilation with 1305 definitions, 84 genuine unresolved symbols, zero duplicates and 22 separately compiled lower units; every source snapshot was independently checked stable and hash current at review. Direct initializer bodies remaining after this round: 307ec8, 308630, 309cb8 (three). This is source/target compilation evidence, not ARC execution or accepted image coverage.

## Final registration preparation

Full C bodies 308630, 309cb8 and genuine child 31408c selected. Independent host fixture passed 256 registration count cases (0 through 255), state bit publication, callback identities and exact 304 byte clear with boundary sentinels. Target build is in progress at `g2/build/c-firmware/20261011/em-init-final-registration-round`. Direct initializer source frontier is now one body: 307ec8. The six callback identities introduced here are genuine unresolved imports. No callback bodies were fabricated.

Final registration target receipt passed: 1308 definitions, 88 unresolved symbols, 0 duplicates; all 23 compile source snapshots stable/hash current at review. Final direct initializer 307ec8 and child304324 now selected after native instruction review and 256 host version/identity cases. New target receipt in progress: em-init-direct-closure-round. All direct initializer bodies are now source expressed; callback provider and runtime gates remain.

## Direct initializer source closure

Final target receipt `em-init-direct-closure-round` passed with 1310 definitions/104 unresolved/0 duplicate symbols. All 23 compile snapshots independently stable/hash current. All direct lower initializer bodies now source-defined, including307ec8 and child304324; 256 host cases passed. Genuine callback and ROM imports remain, and complete image source flag is false.

## Mode safe leaf integration

Native instruction review and independent root host fixture PASS256 connected state cases for full bodies32c978/32cadc/32cb40/32cf78/32279c/313338. Six bodies added as one separately compiled source unit. Actual selected333a60 remains dependency. Ambient stack event bodies deferred pending ABI preservation; no arbitrary C stack equivalence inferred. Target receipt in progress: em-mode-safe-leaves-round.

Mode safe leaf target round passed 1316 definitions/104 unresolved/0 duplicate symbols, 23 lower units and all24 compile snapshots independently hash-current/stable. Four genuine initializer callback bodies30e840/327dc8/3280c8/325450 now source-defined as new selected separate unit, with corrected declarations and independent256-case host fixture. Callback322e44 remains genuine external child. Host fixture uses explicit child cuts and establishes no native runtime proof. Target receipt in progress: em-init-small-callback-round.

Prepared next full genuine child322e44 from authenticated native322e44..322e7c. Independent root host fixture passed256 cases with memset-child state mutation, exact38 initialized bytes,32 byte payload copy and pre-copy event code store. Selected integration awaits current target completion; prepared input receipts saved under init-event20-prepared. The four small callback fixture and six safe leaf fixture also now have hash-bound root host receipts.

## Small callback target completion and event20 integration

Small callback target receipt passed 1320 definitions/101 unresolved/0 duplicate symbols, with all25 compile snapshots independently stable/hash current. Four callback bodies are source complete for their known native contracts; remaining child322e44 now selected with PASS256 root cases. Native318edc full control flow independently reviewed by root; worker20 branch fixtures independently rerun PASS and its separate unit selected. Safe leaf32cf78/32cb40 and selectedrelease31ad90/schedule313354 connected; genuine31ac3c/3231c4 remain imports pending exact ambient ABI treatment. Target build in progress: em-event20-mode-transition-round.

## Event20 and transition target completion

Coherent em-event20-mode-transition-round passed 1322 definitions/102 unresolved/0 duplicates, all27compile snapshots stable/hash-current. Child322e44 and fullmode318edc are selected C providers. Exactstack wrapper322fdc and31ac3c now selected: semantic namedARC instructions retain20-byte frame, signeddivide, native branch/store order and real ambient event bytes; independently compiled/objectdisassembly reviewed. No raw executable bytes and no artificial frame zeroing. Target aggregate in progress: em-mode-native-stack20-round.

## Native stack20 target completion and connected dispatch integration

Coherent em-mode-native-stack20-round passed 1324 definitions/101 unresolved/0 duplicate symbols. All28 compile snapshots independently stable/hash current. Full322fdc native-frame provider and31ac3c gate complete as selected source. Root independently reviewed full named native-frame providers3231c4/323374 and C dispatchers322b70/3212f0 against authenticated instruction envelopes. Root fixture reruns passed:322b70 linksactual313338 source;3212f0 uses explicit special/fallback child cuts. Four separate units selected. Runtime callback data remains genuine contract; source31c420 remains import in selected aggregate. New target in progress: em-mode-connected-frames-dispatch-round.

## Fallback source review correction

Root found prepared31c420 mis-modeled native31c47e/31c482 delay-store: statebyte1 must become3 regardless of prior-state==2. Corrected full source prepared under mode-fallback-corrected-prepared and independently passed1024 states/events plus response/reject/default routes. Prior workerfixture preservingstate1 is superseded. Actualselectedresponse326a84/reject32698c already source-defined; threefullnativebyte-storeleafbodies prepared. No selected integration while current connectedframes build is live.

## Connected native frame/dispatcher target completion

Aggregate em-mode-connected-frames-dispatch-round passed 1328 definitions/101 unresolved/0 duplicate symbols, all32compile snapshots stable/hash current. Four full providers3231c4/323374/322b70/3212f0 source integrated. Next selected group includes corrected31c420 fullfallback, three nativeleafstores32cac4/32cacc/32cad4 and reviewed48-byte323028 nativeframe. Root1024hoststate/eventcases support delay-storecorrection; callback/runtimeeffects remain unqualified. Newtarget: em-mode-fallback-frame48-round.

## Parent31e4a0 full review

Prepared fullnative31e4a0 parent independently reviewed: actualBC unsignedLO event71/72 route, flags refreshed aftermodechild, L/M sharedrelease path, state3 clearing order,14argumentcall and6stackwords. Corrected contexthalf892 volatile read to precede base805c70 matchingnative31e536/31e53a. Independentroot12pathfixturePASS. Candidateunder mode-parent-corrected-prepared awaits currentaggregate completion beforeselectedintegration. Genuine31bd78 remains sourcecandidate pendingindependentreview.

## Correctedfallback/frame48 target completion

Aggregate em-mode-fallback-frame48-round passed 1333 definitions/100 unresolved/0 duplicates; all35compile snapshots independently stable/hash current. Native31c420 delay-store correctedgroup source complete. Full31e4a0 parent plus7typed callback bodies now selected after independentnative review and fixture reruns. Parent connects packetcallback31f9b0/31e7fc to source modegraph, except genuine31bd78 import. Seven callbackbodies are7/30tableidentities; table sourceplacement and remaining23identities notclaimed complete. Newtarget inprogress: em-mode-parent-seven-callback-round.

## Parent/sevencallback target completion and large body/table integration

Aggregate em-mode-parent-seven-callback-round passed 1341 definitions/100 unresolved/0 duplicates, snapshots stable/hash current. Fullnative31bd78 independently reviewed; two volatileordering fixes made before integration. RootboundedfixturePASS. Source-owned typed10x5callbacktable independently matchesall50cells in authenticatedpayload (38nonnullcells,30distinctidentities). Largebodyreferencesownedtablesymbol rather thanstockabsoluteaddress; final placement remainsunqualified. Fulltyped31bd78 callbackdeclarationsandregistration now useactualprovideridentity, nofakealias. Fourgenuine modechildren and23remaining callbackidentities remainexternal. Targetinprogress: em-mode-large-owned-table-round.

## Large/table registration repair and guard integration

Firstlarge/tabletargetterminatedcompilefailureininit_prelink: old31bd78 declarationidentityremainedinone registration aftertypedheaderreplacement. Correctedregistrationnowstoresactualtypedprovideraddressdirectly. Noalias/stubadded. Full31a988guardindependentlynative reviewed(all9onebasedroutes andoutofrange), independentfrozenrootfixturePASS(1408branchdomaincases); sourceunitselected. Correctedaggregate inprogress: em-mode-large-table-guard-repair-round. Firstfailedreceiptretained; large/table buildnotclaimedpassed.

## Selector current-source review and primary loop source

Full31affc selector independentlyreviewed acrossnative14/11/42eventtables, secondarycodeclassifications,event112capturedbitmapsandvolatilewrites. FrozenrootfixturePASS. NewlydownloadedprimaryGCCARCdescription pinnedcommit996a822fe5e1f9d980e7cda6a15fb01c49ce98e4 underthird-party/manuals/gcc-arc-loop confirms hardwareloop testcounter!=1 then decrement. Hash/provenance references existingARC release submodule. This supports LP10classification ratherthan nativeexecution equivalence. Selectorawaitsnextselectedintegration aftercurrentrepairedaggregate.

## Reviewedremainingmodechildren

Fullreject3233b4 anddone3234ec independentlynative reviewed andfrozenrootfixturePASS. Exactnativeeventframes3232a8/323314 reviewed;313960 child correctedfromnewunresolvedname toactualselectedprimary_query provider. Selector31affc rootreview/fixturepassed;allfiveunitspreparedforselectedintegration aftercurrenttarget. Nativeambientstack retainedthroughnamedinstructions; nocallbackruntime equivalenceclaim.

## Largeownedtable/guard correctedtarget completion

Correctedaggregate em-mode-large-table-guard-repair-round passed 1344 definitions/124 unresolved/0 duplicate symbols; all42compile source snapshots independently stable/hashcurrent. Full31bd78/providerregistration,ownedtable andguard source compiled; firstfailedreceipt superseded forcurrentbuild bythisnewreceipt. Nextfivefullunitsselector/reject/done/twoeventframes selected with independentnative review andboundedsourcefixtures; serializer313960 usesactualexistingselectedprovider. Newtargetinprogress: em-mode-deeper-source-closure-round. Sourceclosure ofmodeCFG still leaves23tablecallbacks inselectedaggregate plusgenuine deeperruntimecontracts.

## Deeper mode source closure and next callback group

Five full mode bodies compiled: 1349 definitions, 121 unresolved imports, zero duplicate providers. All 47 initializer source snapshots were stable and hash-current. Next selected group: 32cde0, 325f0c, 325f50. Independent host fixture passes 1280 bounded paths using the actual selected serializer; 32cde0 stores at native byte offset 200. Child 317ea4 remains unresolved. Target build pending; native runtime and hardware remain unqualified.

## Three callback target and five packet providers

Three-callback aggregate passed: 1352 definitions, 119 unresolved imports, zero duplicates; all initializer snapshots stable/hash-current. Selected next five full providers: common325d74, wrappers325dec/325df4,326a64,326aa8. Root native review corrected crossed mode fields: ctx77 controls lower568,ctx76 upper572. Root independent host fixture PASS9472 bounded packet/clamp paths, explicit allocator/sender/reject cuts. Target pending. Callback-table selected identities now14/30; 16 remain unselected. Prepared bodies29/30. Complete image remains false.

## Packet target settled; callback ABI correction

Five packet providers target PASS; source snapshots hash-stable. Followed child native review corrected32cde0 input to317ea4: captured byte, not context. Historical1352/five-packet builds establish compilation only and retain superseded child ABI; corrected host fixture PASS1280. Added three reviewed cleanup/loop/pass-through bodies with independent PASS1024. Next target pending. Table identities17/30 selected,13 await integration; prepared30/30 source group complete. Full EM/source equivalence remains open.

## Connected child and indirect/anchor source round

Cleanup plus corrected byte-child ABI target passed. Two real child providers317ea4/318920 now selected after full native review and authenticated typed eight-halfword table binding. Independent connected source fixtures PASS1179648 paths. Four table callbacks31635c/3163ac/316594/32c828 selected after full native instruction review and PASS132608 bounded paths. Loaded indirect targets remain runtime contracts, no invented providers. Table21/30 selected,9 await integration; prepared30/30. Next target pending; source_complete false.

## Timer callback and registered leaf source round

Connected children/indirect/anchor target passed with all initializer source snapshots stable and hash-current. Selected full32c884 and32ce04 after independent native review; PASS131583 bounded host paths, multiply is explicit host model. Pinned ARC assembler confirms stock MPYWHL operand encodings. Rebound secondary313354 caller directly to existing same-native typed schedule provider, no duplicate body or address alias. Table22/30 selected;8 await integration. Next target pending; complete firmware still false.

## Signed clamp packet callbacks

Timer/registration target PASS with stable hash-current source snapshots. Selected full326090/3260e4 after independent native review and PASS589824 connected signed-clamp/packet source paths using actual318920 provider. Table24/30 selected;6 await integration. Prepared32c908/325b14 corrected plain byte offsets232/236 instead of928/944; these were never selected. Next target pending; no native/hardware completion claimed.

## Packed-record callback round

Signed connected packet target passed; all initializer source snapshots stable/hash-current. Selected corrected32c908 literal offsets232/236 and full325b98 packet record body after independent full native review and PASS1536 bounded fixture paths. Table26/30 selected,4 await integration. Root pinned binutils arc-flag.def establishes CS and LO share code5: prepared32ce84 carry branch had reversed relation and remains withheld pending correction. Full source/native and image/hardware gates open. Next target pending.

## Timer-product and length-guard callbacks

Packed-record target passed with stable/hash-current initializer snapshots. Selected full325b14 after native review and PASS767 host-model/mutation paths; literal offsets232/236 preserved. Selected corrected32ce84 after full native review and pinned ARC CS/LO conditional proof; PASS4752 host guard/field paths. No native numerical runtime claim. Table28/30 selected,325a68/32cffc remain for root integration review. Next target pending; complete image/source remains false.

## Complete thirty-identity callback source group

Timer/length target PASS with stable hash-current initializer sources. Last two full callbacks325a68/32cffc now selected after independent full native review, exact pinned arithmetic instruction operand encoding, and own PASS768/PASS1024 bounded host fixtures. Corrected32cffc MOV.NC unsignedHS threshold and enable-clear delay-slot R0=800;325a68 preserves native interval-first MPYW operands. All30/30 table identities now selected as source; whole table group target pending. Numerical ARC runtime, live pointer producers, broader genuine providers, scatter and hardware remain unqualified; this is not full firmware completion.

## Thirty table identities target complete; initializer source closure continues

All30 source callback identities target compile/link PASS; initializer snapshots stable/hash-current. Group complete at C target-compilation scope, not native runtime/hardware. Next selected full32182c/3266f8/32468c/324698 after native review and PASS768+PASS256 independent bounded paths. Existing selected child providers reused. Literal-zero memcpy source content remains an external platform contract; fixture cuts the copy, no bytes invented. Four previous initializer imports now source-defined pending next target.

## Initializer scan/compositor/two-slot clear

Four initializer callback target PASS, initializer snapshots stable/hash-current. Selected full31ae84/3245ec/31810c after independent native review and PASS17152+PASS512 bounded host paths. Larger product scan counts remain ownership-unqualified; literal-zero source memory remains platform data contract. Captured base and fresh slot rereads preserved against child mutation. Three more initializer imports pending next target. Thirty mode-table identities already target compiled; whole firmware remains incomplete.

## Stream-gate and peer-pair registered callback source

Scan/compositor/two-slot target PASS with stable hash-current initializer snapshots. Selected full318168 and3183ec after independent native instruction review. Stream-gate PASS768 synthetic callback-mutation/gate paths; peer-pair frozen worker fixture rerun PASS4 bounded paths. Captured mode, four-register callback ABI, fresh object/config reload and path-specific returns preserved. Genuine runtime target/product data qualification remains open. Two more initializer providers target pending; full firmware source remains false.

## Identity-pair callback and actual child

Stream-gate/peer-pair target PASS, all initializer snapshots stable/hash-current. Selected full31836c and303918 after independent fullnative review; five frozen worker paths rerun PASS. Both primary/fallback kind paths retain native namedARCXBFU, host shift remains test-only. Actual selected31441c/31467c/303a60 providers reused with checked prototypes. Whole connected runtime/hardware behavior remains open. Next target pending.

## Native fill binding correction and transition leaves

Identity-pair target compiled with stable/hash-current inputs. Native33301c direct instruction review proves byte-fill memset; memcpy is332fc4. Selected324698/31810c corrected to actual selected memory_fill provider. ALL earlier literal-address-zero copy/platform-data claims for these two callbacks are withdrawn; historical receipts establish compilation, not that mistaken interpretation. Connected actual-fill fixture PASS512, exact cleared extents and sentinels checked. Selected three new full transition leaves3249ac/3249b8/327dbc after native review and PASS768 bounded paths. Next target pending; complete image remains false.

## Fill correction target and counter/gate providers

Corrected memset bindings and three transition leaves target PASS, all initializer snapshots stable/hash-current. Selected full3168e4/320068 native entries after independent review and PASS768 connected source paths using actual selected count providers; only commonrelease is fixture cut. Event308664 review corrected ASL single-bit highword composition and pre-serializer delayedstore, nativeframe candidates remain unselected pending review. Next counter/gate target pending; complete firmware still false.

## 2026-10-12 report frame integration

Native 316908 reduced to C body with named ARC 40-byte entry frame. Connected host fixture PASS256 uses actual selected memset and serializer; clears 36 bytes, preserves ambient bytes 38-39, and performs type-byte store before serializer as native delay slot requires. Event callback remains cut. This is source/host evidence, not native runtime or hardware qualification. Counter-gate coherent target passed with stable current initializer source snapshots.

## Event frame and transition parent integration

Report316908 target passed with all initializer snapshots stable/current. Full native review of308664 corrected ADD3 record byte offset to256, two-operand ASL to high<<1, and pre-serializer delayed store. Frozen connected fixture PASS256 uses actual selected serializer and seeded frame, preserving ambient bytes5,21,29..31. Parent324964 full native review plus three-branch host fixture passed with child cuts. Both selected for the next coherent target; no native execution/hardware claim.

## Prepared 31a700 review gate

Root full native review rejects current prepared pointer-lifetime mapping: native R13 retains captured nested object for CRC and late stores; fresh R2/R3 slot reloads supply only specified reads and mode write. Worker correction requested with mutation sentinels and exact volatile ordering. Prepared body is not selected.

## 31a700 corrected preparation selected

Event308664/parent324964 target passed with current stable initializer snapshots. Frozen31a700 source now preserves native capturedR13 stores and distinctfreshR2/R3 reads/modewrite, exact targetID-read-before-request-clear order, twooperandASL high<<1. Root fullbody review and allocator/reject/accepted mutation host fixture passed; childcuts and hostMPYDUmodel remain. Selected for next coherent target, no hardware/native-runtimeclaim.

## 31a434 corrected event/schedule provider selected

Large preparation31a700 coherent target passed; source snapshots current/stable. Fullnative31a434 review corrected scaledhalfword offsets266/262, low16repeat MPYUW, and event60store-before-sharedloads. Frozen hostallocation/copy-mutation/retry fixture passed; children cut and hostMPYWHLmodel explicit. Source now selected for next coherent target.

## Dispatch and finish source integration

Event/schedule31a434 target passed with initializer snapshots stable/current. Frozen316704 fullnative review corrected packet-check input to captured event+4 (not copierreturn); fourbounded hostroutes pass. Finish325eb4 fullnative review and allocationfailure/success fixture pass. Both selected for next target, genuinepacket children remain imports. No nativeARC/hardwareclaim. Secondary32d138 canonical child signatures still being reconciled beforeselection.

## Prepared packet copy ISA review gate

Root32dd54 fullreview required firsthighwordstore in secondpacker BLdelay beforecall. NamedMACU/MACDU added to preparedsource; rootrejected input-only MACU destination constraint because modifiedoperand reusedbyC. Worker correction pending; packetcopy notselected. Packetpredicate32e278 fullreview/frozenhostmatrixpass.

## Secondary transition and packet predicate selected

Dispatch/finish target passed with stable current initializer source snapshots. Canonical secondary32d138 childsignatures independently reviewed:316e74 and321820 ignore incomingR0;321e14 uses slotR0 only. Encoderdestination805fbc corrected. Frozenhostfixtures PASS. Packetpredicate32e278 fullnativeunsignedbranches/readorder reviewed and matrixfixture PASS. Three providers selected for coherenttarget; trueencoder/commit/copierchildren remainopen. No nativeARC/hardwareclaim.

## Packet copier, encoder, and channel compactor selected

Secondary/predicate targetpassed with current stable initializer snapshots. Frozen32dd54/32e164 host64cases each passed after fullnative review: firsthighstore-before-secondpacker, correct namedMACU/MACDU scratch outputs/accumulator/memoryclobbers. Hostmodels explicitly notnativeARCproof. Channel324c68/shift3027f4 fullnative review corrected helperreturn to64bits; host128shifts+256masks PASS. Three units selected for next coherenttarget; sourcechildcommit321e14 stillgenuineopen.

## Scheduler children integration

Packet/encoder/channel coherenttarget passed with stablecurrent initializer snapshots. Time317ebc fullnative review and4352corrected hostarithmetic/gatecases pass; pinnedMPYWHL primarymanual proveslow32, earlierhigh32model withdrawn. Schedule318ad8 fourboundedbranches and current303f5c256livehalfwordcases pass afterfullnative review. Threeunits selected. Selected31a434 namedMPYWHL nowdeclaresaccumulatorR58/R59andmemoryclobbers; no hostbehaviorchange. No nativeARC/hardwareclaim.

## Transition table exact fields and callback review

Root independent bytecomparison matchedfourcallbacktables andthreestatebytetables againstauthenticatednativebinary, hashboundreceiptinit-rom-tables-reviewed/native-field-receipt.json. Rootfullnativeleafreview rejected316894 storeaddress: STB.AB storesold8052fd thenpostincrementsR0to805300 fornotify. Preparedsourcewrotenewaddress; correctionpending. Namednativeeventframe30e988 ambienttail requirespreservation. Remainingleafcallbackbodies staticallyreviewed; notselecteduntildisjointunit/fixturescorrected.

## Remaining transition table callbacks and semantic tables selected

Schedulerchildren target passed with source snapshots stable/current. Root16callback fullnative review corrected316894 postincrementstore old8052fd/passnew805300; frozenhostfixture connectsactualselectedcountergate/twoexistingcallbacks andpasses. Native30e988 named12Bframe preservesambienttail; hostonlyinitialized6bytes checked. Sevenpreparedtables exactfieldcomparednativehash andsourceidentityrelocations preserved. Threeunits selectednextcoherenttarget; no rawcodeaddressesandnoreplacementstubs. This selectsall22distincttransitiontablecallbackidentities but children/placement/fullimagegates remain.

## Full commit321e14 review gate

RootfullnativeCFG review found LP_COUNT15vsdraft16, native savedobjectrecord+48 vsgetterhalfword return, MOV.NC=HS zero conditionreversed at321fe2/322014, freshrecord252reload at321fd2, and exactread/storeordering defects. Draftremainsunselected. NativeDIVU321f46/64 destinationR0isnumerator andzerodivisorretainsit; correctedreadwriteinitializedconstraint verifiedstatically. Fullsource/fixturecorrectionpending; noadmissionfrommodeledtwopathpass.

## Transition callback target completion

All22distinct callbackidentities infourtransitiontables nowselectedandtargetcompiled. Coherentem-transition-all-table-callbacks-round PASS, allinitializer snapshotsstable/current. Semanticcallback/state tables exactnativefield receipts bound. Fullimage notcomplete; genuinechildstart327b60/commit321e14 andremaininginitializer imports, relocation/placement/runtime gates remain.

## Start327b60 independent review correction

Rootfullnative review withdrawsprior lowaddressflagreadclaim: 327cf4 BLdelay savesINPUT root+2 intoR22 before323c78, while return12 goesR21. Nativeflagsread/write therefore root+172, not12+170. Preparedpointermapping rejected. Also root216idwrite isunconditionalbranchdelay at327d3e, modefreshreloadedafterencoder327d2c, andcallbackwriteorder44/40/28 mustpreserve. Draftunselectedpendingcorrectionandmutationfixture.

## Large commit/start providers and shared interval data selected

Fullnative321e14 CFG review corrections include15LPstores, trueobjectrecord48, low16unsignedMPYUW, unsignedHSzero gates, DIVUzerodestinationretention, freshperiod/halfwordloads andmissing276store. Frozenhost3mutation/edgepathswithUBSan passed. Fullnative327b60 review correctscapturedINPUTroot2, alignedroot172flags, unconditional216store, freshmodeafterencoder andcallbackstoreorder44/40/28; frozen7hostrouteswithUBSan passed afteralignment-safetest sentinel. Genuinechildren remaincut/imports. Canonical16B3357d0 table exactnativefields, existing317ea4 reboundshareddata. Threeunitsselectednexttarget; no nativeARC/hardwareclaim.

## Large commit/start target and comparator selection

Large commit/start round passes ARC compilation: 1442 definitions, 97 unresolved imports, zero duplicate strong symbols. All 101 initializer snapshots stable and current. Comparator 3249e8 full native body reviewed and selected with named DSP accumulator sequence. Host fallback proves ordered decisions only; late DSP numerical equality remains unverified without native ARC execution. Full image remains incomplete.

## Comparator compiled; next start-child group selected

Comparator round passes ARC compilation: 1443 definitions, 96 unresolved symbols, zero duplicate strong symbols. Initializer snapshots independently stable/current. Frozen comparator host fixture passes six decision routes with UBSan; scaled DSP numerical runtime remains unverified. Full native records 3239b8/323c78 and tail branch 3243dc reviewed; full stage bodies 318290/318348 corrected for unconditional branch-delay byte store and captured versus reloaded output values. Frozen child-cut host fixtures pass three record routes and eighteen stage cases with UBSan. Native random30c478 is a single tail branch to the existing selected pal_random_step provider; start source now calls that canonical identity. These sources are selected and a new target build is pending.

## Stages/records target completed; callbacks selected

Transition stages/records target passes: 1448 definitions, 90 unresolved symbols, zero duplicate strong symbols, all initializer source snapshots stable/current. Full-native reviewed callbacks318b38/328018/32805c selected after preserving genuine R0 returns; frozen UBSan fixtures pass. Native317afc exact named BMSK/XBFU/ADD sequence selected, host formula independently follows pinned GCC ARC zero-extract descriptor encoding; 1025 worker fixture values pass root rerun. New target callbacks/random build pending. Full327de8 process and scheduling3130d4 are next source gaps.

Start callbacks/random round target PASS: 1452 definitions, 88 unresolved imports, zero duplicates; all 107 initializer snapshots independently stable/current. This completes these full native-contract source groups as target-compilable C, not full image or runtime qualification.

## Latest scheduler full-body selection

Full3130d4 native control flow reviewed and corrected: advance occurs before reading the next node, limits follow the current link, rejection paths advance, and post-store link reads stay fresh. Frozen root UBSan fixture passes seven routes including traversal and live limit mutation. Source selected; target em-latest-scheduler-round pending. Full327de8 process draft remains unselected while retry, carry condition, mode1 return and captured-time corrections are reviewed.

## Latest scheduler compiled; full process selected

Scheduler target passes1453 definitions/88 imports/zero duplicates, initializer snapshots stable/current. Full327de8 process independently reviewed and corrected for mode0 scheduling, random retries, captured original remaining, scheduler success bit, unsigned carry condition, mode1 native return and exact captured-time/volatile-read order. Frozen root UBSan fixture passes12 bounded routes, with genuine child cuts. Full process selected for target compile; no native ARC runtime or hardware equivalence claimed.

Full327de8 process target passes: 1454 definitions, 87 genuine unresolved imports, zero duplicate strong symbols. All 109 initializer snapshots stable/current at independent review. Full native-contract source group is target-compilable; no native ARC runtime or hardware qualification claimed.

## Five registered wrappers and first radio callback target completed

Target em-registered-five-radio-callback-round passes1460 definitions/81 genuine imports/zero duplicates, all115 initializer snapshots stable/current. Five registered wrapper bodies full native reviewed; broadcast selector reload and post-cancel callback reload corrected before selection. Root3041e0 fullbody provider passes256 child-cut host cases. The other radio callbacks304214/30425c/3042b4 fullnative reviewed, host UBSan4/2/24 routes pass, and typed entry declarations selected. Callback325474 uses named168-byte ARC stack entry to preserve ambient mode3 frame; key adapters30ff70/30ffbc selected after correcting first-word volatile byte-store order. Resident curve calls1081e8/108178 remain genuine imports; mocked curve fixture does not prove resident behavior. New em-radio-callbacks-key-modes-round target pending.

Radio/keymode target passes1467 definitions/80 imports/zero duplicates, all120initializer snapshots stable/current at review. One extra import was root naming error radio_request_30fc68; actual same-address full provider already selected as radio_record_request_30fc68. Source and fixture rebound directly; UBSan2routes pass again. New canonical-request target pending. Existing receipt is historical after this correction; no duplicate provider added. Residentcurve108178/1081e8 genuineexternal contracts remain.

### Canonical radio request binding settled

`em-radio-canonical-request-round` passes with 1467 definitions,79 unresolved imports and zero duplicate strong symbols. All120 initializer compilation snapshots are independently hash-current and stable. The30425c request calls the existing full native30fc68 provider under its canonical source identity. Complete image acceptance remains open.

### Full3044e8 callback admitted for target compilation

Independent full instruction review corrected the old-address STB.AB store, replacement-before-old reads, two post-prepare owner reads and live R0-R4 indirect call. The corrected full source is selected; worker strict ARC compilation and five host UBSan routes pass. Numerical/native ARC execution and hardware remain unproved. Coherent target receipt pending.

### Full radio callbacks and packet constructors

Full3043ac/304430 coherent target compilation passes (1470 definitions,76 imports,zero duplicates;122 stable hash-current snapshots). Two complete packet constructors32613c/3263ec are now selected after independent full native instruction review. Corrected native DIVU destination priors and separate MOV/period-load ordering are preserved in named ARC instruction blocks. Prepared strict target and host fixtures pass; host numerical model is non-radix2 only. Coherent target receipt pending; physical divider configuration/runtime/image qualification remains open.

### Full packet constructors settled

Both constructor sources compile in a coherent target round; exact counts are recorded in progress-20261012.json. All124 compilation snapshots independently hash-current and stable. Two more complete native callback bodies306cbc/31ce10 are selected for the next round after513 host UBSan cases covering all256 flag values, all256 loop counts and null lookup. NativeARC execution/resident behavior and final image qualification remain open.

### Record/loop callbacks settled; next full units selected

`em-generic-record-loop-callbacks-round` target passes with1474 definitions,72 unresolved imports,zero duplicates and125 stable current initializer snapshots. Next selected units provide full32922c/32a218/32ae3c call chains, full3246c0/3246dc four-slot loops reusing existing32468c/324698 bodies, and full32c148 named stack-frame queue handler. Three chain routes and32four-slot masks pass focused host fixtures. The stack-frame handler strictARC object uses baseline32-bit LD rather than an unqualified alternateCD2compactencoding; no byte equality claimed. Coherent target receipt pending.

## Root associated callback admission, 2026-10-12

Settled generic chains/four-slot round: 1480 definitions, 68 unresolved imports, zero duplicates; 128 stable current initializer snapshots. Selected full32c254 named stack-frame unit and independently reviewed four associated units (32b618,32b82c,32b9a4,30e858) for the next coherent build. Parent32b61c remains unselected because optional callback ambient R2 is not justified by its two-argument C draft. Six callback and four start host routes cover bounded child-cut behavior, not native ARC numeric or hardware equivalence.

## Associated four and queue-frame round settled

Full ARC build:1485 definitions,67 genuine imports,0duplicates;133stable current initializer snapshots independently checked. The four reviewed associated bodies and full32c254frame compile together. Parent32b61c ambientR2 gate remains open. Next selected full32bc6c typed callback and322178tail thunk; native callbackconsumer318ce0 explicitly supplies R1packet. Tail preserves incoming registers and delay-store ordering; child32233c remains genuine unresolved.

## 312be4 signed-halfword duration correction

Independent full-native review at312c3c/312c4c found selected uint16 child arguments lost EXTH_S sign extension. Corrected both to sign-extended32-bit arguments. Local Clang UBSan compiled regression passes12 nonzero-divisor instruction-model cases; original source mismatches6, corrected matches12. This is host model evidence, not native ARC execution; generic zero-divider ambient destination remains open. Interrupted callback build94008 has no process/receipt and will be replaced by a new coherent build including this fix.

## Complete native duration ABI pair prepared

Named ISA C units for312b88 and312be4 compile and link at isolated native addresses. Entire44-byte piece and120-byte duration bodies match authenticated stock, including three canonical child relocations. This preserves native live-register contracts, signed EXTH and ambient DIVU R11 destination. Both await replacing canonical ordinary C definitions after active coherent build; no full-image/native-execution/hardware proof inferred.

## Guard and quantizer native ABI units prepared

Full303f80 and312c5c named ISA C units strict target compile and independently full-native effect review pass. Source sizes14/70 vsnative12/68 due baseline LD/ADD replacing assembler-selected unprovedCD2 compact forms. Guard preserves R1..R12; quantizer preserves R4..R12 and native branch-specific R1/R2/R3. Both await canonical replacement after active build; no byte equality/native execution/hardware claim.
