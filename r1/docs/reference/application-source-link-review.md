# R1 source application final-link review, 2026-11-11

## Current source-link checkpoint

The latest R1 source receipt is
`build/sources-r1-eabi-agc-signed-20261111/report.json`: 963/963
application and 82/82 bootloader units compile, with no failures or duplicate
strong symbols. The strict application receipt
`build/r1-link-eabi-agc-signed-20261111/report.json` links with zero
undefined references, a complete 512-byte vector at `0x27000`, and 694,200
of 696,320 flash bytes used. The strict bootloader receipt
`build/r1-boot-link-eabi-agc-signed-20261111/report.json` also links with
valid vectors, 16 KiB heap and MSP reservations, and no undefined references.
The boot RAM layout gate rejects a 4 KiB MSP candidate under ignored
`build/r1-boot-stack-negative-20261111/`. No retained stock executable
region enters these links. The NADT root passes bounded direct and calibrated
replays through 100 fresh input calls at 25, 50, 100 and 200 Hz; runtime memory peak
and physical-device execution remain unverified.
The relinked `.bss` ends at `0x2003c570`, 1,720 bytes beyond the old stock
MSP vector word `0x2003beb8`. The application C vector now uses the GNU
linker's RAM top `0x20040000`, and its C source reserves an 8 KiB MSP stack.
The linker records `__StackLimit=0x2003e000`, `__HeapLimit=0x2003c570`, and
6,800 bytes of RAM between static data and the reserved stack. The strict
link validates those bounds and matches the vector's initial SP to
`__StackTop`; this checks static placement, not worst-case runtime stack use.
An ignored negative link at `build/r1-stack-negative-20261111/` replaced only
the vector source with the old MSP constant. GNU ld still resolved all
symbols, but the strict image check rejected it because `0x2003beb8` lies
inside `.bss`. The production image differs from the previous raw image at
the vector word and two CmBacktrace stack-limit relocations.
Both final-link scripts now reject participating inputs that are not `.c`
files under `r1/src`, the pinned vendor/upstream trees, or the build's
generated R1 source directory.
The passing receipts bind 941 application and 82 bootloader participating C
units to their source and object hashes; the application map contains no
archive members. Deliberately changing either source report to a `.S` input
or the legacy `r1/research/source-build/` path made its final link fail before
invoking the linker. This provenance check
does not prove that each source function behaves like stock firmware.
The Goodix SpO2 configuration previously came from an ignored legacy
research directory. Its canonical C owner is now in `r1/src`, with the same
compiled object bytes. The bootloader public key now compiles from its
existing identical `r1/src` copy; the unused application copy was removed
from the manifest. That consolidation retained the previous image hashes
before the later MSP correction.
The strict link scripts now produce raw region images after validating the
source-linked vectors and flash/RAM bounds. At the earlier NADT checkpoint,
the app receipt
`build/r1-link-nadt-history-ordinal-20261111/report.json` records a 694,244-byte image at
`0x27000`, SHA-256
`2c3bf3d374eb1df387c8bf0ae942e983420065b69c814d7de8460c4f26c579ab`.
The boot receipt `build/r1-boot-link-nadt-history-ordinal-20261111/report.json`
records a 23,024-byte region at `0xf8000`, SHA-256
`08e108776638ad4feaf2eada3861ab37d587b44ae3b5b75daacfa386ea67ac67`.
It separately dumps and checks the four-byte UICR values: `0x000f8000` at
`0x10001014` and `0x000fe000` at `0x10001018`. The raw bootloader export
excludes those distant UICR addresses and the NOLOAD settings/MBR pages.
The S140 7.2.0 SoftDevice and MBR occupy `0x00000..0x26fff` in the R1
memory map and remain a pinned Nordic binary, outside these C source links.
Nordic's [SoftDevices documentation](https://docs.nordicsemi.com/r/bundle/ug_gsg_ses/page/ug/gsg/softdevices.html)
describes SoftDevices as qualified precompiled binaries; the current SDK does
not supply a C source implementation of S140 to add to this build.
Thus the checked application and bootloader regions are C compiled, while a
whole-device image made entirely from C has not been established. The
[current SVC inventory](s140-source-dependency-inventory.md) finds 54 distinct
Nordic S140/MBR service numbers in the two linked ELFs; source-built SVC
wrappers do not replace those vendor service implementations.
The boot linker now verifies every participating source hash, including its
generated uECC source; a mutated generated-source hash is rejected before link.
The application formerly pulled Newlib's `libc_a-strcpy.o` for two Segger RTT
ID copies. The existing C libc sequence unit now supplies `strcpy`; the final
map has no archive members, and the linker receipt gates that property. A
focused host check covered empty and nonempty strings, return pointer,
terminator and adjacent sentinel bytes. The application image shrank by 128
bytes; this does not imply stock instruction or output identity.
These artifacts do not include the SoftDevice or package metadata and have
not been tested on hardware.
The [sparse source-region exporter](source-region-hex-review.md) now combines
the checked application, bootloader and UICR bytes in Intel HEX without
filling or claiming ownership of the excluded flash regions.
There are 21 `__asm__` tokens across seven R1 C/header files, so the
assembly-free source gate remains open. The Goodix wear hook no longer uses
register-bound assembly; its isolated four-register C frame passes 3,840
policy and 768 integrated stock/C cases, with all other generated hook bodies
unchanged. The GoMore packed consumer's frame bridge now uses C allocation
and passes its base and later chain replays. The Goodix I/O dispatcher is now
isolated in its own C unit and passes 492 dispatcher and 432 integrated
callback cases; its fixed-frame transfer remains assembly. The
[Goodix root integration gate](goodix-final-root-integration-gate.md)
documents the native binding and focused checks.
An ordinary C probe of the live software-TWI delay wrapper under ignored
`build/r1-delay-pure-c-20261111/wrapper-single.c` emits `CBZ`, `LSLS` and a
direct tail branch. The current wrapper emits `CMP`, `BEQ`, `LDR`, `LSLS`,
`BX` and `BX LR`. The probe changes zero-input APSR flags and branch timing;
it is not admitted as a timing-equivalent replacement. The application also
has four source-level `__builtin_trap` assertion endpoints. Those compile
from C, but the stack-fault behavior of the stock assertion paths has not
been reproduced. Neither a clean link nor a sparse source HEX resolves the
external Nordic S140/MBR binary or establishes physical boot.
The [NADT root replay review](goodix-nadt-root-replay-review.md) records
480 paired early-return cases, 32,000 paired calls across fresh direct
and calibrated sequences, and 128 varied-initial-state one-call pairs. Longer
varied-state sessions show 46 mismatches in 128 cases under unmodified
Unicorn. A diagnostic replay that clears stale Thumb ITSTATE after the
source classifier's `it ne` block passes all 128 sessions of 100 calls;
the production ELF is unchanged. Wider configuration and native-state
coverage remains open.

