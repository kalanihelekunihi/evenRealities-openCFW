# CASE and Touch C completion pass

## CASE

`full_command_candidate.c` composes the previously compared 254 legacy routes
with the `0xee` standby prefix and `0xff` reset sequence. It also composes the
binary route table with `0x06`/`0x41` acknowledgement and one-byte legacy
handoff. Thus every opcode byte reaches a C body in this **candidate**. The
new routing layer passed 65,792 native stub cases (256 legacy plus 256×256
binary opcode/destination pairs). This checks routing, not stock semantics.

All 108 C files in `legacy_default_candidate_20261010` compile for Cortex-M0+.
The deterministic relocatable candidate archive and exact unresolved symbol
list are in `case-build-receipt.json`. The stand-alone archive has the imports listed in its current receipt;
many are named aliases to selected CASE lower
providers, but their return ABI and hardware behavior have not been bound.
The standby guard, secondary sensor read, PMIC write, flash apply, and
primary sensor transaction have C bodies. Bus, scheduler, reader,
and legacy frame contracts have additional C bodies. Live hardware behavior remains
unproved. The candidate is not
selected into the production archive and does not establish byte equality.

`binary_event_aliases_candidate.c` binds three exact stock-address event
forwarding aliases to the selected source provider with matching two-word
inputs and 32-bit return. Event-group effects remain its lower contract.
`logger_aliases_candidate.c` binds ten formatter aliases to the selected
`g2_log_printf` with ARM variadic tail branches that preserve arguments and
return. `legacy_shared_aliases_candidate.c` binds four exact-address flash
and sensor children already sourced in the binary graph. External flash
values remain runtime data. A source-owned ARM EABI byte-copy helper closes
`__aeabi_memcpy`. The formatter now uses source-owned 32-bit-limb radix
division, so the combined link needs no prebuilt arithmetic runtime.
Ignored-return GPIO, send, ACK and hex aliases use the selected void ABI.
Two busy-delay functions and the two runtime-selector sensor line helpers
now have C bodies. Their stock/source oracles pass 7 delay cases and 18 line
helper cases, respectively. Volatile C loops do not prove physical timing.
The full flash apply body at stock `0x0800373c` now handles all three erase
attempts and both eight-byte program blocks, including every success/failure
exit. Its authenticated stock/source oracle passes 96 control-flow cases at
typed flash lower boundaries. Flash mode selection (`0x08002f46`) passes six
stock/source cases; flash unlock/lock MMIO helpers (`0x08004bf4` and
`0x08004b20`) pass eight. The latter oracle caught and corrected a return
polarity error in retained prose pseudocode. Actual flash controller behavior
and external identity bytes remain unproved.
The flash status wait, page erase and doubleword program wrappers now have
C bodies. The program wrapper passes 18 authenticated original/source cases at
its physical leaves. The full sensor read transaction (`0x080028b4`) now
composes start, address, ACK, byte output and input, pulse, and stop; 48
authenticated original/source cases match lower-call traces, output bytes,
selector reset and return at controlled lower boundaries. Six serial transport helpers also have C bodies and match 120 original/source
call-trace cases at GPIO and delay cuts. The sensor sample reads the selected
bit of live GPIO at `0x50000410`; 15 original/source cases match selector
and register combinations. Physical sensor response and timing remain
product contracts. The second sensor transport (`0x0800292c`) and PMIC write transport
(`0x08002a00`) also have full C bodies, passing 23 stock/source cases at
serial lower cuts. Their guarded wrappers pass 30 cases. The serial-number
flash update at `0x08003664` passes 64 cases at flash lower cuts. Three
flash register leaves pass 108 direct cases, the controller snapshot passes
100, and the 64-word copy passes 12. The task cancel control body passes
18 cases at scheduler cuts. The 0x0610 output transaction passes 45 cases
at six named bus lowers; the AA/AB report loops pass 12 cases at reader and
logger cuts. The next reduction pass sources the bus parity, bit sender, AA reader,
waveform composition, poll wrapper, input transaction, sample byte, three
pin leaves, GPIO configuration and output preamble. Direct stock/source
oracles pass 259 parity, 18 bit sender, 24 AA reader, 9 waveform, 30 input
transaction, 20 byte sampling, 36 pin leaf, 96 GPIO config and three
output preamble cases. The watchdog frame body and retrying frame writer
pass four and 36 cases; caller instructions establish a stack-byte pointer
in R2. Task lookup and queue routing pass 64 cases at kernel lower cuts.
The flash elapsed-tick wait (`0x08004958`) now calls the selected tick-word
source. Six authenticated stock/source cases cover delay offset, wraparound,
and the all-ones sentinel. Its scheduler/tick progression is still a runtime
contract.

The stock queue post and send paths at `0x0800c7a8` and `0x0800c686`
now have full C control-flow candidates, with 22 original/source fast-path cases
matching at scheduler cuts. Their timeout and task-list paths need broader
comparison. IRQ save/restore, SCB yield, queue fullness, timeout snapshot
and accounting, scheduler suspend, ring copy, and deferred queue unlock also
have C bodies. Ring copy passes 24 direct original/source cases across item
widths, insertion modes, and occupied counts at the mutex lower cut. It
opens the real mutex priority-inheritance lower.
The scheduler list remove, tail insert and ordered insert now have source
bodies and pass 12 direct original/source comparisons. Queue wake and mutex
priority release pass eight and four cases at list lower cuts. Scheduler resume
passes eight idle cases. Queue wait, task delay and tick update also have C
bodies; timed wake and overflow behavior still need broader direct comparison.
The fixed stock fault sequence, CPSID followed by a self-branch, is now
source-owned for invalid queue/mutex conditions and critical-section underflow.
The candidate emits the same four instruction bytes at two source entries;
ten fixed stock trap sites match, and bounded Cortex-M0 execution confirms
masked interrupts and a stable self-branch. The combined relocatable graph
therefore has zero undefined symbols. This is source graph progress, not a
complete scheduler or physical proof.

`vformat_candidate.c` now exports `case_vformat` in the candidate archive. It
implements the evidenced flag, width, precision, length and conversion grammar
over the ARM word stream, including callback output and `%n` writes. The
authenticated stock/candidate Unicorn comparison passes 180 bounded cases,
including dynamic width, strings, signed and 64-bit numbers, `%p`, and `%n`.
It found stock-specific rules used in the source: `%p` emits eight hexadecimal
digits without `0x`, and `%#x` suppresses the prefix for zero. The comparison
uses a nontrivial callback return and confirms it is ignored in these cases.
The implementation and test
are not a complete formatter-domain proof: null or invalid string pointers,
overflow, all length/conversion combinations, callback failure behavior, and
the full caller-format corpus remain untested. Twenty
five distinct literal or static format strings in the corpus come from
retained CASE source. This is not a complete stock caller-format inventory.

