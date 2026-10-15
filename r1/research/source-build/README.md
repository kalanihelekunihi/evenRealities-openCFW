# R1 source compilation checkpoint

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