The remaining assembly sites have distinct contracts: the Goodix I/O
transfer preserves a 216-byte provider frame and callback register state;
the RTT and software-TWI delays depend on cycle timing and flags; the
divide-zero helper depends on the Cortex-M `DIV_0_TRP` setting; fault vectors
read the exception LR/SP; and an unlinked binary64 comparison candidate
marshals APSR flags. The event profile
callback and stream logger now preserve their raw ARM register handoffs
through C `musttail` calls. Both compile to their prior four-byte branches;
the linked application image is unchanged
([logger review](stream-rate-reduce-logger-tail-c-review.md),
[event review](event-profile-update-c-review.md)).
The [EABI division closure](eabi-divmod-register-return-review.md) removes
every R1 divmod EABI call site and both handwritten register adapters. The
strict image is unchanged by adapter removal because neither section was
live in the preceding link. A subsequent signed Goodix AGC correction keeps
the application image at 694,196 bytes, SHA-256
`6ca24db9ec3209c9abd20858fede662b368f84ea8be5bb0cfb698b6b9f405068`.
The later [Cordio clock-owner review](cordio-nrf52840-source-candidate.md)
found that the SDK example's legacy `CLOCK_CONFIG_LF_SRC=1` overrode the
recovered R1 `NRFX_CLOCK_CONFIG_LF_SRC=0` through `apply_old_config.h`.
Correcting the alias to RC and adding the opt-in Cordio clock PALs compiles
all 973 application and 85 bootloader
units; both strict source links pass. The current application image is
694,228 bytes, SHA-256
`653b09e3d0a52402db2fb4cde65320418954d1a569e9bf4908688127840340c6`,
with 6,800 bytes of RAM headroom. The bootloader remains 23,024 bytes,
SHA-256 `08e108776638ad4feaf2eada3861ab37d587b44ae3b5b75daacfa386ea67ac67`.
The current sparse-region verifier accepts 1,036 participating C sources and
emits only the application, bootloader and two UICR words in
`build/r1-regions-isolated-stock-20261111/r1-source-regions.hex`. The
opt-in R1 Cordio linker layout reserves former S140 lower flash and RAM
for the C controller; the default application image and its SHA-256 are
unchanged. The
sparse image explicitly
excludes S140/MBR, DFU settings, persisted flash and package metadata; this
is not an installable whole-device source image.
The `native_double_flags.c` comparison candidate is compiled from C but its
functions are discarded by the current application link (`application.map`
lists their sections at address zero). It accounts for assembly tokens in the
source scan, not executable bytes in the emitted application image.
`native_stack.h` also contains an unused SP reader. A current Clang
`--target=arm-none-eabi` probe under ignored
`build/r1-stack-builtin-c-20261111/` rejects GCC's
`__builtin_stack_save` as an unknown builtin, so that spelling does not
replace its Clang register binding. Clang's `__builtin_frame_address(0)`
adds a frame and reports its base, while `__builtin_alloca(0)` changes the
stack depth; neither is the same current-SP observation. A pure C RTT probe under
ignored `build/r1-delay-pure-c-20261111/` compiled either to a no-op,
arithmetic replacement, or a stack-backed loop with different timing; none
replaced the production cycle primitive. Each remaining boundary needs its
own ABI or timing evidence before removal.