`build_full_experiment.py --output PATH` verifies the selected archive hash,
rebuilds the command candidate, then twice links both archives without a
prebuilt numerical runtime into a relocatable object. It writes a sibling JSON
receipt with the SHA and unresolved symbol list. The current combined graph has **zero
undefined symbols**. Run from the repository root:

For the distinct command candidate archive alone, use:

```sh
python3 g2/analysis/c-source-completion-20261011/m0/build_case_candidate.py \
  --output /absolute/path/libcase_command_candidate.a
```

Its sibling `.a.receipt.json` records source, object, header, compiler and
archiver hashes, flags, provided symbols and its current unresolved imports. The
candidate archive rebuild is deterministic; inspect its current SHA in the
receipt because the source graph advanced after the prior two-path check.

For the combined experiment, run:

```sh
python3 g2/analysis/c-source-completion-20261011/m0/build_full_experiment.py \
  --output g2/analysis/c-source-completion-20261011/m0/case_full_experiment.o
```

The existing binary dispatcher passes its 65,536-pair route matrix. Using
`/tmp/iar-c-runtime-venv/bin/python`, the linked 254 legacy original/source
oracle reran successfully with 2,540 cases. The linked binary no-lower and
local-four oracles also pass 5,370 and 480 cases. The new full composition
still lacks a full-handler original/source oracle.

### Whole-body and image ownership

`audit_case_body_crosswalk.py` enumerates 426 fixed-image pseudocode entry
addresses and scans only the header/provenance area of 29 selected and 108
candidate C sources. `case-body-crosswalk.json` records 122 entry addresses
with a source header lead and 304 without one. A header address can name a
child or branch, and a missing lead can still have a source body under a
different name; these counts do not measure completed bodies. Every row
needs an explicit entry-to-C mapping and an appropriate comparison before a
whole-body claim. The archive candidate also lacks a source-owned startup
vector/reset path, initialized data and final linker layout crosswalk. A
separate startup candidate now declares all 46 vector slots and implements
the reset, initial stack setup, CRT decode and zeroing routines. Its isolated
link passes 46 vector-slot checks; the bounded startup oracle matches two
stock boundary calls and all 11,400 RAM bytes initialized by the two startup
descriptors. The 104 compressed source bytes remain an explicit product-data
contract. Native NMI/hard-fault loops and four vector forwarding bodies are
also source-owned; forwarders pass four stock/source call-boundary checks.
The combined command/startup relocatable graph currently has 74 external data,
handler and application symbols, with no final
integrated linker layout. External
flash identity bytes, SRAM initialization, and physical peripheral effects
remain independent product evidence. The zero-import result therefore cannot certify a complete CASE image.
`WHOLE_IMAGE_GAPS.md` triages specific large no-header entries, including
application policy `0x08007214`, initialization `0x08002fc8`, and record scan
`0x08001e94`, and records the fixed vector/startup facts and next finite work.
The separate initialization C candidate now covers the full retained
`0x08002fc8` branch graph with typed product/peripheral/log contracts. Its
initial state setup passes eight stock/source cases, and the self-check retry
loop passes ten at sensor and delay cuts. One successful PMIC path matches
through the boost-set boundary. PMIC failure, secondary device and final
service paths still need full original/source qualification.
The record parser's `0x08001e94` header scan, CRC, and valid-frame branch graph now have C candidates. The prefix has 15 early-return comparisons; the dispatch passes 50 bounded original/source cases across 07/08/13/3e/46/58/59/5a/5b, including input clearing and state writes. Diagnostics and unknown-command forwarding use explicit contracts; full payload/message equivalence remains open. Source-owned lower aliases reuse the command graph's elapsed wait, hex output and frame send. The `0x3a30` sensor state preparation passes eight randomized stock/source RAM comparisons. A distinct experimental C control body for peripheral transfer `0x08005528` compiles and passes 28 immediate and three controlled-tick timeout stock/source cases comparing return and MMIO, plus three reconfiguration cases through the 0x08004f14 child boundary. The clock-plan child at `0x08004f14` now has an independent C body, including its descriptor setup, device register writes and priority routing. Its prescaler shift is derived from the retained STM32 HAL APB table; 320 randomized stock/source whole-return cases pass across all eight index values. Live hardware behavior remains open; its `0x08004f14` clock-plan child is a typed contract.

The application entry `0x0800a598` now has a distinct C control candidate covering boot subsystem order, option-byte decision, wake-source policy, `0x08002fc8` handoff, service starts and the native nonreturn loop. Eight prefix-call and 32 option/wake stock/source boundary cases pass. Five native flash option register operations are source-owned and pass 80 randomized MMIO comparisons. The full option reader/programmer, product messages, boot services and hardware resets remain typed contracts. The `0x08007200` policy task has an initial source-owned idle transition (20 stock/source RAM and R6 cases), the idle standby call sequence (two native cuts), and OTA side/box ready transitions (12 native cuts). These are scoped portions of the internal `0x08007214` loop; charging, event processing, no-reply recovery and loop composition remain open. Native inspection identifies `0x08007214` as an internal policy-loop body reached after the stack/context setup at `0x08007200`; its R4 state pointer and stack-derived left/right pointers need an explicit C context contract before whole-entry attribution.

Since that initial policy audit, source-owned scoped paths now also cover the
service gate (eight native cuts), box idle qualification (64), full-battery
standby (20), left/right fake-standby counters (96), and unchanged-service
maintenance (160), changed-status and charging-result decision (576), both no-reply retry/reset tracks (1,296), OTA probe control (256), shared-event and idle-standby gate (192), and the terminal reset decision (16). The probe payload has a typed 12-byte product-data contract and has not been byte-qualified. The portions retain the live R4 state, R5/R6 counters and
left/right stack pointers from `0x08007200`. These are bounded observations;
the cross-branch task composition and real product lower/data bindings require
separate qualification.

