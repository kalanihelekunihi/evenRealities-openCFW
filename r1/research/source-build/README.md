# R1 source compilation checkpoint

Current canonical frontier: **538 tested contract candidates,1,378 compiled
symbol hints,1,410 unresolved routes**. The canonical timer admission section
below supersedes its earlier staging notes. Whole-image source and byte
closure remain unproven.

`make -C r1 source-candidates` rebuilds 15 translation units for Cortex-M4F
with Clang, C11, hard float and `-Wall -Wextra -Werror`. All 15 passed on
2026-10-15. `report.json` records the exact commands, hashes, symbols and
compiler. The remaining 27 references are runtime/math dependencies, not
missing reconstructed-provider symbols. Objects are local build outputs.

`gates.json` tracks all locked image components and S140/MBR separately.
No application or bootloader image is linked by this target. No function
byte match, source completeness, whole-image independent review, stock
configuration equivalence or hardware behavior is established by this result.
The existing 2,972-function corpus structural verifier also passes.

Work remains actionable: the goal is active, and the listed potential external
blockers have not yet been exhausted. In particular, an absent compiler alone
does not prevent further C conversion or cross compilation. Existing historical
configuration guesses must not silently become stock facts.

## Stock checksum contracts

The provider target now compiles **16/16** units. Three added stock-shaped
checksum/hash entry points passed **1,056** differential comparisons against
Thumb routines from the hash-authenticated application. Both polynomial-generated
tables match the stock image data. See `checksum-verification.json`.

## Nordic bootloader candidate

```
python3 r1/tools/build_bootloader_candidate.py \
  --sdk vendor-cache/r1/nRF5_SDK_17.1.0_ddde560 \
  --gnu-runtime vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update
```

Both archives are pinned in the repository tool/dependency manifests. The script
checks the SDK archive and every extracted SDK file, plus the GNU archive and the
extracted runtime headers/libraries it uses. It derives the source/include/define
lists from Nordic's original Makefile and substitutes only the recovered public
verification key. It force-includes `r1_recovered_config.h` with the captured
profile, including the recovered RC clock settings. Other SDK example settings
remain candidates, as documented in `config-recovered/README.md`.

All 74 candidate translation units compile with Clang for Cortex-M4F. The Clang
`-Os` experiment overflowed the original flash region; `-Oz` links within it.
The generated candidate linker script changes the example's libc group to
`libc_nano` to reflect its nano specs. It retains all original memory bounds.
The native GNU linker resolves every symbol. `bootloader/report.json` records
commands, source/object/configuration hashes, dependency archives, image hash,
size, program headers and the undefined-symbol check.

This is a **candidate build**, using GNU startup assembly, GNU runtime binaries
and the SDK's Oberon/CC310 binary libraries. It is not a C-only source closure,
stock ArmCC build, byte-identical image, independently reviewed full recovery,
or tested device firmware. The full 776-byte UICR snapshot is still unresolved;
the candidate's two UICR address words do not establish that snapshot's closure.

## RTOS provider and R1 memory configuration

`make -C r1 rtos-candidate` compiles **12/12** translation units: seven pinned
FreeRTOS 10.5.1 core/allocator units, three Nordic nRF52 port units, the pinned
CMSIS-FreeRTOS wrapper, and R1-owned static memory callbacks. CMSIS RTOS2 API
headers come from the existing pinned CMSIS 5.9.0 tree; its sparse checkout was
additively extended to include `CMSIS/RTOS2/Include`. No dependency pin changed.

`rtos/report.json` records commands, input/object hashes, configuration hash,
type size, definitions and unresolved symbols. `rtos/static-memory-verification.json`
records **20** comparisons between linked ARM C callbacks and the authenticated
stock routines at `0x95BB8` and `0x95BD0`. Observed output pointers, 256-word
depths and guard bytes match. This callback-only link places the two storage
sections at the observed stock RAM locations; it is not an application link.

The build exposed a configuration gap: the candidate static TCB type is 92
bytes, whereas stock reserves 112 bytes before each stack. The source preserves
the observed reservation without claiming the complete stock TCB type. See
`r1/source-config/rtos/README.md`. Exact stock kernel options, CMSIS tick-query
bindings, Nordic platform dependencies and application integration remain gates.
The kernel/port assembly and compiler runtime are not counted as C-only closure.

## Crypto policy and complete function frontier

The R1 two-pass AES adapter and callback now compile against pinned upstream
tiny-AES-c and link as a component without runtime libraries. The original
stock Thumb routines passed 116 transform and 28 XOR comparisons against the
compiled ARM component, covering partial trailing blocks and 4,096 bytes.
See `r1/components/crypto/README.md` and `crypto/verification.json`. Tool dossiers
explicitly show the candidate code size differs from stock.

`make -C r1 source-frontier` accounts for all **3,326 ownership entries** in
`function-frontier.csv`. It verifies recorded sources, objects and the relevant
behavior-receipt inputs before producing `function-frontier-summary.json`:

- 8 tested contract candidates, with bounded-input receipts;
- 1,171 compiled-symbol hints that still need ABI/body/placement validation;
- 2,147 unresolved source routes.

These categories do not establish image source completeness. The ownership
ledger combines inventories and has a different scope from the 2,972-function
structural corpus. Static/local symbols are included as routing hints; a name
match is not accepted source coverage. The largest unresolved groups are 755
product entries, 542 Nordic SDK entries, 157 Goodix democode entries and 129
compiler-runtime entries. Existing source candidates must be mapped and
validated before inferring that an unresolved name requires a new body.

## Application-side Nordic SDK

`make -C r1 application-sdk` now compiles **64/64 nonempty** application-side
Nordic SDK candidate units, emitting 679 function symbols including local/static
helpers. It derives the source/include list from the preserved historical build
seed and adds the SDK units identified by the later source-correlation records.
No SDK implementation body is rewritten. The build authenticates the SDK
archive and every extracted file. Two small inline-assembly operand-format
adaptations are applied only to generated copies for Clang; their patches and
provenance are kept separately.

`application-sdk/report.json` records source/object/configuration hashes,
compiler commands, warnings, emitted-code counts and unresolved references.
Eight authenticated vector checks and 18 effective-configuration assertions
preserve recovered selections after Nordic's legacy compatibility processing.
The advertisement-name SVCI stub retains R12=3 and SVC 0. See
`r1/source-config/sdk/README.md` for exact evidence and remaining default values.
Compiling NFCT/PDM/TIMER providers does not demonstrate peripheral operation.

The refreshed frontier has **1,417 compiled-symbol hints**, **8 tested contract
candidates**, and **1,901 unresolved source routes** across the same 3,326-entry
ownership scope. This supersedes the earlier frontier counts above. The
application-side SDK work removed 246 missing-name routes, but symbol presence
alone does not validate the stock ABI, body, link placement or configuration.
No complete application firmware has linked from these components.

## Goodix public source and stock configuration

The Goodix candidate target now compiles **16/16** public-source units with no
warnings, including the separately source-correlated algorithm-configuration
unit. It emits 354 candidate function symbols and retains 42 external symbol
requirements. No private Goodix archive is inspected, linked or represented by
a success stub. The original upstream tree and pin remain unchanged.

The source configuration audit found a real stock delta: HR's 36 bytes and HRV's
24 bytes match upstream, but three calibration words differ in the public
76-byte SpO2 object. The R1-owned typed patch now reproduces all 136 stock
configuration bytes, with field-offset/size assertions and six linked ARM
getter checks. See `r1/source-config/goodix/README.md`,
`goodix/configuration-verification.json` and `r1/patches/goodix/`.

The newest frontier supersedes earlier counts: **1,526 compiled-symbol hints**,
**8 tested contract candidates**, and **1,792 unresolved source routes**. The
Goodix democode family's unresolved name routes fell from 157 to 48. Name
routing remains weaker than ABI/body/placement validation, and no complete
Goodix algorithm subsystem or application image is linked by this work.

## Sensor APIs and ST25 board bindings

The sensor target compiles **6/6 units** with warnings treated as errors: Bosch
`bma4.c`/`bma456w.c`, ST `lis2dw12_reg.c`, ST `st25dvxxkc.c`/`st25dvxxkc_reg.c`,
and the R1-owned ST25 board binding. Every public source, header and license
input is checked against the existing dependency manifest hashes. The selected
pins remain unchanged. During this run the LIS2DW12 checkout differed from the pinned commit;
that checkout was preserved, and the build materialized the declared pin's
explicit files from Git objects into an ignored local cache. The report records
both the observed checkout and the consumed pin.

The build emits 463 candidate function symbols, including API functions not
retained in stock. Bosch's bus_read/bus_write/delay_us offsets pass compile-time
checks at 0x24/0x28/0x2C. The ST25 binding uses the correct public Write/Read field
order and raw RTC1 counter. Ninety veneer comparisons against authenticated
stock code pass with emulated provider call seams. The registration root and
actual resource, bus and delay implementations remain separate open gates.
See `sensors/report.json`, `sensors/st25-bus-verification.json` and
`r1/components/st25/README.md` for bounded validation scope.

The current 3,326-entry frontier now has **1,595 compiled-symbol hints**,
**14 tested contract candidates**, and **1,717 unresolved source routes**.
Those routing categories remain separate from whole-image source completeness,
stock instruction matching and application integration.

## Shared i2c_5 integration

The fixed-state read/write wrappers and board-resource operations now compile
and make a relocatable link with the real ST25 API, register API, R1 veneers
and reconstructed registry. Genuine remaining symbols are two compiler memory
helpers and the delay provider. There are no fabricated production bus providers.

**782 integrated comparisons** pass against original stock Thumb, including
request bytes, retained null-write buffer pointers, registry status paths and
ordered GPIO/delay actions. This caught and corrected the historical reversal
of P1.10's OUTSET/OUTCLR sequence. REA and Ghidra-MCP confirmed the actual GPIO
setter at `0x79434`; MCP byte readback matched the original 20-byte body.
See `r1/components/i2c5/README.md` for exact scope, loader identity and limitations.

Current frontier: **225 tested contract candidates**, **1,564 compiled-symbol
hints**, **1,537 unresolved source routes**. Whole-image source completeness,
application linking, exact compiler output and physical operation remain open.

## Software-TWI primitive stock oracle

`make -C r1 software-twi-oracle PYTHON=/tmp/r1-source-venv/bin/python`
compares actual compiled C with all twenty stock start/stop/ACK/read-byte/
write-byte bodies (4,144 cases). The oracle corrected an extra SDA release
in the C NACK tail. The source remains a reconstruction with unresolved
upstream attribution; native per-bus record installation, invalid-state guards,
electrical timing and a complete application link remain open.

The same oracle target also runs `--transactions`: eight stock transaction
bodies pass 1,575 comparisons using the actual compiled primitives. Tested
cases include address/register order, lengths 0/1/2/7/255, phase-specific NACK
aborts and full buffer snapshots. Adapter truncation and wide read counts above
255 remain separate gates.

Four native TWI registration wrappers now compile with a typed 112-byte record
layout and the native registry. All 48 stock comparisons pass. The oracle uses
injected layout fixtures; stock scatter values and runtime GPIO/operation
installation remain open, and no initialized bus is fabricated.

Authenticated stock scatter execution now resolves all four TWI initial records,
including the callback references and pull=3. It corrected reversed SCL/SDA
values in the contextual C initializer. Its compiled configuration passes 24
scalar and 24 injected-provider-reference checks; native data relocation and
callback-body closure remain open. See `software-twi/stock-initialization.json`
and `software-twi/board-configuration-verification.json`.

## Nordic TWI GPIO provider bodies

`make -C r1 twi-gpio-candidate` compiles six wrappers over the authenticated
Nordic inline GPIO HAL. Every consumed SDK header is checked against the pinned
SDK archive; the report also hashes transitive compiler headers. No unresolved
symbol remains in this object. `twi-gpio-oracle` compares all 24 native callback
copies: 4,608 cases across all valid pins, pull settings and MMIO patterns pass.
Only 16 of those callbacks have separate entries in the ownership ledger;
ledger counts preserve its existing scope. Native record relocation and delay
provider source remain open, as do physical line/timing proof and byte identity.

Eight native TWI open/close bodies now compile in the integrated component.
All 512 lifecycle comparisons pass with actual compiled Nordic GPIO callbacks;
no GPIO operation is intercepted. Native table installation, delay/transfer
bindings and full application linking remain open.

Eight native request adapters now compile and use the actual transaction and
primitive bodies through fixed bus records. Their 570 stock comparisons pass,
including NULL requests, closed/nonzero flags, NACKs and lengths 0/1/2/257.
The 16-bit i2c_4 path retains 257 while narrow counts truncate. NULL payload
fault equivalence and native initial table installation remain explicit gates.

Two recovered C delay bodies now cover the four TWI delay callback references:
a microsecond-times-64 subtract-three work loop and an intentional no-op. All
32 comparisons pass, including zero and unsigned shift-overflow cases. The
volatile C loop preserves work/termination but adds stack accesses; original
instruction timing and physical elapsed time remain explicit gates. Three of
these callback entries are in the ownership ledger. Native callback-table
installation remains open.

The native TWI table-installation gate is now closed for the four software buses:
448 bytes of typed source-owned initial configuration match stock after explicit
pointer relocation. All 44 full native registry/lifecycle/transfer comparisons
pass with actual GPIO and delay bodies. MMIO inputs remain synthetic, newlib
strcmp is a binary test dependency, and delay cycles, invalid buffers, other
board records and full application startup/link remain open.

The native NULL-payload divergence is now repaired in a dedicated native engine
build mode. All 570 NULL-buffer adapter comparisons pass, including 76 matching
unmapped-access cases. The contextual reconstruction retains its guards.
Invalid callback faults, physical exception state, exact instructions and
physical timing remain open.

Seven named interrupt GPIO descriptors now have typed source-owned records.
Four native bodies compile and pass 74 comparisons, including actual registry
registration, callback storage and compiled pin reads. The 308 initial record
bytes match stock after name relocation. Event-open remains unresolved; close
SDK calls are checked at an intercepted provider seam. See
`r1/components/gpio/README.md` for the scope and remaining gates.

Named-GPIO event-open and shared-pin IRQ dispatch now compile against the
pinned nrfx types. All 202 named-GPIO comparisons pass, covering config bytes,
init-error handling and callback fan-out. Actual nrfx open/close internals and
physical interrupts remain separate gates.

The named-GPIO component now links the actual nrfx GPIOTE provider. A proven
configuration correction raises low-power slots from the historical two to
eight, reproducing the stock 128-byte control-block layout with six field/size
assertions. All 64 SDK units rebuilt and the 202 GPIO comparisons still pass.
The remaining component references are `memset`, compiler memory helpers,
`strcmp` and the ST25 millisecond-delay seam. Real nrfx interrupt execution and
a complete application link remain open.

The actual compiled nrfx lifecycle now passes 29 original-code differential
calls without provider interception, comparing statuses, ordered peripheral/
core writes and relocated 128-byte control state. This exposed and corrected
the historical IRQ priority 2 to stock priority 6 (NVIC byte 0xC0 at IRQ6).
The SDK effective configuration probe now has 20 checks. Four SDK ownership
rows advance from symbol hints to bounded tested contracts; unresolved counts
are unchanged. Asynchronous interrupts, shared-pin duplicate close coherence,
physical timing and full application linking remain open.

Three typed native ADC records now compile with four recovered adapter bodies.
All 124 initial-state bytes match stock after name relocation, and 354 bounded
comparisons pass. The oracle preserves stock's different open-index and
close-input-selector arguments and ignored sample statuses. Actual SAADC
integration, untouched failed-sample storage, settling cycles and fatal-error
behavior remain explicit gates; see `r1/components/adc/README.md`.

The actual SAADC provider now links with native ADC/registry/TWI objects.
Ten lifecycle calls match stock on statuses, 53 ordered peripheral/core writes
and the 48-byte driver state without provider interception. Four SDK ownership
rows advance from compiled-symbol hints to bounded tested contracts. Analog
conversion, asynchronous interrupts, fatal-error implementation and physical
settling remain open; the fatal-error seam traps if reached in this test.

The combined native board component now registers all 14 ADC/GPIO/TWI records
and resolves the three NFC handles without prebinding. All 54 comparisons pass
across six registration orders, including full shared state and MMIO traces.
This caught and corrected shared request startup values (A6, lengths 1/1).
Runtime memory/string helpers, fatal ADC error, ST25 millisecond delay, full
startup and whole-image source/link identity remain gates.

An attributable, unchanged musl v1.2.5 C memory/string subset now supplies
memcpy, memset and strcmp, with R1 EABI clear/copy wrappers. All 3,311 checks
pass, including 1,985 stock comparisons. The board component now has only the
fatal-error and millisecond-delay references, and its 54-case oracle links no
binary C runtime. Original Arm runtime identity, fault granularity, cycles and
whole-image byte identity remain separate gates.

Three recovered board log/delay bodies now compile and pass 1,798 stock
comparisons. The supposed fatal ADC routine is a returning conditional logger;
its exact flags, formats and packed SDK ID are preserved. The millisecond body
requests one 64,000-unit delay per millisecond. The board's remaining references
are now the two logging backends, not missing error/delay wrapper bodies.
Physical timing and logging backend closure remain open.

The native structured-log wrapper and two state getters now compile and pass
6,656 stock comparisons. The wrapper preserves gates, packed descriptor bits,
BASEPRI/task critical routing and the native varargs cursor. The board link now
requires the actual Nordic frontend, structured encoder and FreeRTOS critical
entry/exit; these dependencies are exposed rather than stubbed. Encoding,
scheduler/transport integration and physical exception behavior remain open.

The actual Nordic critical entry/exit functions now link into the board with
translation-unit-scoped native assertions. All 1,040 comparisons pass,
including 104 assertion faults; the structured logger's 6,656 cases also pass
with real critical functions. Two compiled-symbol hints advance to bounded
contracts. Scheduler startup, physical exception state and whole-image
identity remain open. The frontier now includes candidate object/report paths
and pins these critical contracts to the tested native variant.

The compact structured encoder now compiles and passes 1,729 original-frame
comparisons. Record filtering, 32-byte payload limits, argument scanning,
alignment, string suffixes and sequence state match stock. Float conversion,
time inputs and cache transport remain explicit dependencies. Source-compiled
musl strlen is added under the same authenticated version pin; runtime tests
now total 3,320, including 1,994 stock comparisons.

Three native timestamp bodies now compile and pass 185 original-code checks,
including 70 unbound-backend faults. The RTC request, ignored status, NULL
backend context and signed/wrapping local offset match stock. RTC registration
and actual clock sources remain gates. The board resolves timestamp consumers
and still requires Nordic logging, kernel ticks, float conversion and cache
append providers.

The actual pinned CMSIS/kernel tick providers and Nordic interrupt-priority
validator now link into the board. All 17,280 stock comparisons pass without
provider interception, including 8,100 assertion faults and 14,760 interrupt
tick paths. The selected variant enables native assertions before FreeRTOS
headers configure ISR validation. The baseline kernel objects retain their
existing assertion configuration. Four ledger entries advance to tested
contracts; IRQ_Context is inlined and the additional FromISR entry is not a
separate ownership-ledger row. Scheduler startup, the full TCB layout, physical
interrupt behavior and original compiler output remain open. The board now
requires three providers: Nordic logging, float conversion and cache append.

The two recovered Arm float bit-pattern bodies pass 94,208 conversion and
42 rounding comparisons. These preserve stock exponent wrapping, underflow
to unsigned zero and missing IEEE exceptional-value handling; a normal C cast
or standard compiler runtime cannot be assumed equivalent. The encoder also
passes its 1,729 cases with actual float conversion. REA pseudocode and
Ghidra-MCP byte readbacks are retained, with their shared-backend limitation.

Native cache append passes 15,680 comparisons; native copy/peek/consume passes
33,696 with actual source memory and critical providers. A second 15,680-case
append run uses the actual copy body. Admission leaves an extra unused byte;
transport thresholds use pre-append occupancy. All are preserved. The board
now owns the initial 8 KiB buffer at 0x20016bc8, cache state at 0x200068f4 and
236-byte export buffer at 0x20018bc8. Its oracle compares all 8,444 initial
bytes against stock scatter execution. BLE dispatch, connection access and
event publication are exposed dependencies alongside Nordic logging. Ring
concurrency, actual transport and original instruction identity remain open.

Native event publication and its queue adapter now compile and pass 25,349
publisher cases plus 48 direct adapter cases. Stock passes a **16-byte** record:
an uninitialized leading word precedes ID, length and inline/heap payload. The
leading word is excluded from byte comparison and remains an evidence gate.
Queue failure still wakes the consumer; inline padding, heap failure logging,
cleanup and initial 16-byte task-context prefixes match stock. Heap, CMSIS queue
and logging callbacks are intercepted in these tests. The source-owned connection
field at 0x200064b8 initializes to 0xffff and passes every halfword value.

These providers link into the board, which also compares the three context
prefixes and connection initializer against stock scatter. Task creator/stopper
pointers have unresolved real source bodies; stock addresses are used **only**
as test initial-data bindings. Native allocator analysis additionally proves a
16-byte stock block header with saved caller LR, versus the pinned upstream
heap_4 baseline's 8-byte header. The baseline remains reusable ancestry, with
explicit product-layout extensions required before native compatibility can be
claimed. These allocator and task/queue dependencies are exposed in the link.

All three native transmit veneers and the common producer now compile and pass
26,931 stock comparisons. Actual C connection getters run for guarded types
0/1. Tests cover copied envelope bytes, allocation rounding and overflowing
requests, unsigned occupancy thresholds, exact log calls, mutable queue/thread
handles, timeout 100, wake and free behavior. Allocator, CMSIS and log seams
are intercepted; this is not execution of a BLE worker. All three connection
halfwords initialize to 0xffff and pass 196,608 total value comparisons.

Ten native task creators/stoppers now compile and pass 1,080 cases, including
180 original creation-assertion faults. Five typed CMSIS attribute records own
the recovered names, priorities, stack sizes, TCB reservations and timezone
module values. Source-owned TCB/stack storage totals 28,208 zero bytes matching
stock scatter. The board links these actual lifecycle bodies and normalizes
their relocated function pointers when comparing all five context prefixes.
Earlier test-only creator/stopper bindings are superseded in the board oracle
by the actual source. Five task entries, CMSIS thread/queue behavior, allocator
extensions and Nordic frontend bodies remain actual production requirements.
The 112-byte TCB reservation is preserved; the complete kernel layout remains
a separate gate. Firmware identity and physical execution are still unproven.

Five complete native task entry bodies and the storage delayed callback now
compile. Original-versus-C traces pass 3,120 cases plus four callback cases,
including 36 startup/park-return assertions. Tests preserve startup call order,
queue creation and write-before-fault, record initialization/draining, motion,
watchdog handle mutations and suspend loops. The flag guard accepts positive
signed values; the requested low-24-bit mask is not itself a second guard.

Four native synchronization/park helpers pass 66,024 comparisons. ARM group
shifts use the low byte and return zero at counts >=32, without C shift UB.
Startup waits repeat until bit 23 is set, including error values containing
that bit; log text, mode rereads and mutable event handles match. The manager
event field at 0x2000655c and five watchdog slots are source-owned. The task
oracle additionally passes all 3,120 cases with actual synchronization bodies
(30 queue-failure assertions), observing three indefinite-delay attempts.

The combined board now links actual task entries, creators and synchronization
helpers; earlier stock-address task-entry test bindings are removed from that
oracle. Remaining symbols are exposed as explicit test traps for registration
checks. Actual RTOS scheduling, watchdog/dispatch/startup providers, native heap
extensions, manager object creation and original instruction identity remain
open. REA's current automatic analysis has no procedure at these task/helper
entries; authenticated corpus/disassembly, Ghidra-MCP byte readback and original
Thumb execution provide the recorded evidence instead. The callback has no
separate ownership-ledger row and does not inflate the frontier count.

Native watchdog registration, three record operations, two mutex adapters and
nine offset-list helpers now compile. The current-task getter is selected from
the actual pinned FreeRTOS task source. Checks pass 9,504 registrations, twelve
sequential/truncation-collision calls, 1,080 record cases (140 null-port/owner
faults), 158 list cases and six direct current-task values. Real C memory/string
providers run throughout; heap, CMSIS mutex and final sample callbacks are
intercepted. Names use uint8 strlen truncation before the seven-byte cap and
exact duplicates return NULL. Manager initialization and real sampling remain
open. A further 3,120 task cases execute the actual synchronization, watchdog,
list, current-task and memory bodies and compare resulting records.

The native event dispatcher passes all 65,536 low-halfword IDs in three length
classes (196,608 comparisons), plus 468 boundaries. It passes the payload word
and low-halfword length to callbacks, then frees the cached payload when the
cached low length exceeds four, even after callback mutation. Initial callback
table data is **not** claimed complete. Three unresolved RAM table anchors
retain the authenticated roots and the original broad overlapping lookups,
without inventing array extents or extra bounds checks. The board links the
actual body and treats these anchors as address-only test bindings; registration
checks do not establish table configuration or actual handler execution.

Source-owned watchdog enabled/mutex/registry fields and the pinned kernel
current-task cell match 25 initial stock bytes. The board's remaining function
providers stay explicit test traps. REA has no automatically created procedures
at the new entries; accumulated pseudocode, GNU instructions, Ghidra-MCP exact
readback and original Thumb differential execution are retained as evidence.
These contracts do not prove whole-image identity, scheduling or hardware.

Watchdog startup now owns the recovered CMSIS mutex attributes and 80-byte
control reservation, port start/stop/sample table, cached registry client and
80-byte named WDT record/config/ops. Manager initialization passes 128 cases;
deadline scans pass 8,640 (928 expiry assertions, 2,880 null-port faults), and
the expired-task getter passes 60. Initialization resets the list before mutex
creation and enables only after port success. Expiry preserves unsigned wrapping
deadlines, armed-record skips and the first failing record before its assertion.

The port/device chain passes 1,693 cases. Start intentionally opens/feeds twice;
wrappers preserve lazy lookup and ignored device status. Native nrfx adapters
keep the fixed sleep-running, 10,000-ms reload, priority-6 single-channel config,
including continuation after returning error logs. Another 211 cases execute
the actual pinned Nordic WDT code and compare state plus MMIO/core writes.
64-bit division, critical helpers, tick input and error logging are intercepted
in that oracle. R1 SDK logging mode is zero there: original gated SDK logging
is still an explicit source/configuration gate. Physical expiry/reset and
actual RTOS mutex control behavior are not proven.

The board now registers fifteen real records across all 24 group orders
(240 comparisons), preserving NFC handle discovery. It links the actual startup,
port, client, typed WDT adapter and SDK object once. The new division/critical
references remain exposed. Six recovered entry bodies were absent from the
ownership ledger and are recorded separately in watchdog-startup/supplemental-
contracts.json, without inflating the 3,326-row frontier. All identity, complete
executable coverage and physical-operation gates remain separate.


## Integer runtime source and watchdog integration

Two C translation units now supply `__aeabi_uldivmod`, `__aeabi_ldivmod`,
`__aeabi_llsl` and `__aeabi_llsr`. Nonzero unsigned arithmetic reuses unchanged
LLVM compiler-rt 20.1.8 source at immutable commit
`87f0227cb60147a26a1eeb4fb06e3b505e9c7261`. The separate R1 provenance manifest
pins source/header hashes and the compiler-rt-specific license, leaving the
shared upstream cache unchanged for future updates. Small C-compilable inline
assembly wrappers supply the quotient/remainder register ABI. Source-owned C
preserves stock zero-divisor results, signed overflow wrapping and register
shift behavior outside the upstream 0..63 precondition.

`build_integer_runtime.py` produces an object with no unresolved symbols.
`verify_integer_runtime.py` passes 50,822 comparisons against stock execution
and an independent integer model, checking callee-saved registers and stack
as well as results. REA pseudocode documents the stock 64-iteration division;
Ghidra-MCP readback authenticates the complete four-entry span. These tools
share a Ghidra backend, so their outputs are not independent semantic proof.

An additional `verify_watchdog_device.py --sdk --real-division` run passes all
211 Nordic WDT cases with the compiled C division provider executing. That
receipt removes the earlier division interception; critical-region helpers,
tick input and error logging remain intercepted. The shared board now links
the integer provider once and no longer lists division as an unresolved symbol.
Its 240 registration comparisons still pass. Original compiler output, cycle
timing, physical watchdog operation and complete application linking remain
open. That integer checkpoint raised the frontier to 199 tested candidates, 1,577
compiled hints and 1,550 unresolved routes across 3,326 ownership rows.


## Nordic critical regions and actual tick integration

`build_sdk_critical.py` compiles the unchanged pinned Nordic platform provider,
authenticates included SDK files against the SDK archive, and selects only its
two SoftDevice-aware critical-region bodies plus `nrf_nvic_state`. The recovered
12-byte zero state belongs at `0x2002c2fc`. These wrappers use application IRQ
mask `0xbdff06fc` for the first NVIC bank and all bits for the second. The
selected functions pass 52,464 stock/model comparisons, including all nested
byte values on exit, PRIMASK preservation, raw NVIC write ordering, repeated
nesting, saved registers/stack and 16 unmapped-pointer faults. The stock CRT
initializer confirms all twelve initial bytes. REA pseudocode and Ghidra-MCP
readback are retained under `sdk-critical/`; their shared backend is explicit.

The watchdog integration now additionally accepts `--real-critical` and
`--real-ticks`, together with `--sdk --real-division`. The full combination
passes 319 cases with actual compiled Nordic critical-region and CMSIS/kernel
tick providers. Its extra 108 cases check tick output over boundary values,
thread/interrupt contexts, PRIMASK and BASEPRI. Error logging remains intercepted
and SDK logging mode remains zero. Deterministic NVIC/scheduler fixtures are
not physical interrupt delivery or an executing scheduler.

The combined board links the selected provider once. Its layout explicitly
places all six recovered tick/critical variables, compares their 21 zero bytes
with stock startup, and checks the twelve NVIC state bytes separately. The
240 registration comparisons still pass, and critical-region helpers are no
longer unresolved production symbols. At that critical-region checkpoint: 201 tested candidates,
1,577 compiled hints and 1,548 unresolved routes. Whole-image compilation,
original instruction identity and hardware operation remain open.


## WDT SDK log configuration and error-string providers

`build_watchdog_logging.py` reuses unchanged Nordic `nrfx_wdt.c` and
`nrf_strerror.c`, authenticated with their included SDK files against the pinned
archive. The R1-owned `source-config/sdk-wdt/nrfx_log.h` supplies only the
recovered WDT log policy: INFO tests mode bit 0 then bit 2 with short-circuit
reads, passes the `[RING]` descriptor/format and marker, and always performs the
trailing mode read. WARNING has no evaluation or logger call on the observed
early invalid-state path. Other drivers are not admitted through this header.
The source-owned descriptor strings occupy the three authenticated stock
addresses, with all 87 bytes matching; this also preserves packed header inputs.

`verify_watchdog_device.py --native-sdk-logging` executes the new variant,
actual registry, memory, mode getter, division, critical-region and tick source.
All 3,903 comparisons pass, covering the earlier SDK/tick cases, 256 mode bytes
and 512 mode-transition sequences. The returning ADC error logger and structured
formatter are intercepted at documented boundaries; varargs strings, markers,
descriptor addresses, getter ordering, state and MMIO writes are compared.
Actual formatter/transport composition and other SDK log adapters remain open.

`verify_sdk_strerror.py` separately passes 139,272 comparisons for the upstream
lookup and fallback bodies: every 16-bit code, deterministic 32-bit values and
signed boundaries. All 37 table rows (296 pointer-normalized bytes) match by
code and exact string, including null versus `Unknown error code` fallback.
Original pointers/compiler output are not claimed. REA's current autoanalysis
has no procedure at the WDT init entry; that result is retained without claiming
pseudocode support. MCP readbacks authenticate the WDT and error-string spans;
direct disassembly and actual stock execution support the semantic contracts.

The shared board now selects this variant once, uses its existing actual C mode
getter and structured logger, and still passes all 240 registration comparisons.
At that WDT checkpoint the frontier was 203 tested candidates, 1,575 compiled hints and 1,548 unresolved
routes. Full application linking, remaining SDK logging configuration, original
instruction identity and hardware operation remain explicit gates.


## Native output worker and send veneers

`build_native_output.py` compiles the recovered queue-drain body at `0x44f50`
and two send veneers at `0x4e650`/`0x4e65e`. The worker reloads its context's
queue each iteration, initializes the pointer output to null, and stops on a
nonzero queue status or null record. Types 0/2 require a valid glasses handle;
type 1 uses the other channel; unknown types still free their envelope. ID and
length are consumed as 16-bit fields at offsets 0 and 8, while the type is the
full 32-bit field at offset 4. Send wrappers forward channel/timeout 1/200 and
0/100 without narrowing standalone arguments and preserve the backend result.

The implementation preserves pointer reloads after provider calls, the observed
short-circuit mode reads, both invalid-handle log paths and free ordering. Its
two descriptor strings match all 68 bytes at their authenticated stock
addresses. Byte reads avoid C alignment assumptions; original load/fault access
widths remain explicitly unproven. The provider reports keep generic BLE send,
actual queue/allocator and logger dependencies unresolved rather than supplying
success stubs.

`verify_native_output.py` passes 5,346 comparisons against the locked routines,
including 4 fault-address cases, null/status queue stops, unknown types, field
truncation, unaligned mapped envelopes, all mode bytes, mode transitions,
provider pointer/queue mutation, multi-record traces, full-word veneer arguments
and returns, saved registers and stack. Actual connection and mode C getters
execute; queue/free, sender and logging boundaries are intercepted.

`verify_native_tasks.py --real-output` additionally composes the actual worker
with the existing task/synchronization/watchdog/current-task/memory candidates.
All 3,120 task trace comparisons pass (30 assertion cases), plus four callback
cases. Both stock and candidate observe 444 worker entries, 588 sends and 588
frees. This is bounded sequential integration with fixture queues and allocator
boundaries, not scheduler concurrency or physical transmission. Earlier task
oracle variants still pass. The shared board explicitly retains all three
output entries, verifies their data and passes its 240 registration checks.

The accumulated pseudocode and direct disassembly support the contracts. REA's
current autoanalysis has no procedure at this worker entry; that result is
retained alongside authenticated MCP readbacks. At that output checkpoint the frontier was 206
tested candidates, 1,575 compiled hints and 1,545 unresolved routes. Generic BLE
send `0x3e7a8`, allocator metadata, queue/RTOS ownership, complete application
linking and exact image identity remain separate gates.


## Serialized BLE sender and semaphore policy

`build_native_ble_send.py` compiles seven recovered entries spanning
`0x3e7a8` through `0x3e937`: the serialized sender, benign-status classifier,
link semaphore selector, acquire-to-boolean adapter, one/bounded release helpers
and acquire-drain/four-release helper. Source owns two semaphore slots at
`0x200064fc`; their eight initial zero bytes match the stock CRT state. The
service at `0x20006504` remains an unresolved address-only anchor, with no
invented size, initialization bytes or callback table.

The sender preserves the stock asymmetry: flag zero sends even when acquisition
fails; nonzero flags require acquisition, return 19 on failure, and retry only
status 19 once using timeout 1,000. It reuses the mutable length word across the
retry, distinguishes exactly seven benign statuses and keeps the repeated
release/error-log order on non-benign failures. It does not add null-payload
validation or simplify diagnostic-only errors. Semantics are derived from
accumulated pseudocode, direct locked-image disassembly, REA pseudocode and
MCP-authenticated bytes. REA/MCP share a backend and are not independent proof.

`verify_native_ble_send.py` passes 71,797 comparisons: 69,635 classifier inputs,
1,770 sender paths and the selector/acquire/release/drain helpers. Cases cover
full-word identifiers, selector precedence, null handles, count saturation,
scripted drain termination, retry acquisition failure, 16/32-bit length updates,
provider-driven slot mutation, ignored release/log returns and saved registers
and stack. Semaphore APIs, lower BAE8 send and returning error logger are
intercepted. Scheduler progress and physical transmission remain unproven.

`verify_native_output.py --real-sender` passes 5,346 output/veneer comparisons
with this source executing (3,512 sender entries and 1,645 lower BAE8 boundary
calls). `verify_native_tasks.py --real-sender` passes all 3,120 task traces plus
four callback cases, composing output, sender, connection getters, synchronization,
watchdog/current-task and memory providers. The shared board explicitly retains
all seven entries and passes its 240 registration checks. Baseline oracle modes
and the 2,972-function structural corpus also pass; byte rebuild is still skipped.

At that serialized-sender checkpoint: 213 tested candidates, 1,575 compiled hints and 1,538 unresolved
routes. Lower BAE8 service send (`0x526cc`), service configuration and actual
CMSIS semaphore/allocator/queue ownership remain source routes. The fourth
unresolved data anchor is explicitly listed alongside the three event tables.
Complete application linking, original instruction identity and hardware proof
remain open.


## Lower BAE8 send and the actual HVX/SVC boundary

`build_native_bae8_send.py` compiles the recovered `0x526cc` body and a
C-compilable SVC ABI primitive. The Nordic NUS reference source and included
SDK files are authenticated against the pinned SDK archive. The adaptation
retains the Nordic license notice and uses the SDK's actual
`ble_gatts_hvx_params_t` and `SD_BLE_GATTS_HVX` constant, with static layout and
SVC-number assertions. Full r0 connection words at SVC are preserved through
the small assembly ABI primitive, including words beyond the public uint16_t
API's valid range. The new primitive is not counted as another recovered
ownership-ledger entry.

The source expresses R1's two notification-enable bytes, service handle reads
at offsets 6/22, link storage at 40, the 244-byte low-halfword length cap,
return-code normalization and custom structured/SDK log policy. The service
prefix is only a read view: no complete object, size, initialization bytes or
callbacks are invented. All 806 descriptor-string bytes match their stock
addresses. SDK HVX records have all 16 bytes initialized, including padding.

`verify_native_bae8_send.py` passes 14,342 stock comparisons and 1,571 actual
SVC174 paths. These cover all mode bytes, short-circuit transitions, mutable
client pointers/enable flags, null/error lookup, full-word connection/flag
inputs, length boundaries, both handles, exact HVX record bytes, SVC return and
length updates, faults and preserved registers/stack. The SVC instruction
executes, but a deterministic hook supplies its result; this is not SoftDevice
execution or physical BLE transmission. Lookup and logger boundaries remain
intercepted. REA pseudocode and MCP byte readback are retained; they share a
Ghidra backend and are not independent semantic confirmation.

`verify_native_output.py --real-bae8` composes the worker, veneers, serialized
sender, policy helpers, BAE8 body, actual connection/mode getters and source
memory. All 5,346 comparisons pass, including 608 SVC paths from 1,645 BAE8
entries. The shared board retains both BAE8 functions and still passes all
240 registration checks. Existing output and sender oracle modes also pass.

At that BAE8 checkpoint: 214 tested candidates, 1,575 compiled hints and 1,537 unresolved
routes. The next attributable route is the pinned SDK's unchanged
`blcm_link_ctx_get` at `0x514e0`; its source and compiled candidate were located,
but no new behavior admission is claimed here. Service object/configuration,
real connection-state/semaphore/queue ownership, full firmware compilation,
original instruction identity and hardware operation remain open.


## Unchanged Nordic link-context lookup

`build_sdk_link_context.py` compiles the pinned SDK's unchanged
`ble_link_ctx_manager.c`, authenticating included SDK files against the archive.
The original `0x514e0` body correlates to `blcm_link_ctx_get`. The combined board
binds `r1_native_bae8_context_get` directly to that function with a checked
linker alias, keeping the SDK source unchanged and adding no executable shim.
Both names resolve to the same address in the board test executable.

`verify_sdk_link_context.py` passes 37,154 stock comparisons. These cover output
clearing before null/alignment checks, the eight-byte storage descriptor's
pool/capacity/stride fields, the 20-index not-found sentinel, low-byte index
truncation, capacity errors, pointer calculation, descriptor/output aliases and
field reloads after the connection-index callback changes storage. Full register
arguments, compiled-target address wrapping, saved registers/stack and mapped
null/fault cases are compared. Descriptor fixtures are fully mapped; the stock
byte load versus SDK halfword load for the alignment check leaves partial-record
fault granularity open. Observed behavior outside public C input/object contracts
is specific to this pinned compiled target.

`verify_native_bae8_send.py --real-lookup` passes all 14,342 BAE8 cases with the
SDK provider executing, including 1,561 SVC174 paths under actual descriptor
fixtures. `verify_native_output.py --real-lookup` passes all 5,346 output-chain
cases, including 608 SVC174 paths. The connection-index function remains
intercepted, while actual lookup performs its own validation and computes the
client pointer. Service/storage descriptors and client pools remain explicit
fixtures. No production storage size or initialization is admitted by this.

The shared board includes the provider once, verifies the alias, and still
passes its 240 registration checks. REA pseudocode and MCP byte readback support
the authenticated stock location; their shared Ghidra backend is explicit.
At that lookup checkpoint: 215 tested candidates, 1,574 compiled hints and 1,537 unresolved
routes. This promotes one existing compiled hint through behavior admission and
source composition. Actual connection-index/registry state, BAE8 service/pool
configuration, SVC backend, complete application linking, original instruction
identity and physical operation remain open.


## Connection index, validity bitmap and authenticated reset span

`build_sdk_connection_index.py` compiles unchanged Nordic `ble_conn_state.c`
and `nrf_atflags.c`, authenticates included SDK files against the pinned archive,
and selects five bodies once: connection-index lookup, validity test, flag read,
internal reset and public init. The selected object requires source `memset`;
the board already supplies that real C provider. The valid-flags word is bound
to the native literal address `0x2002bdb4`.

The native reset at `0x51440` independently loads base `0x2002bdb0`, length 124
and tail-calls the stock clear primitive. Init at `0x51e78` branches to that
reset. This authenticates the reset destination/span and matches the SDK state
size, rather than inferring size from zero RAM. All field meanings, live writers
and event ownership remain separate gates. The board also compares the initial
124 zero bytes; it includes the state object only once.

`verify_sdk_connection_index.py` passes 157,596 comparisons without provider
interceptions. Actual Nordic bodies and source memory execute. Cases cover every
uint16 handle, walking/complement/random validity bitmaps, wide raw register
words, 4,096-bit mapped arrays, immutable read state, saved registers/stack and
eight unmapped read faults. Reset and init each pass 256 fill patterns, preserving
guards immediately before and after the 124-byte span. Unaligned and out-of-object
cases describe this pinned compiled target, not portable/public C guarantees.

`verify_sdk_link_context.py --real-index` passes 37,334 comparisons with actual
index/validity/flag bodies and no scripted provider responses. The bitmap and
storage remain fixtures. BAE8 `--real-index` passes 14,542 cases including 1,261
SVC174 paths; the output-chain `--real-index` passes all 5,346 cases including
560 SVC paths. The typed service/storage and valid bitmap are explicit fixtures;
logger, queue/semaphore/free and SVC responses remain bounded test boundaries.
The shared board retains all five entries and passes its 240 registration checks.

REA pseudocode and MCP readbacks authenticate the stock locations; their shared
backend is explicit. At that read/reset checkpoint the frontier was 220 tested candidates, 1,569 compiled hints
and 1,537 unresolved routes. Other registry bodies/event updates, real service
and pool configuration, complete image linking, original compiler output and
hardware operation remain open.


## Registry event writers, atomics and observer data

`build_sdk_connection_events.py` compiles unchanged Nordic connection-state,
atomic-flag and atomic source, with SDK headers archive-authenticated. A separate
R1 header maps this translation unit's CONNECTED range-failure diagnostic to the
observed returning `r1_adc_error` policy. Object-symbol exports retain the static
SDK callback/observer under distinct R1 names; recorded transformations change
symbol binding/names rather than executable instructions. The combined board
uses this selected event/read/reset module once, replacing its earlier read-only
selection and preserving one shared 124-byte state object.

`verify_sdk_connection_events.py` passes 15,001 comparisons of the full registry
and write order against stock. Actual atomic loops execute, including 954
controlled failed store-exclusives with interference/retry checks. Coverage
includes CONNECTED stale-record purge across 30 flag collections, role/range
handling, DISCONNECTED, security-level/authentication fields, ordered reconnect
sequences, list construction, flag writes and AND/OR results. Only the returning
error logger is intercepted during event execution. Retry injection models
instruction outcomes, not live hardware concurrency. List comparisons exclude
unused/uninitialized tail handles; invalid/partial event-pointer behavior is
not established. The source OR provider at `0x780ba` is absent from the ownership
ledger and is recorded separately without inflating the frontier.

The new module's read/reset bodies additionally pass all 157,596 existing
comparisons. BAE8 `--real-events` passes 14,462 cases, including 1,257 SVC174
paths, with actual SDK init/connect/disconnect/reconnect writers preceding
lookup and send. Tests preserve deferred invalidation: disconnect clears the
connected bit, and the next CONNECTED event purges stale validity/metadata.
Output `--real-events` passes all 5,346 cases with 10,692 registry event calls
and 560 SVC paths. Notification/storage pools and lower runtime/SVC responses
remain fixtures; registry updates do not establish real service notification
state or physical delivery.

The native observer tuple at `0xc4568` points uniquely to `0x5380d` with null
context. The unchanged SDK's typed eight-byte record is retained, relocated and
checked in the combined board alongside the 240 registration comparisons.
Its source priority section is `.sdh_ble_observers0`; native priority ranges,
complete dispatcher routing and live delivery remain open. REA has no procedure
at the event entry in its current analysis, so that result is retained without
claiming decompiler confirmation. MCP bytes, disassembly, independent models
and actual stock execution support the contracts.

Current frontier: 225 tested candidates, 1,564 compiled hints and 1,537 unresolved
routes. These remain bounded source candidates; complete application/image
linking, observer/event ownership, real service/pool configuration, original
instructions and hardware proof are still required.

## BLE polling, legacy section ABI and observer configuration

The pinned, unchanged nRF5 SDK 17.1.0 `nrf_sdh_ble.c` poller and
`nrf_section_iter.c` now compile into `sdk-ble-dispatch/ble-dispatch.o`.
A localized compatibility header selects the authenticated multi-range ABI:
12-byte set, 12-byte cursor, 8-byte observer, four priorities and a 500-byte
BLE event buffer. Compiler abstractions are cached before the localized SDK
branch selection; upstream sources retain their licenses and remain unchanged.

All 12 observer records are typed C, with four authenticated priority ranges.
The existing registry record remains defined once. The combined board object
includes the dispatcher and tables; 240 registration comparisons pass, with
96 pointer-normalized record bytes, 44 exact range/set bytes and the disabled
state byte checked. The iterator passed 16,257 comparisons across 1,819 range
cases; polling passed 663 cases and 679 more with the actual compiled registry
handler executing. SVC97 replies and eight other callback bodies are controlled
test boundaries. Opaque context addresses are authenticated without claiming
complete extents, initialization or ownership.

See `sdk-ble-dispatch/verification.json`, `iterator-verification.json`,
`registry-integration-verification.json` and `ghidra-memory-evidence.json`.
REA has no analyzed procedure at the poll entry; the error is retained.
Ghidra-MCP bytes match the locked image. These tools share a backend.
Frontier: **228 tested contracts, 1,561 compiled symbol hints, 1,537 unresolved
source routes** across 3,326 ledger entries. Full application linking, live
SoftDevice event delivery, byte identity and hardware behavior remain open.

## Queued-write observer and three owned contexts

`sdk-qwr/qwr.o` now supplies unchanged pinned Nordic `nrf_ble_qwr.c`,
including init, handle assignment, observer and user-memory retry. Typed C owns
three 12-byte contexts at `0x20007e40`, `0x20007e4c`, `0x20007e58`.
The native initialization loop independently confirms all three addresses and
stride; its callback argument is `0x79dc9`. Cold startup confirms 36 zero bytes.
The contract header asserts the zero-attribute policy, sizes and field offsets.

The direct oracle passed **10,340** comparisons and **1,934** SVC calls.
The dispatcher integration passed **739** cases and **7,464** observer calls,
with actual registry and queued-write bodies executing and **126** QWR SVC calls.
Initialization and handle assignment also execute as C in that fixture. SVC
responses and returning error callbacks remain test boundaries. Seven other
observer bodies and five other context anchors remain unresolved in production.
The combined board still passes 240 registration comparisons and retains all
three source-owned contexts once. There are **231 tested contracts, 1,558
compiled symbol hints and 1,537 unresolved routes** in the 3,326-row ledger.
Handle assignment is supplemental evidence because it lacks a ledger row.

A deliberate invalid bool representation (pending byte `2`) differs between
stock and default Clang: stock tests nonzero, Clang tests the low bit. The
accepted `-fno-strict-bool` compiler experiment did not change that result;
it is not selected. Canonical C bool values `0`/`1` pass. The observation and
baseline object are retained in `sdk-qwr/clang-default-bool-observation.json`
and `qwr-default-bool.o`; no byte-identity or arbitrary-corruption equivalence
is claimed. This is a compiler-domain gate, alongside original compiler/link
identity, remaining startup/providers, full image linking and hardware proof.
REA pseudocode and Ghidra-MCP readbacks are retained; both use Ghidra, and
SVC/prototype decompiler artifacts are resolved by native instructions and
execution evidence rather than copied into source.

## GATT initialization and upstream observer differences

`sdk-gatt/gatt-init.o` supplies unchanged pinned SDK init/link-init and one
36-byte typed context at `0x20007e1c`. Native initializer writes authenticate
three 8-byte links at offset 6, callback at offset 32, MTU 247, desired data
length 251, effective MTU 23 and effective data length 27. A local contract
header replaces the historical data-length seed of 27 with the proven 251.
Only the three-link aggregate is proven; the historical peripheral/central
split is still a separate configuration gate. Native startup supplies this
context with a null event callback; cold startup proves 36 zero bytes.

**5,376** direct init/link comparisons pass, covering all fill bytes, random
padding, arbitrary callback bits, null init, mapped aligned link offsets,
write guards and preserved registers/stack. The combined board includes this
context and provider once and still passes 240 registration comparisons.
Frontier: **233 tested contracts, 1,558 compiled symbol hints, 1,535 unresolved
source routes**, total 3,326. Seven observer bodies and four opaque context
anchors still remain in the combined production object.

The full SDK observer is deliberately unselected: four executable counterexamples
confirm a product change. Stock CONNECTED always calls SVC144 with the global
desired data length; SDK calls it only when desired exceeds effective length.
The diagnostic uses controlled successful replies; logging and other observer
branches are not covered by that counterexample. The native connected path also
has no initial MTU-exchange request. Further reconstruction must preserve these
product changes and the R1 dual logging policy, not promote generic SDK symbol
correlation to a complete observer implementation. REA pseudocode, Ghidra-MCP
readbacks and native disassembly support the next reconstruction route.
See `sdk-gatt/verification.json` and `ghidra-memory-evidence.json`.
Whole-image linking, original compiler/link identity, exact bytes and hardware
behavior remain open; the goal remains active.

## Native GATT observer and data-length/MTU helpers

`native-gatt/native_gatt_observer.o` now supplies R1's GATT observer,
data-length update and incoming MTU-request helper in C, using attributable
Nordic public ABI types plus the selected unchanged SDK initialization module.
R1 CONNECTED unconditionally sends a data-length request, and a peer data-length
request uses the desired link length without SDK's peer cap. These product
changes are preserved rather than selecting the non-equivalent generic observer.
Three small SVC primitives contain only the necessary SDK-numbered ABI glue;
there is no copied executable provider. SDK-derived code retains its license.

**16,923** differential cases and **13,098** SVC paths pass with actual source
memory, mode getter, strerror and link-init providers executing. Coverage includes
128 event IDs, bounds, MTU clamps/flags, raw pending/requested byte tests, callback
payloads, error/limitation paths, mode transitions and callback/log mutations.
All ten log descriptors (**668 bytes**) match the authenticated image exactly.
SVC results, limitation outputs, callbacks and final log backends remain fixtures.
Noncanonical flag reads are explicitly byte-based in this reconstructed body;
the separate unchanged QWR compiler-domain bool gate remains open.

The SDK poller/registry/QWR/native-GATT integration passes **763** cases and
**9,192** observer calls. Compiled initialization runs first, then connected,
data-length request/update, MTU response/request and disconnect packets execute
through the real observer tables. GATT SVC responses are controlled successes;
its direct oracle separately covers errors/logging. The combined board object
resolves this observer once and still passes 240 registration comparisons.
Six other observer bodies and four opaque context anchors remain unresolved.

Frontier: **236 tested contracts, 1,555 compiled symbol hints, 1,535 unresolved
routes** across 3,326 entries. The generic SDK counterexamples remain valid
historical evidence; the selected product adaptation is the new provider.
REA helper pseudocode and Ghidra-MCP byte readbacks are retained in `native-gatt/`.
Full-image linking, original compiler/link identity, exact bytes, live SoftDevice
and physical-device behavior remain open. The goal remains active.

## Nordic advertising observer/start/configuration and parsing providers

`sdk-advertising/advertising.o` supplies unchanged nRF5 SDK 17.1.0
`ble_advertising.c` observer/start/configuration/flags/PHY/whitelist code plus
`ble_advdata.c` parsing/search. Both source files and their dependency headers
are authenticated against the registered SDK archive. The ABI contract asserts
the native byte mode, 44-byte configuration, callback/parameter/handle/data/
connection/whitelist offsets and 1,076-byte compatible storage span. Typed C
supplies contexts at `0x20007e64` and `0x200082b0`, with **2,152** cold zero
bytes compared against stock. This compatible storage is not a claim of original
allocation identity or complete product initialization.

**48,585** comparisons and **14,944** actual SVC114/115 paths pass with C memory
providers. Checks cover all canonical mode-enable combinations, both contexts,
directed/fast/slow/idle transitions, peer/whitelist callback replies, controller
errors, disabled state, byte padding, tag/config writes, PHY/whitelist helpers,
256 flags bytes and parsing/search over bounded malformed/random records and
all 256 AD types. Normal control-flow bool inputs are restricted to valid 0/1;
noncanonical bool/invalid wide enum behavior remains a compiler-domain gate.

The SDK poller/registry/QWR/GATT/advertising integration passes **779** cases and
**10,152** observer calls, including both advertising records. Context mode,
callback and data-pointer setup is an explicit test fixture: real product
initialization/data encoding remains unselected. Controller replies and callbacks
are deterministic boundaries, not live SoftDevice/radio proof. The combined board
object resolves the observer once, owns both compatible contexts and retains its
240 passing registration comparisons. Five observer bodies and two opaque
context anchors remain unresolved in that object.

Frontier: **245 tested contracts, 1,551 compiled symbol hints, 1,530 unresolved
routes**, total 3,326. Upstream reuse now includes actual advertising bodies,
not just symbol candidates. Future upstream changes can be assessed against the
pinned native contracts; no untested version is promoted. REA start pseudocode
and Ghidra-MCP readbacks are retained in `sdk-advertising/`. Product advertising
initialization/encoding, remaining providers, full-image linking, original
compiler/link identity, byte equality and physical behavior remain open.

## Advertising initialization and full data-encoding provider selection

The canonical board now selects `sdk-advertising-init/advertising.o` once,
replacing the smaller advertising selection. The same authenticated unchanged
Nordic source supplies `ble_advertising_init`, `ble_advdata_encode` and their
address/connection/manufacturer/service/name/UUID/size-selection helpers.
The new local ABI header asserts the native 60-byte advertising input,
172-byte initializer, configuration/callback offsets and 12-byte payload records.
The older selection and its receipts remain bounded historical evidence.

**4,993** direct initialization/encoding/helper comparisons and **4,020** SVC
paths pass. Actual C memory executes; controller identity/address/appearance/
name/UUID/configuration replies remain explicit fixtures. Tests cover output
sizes/error paths, name truncation, UUID-size queries and writes, manufacturer/
service/connection records, both contexts, initialized/reinitialized state,
configuration rejection, null initializer/context and init-to-start sequences.
The larger selected object also passes the **48,585** earlier advertising
comparisons. The size-selector helper is supplemental and does not inflate the
ownership ledger. **130** undersized-buffer cases retain stock service-data
writes beyond the supplied capacity within mapped guards; this is an observed
native compatibility behavior, not memory-safety or protocol-conformance proof.

Dispatcher integration now invokes the real initializer and encoder for both
advertising contexts before polling: **1,558** actual initialization calls across
**779** cases and **10,152** observer calls. The fixture supplies initializer
parameters; it no longer writes encoded buffers/internal data pointers directly.
This does not prove the product's actual mode/callback/name/manufacturer setup.
The canonical board retains 240 passing registration comparisons. Frontier:
**253 tested contracts, 1,543 compiled symbol hints, 1,530 unresolved routes**,
total 3,326. Five observer bodies and two opaque contexts remain open, together
with complete startup/linking, compiler/link identity, exact bytes and hardware.

REA was checkpointed for requested maintenance without changing firmware or the
separate Ghidra-MCP server. Snapshot save succeeded with 22 primitive queries and
25 evidence records. Snapshot and exact resume metadata are at
`/Users/kalani/Documents/Codex/2026-10-15/task-2/r1-rea-preupdate.snapshot.json`
and `r1-rea-preupdate.resume.json`. No REA update or successful reconnect is
claimed here. Ghidra-MCP readbacks for the new contracts remain in
`sdk-advertising-init/ghidra-memory-evidence.json`; local analysis/build work and
the full goal remain active.

## Product advertising configuration, persistent-read boundaries and callback

`native-advertising-configuration/native_advertising_configuration.o` now supplies
five ledger bodies plus a supplemental status adapter. Actual product setup uses
full-name/appearance/flags 6, scan-response connection intervals 24..40,
manufacturer ID `0x5245`, callback `r1_advertising_event_plan_build` and connection
tag 1 for the first advertising instance. The 21-byte source-owned payload at
`0x20007e04` contains six controller address bytes plus fifteen serial bytes when
the fixed-record sentinel is valid; an absent serial selects a six-byte encoded
payload while retaining the native FF fill in storage. Cold startup proves all
21 initial zero bytes. Intervals and four callback log strings match **88 bytes**.

Fast advertising is enabled at interval 160, timeout 6000 unless configuration
byte `0x70` equals `0x55`. A second independent record read controls slow enable;
slow interval is 1600 and timeout zero. The reads are not cached or collapsed.
Fixed-record accessors call the unresolved KV class reader through the live
handle field at `0x20007dfc`; a non-FF byte at record offset61 selects15 serial
bytes at offset31. Native error-log continuation and subsequent tag setting are
preserved. The callback emits the native fast/slow logs and status argument
mapping; the final status-ring publisher remains a real unresolved provider.

**70,050** comparisons and **2,388** SVC paths pass. These include all65,536
pairs of configuration-byte reads, all sentinel values, optional length output,
full-width ignored KV errors, handle changes, callback events/log modes and
controller/SDK error continuation. **72** cases execute the actual product
constructor, SDK initialization/encoding, advertising start and stored product
callback together. Source memory, SDK and mode-getter bodies execute; persistent
records, controller replies, returning error/logger backends and final status
publisher remain explicit boundaries. Typed ephemeral pointers and callback
identity are normalized; original stack/padding identity is not claimed.

The canonical board links this module once and still passes240 registration
comparisons. Frontier: **258 tested contracts, 1,543 compiled symbol hints,
1,525 unresolved routes**, total3,326. Product configuration for the second
advertising instance, persistent-provider behavior, remaining BLE observers/
contexts, complete startup/full-image linking, compiler/link identity, exact
bytes and hardware remain open. Partial/unfilled persistent reads and controller
address failure writes are explicit evidence gates: fixtures fully populate
124/7 bytes even on error, so no stale-stack behavior is promoted to C proof.
Accumulated pseudocode slices and Ghidra-MCP readbacks are retained with hashes.

REA6.5 recovery remains separate from firmware progress: this chat's existing
transport returns `Transport closed`; the update task's retained recovery
report records a snapshot `profile_mismatch` with unchanged target SHA. The
original snapshot/binding remains untouched. No fresh REA analysis or rewritten
profile was attempted here. Local compilation/execution and the existing
Ghidra-MCP server continue to support the active goal.

## Cached KV class providers and actual advertising read integration

`native-kv-class/native_kv_class.o` supplies the unchanged native policy for
cached-class read/write and the 24-byte health-record wrappers in C. The class
view has flags at18, uint16 size at20 and cached payload at24. A full uint32
requested length must equal the stored size; mismatch returns5 before port or
copy access. Successful reads enter a port callback, copy cached bytes, reload
the live port pointer and leave. Writes set flag bit0 after enter and before the
copy. Callback return contents are ignored, matching the native caller. The
health wrappers return0 for a null caller buffer and otherwise use a live class
handle with size24. These are cached-memory operations, not flash persistence.

**140,156** direct comparisons and **16,984** port callback calls pass with
actual C memory. Tests include all65,536 requested uint16 sizes against a124-byte
record, matched mapped sizes0..1024, wide-register mismatches, no-copy failures,
port swaps/reloads, header/data mutation, dirty flags, callback return values,
zero-length target observations, wrapper nulls and guarded state/registers/stack.
Class/port structures are read views; no complete allocation or initialization
identity is inferred. The port slot at `0x20006974`, health-handle slot at
`0x20007df4` and device-info slot at `0x20007dfc` remain unresolved live fields.

The product advertising oracle passes all **70,050** cases again with the real
cached-class reader and C copy executing. The earlier KV-return stub is removed
in that variant; fixture records populate class caches before entry, and only
port callbacks remain controlled. The72 constructor→SDK init/encode/start→stored
callback cases still pass. This closes the class-read body gate while preserving
cache/handle/port initialization, actual locking, concurrency and backing-flash
gates. The canonical board selects this provider once and still passes240
registration comparisons. Frontier: **262 tested contracts, 1,543 compiled symbol
hints, 1,521 unresolved routes**, total3,326. Full-image linking, original compiler/
link identity, exact bytes and physical behavior remain open.

REA6.5 CLI continuation is verified using the new snapshot and retained function
at `0x489d6`: field+0x24 equal1 selects238, otherwise31. The cached replay retains
its existing fresh6.5 evidence ID/profile; no new analysis evidence is claimed.
All25 historical IDs, prior content and original profiles remain preserved; the
6.5 schema adds only `relationship_coverage:null`. The original snapshot was not
modified. `native-kv-class/rea-owner-continuation.json` records target/profile/
query hashes. Native REA MCP chat transport still requires desktop refresh;
Ghidra-MCP and the supported CLI are available. The whole goal remains active.

## KV port callback bindings and source-owned table

`native-kv-port/native_kv_port.o` supplies seven supplemental native bodies and
one typed nine-entry port record at `0x20006984`. The binder writes this record
pointer through the caller's destination. Three offset-named callbacks return0;
control operation1 increments the byte at `0x20019e49` with uint8 wrap, and
operation3 writes the first word of the live storage context or `0xa5a5a5a5`
when absent, returning1 for a null output. Other operations return0. Names do
not imply unproven shutdown/flash semantics for the zero-return slots.

The critical callbacks cache one read of the mutex field at `0x20006978`, guard
null and call CMSIS acquire with `UINT32_MAX` or release. The source owns that
zero-initialized field, the zero port slot at `0x20006974`, the zero control byte
and the36-byte mutable callback record. Native cold startup proves9 zero bytes
and all nine pointer identities. Initializer/get/put entries are C symbol
references to unresolved production providers, not stock ROM bindings or fake
bodies. The backend storage-context field at `0x2000697c` remains an address-only
live anchor; full port/backend initialization and allocations remain open.

**793,395** adapter/control comparisons pass. The cached-class
suite passes **140,156** cases with actual port adapters, and the product
advertising suite passes **70,050** cases with the actual class reader, table,
mutex adapters, SDK and product callback. The advertising integration observes
**269,646** CMSIS calls; only CMSIS results remain
intercepted in this critical-section route. This is caller/control-flow evidence,
not actual scheduler locking or concurrency proof. Source memory and data paths
remain compiled C. The combined board still passes240 registration comparisons.

All seven entry points are absent from the3326-row ownership ledger and are
recorded in `native-kv-port/supplemental-contracts.json`; frontier counts remain
**262 tested contracts, 1,543 compiled hints, 1,521 unresolved routes**. This
checkpoint closes the callback-body/table binding gate while retaining the
unresolved storage initializer/get/put, CMSIS runtime/locking, field/cache/handle
initialization, backing flash, full-image linking, compiler/link identity, exact
bytes and physical behavior gates. The full goal remains active.


### Native latest-slot KV read

`native-kv-store-get` compiles the248-byte stock entry at `0x95168` into
`r1_kv_store_get`. Ghidra-MCP's body read matches the locked binary exactly;
accumulated pseudocode and native instructions support its field offsets and
callback order. The source reads only the latest slot. It zeroes a24-byte
header, requires a full header and matching magic, then requests the payload.
It retains the original slot/base while reloading the live context for magic
and the driver for the payload callback. Error precedence and separate log-mode
reads are preserved. No generic upstream KV implementation was substituted
for this product-specific storage contract.

**14,049** stock-versus-C comparisons pass, including all cursor bytes, wrapping
addresses, short/oversized callback replies, partially written headers, driver
and context changes, logging modes, output guards, stack and saved registers.
The four source-owned descriptors match stock bytes. The combined board resolves
the port table's get entry to this C provider and passes240 registration cases.
The frontier now contains **263 tested contracts,1,543 compiled hints and1,520
unresolved source routes**.

Storage context/driver pointers and stride remain address-only test bindings;
actual lower-driver allocation, initialization and flash reads remain gates.
The port initializer and write provider remain unresolved. Compiled/differential
evidence does not establish complete linking, instruction identity, byte-identical
firmware or hardware behavior. The full goal remains active.


### Supplemental native KV erase/write provider

`native-kv-store-put` now compiles the292-byte callback at `0x95304` as
`r1_kv_store_put`. Ghidra-MCP body bytes match the locked image. This entry is
absent from both the3326-row ownership ledger and accumulated pseudocode;
its native instruction contract is recorded in `supplemental-contracts.json`.
The fresh REA6.5 analysis also reports no procedure at this entry. That failed
query is retained as a discovery limitation, rather than claimed as successful
decompilation. The source implementation follows authenticated instructions.

On a cursor/threshold match, it erases each configured block using fixed4096-byte
spacing and a4096-byte length, stopping on the first nonzero driver result.
It resets the cursor only after all erases succeed, then computes the write
address with the separately configured stride. Context/driver/count reloads,
post-callback cursor changes, exact log strings, mode short circuit and
zero-success driver return semantics are preserved. This provider does not
increment the cursor; the existing port control callback owns that operation.

**7,232** stock-versus-C comparisons pass, including all cursor bytes, threshold
boundaries, zero block count, erase/write errors, address wrap, context/driver/
count/cursor mutations, all log mode bytes, guarded input and saved registers.
The combined C object resolves the port's write callback and passes240 board
comparisons. Six source descriptors match native bytes. Frontier counts stay
**263 tested contracts,1,543 compiled hints,1,520 unresolved routes** because
this supplemental entry is not in the ledger.

The lower erase/write driver remains an external provider, and live block count,
threshold, stride and backend initialization are unresolved. Controlled driver
replies are not flash persistence proof. The port initializer, full-image linking,
compiler/link identity, byte equality and hardware behavior remain gates.


### Supplemental native KV initializer

The338-byte initializer at `0x94e3c` is now compiled as
`r1_kv_port_initialize` and selected once in the combined board object.
Ghidra-MCP bytes match the locked binary; this supplemental entry is absent
from the ownership ledger and accumulated pseudocode. Source now owns the
context/driver pointer fields, block count, threshold, stride, partition size,
80-byte mutex storage and16-byte CMSIS attributes. Native cold startup confirms
**98 zero bytes** and the attributes/name/log descriptors match stock.

The policy reuses a cached mutex, calls FAL initialization only when its readiness
getter returns zero, looks up `kv.bin`, resolves the partition's device name,
and rejects missing partition/device or lengths below2048. It retains stock
error-state writes, including clearing the context on device lookup failure.
It derives byte-sized snapshot/erase counts with native truncation, writes
2048-byte stride and full partition size, then calls startup scrub and latest-slot
scan before storing the returned cursor byte. No invented successful flash
provider or ROM binding is used.

**7,424** stock-versus-C comparisons pass for mutex/FAL/error paths, boundary and
large geometry, byte truncation, scan mutations, log modes and arguments, state,
stack and saved registers. The combined board passes240 registration cases.
Frontier counts remain263 tested contracts,1,543 compiled hints and1,520 unresolved
routes because the initializer is supplemental. FAL0.5.99 attribution remains
with the pinned FlashDB2.0.0 dependency; its registry/configuration and real
CMSIS/scans must still be linked and validated. Complete linking, original
compiler/link identity, byte equality and hardware behavior remain open.


### Pinned FAL readiness and partition configuration

`sdk-fal-readiness` compiles unchanged `fal.c` from FlashDB2.0.0 commit
`4e5677408256f82d47cd56a6b04605dcee35ed9a` and selects only
`fal_init_check`, aliased as `r1_fal_is_initialized`, with its shared byte.
All other bodies are removed by section collection; unused undefined symbols
are removed, and short-enum ABI flags agree with the combined native graph.
There is no hand-copied upstream body. The6-byte stock getter at `0x62fe8`
is authenticated through Ghidra-MCP; **256** comparisons prove all byte values,
guards and saved registers. Cold startup proves the selected byte at
`0x200077b1` starts zero. The combined board passes240 registration cases.

All seven compiled64-byte FAL partition records match **448 stock bytes** at
`0x9c250`: names, device names, magic, offsets, lengths and reserved words.
This authenticates the existing source table independently of the unproven
registry initialization. Extraction operates on a temporary object copy and
checks the original provider object hash.

Broader FAL selection remains gated: the historical build disables assertions
and diagnostics, whereas stock lookup bodies contain nonreturning assertion
paths. The top-level initializer must eventually share this exact readiness
byte. Generic FAL compilation and table identity alone do not prove those
paths, native scans, actual flash behavior, whole-image linking or exact bytes.
The supplemental getter does not change frontier counts.


### Native startup scrub and latest-slot scan

`native-kv-scans` compiles `r1_kv_flash_erase_scan` (`0x57d0c`,156 bytes)
and `r1_latest_valid_flash_slot_scan_adapter` (`0x64b24`,204 bytes).
Both Ghidra-MCP body reads match the locked image, and source slices from the
accumulated pseudocode are hash-bound in `evidence.json`. Both functions are
selected once in the combined board, resolving the initializer's scan calls.

The scrub zeroes its24-byte header once, checks the initial read provider, then
reloads context/driver and block count during its ascending4KiB page loop.
It deliberately ignores read/erase returns. A short callback may retain previous
header bytes. Matching magic or `UINT32_MAX` avoids erasure; other values trigger
erase and logs. Latest-slot selection instead caches its initial byte-sized
threshold, searches backward with the live stride/context/driver, zeroes each
header, requires exactly24 returned bytes and matching magic, and returns the
one-past slot byte. Its missing driver/read path skips candidates.

**5,472** direct comparisons pass, including every byte-sized count, partial
headers, callback status behavior, pointer/geometry mutations, wrapped addresses,
log modes and descriptors, guards and saved registers. Another **4,064**
initializer comparisons execute the actual scrub/selection bodies with compiled
C memory; only FAL/CMSIS and lower driver results are fixtures. Six descriptors
match native bytes, and240 combined board registration cases pass.

Frontier now accounts for **265 tested contracts,1,543 compiled hints and1,518
unresolved routes**. These are source/control-flow results, not physical flash
or complete startup proof. FAL assertion/diagnostic compatibility, real storage
providers, full-image linking, compiler/link identity and exact bytes remain gates.


### Pinned FAL top-level initializer with native diagnostics

The combined board now selects `sdk-fal-core/fal-core.o` instead of the
isolated readiness object. Unchanged pinned `fal.c` supplies both `fal_init`
(`0x62f40`,62 native bytes) and `fal_init_check` with the same readiness byte.
`fal-native/configuration.h` suppresses informational/debug logs and routes
errors through the real `printf` provider contract. The error macro remains
upstream, preserving its source line48, format/version strings and three calls.
A stock-compatible assertion macro is configured for later bodies; its broader
paths are not claimed verified by this core-only selection.

**10,512** differential cases pass over every initial byte, signed flash/partition
results, state mutation in provider callbacks, ignored printf returns, exact
format/argument/order traces, guards, stack and saved registers. The getter
executes after each initializer call and observes the resulting shared byte.
Ghidra-MCP authenticates the complete native body, and accumulated pseudocode
is bound in `evidence.json`. The combined board passes240 comparisons.

Frontier now has **266 tested contracts,1,542 compiled hints and1,518 unresolved
routes**. `fal_flash_init`, `fal_partition_init`, device/partition lookups and
`printf` remain production providers. Test printf interception does not prove
console output, and controlled lower initialization does not prove a real flash
registry. Full-image linking, compiler/link identity, byte equality and hardware
remain open. The earlier generic no-op FAL configuration remains historical
evidence and is not selected beside this module.


### Pinned FAL device initialization and lookup

`sdk-fal-device` compiles unchanged pinned `fal_flash.c` using the native
assertion/error configuration and no info/debug diagnostics. Both
`fal_flash_init` (`0x62e68`,90 bytes) and `fal_flash_device_find`
(`0x62df4`,58 bytes) are selected in the combined board. Ghidra-MCP body reads
match the locked image, and accumulated pseudocode slices are hash-bound.
The zero initialization byte at `0x200077b2` is now source-owned.

**12,338** comparisons pass, including **271 terminal assertions**. They cover
all initialization-byte values, every callback-presence mask, ignored init
results, callback state mutation, all byte changes across bounded names, NUL
and high-byte input, exact assertion printf strings/arguments and nonreturning
self-loops. The singleton device table is folded by Clang into direct symbol
references; its source semantics and returned pointer match stock, while exact
table section identity remains unproven. The R1 device record at `0x200077c4`
is still an unresolved production data/driver provider.

`runtime-strncmp` adds unchanged `strncmp` from the same musl1.2.5 commit
`0784374d561435f7c787a555aeab8ede699ed298` used by existing memory providers.
Primary cgit and pinned GitHub mirror content matched, and copyright/provenance
are retained. It executes in lookup comparisons; this does not establish
original Arm runtime source or exact instructions. Existing runtime reports
and objects remain unchanged.

Frontier now has **268 tested contracts,1,542 compiled hints and1,516 unresolved
routes**. Combined board240-case verification passes. Partition initialization/
lookup, real device operations, printf runtime output, whole-image linking,
compiler/link identity, byte equality and hardware remain open gates.

The FAL core integration suite additionally passes **10,512** comparisons with
the actual upstream device initializer and shared core readiness getter executing.
Partition initialization, the device record/callback and printf remain controlled
fixtures. This closes the source-to-source initializer boundary without claiming
real flash allocation, driver behavior or runtime output.


### Pinned FAL partition initialization, lookup and cache

`sdk-fal-partition` compiles unchanged pinned `fal_partition.c` and selects
`fal_partition_init` (`0x631c0`,30 bytes), `fal_partition_find` (`0x63150`,
62 bytes) and `check_and_update_part_cache` (`0x57e1c`,98 bytes).
All three complete native bodies match Ghidra-MCP reads and are bound to
accumulated pseudocode slices. The source owns **37 cold-zero bytes** across
the initialization byte, table pointer/count and seven-entry device cache.
All **448 bytes** of the emitted seven partition records match stock.

Two preserved counterexamples constrain compilation. Clang's multiline error
macro reports closing line145, while stock reports opening line144; a partition-only
configuration mapping preserves the observed diagnostic argument. At optimized
settings, Clang narrows the internal initialization state and rejects byte2
where stock accepts every nonzero byte. Compiling this translation unit at
`-O0` preserves the native full-byte behavior without modifying upstream bodies.
These are explicit compiler/configuration differences, not original toolchain proof.

**18,647** comparisons pass, including all initialization-byte values, every
missing-device mask, signed offset/device-length boundaries, partial cache writes,
count mutations, all seven names and bytewise query changes, exact error printf
and a terminal assertion. The combined board passes240 cases. Its former
FAL partition symbols now resolve to actual C bodies; the R1 flash-device
record/operations and printf runtime remain production requirements.

Frontier is **271 tested contracts,1,539 compiled hints and1,516 unresolved
routes**. Complete caller-chain startup, physical flash behavior, whole-image
linking, original compiler/link identity and byte equality remain open gates.


### Native FAL device record and registry adapters

`native-fal-device` now owns the56-byte mutable FAL device record at
`0x200077c4`, its zero handle, two12-byte shared request blocks and16-byte
geometry response (**44 cold-zero bytes**). It compiles native initialization
(`0x71054`,50 bytes), read (`0x87af8`,30 bytes), write (`0x96fb0`,38 bytes)
and supplemental erase (`0x5d4f8`,20 bytes). Ghidra-MCP body reads match the
locked image; available pseudocode slices are hash-bound. Erase is absent
from the ownership ledger and is not counted as a new ledger contract.

Initialization finds `device_flash` through the actual C registry, ignores open
status, reloads the handle for control operation1, and updates base/length/block
size only on a zero control result. It always returns1. Read returns the
original requested length regardless of dispatch result; write fills the same
shared block as erase and uses `strlen` when its supplied length is zero.
Erase returns control operation0's result. Native field widths, byte page count,
32-bit multiplication/wrap and callback-visible request mutations are preserved.

The record uses the official pinned `struct fal_flash_dev` and exact callback
types. A native `fal_cfg.h` wrapper imports the existing authenticated table
macros while exporting a mutable declaration, so FAL consumers and the owner
have consistent C types. The historical generic configuration is unchanged.
All selected FAL modules are rebuilt with this native configuration.

**5,933** native adapter comparisons pass with actual compiled C registry
lookup/dispatch and memory/string providers, including every callback mask, all
page bytes, ignored callback results, shared-block mutation and zero-length
strings0..512. FAL core10,512, device12,338, partition18,647 and core/device
integration10,512 cases pass again after type alignment;240 combined board
cases pass. Record pointers are normalized against the four verified source
symbols, and all nonpointer bytes match native cold data.

Frontier is **274 tested contracts,1,539 compiled hints and1,513 unresolved
routes**. The combined graph no longer has an unresolved FAL device-record
symbol. The actual registered flash descriptor, operation table and Nordic
operations still need source reduction; controlled callbacks are not physical
flash proof. Complete startup, full-image linking, original compiler/link
identity, exact bytes and hardware behavior remain gates.


### Registered native internal-flash device

`native-internal-flash` compiles six manual ownership supplements at
`0x54970`, `0x5498c`, `0x549f0`, `0x54a4c`, `0x54a8c` and `0x54aa4`.
They provide callback configuration, erase/geometry control, Nordic fstorage
configuration, registered read/write wrappers and registry registration.
These six bodies are absent from accumulated function output; authenticated
Ghidra-MCP bytes, native instructions, cold RAM and the existing internal-flash
correlation support them. No accumulated pseudocode receipt is invented.

The source owns the80-byte descriptor at `0x20006f98`, including its embedded
24-byte registry record and36-byte operations table, the13-byte name, and an
official SDK-typed20-byte fstorage context at `0x20007dc0`. Function pointers
are compared by verified identities. Registration retains the native callback
configuration pointer in operation slot`0x1c`; it is not silently moved to the
generic `0x20` dispatcher slot.

Native setup reads UICR/FICR before SDK initialization, logs initialization errors
and continues, falls back to page-size times page-count when the boundary is
erased, and assigns the36-page region with32-bit arithmetic. Its initialized
flag is set even after a returning error logger. The read/write request length
is truncated to16 bits; read/erase ignore lower results, while write returns21
for a zero lower result. Enabled hooks invoke before/after callbacks with native
request timing and post-callback pointer reloads. Error precedence is retained.

**203,735** stock comparisons pass, including all16-bit read/write request
lengths, flag/error paths, callback and request mutation, geometry fallback/wrap,
registered read/write/control, configured callbacks and actual C registry
registration. Nordic operations remain fixtures. The combined board passes240
cases and authenticates the80-byte descriptor,20-byte context and13-byte name.

Frontier is **280 tested contracts,1,539 compiled hints and1,507 unresolved
routes**. Lower page erase, mapped read, word write, event callback/completion
and pinned Nordic fstorage providers remain gates. The API table's native
address is only a test data anchor. Full startup, physical persistence,
original compiler/link identity, full-image linking and byte equality remain
unproven; the full goal stays active.


### Lower internal-flash adapters and completion

`native-internal-flash-operations` compiles page erase (`0x5c40c`,80 bytes),
mapped read (`0x5c464`,24 bytes), word write (`0x5c480`,62 bytes), wait
(`0x969fc`,34 bytes) and event handling (`0x65720`,26 bytes). The last two
are supplemental entries absent from the ownership ledger. All five bodies
are authenticated by Ghidra-MCP reads against the locked image; available
pseudocode slices are retained, with missing accumulated entries explicit.
The pending byte at `0x20006f96` is source-owned and cold-zero authenticated.

Erase computes page-rounded count, caches base/page geometry, sets pending
for each request, ignores SDK erase status and waits after every request.
Write rounds bytes to a word count with native32-bit wrap, retains the otherwise
unused volatile FICR access, sets pending and returns0 immediately on SDK
rejection; it waits and returns1 only after acceptance. Mapped read is a forward
byte loop, preserving overlap behavior rather than substituting memcpy.
The wait loop checks the SDK busy API, polls SoftDevice events, feeds the
existing native watchdog provider and calls `osDelay(5)` until not busy.
Successful event IDs0/1/2 clear pending; other IDs/results leave it unchanged.

**26,322** stock comparisons pass over rounding/wrap, bounded page loops,
ignored erase errors, write rejection, mapped overlap, exact wait sequencing,
event low-byte IDs, pending state, memory guards and saved registers. SDK
busy replies use canonical bool0/1; page size is nonzero and loop counts
bounded. Poll-time flag mutation is controlled, not a real SDK interrupt.
The combined board passes240 registration cases with all five C bodies selected.

Frontier is **283 tested contracts,1,539 compiled hints and1,504 unresolved
routes**. The native storage-policy path now reaches named Nordic fstorage/
SoftDevice providers; those upstream bodies, real runtime scheduling and full
caller integration remain gates. No physical persistence, original compiler/
link identity, byte equality or complete image is established.


### Pinned Nordic fstorage facade providers

`sdk-fstorage` compiles unchanged SDK17.1.0 `nrf_fstorage.c` and selects
`nrf_fstorage_init` (`0x78c78`), erase (`0x78c4c`), write (`0x78dac`) and
is-busy (`0x78c80`). All selected source/header inputs are authenticated against
the SDK archive. A local contract header sets parameter checks disabled and
assertions absent, matching native unconditional dispatch rather than the
historical configuration's error-return behavior. No SDK function body is copied
or patched. Predicates/helpers may be optimized away; their original instruction
identity and invalid-pointer fault behavior are not claimed.

**12,227** comparisons pass for full provider argument forwarding, API assignment,
unchecked alignment/length/bounds requests, result/state mutation and direct or
fallback busy checks with canonical bool replies. Another **26,322** lower-adapter
comparisons execute the actual SDK facades, including erase error handling,
word rounding and completion loops. API callbacks, poll/watchdog/delay and event
mutation remain controlled fixtures. The combined board passes240 cases.

Native fallback busy scans use two20-byte instances at
`0x20007dc0..<0x20007de8`. The first is the source-owned native flash context;
the second and final `fs_data` linkage remain unresolved. Start/end symbols
remain production requirements and are address-only test bindings. They are
not fake source allocations or proof of full SDK initialization.

Frontier is **287 tested contracts,1,535 compiled hints and1,504 unresolved
routes**. `nrf_fstorage_sd`, SoftDevice polling, real asynchronous events and
runtime scheduling remain gates, as do complete startup, original compiler/link
identity, full-image linking and exact bytes.

REA6.5 also returned a fresh `analyze_function` receipt for `0x78dac`:
`ev_1876e2f4eefe6f6bc90263f382ce1212c8d922bd06931a2c60f884aef5df10e8`.
The retained `sdk-fstorage/rea-write-function.json` is bound to the authenticated
ELF digest and audit. It is analysis evidence, not an instruction-identity or
complete-source receipt.


### Complete pinned SoftDevice fstorage implementation

`sdk-fstorage-sd` now compiles the complete unchanged SDK17.1.0
`nrf_fstorage_sd.c`: all eight API methods, queue processing, chunk/retry
logic and system/request/state handlers. Static symbols are isolated for
shared linking, with upstream source/header hashes checked against the SDK
archive. The four-operation queue uses five28-byte slots; native initialization
confirms140-byte buffer size,4KiB chunks and eight retries.

The source owns **184 cold-zero bytes** for FIFO control/buffer, work flags,
current-operation pointer and get context. The32-byte API table and three
8-byte observer records match native function identities at their actual
positions. Flash information matches12 bytes. A typed local4-byte FIFO
pointer retains the native constant that Clang otherwise folds; it does not
replace any upstream function body.

**3,047** direct comparisons and another **3,047** through public fstorage
facades pass, each executing **407** flash SVC calls. Coverage includes all
API methods, allocation failure, busy/error outcomes, sync/asynchronous
completion, queue chaining, retry exhaustion, precise event payloads, request/
state observers, copy/read/map operations and canonical flag states. Memory
helpers are actual compiled C. FIFO/atomic/SDH replies and SVC results are
controlled boundaries, so these tests do not establish real concurrency or
flash persistence. The combined board passes240 cases.

REA's fresh queue analysis receipt
`ev_b60dc1c5fbd8a655c823799b0ae19d5684b9be6c3084d0eb04d95ba16520164d`
explains the404-byte inventory size: Ghidra groups four non-contiguous ranges
(`0x78d08..0x78da1`, `0x7a3ec..0x7a43b`, `0x7a4e4..0x7a4f9`,
`0x87520..0x875b3`). The local queue block is148 bytes; SDH continuation
remains a separate unresolved C provider. Its full inventory row is therefore
not promoted by local-block tests. No legacy size is silently rewritten.

Fourteen other SDK contracts are now tested: frontier totals **301 tested
contracts,1,521 compiled hints and1,504 unresolved routes**. FIFO/atomic/SDH
runtime, complete observer dispatch, second instance/final section allocation,
complete startup, original compiler/link identity, full-image linking and byte
equality remain explicit gates.


### Pinned FIFO and atomic source checkpoint

Unchanged SDK 17.1.0 `nrf_atfifo.c` supplies the six used public APIs and
five exclusive-access helpers. `nrf_atomic.c` supplies flag-set-fetch and
fetch-OR; existing connection-event AND/OR definitions are selected only once.
The combined board now resolves the FIFO/atomic dependencies with compiled C.

**33,548** direct comparisons pass, including **42** controlled failed
exclusive stores per implementation, retry-time mutations, ring positions,
wraps, initialization boundaries and full-word atomic masks. The native and
compiled exclusive instructions execute; injected failures are test-only and
do not prove physical interrupt scheduling or concurrency.

With all FIFO/atomic fixtures removed, **69** fstorage workflows pass across
**920** actions and **290** flash SVC calls per implementation. Actual C queue
operations cover capacity four, queue-full errors, repeated wrap/drain, write
chunks, busy retries, internal errors, timeout, pause/resume and reinitialization.
Only SDH replies, application callback and flash SVC results remain fixtures
in this integration harness. The board still passes **240** registration
comparisons. Ghidra-MCP bytes authenticate all thirteen native spans against
the locked application; available accumulated pseudocode is hash-bound too.

The audit records **314 tested contract candidates, 1,518 compiled symbol
hints and 1,494 unresolved source routes** across 3,326 ownership rows.
These counts have a different scope from the 2,972-function structural corpus.
SDH continuation/polling/state and observer dispatch, the second fstorage
instance, final section allocation, startup, original compiler/link identity,
whole-image linking, byte equality and physical hardware remain open gates.


### SDH dispatcher candidate checkpoint

The unchanged pinned `nrf_sdh.c` continuation closure now compiles under the
authenticated legacy multi-range ABI. Five public entry contracts (poll,
is-enabled, continue, enable request and disable request) pass **3,200**
comparisons and **720** SoftDevice SVC calls per implementation. These tests
execute the actual compiled section iterator, compare **84** native range/set
bytes, and authenticate three cold-zero state bytes against runtime
initialization. Ghidra-MCP binds all five native code spans to the locked app.
REA's direct polling lookup returned no-procedure; that failed receipt is
retained in `sdk-sdh/rea-poll-unrecognized.json`.

This module is a separate tested candidate, **not yet selected in the board
or promoted in the frontier**. Observer callbacks, critical boundaries, IRQ
operations and SVC replies remain controlled fixtures. Production observer
records and section linkage, real IRQ behavior and asynchronous fstorage
integration remain the next work. Non-contiguous inventory entries are not
upgraded from these narrower span contracts.


### SDH core selected in the combined source graph

This supersedes the earlier candidate-only SDH checkpoint. The unchanged pinned
SDK continuation/enable/disable/is-enabled/poll closure now joins the board.
A local typed configuration supplies two stack and two native state observer
records (32 bytes pointer-normalized), alongside the storage-owned request and
state records. The three SDK state bytes match cold runtime initialization;
84 bytes of section range/set configuration match native bytes exactly.

Beyond the3,200 direct comparisons, **4,704** comparisons now execute actual
SDK critical-section and IRQ/NVIC bodies with **784** SoftDevice calls per
implementation. Coverage includes priorities0..7, nested critical state,
PRIMASK states, interrupt masks and returning error codes. Emulated MMIO
receipts are not physical interrupt proof. The native error-wrapper alias
selects the existing `r1_adc_error` C provider; no duplicate body or ROM binding
is introduced. Ghidra-MCP authenticates seven native entry/helper spans and
available accumulated pseudocode is hash-bound.

Combined board verification still passes240 registration comparisons. The
frontier is **319 tested candidates,1,513 compiled hints,1,494 unresolved
routes**. Two native state callbacks, SOC polling and the fault handler remain
real unresolved dependencies. Observer callbacks and SVC replies are controlled
in SDH tests; complete asynchronous fstorage/SDH integration, final linkage and
startup, original compiler identity, byte equality and hardware remain gated.
The REA404-byte queue inventory is not promoted from these separate contracts.


### SOC system-event polling selected

Unchanged pinned Nordic `nrf_sdh_soc.c` now supplies the system-event poller
using the existing legacy iterator. A local error contract selects the native
returning wrapper. The unused SDK stack registration is removed by section
selection; the existing typed SDH stack row points to this single C body.
Typed clock/DFU SOC references supply the first priority-0 and priority-1 rows;
the storage provider supplies the remaining priority-0 row. Those two callback
bodies remain real undefined dependencies, not fabricated implementations.

**2,456** direct stock/source comparisons pass with **8,848** SOC SVC75
fetches and **7,990** observer calls per implementation. Tests cover full-width
events, drained queues, empty ranges, live callback range changes and error
termination. **28** native range/set bytes and **16** typed observer bytes
are authenticated, plus the56-byte supplementary native entry, through
Ghidra-MCP.

All **69** real FIFO/storage workflows (**920** actions) now also pass through
the actual SOC poll and iterator: **748** SOC fetches and **290** flash SVC
calls per implementation. Real fstorage completion callback/state machine,
FIFO and atomics execute. SDH enable/continue, clock/DFU callbacks, application
callback and SVC replies remain fixtures. This does not prove physical IRQ
scheduling, persistence or fully integrated SDH continuation.

The combined board passes240 registration comparisons. Frontier totals are
**320 tested candidates,1,512 compiled hints,1,494 unresolved routes**.
Native clock observer0x907fc has an attributable next route in pinned
`nrf_drv_clock.c::soc_evt_handler` (HFCLK-started flag and notification); its
full control-block/dependency contract still requires implementation evidence.
The two SDH state callbacks, DFU/fault bodies, complete startup/linking, original
compiler identity and byte equality remain explicit gates.

### Legacy clock source selected

The unchanged pinned Nordic `nrf_drv_clock.c` supplies the clock SOC observer,
clock SDH state observer, init, LF request/release and notification/IRQ/enqueue
helpers. Its single20-byte control block matches native cold initialization at
`0x2002c154`. The SDK's unused observer registrations are excluded from the
selected object; existing typed native rows resolve to these C bodies.

A local logging macro contract routes the SDK init message through R1's
structured logger, preserving the native dynamic mode reads, marker, format,
function name and error description. SDK assertions are disabled to match
native unchecked counter/list behavior. Source bodies and included SDK headers
remain archive-authenticated; local configuration/helper changes are hashed.

**3,444** direct comparisons and **3,468** with actual SDK critical-region
instructions pass. Coverage includes both observers, canonical flags/enums,
wraparound counters, duplicate enqueue, list draining, callback insertion and
native short-circuit logging-mode reads. nrfx hardware calls and structured-log
outputs are fixtures; WDT register reads execute against emulated MMIO.

**72** storage/SOC/clock workflows (**941** actions) pass with the actual clock
observer and queued notifications: **766** SOC fetches and **294** flash calls
per implementation. These execute the real fstorage/FIFO/atomic/SOC/clock code;
SDH enabled/continue, DFU, application callbacks and SVC replies remain fixtures.
The combined board passes240 registration comparisons. Frontier totals are
**324 tested candidates,1,511 compiled hints,1,491 unresolved routes**.

Ghidra-MCP authenticates eight native spans and available accumulated
pseudocode is hash-bound. The notify entry `0x584ac` executes34 bytes including
the return at`0x584cc`; the manual ownership ledger records32. That ledger is
preserved and its row is not promoted from the newer contract. REA's init
lookup did not recognize`0x788c8`; its observed procedure inventory and failed
lookup are retained without claiming equivalent function boundaries.

Next providers are the four pinned `nrfx_clock.c` hardware entry bodies,
one remaining SDH state callback, DFU and fault handling. Full asynchronous
integration, real IRQ scheduling, startup/final linkage, original compiler
identity and image byte equality remain explicit gates.

Fresh REA notify receipt
`ev_717e883cc24df862748b9256e5ff83a623736a3e0323710765f6b950f6b36757`
confirms contiguous range`0x584ac..0x584cd` (34 bytes), the return instruction,
and both callback-list head references. It is hash-bound into clock evidence
and the audit; the older32-byte ledger discrepancy remains explicit.

### nrfx clock hardware source selected

The unchanged pinned `nrfx_clock.c` now supplies init, enable, LF-start and
LF-stop, including their real HAL/NVIC helpers. The shared graph no longer has
undefined references to these four APIs. Its eight-byte state block matches
native cold initialization at`0x20007938`.

Native bodies require RC source0, calibration state storage and IRQ priority6.
The historical SDK legacy defaults had overridden the recovered nrfx RC value
with source1 and omitted calibration storage. A scoped native contract restores
source0 and the calibration byte at control+6, with assertions disabled. `-O0`
preserves the contiguous eight-byte state instead of Clang scalar splitting;
this is a semantic/layout candidate, without original compiler identity proof.

**858** direct comparisons execute all selected C/HAL/NVIC bodies without code
or SVC fixtures. Exact register read/write traces, callback storage, control
bytes, start/stop ordering and bounded LFSTAT transitions match, including
**642** LF status reads per implementation. **3,468** legacy-clock comparisons
also pass with actual nrfx hardware and critical-region instructions, replacing
the previous hardware replies. A four-byte code pointer is identity-normalized;
SDH enabled replies, structured-log output and application callbacks remain
controlled boundaries. MMIO execution is not physical oscillator/IRQ proof.

Ghidra-MCP authenticates all four native spans; available accumulated pseudocode
is hash-bound. REA's retained observed procedure inventory has no distinct
entries for these addresses, so no REA function-boundary result is invented.
The combined board passes240 registration comparisons. Frontier totals are
**327 tested candidates,1,508 compiled hints,1,491 unresolved routes**.

Complete clock/shared POWER_CLOCK IRQ dispatch, calibration runtime, startup
vectors, DFU, the remaining state callback and fault handling remain source and
integration requirements. Original compiler/linker identity, physical behavior,
whole-image linking and byte equality remain open.

### POWER_CLOCK IRQ0 source and vector selected

The native IRQ0 entry at`0x30ac8` matches unchanged Nordic
`nrfx_clock.c::nrfx_clock_irq_handler`, exported by SDK macros as
`POWER_CLOCK_IRQHandler` when the separate power driver is disabled. Its154-byte
native body has the same four ordered event branches, anomaly201 duplicate-HF
suppression, anomaly192 register write, calibration state clear and callback
reload behavior. The application vector word at`0x27040` points to this entry;
a typed C configuration now supplies that single four-byte slot.

**4,896** direct comparisons pass with exact MMIO/callback/state traces and
**12,656** callback invocations per implementation. Another **4,896** comparisons
execute the actual legacy clock callback and notification bodies, producing
**10,828** application notifications per implementation. Coverage includes all
four event combinations with full-width nonzero values, interrupt-mask
independence, mutable later events, callback-pointer changes, HF suppression,
calibration completion and repeated IRQ invocations. Tests enter through the
compiled vector word; direct calls do not prove physical Cortex-M exception
entry/return, priorities or nesting. Application callbacks and registers are
controlled boundaries.

The older ownership row labels this entry product-specific POF behavior. New
attribution is recorded as an explicit correction in`irq-evidence.json`; the
original ownership CSV and its authenticated hash are preserved. The audit
checks the original row exactly, applies only routing/evidence fields, and
records the correction hash in the frontier summary. Ghidra-MCP authenticates
the body and vector; accumulated pseudocode and SDK sources are hash-bound.

The combined board passes240 registration comparisons. Frontier totals are
**328 tested candidates,1,508 compiled hints,1,490 unresolved routes**. Other
vectors, full startup/linking, asynchronous integration, physical clock behavior,
original compiler identity and byte equality remain open.

The remaining SDH state callback now has a concrete pinned upstream route:
`examples/ble_peripheral/ble_app_buttonless_dfu/main.c::buttonless_dfu_sdh_state_observer`.
On disabled state it writes the skip-CRC retention marker to GPREGRET2 and
requests system-off. That source route and the SDK power-management provider
are next; this observation alone does not implement or validate them.

### Buttonless-DFU state and power shutdown selected

The remaining typed SDH callback at`0x567ac` now compiles from the exact unchanged
function slice in SDK17.1.0's buttonless-DFU example. The builder authenticates
the archive/source/slice, generates an isolated translation unit with official
headers, and records its hash and compile command. An address-taking compile
anchor preserves the private function for compilation and is removed during
selection. The selected body aliases the existing native observer reference.

**6,144** direct comparisons cover zero-extended short-enum states, ignored
contexts, initial retention values and lower-call mutations. All24 disabled-state
cases write GPREGRET2=`BOOTLOADER_DFU_SKIP_CRC` before requesting SYSOFF.

Unchanged pinned `nrf_pwr_mgmt.c` shutdown/process and the SDK atomic swap now
join the shared source graph. A local INFO macro preserves R1's mode reads,
prefixed formats and argument-count marker, including evaluation of global
arguments after mode selection. A local reset macro forwards the original
shutdown-process caller to the real reset-capture dependency before the SDK
AIRCR reset request. No reset-capture or logger backend body is fabricated.

**1,432** direct power comparisons pass with the actual exclusive swap and
legacy iterator. They cover lock states, blocked/ready callbacks, continuation
cursor persistence, short-circuit logging, callback/mode mutations and terminal
SVC/register ordering. Twelve controlled failed exclusive stores per
implementation exercise retries with lock mutation. Terminal boundaries include
516 off and520 reset cases; execution stops at those register writes and does
not establish physical off/reset effects. All18 source-owned state bytes match
native cold initialization.

**1,864** combined comparisons pass, including **432** workflows through the
actual extracted DFU state callback and power implementation. The shared board
passes240 registration comparisons. Ghidra-MCP binds native spans and available
accumulated pseudocode; SDK headers/sources and local contracts are hash-bound.
Frontier totals: **331 tested candidates,1,506 compiled hints,1,489 unresolved
routes**. The example callback has no separate ownership row, so it does not
inflate these counts.

Logger panic/dequeue, reset-trace capture, authenticated shutdown-handler
records/ranges and power initialization remain requirements. DFU service/context,
full SDH/power integration, startup/linking, real retention/bootloader behavior,
original compiler identity and image byte equality remain open.

### Logger panic and shared source state selected

Unchanged pinned `nrf_log_frontend.c::nrf_log_panic` now resolves the power
shutdown flush path's panic call. Its compiled SDK backend helpers set autoflush,
enable each backend before its panic callback, and reload the next link after
the callback. The scoped frontend configuration uses the native4096-byte ring;
`-O0` keeps one contiguous source state object at`0x2002d60c`.

**600** comparisons and **1,078** backend callbacks per implementation pass,
covering empty/permuted lists, autoflush/enable byte values, and callback-driven
head/next changes. The4128-byte source footprint matches native cold RAM; this
does not establish the behavior/extent of every field unused by panic.

All **1,864** power/DFU comparisons now pass with actual panic/backend traversal,
including432 DFU callback workflows and **2,120** backend panic callbacks per
implementation. Application panic callbacks, dequeue, shutdown handlers, SDH
replies and reset capture remain fixtures; off/reset execution stops at terminal
register writes. Production backend configuration/transport remains a gate.

Fresh REA receipt
`ev_23cf09c62a513f336de2286d9417d6dd9980c3bf2598e38c514846d92378fd78`
confirms the contiguous38-byte native body, autoflush address and backend-head
access. Ghidra-MCP bytes, available accumulated pseudocode, SDK sources/headers,
object and receipt hashes are bound into the audit. The combined board passes
240 registration comparisons. Frontier: **332 tested candidates,1,505 compiled
hints,1,489 unresolved routes**.

A bounded search for shutdown configuration found no admissible static handler
set or initializer route. Literal occurrences and Ghidra xrefs are preserved in
`sdk-power-management/configuration-search.json`. This is not absence proof:
inlined, unindexed, computed, empty or RAM-built initialization remains possible.
No generic SDK initialization/table is added without native evidence.

Dequeue and standard-entry bodies, backend registration/transport, reset capture,
complete startup/linking, physical behavior, original compiler identity and
image byte equality remain open.

### Logger standard and dequeue frontend selected

The pinned Nordic frontend now supplies standard0..4, dequeue, preallocation,
empty detection, packet omission/skip, standard packing and dropped-count
saturation. Ghidra-MCP native bytes and accumulated pseudocode are retained for
all twelve additional contracts. **4,362** differential comparisons pass with
actual SDK atomic/critical instructions and **12,663** memory-object API calls
per implementation. Coverage includes ring wrap/overflow, in-progress entries,
allocation failure, hexdump clamping and callback-driven skip changes.

Source-owned configuration matches4,336 cold-zero bytes, the4-byte mask,
20-byte typed balloc descriptor and40 warning-string bytes. The combined board
passes240 registration comparisons; panic600 and real-panic power/DFU1,864
comparisons still pass. Frontier: **344 tested candidates,1,497 compiled hints,
1,485 unresolved routes**. These are bounded contracts, not instruction identity.

Memory-object allocation/get/put/write and backend callbacks remain fixtures.
Their bodies, initialization/registration and transports are the next provider
requirements. Power integration still fixtures dequeue. Whole-image startup,
linking, compiler identity, hardware behavior and byte equality remain open.

### Logger memory-object provider closure

Unchanged pinned Nordic `nrf_memobj.c` and `nrf_balloc.c` now supply allocation,
rollback/free, reference counting, reads/writes and pool initialization. The
subtract atomic is selected separately; existing add, critical-region and musl
copy providers complete the dependency closure. Source/header hashes are checked
against the authenticated SDK ZIP. Ghidra-MCP bytes and accumulated pseudocode
for eleven native routines are retained. `memobj_op` is inlined in this build
and receives no separate compiled-symbol promotion.

**3,870** comparisons across150 allocation workflows pass, covering exhaustion,
rollback, chunk boundaries, truncation and reference-counted release. The logger
frontend also passes all **4,362** comparisons with actual memory-object/pool
bodies and **12,645** memory-object API calls. Failure cases use a depleted pool;
backend callbacks remain fixtures. Native logger initialization and registration
still require contracts. The board resolves all four former memory-object
providers and passes240 registration comparisons.

Frontier: **354 tested candidates,1,487 compiled hints,1,485 unresolved routes**.
These tests use valid synthetic pool descriptors; concurrency, invalid pointers,
production backend transports, complete startup/linking, compiler/runtime
instruction identity, hardware behavior and image byte equality remain gates.

### Native logger initialization and backend registration

The unchanged SDK initializer, backend-add routine and ring-buffer initializer
now compile in the selected frontend. **427** comparisons pass with actual SDK
pool/critical/atomic providers, including repeat initialization over arbitrary
prior byte states, all256 push-control fill values, list insertion, ID gaps,
duplicate/out-of-range IDs and ten-backend exhaustion.

Native initialization sets autoflush to1, so the scoped configuration corrects
`NRF_LOG_DEFERRED` to0. The native push descriptor at`0x9c9e8` owns128 bytes at
`0x2002d574` and24 control bytes at`0x2002d5f4`; all152 cold-zero bytes and the
12-byte typed descriptor match. Timestamp and runtime filtering remain disabled.
Ghidra-MCP byte receipts and accumulated pseudocode support all three contracts.

The unoptimized initializer retains unused log-constant boundary calculations.
Its direct test binds those boundaries to zero without claiming production
metadata; they remain explicit unresolved symbols in the board bundle. Backend
records, callbacks/transports, registration callers and complete startup/linking
remain requirements. Hardware behavior, original compiler identity and image
byte equality are unproven.

Refreshed frontier: **357 tested candidates,1,484 compiled hints,1,485 unresolved
routes**. Corpus validation passes2,972 functions with exact-byte rebuild skipped.

### Native RTT backend and record selected

Unchanged pinned SDK RTT/default-backend sources now provide the typed RTT
record, callback API, default registration and write/retry state machine. The
native24-byte default initializer selects RTT only; the scoped configuration
therefore disables the seed UART backend. Native staging is4096 bytes, retry
count3 and delay1ms, forwarding64,000 cycles through an explicit lower provider.
The generic SDK embedded delay-machine-code helper is not retained.

**141** comparisons pass for registration/exhaustion, callback argument forwarding,
partial writes, initially absent/present host state, retries and timeout. The
4097 cold-zero bytes,8-byte initial control,16-byte record/name and12-byte API
match native data, with function pointers normalized. Ghidra-MCP native bytes
and available accumulated pseudocode are retained. The combined board passes240
registration comparisons. Frontier: **359 tested candidates,1,482 compiled hints,
1,485 unresolved routes**.

SEGGER RTT initialization/write, serial formatting and the cycle-delay body
remain unresolved providers and test fixtures. No physical debugger output or
elapsed delay is established. Private callback spans are supplemental evidence;
`serial_tx` at`0x8a5fc` matches the SDK but its product-specific ownership row is
preserved pending explicit attribution correction, so it is not promoted.
Whole-image startup/linking, metadata, compiler identity and byte equality remain
open.

### SEGGER RTT native initialization and upstream writer

Pinned unchanged `SEGGER_RTT_WriteNoLock` now resolves the RTT backend writer.
The bundled generic initializer differs from native behavior: it preserves
secondary control fields and assembles a shorter identifier. It is excluded.
A typed local C initializer implements the native120-byte full clear, two
up/down channels,512/64-byte terminal buffers and reversed16-byte identifier
copy. The source-owned terminal name and reverse identifier match native flash;
no executable blob or opcode provider is introduced.

**3,230** comparisons pass across every initializer fill byte, repeated direct
and thunk calls, two output channels, skip/trim/invalid modes, wrap and blocking
mode when sufficient space exists. All696 cold-zero bytes and25 readonly string
bytes match. **141** backend comparisons also pass with actual SEGGER init/write
and existing compiled memory routines. Fixed ring availability replaces the
scripted host fixture in that mode. The board resolves both SEGGER symbols.

Serial formatting and cycle delay remain lower providers. Blocking writes
waiting for debugger consumption, concurrent accesses, physical debugger output,
other SEGGER wrapper/read contracts, complete startup/linking, compiler identity
and image byte equality remain gates. The generic initializer must not be
reintroduced through another SDK wrapper without checking its native contract.

Combined board validation passes240 registration comparisons. Refreshed frontier:
**362 tested candidates,1,479 compiled hints,1,485 unresolved routes**.

### Serial log dispatcher selected

Unchanged pinned `nrf_log_backend_serial_put` now resolves the RTT backend's
serial dispatcher. **3,312** comparisons and **7,680** formatter callbacks per
implementation pass using actual SDK memory-object allocation/read/get/put,
atomic/critical and compiled memory routines. Cases cover standard0..6 arguments,
all severities, dropped/module fields, hexdump8-byte chunk boundaries, zero-length
hex, unknown packet types, multiple output-buffer sizes and reference release.
Ghidra-MCP194-byte native evidence and accumulated pseudocode are retained.

Standard/hexdump formatting calls remain fixtures. The native two-word header
omits timestamp while the SDK header type has a timestamp field; timestamp is
disabled, and unused timestamp/padding bytes are excluded from the comparison.
No emitted text, full pipeline or physical transport proof follows from these
checks. The combined board passes240 registration comparisons. Frontier:
**363 tested candidates,1,478 compiled hints,1,485 unresolved routes**.

The next formatter dependencies are `nrf_log_std_entry_process` and
`nrf_log_hexdump_entry_process`; cycle delay, metadata, complete startup/linking,
compiler identity, hardware behavior and image byte equality remain gates.

### Standard/hexdump formatters and native prefix selected

The original SDK standard, hexdump and postfix bodies now compile with an
explicit replacement of the SDK prefix. The generated source is bound to the
SDK original bytes, removed prefix span and exact replacement declaration. The
local R1 prefix prints native`E/W/I/D` labels and packed local month/day/time,
with dropped-message/color handling. Calendar and color lookup remain provider
boundaries. An ASCII printability helper matches the native hexdump behavior
through all256 input byte values, avoiding a toolchain-specific ctype-table ABI.

**1,894** comparisons and **17,298** printf calls per implementation pass across
argument cases, severities, colors, dropped counts, packed date fields,
autoflush restoration and postfix behavior. The serial dispatcher additionally
passes **2,496** comparisons with actual formatters and **5,760** formatter
invocations. Printf/flush and calendar/color calls remain fixtures; no emitted
byte stream follows from these checks. The native timestamp remains unused.

The SDK36-byte color-pointer table is placed at its authenticated native RAM
address and compared by all nine pointed-to strings. Board registration still
passes240 comparisons. Frontier: **367 tested candidates,1,475 compiled hints,
1,484 unresolved routes**. Ghidra-MCP bytes and accumulated pseudocode are bound
for the four admitted contracts.

Printf/flush, the native calendar ABI adapter, module color lookup, cycle delay,
metadata and complete pipeline/startup/linking remain requirements. The existing
calendar reconstruction takes an explicit context and cannot satisfy the native
single-output-pointer ABI without further source-owned binding evidence.
Physical behavior, original compiler/link identity and byte equality remain open.

### Pinned printf providers and emitted formatter bytes

Unchanged SDK printf wrappers, parser, byte writer and integer/string machinery
now resolve `nrf_fprintf` and `nrf_fprintf_buffer_flush`. Native configuration
inserts CR before every LF and disables double formatting. **3,949** comparisons
match **53,516** sink bytes per implementation, covering public/direct-va-list
entry, signed extremes, padding/precision, strings, pointers, unsupported formats,
all256 byte-writer inputs and buffer/flush boundaries with compiled strlen.
Ghidra-MCP byte receipts and accumulated pseudocode support six contracts.

The standard/hexdump formatter additionally passes **1,625** comparisons with
actual printf/flush, matching **84,010** bytes across **1,196** sink callbacks.
Severity0 prefixes contain a null label and are excluded from this valid-string
byte-stream scope; the earlier formatter-call tests retain their broader control
scope. Calendar/color remain fixtures. CR insertion is compared exactly rather
than normalizing newline output.

The board resolves both printf symbols and passes240 registration comparisons.
Full frontend/serial/RTT integration, actual calendar/color providers, cycle
delay, metadata, startup/linking, physical output, compiler/runtime identity and
image byte equality remain requirements. Byte-sink proof is not device proof.

Refreshed frontier: **373 tested candidates,1,470 compiled hints,1,483 unresolved
routes**. Corpus validation passes2,972 functions with exact-byte rebuild skipped.

### Typed logger module metadata and color lookup

The unchanged SDK color lookup now resolves `nrf_log_color_id_get`. Source-owned
C defines32 typed module records with native names and four severity/color
fields. All256 record bytes and311 name bytes match the authenticated image.
**33,056** comparisons cover original records, every possible info/debug color
byte in every row, constant error/warning precedence and valid8-bit severities.
Ghidra-MCP authenticates the native42-byte lookup and256-byte record span.

The native start literal is explicit. The end of this32-record source span
abuts the authenticated balloc record; original end-linker-symbol identity and
completeness beyond the span remain unproven. Compiled boundary symbols describe
the source-owned array and resolve the previously unused initializer boundary
references without claiming original linker-map proof.

Formatter integration now passes **1,625** comparisons with actual printf and
module lookup/metadata, matching **83,470** bytes across **1,192** sink callbacks.
Calendar remains a fixture. The board retains the typed table explicitly,
compares every record/name, and passes240 registration comparisons. Frontier:
**374 tested candidates,1,469 compiled hints,1,483 unresolved routes**.

Native calendar ABI, cycle delay, full pipeline/startup/linking, physical output,
original compiler/runtime/link identity and image byte equality remain gates.

### Native cached calendar ABI selected

The native calendar at`0x8ac28` now has a single-output-pointer C provider using
the existing shared timestamp thunk and state. It reuses the recovered Gregorian
converter internally, preserving signed timezone/day division, cache behavior
and the native unsigned remainder quirk. The old contextual calendar entry is
not used as an ABI-compatible replacement. Timestamp backend registration stays
an external requirement.

The provider writes **eight** packed bytes, including weekday. The prefix's
former seven-byte buffer, sufficient only for the earlier getter fixture, has
been corrected to eight. Direct tests check the complete output and surrounding
canaries. **2,257** comparisons pass, including3,441 timestamp callbacks per
implementation, timezone extremes, negative local time, date/cache rollover,
null/unregistered output and callback-driven timezone mutation. Existing52-byte
shared cold-zero state matches native RAM. Ghidra-MCP202-byte native evidence
and accumulated pseudocode are bound into the audit.

Formatter integration with actual calendar, module lookup and printf passes
**1,625** comparisons, matching **83,470** bytes across **1,192** output callbacks
and **1,300** timestamp-getter callbacks. The getter is a fixture, not real RTC
proof. All earlier formatter/serial receipts were refreshed after the buffer
correction. The board resolves the calendar symbol and passes240 registration
comparisons. Frontier: **375 tested candidates,1,468 compiled hints,1,483
unresolved routes**.

The Gregorian helper's native standalone pointer ABI is not separately admitted
by its internal use here. RTC registration, full frontend/serial/RTT integration,
cycle delay, startup/linking, physical behavior, original compiler/runtime
identity and image byte equality remain gates.

### Source-compiled ARM delay primitive

The remaining RTT delay dependency now resolves to a C compilation unit with
three explicit ARM mnemonics, matching the pinned SDK instruction contract:
subtract3, branch unsigned-higher, return. It keeps16-byte alignment and emits
no executable-data array. Ghidra-MCP authenticates **21** native six-byte clone
spans; all match the source-compiled primitive byte-for-byte.

**1,215** comparisons match registers, NZCV flags and exact loop/instruction
counts, executing **1,762,961** instructions per implementation. The RTT backend
passes **141** comparisons with actual delay execution, including retry paths.
Existing fixture and actual-SEGGER suites also pass. The canonical board has no
`delay_machine_code` symbol, resolves the delay provider, and passes240 registry
comparisons. Frontier: **396 tested candidates,1,468 compiled hints,1,462
unresolved routes**.

The native clone entries share a tested source provider; their distinct final
image placements/duplication are not supplied by this relocatable build. Local
six-byte identity does not establish whole-firmware identity or hardware delay.
Elapsed time, real clock frequency, cache/flash wait states and interrupts remain
hardware gates. Complete frontend/serial/RTT/clock integration, startup/linking,
original compiler identity and bundle byte equality remain unresolved.

### Source logger graph to actual RTT ring

`python3 r1/tools/verify_native_board.py --logger-pipeline` now exercises the
assembled source graph against native execution. It runs actual logger/default
backend initialization, standard0..4 serialization, dequeue, memory-object/pool
operations, typed RTT callbacks, serial dispatch, formatter/calendar/printf,
delay and SEGGER ring writes. Unresolved board seams remain traps and are not
executed. Driver and complete board-report hashes bind the receipt.

**954** comparisons across **36** workflows and **540** standard messages pass.
Native and source accept **19,920** bytes into the RTT ring across **564** write
attempts, with **360** timestamp-getter callbacks. Tests cover immediate/deferred
logging, three timezones/severities, between-call host consumption and bounded
backpressure/retry behavior. Full defined logger/pool/backend/calendar/ring state
and accepted bytes match after every public call. Persistent format strings are
kept separate for each argument count so deferred packets retain valid input.
The board's240 registry comparisons also pass in the same run.

The clock getter and its registration binding are fixtures; logger backend
records/API are actual compiled source. Host consumption is controlled between
public calls, not a live debugger. Only valid standard0..4 packets and bounded
sequential traces are admitted. Hexdump producer/other frontend selection, real
RTC registration, concurrency, elapsed hardware timing, complete application
startup/linking, duplicate placement, compiler identity and firmware byte equality
remain gates. Frontier remains **396 tested candidates,1,468 compiled hints,
1,462 unresolved routes**.

### Remaining standard wrappers and hexdump producer selected

Unchanged SDK standard5/6 wrappers and the hexdump producer now compile into the
selected frontend. Ghidra-MCP160-byte hexdump and28-byte wrapper spans plus
accumulated pseudocode support the three additional contracts. **8,922** direct
comparisons pass in both fixture and actual memory-object modes, covering the
new argument wrappers, word/byte ring wrap, saturation, overflow, memcpy and
hexdump serialization/consumption. Actual mode executes **27,309** memory-object
API calls; fixture mode executes27,327. Compiled memory providers supply memcpy.

The producer accepts16-bit lengths but packs ten length bits. Lengths1024..4088
are therefore deferred-only packing comparisons; they do not admit consumption
of wrapped/malformed headers. Oversized/nonterminating allocation and corrupted
streams remain explicit gates rather than being normalized to safer semantics.

The complete logger test now passes **2,034** comparisons across36 workflows,
**756** standard messages and **504** hexdumps. It matches **76,396** accepted RTT
bytes across **3,144** write calls and **1,968** timestamp callbacks. It exercises
actual standard0..6/hexdump producers, pool, serial/format/calendar/printf, RTT
and delay bodies; clock getter/registration and between-call host consumption
remain fixtures. The board also passes240 registry comparisons.

All affected panic, initialization, memory-object, power/DFU, backend and serial
receipts are refreshed. Frontier: **399 tested candidates,1,465 compiled hints,
1,462 unresolved routes**. String push/other frontend APIs, real RTC registration,
concurrency, hardware timing/output, complete startup/linking, duplicate placement,
original compiler/runtime identity and whole-firmware byte equality remain open.

### Clock bootstrap and distinct snapshot registration

A bounded literal/registered-xref search found only initializer/descriptor
references for the SDK string-push buffer and no admitted native `nrf_log_push`
entry. The receipt is`sdk-logger-frontend/string-push-search.json`. Computed,
inlined or unindexed uses may exist; no absence proof is claimed and an unused
SDK API is not invented as a mandatory firmware component.

The RTC trace instead recovered a supplemental136-byte bootstrap at`0x8adc0`,
snapshot binder/default accessor and tick callback. Snapshot registration at
`0x20006830` differs from the timestamp fast binding at`0x20006828`; context is
at`0x20006834`. C bodies and typed32-byte default backend/eight-byte initial
configuration now compile using the existing shared globals, timestamp adapter,
registry and memory providers. Five port callbacks remain explicit dependencies.

**2,501** comparisons and **1,452** callback calls per implementation pass.
Tests preserve the exact snapshot flag predicate, early-return/partial failure
state, separate fast/snapshot slots, callback ordering, zero-extended initial
timezone and incoming-R1 fallback context. The tick compares the getter result
to initial epoch but publishes incomingR0 with length1. The32-byte table matches
with normalized function pointers; all eight default configuration bytes and60
shared cold-zero bytes match.

Ghidra-MCP bytes and Thumb extracts authenticate the supplemental spans. Ghidra
has no function boundary for the bootstrap; that limitation is recorded. Only
the existing snapshot ownership row is promoted; supplemental bodies do not
inflate ledger counts. The logging pipeline still passes2,034 comparisons and
76,396 accepted RTT bytes; board registration passes240 comparisons. Frontier:
**400 tested candidates,1,465 compiled hints,1,461 unresolved routes**.

Default-port update/tick binding/other slots, real RTC device setup, initialization
call-site ABI/startup order, event transport, full linking, physical behavior,
original compiler identity and whole-firmware byte equality remain gates.

### Native RTC request ports

`native-clock-port/clock-port.o` now provides the default backend update,
64-bit read slot and tick binder, plus the underlying 64-byte write request and
registry callback binding. Ghidra-MCP byte receipts and Thumb extracts bind all
six native spans, including the read-slot tail thunk. The existing compiled
registry and memory providers execute in **720** native/source comparisons.
Tests compare every request byte, low-16-bit timezone truncation, ignored backend
status, both return registers of the 64-bit read, and absent operation handlers.
Only the device operation remains a fixture. These are owner-authorized native
reconstructions; no additional upstream library is attributed to these wrappers.

The board now resolves three of the five default backend ports. Calendar output
and calendar input slots remain unresolved; the already reconstructed Gregorian
converters are candidates for the next native ABI checks. Real RTC bodies,
startup/device discovery, full linking, instruction identity and physical RTC
behavior remain explicit gates. The original snapshot/bootstrap unit continues
to use bounded port fixtures; the port unit supplies its separate contract proof.

After port integration, the frontier is **404 tested candidates, 1,465 compiled
hints and 1,457 unresolved routes**, accounting for all 3,326 ownership entries.
Four existing ownership rows advance; supplemental read/tail spans do not add
rows. The integrated pipeline remains at 2,034 comparisons / 76,396 accepted
RTT bytes and the board registry at 240 comparisons. `make -C r1 test` verifies
2,972 corpus functions; byte-identical firmware rebuilding is still skipped.

### Native clock calendar ports and converter admission

`native-clock-calendar/clock-calendar.o` closes the two remaining default clock
backend slots: output at `0x50d64` and input at `0x50d8a`. It selects three
unchanged function slices from the accumulated `time_calendar.c` reconstruction:
the validating inverse Gregorian converter, packed-calendar-to-UTC adapter and
UTC-to-packed-calendar adapter. The generated source preserves the source prefix
and records slice offsets/digests; the audit checks exact regeneration. The
existing compiled forward converter remains a shared provider, avoiding a second
copy or a falsely promoted native pointer ABI.

**45,233** native/source comparisons pass, with **19,677** bounded device
callbacks per implementation. Checks include every accepted year (1970–2029),
every month and boundary day values, invalid fields, signed timezone adjustment,
32-bit epoch wrap, full eight-byte output plus canaries, null arguments, complete
64-byte RTC requests, status ignoring and shared-state preservation. The output
slot uses the raw RTC epoch and zero timezone. Rejected non-null input still
writes epoch zero, then returns success. Lax native day validation is retained.

Ghidra-MCP authenticates the converter/port spans and inverse month table. Fresh
REA/Ghidra evidence `ev_e9dbd05920f8c091d7592fb6d10da0df7f76a3cdda6d024a0e61233024ada3e9`
confirms the inverse converter's contiguous 216-byte native body; profile
`7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de` is pinned.
The bootstrap verifier also passes **2,501** comparisons with actual clock ports
linked (`--real-ports`), leaving 300 underlying device/custom-backend/event
callbacks. All eight default backend slots resolve to C in the board object.

The integrated logger pipeline remains at **2,034** comparisons / **76,396**
accepted RTT bytes; board registration passes **240** comparisons and the corpus
check verifies **2,972** functions (byte-identical rebuild skipped). The current
frontier is **407 tested candidates, 1,464 compiled hints, 1,455 unresolved
routes**, accounting for all 3,326 ownership entries. Three existing converter
rows advance; the supplemental port bodies do not inflate the ownership count.

The RTC device operations remain bounded fixtures/absent operations here. Their
older contextual reconstruction deliberately scans more records and adds null
handling, so it cannot be promoted unchanged as a native ABI provider. Device
startup/discovery, full RTC interrupt behavior, physical timing, complete linking,
original compiler identity and whole-image byte equality remain explicit gates.

### Native RTC device snapshot, record writes and callback binding

`native-rtc-device/rtc-device.o` admits the native request ABI at `0x5639c`,
calendar-record write at `0x563f8`, and callback binding at `0x56444`. These
source bodies retain the native single-record scan and unchecked pointer
behavior rather than the contextual reconstruction's deliberate full scan and
extra null guards. Source-owned counter state (8 bytes), record (88 bytes), and
`sys rtc` name (8 bytes) match native cold initialization. The typed record
includes RTC register base `0x40024000`, IRQ36, instance0 and four channels.
No RTC operation table or device registration is inferred from those bytes.

The native snapshot writes only epoch at +44 and milliseconds at +56, retaining
all other request bytes. Milliseconds are computed with 32-bit wrap before
zero-extension. Calendar writes preserve overlapping `memmove` semantics across
all 44 bytes; callback binding accepts zero to clear the pointer. All three
bodies leave the adjacent second-record canary untouched.

The newly selected overlap-safe provider is unchanged musl `memmove` from the
existing v1.2.5 commit `0784374d561435f7c787a555aeab8ede699ed298`, retrieved from
the primary upstream, with separate subset provenance/COPYRIGHT. This does not
change the existing runtime pin or claim original Arm runtime identity. The
native helper at `0x2775c` returns source on its backward-overlap path and
destination-end on its forward path; `native_memory_move.c` preserves that
observed R0 contract over upstream `memmove`. The standard C return value alone
failed the direct native ABI test, so it was not admitted as that helper.

**5,344** native/source comparisons pass, including **1,820** direct movement
cases over all four alignments, both overlap directions, self-copy and lengths
0–64. Ghidra-MCP bytes/Thumb extracts bind all four function spans and the name.
Cold data, complete requests/records, canaries, name mismatch, opened flags,
callback clearing and snapshot overflow are checked with actual C memory/string
providers. RTC open, epoch initialization, interrupts, registration/discovery,
physical timing and full-image linking/identity remain explicit gates.

The assembled logger verifier now executes the real RTC snapshot, registry
request dispatch, timestamp adapter and default backend getter. Getter-result
interception is removed; only registration bindings, emulated counter updates
and between-call host draining remain controlled inputs. All **2,034** pipeline
comparisons pass with **76,396** accepted RTT bytes and **1,968** observed RTC
reads per implementation. The board also verifies all 104 cold RTC bytes before
running its 240 registry comparisons. These checks do not establish RTC device
registration/startup or hardware timekeeping.

The audited frontier after RTC/movement integration is **411 tested candidates,
1,465 compiled hints and 1,450 unresolved routes**, accounting for all 3,326
ownership entries. `make -C r1 test` still verifies 2,972 corpus functions and
skips byte-identical firmware reconstruction. Next providers are the native RTC
open/tick/epoch-initialize paths and pinned Nordic `nrfx_rtc` bodies/configuration.
The discarded epoch conversion must retain the native toolchain `gmtime` ABI
and any shared-state effects; ignoring its result is not proof it has none.

### RTC lifecycle, shared breakdown state and native startup ports

`native-rtc-lifecycle/rtc-lifecycle.o` now contains native-contract C for the
unsigned breakdown helper (`0x276c8`), 44-byte calendar adapter (`0x562e0`),
tick (`0x56274`), epoch initialization (`0x5649c`), named open (`0x56318`),
and supplemental registrar (`0x563c4`). The actual shared counter/record,
registry and string/movement providers link with it. Four explicit driver/error
bridges remain unresolved: initialize, tick-enable, enable and error handling.
Those calls are bounded fixtures in this unit's verifier, not production bodies.

**51,592** native/source comparisons pass. They include all 49,711 day boundaries
of the unsigned 32-bit epoch range, random epochs, the 2100 four-year-cycle
behavior, signed offset wrap, divider values through 65,535, alarm match/miss,
75 observed alarm calls, epoch-init partial failures, named open/status ordering,
11 driver/error calls, and empty/duplicate/append registry registration. The
breakdown helper returns its actual shared 32-byte buffer at `0x20037e88` and
uses the native four-year cycle; it is not replaced by the separate Gregorian
converter. Epoch initialization preserves the discarded conversion's shared
buffer side effect. The adapter writes the eight used words and leaves all
three padding words untouched. The tick resets its divider after the callback.

Source-owned defaults match all eight native bytes at `0x9a638`; open replaces
only the prescaler with 4095. The complete nine-word RTC operation table matches
36 bytes with function pointers normalized; its native RAM location is
`0x200073dc`. Ghidra-MCP bytes/Thumb extracts authenticate functions, table inputs
and constants. REA's fresh lookup has no indexed procedure for `0x276c8`; the
negative receipt is preserved rather than inventing a decompiler result.

The registrar ownership row lists 44 bytes, but a 2-byte return at `0x563f0`
extends its code to 46. Its supplemental 52-byte span includes padding/literal;
this discrepancy remains an explicit gate and its original ownership row is
not promoted. Five other rows advance. Frontier: **416 tested candidates,
1,465 compiled hints, 1,445 unresolved routes** across all 3,326 entries.

The assembled RTC-to-logger pipeline still passes 2,034 comparisons / 76,396
accepted RTT bytes, board registry passes 240 comparisons, and the corpus check
verifies 2,972 functions (exact-byte reconstruction skipped). Actual Nordic RTC
bodies, error handling, real RTC registration/startup and interrupts, physical
behavior, final linking, original compiler identity and whole-image equality
remain gates. Native Nordic RTC functions also contain structured logging;
compiling generic SDK bodies with logging removed cannot close that contract.

### Pinned Nordic RTC startup providers and canonical error reuse

`sdk-nrfx-rtc/nrfx-rtc.o` selects unchanged SDK 17.1.0 `nrfx_rtc_init`,
`nrfx_rtc_enable` and `nrfx_rtc_tick_enable`, plus typed native bridge bodies.
Every included SDK source/header is authenticated against the pinned ZIP.
Scoped configuration disables assertions and the invalid-state warning absent
from native code. A local info adapter preserves native structured logging,
error-string lookup ordering and repeated mode reads; generic disabled logging
is not used as a substitute. The single 3-byte control block at `0x20007950`
and 4-byte handler slot at `0x20007954` retain their original layout.

**6,272** comparisons pass across SDK entries and all three bridge entries.
They compare ordered peripheral/NVIC writes, complete mapped register pages,
state/handler storage (including handler replacement before a repeated-init
failure), prescaler, priority, reliability, latency, tick enable flags, dynamic
mode sequences and formatted log arguments. Ghidra-MCP byte/Thumb receipts
bind the three native functions and all 78 info-format string bytes.

The returning fatal logger at `0x4e5bc` was already provided by
`stock_seams.c:r1_adc_error`. The canonical board now binds
`r1_rtc_driver_error=r1_adc_error` and asserts identical symbol addresses. It
does not link the duplicate independent reference object. That reference is
explicitly marked `reference_only` and supplies **2,560** additional all-three-
mode-read sequence comparisons, including both exact producer words and all
66 native error-string bytes. The existing ownership row keeps its original
board-seams contract rather than being promoted a second time.

RTC lifecycle also passes **51,592** comparisons with actual SDK bridge/driver
bodies and the separately validated native error reference linked
(`--real-driver`). It covers 75 bounded alarm calls and 11 real driver/error
entries; mode-zero lower logging, emulated MMIO and callback fixtures remain
explicit. The four RTC startup provider names now resolve in the canonical
board. The reference helper is a comparison instrument, not another canonical
firmware body or a native-address-placement claim.

RTC2 interrupt dispatch/vector, startup/discovery ordering, live NVIC behavior,
real peripheral timing, full application linking and byte identity remain gates.
The native IRQ36 vector at `0x270d0` points to `0x31750`; its shared dispatcher
at `0x7294c` is the next SDK/native contract to check. No complete RTC interrupt
or hardware proof follows from the startup entry tests.

After RTC provider integration, all 3,326 ownership entries are accounted for:
**419 tested candidates, 1,465 compiled hints and 1,442 unresolved routes**.
The three Nordic RTC rows advance; the existing fatal-logger row is not counted
again. Canonical logger pipeline remains 2,034 comparisons / 76,396 accepted
RTT bytes, board registration remains 240 comparisons, and corpus verification
remains 2,972 functions with exact-byte reconstruction skipped.

### Pinned RTC interrupt dispatcher and source-owned IRQ36 vector

The unchanged pinned SDK RTC translation unit now also selects `RTC2_IRQHandler`
and its common dispatcher. The private dispatcher is renamed/globalized as
`r1_sdk_rtc_irq_dispatch` for stable evidence attribution; no vendor body is
rewritten. `native_rtc_vector.c` supplies the four-byte vector at `0x270d0`,
matching native `0x31751` after function-pointer normalization. No native debug
logging occurs in this dispatcher, and the selected SDK code has no unresolved
IRQ-side logging providers.

**65,536** native/source IRQ comparisons pass with **82,660** callback calls per
implementation. They cover all six-event enable/pending masks, compare-channel
bounds 0/1/4, nonzero event values, ordered peripheral writes and compare/tick/
overflow callbacks. Callback fixtures can disable later interrupts, enable/set
later events, or replace the handler. An explicit W1C model applies interrupt
and event disable writes; the model itself is not physical hardware evidence.

`verify_sdk_rtc_irq.py --real-tick` additionally passes **16,384** comparisons
with **16,245** bounded alarm/handler-replacement callbacks. The actual compiled
RTC tick and shared native calendar execute as SDK callbacks. Counter, divider,
record and shared-breakdown bytes compare after each IRQ; event acknowledgments
and callback order remain native-equivalent in these sequential traces.

Ghidra-MCP authenticates the vector, 16-byte wrapper span, and common dispatcher
plus its literal pool. The wrapper ownership row claims 162 bytes, while native
execution uses ten code bytes, two padding bytes and one four-byte literal. That
row remains held. Current Ghidra has no registered wrapper function, and the
saved REA procedure inventory has neither wrapper nor shared dispatcher; those
limits are recorded, not treated as absence of native code. The common dispatch
row's 154-byte body matches its native boundary and advances independently.

SDK startup (6,272 comparisons), lifecycle with actual SDK/error reference
(51,592), RTC-to-logger integration (2,034 / 76,396 accepted RTT bytes), board
registration (240), and corpus checks (2,972; exact-byte rebuild skipped) pass.
Current frontier: **420 tested candidates, 1,464 compiled hints, 1,442 unresolved
routes** across all 3,326 ownership entries.

Physical interrupt delivery/preemption, peripheral timing, startup/discovery
ordering, the oversized wrapper ownership gate, final linking and complete
firmware byte equality remain open. Next source work is RTC cached discovery
and registration/startup composition; this IRQ proof does not establish them.

### Native cached RTC discovery and composed startup graph

`native-rtc-discovery/rtc-discovery.o` supplies the native 20-byte lazy-cache
contract at `0x50dc0`, using the existing actual registry and shared handle.
Its compiled eight-byte name matches `sys rtc` at `0x50dd8`. Ghidra-MCP/Thumb
receipts bind the lookup, literal/name, and native peripheral-init caller at
`0x50384`; this caller alone does not prove complete device startup ordering.

`verify_native_board.py --rtc-startup` performs **960** native/source comparisons:
240 cache checks and 48 composed workflows. Cache tests include missing names,
multiple matching nodes, failed-lookup retries, non-null sentinel values, changed
registries and invalid heads safely ignored after caching. The composed path uses
actual C registration, lookup, generic open dispatch, SDK startup, default clock
initialization, RTC request/getters, eight IRQ ticks, native calendar and the
clock's second-change callback. It reaches **14** matching event-publish calls.
Complete shared states, normalized callback pointers and ordered peripheral/NVIC
writes compare after public calls. The compiled lookup-name bytes are extracted
from a temporary object copy; the provider object is never rewritten by objcopy.

The harness controls zero log mode and models W1C effects; event publication is
a bounded boundary fixture. This is a selected source-composition sequence,
not proof of the firmware's actual boot order, event transport or hardware
interrupt delivery. Registration and IRQ wrapper ownership extents remain gated.

The combined RTC/startup + logger run passes, with 2,034 logger comparisons /
76,396 accepted RTT bytes and 240 board registration comparisons. Corpus checks
still cover 2,972 functions and skip exact-byte reconstruction. Frontier:
**421 tested candidates, 1,464 compiled hints, 1,441 unresolved routes** across
all 3,326 ownership entries. No new upstream library is attributed to the local
cache; it remains owner-authorized native reconstruction.

A bounded aligned-literal scan finds the RTC registrar pointer `0x563c5` at
`0xc454c`, among 14 candidate registration pointers at `0xc4530..0xc4567`.
The table's actual runner/bounds and surrounding initialization stages are the
next evidence route; pointer occurrence and adjacent section metadata alone do
not establish its complete boot contract.

### Authenticated device initcall table and interrupt-mask wrapper

`native-initcalls/initcalls.o` now supplies the native three-range runner at
`0x5cb6c`, empty post-init runner at `0x5cb4c`, and supplemental boot wrapper
at `0x4e1e4`. Ghidra-MCP literal reads correct the earlier pointer-span hypothesis:
the device table is **13 entries / 52 bytes at `0xc4534..0xc4567`**, excluding
the preceding pointer at `0xc4530`. The first two runner ranges and the post-init
range have start/end zero. Source-owned absolute boundary symbols preserve those
empty range values without claiming the original linker's symbol identities.

The C table names the real registrar providers. Nine already resolve in the
canonical board: ADC, internal flash, GPIO, RTC, software TWI2–5 and watchdog.
Four remain explicit unresolved symbols: hardware-TWI primary/secondary, PWM
registration and YHM2710 registration. This configuration does not substitute
traps, numeric executable arrays or fixtures for their production bodies.

**54** native/source comparisons and **12** injected-null-target fault checks
pass, reaching **540** callback invocations per implementation. Tests prove all
13 calls execute in order despite nonzero return statuses, the native slot-
address test does not silently skip a null function word, and constructor mask
changes propagate. The boot wrapper uses explicit target IRQ disable/enable
primitives and unconditionally enables interrupts after initialization; it does
not restore the incoming mask. All registrar bodies are fixtures in this unit's
control-flow proof. The board separately authenticates all 52 table bytes with
function-pointer normalization; it does not execute the four missing bodies.

Fresh REA/Ghidra evidence `ev_dc1a5c9e730bc9fc42c22beaf99577120be6896a33175d349d3e9ff5bf3b1aaa`
confirms the post-init helper's contiguous22-byte body under the pinned fresh
profile. Native bytes at `0x75fa0` show boot-wrapper invocation immediately
before peripheral-module discovery. This narrows registration/discovery order;
RTC open/clock startup ordering and full boot execution remain separate gates.

The main runner's58-byte ownership row advances. The boot wrapper's inventory
size40 overlaps later code; its authentic18-byte body uses a supplemental
symbol and the original row remains held. Post-init likewise remains a
supplemental body rather than an invented inventory entry.

The canonical logger (2,034 comparisons /76,396 accepted RTT bytes), RTC/startup
composition (960 comparisons /14 event-publish calls), board registry (240)
and corpus checks (2,972; exact-byte rebuild skipped) all pass. Frontier:
**422 tested candidates, 1,464 compiled hints, 1,440 unresolved routes** across
all3,326 ownership entries. Next work is the four registrar/provider bodies,
followed by executing the full authenticated device-initcall stage. Hardware,
complete boot, whole-image linking and byte equality remain open.

### Hardware-TWI registration bodies and source-owned cold configuration

`native-hw-twi-registration/hw-twi-registration.o` implements the constructors
at `0x54f90` and `0x54fc4`. It owns two typed108-byte clusters at `0x20006fe8`
and `0x20007054` and the native `i2c_0`/`i2c_1` names. All216 configuration bytes
match after authenticated native reset, with ten function pointers normalized;
all12 name bytes match exactly. Operation/event-callback fields are symbol
bindings only: their declarations are not body or parameter-ABI admission.

**864** native/source comparisons pass with **864** semaphore calls per
implementation, using actual C registry/strcmp and a bounded `osSemaphoreNew`
fixture. Tests cover empty/duplicate/append registry states, repeated calls,
semaphore success/failure transitions, raw flag values, opened state, previous
handles and surrounding canaries. Native calls `osSemaphoreNew(1,0,NULL)` after
registration regardless of its result; successful allocation sets primary flag
+2 or secondary flag+1. Failure overwrites the handle with null but leaves the
previous flag unchanged. Return is a boolean allocation result, not the handle.

Both registrar names now resolve in the canonical board and in the thirteen-
entry table. `osSemaphoreNew` and eight transfer/lifecycle plus two event-callback
bodies remain explicit providers; their numeric pointer matches do not prove
source completeness or I2C behavior. The callbacks at `0x70778`/`0x707cc` are
IRQ-driven completion/error callbacks, not evidence of the hardware vector ABI.

The earlier PWM label for registrar `0x54e78` was incorrect. Native record names
are `ppg_led_en`, `touch_ldo_en`, `ppg_reset_en`, `ship_mode_en`, `touch_rdy_out`,
and its adapters call GPIOTE output helpers. The source-owned initcall reference
is now `r1_native_output_gpio_registration`. No original ownership row was
rewritten. GPIO-output and YHM2710 registration are the two remaining initcall
registrar bodies; prior PWM references describe the superseded hypothesis.

The initcall checks (54 normal /12 fault cases), logger pipeline (2,034 /
76,396 accepted RTT bytes), RTC/startup composition (960 /14 publish calls),
board registry (240) and corpus checks (2,972; exact-byte rebuild skipped) pass.
Frontier: **424 tested candidates, 1,464 compiled hints, 1,438 unresolved routes**
across all3,326 entries. Hardware transfers, actual semaphore allocation, complete
initcall execution/boot, final linking and whole-image byte equality remain open.

### GPIO-output and STACMD registrar/configuration closure

`native-output-gpio-registration/output-gpio-registration.o` supplies the
supplemental five-record registrar at `0x54e78`. It owns five56-byte records,
a six-entry driver descriptor and nine-word operation table: all340 bytes match
native cold state after pointer normalization. Five exact names and pins10,
30,36,9,17 are source-owned; uninterpreted config fields remain named by offset,
not assigned guessed hardware meanings. The constructor registers all five
records even after duplicate failures and returns the final registration status.

`native-stacmd-registration/stacmd-registration.o` supplies the native registrar
at `0x565f4`, its108-byte `device_stacmd` record and native microsecond-delay
adapter. Six callback fields reuse existing unmodified Nordic inline GPIO HAL
providers. The delay adapter uses the already admitted six-byte native delay
kernel with unsigned `us << 6`, including wrapped-zero inputs. No duplicate HAL
body or opaque executable data is introduced.

The joint verifier passes **408** constructor comparisons over duplicate subsets,
opened flags, existing lists and repeated registration. It also passes **1,158**
native/source primitive comparisons: all48 valid pins, supported input pulls,
three MMIO patterns, read results, and bounded/wrapped delay values. Actual C
registry, strcmp, SDK GPIO and native delay providers execute. All448 cold
configuration bytes and78 name bytes compare;15 driver/device-operation targets
remain metadata-only symbol references. Their bodies/parameter ABIs and real
transfer behavior are not implied by matching pointer words.

Ghidra-MCP authenticates registrar spans and all seven selected primitive spans.
Eight existing ownership rows advance (STACMD registrar, six GPIO clones and
delay adapter). The GPIO-output registrar is a supplemental native entry and
does not invent a row. All13 initcall registrar names now resolve to C in the
canonical board. `osSemaphoreNew`, hardware-TWI operations/event callbacks,
GPIO-output driver/device operations and STACMD operations remain explicit
providers; full initcall execution is not yet claimed.

Canonical logger checks (2,034 /76,396 accepted RTT bytes), RTC/startup composition
(960 /14 publish calls), board registration (240), corpus checks (2,972; exact-byte
rebuild skipped) and evidence audit pass. Frontier: **432 tested candidates,
1,464 compiled hints, 1,430 unresolved routes** across all3,326 entries. Next is
the native semaphore allocator boundary needed to execute the full initcall
stage. Physical delay/electrical behavior, IRQ concurrency, complete boot,
whole-image linking and byte equality remain gates.

### Pinned CMSIS semaphore creation wrapper

`rtos-semaphore-new/semaphore-new.o` selects unchanged `osSemaphoreNew` from
CMSIS-FreeRTOS commit `d213f261b5be6bb29a7cce8b84071706b72f4d53`.
The source configuration statically checks the native80-byte semaphore control
block, attribute offsets8/12 and both allocation modes. A wrapper-only override
sets queue-registry size0 because the native body never reads/registers the
attribute name. The baseline kernel's size2 setting is preserved; the scoped
setting is not generalized to the kernel or other wrappers.

**38,400** native/source comparisons pass with **21,540** backend calls per
implementation. Actual CMSIS IRQ-context logic executes across ISR/thread,
PRIMASK/BASEPRI and scheduler states. Tests cover maximum/initial count bounds,
null/malformed/static/dynamic attributes, exact80-byte threshold, ignored names
(including an unmapped name pointer), binary/counting creation, failed allocation,
initial give success/failure and deletion on failed give. Attribute/control-block
canaries and preserved registers/masks compare. Queue and scheduler backends
remain bounded fixtures in this unit; no actual heap acceptance is inferred.

Ghidra-MCP bytes and Thumb spans authenticate the138-byte native wrapper and
38-byte IRQ predicate. The source predicate is inlined in this selected object;
its separate native entry is not promoted by these wrapper tests. Only the
existing `osSemaphoreNew` ownership row advances from a compiled hint to a tested
candidate. No replacement vendor body or opaque executable input is used.

The canonical board now resolves `osSemaphoreNew` through this C provider and
reuses its existing scheduler-state provider. Six FreeRTOS queue providers remain
unresolved: generic dynamic/static create, counting dynamic/static create,
generic send and delete. Those are the next source reduction boundary before
full initcall execution. Full queue layout/scheduler integration, allocator
behavior, physical exceptions, whole-image linking and byte equality remain gates.

Logger (2,034 /76,396 accepted RTT bytes), RTC/startup composition (960 /14
publish calls), board registry (240), corpus checks (2,972; exact-byte rebuild
skipped) and evidence audit pass. Frontier: **433 tested candidates, 1,463
compiled hints, 1,430 unresolved routes**, accounting for all3,326 entries.

### Pinned FreeRTOS queue constructors and reset

`rtos-queue-create/queue-create.o` selects unchanged `queue.c` and `list.c`
from FreeRTOS-Kernel10.5.1 commit`def7d2df2b0506d3d249334974f51e427c17a41c`.
The native80-byte queue layout and type byte at offset76 match with the baseline
kernel configuration retained. Dynamic/static generic creation, dynamic/static
counting creation, private initialization, queue reset and list initialization
now execute as source providers. **372** native/source comparisons include
full dirty control-block/storage canaries, allocation failure, static buffers,
count values, existing/new reset paths, waiting-sender wakeups, yield writes,
preserved registers and **10** fatal assertion paths.

Ghidra-MCP authenticated seven body spans against the application image.
The original ownership row at`0x97ba4` misnames reset as a second
`prvInitialiseNewQueue`. Its two-argument behavior, reset paths and caller at
`0x85094` establish `xQueueGenericReset`. A supplemental correction retains
the immutable ownership ledger and binds the audit to the original row.
The reset span includes168 instruction bytes and its4-byte ICSR literal.
REA's fresh registered function request failed during provider execution;
that receipt is retained as a tool limitation and contributes no semantic proof.

The canonical graph resolves the four queue-creation APIs below CMSIS
`osSemaphoreNew`. Memory allocation, queue send/delete and scheduler task removal
remain explicit unresolved providers. Critical entry/exit and task removal are
bounded fixtures in the queue unit; this does not prove allocator acceptance,
complete scheduler integration, boot execution, physical behavior or byte equality.

CMSIS/queue composition also passes **38,400** comparisons with **23,808**
backend calls per implementation. All four actual queue-creation APIs, reset
and list initialization execute below the actual CMSIS wrapper; complete
queue memory and attribute canaries compare. Allocator, scheduler state,
critical hooks and queue send/delete remain fixtures in this composition unit.
The private initializer is inlined in the selected object, so its separate
ownership row is not promoted. Six emitted provider rows advance.

### Complete device initcall stage with queue providers

`verify_native_board.py --initcall-stage` now executes both the13-entry native
initcall runner and its interrupt-masking boot dispatcher against the canonical
C graph. All13 real registrars execute in order and populate **25** named device
records. **32** comparisons cover incoming PRIMASK0/1, independent failure of
either TWI semaphore allocation, zero/dirty allocation buffers, preserved
registers and final masks. **64** allocator calls per implementation request
exactly80 bytes. Actual CMSIS context checks, queue creation/reset/list and
canonical Nordic critical-section providers execute; allocator return addresses
are the sole intercepted provider in this stage.

The verifier monitors lower192KiB RAM and compares every byte changed from
either implementation's own cold baseline. It normalizes existing per-field
function pointers and checks relocated name strings before normalizing their
pointers. Unmodeled cold RAM is not claimed source-owned. Registry addresses,
links, names and operations compare. The allocator fixture is enabled only for
the stage and removed afterward; other unresolved-provider traps stay active.

This establishes the authenticated device initcall stage, including continuation
through either allocation failure. It does not establish subsequent peripheral
open order, full application boot, the real allocator, physical behavior or
whole-image byte equality. The native allocator's16-byte header and caller-LR
extension remain a concrete reconstruction gate; unchanged upstream heap4's
8-byte header is not admitted as a compatible substitute.

Current frontier: **439 tested candidates,1,458 compiled hints,1,429 unresolved
routes**, accounting for all3,326 ownership entries. Corpus validation remains
2,972 structural functions; exact-byte rebuild is skipped.

### Native heap4-family extensions and initcall allocation

`native-heap/heap.o` now provides recovered C bodies for allocation, free,
heap initialization, free-list insertion and the fatal allocation-failure hook.
The source-owned layout is authenticated by native literal pools and
Ghidra-MCP spans: storage51200 bytes at`0x2001e588`, start sentinel12 bytes
at`0x2002ad88`, state20 bytes at`0x200077fc`. Allocated headers are16 bytes:
next pointer, size/allocated-bit, incoming caller LR, and preserved padding.
The native request formula is`request + 24 - (request & 7)`, including an extra
8 bytes for already aligned requests. Splitting requires remainder greater
than32. Zero, overflow/sign-bit, exhaustion and invalid free invariants use the
native BASEPRI64/zero-write fatal policy. Free clears the caller field before
scheduler suspension, coalesces adjacent blocks and updates accounting.

**3,165** native/source comparisons pass, including **561** fatal assertions,
with **6,316** scheduler boundary calls per implementation. Every call compares
51232 bytes of heap/sentinel/guards plus20 bytes of state. Tests cover alignment
boundaries, overflow, exhaustion, zero/dirty memory, caller LR, header padding,
all24 four-block free orders, deterministic fragmented sequences, null free,
double free and invalid allocation flags/links. Scheduler suspend/resume are
bounded fixtures in this unit. These bodies preserve native extensions; the
pinned FreeRTOS10.5.1 heap4 is lineage evidence, not a compatible substitute.

`verify_native_board.py --initcall-real-heap` executes the actual allocator
beneath the real13-entry initcall stage, CMSIS wrapper, queue/list providers and
canonical critical-section code. **8** comparisons and **16** allocations pass
across incoming masks, both runner/dispatcher entries and zero/dirty heaps.
Both80-byte queue requests consume104-byte blocks; free/minimum memory becomes
50976 with two successful allocations and no frees. All25 device records and
all mutations across lower192KiB RAM compare. The test authenticates the actual
native/source Thumb BL targets and normalizes only the two caller-LR header
fields, retaining all remaining heap bytes for comparison.

The canonical graph now resolves `pvPortMalloc` and `vPortFree` through C.
`vTaskSuspendAll` and `xTaskResumeAll` remain explicit providers; the composition
fixtures only those scheduler boundaries. Test-only anonymous BSS moved to
`0x2003e000` to avoid overlapping the newly authenticated heap span. This is an
emulator layout adjustment, not an admitted production address for that BSS.
Full scheduler execution, complete boot, hardware and byte equality remain gates.

Post-integration regressions pass: logger2034 comparisons/76396 accepted RTT
bytes, RTC startup960 comparisons/14 publish calls, allocation-fixture initcall
stage32 comparisons, actual-heap stage8 comparisons, board registry240 comparisons
and corpus2972 structural functions (exact-byte rebuild skipped). Frontier audit
accounts for all3326 entries: **444 tested candidates,1455 compiled hints,1427
unresolved routes**. No whole-image instruction identity or hardware claim follows.

### Pinned scheduler suspend/resume and prekernel composition

`rtos-scheduler-resume/scheduler.o` compiles unchanged function and macro slices
from pinned FreeRTOS-Kernel10.5.1 `tasks.c`:
`vTaskSuspendAll`, `xTaskResumeAll`, `prvResetNextTaskUnblockTime` and both
ready-list macros. Each slice has an original byte offset/hash; the audit
reconstructs the generated C exactly. The source-owned interface admits only
an authenticated48-byte TCB prefix (state item+4, event item+24, priority+44).
The full TCB reservation/size remains gated. Existing watchdog `pxCurrentTCB`
and private tick-provider `uxSchedulerSuspended` storage are reused, with an
explicit typed native-address binding for the latter. No duplicate state word
or shadow scheduler is introduced. New ready/pending-list and scheduler fields
are placed at their authenticated native addresses in the emulator layout.

**32,274** native/source comparisons pass, including **8,064** assertion cases
and **10,080** tick-boundary calls per implementation. Actual inline list
removal/insertion moves pending tasks between event/state/ready lists, including
head-index repair, preserved112-byte TCB canaries, priorities0/1/15/55,
higher/equal/lower-current priority decisions, empty/non-empty delayed-list
unblock recalculation, nested suspension, counter wrap, pending ticks, existing
yield flags and ICSR writes. Critical-section and tick processing are fixtures
in this unit; actual tick side effects and context switching are not inferred.

The scheduler's ready-list literal exposes a heap extent correction:
`r1_heap_start` at`0x2002ad88` is a12-byte sentinel ending at`0x2002ad94`, where
the ready-list array begins. Allocated block headers still reserve16 bytes.
The C declaration and canonical layout now preserve that adjacency. All3165
allocator comparisons, including561 fatal assertions, still pass unchanged.

`--initcall-real-scheduler` executes all13 registrars with actual CMSIS,
queue/list, heap, scheduler suspend/resume and critical-section providers.
**8** comparisons/16 allocations pass with25 named registry records and all
changed lower192KiB RAM compared. This stage uses no provider interception;
source/native caller-LR fields retain the authenticated normalization described
above. The controlled prekernel stage has no existing tasks or pending ticks.
It establishes that stage only; `xTaskIncrementTick`, scheduler startup/context
switching, complete TCB allocation, peripheral open order, full firmware boot,
hardware behavior and byte equality remain explicit gates.

The generated scheduler subset retains the upstream Amazon copyright and full
MIT notice, authenticated separately from the unchanged body/macro slices.
Current frontier: **447 tested candidates,1453 compiled hints,1426 unresolved
routes**, accounting for all3326 entries. Logger2034/76396 RTT bytes, RTC960/14
publish calls, board240, initcall variants32/8/8 and corpus2972 checks pass;
exact-byte rebuild remains skipped.

### Pinned tick processing and event-list removal

`rtos-scheduler-tick/scheduler-tick.o` compiles unchanged byte-hashed slices of
FreeRTOS-Kernel10.5.1 `xTaskIncrementTick`, `xTaskRemoveFromEventList`, their
reset-unblock helper and ready/delayed-list macros. The original Amazon MIT
notice is retained. Native shared state is reused; the existing tick getter's
private counter has an explicit typed binding at`0x20007828`. New source-owned
state comprises overflow count`0x2000783c`, overflow-list pointer`0x20007858`,
and two20-byte delayed lists at`0x2002b1f4`/`0x2002b208`. `-fwrapv` preserves
native signed overflow-counter wrap without changing the upstream body.
The48-byte accessed TCB prefix remains separate from the full TCB-size gate.

**40,193** native/source comparisons pass without provider interception:
38,400 tick cases and1,793 event-removal cases, including2,049 assertion paths.
Tests cover tick increment/wrap, delayed/overflow-list swaps, overflow counters,
timeout unblocking, optional event-list cancellation, index repair, priority and
time-slice decisions, preexisting yield flags, suspended/pended-tick wrap,
event removal to ready versus pending-ready lists and null-owner rejection.
Full112-byte TCB canaries, scheduler words and all ready/delayed/pending-list
bytes compare. Ghidra-MCP spans authenticate both bodies and literal pools.

Scheduler-resume composition additionally passes **10,770** comparisons,
including2,688 assertions and3,360 actual tick calls per implementation.
Actual pending-ready transfers, pended-tick replay and a delayed timeout execute
together. Critical-section entry/exit remain bounded fixtures in this unit;
the separate prekernel initcall test retains its real critical providers and
no provider interception. The canonical graph now resolves both tick processing
and event-list removal. Full task creation/allocation, scheduler startup/context
switching, physical interrupt concurrency and whole-image byte equality remain
gates. Neither tick replay nor bounded list tests establish a complete scheduler.

Delayed-list placement is additionally authenticated by the native first-task
initializer span`0x84d68..0x84e57`: literal`0x84e50` supplies base`0x2002b1f4`,
list initialization calls use base/base+20, and scheduler fields+56/+60 receive
those exact pointers. This authenticates the two20-byte storage objects; the
larger TCB-owning first-task registrar is not promoted by this evidence.
Post-integration frontier: **449 tested candidates,1451 compiled hints,1426
unresolved routes**, accounting for all3326 entries. Logger2034/76396 accepted
RTT bytes, RTC960/14 publish calls, board240, initcall variants32/8/8 and corpus2972
checks pass. Exact-byte rebuilding, full boot and hardware proof remain open.

### Pinned queue send/delete with native copy and registry variants

`rtos-queue-operations/queue-operations.o` selects unchanged FreeRTOS10.5.1
`queue.c` bodies for `xQueueGenericSend`, `vQueueDelete`, `prvCopyDataToQueue`
and `prvUnlockQueue`. The scoped configuration disables registry-unregister
calls, matching the native30-byte delete body; the baseline kernel's registry
size2 remains intact. The copy token binds to the existing native-return-ABI
movement adapter and unchanged pinned musl memmove, matching native call0x2775c
and preserving overlap behavior. This binding is local to these bodies; their
unused memory-copy return value does not become an ISO return-contract claim.

**4,875** native/source comparisons pass, including **699** assertion cases:
2526 send,5 delete,1462 copy and882 unlock cases. Actual ring/front/overwrite
movement includes disjoint and overlapping sources, pointer wrap and semaphore
versus mutex paths. Ordered task-boundary fixtures exercise receiver wake/yield,
signed lock-byte drains, full/no-wait rejection, timeout expiry, retry without
blocking, scheduler resume with/without yield, repeated full/timeout handling
and modeled IRQ lock notifications. Task wait/timeout/scheduler/critical/mutex
and free are bounded fixtures in this unit, not actual context switches.

The canonical graph additionally passes **1,088** queue-lifecycle comparisons
across **192** workflows with **360** overlapping sends and no provider
interception. Actual CMSIS binary/counting/static/dynamic creation, queue
constructors/send/delete, native heap, scheduler suspend/resume, critical code
and overlap-safe movement execute together. Tests compare51212 heap/sentinel
bytes per call, state and attribute/control/data canaries, full/overwrite and
front/back behavior, preserved registers/masks and complete heap reclamation.
Only allocated-header caller LR is normalized after authenticating native and
source Thumb BL targets. These controlled prekernel, nonblocking workflows have
no waiters; full blocking scheduler execution remains a gate.

Ghidra-MCP spans authenticate the four bodies plus lower-boundary and TCB-layout
evidence. Two ledger labels are retained as unresolved attribution corrections:
native0x96188 is the ordered `vTaskPlaceOnEventList` used by send, and0x96160
is the internal timeout snapshot without critical hooks. Those lower providers
are fixtures here and are not promoted or silently relabeled.

Native initializer0x850b6 copies up to32 name bytes at TCB+52 and stores its
incoming stack-depth word count at+84. Mutex disinherit reads base priority+96
and held-mutex count+100. The extra TCB word is an R1 stack-depth extension;
it does not establish upstream `configRECORD_STACK_HIGH_ADDRESS` semantics.
Complete TCB construction remains gated pending a source-owned layout and
initializer contract. Task wait/timeout, mutex state, scheduler startup/context
switching, physical concurrency and whole-image identity remain open.

Post-integration regressions pass: logger2034 comparisons/76396 accepted RTT
bytes, RTC960/14 publish calls, initcall variants32/8/8, queue lifecycle1088,
board240 and corpus2972 (exact-byte rebuild skipped). Frontier audit accounts
for all3326 entries: **453 tested candidates,1452 compiled hints,1421 unresolved
routes**. The no-inline upstream compile exposes additional private helper-name
matches; those remain compiled hints and do not acquire behavior or image proof.

### Task timeout, ordered wait and mutex dependencies

`rtos-task-wait/task-wait.o` selects unchanged pinned FreeRTOS10.5.1 timeout
snapshot/check, missed-yield, ordered event-wait, delayed-placement and mutex
disinherit bodies, plus unchanged list insertion/removal. Original source slice
byte offsets/hashes, MIT notice and compiled list source are authenticated.
The interface admits a104-byte native TCB prefix with the32-byte name, native
stack-depth word+84 and base-priority/mutex fields+96/+100. Opaque words88/92
and tail bytes104..111 are preserved; full112-byte TCB construction is not
admitted. The upstream end-of-stack option is not substituted for stack depth.

**18,675** native/source comparisons pass, including **323** assertion cases:
20 internal snapshots,20 missed yields,5041 ordered waits,2702 timeout checks,
768 mutex disinherits,10080 delayed placements and44 direct list primitives.
Cases cover time/overflow arithmetic and indefinite waits, sorted insertion,
ready/delayed/overflow/suspended lists, index repair, mutex count/owner assertions,
priority restoration and112-byte TCB canaries. Only critical entry/exit are
fixtures in this unit. Native pointer/state providers remain explicit in its
standalone link and resolve to the existing shared canonical graph.

Two supplemental attribution corrections bind original ledger rows exactly:
0x96160 is the internal timeout snapshot, and0x96188 is ordered event placement.
The immutable ledger is retained; the audit uses the corrected source names
only for these authenticated tested contracts. Suspended-list storage20 bytes
at0x2002b244 is bound by the native delayed-helper pool and first-task initializer.

The unchanged upstream `uxTopUsedPriority = configMAX_PRIORITIES - 1U`
declaration now supplies the missing4-byte debugger word55 at0x2000784c. Native
scheduler-start load0x9651c and the actual cold-start RAM value authenticate it;
compiled source data is serialized at that address and compared. This does not
promote the complete scheduler-start routine.

Actual blocking-send timeout composition adds **2,016** comparisons across
**216** workflows and **720** actual tick calls, without provider interception.
Queue create/fill/block, timeout snapshot/check, ordered wait/list placement,
suspend/resume, native heap/critical, tick wakeup/event removal, timeout return
and heap reclamation execute together, including tick/overflow-list rollover.
PendSV writes pause execution; ticks run on a controlled separate stack and the
saved task context is restored. This models transfer between task and tick
execution; the native PendSV/context-switch body is not executed or proven.
Complete task construction, event-driven producer/consumer wakeups, scheduler
startup, physical concurrency and whole-image identity remain explicit gates.

Post-integration regressions pass: logger2034/76396 accepted RTT bytes, RTC960/14
publish calls, initcall variants32/8/8, queue lifecycle1088, blocking timeout2016,
board240 and corpus2972 (exact-byte rebuild skipped). Frontier audit accounts for
all3326 entries: **461 tested candidates,1444 compiled hints,1421 unresolved
routes**. These are bounded provider contracts, not complete task construction,
source-complete images, physical scheduling or byte-equality proof.

### Native112-byte task construction and initial execution frames

`native-task-construction/task-construction.o` provides source-owned native
static/dynamic constructors and private initialization, with unchanged pinned
FreeRTOS10.5.1 ready-list/list-setup bodies, unchanged Nordic SDK17.1.0 initial
stack/return-error bodies and pinned list-item initialization. Source slices and
original license notices are authenticated. Kernel names `xTaskCreate` and
`xTaskCreateStatic` bind explicitly to the R1 native constructors; this does not
substitute the baseline92-byte `StaticTask_t` layout for the native ABI.

The source-owned112-byte record preserves32 name bytes, stack-depth words+84,
trace counter+88, opaque word+92, base priority+96, mutex count+100, notification
value+104/state byte+108, allocation mode+109 and two padding bytes. Factories
zero all112 bytes, then set static mode2 or dynamic mode0. Direct initialization
preserves other bytes, fills the stack with0xa5, preserves a null name, clips
non-null names at32 bytes, faults for priority>=56 after stack/name writes,
sets list owners/container fields and publishes the stack pointer/optional handle.
The depth word is not an upstream end-of-stack pointer.

**788** native/source comparisons pass, including **150** assertion cases:
360 private initializations,144 dynamic creates,147 static creates,120 ready
registrations,12 stack frames,4 return-error paths and1 list-item initialization.
Tests compare full TCB/stack/state/canaries, first-task list setup, current-task
selection, priority/yield behavior, counter wrap, allocator failure/cleanup,
name/null/output/alignment variants and malformed static arguments. Allocator,
free and critical boundaries are fixtures in this unit; memory/list/port code is
actual C. Stack-return-handler pointer normalization checks its native counterpart.
The return-error unit also verifies the critical-nesting0xffffffff infinite-loop
case, distinct from the usual BASEPRI64/zero-write assertion path.

The source-owned initial xPSR word4 bytes at0x9c4cc is compared with native flash.
Task-number storage at0x20007840 and the20-byte termination list at0x2002b230
complete the data needed by the reused ready-list constructor.

Actual consecutive creation adds **144** full-graph comparisons across **72**
static/dynamic task pairs, without provider interception. Actual heap, critical,
list and port providers initialize/register both tasks; complete TCBs/stacks,
allocation headers, mode, notification zeros, trace/task counters and prekernel
priority selection compare. Only authenticated allocator caller BL targets and
initial-frame return-handler pointers are normalized. Task code is a controlled,
unexecuted pointer. CMSIS thread creation, other task-runtime operations, cleanup,
scheduler startup/context switching, physical task execution and whole-image
identity remain separate gates. This advances the constructor ABI; it does not
claim a complete running scheduler or semantic admission of opaque word92.

The fresh REA query for registered initializer0x850b6 failed during provider
execution. Its receipt and doctor diagnostics are retained without semantic
admission; Ghidra installation checks pass, while audit-wide diagnostics also
report missing Hopper. Ghidra-MCP authenticated spans and native execution are
the evidence used here. No unchanged failed REA request was retried.

Post-integration regressions pass: task construction788/150 assertions, actual
construction144 across72 task pairs, logger2034/76396 accepted RTT bytes,
RTC960/14 publish calls, initcall variants32/8/8, queue lifecycle1088, blocking
timeout2016, board240 and corpus2972 (exact-byte rebuild skipped). Frontier audit
accounts for all3326 entries: **468 tested candidates,1437 compiled hints,1421
unresolved routes**. Complete firmware source/build/byte identity remains open.

### CMSIS thread creation through the native construction ABI

`rtos-thread-new/thread-new.o` compiles unchanged Apache-licensed CMSIS-FreeRTOS
`osThreadNew`, IRQ-context body and selected Cortex-M mask macros from pinned
commit`d213f261b5be6bb29a7cce8b84071706b72f4d53`. Original slice offsets/hashes
and license text are retained. A scoped header maps `StaticTask_t` to the
verified112-byte R1 record and binds the two constructor tokens to the typed
native providers. The R1 record uses CMSIS's forward-declared task tag, so these
calls compile with compatible task-handle types. The baseline kernel typedef,
configuration and weak memory callbacks are not changed or selected here.

**42,048** native/source boundary comparisons pass with **43,848** backend calls
per implementation. Native/source defaults are priority24 and256 stack words.
Tests cover null/function/attribute cases;112-byte static threshold versus
91/92/111/113; static/dynamic/malformed memory combinations; priorities and
joinable-bit rejection; byte-to-word rounding; full32-bit static depth versus
16-bit dynamic narrowing; opaque name pointers and ignored tz/reserved fields; backend status/partial
handle behavior; and ISR, PRIMASK, BASEPRI and scheduler-state combinations.
The scheduler-state read and constructors are fixtures in this unit. In particular,
wrapper acceptance of priority56 or tiny nonzero stack sizes does not override
the independently authenticated downstream kernel behavior. Ghidra-MCP binds
the142-byte wrapper and38-byte IRQ predicate; the predicate is inlined in this
subset and its separate inventory row is not promoted.

CMSIS/native-constructor composition passes **144** comparisons across **72**
consecutive static/dynamic pairs, including null/default dynamic attributes,
without provider interception. Actual heap, critical, list and port providers
publish full records/frames and choose the prekernel current task. Controlled
entry pointers remain unexecuted; only authenticated allocator caller BL and
stack-return-handler fields are normalized.

The five existing application creation callbacks additionally pass **2,400**
comparisons across **480** workflows: all120 creation orders, incoming mask0/1
and zero/dirty control-block/stack inputs. Actual application attrs/creators,
CMSIS wrapper, native static constructors, ready/list setup, critical and port
code execute together without provider interception. Every snapshot compares
560 TCB bytes and27648 stack bytes, handles, task/trace counters and kernel lists.
Only the authenticated initial-frame task-PC and return-LR words are normalized.
All five tasks are registered with the expected full records and prekernel
highest-priority selection; the real task code is not executed.

This advances thread-creation composition for these five callbacks, not actual
firmware boot order, the complete task set, scheduler/context-switch execution,
task cleanup, physical concurrency or whole-image byte identity. Other task
operations and the remaining provider graph retain their explicit gates.

Post-integration regressions pass: thread-new42048, CMSIS task graph144,
application thread2400, native constructor788/144, logger2034/76396 accepted
RTT bytes, RTC960/14 publish calls, initcall variants32/8/8, queue lifecycle1088,
blocking timeout2016, board240 and corpus2972 (exact-byte rebuild skipped).
Frontier audit accounts for all3326 entries: **469 tested candidates,1436 compiled
hints,1421 unresolved routes**. Whole firmware source/build/byte identity remains
open; these receipts do not establish running threads or a booted device.

Task termination now uses unchanged pinned FreeRTOS `vTaskDelete`,
`eTaskGetState`, `prvDeleteTCB` and `vListInsertEnd`, plus CMSIS
`osThreadTerminate`, with the authenticated112-byte native task layout.
`rtos-task-termination/verification.json` records1903 native comparisons,
including542 matching assertion paths. All256 allocation-mode values are
covered:0 frees stack then TCB,1 frees TCB,2 preserves both, others assert.
The source-owned pending-deletion word is at0x20007820. The state query uses
the notification byte at108 and cleanup uses allocation mode at109.

`board/task-termination-verification.json` adds288 comparisons across72
create-two/delete-other/defer-current workflows, using actual C CMSIS,
constructors, allocator/free, critical and list providers without interception.
Static storage preservation and dynamic reclamation are compared across the
whole heap arena; self-deletion remains queued for idle cleanup. Native idle
cleanup, scheduler start and PendSV execution remain explicit gates. Ghidra-MCP
bytes match the locked application; the fresh REA function request failed and
is retained as a tool limitation in `rtos-task-termination/rea-delete-function.json`.

The refreshed ownership frontier accounts for all 3,326 entries: **474 tested
contract candidates, 1,432 compiled symbol hints, and 1,420 unresolved source
routes**. Five termination/list functions were promoted this checkpoint.
These counts remain routing evidence, not whole-image source or byte identity.
The next cleanup target is the unindexed idle-loop region at 0x84fea..0x8501a,
with a call to reclamation at 0x85010. Its disassembly is preserved as discovery
evidence; no standalone function attribution or callable ABI is admitted yet.

Idle reclamation checkpoint: the termination subset now also compiles unchanged
FreeRTOS `prvCheckTasksWaitingTermination` and `prvGetExpectedIdleTime`.
The combined unit receipt has 2,953 native comparisons, including 584 matching
assertion paths: 150 cleanup-region cases and 900 expected-idle-time cases.
The cleanup region starts at native 0x84fe8, includes the pending list loop,
and stops at 0x8501a before the rest of the idle task. It has no standalone
ownership entry or admitted native callable ABI. Source cleanup has normal C
calling convention; the verifier compares native memory effects at explicit
loop boundaries and checks its known scheduler/list register bases.

The integrated creation/termination/reclamation receipt now has 432 comparisons
across 72 workflows, with actual allocator/free, critical and list providers
and no interception. Each workflow creates static/dynamic task pairs, deletes
the other task, defers self-deletion, drains idle cleanup, then repeats the
empty drain. Dynamic heaps return to 51,184 free bytes with matching allocation
and free counters; static task storage remains preserved. Complete idle-loop
execution, the watchdog idle hook, tick suppression and PendSV/task execution
are still separate evidence gates. Initial task entry and port-return pointers
are authenticated before normalization; these tests do not prove hardware or
whole-image instruction identity.

Expected idle time at 0x84f68 is a separate ownership function. The unchanged
body returns zero for a non-idle current priority, multiple ready idle tasks,
or a higher ready priority; otherwise it returns the unsigned difference
between next unblock time and tick count, including wraparound. Ghidra-MCP
spans include the original code and supplemental literal words.

After idle cleanup/expected-idle admission, the audited frontier accounts for
all 3,326 ownership entries: **475 tested contract candidates, 1,432 compiled
symbol hints, and 1,419 unresolved source routes**. The inlined cleanup region
adds supported compiled source without inventing a new ownership row. The
original ownership CSV remains unchanged. REA procedure inventory lacks both
idle-region and expected-idle entries; its authenticated inventory binding is
saved alongside the successful Ghidra-MCP byte receipts and native comparisons.

The complete pinned FreeRTOS idle-task body now compiles in `rtos-idle/idle.o`.
Its scoped native configuration enables the idle hook, with preemption and idle
yield enabled, tickless mode1 and a two-tick sleep threshold. The baseline
configuration is unchanged. A typed void adapter discards the existing watchdog
feed result, matching the native idle caller. The native region0x84fe8..0x8506c
is an infinite task loop with literals through0x8507c; its missing standalone
inventory row is not replaced or counted as a new ownership function.

`rtos-idle/verification.json` records10,800 native/C control-flow comparisons,
2,160 matching assertion paths and91,584 explicit backend fixture calls per
implementation. It covers one/three iterations, PendSV yield writes, the hook,
preliminary/resampled idle time, suspend/resume, tick-order assertions and sleep
thresholds. `board/idle-loop-verification.json` adds1,200 composed cases with
actual cleanup, expected time, watchdog hook/registry/device/SDK feed and kernel
suspend/resume. Only `vPortSuppressTicksAndSleep` is intercepted in this graph:
108 fixture calls,66 matching assertions, and1,156 actual watchdog feed paths
with matching reload-register writes. Watchdog registration is executed before
using its handle. These are emulated MMIO writes, not physical watchdog proof.

Tick suppression remains an explicit provider. Its native286-byte body at
0x95de4 correlates with the pinned Nordic `port_cmsis_systick.c` RTC branch:
RTC1 at0x40011000, maximum sleep0x00fffffd, SoftDevice NVIC state at0x2002c2fc,
sleep-status query0x5cf78 and tick-step0x9653c. Pre/post-sleep processing and
actual wake/RTC progression require their own contracts. Native context
transfer, physical sleep and full image source/byte equality remain open.
Ghidra-MCP bytes authenticate the idle loop; REA's registered inventory omits
its entry, and the tool coverage limitation is retained in the evidence file.

RTC tick suppression is now source-built from unchanged pinned Nordic
`port_cmsis_systick.c` in `rtos-tickless-port/tickless-port.o`. The scoped header
binds returning native error logging and pre-sleep FPU preparation: only a
nonzero expected idle time checks pending IRQ38, clears FPSCR bits0x9f, reads
FPSCR again and clears the pending IRQ. RTC1,24-bit counter range, maximum
expected sleep0x00fffffd, two-tick threshold and simple-debug clamping match
native code. The baseline configuration remains unchanged.

`rtos-sleep-kernel` supplies unchanged pinned FreeRTOS sleep-status and tick-step
bodies, using existing provider-owned scheduler words. Its unit receipt has
4,048 comparisons and1,588 matching assertions. The port receipt has2,640
comparisons,672 SVC65 instruction fixtures,672 WFE instruction fixtures and288
pending-FPU cases. It compares ordered RTC/NVIC writes, critical state, CPU mask
restoration, counter wrap/clamp, zero/abort sleep and error continuation.
Ghidra-MCP bytes include the port, kernel functions and native event-clear and
NVIC-clear primitives; REA inventory coverage is recorded separately.

`board/idle-real-sleep-verification.json` verifies1,200 actual idle/RTC-port/
sleep-status/tick-step/scheduler/watchdog graphs, including66 matching
assertions,96 actual sleep calls and96 actual tick-step calls, without provider
interception. Its192 counter reads and96 WFE wake boundaries are explicit
hardware fixtures. The original sleep-function-fixture graph remains separate
for control-flow comparison. Native peripheral semantics, autonomous RTC
progression, SoftDevice-enabled wait execution, scheduler startup, native
context transfer and physical wake remain open. Complete image C closure,
compiler reconstruction and instruction equality are still unproven.

After the three sleep-provider admissions, the frontier accounts for all3,326
ownership entries: **478 tested contract candidates,1,429 compiled symbol hints
and1,419 unresolved source routes**. The next concrete target is scheduler
startup: static idle/timer memory callbacks, timer-task creation, port setup
and first native context transfer. Source routing is recorded in
`rtos-tickless-port/scheduler-start-next-target.json`; it does not claim startup
implementation or execution. No original ownership rows were changed.

Scheduler construction now uses unchanged pinned `vTaskStartScheduler`,
`xTimerCreateTimerTask` and `prvCheckForValidListAndQueue`, plus the existing
source-owned static-memory callback bodies compiled against the native112-byte
TCB type. The baseline92-byte `StaticTask_t` and weak CMSIS candidates remain
unchanged. Startup owns the idle handle at0x20007848 and timer handles/list
pointers at0x2000785c/60/68/6c. Two20-byte timer lists occupy0x2002b4a8 and
0x2002b4bc. The static timer queue at0x2002b258 owns80 bytes, followed by32
sixteen-byte messages at0x2002b2a8. Idle and timer reservations are1136 bytes at
0x2002b4d0 and0x2002b940, each112-byte TCB plus256-word stack. Timer priority53,
queue registry0 and native names are scoped to these selected bodies.

`rtos-scheduler-start/verification.json` records312 native comparisons,
including102 matching fault paths, static callback output aliasing/null writes,
queue fresh/already-present paths and constructor/port failure statuses.
`board/scheduler-start-verification.json` records24 comparisons across16 actual
C workflows: empty/five-application-task startup, fresh/preinitialized timer
queue, clean/dirty static storage and PRIMASK0/1. Actual callbacks, task/queue
constructors, lists, critical and initial-stack providers run without provider
interception. Both system task handles/stacks/TCBs and scheduler state match;
timer priority53 becomes current before the port starts. Static construction
consumes no heap. Only authenticated initial frame PC/LR fields are normalized.

The graph stops before `xPortStartScheduler` at native0x979dc. That port body,
first-task transfer and timer runtime body at0x85510 remain explicit providers.
Native port-start routing preserves a subtle configuration distinction: the
priority readback is ANDed with raw configured value2, while critical BASEPRI
operations use64. Hardware priority writable-bit readback needs an explicit
fixture; no corrective64 substitution is authorized by the native contract.
`rtos-scheduler-start/port-start-next-target.json` records source/hash and next
steps without claiming port startup or physical scheduling proof.

The refreshed frontier accounts for all3,326 ownership entries: **481 tested
contract candidates,1,426 compiled symbol hints and1,419 unresolved source
routes**. This checkpoint newly admits three kernel startup functions and
strengthens the two existing static-memory callback contracts with native
112-byte typing, fixed addresses and actual constructor composition. Legacy
baseline callback receipts remain authenticated separately; the frontier now
routes those entries to the typed startup subset. No ownership rows changed.

Nordic port startup and RTC1 setup now compile from unchanged pinned SDK bodies
in `rtos-port-start/port-start.o`. Existing private port state is reused at
0x20007810/14/18 through typed address bindings, without duplicate globals.
Raw maximum syscall priority2, kernel priority15, CPUID0x410fc241, RTC1 IRQ17
and prescaler31 are compile-time checked. The private unexpected-return helper
is scoped to avoid aliasing the task-construction provider's return handler.

The port unit receipt has5,220 native comparisons, including4,536 matching
fault cases and648 successful first-task boundaries. It covers CPUID checks,
priority writable-bit readbacks, original byte restoration, priority groups,
PendSV/RTC priorities, ordered RTC/NVIC/FPU writes, initial mask preservation
and unexpected first-task return. LF-clock request and first-task behavior are
explicit fixtures in that unit. Native raw priority2 masked by0xe0 yields
ucMaxSysCallPriority0 and group4; the source preserves this behavior instead of
substituting the separate BASEPRI64 value.

`board/port-start-verification.json` adds24 comparisons across16 actual C
kernel/system-task/port/RTC/LF-clock workflows without provider interception.
The entire static construction and SDK LF-clock request/critical/clock bodies
run, stopping before first-task transfer at native0x27238. The priority readback
uses an explicit0xe0 hardware fixture. This compares memory-backed MMIO and
state; it does not prove autonomous RTC/clock progression or physical boot.

The next source path is the pinned SDK GCC/nrf52 `port.c`, a licensed C file
containing explicit ARM inline assembly for first-task startup, SVC restore
and PendSV. Source/hash and native routing are recorded in
`rtos-port-start/first-task-next-target.json`. Vector placement, exception/frame
restore, task selection, timer runtime and hardware execution remain separate
gates. Whole-image source closure and byte identity remain unproven.

The audited frontier now accounts for all3,326 entries: **483 tested contract
candidates,1,424 compiled symbol hints and1,419 unresolved source routes**.
Port start and RTC1 setup were promoted; first-context, timer runtime and full
image compiler/byte closure remain explicit. Original ownership rows and locked
firmware hashes are unchanged.

The pinned Nordic GCC/nrf52 `port.c` now compiles unchanged as a C translation
unit containing explicit ARM assembly for first-task startup, SVC restore and
PendSV. Unchanged pinned `vTaskSwitchContext`, generic ready-list selection and
stack-check macros use the authenticated112-byte native TCB. Three source-owned
vector records are compiled and placed: initial SP at0x27000, SVC at0x2702c and
PendSV at0x27038. The SDK-compatible `__isr_vector` anchor is an initialized
uint32 word placed in application flash. Other vector slots remain separate
gates; no complete vector-table or flashable-image claim follows.

`rtos-context-port/verification.json` has2,232 comparisons:12 first-task
boundaries,12 SVC restores,48 isolated PendSV core/FPU cases and2,160 actual
kernel selection cases. It records72 matching assertion faults and480 bounded
stack-overflow-hook calls. Core and high-FPU software frame saves/restores,
same/other task targets, masks, ready-list rotation, suspended yielding and the
four stack canary words are compared. PendSV's selector is a fixture only in
those isolated port cases; actual kernel selection is independently exercised.
SVC0 and BX-LR exception return stop at explicit instruction boundaries.

`board/context-start-verification.json` adds224 comparisons across32 workflows
using actual construction, port/RTC/clock, first-task setup, SVC restore,
PendSV and kernel selection without provider interception. An explicit handler
entry fixture connects the SVC0 boundary to software restore. Four actual
PendSV/selector bodies run per workflow, including round-robin selection of an
additional priority53 peer. No task instructions or exception-return hardware
execute. Peer entry is a controlled unexecuted pointer; initial PC/LR words
are normalized only after exact source/native pointer checks. Physical
exceptions, full vectors, overflow-hook logging/fatal source, timer runtime,
complete firmware source and byte identity remain open.

After the four context-provider admissions, the frontier accounts for all3,326
entries: **487 tested contract candidates,1,422 compiled symbol hints and1,417
unresolved source routes**. Original ownership rows, upstream sources and locked
firmware hashes are unchanged. Three authenticated vector records are source
owned; the rest of the vector table and actual exception/task execution remain
explicit gates. The next bodies are overflow logging/fatal handling and timer
runtime with its queue/wait dependencies.

The native stack-overflow callback now has source-owned C at
`native_stack_overflow.c`, resolving the context selector's callback provider.
Its authenticated behavior is terminal logging/drain, not an assertion fault:
independent mode reads select the structured producer0x0c400000 and Nordic
producer0x001c0003, then actual `nrf_log_frontend_dequeue` is called until false,
followed by a permanent loop. No explicit BASEPRI/PRIMASK change is added.
The unused task argument and opaque name argument retain native behavior.
The two source-owned format strings are placed at0x95c44 and0x95c70; module28
is authenticated by the native module-record/base/stride calculation.

`native-stack-overflow/verification.json` records12,360 native comparisons:
12,336 terminal-loop entries and24 bounded busy-drain paths. All effective
three-read mode sequences, exact producer pointers/words, name/task argument
values, dequeue results and input masks are compared with explicit lower
logging fixtures. No ABI return restoration is claimed for this nonreturning
callback. Reaching the terminal branch does not prove physical nontermination.

`board/stack-overflow-verification.json` records256 direct/actual-selector
workflows with the complete source logging graph: structured cache/clock,
Nordic init/std1/dequeue/pool/formatters and RTT. The graph executes320 dequeues
and accepts8,064 RTT bytes per implementation without provider interception.
It covers all modes, immediate/deferred logging, clock-state flag, masks and
two valid task names, including compact-string tail retention. Clock/RTC
registration is controlled; actual snapshot/default clock providers execute.
Accepted RTT bytes remain distinct from debugger delivery or physical device
failure. Exception return, full vectors, timer runtime and whole-image source/
byte closure remain open.

The audited frontier now accounts for all3,326 entries: **488 tested contract
candidates,1,422 compiled symbol hints and1,416 unresolved source routes**.
The overflow callback's source dependency is resolved in the board/context
selector graph. Timer runtime and queue/wait providers are next; partial
vectors, actual exceptions/task execution and whole-image byte closure remain
explicit. The original ownership CSV and locked firmware hashes are unchanged.


### Timer runtime staging: isolated contracts verified, graph admission pending

The unchanged pinned FreeRTOS10.5.1 timer runtime now compiles with its native
44-byte timer and16-byte daemon-message layouts. Its helpers and bounded timer
loop pass12,349 native comparisons. Actual pinned queue receive/restricted wait
pass1,849 comparisons; restricted task event placement and its delayed-list
helper pass15,121. These tests retain explicit lower-provider fixtures and do
not establish task execution or physical time progression.

`rtos-timer-runtime/evidence.json` binds Ghidra-MCP memory reads to the locked
application and REA procedure-inventory rows. The restricted queue wait calls
`vTaskPlaceOnEventListRestricted` at0x961b8;0x96208 is a different event-list
operation. Existing startup-owned timer queue/lists/pointers are reused;
`prvSampleTimeNow.xLastTime` occupies0x20007864 in the isolated runtime test.

Run `python r1/tools/check_rtos_timer_stage.py` after the three isolated
verifiers. It validates report/input/source-slice/receipt hashes and links the
new source objects with the current board object. The staged link resolves
`r1_native_timer_task` and adds no unresolved symbols. Its29,319 isolated
comparisons are **not** a combined runtime-graph result. These additions remain
outside the canonical board/frontier: the tested frontier remains488 until
actual queue, restricted task wait, heap and scheduler workflows are composed
and audited. Source completeness, original instructions, whole-image layout,
full vectors, actual exceptions and byte identity remain open.


`rtos-timer-runtime/graph-verification.json` now adds240 combined comparisons
across48 workflows (24 static/24 dynamically allocated timer controls). Run
`python r1/tools/verify_timer_runtime_graph.py` after the staging check. Actual
kernel startup constructs the static timer queue and system tasks, bounded
before port entry. Actual queue send/receive, timer commands/expiry, restricted
queue/task wait, delayed/suspended placement, scheduler suspend/resume, and heap
malloc/free then execute together. Native/source entry counts match:288 queue
receives,48 restricted queue waits and48 restricted task waits,96 scheduler
suspend/resumes,24 allocations and24 frees per implementation. Controlled tick
writes cover arithmetic wrap; the runtime samples time and swaps timer lists
before processing post-wrap expiry. A queue-driven stop command wakes the blocked daemon through the actual
event-list providers; a subsequent delete command exercises static/dynamic
reclamation. Timer-control setup
and callback returns remain explicit fixtures. Task transfer, the timer task
loop itself, actual exception delivery and physical time do not execute in
this graph. Canonical board placement and strict frontier admission remain
pending; the isolated-stage receipt deliberately keeps its narrower claim.


### Timer factories and ISR commands: later graph supersedes control fixtures

`rtos-timer-api` now compiles unchanged pinned `xTimerCreate`,
`xTimerCreateStatic`, private initialization and `xTimerGenericCommand`.
Its4,813 isolated comparisons include853 assertions, all status-byte values,
NULL/allocation failure, period validation and task/ISR command routing.
`rtos-timer-isr-queue` adds actual ISR queue send/copy/lock-increment bodies:
9,225 comparisons,2,690 assertions, with explicit event-removal/task-count
fixtures. Its scoped header restores the native priority-validation call that
was disabled by the baseline header include order. An independent unchanged
Nordic priority-validator build passes13,440 comparisons/7,016 assertions over
controlled IPSR, NVIC priority, AIRCR grouping and native port state. The graph
uses the already-owned board `rtos-critical` validator; the independent copy
is not linked twice. Ghidra-MCP/REA evidence receipts accompany these modules.

The latest `rtos-timer-runtime/graph-verification.json` now records480
comparisons/96 workflows,48 dynamic/48 static, including48 ISR command routes.
Actual factories replace the earlier control-initialization fixture; actual
generic commands replace direct message setup. Queue send/receive, timer
expiry/stop/delete, blocking/wakeup, source heap and SDK priority validation
compose without provider interception. Callback returns remain fixtures.
The graph checks the12 defined message bytes and excludes exactly four
uninitialized padding bytes per16-byte queue slot. Allocator caller LR is
normalized only after validating its BL target and constructor call site.
Task/exception transfer and physical time do not execute. Locked ISR queue
increments retain a task-count-query fixture in isolated tests; the graph
uses unlocked ISR sends. Canonical board layout/frontier admission and timer
task-loop composition remain pending; the earlier stage linker receipt
still deliberately covers only its original three objects.


### Native task count and bounded daemon iteration

`rtos-task-count` selects the unchanged pinned `uxTaskGetNumberOfTasks` body,
sharing the existing kernel word at0x20007824 and owning no duplicate state.
Ghidra-MCP authenticates its native0x9566c span; the REA inventory reference is
recorded. ISR queue tests now link this actual getter instead of intercepting
it. The expanded ISR suite passes27,657 comparisons with8,450 assertion cases;
lock/task-count saturation includes127/128 and unsigned32-bit boundaries. Event removal and mutex disinherit retain explicit isolated-test
fixtures; priority validation, mask/restore and movement execute actual code.

The combined graph retains480 comparisons/96 workflows and now executes one
complete native/source daemon iteration in each workflow. A queued delete
command prevents blocking in that iteration; execution stops before the next
iteration. Thus the real loop's expiry lookup, wait decision, command receive
and deletion compose without inventing exception dispatch or task resumption.
Provider entry counts match between implementations, including96 task-count
queries,576 queue receives,192 restricted queue waits,96 restricted task waits,
288 scheduler suspend/resumes,96 ISR sends/priority checks and48 allocations/
frees. Lower ISR lock saturation is separately tested with the real getter;
that locked route is not claimed as a full combined ISR/scheduler workflow.
Canonical board/frontier admission and physical/whole-image gates remain open.


### Canonical timer provider admission

The canonical board now includes the runtime, receive/restricted queue wait,
restricted task wait, timer API, ISR queue and task-count source objects.
`prvSampleTimeNow.xLastTime` is placed at0x20007864 and its four cold bytes
are compared against the native image. Existing queue, timer lists, task and
kernel counters retain their single shared owners. No duplicate priority
validator is linked. `audit_rtos_timer.py`, called by the frontier audit,
reconstructs every selected timer/task source unit byte-for-byte from the
pinned licensed upstream slices and explicit ABI declarations, validates all
input/object/receipt/evidence hashes, and requires the canonical combined
graph and native/source provider counts. This supersedes earlier staging-only
admission notes in this document.

The audited frontier contains503 tested contract candidates,1,410 compiled
symbol hints and1,413 unresolved routes out of3,326 unchanged ownership rows.
The15 new tested entries include the native restricted waiter at0x961b8;
a supplemental authenticated correction records its restricted FIFO/indefinite
wait semantics without changing the original CSV. The unindexed timer task,
inlined next-expiry and switch-list paths are exercised without inventing
separate ownership rows. Bounded daemon iteration, callback fixtures and
message padding/LR normalization retain their stated limits. Combined locked
ISR/scheduler workflows, actual callbacks, blocking task resumption, physical
interrupts/time and whole-image source/byte closure remain open.


### CMSIS message queues admitted to the canonical graph

The pinned CMSIS-FreeRTOS wrappers `osMessageQueueNew/Put/Get/GetCapacity/
GetCount` now execute with real kernel queue providers in the canonical board.
Creation uses the authenticated80-byte static queue and24-byte attribute
layout; registry0 is scoped to the native wrapper. Names, attribute bits and
message priority remain ignored as in the native body, and unchecked32-bit
attribute product arithmetic is preserved. The18,240 isolated wrapper cases
retain explicit lower queue/scheduler fixtures, separating attribute acceptance
from kernel allocation or physical execution.

`rtos-queue-receive-isr` adds unchanged pinned ISR receive, copy-from-queue and
message-count providers. Its9,239 isolated comparisons include644 assertions,
ring/empty behavior, overlap, waiter signaling, lock saturation and actual
native task-count/priority/movement providers. Event removal and critical
boundaries remain explicit in that isolated test. The canonical graph uses
actual critical/heap/query bodies and passes4,800 comparisons across192
static/dynamic queue lifetimes and768 messages per implementation. It covers
task/ISR send/receive, capacity/count, full/empty, two ring rounds, dirty heap,
masked prekernel calls and deletion/reclamation without provider interception.
These nonblocking workflows have no waiters; blocking scheduling, actual ISR
delivery, physical concurrency and original instruction bytes remain gates.

`audit_rtos_message_queue.py` validates pinned source-slice reconstruction,
compiler inputs/objects, all lower-provider receipts, native Ghidra-MCP bytes,
REA inventory references and canonical graph hashes/counts. Seven ownership
entries are newly admitted, including transitively exercised copy-from-queue;
unindexed count-query bodies are not assigned invented ownership rows. The
frontier is510 tested candidates,1,403 compiled hints and1,413 unresolved routes.
The full canonical regressions and2,972-function corpus check pass. The five
wrapper symbols are no longer unresolved board references. Semaphore/mutex/
thread-flag wrappers and the remaining firmware components stay in scope.


### Semaphore/mutex source staging

`rtos-synchronization` compiles unchanged pinned CMSIS mutex creation/acquire/
release and semaphore acquire/release/count wrappers. The18,192 native unit
comparisons cover recursive pointer tagging, robust rejection,80-byte static
storage/16-byte mutex attributes, task/ISR restrictions, timeout/resource
statuses, wake-yield and counts. Kernel queue and scheduler calls remain
explicit fixtures in this wrapper unit.

`rtos-mutex-tasks` selects unchanged pinned held-count increment, priority
inheritance and timeout disinheritance bodies against the authenticated
104-byte accessed prefix of the native112-byte TCB. Its5,162 comparisons
include1,024 assertions, ready/blocked holders, event-list ownership bits,
priority/base/highest combinations and held-count wrap, using actual list
primitives. The already canonical current-task getter is reused, avoiding a
duplicate definition. The selected kernel mutex/semaphore module reuses
public queue create/send providers instead of embedding duplicate bodies.

`check_rtos_synchronization_stage.py` binds source-slice/input/object/receipt
hashes and Ghidra-MCP spans/REA inventory, then links all three new objects
with the canonical board. It resolves six CMSIS symbols without adding an
unresolved symbol. The23,354 isolated comparisons establish wrapper and task
helper contracts; **rtos-mutex-kernel bodies are compiled but not yet
native-differentially verified**. That kernel unit and the composed
synchronization graph remain admission gates. These additions do not promote
the canonical510-entry tested frontier, establish physical scheduling or
close any whole-image byte gate.


### Canonical synchronization admission

The staged semaphore/mutex providers are now native-verified and admitted.
The kernel unit passes5,562 comparisons/2,444 assertions, adding nonempty
highest-waiter timeout paths to creation, recursive ownership/count wrap,
semaphore take/retry and ISR give/lock saturation. Together with18,192 wrapper
and5,162 task-helper comparisons, the selected source modules have28,916
isolated comparisons with their explicit lower-fixture scopes.

`board/synchronization-verification.json` adds1,344 composed comparisons over
64 lifetimes. Actual static task constructors produce both native112-byte
TCBs; actual CMSIS/kernel/queue/heap/list/critical providers then exercise
static/dynamic normal and recursive mutexes, recursive wrong-owner rejection,
64 inheritance/restoration lifetimes,320 semaphore operations, task/ISR routes,
full/empty states and reclamation. Task selection is controlled by writes to
the shared current-task pointer; inheritance is invoked explicitly, without
blocking or context transfer. Task code and stack frames are not compared by
this graph. IRQ/mask/MMIO inputs and authenticated allocator-LR normalization
retain their stated limits. This does not prove physical scheduling.

`audit_rtos_synchronization.py` reconstructs all selected C byte-for-byte from
pinned licensed source slices plus explicit native interface text, and binds
compiler/input/object/receipt/evidence/canonical graph hashes. The canonical
board shares existing queue create/send/current-task providers and kernel
state, avoiding duplicate public bodies. Sixteen entries are admitted; the
frontier is526 tested candidates,1,387 compiled hints and1,413 unresolved
routes. Full canonical regressions and the2,972-function corpus check pass.
Blocking resumption, callback bodies, physical concurrency and whole-image
source/byte closure remain open. Notification/event/delay source routes are
next in `rtos-synchronization/next-target.json`.


### Indexed notifications, flags and delay staging

`rtos-notification-wrappers` selects unchanged pinned CMSIS thread flags
set/wait, event flags set and delay bodies. Its25,128 native comparisons cover
31-bit thread/24-bit event masks, task/ISR/context predicates, set/query order,
wait-any/all/no-clear accumulation, tick wrap/timeout, deferred event returns,
wakeup signaling and zero delay. Lower notification/event/tick/delay calls
remain explicit fixtures in this wrapper unit.

`rtos-notification-tasks` selects unchanged indexed notify task/ISR/wait and
delay bodies, private delayed/reset helpers and native112-byte TCB spelling.
The one supported notification slot has value at104 and state at108. Its14,840
comparisons include4,830 assertions, notification actions/overwrite policy,
previous values, ready/delayed wakeup, scheduler-suspended pending-ready
placement, clear-on-entry/exit, wait return values and delayed rollover. List
primitives and priority validation execute actual source; critical and
scheduler suspend/resume remain fixtures. Blocking code paths continue in the
emulator without real exception delivery/resumption, so these are bounded
memory/control-flow comparisons rather than temporal scheduling proof.

`check_rtos_notification_stage.py` validates source-slice/input/object/receipt/
evidence hashes and composes the source stage with the canonical board. The
39,968 isolated comparisons replace four unresolved wrapper references with
three explicit event-group provider references. Those providers and a
composed notification/event/timer graph remain required before canonical
admission. The tested frontier therefore remains526.

Fresh REA inspection of the authenticated analysis ELF confirms the event ISR
entry at0x9787c has a46-byte **noncontiguous** body:12 bytes at0x9787c..0x97887
and34 bytes at0x98d98..0x98db9. Native bytes and pseudocode show an event stub
feeding callback0x95c8c into a shared timer-pend implementation, posting
command-2 and event/bits parameters to the timer queue. The pseudocode's void
signature is weaker than the native caller's R0 test and pinned BaseType_t
contract. `event-next-target.json` binds these fresh REA/Ghidra observations;
no flat46-byte assumption or invented ownership row is admitted. Event body,
deferred callback and unordered-event wakeup source/graph checks remain open.


### Event-group and deferred-call source stage closed

`rtos-event-groups` now selects unchanged pinned event set/get-ISR/set-ISR and
callback bodies; `rtos-timer-pend` selects the shared ISR pended-call body.
Their combined4,568 native comparisons include917 matched faults, any/all
waiter matching, clear-on-exit/ordering, mask restoration, the actual event
callback/set path and all four defined command-2 message words. Unordered
wake and ISR queue/scheduler boundaries are fixtures in this unit. Callback
pointers are normalized only after exact native/source symbol checks. The
native32-byte event object and allocation flag at28 are independently bound
to the creation-body evidence; no creation provider is admitted by this check.

`rtos-unordered-event` selects the pinned wake/removal/reset body. Its7,290
comparisons include4,860 scheduler/owner assertion cases, valid unique task/
list fixtures, event control bits, neighbor/index updates, ready/delayed/
suspended records, priority/yield and next-unblock state. The suspend count
uses the existing native word0x20007850; it does not declare another owner or
assume the canonical private symbol is externally linked. No provider is
intercepted on that isolated wake path. Actual event delivery/resumption is
still a separate graph gate.

The notification source stage now binds all five selected modules and51,826
isolated comparisons. It resolves the four CMSIS wrapper references without
adding any unresolved symbol. `check_rtos_notification_stage.py` validates
current reports/objects/source slices/receipts/native bytes and fresh REA
noncontiguous-body evidence. That relocatable closure is not composed runtime
or canonical frontier admission: the frontier remains526 tested candidates.
The next gate is actual notification/event/timer queue/callback/unordered-wake
composition, followed by strict audit admission. Blocking resumption, physical
interrupts/scheduling and whole-image source/byte closure stay open.


### Canonical notification/event admission

All five selected notification/event modules now participate in the canonical
board. The51,826 isolated comparisons are supplemented by672 composed
comparisons over64 workflows. Actual static task/timer construction,
notification set/query/consume, delay code, event task/ISR producers, exact
negative callback messages, real ISR queue send, daemon iteration, callback,
event matching and unordered wake execute without lower-provider substitution.
Native/source entry counts agree:128 delay calls;64 each task notify, ISR
notify, notify wait, timer-pend, ISR queue send, event callback and unordered
wake;96 event-set calls. There are64 notification wakes,64 event wakes and64
bounded daemon iterations per implementation.

Current-task selection, initial notification-wait state and event wait-list
attachment are controlled fixtures. Event storage is fixture-initialized;
event creation is not admitted by this graph. Delay/wait code runs without
physical exception dispatch or actual blocked-task resumption, and no task
stack/exception-return claim is added. Callback pointers are normalized only
after exact function/payload validation.

`audit_rtos_notification.py` reconstructs selected C from pinned source slices
and explicit interface text, validates source/input/object/native/REA/graph
receipts and preserves the12+34-byte noncontiguous event/shared implementation.
Supplemental mappings refine indexed notify-wait and void unordered-wake
names without rewriting the authenticated ownership CSV or inventing rows.
The frontier now has538 tested candidates,1,378 compiled hints and1,410
unresolved routes. The four remaining CMSIS flag/delay wrapper references
are resolved. Full canonical regressions and the2,972-function corpus check
pass. Product provider recovery continues at
`rtos-notification-wrappers/next-target.json`; whole-image closure is open.

The canonical source-test executable grew to64,220 bytes and overlapped the
old test-guard region. The harness now separates unresolved-call guards at
0x1100000 from its bounded source-text window; standalone timer callback
fixtures use0x1200000. Guard checks remain enabled. A temporary-file lifetime
error in receipt generation was corrected, then the full suite reran cleanly.
These are test-layout changes, not original image placement or byte identity.

### Product delayed scheduler, 0x65b4c

`native-delayed-schedule` compiles the recovered scheduling body and passes
1,200 native/source comparisons across readiness waits, immediate delays,
all first-free-slot boundaries, full tables, null callbacks, arithmetic wrap,
mutex failures and repeated/changing logging modes. The harness compares
provider traces, all six context words and all192 table words. REA pseudocode
and an independent Ghidra-MCP308-byte read bind the stock contract.

The body preserves scheduling after lock failure, ignored timer-stop status,
32-bit tick multiplication before shifting and null callback acceptance.
Lower providers remain fixtures in this isolated receipt. Source-owned state
initialization and canonical board composition remain gates; the frontier
has539 tested candidates,1,378 compiled hints and1,409 unresolved routes.
No instruction identity or complete-image closure is claimed.

`native-delayed-schedule/next-target.json` records immediate push, timer callback
and CMSIS timer-stop recovery. Native instructions confirm that the callback
excludes minimum delay0x7fffffff while initializing its minimum to0xffffffff;
that quirk must not be silently corrected in reconstructed source.

### Immediate event push, 0x659e8

`native-delayed-push` compiles the product queue-push body. It passes2,304
native/source comparisons plus1,536 comparisons composing the real recovered
delayed scheduler with the real recovered push body for delay0/1. Tests cover
missing readiness/queue, null callbacks, argument and timeout forwarding,
queue status outcomes, fixed/changing log modes and backend context mutation.
Provider traces and complete context/table state match; the queue record is
exactly `[argument, callback]` with priority0. The apparent fourth Ghidra
argument is saved scratch in the early readiness logging path, not a semantic
input. The source keeps the existing three-argument void caller interface.

An independent Ghidra-MCP144-byte read and retained REA pseudocode bind the
native entry. Lower queue/log/timer providers remain controlled fixtures in
this receipt. Actual queue composition, timer callback recovery, timer control,
state initialization and canonical board integration remain open. The audited
frontier is540 tested candidates,1,378 compiled hints and1,408 unresolved
routes; there is no original instruction identity or whole-image closure claim.

### CMSIS timer controls and timer-active predicate

`rtos-timer-controls` compiles unchanged pinned CMSIS `osTimerStart`0x7d9b0
and `osTimerStop`0x7d9ea. `rtos-timer-active` compiles unchanged pinned
FreeRTOS `xTimerIsTimerActive`0x98d68, with44-byte timers and status byte40.
The controls call the real recovered timer-active body in the differential
harness. There are2,880 comparisons per CMSIS wrapper and1,024 timer-active
comparisons, including512 native/source assertion paths. Inputs cover interrupt
and scheduler state, masks, null handles, tick boundaries, command outcomes,
all256 status bytes and controlled status mutation across critical boundaries.

The receipt compares return values, backend traces, timer state and masks;
returning paths also check stack and saved registers. Assertions compare the
native unmapped zero write and BASEPRI64 without asserting restored stacks.
Critical sections, scheduler state and generic timer command are fixtures.
`audit_rtos_timer_controls.py` reconstructs generated C from pinned byte slices,
licenses and explicit interfaces, and authenticates current build/native inputs.

REA returned start/stop pseudocode. The timer-active REA request failed with
`execution_failure`; it is not counted as positive evidence. Native instructions,
the corpus and an independent Ghidra-MCP byte read bind that body. Actual
provider/queue/product composition and canonical integration remain gates.
The frontier now has543 tested candidates,1,375 compiled hints and1,408
unresolved routes. Whole-image and original instruction identity remain open.

### Product timer callback, 0x65f84

`native-delayed-reschedule` compiles the timer callback from recovered behavior.
It passes3,840 isolated native/source comparisons and3,840 more composing the
actual recovered immediate-push body. The verifier compares the complete
six-word context,192 table words, logging/provider traces and every queue-push
boundary. Controlled queue submission mutates earlier and later slots to check
that the first and second table passes retain native ordering and observations.
Both implementations preserve clear-before-push, elapsed input override,
unsigned deadline subtraction, mutex failure continuation, minimum selection,
timer-start status logging and wrapped32-bit tick conversion.

The native minimum starts atUINT32_MAX, while its final exclusion isINT32_MAX.
Consequently an empty table can start a timer withUINT32_MAX. Reconstructed C
preserves this behavior, as well as the zero-minimum early return. Tests span
empty/full/sparse tables, first/middle/last slots, expiry/sentinel boundaries,
fixed/changing log modes, timer/mutex/queue outcomes and controlled reentrancy.
The composed cases record16,326 queue-submission boundaries per implementation;
the isolated cases record16,320 push-provider boundaries per implementation.
The sets use independently deterministic inputs, so their event totals need
not match one another; native and source totals match within each case.

REA pseudocode and an independent Ghidra-MCP376-byte read authenticate the
entry. Timer controls, queue, critical sections and logs remain fixtures here;
there is no physical callback execution, canonical board admission, state
initialization or instruction-identity claim. The frontier has544 tested
candidates,1,375 compiled hints and1,407 unresolved routes. The next work is
the actual timer/queue provider graph and remaining event-loop initialization.

### Delayed product/provider composition and initializer coverage gate

`check_native_delayed_stage.py` links the canonical source board and all selected
product scheduler/push/callback and pinned timer-control/active objects without
stubs. It resolves the board's scheduler reference and introduces only the
four known context/table anchors. This stage is separate from canonical board
admission and preserves the unresolved source-initialization requirement.

`verify_native_delayed_graph.py` passes30 native/source state comparisons in12
workflows. Actual static queue/mutex/timer factories, product scheduling, timer
stop/start/active/command paths, daemon command processing, timer expiry,
product callback/push and queue receive execute. Matching counts include18
schedule calls,30 callbacks and starts,18 stops,36 generic commands,12 queue
puts and348 critical enter/exit pairs per implementation. It compares product
state, queue/timer structures, daemon buffers, timer lists and kernel state.
The callback pointer is normalized only after identity verification, and only
four undefined padding bytes per16-byte daemon command are excluded.
Source execution cannot enter stock code or unresolved-call guards.

Shared authenticated cold RAM, product context/table initialization and current
scheduler setup remain fixtures; startup stops at port-start, and physical
scheduling/blocking is not established. The first expiry is delivered and
received per workflow; a second pending event is not claimed as delivered.
No canonical board, complete-image or original-instruction claim is added.

Tracing native context literals identifies initializer0x65740 (return0x65864),
which creates a15-by8-byte queue, timer callback0x65f85, mutex and worker0x65ea9.
It reuses existing object handles but terminates/recreates an existing thread.
Neither initializer0x65740 nor worker0x65ea8 appears in the locked ownership
CSV/corpus scope. This is an explicit supplemental recovery gate, not a new
row added to the locked accounting. REA exact-entry lookup did not recognize
the initializer; the error's file-offset fallback is not positive pseudocode
evidence. An independent Ghidra-MCP296-byte read matches the locked application.
See`native-delayed-reschedule/initialization-next-target.json`. The2,972-function
corpus structural check does not establish recovery of these additional bodies.

### Supplemental initializer and source-owned delayed state

The initializer0x65740 now compiles from supplemental instruction-backed
pseudocode. Its3,072 native/source comparisons cover1,536 two-call sequences:
all existing-handle/factory-failure combinations, fixed/changing log modes,
termination failure and repeated initialization. Traces and all context/table
words agree. Factory/thread-lifecycle bodies remain fixtures. This supplements
the locked accounting; its entry is not added to or counted as a CSV/corpus row.
`native-delayed-initialize/supplemental-pseudocode.txt` records the recovery.

`native_delayed_state.c` owns the six-word context, three64-word tables,
static queue/mutex/timer/thread storage and typed source attributes. Generated
section sizes/zero bytes are checked against observed stock cold RAM; attributes
match native names, sizes, pointers, priority and flags. The stock timer name
matches its mutex name, and thread storage is112 bytes with a3,072-byte stack.
The initializer reuses queue/timer/mutex handles but terminates, clears and
recreates the thread. It does not reset scheduling tables or epoch words.

The source stage now resolves all four formerly unresolved storage anchors.
The30-comparison/12-workflow provider graph passes with actual source storage
sections in place of linker-symbol substitutions. Product runtime initialization
in that graph remains a fixture: actual initializer/factory/thread lifecycle
composition, worker0x65ea8 recovery and canonical board admission are next.
Pinned CMSIS osTimerNew0x7d90c and osThreadTerminate0x7d8d6 are available upstream.
The locked frontier remains544 tested candidates/1,375 hints/1,407 unresolved;
the initializer is separately reported as a supplemental native candidate.

### Supplemental delayed-event worker, 0x65ea8

`native-delayed-worker` compiles the instruction-backed queue loop outside the
locked corpus/ownership rows. Its1,512 bounded native/source comparisons cover
three-receive sequences with success and four error statuses, fixed/changing
log modes, callback-driven queue-handle changes and12 null-callback faults.
There are912 callback invocations per implementation in the isolated receipt.
Successful queue fixtures write all eight record bytes. Error paths log and
retry; no null callback guard is invented. No return/restored-frame claim is
made for this nonreturning worker.

The source stage includes the worker without new unresolved providers. The
actual queue/provider graph now dispatches through the real worker:12 timer
expiry workflows deliver the expected argument to a controlled user callback,
then stop at the next empty-queue receive boundary before blocking. Actual
queue gets, timer/mutex/critical providers and product bodies execute, with
matching native/source entry counts and no stock-code execution in the source
run. Physical blocked receive/resumption and actual user callbacks remain open.

Locked frontier counts remain544/1,375/1,407. The summary separately tracks two
supplemental candidates, initializer0x65740 and worker0x65ea8. Their discovery
and recovery do not change the authenticated corpus/ownership inputs. Next
are pinned CMSIS timer creation/thread termination and actual initialization.

### Pinned CMSIS timer creation and real callback-ID retrieval

`rtos-timer-new` compiles unchanged pinned CMSIS `osTimerNew` and its static
callback trampoline;`rtos-timer-id` compiles unchanged FreeRTOS
`pvTimerGetTimerID`. The4,778 native comparisons include4,752 creation cases,
16 callback cases and10 ID cases, with15 assertion/null-callback faults.
Creation covers interrupt/scheduler masks, null functions, once/periodic types,
static-block and callback-metadata size boundaries, allocation/factory failure
and cleanup. The callback uses the real getter, strips the allocation tag and
calls the controlled user callback. Fixtures remain at heap/factory/critical
boundaries. No hardware/whole-image behavior is asserted.

For the product's44-byte timer block CMSIS allocates an additional eight-byte
callback record. A52-byte block can own that metadata inline. Generated source
is reconstructed from pinned slices with licenses and explicit native layout
assertions by`audit_rtos_timer_new.py`. REA returned creation and callback
pseudocode; the ID query failed and is not positive evidence. Native caller,
getter instructions and independent Ghidra-MCP bytes support the ID contract.

The native0x8569c row was labeled task application tag in the locked ledger.
The actual CMSIS callback passes its timer and reads callback metadata from
the returned ID. Supplemental`rtos-timer-new/attribution-correction.json`
records the original row and effective timer-ID mapping, without editing it.
The frontier now has546 tested candidates,1,374 hints and1,406 unresolved routes.

`osThreadTerminate` was already implemented and admitted in the canonical
termination module, so it is reused. The product stage now includes actual
initializer, worker, state, timer creation/callback/getter and existing board
providers with no new unresolved symbols. Its existing30-comparison dispatch
graph remains green. Actual initializer execution with heap/lifecycle providers,
canonical admission and original-image closure remain open.

### Actual delayed-event initialization and reinitialization graph

`verify_native_delayed_initialization_graph.py` now executes actual product
initialization with pinned CMSIS queue/mutex/thread/timer constructors, native
source heap, callback metadata, existing task termination and the full product
schedule/expiry/worker dispatch path. There are60 native/source comparisons
across24 workflows;12 workflows call initialization twice, exercising actual
thread termination and recreation while reusing queue/timer/mutex handles.
Factory or heap bodies are not intercepted, and source execution cannot enter
stock code or unresolved-call guards. Per implementation there are36 initializer
and thread-create calls,24 timer creations/allocations,12 thread terminations,
24 actual timer callbacks/ID reads,24 worker dispatches and804 critical pairs.

Snapshots compare context/tables, queue storage,112-byte thread control block,
full3,072-byte initial thread stack, mutex/timer structures, the complete51,200-
byte heap and its state, timer/kernel list roots and1,220 bytes of task lists.
Only known code/name pointers are normalized after exact identity checks:
timer name and CMSIS callback, heap callback entry, initial worker PC/task-exit
LR and allocator debug LR. The latter is checked within the exact source
`osTimerNew` extent and its preceding BL must target the selected allocator.
Only the four undefined padding bytes per16-byte timer command are excluded.

Authenticated cold RAM and scheduler-start boundary remain controlled fixtures;
this is not complete source-startup proof. The actual worker stops at its next
empty receive boundary; its user callback is controlled. Physical context
transfer/blocking/resumption and complete instruction/layout/image equality
remain open. Source-owned product initialization and real heap/lifecycle
composition are now supported by this receipt. Canonical board admission,
cancellation0x65d64 and remaining whole-firmware providers are next gates.

### Delayed-event cancellation, 0x65d64

`native-delayed-cancel` compiles cancellation and passes6,912 native/source
comparisons, including2,735 matched cases. REA pseudocode and an independent
Ghidra-MCP228-byte read bind the entry. The tests compare return value, provider
traces, the six-word context and192 table words, plus preserved registers/SP.
Inputs cover no readiness, first/middle/last/multiple/absent matches, callback0,
argument0 wildcard, mutex failures, changing log modes, wrapped tick arithmetic
and controlled epoch changes during tick retrieval and timer stop.

The stock body ignores mutex-acquire failure and clears only matching callback
words. It also matches already-empty callback slots when callback0 is requested;
this can return1 and trigger timer recalculation. Tick retrieval precedes the
epoch read, while elapsed time is captured before timer stop. Reconstructed C
preserves these details rather than adding occupancy guards or changing errors.

The actual initialization graph now includes12 cancellation workflows: the
second pending event is removed with the actual mutex/timer/queue providers,
then the first expires and dispatches through the worker. There are still60
comparisons/24 workflows and12 reinitializations. Native/source counts match,
including12 cancellations,72 timer starts,48 stops,96 generic timer commands
and948 critical pairs per implementation. Source storage, heap and validated
pointer-normalization checks remain in force. The independent original dispatch
graph also passes after the staged object update.

The locked frontier now has547 tested candidates,1,374 hints and1,405 unresolved
routes, with initializer/worker kept as separately documented supplemental
candidates. Canonical source-board/layout admission and related regressions
are next; complete source startup, remaining image providers, physical context
transfer and original compiler/layout/instruction equality remain gates.

### Canonical delayed-event source admission

The canonical board now includes all11 selected delayed-event product/state and
CMSIS/FreeRTOS timer objects. Source-owned storage has explicit authenticated
RAM sections in the canonical native-test layout, and all selected bodies and
attributes are kept as test roots. There are no duplicate stage inclusions:
`check_native_delayed_stage.py` detects canonical object membership and links
the board alone. Its output adds no unresolved symbols. The canonical board
now has62 remaining provider symbols and67,240 source-test text bytes.

Both source graphs pass from that canonical object:30 comparisons/12 dispatch
workflows, plus60 comparisons/24 actual initialization workflows with12 thread
reinitializations and12 cancellations. Full canonical notification, sync,
message queue, overflow/logging, context/port/scheduler, idle, termination,
task/thread/application construction, queue timeout/lifecycle, initcall/real
heap/real scheduler, RTC and logger-pipeline regressions pass after admission.
The separate timer graph also passes480 comparisons/96 callback workflows.
Stage receipts and strict frontier checks are refreshed against the current
board/report/driver hashes. The locked frontier counts remain547/1,374/1,405.

Canonical source-board admission is separate from complete image placement,
source startup, original compiler/instruction equality and physical scheduling.
Those gates and all remaining firmware components remain open. The next actual
board providers are service/storage hardware-init wrappers0x45c84/0x45d00:
the accumulated pseudocode shows logging only, so their names must not be
promoted to hardware-initialization evidence.

### Service/storage initialization-log wrappers

`native-thread-init-logs` compiles0x45c84 and0x45d00 under their existing caller
bindings. Each is a log-only native body, with repeated/short-circuited mode
reads, ring marker0x0c000000 and SDK module28/severity3. They do not perform
hardware initialization. Accumulated pseudocode, fresh REA pseudocode and two
independent Ghidra-MCP64-byte reads bind the recovered control flow.

The wrappers pass4,394 native/source comparisons (2,197 each), covering all
three-read combinations of13 low/high-bit mode values. Tests compare exact
getter/backend traces, strings, severity/module values, duplicate ring format
pointer, stack and preserved registers. Void scratch returns are excluded.
Lower logger providers are controlled fixtures in this receipt; concrete
logger composition and canonical board admission remain explicit next gates.
No physical-device or firmware initialization proof is inferred from the names.

The locked frontier now has549 tested candidates,1,374 hints and1,403 unresolved
routes. The canonical board still has62 unresolved symbols until these new
objects are integrated. Whole-image startup/provider/byte-identity gates remain.
See`native-thread-init-logs/next-target.json`.

The initialization-log wrappers also own four distinct C string sections at
the native service/storage ring and SDK addresses. The structured logger
encodes descriptor addresses into records, so equal text alone is insufficient.
The strengthened4,394 comparisons check actual descriptor/string pointer values
as well as text and validate the generated section bytes against native spans.
This retains source-owned descriptor IDs for subsequent concrete composition;
no opaque executable data or fixture provider is added to production C.

### Canonical initialization-log wrappers and concrete log graph

The service/storage log wrappers and all four source descriptor/string sections
are now in the canonical board, reducing its remaining symbols from62 to60.
`verify_native_board.py --thread-init-logs-graph` authenticates descriptor data
at native addresses and executes the wrappers through actual structured-log
routing/encoding/cache and Nordic frontend/pool/backend/serial/calendar/RTT
providers. The isolated4,394 comparisons remain a separate control-flow check.

The concrete graph passes2,592 comparisons across384 workflows: all modes0..7,
clock/export state combinations, three timezone offsets, immediate/deferred
Nordic output and controlled host drain. There are768 wrapper invocations,
384 Nordic messages/RTT writes and624 actual RTC timestamp calls, with15,360
accepted RTT bytes per implementation. Raw structured-cache bytes, descriptors,
sequence/state, export buffer and Nordic backend state are compared without
pointer normalization. The records remain below event/BLE export thresholds.

This graph clones authenticated canonical images into Cortex-M-class Unicorn
engines so IPSR instructions execute directly; it does not intercept those
instructions. Source execution cannot enter stock code or unresolved-call
guards. Original canonical machines remain isolated from this graph's state.
Physical scheduling/concurrency, export thresholds, complete startup and
original-image instruction/layout equality remain gates. These bodies still
log only and do not establish hardware initialization.

The next actual board provider is status-ring publisher0x5e118, reached by the
advertising configuration path. Fresh REA evidence is retained with the next
target. Record packing, ring data initialization, three state-getter providers
and the final event-publish ABI require native validation before source admission.

The final full canonical suite passes with the expanded all-mode graph enabled;
all delayed-event and timer-stage receipts are refreshed against the new board.
The strict source frontier audit, corpus check and whitespace check pass. The
canonical native-test text is67,336 bytes and60 board symbols remain unresolved.
These test/layout figures are not original image placement or byte identity.

### Status-record publisher and real state getters

`native-status-record` compiles0x5e118 and the peer/device/charge getters at
0x4cb08/0x91264/0x91270. Fresh REA pseudocode and independent Ghidra-MCP reads
bind all four bodies.21,008 native/source comparisons pass:17,664 publisher,
256 device-byte,16 peer-channel and3,072 charge-byte cases. Publisher cases
execute the actual selected getters; configuration/updater/timestamp/critical
and final event publication remain controlled fixtures.

The packed word fills all32 bits: type nibble0xa, two kind bits, six event bits,
six value bits, three detail bits, two device bits, two peer bits and seven
charge bits. A second word stores local timestamp. Timestamp precedes critical
entry, and the ring state is read after entry. Valid write indices0..15, all
read/write positions, full-ring cases, input truncation, getter side effects
and controlled pre-critical/at-entry state changes are checked. There are1,759
drop-counter updates and17,664 unconditional drain-event calls per implementation.

Native LDRH/STRH at0x5e192/0x5e196 show a16-bit drop counter at0x2000693c;
the decompiler's32-bit spelling is corrected in supplemental evidence without
editing the locked corpus. Adjacent-byte and record-boundary sentinels remain
unchanged, including on overflow. The final event tail call sets all three
arguments explicitly to0x2003,0,0. Scratch returns of the void publisher are
not compared. Device/charge roots and ring initialization remain unresolved.

The configuration byte70 accessor is already admitted as
`r1_advertising_configuration_byte_get`0x7ba24 and is reused. No duplicate body
is added. The charge getter calls battery updater0x31fd0 only for exact0x55,
then reloads its byte and maps0 to1. Actual battery/runtime and whole-provider
composition remain gates. The locked frontier now has553 tested candidates,
1,374 hints and1,399 unresolved routes. Canonical board symbols remain60 until
this block is composed/admitted. See`native-status-record/next-target.json`.

### Battery runtime updater, 0x31fd0

`native-battery-runtime` compiles the406-byte native updater contract as recovered
C.2,896 native/source comparisons pass, including336 explicit numeric/FPSCR
cases and randomized state transitions. They compare return value, complete
provider traces, device/runtime memory with boundary bytes, saved registers/SP
and final FPSCR under all four rounding modes. Charging/session setup, zero-tick
fallback, persisted-state retention, offset bounds, sample and level rings,
level-increase suppression, reporting and callback-driven state reloads agree.

The scaling path sign-extends the sample's low16 bits, reinterprets it as
uint32, converts to float32, divides by scale bits0x3f86c8b4 and truncates to
uint32 before storing low16. Signed float conversion is not equivalent. Initial
C compilation speculated float operations outside the charged condition and
changed FPSCR on the uncharged path. A volatile unsigned input inside the branch
now keeps those operations conditional; the strengthened native checks pass.

Native charged-state refresh0x3dd0c takes five semantic arguments; an independently
read144-byte callee and the caller's one explicit stack argument contradict the
decompiler's scratch sixth value. Fresh REA and Ghidra-MCP evidence bind the
updater and supplemental ABI observations without editing locked corpus data.
The status consumer now declares the same uint32 return ABI and its21,008 native
checks rerun cleanly after the interface correction.

Lower hardware/algorithm/report providers remain controlled fixtures. Device
and runtime roots are typed address bindings, not source-owned initialization.
Packed native-width SRAM views preserve unaligned values in the selected build;
physical interrupt ordering, atomicity and FPU/concurrency remain unproven. Actual
updater/status composition and canonical board admission remain gates. The
locked frontier now has554 tested candidates,1,374 hints and1,398 unresolved
routes. Next are charged-state refresh, voltage and level averaging, together
with shared state ownership and remaining provider closure.

### Charged-state refresh and battery statistics

`native-battery-statistics` compiles0x3dd0c/0x3dda0/0x3d834 from authenticated
native and REA contracts.5,536 direct native/source comparisons pass:1,440
refresh transitions,2,048 voltage averages and2,048 level averages. Tests cover
charging/noncharging/retry states, captured tick0 fallback, retained start data,
charge-counter bounds, callback-driven state changes, every zero/nonzero sample
mask, extreme and randomized values, and unaligned state fields.

Both averages ignore zero samples. With eight nonzero samples they remove one
minimum and maximum; level uses(sum-min-max+3)/6, while voltage truncates the
six-sample mean. With fewer samples both divide by the nonzero count. Empty
level input returns0; empty voltage input leaves the previous voltage unchanged.
Refresh takes exactly five arguments and preserves native tick/session capture,
retry-counter handling and shared-resource/progress-reset ordering.

`verify_native_battery_runtime.py --real-statistics` passes another2,896 native
comparisons with all three actual selected bodies and matching entry counts:
2,896 refresh, voltage-average and level-average calls per implementation.
The original updater unit receipt is refreshed separately against the same
driver. Remaining hardware/algorithm/report providers are still fixtures.

The runtime and statistics now share packed may_alias volatile16/32-bit SRAM
views and scoped`-munaligned-access`. Emitted code uses native-width halfword
accesses, including the unaligned field at device+49. This replaces earlier
bytewise helper accesses; no global kernel compiler/configuration is changed.
Physical interrupt ordering, bus atomicity and concurrency remain unproven.
The full memory, numeric and FPSCR comparisons remain green after this change.

The locked frontier now has557 tested candidates,1,374 hints and1,395 unresolved
routes. Device/runtime ownership, remaining providers, canonical integration,
source startup and original whole-image instruction/byte equality remain open.
Next are charging-progress reset, battery-task flags and shared-resource acquire.

### Battery control and shared power

`native-battery-control` adds six compiled bodies covering five ownership rows:
charging-progress reset, task-flag forwarding, client acquire/release and the
YHM active/inactive command wrappers. REA confirms the release body is
noncontiguous: 28 bytes at0x50758 plus the20-byte inactive command at0x35594.
The locked ownership row remains unchanged. Ghidra-MCP bytes are authenticated
against the application slices.

4,504 direct comparisons pass. The updater graph passes another2,896 comparisons
with actual statistics and control bodies, executing1,825 acquire/release calls,
2,004 reset calls and528 flag calls per implementation. Tests preserve raw
32-bit RTOS/transport status, invalid-client behavior and the acquire mask reload
after callback mutation. Transport and RTOS endpoints remain fixtures.

The native wrappers send register2, length1, payload0xa8/0x28. The existing
contextual YHM reconstruction exposes a different device-pointer/bool interface;
it cannot silently supply the recovered zero-context/raw-status ABI. Transport
binding and shared state initialization remain explicit gates. The frontier has
562 tested candidates,1,374 compiled hints and1,390 unresolved routes. These
battery modules remain outside the canonical board; full startup, instruction
identity, complete bundle byte equality and hardware behavior remain open.

### Native charger classifier

`native-charger-state` compiles the0x35272 classifier and0x50618 tail-call
adapter.4,616 native/source comparisons cover all byte values, high unsigned
boundaries and2,048 randomized32-bit statuses through each entry, with exactly
one raw-status call and preserved callee registers/SP. States10..12 map to1,
13 maps to2, and every other status maps to0.

REA body ranges contain26 instruction bytes over a40-byte span; the intervening
14-byte jump table is separately authenticated through Ghidra-MCP. The locked
ownership size remains26. The module links only against the explicit unresolved
`r1_yhm_status_native` boundary and is not admitted to the canonical board.
The frontier now has564 tested candidates,1,374 hints and1,388 unresolved routes.

The existing contextual YHM model corroborates the classifier but is not an ABI
alias. Native0x3529a pushes incoming r3, tests readiness, then reads register6
without checking the transport result; if that read leaves the byte untouched,
its result depends on the incoming stack byte. The contextual reconstruction
initializes0xc0 and checks read success. Raw transport/write guarantees or a
native input contract are required before substituting it. This remains an
explicit evidence gate, alongside actual battery composition and state ownership.

### YHM readiness and read frontend

`native-yhm-frontend` compiles readiness0x3541c and read adapters0x3540c/0x35412
with832 native/source comparisons. REA body metadata and Ghidra-MCP bytes bind
all three entries. Read adapters preserve full register argument/raw return,
truncate only length to8 bits, and forward byte reads with length1. Tests cover
transport output writes and no-write outcomes, including high unsigned inputs.
Readiness calls select(context,line), reloads the probe pointer and context after
that callback, then normalizes its full32-bit return to0/1. Callback mutation,
zero/high return values, byte-line bounds and register/SP preservation are tested.

The source has explicit unresolved callback-context and read-record providers.
This does not close native0x3529a's incoming-r3/no-write behavior. Context root
0x200075c4 remains a test binding, not source-owned configuration. The frontier
has567 tested candidates,1,374 compiled hints and1,385 unresolved routes.
Actual transport/updater graphs, canonical integration and complete source image
with original instruction/byte identity remain unresolved.

### YHM transaction records and completion

`native-yhm-transport` adds six compiled bodies covering four ownership rows:
resource acquire/release, register read, native write adapter, write record and
shared completion.2,928 native/source comparisons pass across byte/word input
bounds, transport output writes/no-writes, callback presence and state mutation
at every registry boundary. REA confirms the write body totals78 bytes across
0x35760..0x35765,0x50558..0x50571 and0x50804..0x50831. Ghidra-MCP authenticates
all entry blocks; the locked ownership row remains unchanged.

Both transactions release the auxiliary handle, acquire the current bus, update
selected bytes/words in the shared request, dispatch read/write, then release the
current bus and reload the optional completion callback. Completion returns the
last release result when absent, or callback(0)'s raw result when installed.
Dispatch results are not interpreted as read/write success. Native transport
state reloads and untouched request fields are preserved under callback mutation.

The existing admitted registry08/0c/10/14 interfaces are reused; this receipt
uses boundary fixtures and does not yet prove actual registry/bus composition.
Context0x2000687c and request0x20016b70 remain address bindings, not initialized
source-owned state. The frontier has571 tested candidates,1,373 compiled hints
and1,382 unresolved routes. Raw-status no-write semantics, full battery graph,
canonical admission, source image and original byte identity remain gates.

### YHM transport with actual registry dispatch

`verify_native_yhm_transport.py --real-registry` links the selected transport
object with the existing admitted `i2c5/stock_registry.o`, garbage-collecting
unrelated registry functions.11,712 comparisons pass across valid/null bus and
auxiliary handles, missing operation slots, raw result bounds, callback mutation
and transport writes/no-writes. Registry entries execute directly, with no
provider interception. Entry counts match native/source:11,584 slot08,
23,168 slot0c,3,840 slot10 and7,680 slot14. The receipt binds the registry report,
transport report/object and driver. The original2,928 boundary comparisons are
refreshed against the same driver.

Only lower operation callbacks remain fixtures in this graph. Handles/tables
are controlled test records; source-owned transport/context initialization,
actual frontend/control/updater integration, bus serialization and physical
hardware behavior remain gates. Frontier counts remain571 tested candidates,
1,373 compiled hints and1,382 unresolved routes; stronger composition evidence
does not add ownership rows or establish whole-image source/byte identity.

### YHM device-handle discovery

`native-yhm-initialize` compiles0x50578 from native/REA evidence, with Ghidra-MCP
authenticating its70 instruction bytes plus literal/name data.1,536 comparisons
pass in512 three-call workflows, covering every cached-handle/missing-lookup
combination and callback mutation. It lazily finds `device_stacmd`,
`ship_mode_en`, `device_stacmd_irq` and `vpmic_isns_adc`. Only an uncached ship
handle triggers slot08 then slot18(handle,0,0), even when lookup returnsNULL.
The handle is reloaded between those calls and later caches are reread after
callbacks. Missing lookups retry on subsequent initialization calls; cached
handles skip lookup/configuration. Raw void scratch returns are not claimed.

Registry lookup/dispatch remain fixtures in this receipt. The context remains
an external root; native reset/zero initialization and callback configuration
must be established before source-owned storage is admitted. The frontier has
572 tested candidates,1,373 compiled hints and1,381 unresolved routes. Actual
initialization/transport/updater composition, lower device bodies, whole source
image and original byte identity remain gates.

### Initialization with actual registry and musl strcmp

`verify_native_yhm_initialize.py --real-registry` now links the actual admitted
registry and pinned musl-memory1.2.5 `strcmp` objects.3,072 comparisons pass across
1,024 three-call workflows. Tests cover all initial-cache/missing-device masks,
missing operation slots and callback mutation. Registry lookup/08/18 and strcmp
are never intercepted in this mode; only selected lower operation callbacks are
fixtures. Native/source entry counts match:4,160 lookups,1,024 slot08 calls,
1,024 slot18 calls and6,536 strcmp calls. The original1,536 boundary comparisons
are separately refreshed against the same driver.

Controlled source-layout registry records are used in the composed test. This
closes selected registry/strcmp composition, not production record registration,
transport-context zero initialization, callback ownership or device behavior.
Whole transport/updater composition, canonical admission and full image source
and original byte identity remain gates. Frontier counts remain572 tested,
1,373 compiled hints and1,381 unresolved routes.

### Fixed-state STACMD operation bodies

`native-stacmd-operations` compiles0x56568/0x5657c/0x56590/0x5660c with1,580
native/source comparisons:256 close,256 open,960 read and108 write. These are
manual-provenance ownership entries; REA procedure_info yielded no structured
function metadata. The receipt therefore binds locked manual rows and Ghidra-MCP
bytes directly, and records the REA coverage limitation without claiming a
positive function result.

Open/close access the fixed configuration's byte4 and ignore device arguments.
Read checks null request before opened state, captures register/length/buffer,
then makes nine recovery/frame attempts. Each failed frame increments the32-bit
counter at0x200075c0; exhausted reads fill exactly length bytes with0xff and
return31. Success returns0. Write returns11 for null request,27 when closed,
otherwise maps the raw retry result to0/30. Tests cover counter wraparound,
callback mutation, high nonzero results and lengths0/1/3/255. Native cached
request values and absence of subsequent open-state checks are preserved.

Recovery/read-frame/write-retry remain fixtures. Configuration0x200075c4 and
counter0x200075c0 are address bindings; a shared typed registration ABI and
actual registration/transport integration remain gates. No null-output fallback
is added; nonzero-length null output faults are not claimed by this receipt.
The contextual YHM model has a different device-pointer policy and cannot be
silently substituted. Frontier:576 tested candidates,1,373 compiled hints,
1,377 unresolved routes. Full startup/source image/original byte identity and
physical wire timing/concurrency remain open.

### STACMD bus recovery

`native-stacmd-recovery` compiles0x5cc8c and passes240 native/source comparisons.
The trace preserves high/output/high, one delay, low, four more delays, then high
with the last callback's raw return. Native pin/callback fields are reloaded
between calls. Tests mutate those fields at each of the ten callback/delay
boundaries, plus no-mutation and all-boundary cases, across pin and raw-return
bounds. Ghidra-MCP authenticates58 native bytes and the locked ownership row.
REA procedure_info did not yield structured metadata; no positive REA function
metadata is claimed.

The five0x5c0fa delay invocations and GPIO callbacks remain test fixtures.
Instruction-backed timing details show209 iterations containing four NOPs, but
physical delay calibration is not established here. Frame/read/write-retry
bodies, actual adapter/transport composition and shared typed registration/state
ownership remain gates. Frontier:577 tested candidates,1,373 compiled hints,
1,376 unresolved routes. This source candidate is not canonically admitted and
does not establish whole-image source or original byte identity.

### Source delay and actual recovery composition

`native-stacmd-delay` compiles the209-iteration loop with four explicit NOP
mnemonics per iteration.64 direct comparisons verify zero return, preserved
callee registers/SP/stack and836 executed NOPs per call. A module-scoped
`-falign-loops=1` prevents an extra alignment NOP from executing. The compiler
uses a different loop schedule, so instruction equality and cycle timing are
not claimed. Ghidra-MCP bytes and the locked ownership row bind native0x5c0fa;
REA did not yield structured metadata for the query.

`verify_native_stacmd_recovery.py --real-delay` links and executes the actual
delay object.240 recovery comparisons pass with1,200 delay entries and1,003,200
executed NOPs per implementation. GPIO callbacks remain fixtures; delay is not
intercepted. The240 original boundary comparisons are refreshed separately.
Reports/objects/driver hashes and NOP counts are enforced by the frontier audit.

Frontier:578 tested candidates,1,373 hints,1,375 unresolved routes. Physical
clock calibration/interrupt timing, actual GPIO/frame/adapter composition,
shared typed registration and full source image/original byte identity remain
open. NOP-count equality is not physical timing proof.

### STACMD write retry and adapter composition

`native-stacmd-write-retry` compiles0x35698 with2,574 native/source comparisons.
Thirteen stable/changing log-mode sequences, success on attempts1..9, absent or
late success, full-width register/length values, high raw results and callback
counter mutation are covered. It preserves recovery before each frame, up to
nine attempts, short-circuit/repeated mode reads, both logging branches and the
counter increment after logging. Successful frames return their full raw word;
exhaustion returns0. Source descriptor sections at0x3570c/0x3573c match native
bytes exactly. Native code/literals are authenticated through Ghidra-MCP. REA
currently reports no procedure at0x35698; the locked ownership row and native
bytes remain the positive evidence, with that analysis limitation recorded.

`verify_native_stacmd_operations.py --real-retry` executes the actual retry body
inside the write adapter.1,580 comparisons pass with36 retry entries and132
frame calls per implementation. This graph disables logging; the direct retry
receipt tests all logging branches with descriptor identities. Original adapter
boundary comparisons are separately refreshed. Recovery/frame/logger endpoints
remain fixtures; this does not prove bus success or physical timing.

Frontier:579 tested candidates,1,373 hints,1,374 unresolved routes. Actual full
recovery/frame/logger/transport composition, shared typed registration/state,
canonical admission and original whole-image source/byte identity remain gates.

### STACMD read/write frames

`native-stacmd-frames` compiles0x28bb0/0x28c6c with15,360 comparisons:7,680 per
entry. Ghidra-MCP authenticates184/130 native bytes against locked ownership
rows. REA procedure_info reports no procedure at either entry in its current
analysis; positive evidence and that limitation remain explicitly separated.

Native header arithmetic wraps `(command&0xf0)+reg` to8 bits. Read/write require
command bit6, then preserve idle/header/direction/parity ordering. Length loops
compare signed32-bit index and length; high-bit lengths skip data but retain
handshake and successful release behavior. Read failure stores the partial byte
before cleanup. Read acknowledges intermediate bytes only when parity returns
exactly1. Write reloads a byte after the receive callback before checking parity.
Successful frames clean up and reload the configured release callback/pin/line;
failures clean up and return0. No convenience device/null-buffer fallback is added.

Tests cover wrapped headers, zero/small/high-bit lengths, every selected receive
failure boundary, header/data parity mismatch, full-width receive words and
buffer/configuration mutation at every fixture callback. Lower idle/bit/parity/
write-bits/release providers remain fixtures. Actual adapter/retry/transport
composition and shared typed registration/state ownership remain gates.
Frontier:581 tested candidates,1,373 hints,1,372 unresolved routes. Physical
wire timing/concurrency, source startup/full image and original byte identity
remain unproven.

### STACMD transmit primitives

`native-stacmd-transmit` compiles drive-bit0x5cbe4, write-bits0x5cc68,
idle0x5cccc and parity0x968a8.5,792 comparisons pass:560 drive,4,096 write-bits,
112 idle and1,024 parity. Write-bits executes the actual selected drive-bit body.
Both implementations execute4,225,728 NOPs over the suite. Drive preserves
high/output/high/low,13 four-NOP iterations for zero or52 for any nonzero bit,
then the final high callback/raw return. Idle uses the same transitions with one
long delay instead. Tests cover live callback/pin reloads and mutation boundaries.

Write-bits sends seven bits only when its second word equals1; other values send
eight, MSB first, returning the last drive result. Parity XORs only the low eight
input bits. All byte patterns, high-word parity inputs, header-selector bounds,
raw callback results and fixed-state sentinels are tested. Ghidra-MCP byte spans
and locked ownership rows authenticate the entries. The drive ownership body is
118 bytes across a126-byte span; source evidence preserves that distinction.

Scoped loop alignment preserves selected NOP counts, not original instruction
scheduling or cycle timing. GPIO callbacks and idle long-delay remain fixtures.
Receive-bit bodies, actual frame/adapter/retry/transport composition and shared
typed registration/configuration remain gates. Frontier:585 tested candidates,
1,373 hints,1,368 unresolved routes. Source startup/whole image/original byte
identity and physical timing/concurrency remain unproven.

### STACMD receive and actual adapter

`native-stacmd-receive` compiles0x87b30/0x969ec with1,152 comparisons:576 per
entry. The adapter executes the actual selected receive body. Each implementation
makes1,633,824 read callbacks and executes119,808 NOPs. Ghidra-MCP authenticates
110/16 native bytes against locked ownership rows.

Receive selects input, polls while values equal1 for at most1,000 reads, executes
26 four-NOP iterations, captures a full32-bit sample, then polls while values
equal0 for at most1,000 reads. Either timeout clears status, but sampling and
both phases still complete. It always writes the full32-bit `(~sample)&1`, even
on timeout. The adapter copies that word while preserving status. No device or
null-output fallback is introduced. Pin/read callbacks are reloaded at every
poll; tests mutate them through actual callback execution.

Tests cover24 falling/rising boundary pairs, including999/1,000 limits, samples
0/1/2/0xffffffff, non-Boolean transition values, preserved registers/SP and output
sentinels. GPIO/input/read providers remain fixtures. Actual frame/transmit/
adapter/retry/transport composition and shared typed registration/configuration
remain gates. Frontier:587 tested candidates,1,373 hints,1,366 unresolved routes.
Physical timing/concurrency and original whole-image source/byte identity remain
unproven; NOP counts do not establish delay calibration.

### Actual STACMD frame/wire provider graph

`verify_native_stacmd_wire_graph.py` links frame, transmit, receive and delay
objects with no interception of their nine provider bodies.480 comparisons pass
(240 read/240 write), covering96 successful and384 failure paths with controlled
GPIO waveforms, header parity faults, falling/rising timeouts, partial data
failures, invalid commands, high-bit lengths and callback-state mutation.
Only GPIO callbacks remain fixtures. Native/source provider-entry counts match:
240 per frame,2,960 drive,368 write-bits,800 idle,240 parity,672 receive,
368 receive-adapter and800 delay. Each executes1,132,224 NOPs and181,424 GPIO
callbacks, with matching traces, state and buffer outputs.

Composition exposed one executed compiler-alignment NOP in source frame loops.
The selected frame module now uses scoped`-falign-loops=1`, and its15,360 direct
comparisons pass again. The composed graph passes with matching NOP counts after
that change. This narrows compiler padding without claiming original scheduling
or cycle equality. No global compiler configuration changes.

The graph binds all four report/object hashes and its driver. Controlled GPIO
waveforms do not prove physical wire behavior. Typed production registration,
actual adapter/retry/transport and GPIO composition, canonical admission, source
startup/full image and original byte identity remain gates. Frontier counts
remain587 tested candidates,1,373 hints and1,366 unresolved routes.

### Actual STACMD adapters through wire providers

`verify_native_stacmd_adapter_wire_graph.py` links seven source modules and
executes13 provider bodies without interception: read/write adapters, write
retry, recovery, frames, transmit, receive and delay.192 comparisons pass
(96 read/96 write), including24 successes and168 failures. Tests cover null
requests, closed state, zero/small lengths, immediate success, first failure then
success, exhausted parity/timeouts and callback mutation of live configuration.
Native/source status counts match:0×24,11×96,27×24,29×24,30×12 and31×12.

All provider-entry counts match, including126 per frame,252 recovery calls,
24 write-retry entries,396 receive calls and1,764 delays. Each implementation
executes1,733,560 NOPs and124,040 GPIO callbacks with matching trace, state and
buffer outputs. Counter wraparound and nine-attempt exhaustion execute through
the actual bodies. GPIO callbacks and the disabled logger-mode endpoint remain
fixtures; enabled logger behavior is covered by the separate direct receipt.

Adapter/retry modules now also use scoped`-falign-loops=1` to remove observed
executed alignment padding. Their2,574 retry and1,580 adapter comparisons and
previous1,580 real-retry comparisons pass again. This does not establish cycle
or original instruction equality. Actual registry/transport/logger and GPIO
composition, shared typed production registration/state, canonical source startup
and whole-image original byte identity remain gates. Frontier counts remain
587 tested candidates,1,373 hints and1,366 unresolved routes.

### Shared STACMD registry ABI and source-owned configuration stage

`components/board/native_stacmd.h` now supplies one tagged108-byte configuration
and36-byte operations layout to registration and all seven recovered source
units. Static assertions enforce device offset48, operations offset72 and
open/close/read/write slots8/12/16/20. Open/close accept the registry device
argument while retaining native fixed-state behavior; request operations use the
actual four-word registry signature. Address-only operation declarations and
incompatible opaque configuration tags are removed. Raw GPIO tail-return
interpretation remains explicitly gated at the callback boundary.

`check_native_stacmd_stage.py` links the canonical board with those seven source
objects. Exactly one `r1_stacmd` definition comes from the canonical source-owned
registration. Four operation providers close; the failed-transaction counter
remains an external data gate. The standalone stage has57 unresolved symbols
versus60 in the unchanged canonical membership. This is a relocatable stage,
not canonical operation admission or an executable-stage runtime proof.

The canonical suite and delayed/notification/synchronization/queue/timer checks
are refreshed after the header change. Canonical testing compares the108-byte
configuration at0x200075c4 with pointer normalization and exercises registration.
Source storage/reset ownership of the preceding counter0x200075c0, actual
staged-runtime GPIO/transport composition, physical timing/concurrency and full
source startup/image/original byte identity remain gates. Frontier ownership
counts remain587 tested candidates,1,373 hints and1,366 unresolved routes.

### Source-owned STACMD failed-transaction counter

`native-stacmd-state` defines the four-byte counter as a zero-initialized C
object in its own aligned section. This follows positive native scatter-load
writes, not default emulator RAM: starting with0xa5/0x5a/0xff/0x3c throughout
RAM, each authenticated native run explicitly writes zero to0x200075c0..c3
from0x28726 before stopping at0x27208. The compiled source section contains
exactly those four bytes and preserves neighboring sentinels when installed.
Ghidra-MCP authenticates the scatter decoder/table slices; the whole input
application hash, source/object/driver and write observations are receipt-bound.

`check_native_stacmd_stage.py` now links exactly one counter definition alongside
the canonical configuration and recovered operations. The standalone stage has
56 unresolved symbols, with no new unresolved data; canonical membership remains
60 unresolved. This admits the counter's cold initial value only. Warm-reset
lifecycle, complete source startup/scatter behavior, executable-stage operation
validation/canonical admission, physical GPIO/transport behavior and original
whole-image instruction/byte identity remain gates. Frontier ownership counts
remain587 tested candidates,1,373 hints and1,366 unresolved routes.

### Executable wire path with compiled configuration and counter

`verify_native_stacmd_owned_state_graph.py` links the registration data and cold
counter objects with the recovered adapter/wire bodies. The executable installs
compiled counter(4 bytes), configuration(108 bytes) and name(14 bytes) sections
at native addresses. These match native scatter output after explicit function
pointer normalization. The initial counter comes from emitted C storage, not a
counter-address alias or synthesized configuration record.

192 comparisons pass, with all13 provider-entry counts, statuses, state, buffers,
1,733,560 NOPs and124,040 GPIO callbacks matching native execution. The cases
cover open/closed state, null requests, immediate success, recovery after an
initial failure, exhausted parity/timeouts and configuration mutation. Source
configuration function references are linked to GPIO test callbacks; native
GPIO references are intercepted at the same explicit boundary. Disabled logging
remains a fixture. Registration execution, actual registry/transport/logger/GPIO
composition and canonical admission are not claimed by this graph.

Counter warm-reset lifecycle, complete source startup, physical timing/concurrency
and original whole-image byte identity remain gates. The source stage remains
56 unresolved symbols, versus60 canonical. Frontier counts remain587 tested
candidates,1,373 hints and1,366 unresolved routes.

### Actual registry registration and dispatch through the wire path

`verify_native_stacmd_registry_graph.py` extends the source-owned-state graph
with the actual registrar, registry insertion/duplicate checks, pinned musl
strcmp and08/0c/10/14 dispatchers.192 comparisons pass through22 actual provider
bodies. Each case registers the source-owned record twice (success then duplicate
rejection), opens or closes through dispatch, and reaches read/write via the
compiled operations table. Matching registry heads and normalized configuration
are compared with the native path.

Native/source counts match:384 registrar and384 registry-register calls,
192 strcmp calls,96 calls per dispatch slot and96 per open/close body, in
addition to the previous wire-provider counts. Wire phase NOPs remain1,733,560
and GPIO callbacks124,040 per implementation. NOP accounting excludes setup;
registration instruction scheduling/cycle equality is not claimed. GPIO and
disabled logging remain explicit fixtures. Cold sections come from compiled
source and are checked against native scatter initialization.

This closes selected registration/registry/strcmp composition, not actual
canonical GPIO/logger or higher transport execution. Canonical admission,
warm-reset lifecycle, complete source startup/image, physical timing/concurrency
and original byte identity remain gates. Source stage remains56 unresolved,
canonical60; frontier587 tested candidates,1,373 hints,1,366 unresolved routes.

### Actual Nordic GPIO helpers with modeled peripheral registers

`verify_native_stacmd_gpio_graph.py` now links the pinned Nordic nRF5 SDK GPIO
wrapper object instead of GPIO function aliases.192 comparisons pass through27
actual provider bodies. Native/source traces and final peripheral registers,
configuration, counters, buffers and statuses match. Counts include2,908 low,
8,724 high,2,908 output,420 input and109,080 read calls per implementation,
with1,733,560 wire-phase NOPs. No GPIO helper is intercepted or given a synthetic
return; its compiled instructions execute the register accesses.

The hardware boundary is modeled IN values plus OUTSET/OUTCLR register behavior.
Ordered register reads/writes and final4-KiB peripheral state are compared. Pin
mutations stay within valid nRF52840 pins and preserve native callback reload
behavior. Source-owned configuration/counter/name, actual registration/registry,
musl strcmp and all recovered wire bodies remain in the graph. Logging stays
disabled through its explicit fixture. This establishes selected SDK HAL source
composition, not physical pin timing or bus/device success.

Actual logger/higher transport composition, canonical operation/state admission,
warm-reset lifecycle, complete source startup/image and original byte identity
remain gates. Stage remains56 unresolved versus60 canonical; frontier587 tested
candidates,1,373 hints and1,366 unresolved routes.

### Canonical STACMD source admission

The canonical board now includes operations, recovery, transmit, receive,
frames, delay, write retry and counter-state source objects exactly once.
Its unresolved symbols fall from60 to56 with no new unresolved dependency.
`check_native_stacmd_stage.py` detects canonical membership and links the board
alone, preserving one configuration and one counter definition rather than
including duplicate providers.

The canonical verifier places and compares the four-byte cold counter and both
retry descriptors at native addresses. Selected test text is68,376 bytes. The
full canonical scheduler/queue/context/startup/logger/task/registration suite
passes after admission; delayed-work, notification, synchronization and timer
stage/graph receipts are refreshed against the new board. The existing27-body
registry/wire/Nordic-GPIO waveform graph remains a separate runtime proof.

Admission establishes canonical source-provider membership, not complete firmware
startup or a flashable image. Enabled retry logging/higher YHM transport
composition, warm-reset lifecycle, physical timing/concurrency and original
compiler/layout/instruction/bundle byte identity remain gates. Ownership frontier
counts remain587 tested candidates,1,373 hints and1,366 unresolved routes.

### Source-owned YHM transport/request state and STACMD binding

`native-yhm-state` defines the20-byte transport context at0x2000687c and20-byte
shared request at0x20016b70 from explicit cold scatter writes. Four nonzero RAM
poisons pass: native writes20 zero bytes from0x28726 and five zero words from
0x3bc6c. Emitted source sections match all40 bytes and preserve neighboring
sentinels. Ghidra-MCP authenticates decoder/zero-writer/table slices; the whole
application hash and all source/object/driver evidence are receipt-bound.

Readiness now references the existing typed `r1_stacmd` object rather than the
invented callback-context alias. Its832 native/source frontend comparisons pass
after rebuilding against the shared header. Native configuration address/field
contracts are retained; no new device context or GPIO implementation is created.

`check_native_yhm_stage.py` links frontend, transport, handle initialization and
cold state with canonical providers, with single definitions of configuration,
transport context and request. It adds no unresolved dependency:56 canonical
symbols remain. This is a relocatable source stage, not executable YHM runtime
or canonical YHM admission. Runtime callback/handle lifecycle, warm-reset behavior,
full source startup/image, physical timing/concurrency and original byte identity
remain gates. Frontier remains587 tested candidates,1,373 hints,1,366 unresolved.

### Actual YHM handle/transaction/registry/wire/GPIO composition

`verify_native_yhm_transport_graph.py` links16 source objects, including the
source-owned YHM context/request, frontend, transport and handle initializer.
192 comparisons cover present/missing STACMD registry records, repeated handle
initialization, reads/writes, immediate success, recovery after an initial
failure, exhausted parity/timeouts, completion callbacks and GPIO-state mutation.
Cold sections are compiled C; registry, pinned musl strcmp, STACMD and pinned
Nordic GPIO providers all execute directly.

Native observes37 provider entrypoints. Source entry counts match except three
helpers(acquire/release/complete) that the compiler inlines into transaction
records; their public bodies remain separately verified by the direct receipt.
All lower dispatcher counts, full context/request memory, buffers, completion
calls and ordered/final peripheral state match. Each implementation executes
3,545,744 wire-phase NOPs and248,080 GPIO callbacks. Native/source counts include
384 handle initializations,1,440 lookups and768 strcmp calls.

The raw completion result is distinct from wire outcome:48 calls return0,
48 missing-device completions return1 and96 configured callbacks return
0x80000007. Release/completion status can be zero after exhausted wire retries;
this is native behavior, not a bus-success interpretation. Peripheral registers,
disabled logging and application completion callbacks remain explicit models.
The receipt labels zero/nonzero completion returns accordingly.

Additional production device bindings, callback/warm-reset lifecycle, enabled
logger and charger/status composition, canonical YHM admission, complete source
startup/image and original instruction/byte identity remain gates. Canonical
unresolved symbols remain56; frontier587 tested candidates,1,373 hints,
1,366 unresolved routes.

### Raw YHM status with explicit incoming-register contract

`native-yhm-status` compiles0x3529a without an uninitialized C read or a changed
public signature. Native instructions and fresh REA pseudocode/body ranges show
that the function saves incoming r3 as its read word, calls readiness, optionally
reads register6/length1 without checking transport return, then restores the
whole word to r3. The selected C source uses explicit ARM register moves at
capture/restore and a noinline boundary. Nibble14 maps to17; not-ready returns12.
No-write reads retain the incoming low byte, including high-word preservation.

55,296 comparisons pass:18,432 for the raw body and18,432 each through the actual
classifier and charger-state adapter. Tests cover all incoming low bytes, three
high-word patterns, zero/high readiness results, byte writes/no-writes, varied
ignored transport returns, deliberate provider clobbering of r3 and full final
r3/SP/callee-register preservation. Native/source lower-read counts both36,864.
REA and Ghidra-MCP authenticate96 body bytes over112 bytes, with16 jump-table
bytes excluded from the locked ownership size. The original row is unchanged.

The YHM source stage now also includes raw status and classifier/adapter bodies,
adding no unresolved dependency. This verifies the selected emitted compiler
contract; different prologue/toolchain/LTO behavior requires revalidation. Actual
lower readiness/transport composition, charger/updater policy, canonical YHM
admission, full startup/physical behavior and original byte identity remain gates.
Frontier:588 tested candidates,1,373 hints,1,365 unresolved routes.

### YHM system-track/charger initialization provider

`native-yhm-system-track` compiles0x355bc and its0x5079c battery-provider thunk.
80,184 native/source comparisons pass:40,092 per entry, covering every read byte,
no-write reads,13 stable/changing log-mode sequences, four raw write returns and
three incoming-register pattern pairs. Full r2/r3 restoration, SP and callee
registers are checked despite deliberate provider clobbering.

Native code zeroes the read word's low byte before register1/length1, computes
read_byte|2, preserves incoming r2/r3 high bytes in the two stack words, emits
both conditional logging paths, writes register1/length1 and forwards the raw
write return. No-write read therefore programs2. Explicit register moves and a
noinline boundary preserve the selected target ABI without undefined C input.
Compiled descriptor sections at0x35628/0x3565c match44/38 native bytes. Fresh REA
body metadata and Ghidra-MCP code/data authenticate both locked ownership rows.

The updater now declares uint32 return and explicitly discards it, matching the
native call site. Its2,896-case unit, real-statistics and real-control receipts
all pass again, including336 numeric/FPSCR cases each. The YHM source stage adds
these bodies with no new unresolved dependency. Actual transport/logger and
updater composition, alternate compiler/prologue/LTO behavior, canonical YHM/
battery admission, full startup/physical behavior and original byte identity
remain gates. Frontier:590 tested candidates,1,373 hints,1,363 unresolved routes.

### Raw charger status through actual providers

`native-yhm-stage/status-integration-verification.json` records144 native/source comparisons across raw status, classifier and adapter. Eighteen compiled provider objects execute through actual readiness, registry, transport, STACMD wire and pinned Nordic GPIO. Cases cover two incoming r3 seeds, readiness and bus absence, successful reads, exhausted parity/timeout reads and live pin/pull mutation. Full final r3, peripheral transactions/state and1,605,072 delay NOPs match;122,028 GPIO entries execute on each side. Compiler-dependent stack addresses are normalized only after independently checking the full pointed read word. Peripheral inputs, disabled logging and completion callback remain modeled. Canonical admission, updater integration, original instructions/bytes and hardware proof remain open. Frontier remains590 tested/1373 compiled hints/1363 unresolved routes; canonical board56 unresolved symbols.

Next filter0x91184 now has fresh REA body/pseudocode and Ghidra-MCP192-byte authenticated body/literal evidence in `native-battery-runtime/`; no implementation claim is made from pseudocode alone.

### Battery five-sample ADC filter compiled

`native-battery-filter/verification.json` authenticates native0x91184 (182-byte body) against REA and the Ghidra-MCP192-byte body/literal window. The C provider retains incoming r0's high half in the read word, clears low16 between reads, reloads the live ADC handle and delay mode, drops the two minima including duplicates, and preserves wrapping32-bit multiplication before final unsigned division/truncation. Selected compiler register capture remains an explicit gate for other toolchains/LTO.

7,104 native/source comparisons cover148 sample patterns, three incoming seeds, absent/partial/mixed-width writes and changing handle/mode values. They compare35,520 ADC reads,12,432 busy delays and23,088 RTOS delays on each side. `native-battery-runtime/filter-integration-verification.json` adds2,896 comparisons through actual updater/filter/statistics/control bodies, checking returned values, state and FPSCR. ADC registry/delay endpoints remain fixtures. The integrated graph uses halfword ADC writes and does not compare the unused high half of the scratch word across compiler-generated caller boundaries; direct filter verification checks that boundary independently. This is semantic evidence, not original instruction identity.

Strict ownership audit now reports591 tested candidates,1,373 compiled symbol hints and1,362 unresolved routes across3,326 ownership rows. Canonical board still has56 unresolved symbols. Runtime state ownership, actual Nordic ADC/delay composition, remaining battery policies/reporting, canonical admission, full startup, hardware proof and whole-image byte identity remain open.

### Discharge curve and source-owned calibration

`native-battery-discharge/verification.json` records262,687 native/source comparisons: all65,536 halfword inputs for each of four table selections (262,144), plus boundary/wide inputs with three out-of-range selector words. The configuration getter always executes, including below2400 mV, and remains a fixture. REA authenticates180 body bytes over a182-byte span (one padding NOP excluded); Ghidra-MCP authenticates the body/literals and480-byte calibration region. Four20-row structured C tables compile byte-identically to0x99d16..0x99ef5. The body clamps inputs, selects the first matching interval, accumulates byte weights and preserves signed integer interpolation/truncation. The locked tables cap at4310 mV, so the native4340 mV override and device-context read remain unreachable; the source retains that policy, and optimization removes its dependency. This is recorded explicitly, not claimed as exercised override coverage.

`native-battery-runtime/discharge-integration-verification.json` passes2,896 comparisons through actual updater, filter, statistics, control and discharge bodies, including1,783 discharge entries per side and all four FPSCR rounding modes. Compiled calibration data are installed in the source replay. Actual configuration, ADC/delay, remaining policy/reporting and source-owned battery state remain open. The strict frontier is592 tested candidates/1373 compiled hints/1361 unresolved routes, with56 canonical link symbols unresolved; canonical battery admission, original instruction/whole-image identity and hardware proof remain gated.

### Battery configuration getters and actual cached-class composition

`native-battery-configuration/verification.json` authenticates and tests native0x7bb44 (byte0),0x7bb5c (nonzero upper half) and0x7bb7c (signed upper half), with20/26/20-byte REA bodies and Ghidra-MCP byte windows. Each ignores the four-byte cached-read result, begins with incoming r3 as its word, and restores the full modified word to r3. No initialized default replaces failed/no-write behavior.196,752 direct comparisons cover all65,536 high-half values per getter plus partial/no/full writes and three seeds. Selected compiler/noinline/register-transfer behavior is verified; other compiler/LTO settings remain gated.

`kv-integration-verification.json` adds23,040 comparisons using the actual cached-class reader and compiled musl copy provider: matched and rejected sizes, payload mutation, live port reload and9,216 port callbacks per side. `native-battery-runtime/configuration-integration-verification.json` passes2,896 actual updater/configuration/KV/discharge/filter/statistics/control comparisons with4,679 cached reads per side (2,896 signed-offset and1,783 byte0 reads). This graph uses valid four-byte cached records and fixture port callbacks; rejected-size composition into callers remains an explicit gate because scratch-register words may differ across compiled callers. Handle/port initialization is not promoted to source ownership.

Strict frontier:595 tested candidates,1373 compiled hints,1358 unresolved routes across3326 rows. Canonical board remains56 unresolved symbols. Remaining cadence/recovery/reporting, source-owned battery state and persistent handle initialization, actual ADC/delay/transport composition, canonical admission, full startup, original instruction/whole-image equality and hardware proof remain open.

### Charging cadence compiled and updater argument contract repaired

`native-battery-cadence/verification.json` authenticates194 native body bytes using REA and a204-byte Ghidra-MCP body/literal window.6,616 native/source comparisons preserve initial-level early returns, timestamp-key reset, tick wrapping, zero-frequency behavior, the180-second increment cap, wrapping accumulator, config-selected12-byte threshold stride, zero-threshold stopping and the voltage/charge override. Provider-boundary state snapshots include live mutation. Native64-bit division helper executes1,992 times; source uses equivalent bounded32-bit unsigned hardware division. Tick/config providers remain fixtures.

The native updater call site loads voltage and charge-start timestamp before calling either discharge or cadence. Its source cadence declaration/call now takes both semantic arguments explicitly. All six preexisting updater verification modes were refreshed after rebuilding and pass2,896 comparisons each. `cadence-integration-verification.json` adds the actual cadence body to the compiled updater/configuration/KV/discharge/filter/statistics/control graph:2,896 comparisons,1,113 cadence entries,2,685 byte0 getters,2,896 signed-offset getters and5,581 cached-class reads per side. All FPSCR modes, return values and guarded state agree.

Four12-byte threshold rows at runtime context+44 are mutable RAM fixtures; their initialization/source ownership is not established by this replay. Stuck-charge recovery, remaining reporting/diagnostics, battery state/handle ownership, actual providers and canonical admission remain open. Frontier is596 tested candidates/1373 compiled hints/1357 unresolved routes; canonical board56 unresolved symbols. Full startup, physical timing/atomicity/concurrency and original instruction/whole-image byte identity remain gates.

### Stuck-charge recovery compiled, including saved log argument words

`native-battery-recovery/verification.json` authenticates272 body bytes and122 bytes of RING/Nordic descriptors using REA and a412-byte Ghidra-MCP body/data window.11,460 direct comparisons cover charge/level/state guards, first observation and changed-level handling,35mV voltage threshold,120-second unsigned64-bit timeout bounds, tick wrap, ignored/reset provider returns, raw initial-curve clamping and live state mutation across callbacks.13 mode sequences exercise short-circuit logging reads,756 RING and588 Nordic log calls per side. Both descriptor sections compile byte-identically to the authenticated data.

Native argument words saved for r1/r2/r3 are overwritten by stack logging arguments. Source explicitly captures/restores these words, including the different RING-only/Nordic-only/both-log return values; every comparison checks full r1/r2/r3, SP and callee preservation. The C void return does not acquire a fabricated raw-r0 contract. Other compiler/LTO settings require register-boundary revalidation.

`native-battery-runtime/recovery-integration-verification.json` passes2,896 comparisons through actual updater/recovery/cadence/configuration/KV/discharge/filter/statistics/control bodies. Recovery executes2,896 times, its reset/initial-curve path triggers312 times, and compiled progress reset executes2,316 times per side. The graph uses disabled logging and a fixture initial-charge curve; direct tests cover enabled logging. Mutable threshold/state/handle initialization, initial-charge curve0x4ff3c, diagnostics/escalation/reporting, actual hardware providers and canonical admission remain open. Frontier597 tested/1373 compiled hints/1356 unresolved routes; canonical board56 unresolved symbols. Full startup, physical timing/atomicity/concurrency and original instruction/whole-image identity are not established.

### Initial-charge curve and separate calibration compiled

`native-battery-initial-curve/verification.json` authenticates190 body bytes across a200-byte span (three REA ranges exclude8 literal bytes and2 padding bytes), plus480 calibration bytes at0x99ef6..0x9a0d5 through Ghidra-MCP. Structured C calibration compiles byte-identically.262,538 native/source comparisons include all65,536 halfword inputs for all four selections (262,144), four extra wide words per selection, and boundaries under three out-of-range selectors. Getter ordering, guarded state, SP/callee preservation and returned values agree.

The curve uses unsigned interpolation, a16-bit denominator and explicit zero-width handling. These differ from discharge's signed interpolation, so no shared replacement changes those contracts. The first table's final interval is exactly{4340,4310,5,0}; its upper clamp4310 causes first-match selection earlier in the table. The other tables clamp4350. This unusual authenticated data is preserved, not repaired. Zero-width handling remains in source but no locked row has zero width; it is not claimed as an exercised branch.

`initial-curve-integration-verification.json` passes2,896 comparisons through actual updater/initial-curve/recovery/cadence/configuration/KV/discharge/filter/statistics/control bodies.312 initial-curve estimates and5,613 cached-class reads execute per side. Both480-byte compiled calibration regions are installed and hash-checked. Diagnostic cadence, escalation/reporting, initialization and source-owned mutable thresholds/runtime/handles, enabled full-graph logging, actual hardware providers and canonical admission remain open. Frontier598 tested/1373 compiled hints/1355 unresolved routes; canonical board56 unresolved symbols. No full startup, hardware, original instruction or whole-image byte identity claim is made.

### Diagnostic cadence and six log descriptors compiled

`native-battery-diagnostic/verification.json` authenticates268 body bytes through REA, the440-byte native body/local-data window and two external charge descriptors through Ghidra-MCP. Six structured C descriptors (286 bytes) compile byte-identically.39,936 native/source comparisons cover all256 counter seeds,13 repeated/short-circuit mode sequences, three raw argument sets, callback mutation and counter aliasing device level. The native counter wraps before modulo5 testing and is reloaded after periodic logging before the >=30 diagnostics; source preserves that order. All six semantic arguments, live level/voltage/config values, raw signed-offset words and native headers agree. Nordic std1 retains the authenticated severity/module word0x1c0003.60,366 RING,18,978 Nordic std1 and22,800 Nordic std4 calls execute per side in direct replay. Void scratch returns are not promoted to output contracts.

`diagnostic-integration-verification.json` passes2,896 actual updater/diagnostic/initial-curve/recovery/cadence/configuration/KV/discharge/filter/statistics/control comparisons. The counter is seeded acrossall256values; all286 compiled descriptor bytes are installed and hash-checked. Full graph logging is disabled; enabled logging is directly replayed above, not promoted to full logger composition. Low-battery escalation0x3d88c and final reporting providers, source-owned mutable thresholds/runtime/handles, actual hardware providers, enabled full-graph logging and canonical admission remain open. Frontier599 tested/1373 compiled hints/1354 unresolved routes; canonical board56 unresolved symbols. Full startup, physical concurrency/timing/atomicity and original instruction/whole-image byte identity remain unproven.

### Low-voltage escalation compiled with packed-record and event-tail ABI

`native-battery-low/verification.json` authenticates176 body bytes and104 descriptor bytes using REA and a300-byte Ghidra-MCP body/data window.53,248 native/source comparisons cover all256 counter values,13 log-mode sequences, voltage reset boundaries, two incoming record seeds and callback mutation. The body resets at>=3350 mV, wraps byte increments, publishes event0x100c at the reloaded count9 and otherwise creates a timestamp/14-bit-voltage record and sets thread flag1 for counts>=10. Full r2/r3 restoration includes ring-log word0 replacement and mutations to the submitted record. The selected compiler emits the count9 path as an event tail call; raw event return and returned registers agree. There are25,584 record paths,104 event paths and26,624 reset paths per side. Other compiler/LTO settings require revalidation.

`low-integration-verification.json` passes2,896 actual updater/low/diagnostic/initial-curve/recovery/cadence/configuration/KV/discharge/filter/statistics/control comparisons, including920 record paths and5 event paths per side. Full eight-byte input records agree, including upper-halfword observation hashes. A fresh authenticated64-byte view of consumer0x73710 confirms that downstream code reads timestamp plus low16 packed bits; it remains a fixture, so this is not actual KV persistence proof. Source descriptor sections are compiled/installed/hash-checked. Voltage getter, time, KV-field setter, event and thread endpoints remain explicit fixtures; enabled logs are covered directly while full graph logging is disabled.

Frontier600 tested candidates/1373 compiled hints/1353 unresolved routes; canonical board56 unresolved symbols. Final reporting and downstream provider bodies, threshold/runtime/handle initialization, actual hardware/provider composition, persistence and canonical admission remain open. Physical timing/atomicity/concurrency, full startup and original instruction/whole-image byte identity are unproven.

### Device-info KV fields now use compiled cache operations

`native-kv-device-fields/verification.json` authenticates60 body bytes using REA and a64-byte Ghidra-MCP body/literal window.72,017 native/source comparisons cover every packed halfword, ten cached-read widths (including no write), three incoming frame patterns, nine input views including stack aliases, ignored raw statuses and read-driven handle/input replacement.72,016 read/write pairs and one null-input path pass. The C worker performs the native ordered timestamp and two bitfield updates, preserves the other cached bytes and reloads the record handle before writing.

Native allocates an uninitialized52-byte work record at incoming SP-64 and ignores cached-read failures. A small naked C/assembler ABI boundary supplies that exact raw external stack slice to the C worker; no initialized fallback record or uninitialized C automatic object replaces it. The frame is authenticated/tested for this target, with SP/callee preservation and alias-visible ordering. Other compiler/LTO settings and compiled-caller failed-size composition remain gates; this is C-compilable source with an explicit stack boundary, not original instruction identity.

`device-fields-integration-verification.json` passes2,896 actual updater/device-fields/low/diagnostic/initial-curve/recovery/cadence/configuration/KV/discharge/filter/statistics/control comparisons.920 setter calls execute actual52-byte cached reads and writes through the existing KV class and musl copy. Complete cached-node contents and handle slots are compared, alongside full low-battery event records. Valid-size cache updates are proven; port callbacks remain fixtures, and flash persistence is not established.

Frontier601 tested/1373 compiled hints/1352 unresolved routes; canonical board56 unresolved symbols. Device-info handle/port initialization, actual locking/persistence, rejected-size callers, remaining voltage/time/event/thread/reporting providers, mutable battery state ownership and canonical admission remain open. Full startup, physical interrupt/stack/concurrency behavior and original instruction/whole-image byte identity are unproven.

### Voltage getter and overlapping service entry compiled

`native-battery-voltage/verification.json` authenticates20 getter bytes and the four-byte service prefix with REA, plus24-byte getter/literal and412-byte service/updater windows with Ghidra-MCP.262,384 native/source comparisons comprise262,264 getter cases and120 service cases. Every16-bit initial voltage is checked with refresh off/on and configuration-provider mutation; extra full-word configuration values (including0xffffff55), raw refresh returns and edge values are tested. The getter compares exactly0x55 and reloads the halfword after optional service refresh.131,222 wide NOP prefixes execute per side in direct replay.

`voltage-integration-verification.json` starts all2,896 actual battery graph cases at native0x31fcc/source service, executes one four-byte NOP prefix per case, then runs the already compiled updater and existing policy/cache graph.920 actual voltage getters execute with advertising configuration fixture zero. Optional nested refresh is proven against a controlled updater in direct replay; recursive actual-updater refresh remains an explicit composition gate.

The ownership row0x31fcc spans412 bytes, overlapping the existing406-byte0x31fd0 updater row. REA observes only the four-byte prefix, with fallthrough established by execution; the remaining two span bytes are padding. The frontier maps the overlapping row to the actual service/updater graph, not to an inflated independent body claim. Both ownership rows remain bounded tested candidates, not additional unique coverage or instruction identity.

Frontier603 tested candidates/1373 compiled hints/1350 unresolved routes; canonical board56 unresolved symbols. Reporting and remaining time/event/thread providers, source-owned thresholds/runtime/handles/configuration, enabled logging and recursive refresh composition, actual hardware/locking/persistence and canonical admission remain open. Full startup, physical timing/concurrency and original instruction/whole-image identity remain unproven.

### Glasses battery frame compiled with return/register contract

`native-battery-frame/verification.json` authenticates62 body bytes with REA/Ghidra-MCP.66,536 direct comparisons cover all65,536 level/state byte pairs and extra full-word inputs, changed handles, the exact0xffff first-read sentinel, raw dispatch returns and provider mutation of the12-byte record. Source sends six bytes (00 09 8b 00 level state), reloads the handle before dispatch without rechecking the second value, and restores all three full record words to r1/r2/r3 on return. There are132,872 connection reads,66,336 sends and200 sentinel skips per side. The selected compiler contract is verified; other compiler/LTO settings require revalidation.

The updater declaration now accepts the wrapper's uint32 raw return and explicitly discards it. All13 previous unit/statistics/control/provider graph modes were rebuilt/refreshed and pass2,896 comparisons each. `frame-integration-verification.json` adds the actual frame body to the service/updater/policy/cache graph:2,896 comparisons,2,823 frame entries,4,696 connection reads,1,873 sends and950 skips per side. Connection lookup and type0 queue dispatch are fixtures; queue acceptance and physical BLE delivery are not established.

Frontier604 tested candidates/1373 compiled hints/1349 unresolved routes; canonical board56 unresolved symbols. Protocol battery sender0x8345c, connection getter/type0 dispatch/lower queue composition, remaining time/event/thread providers, initialization, enabled full-graph logs and recursive refresh, hardware/locking/persistence and canonical admission remain open. Full startup, physical delivery/concurrency and original instruction/whole-image byte identity remain unproven.

### Battery frames compose actual connection and shared TX producer source

`frame-tx-integration-verification.json` replaces the connection getter and type0 dispatch fixtures with existing authenticated `connection-handle` and `native-tx` objects, reusing compiled musl copy.2,896 native/source comparisons execute1,873 shared-producer calls. Outcomes per side:373 missing-queue rejections,374 invalid-connection rejections,161 failed allocations,241 accepted queue puts and724 failed puts with envelope cleanup. There are1,126 allocation attempts and965 puts; full heap envelopes/payloads, queue/thread reloads and ownership transfer/free effects agree at fixture boundaries.6,196 actual connection-getter entries execute, including modeled connection changes between the frame's two reads and producer validation. Allocator/CMSIS queue/notification APIs remain fixtures, so queue acceptance is modeled and physical BLE delivery is unproven.

Two16-byte TX contexts and three2-byte connection fields compile byte-identically to native startup after all SRAM is poisoned0xA5. Runtime queue/thread slots and transitions remain controlled fixtures, not proof of actual thread creation or full startup. The frame's dispatcher declaration now matches the existing int32 provider, explicitly preserving the raw uint32 return bits;66,536 direct frame and2,896 previous frame-graph comparisons were refreshed and pass.

Fresh REA observations bind the12-byte0x34064 veneer and shared0x3e274..0x3e48b producer (536 bytes). REA represents the latter inside the0x34070 function, whose complete body is548 bytes including another12-byte veneer; fresh Ghidra-MCP slices authenticate each selected native range. `frame-tx-attribution.json` explains the manual inventory name `r1_output_dispatch` at0x3e274 and its actual compiled private candidate `dispatch` in `native_tx.c`. The locked ownership ledger is unchanged; no alias to the separate output worker is introduced. This previously unresolved route is now bounded tested-source evidence, not new unique code or instruction-identity proof.

Frontier605 tested/1373 compiled hints/1348 unresolved routes; canonical board56 unresolved symbols. Actual allocator/RTOS queue/notification and worker/BLE composition, protocol battery sender, remaining time/event/report providers, initialization, enabled logging/recursive refresh and canonical battery admission remain open. Full startup, hardware and original instruction/whole-image identity are unproven.

### Protocol battery-status sender compiled

`native-battery-protocol/verification.json` authenticates108 body bytes through REA and body/descriptor windows through Ghidra-MCP.126 descriptor bytes compile byte-identically.160,992 native/source comparisons cover all percentage bytes plus wide values, six full-word state inputs,13 repeated/short-circuit mode sequences, four raw dispatch returns and packet mutation. The eight-byte packet contains the percentage low byte and charge1 for any nonzero state/2 for zero, with other bytes zero. Loggers receive the full percentage word, not its narrowed packet byte. RING logging replaces the saved r1 word with encoded charge; otherwise r1 retains original state, while r2/r3 restore the two packet words, including provider mutation.111,456 RING and86,688 Nordic log calls execute per side; raw operation1 return bits are forwarded. Other compiler/LTO settings require register-boundary revalidation.

The updater declaration now reflects the uint32 result and explicitly discards it. All14 prior runtime modes were refreshed and pass2,896 comparisons each, including the frame/TX graph (its attribution receipt hash refreshed without changing ownership metadata). `protocol-integration-verification.json` passes2,896 cases through the actual protocol sender and existing service/updater/frame/TX/policy/cache graph, with1,071 operation1 calls. Enabled logs are directly tested; full graph uses disabled logging and an operation1 transport fixture. Packet source sections are installed and hash-checked.

Frontier606 tested/1373 compiled hints/1347 unresolved routes; canonical board56 unresolved symbols. Phone operation1 transport0x83896 and lower protocol/BLE providers, actual allocator/queue/notification/time/event composition, initialization and source-owned mutable battery state, enabled logs/recursive refresh and canonical admission remain open. Full startup, locking/persistence, physical delivery/concurrency and original instruction/whole-image byte identity remain unproven.

### Phone operation1 and response-header wrappers compiled

`native-phone-operation/verification.json` authenticates36-byte0x83896 and82-byte0x84c0c bodies using fresh REA/Ghidra-MCP evidence.98,176 direct native/source comparisons execute both C wrappers and the existing compiled phone connection getter:3,840 operation-wrapper and94,336 direct header-wrapper cases. Every16-bit opcode is covered, plus raw full-word flags/status/handles, null and mapped payloads, full-word lengths, lower return values and header/payload mutation.90,976 lower sends and1,920 null-input wrapper returns are exercised. Incoming stack argument slots remain unchanged in direct common-wrapper replay.

Operation1 rejects null input with0, otherwise reloads the phone handle and calls the common wrapper with opcode1, both caller words, payload pointer and literal7. The saved words restored to r2/r3 are the original second/incoming-r3 words on null input, otherwise the payload pointer and7. The common wrapper rejects exactly0xffff, constructs its eight-byte base0x100/opcode/flag/low16 header and maps lower result0 to1, all other results to0. Its two header words restore to r2/r3, including callback mutation; invalid-handle returns restore the incoming first/second words. This selected compiler boundary is verified; other compiler/LTO settings and wrapper-stack-overlapping payloads remain gated.

`phone-operation-integration-verification.json` passes2,896 cases through actual battery/report/frame/TX/cache policies and both wrappers/getter.1,071 operation/header/phone-getter calls yield261 invalid-handle rejections and810 lower response calls (207 raw-zero and603 raw-nonzero results). The lower0x828b4 sender remains a fixture. Full graph logging is disabled; earlier direct protocol/logger contracts remain independently verified.

Frontier608 tested/1373 compiled hints/1345 unresolved routes; canonical board56 unresolved symbols. Lower response allocation/serialization/BLE composition, actual heap/queue/notification/time/event providers, source-owned mutable battery state and handle/config initialization, enabled logging/recursive refresh and canonical admission remain open. Full startup, locking/persistence, physical delivery/concurrency and original instruction/whole-image byte identity remain unproven.

### Lower response sender compiled with allocation wrap and cleanup semantics

`native-protocol-response/verification.json` authenticates364 body bytes using REA and a672-byte Ghidra-MCP body/data window. Six descriptors (290 bytes) compile byte-identically.100,480 direct comparisons cover all65,536 halfword lengths plus wide/wrapped lengths, null headers, short-circuit connection gates, allocation failures, raw encoder returns, send success/failure,13 logging-mode sequences and callback-driven header/packet mutation. Allocation uses(uint16_t)(length+12) while encoder receives the full original32-bit length. Native REV16 logging is modeled as a16-bit byte swap rather than the wider expression suggested by pseudocode. Unaligned encoded packet fields reload after logging callbacks.

The function returns2 for null header,5 for closed gates,3 for allocation failure, raw nonzero encoder status after freeing,4 for send failure after logging/freeing, and0 after successful send/free. Direct replay includes72,088 allocations with encoder entry and cleanup,3,276 send-hook calls and all status paths. Fixtures keep mapped storage accessible even for wrapped requests; these comparisons do not establish actual encoder allocation bounds or physical memory safety.

`response-integration-verification.json` passes2,896 actual battery/policy/report/wrapper/cache/TX comparisons, including810 response-sender entries. Connection gates permit716 allocation attempts;645 succeed and all645 reach free. Encoding reaches308 send-hook calls:103 raw-zero results and205 failures. Encoder rejects337 cases with raw7/0xffffffff; closed gates reject94 and allocation fails71. Gates, allocation, encoder and send hook remain fixtures; enabled logs are directly tested while full graph logging is disabled. Source descriptors are installed and hash-checked.

Frontier609 tested/1373 compiled hints/1344 unresolved routes; canonical board56 unresolved symbols. Actual encoder/send-hook/gates/heap, wrapped-length bounds, RTOS queue/notification/time/event composition, initialization, enabled logs/recursive refresh and canonical admission remain open. Full startup, physical delivery/concurrency/locking/persistence and original instruction/whole-image identity are unproven.


### Protocol encoder and source-owned cold state

The136-byte native encoder0x82f9c is authenticated with REA and Ghidra-MCP and implemented in C.6,600 direct comparisons execute pinned musl1.2.5 memmove and recovered Modbus CRC, preserving capacity underflow, full32-bit movement lengths,16-bit CRC lengths, sequence wrap and alias-sensitive store order. Six compiled sequence/version-map bytes match native cold startup under four SRAM poisons.

The complete battery encoder graph passes2,896 cases with645 actual encoder/memmove/CRC calls per side;810 responses include645 allocations/frees. Frontier610 tested/1373 compiled hints/1343 unresolved routes. Actual hook/gates/heap, source state ownership/canonical admission, physical bounds/delivery/concurrency and exact whole-image identity remain gated.


### Send-hook dispatcher and connection presence gates

REA/Ghidra-MCP authenticate the14-byte dispatcher0x827f8 and two20-byte predicates0x4cbb0/0x4cb40. The dispatcher compiles with8,232 direct comparisons covering tail stack/LR, callback register forwarding, mutation and raw results. Four compiled callback-slot bytes match native cold zero initialization across four SRAM poisons. Both predicates reuse existing connection fields and pass131,072 exhaustive halfword comparisons, including full returned r0/r1/r2/r3. The historically named authenticated predicate only tests handle !=0xffff.

Two additional2,896-case graphs compose actual dispatcher and then actual predicates with the encoder/CRC/musl/battery path. The final graph executes810 phone and272 peer presence checks plus645 actual hook/encoder/movement/CRC calls per side. Callback target/live transitions and heap/queue endpoints remain modeled. Frontier613 tested/1373 compiled hints/1340 unresolved routes. Registration0x83448 (native BL target; REA has no entry, boundary attribution pending) and its registered native target0x32408 are next; canonical admission, full startup, physical delivery/concurrency and original-image identity remain gated.


### Send callback registrar preserves failed-registration state

The16-byte native registrar0x83448 now compiles as C.65,544 direct comparisons preserve fullr0/r1/r2/r3, arbitrary nonzero callback words and two null-rejection cases retaining previous registration. REA has no procedure entry here; the locked ownership row, independently decoded nativeBL at0x830b4 and Ghidra-MCP body/call-site bytes are the explicit attribution evidence. The ledger and REA metadata remain unchanged.

The2,896-case integrated graph executes5,792 registrations per side (valid then null), retaining the installed callback for645 actual hook/encoder/CRC/musl sends. Callback targets and live connection transitions remain modeled; full product initialization is not proven. Frontier614 tested/1373 compiled hints/1339 unresolved routes. Next target0x32408 fragments through a second callback slot0x20006960 and can reuse the compiledCRC32 update and musl movement providers. Actual heap/RTOS composition, source-state/canonical admission, physical behavior and exact whole-image identity remain gated.


### Fragmenter reuses actual CRC32, musl movement and type1 TX

The0x32408 fragmenter compiles with106 exact descriptor bytes.4,957 direct comparisons cover every length0..4097,13 logging sequences, additional mapped8192-byte failures, null/empty input, raw ignored callbackstatuses and live callback/input mutations. Actual recovered non-reflected CastagnoliCRC32 and pinned muslmemmove execute. Native CRC runs before the4096 limit check; exact239-byte multiples emit an extra empty fragment. The locked272-byte body spans274 bytes with an excluded2-byteNOP at0x32486. Native registration pointer/Ghidra-MCP bytes establish attribution while REA entry absence stays explicit. Volatile returnr1/r2/r3, compiler-private stack aliases and full-width CRC fault behavior remain gates.

Four poisoned cold starts resolve callbackslot0x20006960 to existing type1TX veneer0x3407c. Four bytes are now source-owned through a symbolic C relocation to the existing provider. Native-target linking matches those bytes; actual source-target relocation executes in the2,896-case fragment/TX graph. This graph executes645 fragmenter/type1 calls and2,573 sharedproducer dispatches per side, including336 modeled queue acceptances. Native/source memory and traces match. Separate fragment-only graph also passes2,896 cases. Allocator, queue and notifications remain modeled endpoints; live connection transitions are fixtures. Frontier615 tested/1373 compiled hints/1338 unresolved routes. Full startup, batteryroot ownership/canonical admission, physical delivery/concurrency and original instruction/whole-image identity remain unproven.


### Protocol port initialization and receive registration

Initializer0x830a8 and receivecallbackregistrar0x832d4 now compile with320 exact descriptor bytes.66,472 direct comparisons cover66,160 receive registrations and312 initializers, every callback halfword,13 logging-mode sequences, live callback mutation and ordered stores. Initializer clears both callbackslots before actualsend/receive registration. Nullreceive registration returns failure without clearing previous state. Raw initializer r0 is preserved, including the final mode leftshift or SDK tailreturn; pseudocode void return is not treated as a full ABI contract. Four receive-slot bytes match compiled zero initialization across four SRAM poisons.

The2,896-case graph executes actual portinit/send/receive registration before the full battery/encoder/fragment/type1/sharedproducer path, including645 fragment/type1calls per side. Ingress0x8316c is an unexecuted symbolic address binding; neither full ingress nor productstartup is proven. Lockedownership/nativecalls/Ghidra-MCP authenticate bodies while REAentryabsence remains explicit. Frontier617 tested/1373 compiled hints/1336 unresolved routes. Volatile r1/r2/r3, actual enabledlogs/heap/RTOS, sourcebatteryroots/canonical admission, fullstartup, physical concurrency/delivery and original instruction/whole-image identity remain gated.


### Receive callback dispatcher

The130-byte0x826b4 dispatcher compiles with172 exact descriptor bytes.16,848 direct comparisons cover4,680 tailcallback calls,9,828 invalidbuffer/length paths and2,340 missingcallback paths across13 logging sequences. Valid paths preserve fullhandle/buffer/length, callbackpointerr3, callback returnr0/r1/r2/r3 and tailSP/LR. Invalid/logging rawr0 follows the finalmodeshift or SDKtailreturn. Callback mutation during a missingcallback log does not trigger a recheck. These are boundary checks, not packetheader/CRC validation.

The2,896-case initialized receive/battery graph executes1,804 ingressfixture calls,911invalid and181missing paths per side, followed by actual encoder/fragmenter/type1/sharedproducer composition. Registered ingress remains an explicit callback fixture. Frontier618 tested/1373 compiled hints/1335 unresolved routes. Fresh ingress evidence authenticates a176-byte lockedbody and four poisoned native cold module tables: null,system0x83ca9,health0x82be9,null. Those observations do not compile the ingress/module handlers. REA entry gaps remain explicit alongside lockedledger/Ghidra-MCP attribution. Real logger/heap/RTOS, volatile invalid/logging scratchABI, sourcebatteryroots/canonical/fullstartup, hardware delivery/concurrency and whole-image identity remain gated.


### Registered ingress with saved-frame and module-table ownership

The176-byte locked0x8316c ingress now compiles as a Cworker with an explicit native32-byte saved-argument/tail boundary.72,220 direct comparisons check every16-bit length, fullr0/r1/r2/r3, exactsavedframe, nativecallbackSP/LR,13loggingmode sequences and6liveheader/tablemutation modes.936 cases preserve logger-mode scratchregisters; the source explicitly restores native incomingr2/r3 before querying modes. Headeraliases into the native savedframe are exercised. The module is reloaded after logs, including mapped module200 mutation; no newvalidation is inserted.

110 descriptorbytes compile exactly. The16-byte module table is source-owned through symbolic system/health relocations; native-target linking matches fourpoisoncoldstartup bytes. Actualsource symbolic relocations execute with handlerfixtures in the2,896-case initializedingress/receive/battery graph:1,804 ingressentries and151system/151health/226specialhandlercalls per side. REAentryabsence stays explicit; lockedmanualownership/nativecallback/Ghidra-MCP provide attribution. Frontier619 tested/1373 compiled hints/1334 unresolved routes. This dispatcher is not CRC/advertised-length/authentication validation. Actualmodulehandlers/enabledlogger, loggerwrites into outgoingstackarguments, othercompiler/LTO, physicalbounds/concurrency, heap/RTOS, sourcebatteryroots/canonical/fullstartup and exactinstruction/whole-image identity remain gated.


### Module dispatch wrappers and shared command lookup

Three36-byte modulewrappers0x82be8/0x83ca8/0x84c98 and the58-byte sharedlookup0x83298 now compile.196,818 native/source helpercomparisons cover every16-bit command per each original table and full-word inputs:196,560 return and258 produce matching emulated readfaults/addresses.4,104 actual-wrapper/search comparisons include1,890 leafcallback calls and comparefullr0/r1/r2/r3 plus tailSP/LR. Native literal table-binding reads are normalized; actuallookup datareads match.

Unsigned upperindex underflow is preserved: a below-minimum key can wrap the index, read a mapped preceding record and return its pointer, or fault with the original table backing. The controlled predecessor case returns0x12345679 with upper0xffffffff/index0x7fffffff/lower0. This is nativebehavior evidence, not physical exception proof or a bounds remediation.

280 commandtablebytes are source-owned symbolic references to35 leafhandlers; native-target linking matches original data. Nine exacttargets lack lockedownership entries and remain in command-targets.json as attributiongaps; the ledger is unchanged. The2,896-case initialized graph executes allmodulewrappers/sharedlookup/ingress/receive and existingbatterytransport, with528lookups andall35 leaf fixtures exercised. REAentryabsence is retained alongside lockedledger/nativecalls/Ghidra-MCP attribution. Frontier623 tested/1373 compiled hints/1330 unresolved routes. Leafsource, faultsemantics onhardware, actuallogger/heap/RTOS, sourcebatteryroots/canonical/fullstartup and exactinstruction/whole-image identity remain gated.


### Special event leaf and activity-refresh record

Registered specialtarget0x84cc0 is a24-byte eventforwarding body, now compiled with supplemental attribution from its Thumb registration at0x9a588, exact Ghidra-MCP bytes and native branch/return execution. It has no locked ownership row; the original ledger is unchanged and the frontier summary lists it separately. Activityrefresh0x82c10 (52bytes) also compiles through a native16-byte saved-frame boundary and Cworker. Its8-byte event record retains the incomingr3 word; no zero padding is invented. A directalias failure exposed private Cstack overwriting a sequence before read; the boundary now conditionally snapshots required header values and the Cworker models overlap with native record stores.

154,378 native/source directcomparisons pass:65,633 special and88,745 activity cases, including all16-bit speciallengths/activitysequences, allflagbytes, fullr0/r1/r2/r3, callback mutations, stackheaderaliases, wrappedpayloadpointerzero and matching nullheader readfaults. They execute65,571 special and71,336 activity eventboundarycalls per side. Private Cstack bytes outside the native16-byte savedframe are not compared, including headeraliases there; actual provider access beyond the passed record remains gated.

The2,896-case initialized graph executes226special/10activity bodies and181special/3activity eventpublications per side, while keeping33 other leafbodies as fixtures. Eventpublisher remains an explicit boundary fixture; its existing source and downstream uninitialized leadingrecord/queueownership need composition. Lockedfrontier624 tested/1373compiled hints/1329 unresolved routes, plus the supplemental24-byte testedtarget. Eight other exacttargetattributiongaps remain. Sourcecompilation/contract evidence is not canonical/fullstartup, physicalfault/delivery/concurrency, othercompiler/LTO or instruction/whole-image identity proof.


### Device-status response and charge predicates

REA authenticates contiguous66/18/14-byte bodies at0x83de4/0x91244/0x91256; Ghidra-MCP bytes match the locked artifact. Allthree now compile as C with an explicit24-byte native statusframe boundary. Eight defaultrecordbytes at0x9a4c4 compile exactly. The shared existing charge-bytegetter executes; the source does not duplicate its configuration/refresh policy. Status latches the byte first, then performs separate active/full chargerobservations, giving fullstate priority. Headersequence reload follows those calls and recordstores.

381,191 native/source directcomparisons pass:250,109 status cases and65,541 per predicate. They include all16-bit predicateinputs/statussequences, every chargebyte, full-word config85/0x10055 comparison, live distinct chargerobservations, header/state/recordmutation, stackheaderaliases, fullr0/r1/r2/r3/nativeframe and matching nullheaderfault.61,440 optionalupdatercalls are modeled; actual recursive refresh remains gated.

The2,896-case initialized receive/module/battery graph now executes9 actualstatus/getter/predicate/operation requests,5 real statusencodes and650 totalencoder/CRC/fragment/type1 calls per side. Four statusrequests stop at the modeled connectionstate; actualTX has337 modeled queueacceptances overall. The reused getter is retained from its source-compiled object with a relocatable section-GC link, preserving source/report/object provenance. Advertisingconfig is zero in this composition; rawcharger, heap/RTOS and liveconnection endpoints remain fixtures. Frontier627 tested/1373 compiled hints/1326 unresolved routes, with supplemental specialtarget retained separately. Extra privateCstack/othercompiler/LTO/providerABI, sourcebatteryroots/canonical/fullstartup, physicalfault/power/delivery/concurrency and original instruction/whole-image identity remain gated.


### Device information and operation-2 response

The54-byte native device-info body0x83d5c and36-byte operation2wrapper0x83872 now compile. The manual device-info ownership row has no extent; native calls/return boundary and exact Ghidra-MCP body supply the54-byte extent while REA entry absence is explicit. REA authenticates the operation2wrapper and48-byte snprintf wrapper.25 stock metadata bytes (firmware2.2.6.0009, hardware603MV1.9.3 and%s) compile exactly; they are not an OpenCFW release identity.

133,597 direct comparisons cover67,197 info calls and66,400 wrapper calls, all16-bit sequences, four formatting boundarymodes, lateheader reads, nullfault and native40-byte record. Real EABI/musl clearing and shared connection/header code execute. Returnr0, r2/r3 and payload/call behavior agree. Caller-savedr1 differs in133,560 cases with the actual sourceheader; this is recorded as an unresolved register-identity gate, not promoted to full ABI equivalence. Private Cstack outside the nativebuffer and othercompiler/LTO remain gated.

The2,896-case initialized graph executes9inforequests/18formatcalls,5infoencodes,655totalencoder/CRC/fragment calls and2,905actualmemoryclears per side. Modeled pre-clear concurrent D-byte mutation retains the earlier battery scenarios. Existing allocator/RTOS/liveconnection endpoints remain fixtures. Generic snprintf0x38080 is still a named formatter fixture; fixed%s caller checks do not close it. Localtoolchain headers/readme identify Newlib3.3.0 as a sourcecandidate; official source access and localhash provenance are in formatter-next-target.json, with source revision/license/build/native-identity gates open. Frontier629 tested/1373 compiled hints/1324 unresolved routes plus the supplemental specialtarget. Canonical/fullstartup/hardware/delivery/concurrency and original instruction/whole-image identity remain unproven.

Newlib formatter closure candidate: `newlib-stdio/report.json` records 29 newly
compiled C units plus six reused source-provider objects. Only assertion,
malloc lock/unlock and heap growth remain unresolved in the isolated link.
`double-comparisons-verification.json` records 35,072 EABI adapter checks against
binary64 ordering. These are semantic checks, not native identity evidence.

`formatter-experiment.json` compares the actual native formatter with the
candidate for 225 cases: 139 match and 86 differ, with zero execution errors.
Counterexamples include pointer spelling, unsupported native hexadecimal-float
formatting, subnormals and exceptional/extreme floating values. Heap growth and
locks are explicitly modeled Unicorn boundaries; source allocator, locale,
formatting and arithmetic bodies actually execute. Native SRAM reads outside
arguments, output and the stack were empty for this corpus. No function is
newly admitted: generic equivalence, native ABI and byte identity remain gated.
The mismatches require native formatter reconstruction rather than promotion of
an upstream-compatible substitute. Retain all counterexamples when changing
providers. See `third-party/upstream/newlib-stdio-3.3.0/` for provenance/licenses.

Native formatter output checkpoint: `native-formatter-output/report.json`
compiles recovered left-padding (0x43734), width-padding (0x43758) and bounded
output (0x43bbc). Direct verification passes 145,407 cases, including exhaustive
low16 flag patterns, every byte value, context aliases and 1,036 matching
faults. Ten enormous padding cases compare only the first16 callback events.
The native formatter graph executes these C helpers for all225 prior format
cases with225 matches: width190, left190 and bounded output1880 calls. The core
parser/numeric conversion and snprintf wrapper remain native in this graph.
Caller-saved scratch/private frame identity remains gated. The strict audited
frontier is632 tested candidates,1373 compiled hints and1321 unresolved routes
across the unchanged3326-row ledger; no instruction-identity claim follows.

Native decimal conversion checkpoint: `native-formatter-decimal/report.json`
compiles the recovered 366-byte native control-flow contract at 0x3f530 and
owns its four-byte zero literal. Direct verification passes 4,818 cases,
including all nonnegative binary64 exponents, six precision/mode combinations,
28 zero cases and 260 result-buffer aliases. Arithmetic argument traces match
while actual native multiply/divide/add/to-unsigned bodies execute; integer
division uses the existing source provider. The 225-case formatter graph also
matches with 120 actual C decimal calls and the three C output helpers.

Four native binary64 bodies remain explicit gates, with REA attribution in
`native-formatter-decimal/arithmetic-next-targets.json`. The main parser and
snprintf wrapper remain native in this experiment. The strict frontier is now
633 tested candidates, 1,373 compiled hints and 1,320 unresolved routes across
3,326 unchanged locked rows. These bounded contracts do not prove complete ABI,
source ownership, instruction identity or a source-built firmware image.

Native unsigned binary64 conversion checkpoint: the C provider at 0x28334 is
compiled in `native-formatter-unsigned/`. Direct verification passes 81,920
bit-pattern cases covering every exponent, both signs, selected fractions and
16,384 seeded random words. Native sign-discarding and oversized register-shift
behavior is preserved using actual recovered C shift providers. The old locked
standard-helper role label does not establish standard saturation semantics;
the ledger remains unchanged and the direct native evidence controls this body.

The 4,818-case decimal chain also passes with this C conversion; all native
math argument traces match. The formatter graph matches all 225 cases with
100 actual C unsigned conversions, 120 C decimal calls and three C output
helpers. Only multiply, divide and add remain native arithmetic boundaries in
these graphs; parser and snprintf wrapper source remain required. The audited
frontier is 634 tested candidates, 1,373 compiled hints and 1,319 unresolved
routes across 3,326 locked rows. Full register/flag, instruction and image
identity remain explicit gates.

Native binary64 addition checkpoint: `native-formatter-add/report.json`
compiles four bodies (544 native bytes): addition at 0x27afc, signed shift at
0x27fd0, remainder rounding at 0x28122 and normalization/packing at 0x28140.
Direct verification passes 52,778 cases. Actual C logical shift providers
execute; no floating arithmetic provider is needed by these four C bodies.

The decimal chain passes all 4,818 cases with C addition, normalization,
rounding, signed/logical shifts and unsigned conversion. The formatter graph
passes all 225 cases, with 100 C additions and 1,055 normalization/80 rounding
calls redirected from remaining native arithmetic. Only multiply/divide remain
native arithmetic providers in these graphs; parser and snprintf wrapper are
still native. Pinned LLVM addition differs in 183 of 2,624 comparison cases,
including NaN and subnormal behavior. Preserve these upstream counterexamples.

Strict frontier: 638 tested candidates, 1,373 compiled hints and 1,315 unresolved
routes across 3,326 locked rows. Caller-saved/flag/private frame and instruction
identity, full source image integration and hardware remain gated.

Native multiplication/division checkpoint: `native-formatter-product/` compiles
both remaining native decimal binary64 arithmetic bodies (450 native bytes).
All 263,712 direct cases pass: 131,856 per body, covering every exponent, both
signs, selected mantissas and seeded random pairs. Packing, rounding and integer
shifts execute the recovered source providers.

The 4,818-case decimal chain now executes C source for every arithmetic helper,
with unchanged native argument traces and outputs. The 225-case formatter graph
also matches using the actual combined `native-formatter-math.o`: 1,055 C
multiplications and 80 C divisions. Its build report validates five provider
reports and requires zero unresolved symbols. This closes only the decimal
arithmetic dependency bundle, not the formatter or image. The parser and
snprintf wrapper, complete register/flag/frame ABI and instruction identity
remain gated. Strict frontier: 640 tested candidates, 1,373 compiled hints and
1,313 unresolved routes across 3,326 unchanged locked rows.

Native formatter core checkpoint: the full 1,656-byte noncontiguous native
parser/emission contract at 0x43080 now compiles in C, with 56 bytes of owned
flags/digit/sign literals. All 39,002 direct parser cases pass (303,233 callback
observations and 10 matching faults), covering flag subsets, nine length forms,
negative dynamic precision, aligned 64-bit arguments, `%n`, unsigned byte
callbacks and four mutation modes. The initial high-byte callback translation
error is preserved in `native-formatter-core/byte-callback-counterexample.json`.

`native-formatter-engine/` links the parser, arithmetic and output providers
with no undefined symbols. All 225 existing wrapper-based cases execute this
actual engine and match. Native variadic wrappers and exact136-byte frame /
caller-saved / flag identity remain gated; no full input-domain, instruction or
whole-image identity follows. Strict frontier: 641 tested candidates, 1,373
compiled hints and 1,312 unresolved routes across 3,326 locked rows.

Bounded wrapper checkpoint: `native-formatter-wrappers/` compiles public
snprintf at 0x38080 and vsnprintf at 0x380dc with source C formatting/termination and
native-frame ABI adapters. Direct tests pass 2,532 cases, with 1,096 matching
faults and 36 frame aliases. Native outer 40/24-byte frames and r0/r2/r3 agree;
r1 differs in 24 zero-capacity cases and remains an explicit identity gate.

`native-formatter-runtime/` links the complete bounded formatter with zero
undefined symbols. The 225-case complete formatter experiment matches. Actual
source formatting also passes 65,637 device-info cases (all sequence halfwords,
131,274 format calls per side); raw r1 differs in 65,636 cases, consistent with
the existing header/private-frame gates. The new broader graph at
`native-battery-runtime/source-formatting-integration-verification.json`
passes 2,896 cases and 336 numeric/FPSCR cases, with 18 actual formatter calls and
655 encoder/CRC/memmove/fragment/TX operations per side. All earlier graph
observations are preserved; the formatter fixture is removed. Lower response,
allocator/queue/connection and hardware boundaries remain scoped in receipts.

Strict frontier: 643 tested candidates, 1,373 compiled hints and 1,310 unresolved
routes across 3,326 unchanged locked rows. Private frames, complete raw ABI,
original instructions, full-image source integration and hardware remain open.

String/stdout checkpoint: `native-formatter-stream/` compiles native printf,
sprintf, unbounded buffer output and stdout-byte adaptation (82 native bytes).
All 4,212 direct cases pass, including 343 matching faults, three backend-record
mutation modes and 3,978 backend calls per side. Sprintf and buffer-putc raw
r0/r1/r2/r3 are checked; printf caller-saved registers and private callback
addresses remain gated. One 10-byte compiled buffer-putc section matches native
instruction bytes without relocations. The summary records that section-local
match separately from original image placement/full instruction identity.

`native-rtt-write/` replaces the stdout backend boundary with the recovered
52-byte wrapper over existing pinned SEGGER RTT 6.18a ring writing and native
source initialization. All 3,538 direct cases pass, including all BASEPRI byte
values, initialization, wrap/skip/trim and blocking with sufficient free space.
The 972-case actual-source printf graph also passes, with 9,900 ring writes per
side and no backend fixture. R1 differs in 108 combined cases and remains
explicit. `native-formatter-stdio/` links all four formatted-output entrypoints
and the RTT/memory providers with no undefined symbols. This does not close all
stdio APIs, private frame/interrupt/debugger behavior or the full image.

Strict frontier: 648 tested candidates, 1,372 compiled hints and 1,306 unresolved
routes across 3,326 unchanged locked rows. Five bodies were added; the RTT write
route advanced from a compiled hint to a tested native contract. Hardware,
source-owned whole-image startup/configuration and original identity remain
open.

Floating-bit helper checkpoint: `native-float-bits/` compiles eleven native
classifiers, conversions, subtraction adapters, power-of-two scaling and the
authenticated environment-control leaf (358 native bytes). All 459,814 direct
comparisons pass. The explicit header models physical register slots for the
classifiers; an initial compiler-clobbered R3 failure and its resolution remain
in `classifier-register-counterexample.json`.

`native-float-bits-runtime/` links these bodies with the existing source math
and pinned LLVM integer runtime, with zero undefined symbols. Its actual object
passes 1,552 cases through 23 native math callers under four FPSCR rounding
modes. These callers remain native bodies. Native cold-boot SRAM is an explicit
fixture. The four-byte environment-control section matches native instruction
bytes without relocations, separately from image placement/full identity.

Strict frontier: 659 tested candidates, 1,372 compiled hints and 1,295 unresolved
routes across 3,326 unchanged locked rows. Complete raw ABI/private frames,
source-owned startup, full image integration, instruction identity and physical
hardware remain open.

Native polynomial checkpoint: `native-polynomial/` compiles the 248-byte
hard-float Horner evaluator at 0x3b40c against recovered source add/multiply.
REA establishes body ownership; Ghidra-MCP bytes authenticate its D0 argument
and result with R0 coefficient pointer/R1 count. All 3,840 direct comparisons
pass, with 59,748 source additions and multiplications per side. Coefficient
counts1..32, selected exceptional values, random patterns and all four FPSCR
rounding modes are covered. Zero/unbounded counts, invalid pointers, private
aliases and complete raw ABI remain gated.

The verifier links `native-polynomial-runtime.o` with no undefined symbols.
The actual object passes another 1,552 native-consumer cases, including 148
polynomial calls per side, alongside the eleven source bit helpers. All 23
consumer bodies remain native. Strict frontier: 660 tested candidates, 1,372
compiled hints and 1,294 unresolved routes across 3,326 locked rows. This
checkpoint does not close whole-image source integration or byte identity.

Floating rounding checkpoint: `native-float-rounding/` compiles signed64 to
binary32, its shared packer, and binary32/binary64 integral rounding. Four
source routes advance, representing 328 unique new native instruction bytes.
The 92-byte packer at 0x2808a is an interior entry of the noncontiguous 136-byte
0x27e0c body, not 92 additional bytes. The existing tested 18-byte 0x28078
remainder primitive is reused from `structured-float/`. A four-byte encoded-one
literal at 0x28330 is source-owned and byte-equal; placement remains gated.

All 232,492 direct comparisons pass, including 139,456 signed integers, every
binary32/64 exponent with selected fractions, and raw packer/rounding samples.
`native-float-rounding-runtime/` links with zero undefined symbols. Its actual
object passes 1,552 native-consumer cases with 56 calls each to source integral32
and integral64, 16 source remainder calls and 148 source polynomial calls. All 23
consumer bodies remain native. Internal native calls, redirected boundaries
and actual compiled-entry observations are recorded separately; the initial
inlining/count harness counterexample is retained.

`llvm-signed64-float32/` compiles unchanged pinned LLVM 20.1.8 floatdisf and its
headers. All 139,456 native signed-conversion comparisons pass. This is a
bounded reuse candidate, not selected runtime or full ABI/instruction proof.
Strict frontier: 664 tested candidates, 1,372 compiled hints and 1,290 unresolved
routes across 3,326 unchanged locked rows. Complete private/register/flag ABI,
whole-image source integration, byte identity and physical hardware stay open.

Square-root checkpoint: `native-float-sqrt/` compiles the 162-byte raw binary64
integer recurrence at 0x2820a against source shifts and remainder rounding.
REA and Ghidra-MCP authenticate the complete native span. All 73,728 direct
cases pass, including every exponent/sign with selected fractions, random
patterns and 4,096 integer squares. The native signed encoding entry test
returns +0 for nonpositive encodings; positive exceptional/subnormal encodings
retain the forced hidden bit. This is not a generic IEEE replacement.

`native-math-sqrt/` closes source public sqrt (122 bytes), VFP sqrtf (58 bytes)
and the errno setter (6 bytes). The authenticated pointer at 0x3bca4 identifies
a four-byte SRAM cell at 0x20007dbc. Source owns the cell and its verification
layout; cold initialization/final placement remain gated. Direct comparisons
pass 237,568 cases: sqrt 69,632, sqrtf 98,304, errno 69,632. Float cases cover
all rounding/flush-to-zero/default-NaN combinations with a preexisting inexact
flag. The 48,504 sqrtf and 69,632 setter writes match native observations.

`native-math-sqrt-runtime/` links without undefined symbols. Its 1,552-case
graph executes actual source sqrt/sqrtf, errno, integer root and prior helpers.
Two consumer bodies are now source; 21 remain native. Compiler-inlined errno
writes and redirected native setter entries remain separate call observations.
The binary64 wrapper error branch is not forced by a numerical boundary
fixture; only actual source helper results are observed. Complete raw ABI,
private aliases, physical VFP/interrupt behavior, full domain and original
instructions remain open.

Strict frontier: 668 tested candidates, 1,372 compiled hints and 1,286 unresolved
routes across 3,326 unchanged locked rows. Four bodies represent 348 native
instruction bytes; source-owned errno adds four SRAM bytes. Whole-image source
startup/integration, final placement, byte identity and hardware remain gated.

Floating selection checkpoint: `native-math-selection/` compiles eight native
routes (454 instruction bytes): binary32 raw compare flags, ceilf/floorf,
fmaxf/fminf, hard/core-register binary64 fabs and comparison-based fabsf.
The raw compare preserves R0 plus APSR NZCVQ. Core-register fabs preserves its
additional D0 result as well as R0/R1. Two source-owned literal spans total
20 bytes and match the native ceilf/floorf constants; their verification layout
is separate from final whole-image placement.

Direct comparisons pass 483,940 cases. Single-precision rounding/selection tests
cover every exponent with selected fractions, random words/pairs, all rounding,
flush-to-zero/default-NaN combinations and a preexisting inexact flag. Native
ceilf/floorf additions and comparisons retain FPSCR effects. Comparison-based
fabsf retains negative zero and native NaN signaling behavior. No generic
floating replacement is admitted by symbol name.

`native-math-selection-runtime/` links without undefined symbols. Its expanded
1,952-case graph has 27 consumers: eight source bodies and 19 native bodies.
Actual source core-register fabs executes 84 calls. Internal helper inlining,
redirected boundaries and compiled-entry counts remain separate observations.

REA confirms seven function bodies. At 0x98eca both live REA and Ghidra-MCP lack
function registration; the negative results are preserved. That candidate is
bound to locked corpus/ownership, exact Ghidra-MCP memory bytes, authenticated
ELF disassembly and native entry comparisons. Live metadata and exhaustive
boundary/caller identity remain explicit gates, alongside private frames,
remaining raw ABI, physical FPU/interrupt behavior, full domain and original
image identity.

Strict frontier: 676 tested candidates, 1,372 compiled hints and 1,278 unresolved
routes across 3,326 unchanged locked rows. Whole-image source startup and
integration, final placement, byte identity and hardware remain open.

Binary64 flag checkpoint: `native-double-flags/` compiles both 48-byte physical
comparison entries at 0x27f0c/0x27f3c. REA and Ghidra-MCP authenticate both spans.
C computes native encoded integer keys, while final source-compilable compare
instructions preserve high/low-word NZCV semantics. Small ABI adapters retain
native R12 and LR rather than capturing undefined incoming C register values.
Their private frames differ from the native 12-byte frames and remain gated.

All 312,896 direct comparisons pass: 156,448 per direction. They cover every
binary64 exponent/sign with selected fractions, equal/high/low variants, edge
pairs and seeded random pairs under both initial Q values. R0/R1/R2/R3,
APSR NZCVQ, R12/LR, stack balance, callee registers and FPSCR are checked. These
raw encoded-key outputs differ from a generic boolean IEEE comparison API.

`native-double-flags-runtime/` links without undefined symbols. The actual
bundle passes the existing 1,952-case graph, with 136 forward and 84 reverse
source helper calls per side. Consumer source counts stay eight source and
19 native; helper closure does not admit the remaining native caller bodies.
Private-stack aliases, full input-pair domain, other architectural state,
original instructions and hardware remain open.

Strict frontier: 678 tested candidates, 1,372 compiled hints and 1,276 unresolved
routes across 3,326 unchanged locked rows. Two new routes account for 96 native
instruction bytes. Whole-image source startup/integration, final placement and
byte identity remain gated.

Double directed-rounding checkpoint: `native-double-directed/` compiles native
ceil at 0x388d8 and floor at 0x39108 (252 bytes each). REA and Ghidra-MCP
establish both complete spans. Two source-owned 24-byte tables contain the
native huge/zero/one/mask values and match exact authenticated data bytes.
Source calls recovered add/reverse-subtract and binary64 comparison providers;
the flag call and MRS execute in one asm statement to prevent intervening
compiler arithmetic from overwriting the result.

All 403,328 direct comparisons pass: 201,664 per routine. They cover every
binary64 exponent/sign with selected fractions/random patterns, every low16
fraction word at exponent20, and high/low carry samples across exponents20..51.
D0, FPSCR, balanced stack, integer/FP callee registers and nonstack writes match.
The exponent20 high-word increment is preserved explicitly from instructions,
rather than trusting the incomplete decompiler return expressions.

`native-double-directed-runtime/` has zero undefined symbols. The actual bundle
passes the 1,952-case graph with source ceil/floor (56 calls each). Ten of its
27 consumer bodies are now source and 17 remain native. Source comparison
entries execute 136 forward/84 reverse calls; redirected native-boundary counts
remain separate from compiled source calls. Private 40-byte native frames,
remaining raw caller/APSR behavior, full-domain and hardware proof remain open.

Strict frontier: 680 tested candidates, 1,372 compiled hints and 1,274 unresolved
routes across 3,326 locked rows. Two new routes represent 504 native instruction
bytes and 48 source-owned data bytes. Whole-image startup/source integration,
final placement, original instructions and byte identity remain gated.

Public round checkpoint: `native-math-round/` compiles round at 0x3ac88 and
roundf at 0x3ad68, with 24 source-owned bytes for one and signed-half constants.
REA records the double routine as 192 body bytes across a 194-byte span:
0x3ac88..0x3ace9 and 0x3acec..0x3ad49, excluding two padding bytes. Both complete
ranges are authenticated against Ghidra-MCP and the locked app. The earlier
192-byte contiguous prefix is retained explicitly as a prefix observation.
The float body is 154 bytes, for 346 unique body bytes across both routes.

All 376,832 direct comparisons pass: round 81,920 and roundf 294,912. Tests cover
every binary32/64 exponent with selected fractions/random words, halfway
integers -2048..2047 and adjacent bit patterns. Float cases exercise all
rounding/flush-to-zero/default-NaN combinations with a preexisting inexact flag.
D0/S0, FPSCR, integer/FP callee registers, balanced SP and nonstack writes match.
The double routine uses actual source integral rounding, subtraction/addition
and both physical flag providers. Float executes authenticated VFP arithmetic
and signed-bit branch rules, then restores the original sign bit.

`native-math-round-runtime/` links without undefined symbols. Its actual bundle
passes the 1,952-case graph with 56 source round and roundf calls each. Twelve
of 27 consumer bodies are now source; 15 remain native. Redirected boundaries,
compiled helper entries and compiler inlining remain separate observations.
Native 64-byte double/16-byte float frames, private aliases, remaining raw
caller/APSR, full-domain and physical hardware proof remain open.

Strict frontier: 682 tested candidates, 1,372 compiled hints and 1,272 unresolved
routes across 3,326 locked rows. Whole-image source startup/integration, final
placement, original instructions and byte identity remain gated.

Shared special-value checkpoint: `native-math-special/` compiles twelve entry
contracts for binary64/binary32 division, self/pair addition and square-based
exceptional paths. Their routed leaf spans total 196 instruction bytes, with
56 source-owned constant bytes. Five entries are shared tails of remaining
parent functions; their ranges must not be counted again as disjoint whole-image
coverage or promoted to complete parent source.

REA authenticates six independent leaf bodies and five shared parent ranges.
Live REA/Ghidra function metadata at 0x3bace is absent; its locked powf label,
exact six-byte memory span, authenticated disassembly and direct execution
provide the bounded leaf contract. Negative metadata results remain explicit.
The compiled float self/pair-add sections each match their six native instruction
bytes without relocations. They join the separate compiled-span registry;
original image placement/full instruction identity remains unproven.

All 309,828 direct comparisons pass. Software binary64 wrappers execute the
existing source add/multiply/divide; binary32 wrappers use the native VFP
operations, including exception/status effects. Samples include all exponents
with selected fractions, random pairs, both signs and all float rounding/
flush-to-zero/default-NaN modes with initial inexact zero/one. These tests do not
infer generic IEEE behavior from helper names.

`native-math-special-runtime/` links without undefined symbols. Its actual
bundle passes the 1,952-case graph with new leaf providers substituted. The
add-pair entries have direct coverage but zero calls in this bounded graph.
Consumer source counts remain twelve source and fifteen native; shared-tail
replacement does not compile the parent transcendental bodies. Raw caller
registers, private aliases, full domain and physical hardware remain open.

Strict frontier: 694 tested candidates, 1,372 compiled hints and 1,260 unresolved
routes across 3,326 locked rows. Whole-image startup/source integration, final
placement, original instruction identity and byte equality remain gated.

Expf/tanhf checkpoint: `native-expf-tanhf/` compiles native expf and tanhf with
recovered VFP range reduction, coefficient evaluation, scaling and errno paths.
Expf contributes 426 contiguous native bytes. Tanhf has 214 body bytes across
208 main bytes and its already source-compiled six-byte self-add tail at
0x3bac8. New disjoint code is therefore 634 bytes, not 640. REA and Ghidra-MCP
authenticate both body ranges and the reused tail.

Named C arrays own 116 numeric bytes: 32 coefficient/domain bytes, 16 scaling
bytes, 48 indexed table bytes and 20 tanhf coefficients. Three authenticated
PC-relative offsets resolve to the base/residual/multiplier tables. Those
pointer literals are replaced by named C references, not counted as emitted
original-layout numeric bytes. Original relocation/instruction layout remains
an explicit gate.

All 672,832 direct cases pass: 336,416 per body. Tests cover every binary32
exponent with selected fractions/random words, threshold-adjacent bits, a dense
numeric grid and all rounding/flush-to-zero/default-NaN modes under initial
inexact zero/one. S0, FPSCR, source errno writes (127,084 per side for expf),
balanced SP, integer/FP callee registers and nonstack writes match. Operations
retain native VMLA/VMLS and conversion order rather than generic host math.

`native-expf-tanhf-runtime/` links without undefined symbols. Its actual source
bundle passes the 1,952-case graph, including 72 compiled expf and 56 compiled
tanhf entries. Fourteen of 27 consumer bodies are source and thirteen remain
native. Redirected boundaries and direct compiled calls remain distinct.
Remaining raw caller/APSR/private frames, full domain, physical VFP/interrupt
behavior and source cold initialization are unproven.

Strict frontier: 696 tested candidates, 1,372 compiled hints and 1,258 unresolved
routes across 3,326 unchanged locked rows. Whole-image startup/source integration,
final placement, original instructions and byte identity remain gated.

Float logarithm checkpoint: `native-float-logs/` compiles log10f at 0x396e4
(332 native bytes) and logf at 0x39864 (320 bytes). REA and Ghidra-MCP
establish both complete contiguous bodies. Source retains native subnormal
normalization, near-one and indexed polynomial paths, VFP operation order,
zero comparisons and errno/exceptional branches. In flush-to-zero mode the
native comparisons can classify subnormal inputs as zero; no generic raw-bit
sign check replaces those VFP comparisons.

Named C arrays own 208 numeric bytes: 80 coefficient/scaling bytes and four
eight-entry high/low tables totaling 128 bytes. Four authenticated native
PC-relative offsets resolve to these named table slices. Raw pointer literals
are not counted as emitted source-owned numeric data or final relocation proof.

All 694,592 direct cases pass: 347,296 per routine. Cases cover every exponent
with selected fractions/random words, near-one/index-boundary adjacent bits,
a dense numeric grid and all rounding/flush-to-zero/default-NaN modes under
initial inexact zero/one. S0, FPSCR, errno (171,856 matching writes per side for
each body), balanced SP, integer/FP callee registers and nonstack writes match.

`native-float-logs-runtime/` links without undefined symbols. Its actual bundle
passes the 1,952-case graph with 56 compiled logf and log10f calls each. Sixteen
of 27 consumer bodies are source and eleven remain native. Redirected native
boundaries and direct compiled calls remain separate observations. Native
eight-byte/private frames, remaining raw caller/APSR state, full domain,
physical FPU/interrupt behavior and source startup remain unproven.

Strict frontier: 698 tested candidates, 1,372 compiled hints and 1,256 unresolved
routes across 3,326 locked rows. Whole-image source integration, final placement,
original instructions and byte identity remain gated.

Atanf checkpoint: `native-atanf/` compiles the complete 296-byte native body at
0x38774, with 56 source-owned constant bytes. REA and Ghidra-MCP establish both
code/data spans. Source retains native reciprocal and signed-half argument
reductions, split high/low offsets and VMLA polynomial order. Small subnormals
use the existing source classifier/underflow helper, then return the original
bits; NaNs use the existing source self-add entry. Large-input constants are
retained rather than generated by a generic host-math replacement.

All 467,488 direct cases pass. Cases cover every exponent with selected
fractions/random words, reduction-threshold adjacent bits, a dense numeric grid
and all rounding/flush-to-zero/default-NaN modes under initial inexact zero/one.
S0, FPSCR, errno (zero writes on both sides), balanced SP, integer/FP callee
registers and nonstack writes match.

`native-atanf-runtime/` links without undefined symbols. Its actual bundle
passes the 1,952-case graph with 56 compiled atanf entries. Seventeen of 27
consumer bodies are source and ten remain native. Redirected boundaries and
compiled dependency entries remain distinct. Native 16-byte/private frames,
remaining raw caller/APSR, full domain, physical FPU/interrupt behavior and
source startup remain unproven.

Strict frontier: 699 tested candidates, 1,372 compiled hints and 1,255 unresolved
routes across 3,326 locked rows. Whole-image source integration, final placement,
original instructions and byte identity remain gated.

Atan2f checkpoint: `native-atan2f/` compiles the complete 594-byte native body
at 0x384c8, with 88 source-owned constant bytes. REA and Ghidra-MCP establish
both code/data spans. Source preserves distinct integer classification words
and live FP operands on exceptional paths, signed-zero/infinity handling,
exponent-gap shortcuts, normalization, quadrant offsets and native VFP
argument reduction/polynomial order.

All 942,112 direct pair cases pass. They cover all binary32 exponents in paired
exponent-gap samples, both quadrant signs, signed-zero/infinity/NaN pairs,
normalization/reduction boundaries, a numeric grid and random pairs under all
rounding/flush-to-zero/default-NaN modes with initial inexact zero/one. S0,
FPSCR, balanced SP, integer/FP callee registers and nonstack writes (including
errno) match. An inherited harness label incorrectly claimed binary64 coverage;
the label counterexample is retained and the complete numerical set was rerun
with the accurate binary32 label and unchanged numerical trace.

`native-atan2f-runtime/` links without undefined symbols. Its actual bundle
passes the 1,952-case graph with 144 compiled atan2f entries. Eighteen of 27
consumer bodies are source and nine remain native. Redirected boundaries and
compiled helper entries remain distinct observations. Native 32-byte/private
frames, remaining raw caller/APSR, full pair domain, physical FPU/interrupt
behavior and source startup remain unproven.

Strict frontier: 700 tested candidates, 1,372 compiled hints and 1,254 unresolved
routes across 3,326 locked rows. Whole-image source integration, final placement,
original instructions and byte identity remain gated.

### Native float trigonometric reducer candidate

`native-trig-reduce/` records REA's 316-byte contiguous body at `0x3bb04`,
Ghidra-MCP reads matching the locked application, and a C implementation in
`components/runtime/native_trig_reduce.c`. Its raw ABI uses R0 for the quadrant
pointer, R1 for encoded input and S0 for incoming/result. Invalid encodings
store `0xffffffff` and preserve incoming S0. A signed exponent index reaches
four words before the nominal table: the source owns an authenticated 48-byte
window plus 20 coefficient bytes, without counting shared data as new firmware
coverage. The PC-relative pointer is replaced by a named source array.

The source passes 212,992 direct cases covering every binary32 exponent, both
signs, selected mantissas, 4,096 random encodings, all rounding/FZ/DN controls,
and initial inexact zero/one. Incoming S0 is independently seeded. S0, FPSCR,
quadrant write sequence, SP balance and integer/FP callee registers match.
The first harness attempt retained IT state after conditional returns and
faulted in native code at the first negative-zero input; the retained
`harness-counterexample.json` describes this. Resetting XPSR for each independent
call permits the full set to pass. This is emulator evidence, not physical FPU
proof.

`native-trig-reduce-runtime/` links this object with the previous atan2f runtime
without undefined symbols. `tools/audit_native_trig_reduce.py` authenticates the
candidate independently. Consumer-graph verification and strict frontier
admission remain pending; this candidate does not change the 700 tested / 1,372
compiled-hint / 1,254 unresolved counts. Caller scratch/APSR, native private
frame, pointer faults/stack aliasing, full input domain, instruction equality,
final image placement and whole-firmware completeness remain open.

The reducer is now admitted after its 1,952-case consumer graph passes, with
48 observed compiled reducer entries through native math callers. Graph return,
FPSCR, integer/FP callee preservation and nonstack writes match. This graph
explicitly resets XPSR for independent calls and preserves R0/R1/S0 when
redirecting the raw helper. All previous helper observation totals remain
unchanged; the new helper adds 48 native, redirected and compiled observations.
The earlier pending-admission note above records the preceding checkpoint.

`audit_native_trig_reduce.py` now authenticates the frozen corpus slice, locked
ownership row, REA target, direct and graph drivers/receipts, data reads,
source/object inputs, partial runtime providers and parent layouts. The strict
frontier now contains 701 tested candidates, 1,372 compiled hints and 1,253
unresolved routes across the same 3,326 locked rows. Eighteen graph consumer
bodies are source and nine remain native. Source sinf/cosf/tanf bodies remain
next work; the helper admission does not imply those parents are reconstructed.

### Native cosf source checkpoint

`native-cosf/` supplies the full recovered entry body at `0x38a5c` (280 bytes)
plus 56 source-owned numeric bytes at `0x38b74`. REA authenticates the inclusive
body range and Ghidra-MCP reads match the locked application. The frozen corpus
slice and ownership row remain hash bound. C owns threshold classification,
quadrant control, four-stage medium-input reduction, small-input return,
polynomial structure and exceptional dispatch. Explicit VFP instructions retain
nonfused arithmetic and conversion ordering. Large inputs use the source trig
reducer; infinity sets errno then invokes the source invalid helper, and NaNs
use the source self-add helper.

The source passes 470,752 direct cases: all binary32 exponents, both signs,
selected mantissas, threshold neighbors, a numeric grid, random encodings and
all rounding/FZ/DN controls with initial inexact zero/one. S0, FPSCR, integer/FP
callee registers, balanced SP, errno and nonstack writes match; 64 errno writes
occur per side. Independent calls reset XPSR. The 1,952-case consumer graph
passes with 56 actual compiled cosf entries. Nineteen public consumer bodies
are now source and eight remain native. `native-cosf-runtime/` links the actual
cosf object with prior providers without undefined symbols.

The accumulated verification scripts exceeded the linker's nested-INCLUDE
limit. `native_cosf_verification.ld` expands the ten parent layouts into one
script; receipts bind all original parent hashes. This changes verification
plumbing and supplies no evidence of original final layout. Complete raw caller
scratch/APSR, native eight-byte frame and alias/fault contracts, full domain,
physical FPU behavior, startup, original instructions and image identity remain
open. Strict frontier after admission: 702 tested candidates, 1,372 compiled
hints and 1,252 unresolved routes across 3,326 immutable ownership rows.

### Native sinf source checkpoint

`native-sinf/` implements the full 344-byte entry body at `0x3ae04`, with
56 source-owned numeric bytes at `0x3af5c`. REA body metadata, Ghidra-MCP byte
reads, the frozen corpus slice and immutable ownership row are bound in its
receipts. C owns range/quadrant decisions, four-stage medium reduction,
polynomial structure and exceptional dispatch; explicit nonfused VFP operations
retain native order. Large inputs use the source reducer. Tiny finite inputs
retain their raw encoded return, while source classification and low-square
helpers reproduce the native underflow side effect when classification is four.
Infinite inputs set errno and invoke the source invalid helper; NaNs use source
self-add.

All 470,752 direct cases pass across every binary32 exponent, both signs,
selected mantissas, reduction thresholds, grid/random values and all
rounding/FZ/DN controls with initial inexact zero/one. The inherited threshold
list did not explicitly center the tiny boundary; a separate 1,088-case receipt
checks both signs within eight encodings of `0x39800000` under the same controls.
Its coverage labels explicitly exclude all-exponent and dense-grid coverage.
S0, FPSCR, balanced SP, integer/FP callee registers, errno and nonstack writes
match. The broad run observes 64 errno writes per side; the supplemental run
observes none. Each independent call resets XPSR.

The actual source bundle passes 1,952 graph cases with 56 compiled sinf entries.
Twenty public consumer bodies are source and seven remain native. The partial
`native-sinf-runtime/` has no undefined symbols. Its flattened verification
layout preserves the previous placement declarations and binds every parent
layout hash; final original placement remains unproven.

`audit_native_sinf.py` validates both direct receipts, consumer graph, numeric
sections, upstream provider inputs and frozen evidence before frontier admission.
Strict frontier: 703 tested candidates, 1,372 compiled hints and 1,251 unresolved
routes across the same 3,326 locked rows. Complete raw caller scratch/APSR,
native sixteen-byte frame and alias/fault contracts, full numerical domain,
physical FPU behavior, source startup, remaining bodies, original instructions
and whole-image byte identity remain gated.

### Native tanf source checkpoint

`native-tanf/` implements the recovered tanf entry at `0x3b048`. REA records a
noncontiguous 332-byte body: 322 main bytes through `0x3b189`, plus the ten-byte
invalid-value tail at `0x3bad4` already implemented by shared source helpers.
New unique native coverage is 322 bytes, not 332. Ghidra-MCP reads authenticate
both ranges and the 56-byte numeric block at `0x3b18c` against the locked image.

Frozen pseudocode reports an unrecovered jump table at `0x3b0c2`. Authenticated
native disassembly resolves it as conditional POP {PC}: the even-quadrant path
returns the six-coefficient polynomial result, while the fallthrough computes
`-1/result`. The C body owns this control flow, medium-range four-subtraction
reduction, tiny-input classification/underflow behavior and exception dispatch.
Large inputs use the source trig reducer. Explicit VFP instructions retain
nonfused operation and conversion order. No executable blob or opcode array is
used as source.

The full 474,016 direct cases pass: all binary32 exponents, both signs, selected
mantissas, random/grid inputs and neighborhoods of exact tiny/reduction and
pole-related boundaries under all rounding/FZ/DN controls and initial inexact
zero/one. S0, FPSCR, balanced SP, integer/FP callee registers, errno and nonstack
writes match, including 64 errno writes per side. The actual source runtime
has no undefined symbols and passes 1,952 consumer cases with 56 compiled tanf
entries. Twenty-one public consumer bodies are source; six remain native.

`audit_native_tanf.py` authenticates the source/build inputs, direct and graph
receipts, REA ranges, Ghidra data, frozen corpus/ownership, native disassembly,
shared-tail accounting and verification layout ancestry. The strict frontier
now has 704 tested candidates, 1,372 compiled hints and 1,250 unresolved routes
across 3,326 immutable ownership rows. Caller scratch/APSR, native sixteen-byte
frame/alias/fault behavior, full domain, physical FPU behavior, source startup,
remaining providers, final placement, original instructions and whole-image
byte identity remain gated.

### Native binary64 atan source checkpoint

`native-atan/` implements the full 622-byte contiguous entry at `0x381f0`,
using existing source raw binary64 add/multiply/divide/subtract, classifier,
absolute value, shared exceptional helpers and polynomial evaluation. C owns
high-word threshold classification, four reductions, two ordered polynomial
chains and final correction/sign reconstruction. No host double arithmetic
replaces native software arithmetic. REA and Ghidra-MCP authenticate the body,
88 local numeric bytes and 152 coefficient/correction-table bytes. Four
PC-relative table words are authenticated and replaced with named C arrays;
the original pointer words are not claimed as recreated numeric data.

All 37,436 direct cases pass. Every binary64 exponent, both signs and selected
mantissas are checked under four rounding modes, alongside threshold neighbors,
a numeric grid and random encodings. Nine explicit values additionally cover
all rounding/FZ/DN controls with initial inexact zero/one; that additional
control coverage is not claimed for every exponent sample. D0, FPSCR, balanced
SP, integer/FP callee registers, errno and nonstack writes match; there are no
errno writes. The initial run reached receipt generation without comparison
failure, then failed on a copied `native_aatan` parent-layout typo. Its error
log is retained. The typo was corrected and the full run repeated to produce
the admitted receipt.

`native-atan-runtime/` links without undefined symbols and passes the
1,952-case graph with 56 actual compiled atan entries. Twenty-two public
consumer bodies are source; five remain native. The strict frontier now has
705 tested candidates, 1,372 compiled hints and 1,249 unresolved routes across
3,326 immutable ownership rows. Complete raw caller scratch/APSR, native
48-byte frame and aliases, full numerical domain, physical FPU behavior, source
startup, remaining providers, final placement, original instructions and
whole-image byte identity remain open.

### Native tanh body candidate: source expm1 remains open

`native-tanh/` compiles the recovered tanh control flow, using source raw
binary64 arithmetic, classification, absolute value and exceptional helpers.
REA's 326-byte noncontiguous body contains 306 main bytes at `0x3b1c8` and
20 already source-owned self-add bytes at `0x3b538`. Ghidra-MCP authenticates
both spans and the 40-byte numeric block at `0x3b300`. The frozen corpus and
ownership row remain unchanged and hash bound.

The partial `native-tanh-runtime/` intentionally retains exactly one unresolved
source provider: `r1_native_expm1`. The explicitly named fixture layout binds
this symbol to the authenticated native entry `0x3b5c0` solely for verification.
No source expm1 body, source-complete runtime or frontier admission is claimed.
The native linker emits its expected absolute-Thumb-fixture warning; the
executed fixture still remains original application code, not source evidence.

The candidate passes 37,316 direct cases: every binary64 exponent with selected
mantissas under four rounding modes, threshold neighbors, grid/random cases,
and a separate nine-value all-FZ/DN/initial-inexact control set. D0, FPSCR, SP
balance, integer/FP callee registers, errno and nonstack writes match; there are
no errno writes. The graph passes 1,952 cases, with 56 compiled tanh entries.
Twenty-three public entry bodies execute source in this fixture graph, but tanh
still delegates to native expm1; the admitted source graph remains twenty-two
source entry bodies and five native bodies. The strict frontier stays at
705 tested, 1,372 compiled hints and 1,249 unresolved routes.

`audit_native_tanh_fixture.py` separately audits this candidate and enforces the
unresolved-provider/fixture labels. REA records the pending expm1 body as 1,092
bytes across `0x3b5c0..0x3b9e7` and `0x3ba98..0x3bab3`; source implementation is
available internal work, not an external blocker. Native 48-byte frame,
caller scratch/APSR and aliases, full numerical domain, physical FPU behavior,
source startup, full provider integration, final placement, original instruction
identity and whole-image byte equality remain open.

### Source expm1 closes the tanh dependency gate

`native-expm1/` reconstructs the complete 1,092-byte body across
`0x3b5c0..0x3b9e7` and `0x3ba98..0x3bab3`. C owns native special-value and
range decisions, signed reduction, correction terms, polynomial sequencing and
final encoded-exponent reconstruction. It uses existing source arithmetic,
integer conversion, flag-comparison, errno and exceptional helpers; no host
double arithmetic or native code fixture supplies the algorithm.

The source emits 212 numeric bytes: 112 prefix bytes, 60 suffix bytes and a
40-byte polynomial. The four-byte PC-relative pointer at `0x3ba58` is separately
authenticated and replaced by a named array. The polynomial's last eight bytes
overlap the previously recovered reducer table prefix; only 204 numeric bytes
are newly unique. The initial verification link rejected overlapping original
placements. Its error is retained, and the new verification layout places the
polynomial array with source text. Input section bytes independently match the
native polynomial. This verification placement does not establish final image
placement or original pointer words.

All 37,696 direct expm1 cases pass, including 8,648 errno writes per side. Cases
cover every binary64 exponent and selected mantissas under four rounding modes,
random/grid inputs, threshold/overflow neighbors and selected reduction-index
boundaries including -2/-1/0/1/2, 19/20, 55/56/57 and 1023/1024. Nine explicit
values additionally cover all FZ/DN/initial-inexact combinations; this does not
claim those controls for every exponent sample. D0, FPSCR, SP balance,
integer/FP callee registers, errno and nonstack writes match.

`native-tanh/source-verification.json` reruns all 37,316 tanh cases with compiled
source expm1. Its numerical trace matches the earlier native-fixture trace;
the original fixture receipts remain historical evidence. The new
`native-expm1-runtime/` has no unresolved symbols and no expm1 fixture binding.
Its 1,952-case graph passes with 20 compiled expm1 entries and 56 compiled tanh
entries. Twenty-three public consumer bodies are source and four remain native.

`audit_native_expm1.py` validates the source/runtime dependency chain, new tanh
receipt, REA/Ghidra spans, frozen corpus/ownership, overlapping numeric bytes,
PC-relative table contract and layout/error evidence. The strict frontier now
contains 707 tested candidates, 1,372 compiled hints and 1,247 unresolved routes
across 3,326 immutable rows. The source expm1 gate supersedes the prior tanh
candidate checkpoint. Complete raw caller scratch/APSR, native 80-byte expm1
and 48-byte tanh frames/aliases, full domain, physical FPU behavior, source
startup, remaining providers, final placement, original instructions and
whole-image byte identity remain open.

### Native binary64 exp source checkpoint

`native-exp/` reconstructs the complete 714-byte contiguous entry at `0x38bb0`.
C owns special/range classification, signed reduction, native polynomial
sequencing, exponent-word scaling and the two-stage subnormal-result path.
Existing source software arithmetic, flag comparisons, integer conversion,
classification, errno and exceptional providers supply all dependencies.
REA authenticates the body and Ghidra-MCP reads match its instructions, local
data region and tables to the locked application. The frozen corpus slice and
ownership row remain immutable and hash bound.

The source emits 208 numeric/padding bytes across four local spans and four
tables. Four PC-relative table pointers are separately authenticated and
replaced by named arrays. `native_exp_verification.ld` places these sections
for comparison; this is not original final layout or pointer-word equality.

All 37,776 direct cases pass: every binary64 exponent and selected mantissas
under four rounding modes, signed threshold/overflow/underflow neighbors,
random/grid inputs and selected reduction/scaling-index boundaries including
-1075/-1074 and -1022/-1021. Nine explicit values additionally cover every
FZ/DN/initial-inexact combination; that control scope is not claimed for every
exponent sample. D0, FPSCR, balanced SP, integer/FP callee registers, errno and
nonstack writes match, including 17,332 errno writes per side.

The actual `native-exp-runtime/` has no undefined symbols and passes all
1,952 graph cases with 56 compiled exp entries. Twenty-four public consumer
bodies are source; log, pow and powf remain native. Strict frontier: 708 tested
candidates, 1,372 compiled hints and 1,246 unresolved routes across 3,326 locked
rows. Complete caller scratch/APSR, native 72-byte frame/alias contracts,
full numerical domain, physical FPU behavior, source startup, remaining firmware
providers, final placement, original instructions and whole-image byte identity
remain open.

### Native binary64 log source checkpoint

`native-log/` reconstructs the complete 872-byte contiguous body at `0x39320`.
C owns native special/error dispatch, subnormal multiplication/normalization,
encoded exponent/mantissa reduction, near-one and two-polynomial general paths,
and ordered ln2 correction. Existing source raw arithmetic, integer conversion,
flag comparison, errno, polynomial and exceptional helpers supply its providers.
REA/Ghidra-MCP evidence authenticates the complete body, local data and tables;
the frozen pseudocode and ownership row remain unchanged and hash bound.

The source emits 144 numeric/padding bytes. Eight zero-table bytes at `0xbdb50`
overlap the previously recovered reducer window, leaving 136 newly unique
bytes. The zero array is placed with source text for verification, while its
input section bytes match the authenticated original table. Three PC-relative
pointer contracts are checked separately and replaced with named C arrays.
This proves neither final original layout nor recreated pointer-word bytes.

All 37,716 direct comparisons pass, including 18,688 errno writes per side.
Cases cover every binary64 exponent and selected mantissas under four rounding
modes, signed zero/negative/error values, random/grid samples, subnormals,
near-one and normalization/polynomial gate boundaries. Nine explicit values
additionally cover all FZ/DN/initial-inexact combinations; those controls are
not claimed for every exponent sample. D0, FPSCR, balanced SP, integer/FP callee
registers, errno and nonstack writes match the native contracts.

The actual `native-log-runtime/` links without undefined symbols and passes
1,952 consumer cases with 56 compiled log calls. Twenty-five public consumer
bodies are source and pow/powf remain native. Strict frontier: 709 tested
candidates, 1,372 compiled hints and 1,245 unresolved routes across the same
3,326 immutable ownership rows. Complete raw caller scratch/APSR, native
88-byte frame and aliases, full domain, physical FPU behavior, source startup,
remaining firmware providers, final placement, original instructions and
whole-image byte identity remain open.

### Powf dispatch candidate: reduced core remains open

`native-powf-dispatch/` compiles the recovered exceptional-input dispatch and
core handoff for native powf at `0x3a620`. REA authenticates three body ranges
containing 1,524 bytes; they exclude a two-byte alignment gap and an embedded
80-byte constant block. The dispatcher corresponds to 580 native bytes, while
the remaining reduced logarithm/exponential core occupies 944 bytes across
`0x3a65c..0x3a9b9` and `0x3ac14..0x3ac65`. This accounting does not claim compiled
instruction equality. The dispatcher emits 16 authenticated numeric bytes.

C owns signed-base integer parity, NaN/identity priority, signed zero/infinity,
small-exponent words/live operands, subnormal base adjustment and error helpers.
Integer exponent words and the live FP operand deliberately remain separate:
some native paths modify only the floating slot before later integer decisions.
The source invokes existing add, invalid, errno and division-by-zero helpers.
One source provider, `r1_powf_reduced`, remains explicitly unresolved in
`native-powf-dispatch-runtime/`.

The verification-only C adapter in `tools/fixtures/` creates the native 32-byte
frame and binds that provider to native `0x3a65c`. Both the adapter and linker
fixture are hash bound, excluded from source-runtime completeness, and labeled
in every receipt. All 427,168 pair cases pass under every rounding/FZ/DN control
with initial inexact zero/one: every binary32 exponent, both base/exponent
signs, parity cases, signed zero/infinity/NaN pairs, grid and seeded random
pairs. S0, FPSCR, balanced SP, integer/FP callee registers and nonstack writes
(including errno) match. The 1,952-case fixture graph passes with 144 compiled
powf dispatcher entries. The fixture enum ABI flag was aligned with source
builds and both runs were repeated; numerical traces are unchanged.

`core-contract.json` records the raw native register handoff, exact range
partition and four PC-relative table contracts. Ghidra-MCP reads independently
authenticate all pending-core constants and four tables against the locked
application. The source core remains available internal work, not an external
blocker. `audit_native_powf_dispatch.py` enforces the unresolved/fixture labels
and validates frozen evidence, source/object/runtime inputs and execution
receipts. The candidate is not admitted to the strict frontier: counts stay
709 tested, 1,372 compiled hints and 1,245 unresolved routes. The admitted graph
still has 25 source bodies and pow/powf native; the fixture graph executes a
source powf dispatcher with its native core and leaves pow's entry native.
Complete raw scratch/APSR/frame aliases, full pair domain, physical FPU behavior,
source startup, provider integration, final placement, original instructions and
whole-image byte identity remain open.

### Source powf core closes the dispatcher gate

`native-powf-core/` compiles the remaining 944 native core bytes as ordered C
arithmetic, completing the 1,524-byte powf body with the prior dispatcher. It
owns bucketed logarithm reduction, the separate near-one path, split exponent
product, saturation decision, exponential tables and conversions, signed
one/two-stage scaling and overflow/underflow handling. Explicit VFP add/subtract,
multiply/divide, negative multiply, nonfused accumulate/subtract and conversion
instructions retain native sequencing; opcode arrays and executable blobs do
not supply source logic. The source helper interface is internal C ABI, not an
assertion of arbitrary raw native interior-entry compatibility.

The core emits 396 authenticated numeric bytes across four local spans and
four tables; the dispatcher adds 16 bytes (412 total). The prior REA body and
Ghidra-MCP reads, four PC-relative table contracts and frozen corpus/ownership
remain bound through the new evidence audit. Verification linker placement and
numeric equality do not establish original instruction or final image layout.

All 427,168 original pair cases pass again with compiled source core, preserving
the numerical trace of the earlier native-fixture run. A separate 67,840-case
set checks every log-table bucket boundary and the near-one threshold under
all rounding/FZ/DN/initial-inexact controls. Its inherited signed-zero/infinity
input-pair label was inaccurate; the counterexample and initial receipt are
retained, the label was set false and the complete supplemental set rerun with
unchanged numerical trace. It explicitly does not claim all-exponent or random
coverage. The broad receipt retains those separate coverage claims. S0, FPSCR,
balanced SP, integer/FP callee registers and nonstack writes match.

`native-powf-runtime/` links without undefined symbols and has no native-core
fixture binding. Its actual bundle passes 1,952 graph cases, with 144 compiled
powf entries and 132 compiled core calls. The core's native register handoff
is not redirected as though it were the C helper ABI; only actual compiled
helper entry observations are counted. Twenty-six public consumer bodies now
execute source and pow remains native. Historical fixture receipts stay intact;
the new source checkpoint supersedes their open dependency gate.

`audit_native_powf.py` validates the closed source/runtime dependency chain,
both direct receipts, graph, numeric sections, frozen evidence and the corrected
coverage label. Strict frontier: 710 tested candidates, 1,372 compiled hints
and 1,244 unresolved routes across 3,326 locked rows. Complete raw caller
scratch/APSR, original 32-byte frame/aliases, full pair domain, physical FPU
behavior, source startup, remaining providers, final placement, original
instructions and whole-image byte identity remain gated.

### Pow dependency: raw-register square-root wrapper

`native-sqrt-core-abi/` reconstructs the 110-byte wrapper at `0x90e8c`, called
by pow's half-exponent shortcut at `0x39c2e`. REA/Ghidra-MCP authenticate its
whole body against the locked artifact, and the frozen corpus/ownership row
are hash bound. It takes and returns encoded binary64 in R0/R1, with D0 as an
independent preserved incoming slot. This is distinct from the existing
hard-float public sqrt. C calls the existing source integer-root recurrence,
performs the native encoded result/input classification, and sets source errno
only when the native condition requires it. No new numeric data is emitted.

All 37,436 direct cases pass: every binary64 exponent, both signs, selected
mantissas, threshold/grid/random cases and four rounding modes, plus nine
explicit values with all FZ/DN/initial-inexact controls. Tests independently
seed D0 and compare it alongside raw R0/R1, FPSCR, balanced SP, integer/FP
callee registers, errno and nonstack writes. The first harness's inherited
write counter measured the eight-character errno string after the additional
D0 field shifted the write-list index. The counterexample and initial receipt
are retained; the index was corrected and the full set rerun with unchanged
numerical trace. The corrected nonstack/errno write count is zero per side.

The actual partial runtime links without undefined symbols and passes the
1,952-case graph with 16 compiled wrapper entries through still-native pow.
This is a dependency closure, not reconstruction of pow. Its REA dependency
contract records the pending 2,900-byte pow body across four ranges, including
44 bytes already owned by shared add/invalid helpers (2,856 newly unique bytes).
The pending body remains internal implementation work, not an external blocker.

`audit_native_sqrt_core_abi.py` validates the raw ABI, corrected counter,
source/runtime inputs, numerical/graph receipts and frozen evidence. Strict
frontier: 711 tested candidates, 1,372 compiled hints and 1,243 unresolved routes
across 3,326 immutable rows. Complete raw scratch/APSR/native32-byte frame
aliases, full domain, hardware behavior, source startup, remaining bodies,
final placement, original instructions and whole-image byte identity remain open.

### Binary64 pow dispatcher candidate: reduced core remains open

`native-pow-dispatch/` compiles the native exceptional/shortcut dispatch at
`0x399d0`. C owns signaling/quiet-NaN priority, zero/identity cases, negative-base
integer parity, signed zero/infinity, reciprocal/range-error cases, square and
half-exponent shortcuts, absolute-value normalization, domain errors and sign
selection. It reuses existing source arithmetic, add/invalid/division-by-zero/
overflow/errno helpers, signed conversion and the newly admitted raw-register
sqrt wrapper. No host pow or sqrt operation substitutes native behavior.

REA authenticates a 2,900-byte body across four ranges. The dispatcher
corresponds to 850 native bytes, the reduced core remains 2,006 bytes, and
44 shared add/invalid bytes were already source-owned. These are range-accounting
facts, not compiled instruction equality. Ghidra-MCP reads authenticate all
body ranges and local data against the locked application. Source emits
84 numeric/padding bytes, including eight existing zero-table bytes (76 newly
unique). The authenticated PC-relative zero-table contract is replaced by a
named C array placed with text solely for verification.

The partial runtime intentionally retains one unresolved source provider,
`r1_pow_reduced`. A separate verification-only adapter constructs the native
192-byte frame, supplies encoded absolute base/exponent/sign and binds that
provider to native `0x39d04`. `core-contract.json` records the exact native
register/stack handoff and dispatcher/core/shared-tail partition. This native
fixture and its downstream native execution do not establish source completion.

All 90,708 direct pair cases pass: every binary64 exponent with selected
mantissas, both signs, parity, signed zero/infinity/NaN, grid and random pairs
under four rounding modes. The explicit edge-pair set additionally covers all
FZ/DN/initial-inexact combinations; those controls are not claimed for every
exponent pair. D0, FPSCR, balanced SP, integer/FP callee registers and nonstack
writes (including errno) match. The 1,952-case fixture graph passes with
144 compiled pow dispatcher entries. All 27 public entries execute source in
that fixture graph, but pow still delegates to its native reduced core; the
admitted graph remains 26 source bodies and one native pow body.

`audit_native_pow_dispatch.py` enforces the unresolved/native-fixture labels
and validates source/runtime inputs, native ranges, data/zero-pointer contract,
frozen corpus/ownership and execution receipts. No source route is admitted;
strict frontier remains 711 tested, 1,372 compiled hints and 1,243 unresolved.
The remaining core is internal implementation work, not an external blocker.
Complete raw scratch/APSR/native192-byte frame aliases, full pair domain,
physical hardware behavior, source startup/integration, remaining providers,
final placement, original instructions and whole-image equality remain open.

Binary64 pow now has a compiled C reduced logarithm/product/exponential core,
closing the dispatcher candidate's last provider without its native fixture.
The source reuses existing software arithmetic, flags, conversion, polynomial,
classification and errno/range providers. REA authenticates the 2,900-byte
noncontiguous native body; Ghidra-MCP independently binds 324 core numeric
bytes. Together with dispatcher data this is 408 bytes, including eight shared
zero bytes. The 90,708 direct cases, 4,480 targeted boundaries and 1,952-case
consumer graph pass; all 27 public graph entries execute source (144 pow and
32 reduced-core calls). The partial runtime has zero undefined symbols.
No upstream origin is inferred from table or algorithm resemblance. Existing
pinned upstream providers remain the reuse path; adopting updates requires
preserving authenticated native arithmetic and exception contracts. Full raw
ABI/private frames, remaining firmware components, source startup/configuration,
original instructions/placement and byte-identical image integration remain
open. The historical dispatcher fixture checkpoint is superseded for source
closure and retained as immutable evidence.

Four native libc primitives now compile without undefined symbols: PRNG
rand/srand and scanf digit/cursor reads (66 native bytes). All 25,646 seeded
state, radix/raw-character and byte/cursor-advance cases pass, including exact
non-stack writes. Native digit conversion uses unsigned >= 0x41 at 0x28000;
the frozen pseudocode's strict comparison is corrected from authenticated
instructions. REA has PRNG function records but no parser records at 0x27ff4
or 0x28010; those negative observations are saved. Locked entries, decoded
instruction boundaries and Ghidra-MCP byte checks support the parser bodies.
This reconstructs native contracts without asserting a new upstream origin
or generic libc replacement compatibility. PRNG startup seed ownership, full
raw ABI and whole-firmware source/instruction/image integration remain open.

Native qsort, strcat, strncpy, memcmp and strtok now compile from C without
undefined symbols (292 corresponding native bytes). The 68,481 direct cases
pass with 213,646 identical comparator observations, exact non-stack write
order and complete test-arena equality. The first qsort counterexample found
an opposite byte-store order despite matching final data; the source now
follows native lower-index-first stores, with the failed trace retained.
REA function records and Ghidra-MCP byte reads authenticate all five ranges.
The comparator is an explicit byte-comparison fixture; arbitrary callbacks,
huge arrays, invalid/overlapping memory and complete raw ABI remain gated.
Strtok retains native exhausted-cursor behavior at 0x20007db4; source startup
ownership remains unproven. These recovered implementations do not establish
new upstream attribution or interchangeable libc behavior. Existing dependency
pins and native contracts remain necessary for subsequent provider upgrades;
whole-firmware source, placement and byte-identical image integration are open.

Scanf input get/unget and integer/string conversion bodies now compile as C
(620 native bytes), with the recovered digit helper resolving the partial
runtime's last symbol. All 25,400 seeded descriptor cases and 80,373 callback
observations match native return/callee state, write order and full test-arena
contents. Whitespace is a named verification callback fixture; native ctype
and full frontend/core remain separate providers. REA returns missing-function
records for these entries; locked ownership, frozen conversion pseudocode,
decoded control/return boundaries and Ghidra-MCP byte checks are retained.
No new upstream attribution is inferred from scanf resemblance.

A controlled replay demonstrates Unicorn 2.1.4 corrupting Thumb IT progression
when a memory-write hook observes a conditional store, skipping a subsequent
stack adjustment. The conversion C is unchanged from before that finding.
The repaired verifier observes executed decoded stores without memory hooks,
then reconciles their effects with independently read complete test-arena
bytes. The failing parser trace and hooked/unhooked reproduction are bound
into the audit. A separate inventory keeps historical direct named write-hook
drivers pending conditional-store exposure review; this finding alone does
not establish that a prior passing receipt is wrong. Complete raw ABI/control
flow, arbitrary callbacks/aliasing, source startup, remaining firmware and
original instruction/byte-identical image integration remain open.

Native ctype pointer/isspace now compile from C with a 257-byte non-executable
lookup window: EOF(-1), 128 ASCII flags and adjacent native data reached by
unchecked byte indices. Direct EOF/all-byte checks pass (261 calls); the
native low-bit lookup marks 64 non-ASCII bytes as whitespace. This qualifies
the locked standard-symbol identification without changing the ownership
ledger or substituting generic ASCII semantics. REA function records and
Ghidra-MCP bytes authenticate both bodies and the window. All 25,910 scanf
conversion/input cases and 84,687 callback observations now pass with source
native whitespace and no ASCII callback fixture. The partial runtime has
zero undefined symbols. Neighbor data overlaps independently recovered
numeric/configuration sections; final shared placement remains open.

The sscanf variadic frontend and descriptor initializer also compile with
source callback configuration. Their separate candidate bundle leaves exactly
r1_native_scanf_core unresolved, with no executable fallback or native core
fixture. The observed core entry is 0x283c4 (R0 input state, R1 descriptor;
44 pushed plus44 scratch bytes). Frontend behavior is not yet verified or
admitted to the tested frontier. One-word ARM AAPCS va_list handling is pinned
to the compiler representation. No new upstream origin is asserted. Full
core, raw ABI/private frames, source startup/configuration, original compiler
output/placement and byte-identical firmware integration remain open.

The scanf core is now C and resolves the frontend candidate's last provider.
All 38,356 full variadic calls and572 direct core/descriptor calls pass with
497,060 matching normalized callback observations, exact non-stack write order
and reconciled full test-arena readback. Candidate execution of native code is
forbidden. Source descriptor callbacks, input state, integer/string conversion,
raw ctype and variadic register/stack outputs execute source; there is no
native core fixture or unresolved runtime symbol. The direct calls separately
exercise the descriptor initializer that Clang inlines in the public frontend.

The810-byte native core, four-byte width limit and NOP conversion call sites
are authenticated with Ghidra-MCP; REA's missing core function record remains
explicit. Native floating and long-long integer scanf paths return preset
failure through NOPs, and are preserved rather than filled with generic libc
behavior. No new upstream origin is inferred. The initializer guarantees
mode zero; alternate descriptor/private scanset-frame modes, arbitrary
callbacks and full raw scratch/APSR/stack aliases remain gated. Callback
provider relocations are normalized only after raw-store reconciliation.
The locked scatterload analyzed extent also contains this manual core;
corresponding spans are not unique byte coverage or proof of source startup.
Historical observer review, startup/configuration, remaining firmware,
original compiler/shared-data placement and byte-identical image integration
remain open. This supersedes the frontend candidate's unresolved-core gate
while retaining its original evidence.

Native scatter decompression (86 bytes) and its supplemental word-zero handler
(14 bytes) now compile as C without undefined symbols. The127,394 comparisons
pass with exact non-stack write order, reconciled full-RAM effects and no
native code execution by the candidate. Token bytes, extended lengths,
overlapping/distance-zero backreferences and mandatory first-token processing
for zero output size are retained. The official input expands6,492 RAM bytes
and the zero handler clears213,172 bytes. Independent native return-cursor
observation establishes1,781 consumed compressed bytes within a1,784-byte span,
followed by three zero alignment bytes. The decoded RAM artifact is research
evidence; compressed payload/source-owned initialization remains a gate.

The two-row scatter configuration uses source callback relocations with
native source/destination/length fields. It is separate from final table
pointer bytes/placement and source startup. The word-zero entry is not in the
locked function ledger and is not counted as another tested route. REA lacks
function records for these entries; frozen ledger/pseudocode, decoded control
and Ghidra-MCP byte evidence remain explicit. The locked846-byte scatterload
extent partitions into28 dispatch bytes,8 literals and810 already recovered
scanf-core bytes, so it is not unique startup coverage. Dispatcher/continuation,
malformed input/alignment/raw ABI, initialized-data ownership, historical
observer review, remaining providers and byte-identical image integration
remain open. No upstream source origin is inferred from the compression format.

Scatter dispatch and its runtime handoff now compile with source region-handler
configuration and both source initialization providers. Fourteen seeded RAM
states produce identical provider arguments/order, exact non-stack writes and
full initialized RAM at an unexecuted application boundary. Boundary SP also
matches. The partial bundle deliberately leaves r1_native_application_entry
unresolved; its verification symbol is stop-before-execution only, with no
application code supplied as a fallback.

Raw handoff registers and LR differ and are saved as an explicit ABI gate:
R0/R1/R3/R4/R5/R12 values are not inferred equal from matching RAM/SP. This is
bounded initialization/control-target evidence, not full startup behavior.
REA lacks entry records; frozen entries and Ghidra-MCP bytes authenticate the
28-byte dispatcher,8 literal bytes and4-byte runtime trampoline with its4-byte
literal. The misleading locked846-byte scatterload analysis extent retains
810 separate scanf bytes and is not changed or counted as unique startup
coverage. Next application dependencies and the decoded callback at0x20006540
are recorded for source work; native main is not executed. Initialization-data
ownership, reset SP setup, raw ABI, remaining application/providers, historical
observer review and original instruction/byte-identical image integration
remain open. No new upstream origin is inferred for the product handoff.

The146-byte application entry now compiles as C with144 bytes of source-owned
build/version strings, SCR/callback-cell literals and log-module bounds.
All27,648 controlled cases pass for typed call order/arguments, three status
queues, mode-mask triples, SCR writes and non-stack RAM. Three fatal iterations
after a returning initialized callback are checked. The69,120 observed mode
reads reflect native short circuiting; the earlier ambiguous three-mode label
and original receipt are preserved beside its clarification. REA's missing
function record and authenticated Ghidra-MCP body/data evidence remain explicit.

Application entry now links with source scatter dispatch and initialization
providers. Thirteen imports remain in that partial bundle; several already
have separate source/test receipts, which are not assumed integrated here.
Every external provider and initialized callback in the entry test is a named
typed fixture. Provider execution/nonreturn behavior, native raw call ABI,
callback source ownership and initialized-data ownership remain open.

The registered CmBacktrace provider is available at
`third-party/upstream/cmbacktrace`, not the older path in historical correlation
notes. Its source hash and checkout match commit
`73714489f9d8af130aacb515586b397b604a5768` and the MIT license in the fetched
manifest. This is the authenticated1.4.2-compatible baseline, with an explicitly
unproven exact vendor checkout. The upstream core should be reused with recovered
R1 configuration/adapters rather than copied into another local implementation;
future updates still require native initialization, stack/frame and unwinding
contract checks. Integration, full startup, remaining bodies, raw ABI/hardware,
original compiler/shared-data placement and byte-identical image remain open.

Startup constructor reuse now resolves the held40-byte native route without
changing the locked ledger or adding another local implementation. Its frozen
end/size describe18 wrapper bytes at0x4e1e4 plus the22-byte shared post-init
tail at0x5cb4c, not a contiguous40-byte span. Fresh Ghidra-MCP bytes, REA's
post-tail and neighboring-function records, existing frozen pseudocode and
54 returned/12 null-fault comparisons support that accounting. The original
receipt/boundary hold is retained as historical evidence. The same existing
C wrapper and walkers are reused, with540 callback observations per side;
real registrars, raw argument residue and physical interrupts remain gated.

The46-byte peripheral module dispatcher now compiles as C. Its270 controlled
cases and2,700 callback observations per side preserve ten-call order, sampled
last raw R0, stack/callee state, PRIMASK changes and non-stack RAM. All leaf
provider bodies in that test remain explicit typed fixtures. Linking the
application/scatter candidate with this dispatcher and existing board sources,
plus a source-owned constructor alias, resolves nine direct application
imports. Four direct imports and67 total linked imports remain visible. The
aggregate is not claimed as an executed or complete application image.
Initialized data/callback ownership, full linked-provider ABI, raw startup
register/frame behavior, physical hardware, historical observer review and
original instruction/byte-identical image integration remain open.

Device-module and reset startup now compile from C with 248 bytes of recovered
strings, bounds and state/register configuration. The device ownership row's
158 bytes comprise its 74-byte entry plus an 84-byte shared hardware-check tail.
The RTC open/bind body, its supplemental empty callback, the pre-initialization
thunk and the reset adapter are also source. All 16,377 selected cases and
85,473 callback observations per side pass for raw R0, stack/callee state,
call order, state writes and full non-stack RAM. Tests demonstrate RTC handle
reload after open, byte flag updates after self-check mutation, and preservation
of the original reset snapshot across provider MMIO mutation. The broader raw
R0 comparison was added without changing the compiled firmware object.

The empty RTC callback uses the existing void(uint32_t) clock contract. Its
compiled two-byte BX LR matches the native bytes at the verification address;
this supplemental body is not another locked route or a whole-image identity
claim. REA identifies the reset adapter but lacks records for the other entries;
frozen ownership/control flow and Ghidra-MCP bytes remain explicit evidence.
All leaf provider bodies in the new behavior tests are named fixtures. Physical
RESETREAS write-one-to-clear behavior, arbitrary callbacks/raw argument residue,
private frames and actual linked-provider execution remain unproven.

The expanded source startup bundle resolves eleven direct application imports.
Only DFU SVC initialization and CmBacktrace initialization remain direct imports,
with 68 total unresolved imports including device pre-initialization, sensor
self-check and reset decode/report. That larger transitive graph is kept visible.
Source-owned initialized data/callbacks, full startup, historical observer
review, original compiler/shared-data placement and byte-identical firmware
integration remain open; no new upstream attribution is inferred for these
product-specific adapters.


Pinned MIT CmBacktrace now builds as an unmodified upstream translation unit
(commit73714489f9d8af130aacb515586b397b604a5768). Initialization alone is
selected into the startup bundle, using a thin pointer-type port to the already
source-tested R1 strncpy provider. The recovered FreeRTOS/Cortex-M4/FPU config
and stack/code linker symbols are source-owned. O0/fno-inline retains the four
range-field stores observed in native code; it does not establish original
compiler settings or instruction equality. Other compiled upstream fault/unwind
bodies are hints pending their own R1 adapter and native contracts.

The initializer passes10,240 native/source cases with30,720 actual source copy
calls per side and2,048 named logger-fixture calls per side. Full non-stack RAM,
store order, copy arguments and callee/SP state match. Tests distinguish zero
stack from zero code, retain the previous init flag on error, preserve the21st
name-array bytes and exercise wrapped range arithmetic. Noncanonical bounds
are explicit fixtures; authenticated files remain unchanged. Raw void-return R0
differs and remains an ABI gate. Ghidra-MCP authenticates84 code bytes,28 literal
bytes, the error pointer and98-byte string; REA has no procedure record there.

The new source bundle resolves twelve of thirteen direct application imports;
DFU SVC initialization remains direct and68 total transitive imports remain,
including the retained logger. Whole linked-provider execution, fault/unwind
adaptation, complete source data placement, raw ABI and byte-identical firmware
remain open. The locked frontier is now741 tested contract candidates,
1,376 compiled hints and1,209 unresolved routes across3,326 rows; these are
source evidence categories, not image completion.


DFU SVC initialization now reuses the authenticated Nordic17.1.0 unbonded DFU
source entry, its actual SVC0/R12=3 bridge and12-byte source async-state object.
The shared vector-restore tail is recovered R1 C: it preserves the native
short-circuit mode reads, ring/Nordic logging order and original supervisor
return across logging. Its SVC19 bridge remains an architectural call to an
external supervisor provider.216 bytes of source constants/strings match the
locked image at the verification addresses. This is selective upstream reuse;
the R1 logging adaptation is not attributed as unchanged Nordic source.

REA independently confirms the ownership row comprises32 bytes at0x52018 and
130 shared bytes at0x7876c, rather than a contiguous span. Ghidra-MCP reads match
those162 bytes, the4-byte async pointer and all216 source data bytes. The new
10,896-case differential receipt includes3,216 upstream-entry workflows and
7,680 direct restore cases,79,988 callback observations per side,2,136 SVC0 and
9,636 SVC19 observations per side. Raw R0, callee registers/SP, full non-stack
RAM and typed call order/args match, including early errors and async-state
mutation. All triples of mode values0..7 are exercised per logging group,
plus independent seeded six-read queues. Supervisor, vector-set and logger
bodies are explicit fixtures; physical SVC and full raw ABI remain unproven.

All thirteen direct application imports now resolve to compiled source in
native-dfu-startup-runtime.68 transitive unresolved imports remain visible,
including vector-to-bootloader setup, retained logging, device initialization,
sensor providers and event/database state. This aggregate has not executed as
a full provider graph. The locked frontier now contains742 tested contract
candidates,1,375 compiled hints and1,209 unresolved routes across3,326 rows.
Full source/data closure, original compiler and placement, all supervisor and
hardware contracts, and byte-identical whole-image rebuilding remain open.


The vector-to-bootloader setter now compiles from the unchanged registered
Nordic SDK 17.1.0 nrf_dfu_svci.c. An isolated logging macro header generates
padded ring/Nordic string pairs and forwards to small recovered R1 C logging
ports. The upstream MBR/UICR fallback, missing-address result and SVC19 return
algorithm remain unchanged. REA reports the exact contiguous 202-byte native
body; Ghidra-MCP reads match that body and 272 constant bytes. Of these, 264
string bytes survive selection; the raw source port's 8-byte bounds pair folds
into the log tag and is not claimed as selected linker placement.

The setter and actual linked source DFU graph pass 77,568 comparisons: 61,440
setter calls and 16,128 complete initialization workflows. This includes
703,230 callback/read observations per side, 5,352 SVC0 calls and 70,764 SVC19
calls per side. The native and source graphs agree on MBR precedence, UICR
fallback, both-addresses-missing result 4, zero/one/unaligned/high-bit address
values, boot-read order, short-circuit logging, early errors, async-state
mutation, raw R0, callee/SP preservation and full non-stack RAM. Low flash and
UICR values, supervisor handlers and logger bodies are explicit fixtures;
this establishes no physical boot transition or device provisioning state.

The source DFU subgraph has four logging imports, with vector setup no longer
a fixture. The larger startup bundle retains all thirteen direct application
imports resolved and now has 67 transitive unresolved imports. Its full
provider graph has not executed. The frontier contains 743 tested contract
candidates, 1,374 compiled hints and 1,209 unresolved routes across 3,326 rows.
Source/data closure, physical supervisor implementation, raw ABI/private
frames, final state/link placement, original compiler and whole-image byte
identity remain explicit gates.


Native YHM pre-initialization and the paired GXT310 self-check now compile from
recovered R1 C. The YHM implementation preserves a material distinction from
the older generic yhm2710_configure helper: native code ignores all five write
results and returns zero after chip ID 0xa0, whereas the generic helper returns
5 when a write fails. The generic helper remains historical and is not linked
as this native provider. No exact licensed vendor YHM/GXT source is inferred.
The new void adapter serves the previously compiled startup thunk while keeping
the native uint32 result body explicit; its sampled raw R0 is also tested.

The new receipt covers 110,424 comparisons: 40,448 YHM configuration cases,
3,840 void-adapter cases and 66,136 GXT self-check cases. It includes all 256
8-bit YHM chip IDs, all 65,536 8-bit GXT ID pairs, selected high-word values,
logging mode queues, failed write returns and callback mutation of the reused
write byte. The native and source calls agree on arguments/order, raw R0,
callee registers/SP and full non-stack RAM. There are 1,099,978 callback
observations per side, 44,840 write calls and 448,400 delay calls per side.
Success makes exactly 50 delay calls with 64000; chip mismatch writes nothing
and delays nothing. GXT always acquires/enables, reads both IDs, disables and
releases before returning its two-ID comparison. Providers are named fixtures
in these tests; private write-buffer addresses are normalized to byte contents.

Ghidra-MCP authenticates 224 YHM code bytes, 46 GXT code bytes and 124 data bytes.
REA has no procedure records for these entries, retained explicitly. Source
strings/bounds comprise 120 bytes, plus a four-byte source delay-function
relocation; no executable address fallback is introduced.

The larger startup candidate links existing source YHM write, handle discovery,
initialized context/request state and delay providers. Full execution of this
larger graph remains unverified. It resolves three old imports (pre-init,
self-check and handle discovery) and exposes seven deeper chip/GXT providers,
so total transitive unresolved imports rise from 67 to 71. All thirteen direct
application imports remain source-linked. The frontier now has 745 tested
contract candidates, 1,374 compiled hints and 1,207 unresolved routes across
3,326 rows. Leaf provider execution, physical bus/sensor/timing behavior,
complete raw ABI/private frames, source initialization and final placement,
original compiler and byte-identical whole-image reconstruction remain open.


The native YHM chip-ID provider at 0x3530c now compiles as recovered R1 C with
120 bytes of source-owned strings and log bounds. It initializes the read byte
to zero, requests register 8/length 1, ignores the read result, selects success
or failure messages from the initial byte and returns a reload of that live
byte after logging. No licensed vendor-source attribution is inferred.
Ghidra-MCP reads match all 134 code bytes and 120 data bytes; REA lacks a
procedure record at this entry and that absence is retained.

The new 98,304-case receipt compares 466,560 callback observations per side.
All byte IDs are covered with four fixed logging-mode queues; selected byte
values and an unwritten read cover all mode triples 0..7 plus seeded full-width
modes, three read-status values, scoped callback byte mutations and two RAM
fills. Return values, typed arguments, call order, callee/SP state and the full
observed non-stack RAM region match. The read pointer's private stack address
is normalized. The tests distinguish message selection from the later returned
byte and confirm that a read provider leaving the buffer unchanged returns
zero regardless of status. All read/logger bodies remain fixtures here.

The larger source startup bundle now links this provider and the existing
native YHM read frontend/transport together with source write, discovery,
initialized context/request state and delay. This graph has not executed as a
whole. All thirteen direct application imports remain resolved; transitive
unresolved imports fall from 71 to 70. The locked frontier is 746 tested
contract candidates, 1,374 compiled hints and 1,206 unresolved source routes
across 3,326 rows. Actual bus/sensor/timing behavior, provider graph execution,
full raw ABI/private frames, source state/data ownership and final placement,
original compiler and byte-identical image integration remain open.


The GXT310 shared chip-ID reader and channel 0x90/0x94 veneers now compile from
recovered R1 C. Ghidra-MCP bytes match the 96-byte shared reader, both six-byte
veneers and 100 data bytes. REA identifies the shared body and lacks records
for the veneers; both results remain explicit. A separate REA boundary inquiry
confirms that the power-down ownership row contains an 18-byte wrapper plus a
106-byte shared mode body. That row is not promoted by this ID-reader work.
No licensed vendor implementation or new upstream attribution is inferred.

The reader matches the entire native four-byte zero-initialized word, requests
register 3/length 2, ignores the read result, logs a big-endian 16-bit snapshot
and reloads the first byte after callbacks for its return. The source veneers
retain explicit tail relocations to the shared source reader. The first
candidate used a two-byte local array; it was strengthened before admission,
and its source, drivers, objects, reports and receipts are retained under
initial-two-byte-candidate with a hash manifest. Final receipts bind the
four-byte-word source and strengthened initial-zero assertions.

Direct verification passes 137,536 cases and 650,968 callback observations per
side: 123,136 shared-reader cases and 7,200 per veneer. Every 16-bit read word
is exercised, with additional ignored-error, unwritten-buffer, full-width
address/mode and scoped callback-mutation cases. The ring logger's fifth
argument is checked on the stack. The packed log snapshot stays fixed while
the late first-byte return reflects valid in-scope callback changes.

Another 44,096 workflows and 591,498 callback observations per side execute the
actual source self-check, both veneers and shared reader together. They verify
both reads, late-byte success decisions and acquire/enable/read/read/disable/
release order. Bus, enable/disable, lower register-read and logging providers
remain fixtures in this subgraph. Source strings occupy verification addresses;
the raw source object's eight-byte bounds pair folds into the log header and
is not selected graph data, leaving 92 selected data bytes. Full private-frame
addresses, saved-register placement and padding outside the word remain open.

All thirteen direct application imports remain source-linked. Replacing both
ID leaves with source and exposing one lower register-read import reduces
transitive startup imports from 70 to 69. The frontier now has 749 tested
contract candidates, 1,374 compiled hints and 1,203 unresolved source routes
across 3,326 rows. Full startup execution, lower provider bodies, physical bus/
sensor behavior, raw ABI, source initialization/link placement, original
compiler and byte-identical whole-image rebuilding remain explicit gates.


Seven native GXT/I2C2 bus entries now compile from recovered C: cached handle
lookup, lock/unlock, read/write request construction and the two forwarding
veneers. REA identifies all seven exact body ranges, totaling 118 code bytes;
Ghidra-MCP matches those bytes, five pointer literals (20 bytes) and the
8-byte i2c_2 name. No new vendor-source attribution is inferred. The existing
recovered registry header supplies the shared device/dispatch interfaces.

The source state uses checked C field offsets: address at request+0, register
at+2, write pointer/length at+4/+8 and read pointer/length at+12/+16. Its C
initializer reproduces 24 authenticated cold RAM bytes: zero device pointer,
address 0x12, both lengths 1, and all other observed bytes zero. This slice is
bound to the previous verified scatter/decompression observation; it does not
promote the whole initialized-data image to source-owned data or establish
final symbol boundaries/link placement. The source name adds eight bytes.

All 69,340 comparisons pass, including 69,644 registry callback observations
per side. The receipt covers scalar truncation, exact field store order,
unconditional read-pointer replacement, NULL write-pointer preservation,
zero-status success inversion, repeated cache lookup/reuse, callback mutation
of the handle and untouched padding, and persistent multi-call sequences.
Raw R0, callee registers/SP, callback arguments and full observed non-stack RAM
match, with executed-store observation reconciled against independent readback.
Registry lookup/dispatch are named fixtures in these body tests.

An initial passing build inlined the two veneers. The audit detected the lost
four-byte forwarding structure; core noinline declarations restore explicit
R_ARM_THM_JUMP24 tail relocations. Source, objects, report and passing receipt
from the superseded build remain hash-bound under initial-inlined-candidate.
The final build passes the same 69,340-case suite and tail-relocation audit.
This is source call-structure evidence, not final native instruction equality.

The larger startup candidate links these bodies with the existing source
registry. Cache, lock/unlock and the lower GXT read import now resolve, reducing
transitive imports from 69 to 65. All thirteen direct application imports remain
source-linked. The frontier is 756 tested contract candidates, 1,374 compiled
hints and 1,196 unresolved routes across 3,326 rows. GXT mode enable/disable,
other provider bodies, physical I2C/sensors, actual full startup execution,
raw private ABI, source state/link ownership, original compiler and byte-identical
whole-image rebuilding remain explicit gates.