The HR, SpO2, HRV and activity notification stages now run from C source.
Each passes 106 paired Cortex-M4 stock/C cases matching record operations,
time-window selection, FlashDB calls, packet fields, logging, allocation
failure paths, offline merging and cleanup. The replay found and corrected
two source defects before this receipt. The
[stage review](health-notification-stages-c-review.md) records the modeled
provider boundary and remaining validation. The assembler-only alias for
the event callback's interior string was also removed; its two relocations
now target the same C string with a 20-byte addend.

The profile update callback's former 352-byte literal assembly body now
branches directly to a C implementation. The C tail branch retains incoming R2/R3
fallback words at the public two-argument event ABI. Its 768 paired
Cortex-M4 stock/C cases cover admission, old/new log values, ordered payload
read widths and update arguments with filled and fallback records. The
[callback review](event-profile-update-c-review.md) states the modeled
boundaries and the raw ARM entry contract.
The event dispatcher now uses direct packed C loads for the record and
callback table entry. Its former `memcpy` calls clobbered incoming R3 before
that profile callback. The new source dispatcher matches stock callback
entry arguments and SP in 32 paired cases and passes 768 dispatcher-plus-
callback cases; the previous ELF fails the fallback-record negative control.
The [callback review](event-profile-update-c-review.md) records the current
receipt and modeled-provider limits.
The [device-ID reader replay](identity-shared-state-review.md) adds 168
cached/uncached stock/C pairs with destination and provider-argument checks.
The [time-sync command replay](time-sync-command-c-review.md) adds 256 pairs
covering payload admission, recovery routing, event bytes and logging modes.
Their controller, formatter and other lower providers remain modeled where
the individual reviews say so.

The activity refresh handler now receives the dispatcher's callback and
lower-bound words as typed arguments and constructs the eight-byte event in C.
Its flag branches and exact event bytes passed a focused host check. The
formatter's unbounded byte writer and stdout-byte callback also use C instead
of register bindings and a naked frame bridge. They still require stock-output
and device replay; the source link alone does not establish those behaviors.
The three daily cache notification loops now use a shared typed C logger.
Their header, sample-order and temperature-offset paths passed a focused host
check, and the linked app contracted by 576 flash bytes. Live cache contents
and actual log-sink behavior remain unverified.
The sleep report notification now passes its record explicitly from the C
event callback, logs its fields from C, checks the one-hour duration gate and
publishes the length derived from the stage count. Host checks cover the
duration boundary, publication length, failed-publication fallback and log
branches. The strict app link uses another 208 fewer flash bytes. Stock output
parity and device behavior have not been established.
The health GET dispatcher now logs and routes requests in C, updates its
notification timestamp, and assembles HR, SpO2 and HRV response bytes from the
source-owned template table. A host check covers valid and missing samples,
SpO2 admission, wire bytes, stage routes, no-data cases and the activity
event. The template table remains in the strict linked image. Stage-handler
behavior and stock-output parity remain separate checks.
The event publisher's naked stack bridge is now C. Its four-word queue record
has a defined zero padding word; the C event dispatcher reads the other three
words. A focused host check covers inline payload delivery, queue rejection,
allocation and allocation failure. Host pointer width prevents that check from
following an allocated queue pointer, and physical queue behavior remains
unverified.
The sleep wake timer callback now builds its eight-byte health request in C.
The receiving callback reads the first four bytes; a host check covers those
bytes, event width, timer release and state clearing. The diagnostic daily
fixture also uses C for its hour window, three cache kinds, random samples and
notification calls. Its day timestamp writes target the named cells after the
80-byte cache prefixes instead of forming out-of-bounds C pointers. A host
check covers all kinds, signed random remainders, timestamp cells and gating;
stock replay and hardware execution remain open.
The `sprintf` and `printf` entry wrappers now use Arm Clang's one-word
`va_list` cursor and call the existing C formatter cores. The actual Arm
objects spill `r2`/`r3` for `sprintf` and `r1`–`r3` for `printf` immediately
before passing the cursor, matching the former stack argument boundary. The
strict application link stays at 695,064 flash bytes. Format-output replay
and the old incidental return-register effects remain unverified.
Protocol ingress now uses C for header admission, ordered logging and module
dispatch. Its normal target lookup retains the native integer-address access;
the special module's host check covers rejection branches, ring/SDK arguments,
handle truncation and returned dispatch status. Normal table dispatch and
stock register residue still need target-level replay. The strict app link
uses 48 fewer flash bytes than the previous checkpoint.

## Earlier 946-unit link checkpoint

The remainder of this review records the earlier incomplete link and its
diagnostics. Its "current" and "latest" references below refer to that
checkpoint.

The strict application linker consumes the 946-unit application composition
and verifies its participating objects individually. It checks each object's and source's build
hash before invoking Arm GNU ld, and writes the exact command, input hashes,
map and diagnostics under the requested ignored build directory. The previous
single composed-object link hid 27 final-address registry boundaries.