The fake-standby state lower bodies at `0x08003a00` and `0x080013b8` now
compile in the combined graph. Their native/source oracle compares 256
randomized set mutations and 96 clear mutations including three task-cancel
arguments and conditional diagnostic calls. The full two-side sensor service
update at `0x0800ce34` now has a C body and passes 128 controlled native/source
call-trace and RAM comparisons. These controlled oracles do not prove physical
measurements or the CASE whole image.
The `0x0800d250` eight-byte sensor snapshot is now source-owned and passes
128 randomized native/source RAM cases. The measurement child at `0x08002edc`,
unsigned divider at `0x08000160`, delay guard at `0x0800a7b0`, and task cancel
guard at `0x0800aa00` are source-owned; bounded comparisons pass 80 sample,
128 divider, 64 delay, and 64 cancel cases. The existing `0x08009a14`
idle-clear body is reused directly by service update. ADC hardware children,
scheduler sleep/cancel and bus writes remain real source contracts.
The ADC front-end at `0x08004328`, `0x08004710`, `0x080047d4`, and
`0x0800483c` is now C source, with 80 controlled native/source cases per body
comparing return, calls, handle RAM and ADC register effects. The scheduler
sleep body at `0x0800c128` and cancel core at `0x0800c228` are source-owned;
96 controlled cases per body compare return, call sequence and scheduler RAM.
Their newly exposed ADC configuration, clock, scheduler queue and lock children
remain typed external contracts; these tests do not prove hardware or full
scheduler operation.
The ADC `0x08004eac` tick and `0x0800678a`/`0x08006792` register predicates
now pass 128 original/source cases each. Full ADC open/close configuration
at `0x080007a8`, `0x080006d4`, and `0x08000734` passes 80 controlled register,
handle and return cases each. Scheduler lock/unlock, PendSV request and sleep
entry pass 64 cases each; task-valid and sleep enqueue pass 96 each. The
`0x0800ca78` tick and `0x0800cc0c` sleep-exit bodies pass 96 no-wake cases
each. Sorted/unsorted queue insertion, unlink, and wake deadline C bodies are
source-owned; 192 multi-insert/unlink and 128 wake-deadline comparisons pass.
The residual
external graph remains explicit, including product bytes and hardware effects.
Native task-notify `0x0800aa24`, scheduler start `0x0800a900`, notify core
`0x0800c2f8`, and activation `0x0800c284` now have C bodies; 96 wrapper cases
per body and 80 controlled core cases per body pass. Activation exposes the
idle task entry/name and task-creation/ready/run contracts, rather than
assuming an executable address from stock is a source binding.
The scheduler ready-queue dispatcher at `0x0800c390` now passes 96 valid-list
native/source RAM comparisons. The nonreturning `0x0800ae5c` idle task loop is
source-owned. Its `0x0800ace4` maintenance body passes 80 controlled cleanup
comparisons and exposes the task-reclaim child. Scheduler-ready `0x0800cd20`
and scheduler-initialize `0x0800ac84` pass 64 controlled cases each, including
list setup, task creation arguments and state writes. Scheduler-run
`0x0800c57c` and SysTick setup `0x0800c078` pass 96 MMIO/state/call comparisons.
The architectural first PSP handoff `0x080000cc` passes 32 register/stack
comparisons with a synthetic task frame. Task creation, reclaim and pool
management still require source bodies and linker memory ownership.
The task-creation wrapper at `0x0800ca06` now has a C body that passes 96
native/source ABI, storage and return comparisons. It exposes the actual
`0x0800ae96` task-frame initializer and `0x0800ac08` registration body as
separate source obligations; neither is replaced by a synthetic task pointer.
The task-frame initializer `0x0800ae96`, its fill/link reset/frame descendants,
and the return fault policy now compile from C. Ninety-six native/source full
task-frame RAM cases pass after normalizing only the return-handler symbol
address across the two link layouts. Task registration `0x0800ac08` passes 128
bounded scheduler/call comparisons; first task list preparation, scheduler
registry and deferred task reclamation pass 48 cases each. Heap free and pool
allocation remain typed platform lower contracts, with exact allocation
ownership and linker memory still open.
The pool-create `0x0800c5d0` and heap-free `0x0800c030` bodies pass 96
controlled native/source cases each. Their descendants, pool setup
`0x0800ae74`, free-list coalescing `0x0800afcc`, and pool reset `0x0800c616`,
now have C bodies and pass 96 cases each across sampled register, memory and
list states. Waiter wake `0x0800cba0` remains a true scheduler lower contract;
heap construction, owned RAM region and physical memory behavior remain open.

An experimental `0x08007200` task entry and `0x08007214` iteration now compose
the retained policy portions with explicit R4 state, R5/R6 counters and two
stack-derived lens pointers. One hundred twenty-eight native/source cases
match from `0x08007214` to the `0x08007ed6` loop edge across idle/nonidle and
box mode states, comparing calls, state bytes and R5/R6. The two changed-sensor
refresh lower bodies at `0x08003a3c` and `0x08003a60` now have C equivalents:
160 randomized RAM/register cases match the original, and 32 changed-service
whole-iteration cases match through the loop edge while the physical service
update remains a typed test hook. This is C control reduction, not proof of
all service, product-data or hardware paths.

The post-service portions are now composed from `0x08007884` through the
`0x08007ed6` loop edge. Thirty-two contiguous native/source cases pass when
the OTA probe and event paths are inactive. This proves that branch and its
calls/state, not all post-service combinations. The `0x08007200` entry now has
a compilable experimental C candidate, but broad whole-entry validation and
product sensor effects remain open.

## Touch

The four reset layout sources compile and relocatably link for Cortex-M0+ with
zero undefined symbols. This confirms C syntax/object compatibility, not a
complete Touch image. The retained Touch build has 45/45 selected C units and
eight provider objects. The initialized reset copy payload has 25/964
source-owned bytes; 939 bytes have no source declaration, value provenance,
or original relocation proof. The smallest external source input is the
product `.cycapsense` or generated `cycfg_capsense.c/.h` and final link map.
Absent those, each missing field needs independent source/relocation proof.
The reset call at `0x3464`, absolute layout and hardware behavior remain open.

## Completion flags

| Component | C candidate routing/units | Production source complete | Byte equal | Physical proof |
| --- | --- | --- | --- | --- |
| CASE | command graph: all opcode routes plus formatter compiled, zero imports; distinct command+startup graph: 74 imports | no | no | no |
| Touch | 45/45 retained units; reset layout sources compile | no, 939 reset bytes open | no | no |

The remaining CASE work is measured by a full accepted-frame original/source oracle, formatter
domain completion, and external flash and hardware effect proof. The selected frame dispatcher declares handlers void and discards their
return register. Experimental ARM tail aliases preserve residual R0 on direct
entry without inventing a success value; direct-entry ABI proof remains open. `remaining_contracts.json` lists every remaining import,
its known stock address, and the precise missing source or product contract.
Touch product source remains absent. Neither component has
a defensible calendar estimate.
# Combined CASE startup/application progress, 2026-10-11

The application bus and event round sources config read transaction `0x0310`,
motion read transaction `0x0420`, output sample/response `0xb5ac`/`0xa164`,
service startup `0xd178`, event clear/signal `0xa7d2`/`0xaaf0`, immediate
event routing `0xcd80`/`0xc7a8`, and ring message copy `0xad48`. Original/source
checks pass 96 config/motion transactions, 80 retry reads, 96 event wrapper
thread cases, 72 event dispatch cases (including native stack fifth argument),
80 immediate insertions, and 96 ring-copy cases. The config transaction
oracle caught a third parity byte error, corrected to `(command<<1)+1`.
The event route's fifth stack argument is the packet operation word and is
now explicit in C. Current combined graph SHA-256 is
`c3c9a95b2e0b04a4a8316df960fc210507c880b36b24a06f58b16e4c2557d845`
with 45 imports: policy 19, boot 16, vector five, IRQ four, CRT data one.
There are further scheduler descendants, full boot/IRQ bodies, product data,
and linker layout still to reconstruct.

Initialization source round: product measurement `0x9ebc`, PMIC power gates
`0x2c30`/`0x2c8e`, register writes and guarded transactions, probe/config
status and repair `0x9df4`/`0x9ef8`/`0x9f80`/`0xa046`/`0x9e0c`, and
reset/LED/sensor-finish paths `0x502c`/`0x38a0`/`0x2b40`/`0x35f0` now have
C bodies. Comparisons pass 96 product cases, 120 power call traces, 96 PMIC
write transactions, 64 probe/status cases, 24 repair cases (including
multi-poll status), and the three finishing call sequences. The native
two-byte register write ABI at initialization call `0x3112` required both
arguments (`0x14`, `0x14`); the C caller now passes both. The PMIC expected
80-byte configuration still comes from RAM `0x2000002a`, whose CRT/product
initialization remains open. Current combined SHA-256 is
`602447be75bd7ef93f4b59a031d042ef5d6af8fd9611dd4029210f535b399226`
with 58 genuine imports: policy 25, boot 16, initialization six, vector five,
IRQ four, CRT data one, record log one.

All seven exposed PMIC bus primitives now have C bodies at native
`0xa3d2` through `0xa4fa`. They use the authenticated `0x50000400` GPIO
set/clear/input registers and `0x20000114` pin selection. A 112-case
original/source comparison passes for GPIO write traces and sampled return
values across both pin selections. This checks register sequence, not
electrical timing or live device behavior. The combined graph now builds at
SHA-256 `ba1a84583a3515123bc6066ddd0cb7452e126e8a01721dc4a474209f21ec2b55`
with 68 genuine imports: 25 policy, 16 initialization, 16 boot, five vector,
four IRQ, one CRT data, and one record log.

The next source round adds native event peek `0xa816`, queue receive
`0xc44c`/`0xc4cc`, elapsed conversion `0xa01e`, timer query `0xa074`, guarded
bus read `0xa130`, busy delay `0xa148`, both PMIC transaction readers
`0x28b4`/`0x292c`, and their guarded initialization entries
`0x35b8`/`0x35d4`. Original/source bounded comparisons pass 80 event
thread-mode cases, 96 timer cases at bus/delay cuts, and 96 transaction
cases at physical bus cuts. The combined graph builds at SHA-256
`78062a619a56e70dfc70d6ced1ecf1962111c2c4af5a7eb32322ac234f195526`
with 75 genuine imports: 25 policy, 16 initialization, 16 boot, seven newly
exposed physical PMIC bus operations, five vector, four IRQ, one CRT data,
and one record log. The increased import count exposes actual lower hardware
obligations; it does not imply lost body coverage. Physical PMIC bus timing and
product memory layout remain unvalidated.

The experimental command plus startup/application relocatable graph currently
builds with 72 genuine undefined symbols (SHA-256
`9756209c61c0de0819d9cc60a64ef15f5478b92a98ed94e1bedbfdedc4fd1114`).
The receipt is `case_command_startup_experiment.o.receipt.json`. Its imports
partition into 27 policy, 18 initialization, 16 boot, five vector, four IRQ,
one CRT data, and one record log. The command-only zero-import archive is a
separate graph and does not prove a complete CASE image. Linker-owned RAM and
flash layout, product data, vector composition, OTA template data, and physical
device behavior remain open.

Native pool waiter wake at `0x0800cba0` now has a C body. The bounded
original/source comparison passes 96 scheduler-mode and priority cases at the
list-operation child cuts. The policy delay import was reconciled with the
already sourced native `0x0800a7b0` body; policy callers discard its status.
This comparison does not validate physical scheduling or the full pool chain.

### Continued scheduler, policy, and boot C reduction (2026-10-11)

The task-context queue-send function at native `0xc686` now has a full C
control flow, including immediate copy, waiter wake, timeout snapshot, sleep,
cleanup, and retry. Its native child functions at `0xcb38`, `0xc15c`,
`0xc178`, `0xc948`, `0xb080`, `0xb374`, `0xc16c`, and `0xca4c` also have
source bodies. The `0xcb38` priority restoration oracle passes 96 native/source
cases. The queue-send body and its deeper wait paths compile but do not yet
have a whole-body execution comparison.

The periodic GPIO pulse path `0x2cb8` to `0xa270` passes 24 native/source
GPIO trace and state cases. Boot power GPIO setup `0x2888`, clock restore
`0x4eec` with fallback `0x4fb0`, wake arm `0x50e8`, service latch `0xa8d8`,
and logger alias `0x9170` are source-owned. Bus and sensor descriptor
initializers `0x6bb0` and `0x6c00` pass 10 native/source child-cut cases,
including injected error results. Boot option read `0x4a00` passes 96
native/source MMIO cases; option write `0x4a6c` passes 96 varied
control/selector/busy/wait cases at the `0x3f6c` wait cut. The wait child has
a source body. Boot bus open `0x5a74` passes 96 native/source cases at its
reset/prepare/apply cuts; bus start `0x5910` and frequency setup `0x598c`
pass 96 ready-path MMIO cases. The reset `0x5b24`, prepare `0x6d72`, apply
`0x6db8`, and apply core `0x5b8c` have source bodies. Policy refresh `0xbb74`,
task reset `0xab26`, and task active `0xcde4` have source bodies.