The existing source-owned observer and log registry linker fragments still
define record order and size assertions for relocatable composition. The
final-link tool adapts those fragments into output sections in flash, plus an
initialized RAM log section after `.data`. Its generated scripts live only in
the link output directory. All registry-size and placement assertions in the
latest map evaluate true. The current R1-only build receipt is
`build/sources-r1-nadt-native-view-fixed-20261111/report.json`; the strict
application receipt is
`build/r1-link-nadt-native-view-fixed-20261111/report.json`.

| Gate | Latest result |
| --- | --- |
| R1 source manifest | 1,028 units, 815 source files, 0 unbuilt |
| Application composition | 946/946 units; no failures or duplicate strong symbols |
| Bootloader composition and strict final link | 82/82 units; link and 512-byte C vector valid |
| Application vector | 512 bytes at `0x27000`; reset defined |
| Application strict final link | 3 unresolved functions; 663,720 of 696,320 flash bytes used; no flash overflow |
| Reset data placement | FDS and dynamic log load-address assertions pass |

The missing functions are the three Goodix calculation roots. The SDK
authorization adapter now matches the stock cold-token path, two rejection
paths, and two timestamp extremes, as recorded in the
[auth review](health-sdk-auth-c-review.md). The reset-ring and
three role/manager assertion paths are now expressed as C logging followed by
a compiler fault intrinsic. This models their source-level terminal behavior;
it is not stock byte identity or hardware fault validation. The link still emits
mixed enum-size ABI warnings; these require a provider/caller audit before
hardware use. The current source graph fits the recovered flash span after
removing blanket retention from two large algorithm libraries. Future source
bindings may make more of their sections reachable, so final flash fit remains
unproven. The receipt uses `TotalFlashUsed`
from the SDK script, which includes initialized RAM sections; ld's
output-section region message alone understates the required flash. A linker
pass would establish neither
stock byte identity nor a safe hardware boot. The source reset now follows
linker-owned initialization bounds, but board execution remains unverified.

The source-only objective has a separate assembly gate: a current search finds
inline assembly or register-bound `asm` in 25 R1 C files. These include
exception/EABI entry bridges, private stack-frame adapters and timing loops.
The successful C compiler pass does not establish that those boundaries have
been replaced with ordinary C; each needs an ABI or timing review before
removal.

All child commands exposed by the linked BLE and factory legacy routers are
source-owned. The current unresolved roots are:

| Area | References |
| --- | --- |
| Goodix | `goodix_hba_calc`, `goodix_hrv_calc`, `goodix_nadt_calc` |

The [Goodix root integration gate](goodix-final-root-integration-gate.md)
records the existing typed cores and the remaining native state bindings.
The NADT root now has a [non-owning workspace view](goodix-nadt-workspace-view-review.md)
for the four production history banks; its live state and callback binding
remain to be implemented.

The [HBA diagnostic bridge](goodix-hba-diagnostics-c-review.md) removes the
`goodix_hba_essential_info_print` reference. Its log callback cells are
relocatable because the current source link places other state at the stock
RAM addresses.
The [health initializer bridge](health-engine-initialize-bridge-review.md)
binds stock `0x6fea0` to the existing typed C primitive and moves its engine
and output buffers into source-owned RAM. Its adapter and primitive probes
pass, while full stock replay and hardware behavior remain unverified.
The [random-state relocation](random-state-relocation-review.md) removes a
fixed stock RAM pointer that overlapped Goodix workspace in this link map.
The [STACMD delay conversions](stacmd-delay-intrinsic-c-review.md) remove
three inline assembly loops with Arm Clang C intrinsics. Their production
objects have the same dynamic instruction-address traces as the prior source
objects under the Cortex-M4 emulator; board timing remains unmeasured.
The [GoMore sleep stage binding](gomore-sleep-stage-binding-review.md) connects
the typed C stage and classifier to both source-owned model regions. Its
model descriptors and parameters are verified; full stock/C classification
replay and hardware behavior remain open.
The [shared GoMore authorization record](gomore-auth-record-owner-review.md)
now covers the parser's full 20-byte RAM status object. Stock startup and the
compiled C initializer match. The missing fourth field parser is now typed C
and passes 100 stock/host/Arm comparisons, including its seeded-random path;
authentication callback binding
remains unfinished.
The [reset PC probe conversion](reset-pc-probe-pure-c-review.md) replaces its
leaf inline assembly with a relocated C label address. The actual Arm object
matches the former probe's return, preserved registers and flags in nine
emulated cases; the linked probe stays eight-byte aligned.

The EAT initializer now uses a source-owned 37-entry command table; the
`AT^RESET_RING` callback still requires a C implementation. The GoMore sleep-stage
model is bound, while stock/C classification replay remains open. The assertion
transfers need an architecture-level C design and evidence; the stock path
executes a word on the stack. These are explicit gaps, not link placeholders.
`AT^RESET_RING` likewise emits five retained assertion messages and executes
`0xe7f00000` from the stack in ARM state. Replacing that fault path with a
normal reset would change its observable behavior; it remains unresolved
until its C fault/reset route is established.
The [fault-path review](eat-reset-ring-fault-path-review.md) records its
log arguments and stack-executed word.

The [legacy reply helpers](legacy-version-reply-c-review.md) at `0x62584`,
`0x62834`, `0x628ae`, `0x4e1f8`, and `0x62546` are source-owned. Their
2,048 selector cases and fixed response check pass. The
[BLE and factory routers](legacy-command-router-c-review.md) call these C
functions and make their child dependencies visible to the strict
linker. The router probe covers all 256 command bytes for each entry. The
[Goodix profile command adapters](goodix-profile-commands-c-review.md)
close two more reachable child imports after 512 selector cases. The
[ring-size command](ring-size-command-c-review.md) closes another after a
256-selector storage probe. The [address compare command](legacy-mac-compare-c-review.md)
closes one more after 257 selector/readback cases. The
[serial and BSN commands](legacy-serial-commands-c-review.md) close two more
after 512 selector cases. The [derived SN command](legacy-sn-derived-c-review.md)
closes another after 256 selector cases and an erased fallback check.
The [power configuration command](legacy-power-config-c-review.md) closes
one more after 256 selector cases and the signed-field probes.
The [touch long-press command](touch-long-press-command-c-review.md) closes
another after 256 selector cases and clamp/log boundary checks.
The [factory-mode subcommand](legacy-subcommand-c-review.md) closes another
after 256 selector cases and invalid-handle checks.
The [device-info command](legacy-device-info-c-review.md) closes another
after 256 selector cases and flash-geometry arithmetic checks. The current
R1-only source composition and strict R1 bootloader link pass. The
[pair command](legacy-pair-command-c-review.md) closes another after 256
selector cases and handle/guard checks. The
[factory aging stream](factory-aging-stream-c-review.md) closes another
after selector and 100-sample accumulation probes. The latest all-device
source attempt failed in G2 during concurrent G2 work; its R1 units passed.
The [system-control command](system-control-37-c-review.md) closes another
after a 256-selector probe, including the reset paths.
The [ATI calibration command](ati-calibration-command-c-review.md) closes
another after a 256-selector touch and task-message probe.
The [legacy 0xf2 dispatch](legacy-f2-dispatch-c-review.md) closes the last
router import after decoding its 72-slot RW table and probing all slots.
The [health GET encoders](health-get-encoders-c-review.md) replace three
naked assembly wrappers with C. The strict import count stays 13.
The [sleep storage iterator](sleep-sync-iterator-c-review.md) closes one
more strict import after an isolated storage probe. Its C implementation
raises flash use by 672 bytes and leaves 12 unresolved functions.
The [generic export transport dependencies](export-transport-c-review.md)
source-own the `0x32598` fragmenter and `0x4ca08` fast-connection path.
At that checkpoint the command had not yet been reconstructed. The
[source-owned export command](export-command-c-review.md) now reaches them.
The [export start and finish callbacks](export-guard-c-review.md)
source-own the descriptor's two guard transitions. The strict import count
remained 12 at that checkpoint. Preparation, reading and command dispatch
now have C owners, leaving 11 strict references.

The [sleep-stage refiner](gomore-sleep-stage-refine-c-review.md) closes the
native `0x81040` import after 312 paired stock/C cases using the actual
manifest Clang objects. It adds 2,416 bytes to the full flash use relative
to the previous 975-unit checkpoint. The strict bootloader link still passes.

The [dormant estimator stage](gomore-dormant-stage-c-review.md) closes native
`0x5feb8` and adds its record callback. Its 288 exercised mode-one cases all
match stock, while broader state coverage and board behavior remain unverified.
The two C units add 10,240 bytes of flash relative to the 976-unit
checkpoint.

The [accelerometer SPS candidate](gomore-sps-candidate-c-review.md) closes
native `0x5ef1c` after 1,344 paired stock/C cases using the actual manifest
Clang objects. It adds 2,808 bytes of flash relative to the 978-unit
checkpoint.

The [energy updater C binding](gomore-energy-stage-c-probe.md) closes native
`0x5f56c` after 1,396 paired stock/C cases, including populated state and all
six modes. It adds 8,168 bytes of reported flash use relative to the
979-unit checkpoint. The application still lacks 20 functions.

The [EAT TX callback registry](eat-tx-registry-c-review.md) adds source-owned
channel registration, its two stock defaults, and C RTT/BLE callback wrappers.
Four hundred randomized register comparisons match stock. The initializer
and command dispatch remain unbound, so the strict link stays at 20 missing
functions and flash use is unchanged.

The [activity FlashDB record merge](activity-flash-record-c-review.md) closes
the native `0x3c958` callback after 400 paired stock/C cases. It adds 568
bytes of flash use and leaves 19 undefined application functions.

The [heart-rate FlashDB record merge](hr-flash-record-c-review.md) closes
the native `0x40508` callback after 500 paired stock/C cases. It adds 496
bytes of flash use and leaves 18 undefined application functions.