The cold-reset boot option selector at `0x20002c70` is in the CRT-zeroed RAM
range `[0x200001a4, 0x20002c88)`. Native reset sets SP to `0x20002c88`;
native entry subtracts 32 and passes SP+4 as option words, so words[1] is
at `0x20002c70`. Preceding boot calls use stack below entry SP
`0x20002c68`, preserving that zeroed selector. The source initializes only
this selector to zero for the cold-reset path; direct entry from an arbitrary
stack remains unqualified.

The latest strict command plus startup relocatable build is SHA-256
`822feb3a0e5e9dcde9132ab595d1a2201fc39efa26f45783796c163e076ee517`
with 38 genuine undefined symbols in its adjacent receipt. This is a C
source/build milestone, not full CASE image completion. Open work includes
remaining policy and boot descendants, IRQ/vector bodies, CRT product bytes,
linker-owned RAM/flash layout, OTA template data, and physical behavior.

## Continued CASE boot and sensor reduction

The current strict command plus startup relocatable build is SHA-256
`68bbb4076f2805870d48f4400469a0cd8ac6a74e700d97280d385d36ee36c38a`
with 35 genuine undefined symbols in its adjacent receipt. Sensor start,
clock, and mode bodies at `0x5e2e`, `0x5e6e`, and `0x5eb6` pass 96 native/source
cases at their commit child cut. The commit body `0x856c` passes 96
native/source descriptor cases. Its two timing tables at `0xd398` and
`0xd3a0` remain external product data. The bounded oracle reads stock table
bytes as a test fixture; the implementation does not embed them.

Input initialization `0x8438` and policy system configuration `0xb600` have
source bodies sharing the actual 56-byte transfer plan. Both pass native/source
comparison at their three child cuts. Their gate child `0x5048` has a C body
for the MMIO mask, timing divide, and readiness timeout. The sensor bind core
`0x8d98` has a C body for descriptor fields, limit selection, PRIMASK-protected
register changes, DMA branch, and callback selection. The four referenced
callback bodies remain genuine source contracts. Neither the gate child nor
bind core has a complete native execution oracle yet.

The four sensor callback bodies `0x8758`, `0x8998`, `0x8808`, and `0x8a48`
are now source-owned. The simple byte/halfword callbacks pass 96 native/source
buffer, descriptor, and MMIO comparisons at the finish child cut. The
streaming callbacks pass 96 further comparisons covering transfer, flag,
completion, and tail transitions. That oracle models the sample-ready flag
clearing after a sample read; the real peripheral is still unqualified. The
callbacks expose actual status `0x5f42` and finish `0x6544` child bodies.
The latest strict build is SHA-256
`39cbb98df0c49829c7f39d338da5f6b943983cb25a93d4f2b7408304a346c963`
with 33 genuine undefined symbols.

The streaming callback's status child `0x5f42` is an authenticated `BX LR`
leaf, represented directly in C. The streaming oracle still passes all 96
cases after compiler inlining. The latest strict build SHA-256 is
`8ff65bf14e78b7c4366f786cbaf4530f06bae0af1bff5c647277516a6752567d`
with 32 genuine undefined symbols. The remaining sensor callback descendant
is `0x6544`; sensor open and two timing tables also remain.

## Sensor open and finish parser continuation

Sensor open `0x6240` passes 96 native/source cases at its four child cuts.
Its initializer `0x6308` passes 96 two-base MMIO and clock/GPIO child-cut
cases; its field application `0x85b0` passes 96 register comparisons; and
its final readiness `0x867c` passes 96 cases with the authenticated fifth
stack argument `0x01ffffff` at child `0x8ec4`. IRQ enable `0x500c` is also
source-owned and included in the initializer comparison. Sensor validation
`0x8bd8`, readiness `0x8ec4`, and bus clock setup `0x5128` remain separate
native bodies.

The sensor finish callback parser `0x6544` is source-owned and passes 192
native/source state and child-call comparisons. It uses native RAM layout
addresses `0x20000108` for parser state, `0x20000974` for its buffer,
`0x20000e24` for the receiver, and `0x200000f0` for the task handle. Initial
contents and final linker placement still require product data/layout work.
Its synchronous transfer guard `0x63ec` passes 96 native/source cases at
the readiness child cut. Its two-byte probe `0xbe74`, parser reset `0xa358`,
and task/ISR notification dispatcher `0xa888` have C bodies. The notification
dispatcher passes 96 native/source cases including ISR wake and return paths.
The parser's remaining true children are readiness `0x8ec4` and scheduler
notification `0xc568`/`0xc4de`.

The latest strict command plus startup build SHA-256 is
`2458c26dad903eecde24ebffaa76578b57b682d95f39107f49cda374342d8acd`
with 34 genuine undefined symbols. This is source and bounded oracle progress,
not peripheral or full image equivalence.

Sensor readiness `0x8ec4` is now source-owned and passes 96 bounded native/source
cases covering immediate status return, timeout, and hardware error cleanup.
The infinite-timeout sentinel is preserved in source control flow; a live
peripheral transition under that sentinel is unverified. Sensor validation
`0x8bd8` passes 128 native/source cases across seven base-address classes,
clock choices, prescale choices, and register effects. Its clock source
functions `0x5474` and `0x549c` pass 192 native/source cases. The latest strict
build SHA-256 is
`3aee07077d635bb574c8f866be49921c355bb8f6804a0277795ddfae3123bb88`
with 34 genuine undefined symbols. Prescale and shift tables at `0xd380`
and `0xd3e8`, plus timing tables at `0xd398` and `0xd3a0`, remain product data
imports; test fixtures read those bytes from the pinned stock image.

The remaining 35 undefined symbols are genuine lower bodies or data/layout
contracts: boot bus clock/device setup, console and sensor open, four sensor
callbacks, transport/task creation, IRQ and vector handlers, OTA payload data,
CRT initial bytes, and policy IO/reset children. A zero-import command-only
subgraph does not establish full image coverage or device behavior.

### Scheduler notification, clock setup, and typed clock tables