The [HRV FlashDB record merge](hrv-flash-record-c-review.md) closes native
`0x41438` after 600 paired stock/C cases and adds 496 flash bytes. The
[SpO2 FlashDB record merge](spo2-flash-record-c-review.md) closes native
`0x446b4` after another 600 paired cases and adds 496 flash bytes. Sixteen
application functions remain undefined.

The [EAT command dispatcher and background task](eat-command-dispatch-c-review.md)
close the native `0x4f6f8` import and source-own the `0x3d7cc` enqueue and
`0x44ea0` task body. Their 1,300 paired stock/C cases pass. The strict link
now has 15 undefined application functions and uses 628,704 flash bytes.

The [GoMore source selectors](gomore-source-select-c-review.md) close two
native application imports. Their 1,831 paired stock/C emulator cases pass;
the additional C code increases full flash use by 320 bytes relative to the
prior 952-unit checkpoint.
The [GoMore accumulators](gomore-accumulators-c-review.md) close two more
imports after 1,244 paired comparisons; their C code increases full flash
use by another 112 bytes.
The [GoMore record table](gomore-record11-c-review.md) closes one more import
without duplicating the source-owned model data. It passes all 256 reachable
indices and increases full flash use by 48 bytes.
The [GoMore motion classifier](gomore-motion-classifier-c-review.md) closes
another import. Its 548 paired cases execute all 180 stock entry bytes and
increase full flash use by 48 bytes.
The [GoMore motion gate](gomore-motion-gate-c-review.md) closes another
import after 832 paired comparisons, all 352 stock entry bytes and an exact
72-byte weight-table check. Its code and weights increase full flash use by
104 bytes.
The [multicast callback tail call](subscriber-multicast-pure-c-review.md)
removes one handwritten assembly trampoline. Its compiled object is byte-for-byte
identical to the preceding assembly version; application link totals are unchanged.
The [subscriber callback tail call](subscriber-consume-pure-c-review.md)
removes a second handwritten assembly trampoline with another identical
compiled object. It also leaves application link totals unchanged.
The [sleep report request wrapper](sleep-report-wrapper-c-review.md) removes
one more handwritten assembly entry. The R1-only source build and strict
bootloader link pass; the application still has 32 missing functions and the
same 26,712-byte flash overflow.
The [short-row RAM cache merges](short-ram-cache-merges-c-review.md) close
three application imports after 5,535 paired cases over all 509 stock
instruction starts. Their shared C and log data add 1,128 bytes to the full
flash load relative to the 32-import checkpoint.
The [activity RAM cache merge](activity-ram-cache-merge-c-review.md) closes
another import after 1,312 paired cases over all 219 stock instruction
starts. It adds 872 bytes to the full flash load.
The [`atanf` C arithmetic](atanf-pure-c-review.md) removes two handwritten
assembly sites. Its 131,776 paired floating point cases pass; the current
incomplete link discards this routine, so its flash total is unchanged.
The [`atan2f` C arithmetic](atan2f-pure-c-review.md) removes four more
handwritten assembly sites. Its 212,096 paired cases pass; this routine is
also discarded by the current incomplete link.
The [`logf` and `log10f` C arithmetic](float-logs-pure-c-review.md) removes
five more handwritten assembly sites. Its 263,552 paired cases pass; these
routines are likewise discarded by the current incomplete link.
The [GoMore three-axis sleep motion adapter](gomore-sleep-motion-adapter-c-review.md)
closes one application import after 4,096 paired cases covering all 80 stock
instruction starts. The signed warmup-count correction and adapter add 64
bytes to the full flash load.
The [GoMore optical peak adapter](gomore-optical-peak-adapter-c-review.md)
closes another import after 1,024 paired cases covering all 55 stock
instruction starts. The empty-record correction and adapter add 64 bytes to
the full flash load.
The [GoMore sleep cycle adapter](gomore-sleep-cycle-adapter-c-review.md)
closes another import after 1,096 paired cases covering 182 stock instruction
starts. Source-owner latch, interval-record and policy-copy corrections plus
the adapter add 256 bytes to the full flash load.
The [GoMore activity-window adapter](gomore-activity-window-adapter-c-review.md)
closes another import after 2,048 paired cases covering 269 stock instruction
starts. The variability threshold correction and adapter add 128 bytes to the
full flash load.
The [mainline powf dispatcher helpers](powf-dispatch-mainline-c-review.md)
remove four inline-assembly sites after the 21,504-case probe and 4,224-case
normal-profile replay. The replacement adds 160 bytes to the full flash load;
the strict import count is unchanged.
The [packed consumer signaling comparison](gomore-consume-signaling-c-review.md)
removes another inline-assembly site after 1,537 paired cases. Its C FPSCR
helper and ordered multiply add 80 bytes to the full flash load.
The [double-log equality predicate](native-log-equality-c-review.md) removes
five assembly annotations from one source function. Its integer-key equality
is tested over 600,121 input pairs. The incomplete strict application link
still has 24 unresolved functions and 29,464 bytes of flash overflow.
The [SDK log and formatter size profiles](r1-log-formatter-oz-review.md)
reduce full flash use by 1,152 bytes, with the same 24 unresolved functions.
The [trig reducer and powf arithmetic helpers](float-core-helpers-pure-c-review.md)
replace twelve inline-assembly sites with C. Paired stock/C replays pass
15,246 trig reducer cases and 6,272 powf dispatcher cases. The added source
code increases full flash use by 16 bytes from the preceding size checkpoint.
The [powf zero comparison](powf-zero-compare-pure-c-review.md) removes the
remaining inline-assembly site in the reduced core. Its direct VCMPE/FPSCR
replay passes 33,344 cases. The C helper adds 96 bytes to full flash use.
The [DFU authorization C frame](dfu-auth-frame-pure-c-review.md) removes a
third assembly boundary. Its paired replay passes 6,746 core cases and 1,472
integrated dispatch cases; the strict application link totals remain unchanged.
The [DFU system-event and control-point C frames](dfu-backend-frames-pure-c-review.md)
remove two more assembly boundaries. The authorization replay still passes;
72 additional seeded system-event sequences compare active responses and SVC
parameters against stock. Application link totals remain unchanged.
The [GoMore numerical sleep score](gomore-sleep-score-c-review.md) closes one
more native import after 1,181 paired stock/C comparisons. The exact score
fixes increase the full flash load by 1,528 bytes.
The [GoMore interval and stage statistics](gomore-sleep-statistics-c-review.md)
close two more imports. Each passes 411 packed/unpacked paired stock/C cases;
together they add 96 bytes to the full flash load.
The [Goodix formatted logging hook](goodix-log-hook-c-review.md) closes one
upstream integration import and adds 64 bytes to the full flash load.