Native CASE `0xc568` ISR notification forwarding and `0xc4de` task notification
waiter traversal are now C bodies. The ISR forwards to the existing `0xce0c`
event dispatcher; the task path uses the existing scheduler enter/exit sources
and the source-owned `0xc1cc` waiter-unblock body. These paths compile. The
task notification path passes 192 bounded original/C cases across empty
and one populated waiter, matching unblock calls, return value, and RAM state.
Full ISR dispatch and actual scheduler waiter effects remain to be qualified.

The retained STM32G0 HAL `UARTPrescTable` exactly gives the 12 typed halfwords
at `0xd380`. Retained ST `APBPrescTable` and `AHBPrescTable` definitions give
the native word-sized values at `0xd3e8` and `0xd3a8`, respectively. The two
timing tables at `0xd398` and `0xd3a0` have no attributable retained source and
remain explicit data contracts. This typed construction does not assert final
linker placement at those stock addresses.

Native `0x5128` bus clock setup and `0x52e4` clock device apply are now C
bodies with true MMIO branches and timeouts. Bounded original/C comparisons
pass 128 no-wait clock-setup cases and 96 no-wait clock-device cases, including
config fields and resulting MMIO/RAM state. Device clock transitions and timeout
behavior still need physical qualification. The current strict experimental
command plus startup build SHA-256 is
`077133f14b21870c1d68a9b3efdb91b62b650d686333242bd5a835b067b6a57a`
with 28 genuine undefined symbols. The receipt enumerates each unresolved
lower/data/vector contract; neither this count nor the bounded comparisons
prove a full CASE image.

### IRQ and scheduler vector continuation

The `0xc1cc` waiter unblock implementation was already present in the command
archive via `scheduler_list_candidate_20261010/unblock.c`; its coherent native/C
oracle passes 576 cases. A duplicate startup definition was removed after a
strict link exposed it. New source bodies cover IRQ child `0x5a52` (96 original/C
register-state cases), SysTick vector `0x8420` and tick wrapper `0xc5ac` (192
child-call/ICSR cases), IRQ clear `0x4d04` (128 MMIO cases), and PMIC IRQ vector
`0x3bc8` (96 branch and diagnostic call cases). The vector exposed true button
refresh child `0x3a84` as an import. The latest strict combined graph SHA-256 is
`187f18f49a17ff006b4163dfe2abca68cdaa90c360ebb038711cf88109893c0b`
with 26 genuine imports. IRQ children `0x4330`, `0x5c90`, `0x5f50`, vectors
`0x3c2c`/`0x3d24`, PendSV, remaining boot providers, product timing data,
CRT initial bytes, and final linker placement remain open.

Native `0x3a84` button/battery IRQ refresh and its `0x3a00` mode reset child
are now C bodies. The source preserves sampled value comparison, both logging
branches, RAM flags, mode resets, and guarded PMIC write. A bounded native/C
oracle passes 128 cases with real mode-reset code and cut sampler/logger/write
children. Its `0x9ebc` sampler was already source-owned as
`case_init_read_product_byte`, so the refresh now binds that existing body.
The strict graph has 25 imports. Latest SHA-256 is
`a7fcac93d3f62f0ecd36e8afd71bdd2c872539054669f58e06c8f00439870c14`.

### IRQ continuation through USB vector

The subsequent candidate graph source-reduces serial IRQ child `0x4330`, timer
IRQ child `0x5c90`, PendSV, hall IRQ vector `0x3c2c`, USB IRQ vector `0x3d24`,
hall preparation/state children `0x3848`/`0x2a5c`, and USB reset command child
`0x3656`. Original/C bounded comparisons pass 256 serial IRQ, 256 timer IRQ,
96 PendSV, 128 hall vector, 160 hall lower, and 128 USB vector cases. The
strict combined command plus startup source build passes with SHA-256
`ab3889b58d7c2bd826870219b3c246d27eb3c1512eba4e33bd44dc4844380f07`
and 20 genuine undefined contracts. Sensor IRQ child `0x5f50`, remaining boot
providers, product timing data, CRT initial bytes, and final linker placement
remain open. These bounded comparisons do not establish hardware behavior or
whole-image equality.

The full sensor IRQ dispatcher `0x5f50` is now C, with 512 bounded original/C
cases spanning status, enable, control, error, and transfer branch cuts. Its
restart children `0x487a`/`0x48e6` pass 192 original/C peripheral-state cases;
error recovery `0x86f4` passes 128; `0x6776` is a native BX LR leaf. The
pin initializer `0x6a40` also has a full C body and 64 original/C cases for
clock MMIO, GPIO arguments, and IRQ configuration calls. The latest strict
combined build SHA-256 is
`cf91400114a17e0663b59169f00e27116ca4ca20b95b956b1b132f7a2323b802`
with 18 genuine imports. Product data, remaining boot/policy bodies, CRT
initial bytes, and linker layout are still unresolved.

The console start routine `0x3fd0` is also source-owned as a C candidate.
The early occupied/ready paths pass 128 bounded original/C cases. Its sample
calibration and timeout paths still require a modeled ADC state transition
for direct stock comparison. The strict combined source build is
`26923f5c23c990d87a35d57df837e2b38efe3599f56333b1a51fd17f9f53723a`
with 17 genuine imports.

A modeled ADC calibration-bit transition now supports 64 more stock/C
console-start comparisons, passing with the 128 early-state cases. The
generic FreeRTOS task and queue names (`IDLE`, `TmrQ`, `Tmr Svc`) are C string
literals with exact native NUL-terminated bytes and sizes, reducing the strict
combined graph to 14 imports. Build SHA-256:
`4ed87bf3a6727d9b6fb7569a09d4d99ea636e83835b9453218a30cc4bb306ad3`.
`remaining_case_contracts_14.json` separates nine source-reducible bodies,
three product data sources, one ambient caller-stack ABI, and the CRT initial
data/layout contract. These unresolved contracts remain genuine; the census
does not claim full image completion.

### Later CASE transport and reset checkpoint

The distinct command-plus-startup graph now includes source C for the native
0x9a9c reset branch and children through GPIO/IRQ shutdown, the 0x6968
transport registration sequence, three transport callbacks, the 0x82ec
monitor, 0x1c1c action, 0xa836 event classifier and its storage helpers, and
0xb3e8/0xae0c heap allocation/setup. A strict relocatable build passes with
21 genuine imports and SHA-256
`28b692680ad979293eeb42cd6e2a2324711c9f6f04e0d41d7064f98fbf0ac5eb`.
The transport registration, callback, action, event and first-allocation
stock/C comparisons are recorded in the corresponding `verify_case_*` and
`verify_case_transport_*` scripts. The reset guard passes 192 branch cases;
the physical reset waveform is not dynamically qualified.

The refreshed startup-inclusive header-lead crosswalk covers 426 fixed
pseudocode entries: 255 have address leads and 171 do not. `WHOLE_IMAGE_GAPS.md`
classifies the 21 current imports as 13 C-body, six product-data, one ambient
ABI and one CRT-initial-data obligation. This is an import/census checkpoint,
not a complete-image or physical firmware claim.

The later heap/registration source pass compiles and links with 20 imports,
SHA-256 `4d158f42a291338151aa0ae2b14bb33129eeb16da159440f85978238635a8ea8`.
The 0xb3e8 first-allocation oracle passes 14 sizes; 0xaa48 registration
passes 384 storage/allocator cases; 0xaf30 task initialization passes 192.
Native literal 0x8559 is a callback trampoline and is now C source, not a
task-name data item. The startup-inclusive lead audit now reports 260
addresses with header leads and 166 without among 426 fixed entries.
`WHOLE_IMAGE_GAPS.md` retains the remaining 12 body, six product-data, one
ambient-ABI and one CRT data contracts, plus layout and physical limits.

The transport worker follow-on C pass adds the 0xa93c selector and
0xc9a8/0xca06 task creation children. Stock/C checks pass 384 selector,
192 dynamic creation and 96 existing static creation cases. The strict
relocatable graph builds with 19 imports, SHA-256
`ae88b8f59ee6f46e1d8bd34e2cfd91ca5eaf9b964f0b91a8f31d2b958fe969a9`.
The updated header-lead audit is 262/164 of 426 entries. Eleven code-body,
six data, one ambient-ABI and one CRT initial-data obligations remain, in
addition to full entry coverage, final layout and physical qualification.

The aging transport pass adds complete callback 0x9684 and refresh children
0x9bc0/0x9cc8. The strict combined relocatable graph builds at SHA-256
`903741d9748a448cb12d76a9e415358ed8d6ba1c3a5115a2d0f941567fcee2af`
with 19 unresolved imports: the callback and both children closed while
the true 0x1408 aging-status provider became visible. A bounded stock/C
0x9cc8 oracle passes 256 mode-four state and cut-call cases. 0x9bc0 and
0x9684 have source and compile evidence, but no complete dynamic oracle yet.
The header-lead crosswalk is now 265/161 of 426 fixed entries; its 161
no-lead rows need alias resolution and body evidence before any coverage
claim. Product data, CRT initialization, final layout and hardware behavior
remain open.

Native 0x1408 aging-status exchange is now C source. Its four protocol
requests use explicit command/side/state fields from the native immediate
packets at 0x1564/0x156c; no opaque firmware blob is embedded. A bounded
stock/C oracle passes 256 cases over availability, busy/quiet flags and
response combinations, comparing call order, packet bytes, return and RAM.
The corrected strict graph builds with 18 unresolved imports, SHA-256
`384bf960171b0dd869ceca183282659cdc6430aca227da1f06817f7dcc2b9851`.
The fixed pseudocode header-lead census is 266/160 of 426. Packet exchange
has source and bounded execution evidence; real transport, whole image data,
layout and physical effects remain unqualified.

The 0xb7ec aging entry/exit callback is now C source. A bounded stock/C
comparison passes 256 state and child-call cases; the native nonreturn reset
path was excluded from this dynamic corpus. The strict graph builds with
19 imports, SHA-256
`8eeae0381d3ba9cc3f039bd20aacaa4fdde6d1fdc438d72e92d60b70d8b86fe3`:
its 0xb7ec callback import closed and genuine 0x23f4/0x24c0 aging-control
children became visible. Native 0xb7ec is not present among the fixed
pseudocode's 426 function markers, so the 266/160 header-lead count did not
change. That census is not an exhaustive native-function inventory.

Native 0x23f4/0x24c0 aging controls are now C source with typed six-byte
command packets. Their symmetric original/source oracle passes 384 cases
over side, enable, present, busy/quiet and response, comparing packet bytes,
call sequence and RAM. The strict graph builds with 17 unresolved symbols,
SHA-256 `d7da8c1bd7af4c41c7ee921ea2639a88c1c42842ab8956b8089d4f5f2bc1e5e0`.
The fixed pseudocode header-lead audit is 268/158 of 426. Source/code
closure remains distinct from transport, product data, layout and hardware
qualification.

Native 0xbb90 transport inbox/charging confirmation callback is now C
source. Its bounded original/source oracle passes 768 state, timer and
quiet-log cases while cutting existing event/IRQ/log child calls. The
typed 0xd26c transport registry has six timer descriptors, four worker
descriptors and one event descriptor (276 bytes); an ELF/native comparison
matches every numeric field and all 11 task labels. The 0x1d04/0x1e4c
protocol command seeds are source-owned as 8- and 12-byte typed arrays;
their 20 bytes match native data exactly. The strict combined graph builds
with 13 imports, SHA-256
`46eb2d4556b4684e1a4402201eca241385de62ba359dbcfd08d4780564a8f359`.
Eight code bodies, three product-data contracts, one ambient ABI and one
CRT initializer remain in its reachable graph. The 426-entry fixed
pseudocode lead audit stays 268/158; native 0xbb90 is absent from that
catalogue.

The remaining reset configuration import at 0xd36c was an alias of the
transport event descriptor tail at 0xd26c+0x100, not distinct product data.
The reset C path now reads that typed source field, with a compile-time
offset check; its 192-case bounded guard oracle still passes. The two
eight-entry sensor divisor/rate tables at 0xd398/0xd3a0 now have typed C
source and exact 16-byte native data checks. The strict combined graph
builds with 10 imports, SHA-256
`74645a362c98e3aa5df02c9303f0670728edbc616ceb8f3560641e0124891626`:
eight genuine code bodies, one ambient ABI and one CRT initial-data payload.
This closes reachable product-data imports only; the whole image still needs
function inventory, all data/layout, and hardware qualification.