An ignored diagnostic linker script removed 19 deliberate vendor-module
`KEEP` roots while retaining normal reachability and registry roots. The
application still had the same 50 unresolved functions and ld reported a
192,792-byte output-section overflow, a reduction of only 27,200 bytes.
Dropping those roots alone
cannot make this image fit, and the experiment was not adopted as the firmware
layout. The largest kept module object contributions in the pre-optimization map were
Goodix primitives (156,478 bytes), GoMore primitives (130,644 bytes), model
data (112,840 bytes) and the quantized runtime (49,164 bytes); these counts
are output-section contributions, not proven removable code.

The shared `r1-application-6` profile now compiles its 13 reconstructed
vendor/checksum units with `-Oz`, function sections and data sections. An
isolated probe compiled all 13 and retained exactly the same exported symbol
sets. The authoritative 952-unit rebuild has no failures or duplicate strong
symbols, and its strict bootloader link passes. The application still has the
same 50 unresolved functions, while full flash overflow drops from 378,848 to
179,536 bytes. Moving zero-initialized heap, model workspace, stacks,
control blocks and scratch buffers into `.bss` then reduces full overflow
to 27,608 bytes. The reset copy now ends at `0x20009af8`; `.bss` starts there
and occupies `0x28aa0` bytes. The map's RAM limit and data-placement
assertions pass. A readback of the current application objects finds 82
`.bss.r1.*` input sections totaling 160,370 bytes, all `NOBITS`. Keeping all
vendor module roots leaves a 20,680-byte ld region
diagnostic. A broader ignored `-Oz` probe compiled 774 of 832 `-Os` units;
58 Arm GCC units rejected `-Oz`. Substituting the 774 successful probe objects
left the same 50 unresolved functions and reduced full flash overflow to
150,376 bytes at that earlier data layout. With the later BSS layout, an
ignored probe using 774 current/recompiled Clang `-Oz` objects fits the
configured flash span with only 1,552 bytes spare before the 50 missing
functions are implemented. A probe removing all vendor `KEEP` roots had much
more headroom, but it discarded unreferenced reconstructed functions whose
firmware coverage has not been audited; it was not adopted. The broad `-Oz`
probe is also not in the manifest; compiler and ABI regression checks would
be needed before adopting more profile changes.

## Sleep drop guard continuation (2026-11-10)

The wear sleep latch getter and final-record drop guard now compile from C,
with 512 paired stock/C branch and logging cases in
[sleep-drop-guard-c-review.md](sleep-drop-guard-c-review.md). The current
strict application report is `build/r1-sleep-guard-c-final-20261110/app-link/report.json`: 39 undefined symbols and 29,992 flash overflow bytes. The strict
bootloader link remains complete and vector-valid.

## Native interval selector continuation (2026-11-10)

The GoMore interval selector now builds from C and resolves one direct strict
application import. The [review](gomore-interval-select-c-review.md) records
576 paired stock/C cases. The current strict application report is
`build/r1-interval-select-c-20261110/app-link/report.json`: 38 undefined
symbols and 30,136 bytes of flash overflow. Bootloader linking remains
complete with a valid vector.

## Final sleep publication continuation (2026-11-10)

The final sleep serializer and event publisher now compile from C and resolve
one direct application import. The [review](gomore-final-sleep-c-review.md)
records 912 paired normal-domain cases and 12 high-bit stage cases with a
source-side allocation safety byte. The current strict application report is
`build/r1-final-sleep-c-revised-20261110/app-link/report.json`: 37 undefined
symbols and 31,432 bytes of flash overflow. The bootloader still links with
a valid vector.