Native 0x258c probe/send and its exposed 0x6cf8/0x6c80 descriptor
reconfiguration, 0x3bb0 packet wrapper, and 0x66ac synchronous sensor
transfer now have C bodies. The 0x258c, reconfiguration, wrapper, and
transfer bounded original/source oracles pass 384, 256, 128, and 192 cases,
respectively. The 0x66ac comparison includes descriptor RAM, MMIO transmit
register, return code, and five-argument ready-child calls across byte,
halfword, invalid-state, and wait-failure cases. The native error/reset paths
of the reconfiguration helpers remain outside that dynamic corpus. The
strict combined graph builds with nine unresolved symbols, SHA-256
`62047d070f0338fb186f02c253fa75d8e84fd36699628087d7faf1e34d6de1d7`:
seven source code bodies (two console, two transport callbacks, box file
open, OTA transmit, service maintenance), one ambient selector ABI, and
one CRT initial-data payload. The fixed pseudocode header-lead audit is
271/155 of 426; this is a lead census, not complete body coverage.

Native 0x2744 OTA transmit is a separate C body, not an alias of the
0x258c probe. Its 384-case bounded original/source oracle passes packet,
framed response, no-header, short-read and timeout paths, comparing child
calls, response RAM and result. The final response timeout in native code
returns through shutdown without diagnostic output; the candidate follows
that observed behavior. Strict combined graph: eight imports, SHA-256
`25c7c5eb0d16a7d46943ca5bd47ab3f920f57d98b609338a4e6dc5b10093eff6`.
Six reachable source code bodies, ambient selector ABI and CRT initial data
remain. Fixed pseudocode header leads: 272/154 of 426.

Native 0x1574 box file open outer state machine is now C source. Its 160-case
bounded native/source oracle compares query and chunk packets, checksum,
transmit/parse calls, bank/erase/copy failure exits, one-chunk success,
result, lock and box RAM. The source exposes five real bank/file children:
0x2f46 running bank, 0x2d48 erase, 0x2b4c serial copy, 0x2e04 chunk write,
and 0x2cc0 final apply. Strict combined build has 12 imports, SHA-256
`3f8c407e4147fddf47a7b5a547369994df716e84e57d1aeca140b254fbc2dcba`:
five remaining original code bodies, five new children, ambient selector ABI
and CRT initial data. The fixed 426-entry lead audit remains 272/154 because
0x1574 already had a header lead in the caller candidate.

The box file children 0x2f46 running-bank selector, 0x2d48 bank erase
retry policy and 0x2cc0 image checksum now have C source. Their bounded
native/source checks pass 128, 96 and 160 cases. Erase exposes the genuine
0x497c option erase executor as a typed hardware contract. The 0x2cc0
checksum reads the OTA image region at 0x08040000 and compares the native
big-endian word sum to box metadata; test memory is synthetic and does not
qualify a physical image. Strict graph: ten imports, SHA-256
`6999ba9bb64fa2e3f88537749ebf4ccdac58c3a14d622878d3e33e5122aa0d8b`:
five original code bodies, 0x497c erase executor, 0x2b4c serial copy,
0x2e04 chunk write, ambient selector ABI and CRT data. Pseudocode header
leads: 274/152 of 426.

The exposed box descendants now close in C: 0x2b4c serial copy,
0x2f60/0x2f88 flash identity readers, 0x2e04 8-byte chunk writer,
0x497c erase executor and 0x3e94/0x3eec flash register primitives.
Bounded original/source comparisons pass 128, 256, 192, 160 and 320 cases.
The 0x1574 caller was corrected to pass the native live three-register
0x2e04 ABI (offset, data pointer, byte count); its 160-case oracle now
checks those arguments and still passes. The strict combined graph builds
with seven imports, SHA-256
`60cf478c426ba90cd0a0c86918d9c9574cc18655caa2fb9285a1c9eec706a013`:
five original code bodies (console open/apply, transport callbacks 6e1c
and 7f2c, service maintenance), ambient selector ABI and CRT initialized
data. Hardware flash effects remain unqualified by device tests. The fixed
pseudocode header-lead census is 276/150 of 426.

Native 0x18e4 periodic service maintenance now has C source. Its 256-case
bounded original/source comparison covers side presence, charging/water
suppression, divisible tick schedules, status packets, parse success/failure
and state counters. Legacy diagnostic strings with `%d` but no explicit
native argument are compared by message only; live R1 is not claimed as a
stable contract. Strict combined graph: six imports, SHA-256
`431ae5798ef7a369e89b3160e059e812ac4770fd23f0a89406c62e9b40fc38ba`:
console open/apply, transport callbacks 6e1c/7f2c, ambient selector ABI and
CRT initial data. Header leads stay 276/150 because 0x18e4 was previously
mentioned in a caller header.

Native console open 0x4480 and apply 0x4100 now have C source. Their
bounded original/source oracles pass 160 and 256 cases, comparing result,
descriptor RAM, peripheral/global MMIO and lower call arguments. Exposed
0x46a4 console GPIO/IRQ setup and 0x67b0 field writer also have C source,
with 320 bounded lower comparisons. Explicit volatile initialization avoids
a compiler-generated `__aeabi_memclr4` dependency. The strict combined
graph builds with four imports, SHA-256
`6e54db719a11dc236480d75fd8e79d930e9c75bc89a5b930891cdf4de7d1c311`:
transport callbacks 6e1c and 7f2c, ambient selector ABI and CRT initial
data. The fixed pseudocode header-lead audit is refreshed in
`case-body-crosswalk.json`; it is still only a source lead inventory.

Native long-running transport callbacks 0x6e1c and 0x7f2c are now C loops
from an authenticated Thumb ELF view of the same stock image. Bounded
one-iteration comparisons at the task-wait cut pass 192 and 224 cases,
covering event bits, send packets, periodic battery/temperature transitions,
aging state and shared RAM. Quiet diagnostics were excluded from these
corpora and are not claimed equal. The callbacks expose nine genuine code
children: 0x1334 aging begin, 0x9ebc battery percent, 0xa01e battery
sample, 0x9f18 current sample, 0x2a68 periodic update, 0x9ff0
temperature sample, 0x085c event handler, 0x3b90 RX restart, 0x9a9c
command reset. Strict combined graph builds with 11 imports, SHA-256
`4cd05923ef2281d623dee32dc290c7cdd63a480fa50962c9e2947f12c1c0e22c`:
those nine children, ambient selector ABI and CRT initial data. These two
native callbacks were absent from the fixed 426-entry pseudocode catalogue,
so header-lead count remains 280/146. Reachable callback closure is still
separate from whole-image native body inventory.