## Floating point assembly continuation (2026-11-10)

Four inline-assembly occurrences were removed from the hourly average and
`roundf` source while retaining target behavior under the pinned Clang build.
The [review](float-assembly-to-c-review.md) records identical hourly average
function bytes/relocations and 2,225 paired stock/C roundf cases, including
FPSCR. The strict application link remains at 37 undefined symbols and
31,432 bytes of flash overflow; bootloader linking remains complete.

## Targeted Clang size profiles (2026-11-10)

The [flash profile review](r1-flash-oz-profiles-review.md) records an
additional 2,816-byte reduction in the strict flash load from 25 targeted
`-Oz` application units. The current application still has 37 undefined
symbols and 28,616 bytes of flash overflow. Source and bootloader builds
remain valid; hardware behavior and byte identity are not established.

## Factory and sleep sync callbacks (2026-11-10)

The [factory record dispatcher](factory-record-dispatch-c-review.md) now drains
the factory queue in C and exposes its distinct legacy command router. Its
165 paired stock/C cases pass. The
[sleep sync report callback](sleep-sync-report-c-review.md) now formats and
forwards sleep report metadata in C; 144 paired cases pass. It exposes the
lower sleep packet builder. The two additions exchange two higher-level
imports for their lower providers, leaving 37 unresolved functions. The
latest strict report is
`build/r1-sleep-sync-report-c-20261110/app-link/report.json`, with 28,984
bytes of flash overflow. The strict bootloader remains linked and vector-valid.

The [sleep sync packet and ACK chain](sleep-sync-packet-c-review.md) adds
source-built packet compression, both module 6 event-post paths and ACK
completion. Its paired stock/C checks cover 1,436 event-post, 1,480 packet
and 84 ACK cases. The ACK callback closes the chain's final direct import,
leaving 36 undefined functions and 30,232 bytes of flash overflow in the
latest strict application report.

## Additional size profiles with stable RAM sections (2026-11-10)

Fourteen selected application units now compile with `-Oz` and
`-mno-global-merge`. The second flag keeps the stock section names and
placement of private SDK state. An initial `-Oz`-only peer-observer probe
merged pinned RAM variables and failed its layout check; it was not adopted.
The selected no-merge objects have unchanged named data sections, exported
symbol names and sizes, and Arm ABI attributes apart from the expected size
optimization tag. Their C replay passes 3,300 peer-observer event cases,
3,122 Goodix algorithm-version cases, and 2,176 SpO2 cases across all 32 FP
modes. The other vendor and library units have not had device-level timing
validation.

The fresh manifest build reports 886/886 application and 82/82 bootloader
units compiled, with no failures or duplicate strong symbols. The strict
bootloader link remains complete and vector-valid. The strict application
still has 36 undefined symbols, while full flash overflow falls from 30,232
to **25,064 bytes**, a **5,168-byte reduction**. A temporary-object link
initially suggested a larger saving, but its hashed filenames bypassed an
object-name wildcard in the recovered linker script. The fresh manifest link
is the authoritative size measurement. The source reports and link maps are
under `build/r1-oz-no-merge-final-20261110/`; this is not a complete or
byte-identical application image.

## Health event consumers in C (2026-11-10)

The [six health event consumers](health-event-consumers-pure-c-review.md)
now use C rather than handwritten naked assembly. Their 1,440 paired
stock/C cases pass, including gate boundaries and live timestamp updates.
The strict application still has 36 undefined symbols and now exceeds flash
by 25,160 bytes, 96 bytes above the preceding checkpoint. The bootloader
link remains complete and vector-valid.

## Health sync acknowledgements in C (2026-11-10)

The [four health sync acknowledgement callbacks](health-sync-ack-c-review.md)
now build from a shared C helper. Their 7,644 paired stock/C cases cover
cursor, FIFO, logging and live provider-mutation paths. The strict
application loses four imports, leaving 32 undefined symbols. These C
functions add 1,552 bytes to full flash load, which now exceeds the
configured span by 26,712 bytes. The bootloader link remains complete and
vector-valid.

## Current size and assembly checkpoint (2026-11-10)

The [final-sleep size profile](gomore-final-sleep-c-review.md) saves 352
bytes of strict flash load after 912 paired stock/C cases and 12 documented
high-bit cases. The [double-round C comparison](double-round-comparison-pure-c-review.md)
removes two inline assembly call sites after 2,624 compiled old/new pairs and
saves another 16 bytes. The [algorithm-library reachability change](application-library-reachability-review.md)
then saves 121,504 bytes in the current source graph without changing its
24 unresolved functions. The [shared binary64 C comparison](binary64-comparison-c-review.md)
removes 20 more inline-assembly occurrences after 65,824 direct comparisons;
the current source graph uses 602,776 of 696,320 flash bytes. The strict
bootloader links, and the R1 manifest has zero unbuilt units.
