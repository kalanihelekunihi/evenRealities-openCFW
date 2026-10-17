# R1 upstream reuse and reverse-engineering tools

The reconstruction target remains R1 2.2.6.0009. Build attributable upstream
bodies directly at the proven or compatible pin; keep product glue and
configuration in R1-owned files. Future dependency upgrades belong to a separate
maintenance build, with behavior and image differences measured against this
locked reconstruction baseline.

## Source reuse map

| Dependency | Baseline and evidence | Reuse / remaining work |
|---|---|---|
| [nRF5 SDK](https://developer.nordicsemi.com/nRF51_SDK/nRF5_SDK_v17.x.x/) | 17.1.0 `ddde560`; archive hash in `third-party/fetched/manifest.json`; `toolchain-and-dependencies.md` | Candidate bootloader compiles 74 units and links. Reuse BLE, nrfx, storage, DFU, crypto adapters and bundled RTT directly. Exact app configuration and ArmCC placement remain open. |
| [FreeRTOS-Kernel](https://github.com/FreeRTOS/FreeRTOS-Kernel) | `def7d2df2b0506d3d249334974f51e427c17a41c`, 10.5.1; `correlation/FREERTOS-KERNEL-VERSION-CORRELATION.md` | Reuse core directly with Nordic port. Do not substitute SDK's 10.0.0 core. Candidate configuration retains historical guesses and an obsolete delay-API workaround; derive a separate stock-supported configuration before integration. |
| [CMSIS-FreeRTOS](https://github.com/ARM-software/CMSIS-FreeRTOS) | `d213f261b5be6bb29a7cce8b84071706b72f4d53`; same version correlation | Initialized at existing gitlink. Reuse wrapper bodies and isolate R1 OS hooks. Wrapper compilation now passes in the 12-unit RTOS audit; full application integration remains open. |
| [FlashDB / bundled FAL](https://github.com/armink/FlashDB) | `4e5677408256f82d47cd56a6b04605dcee35ed9a`; `correlation/FLASHDB-FAL-CORRELATION.md` | Seven upstream units compile directly. Keep seven-partition layout and device adapter R1-owned. Write granularity 32 is inferred; no-op logging is historical, not stock-proven. |
| [tiny-AES-c](https://github.com/kokke/tiny-AES-c) | `e72b6eff0884673997d0ca6385169bbd9b31936d`; `correlation/TINY-AES-CORRELATION.md` | `aes.c` compiles directly with ECB enabled and CBC/CTR disabled. Eight stock inverse-core functions identify lineage; exact original checkout is not uniquely established. Two-pass chaining is product glue, not upstream AES. |
| [CmBacktrace](https://github.com/armink/CmBacktrace) | `73714489f9d8af130aacb515586b397b604a5768`; `correlation/CMBACKTRACE-CORRELATION.md` | Initialized at existing gitlink. Reuse diagnostic bodies; recover R1 log/exception-entry integration. Compile/integration pending. |
| Bosch BMA456, ST LIS2DW12 / ST25DVxxKC | archive/source pins in `third-party/fetched/manifest.json`; sensor correlation notes | Reuse authenticated sensor APIs. Separate register profiles, bus binding and product policy from driver bodies. |
| Goodix GH3X2X democode | `third-party/upstream/goodix-gh3x2x`; fetched manifest and `boundaries/GOODIX-DEMO-DRIVER-MAPPING-2026-08.md` | Reuse admitted driver/configuration subset. Public democode does not establish source availability for private HR/SpO2/HRV algorithms. |

GoMore, Bravechip platform bodies, private Goodix algorithms, Nordic S140/MBR,
and Oberon/CC310 source remain separate unresolved/provider gates. A package
containing a binary library does not establish C-source availability.

## Verified tool usage

REA opened the locally built ARM bootloader ELF with Ghidra 12.1.4 and produced
a function dossier for `crc32_compute`. Ghidra-MCP 7.0.0 imported the same ELF in
a separate headless project and queried its signature, pseudocode, calls and
body. Both observed entry `0x000F83A8`, 56 code bytes and ten callers. The
candidate's CRC is reflected IEEE (`0xEDB88320`, complemented seed/output),
whereas the application's separately authenticated `0x0005D8A4` uses
non-reflected Castagnoli and caller-owned state. They must not be merged based
on a CRC name alone.

Receipts are under `r1/research/source-build/`:
`rea-crc32-dossier.json`, `ghidra-mcp-crc32-dossier.json` and
`tool-crosscheck.json`. The tool agreement is not independent semantic review:
both adapters use Ghidra. These observations describe the candidate ELF, not a
stock bootloader capture. REA's generic artifact-authority label does not
change that provenance.

For subsequent functions, use REA dossiers for complete body ranges, CFG and
references; use Ghidra-MCP for targeted type/xref/provider correlation. Bind
all observations to the image hash and correct load address. Preserve explicit
unresolved indirect targets. Use authenticated stock execution and upstream
compilation to test hypotheses rather than counting decompiler text as C.

## Build and maintenance rules

`python3 r1/tools/build_public_providers.py` checks initialized submodule pins
and clean trees, compiles the original source files to Cortex-M4F objects and
records source hashes, commands, symbols and configuration limits in
`r1/research/source-build/public-providers/report.json`. The run compiled eight
units. It does not establish the application's source closure or byte identity.

Keep upstream trees unmodified. Put recovered configuration and any necessary
patches in R1-owned files with stock evidence and explicit confidence. When an
upstream improvement is adopted, record old/new pins and the intended fix,
rebuild its consumers, compare behavior and bytes, and preserve the locked
baseline's results. Do not silently advance dependency pins to make a build pass.

The RTOS candidate build now compiles the pinned 10.5.1 core and CMSIS wrapper directly. Exact configuration remains gated by the 92-byte candidate TCB versus the stock 112-byte reservation; see `r1/source-config/rtos/README.md`.

The application-side SDK target now compiles 64 nonempty units directly from
the authenticated Nordic tree, with the later correlated BLE/DFU, logging,
power and nrfx sources included. The R1-owned candidate configuration corrects
the RTT down-buffer size and preserves the proven TIMER2/TIMER4 selections.
Remaining example defaults and Clang-only operand adaptations stay explicit in
`r1/source-config/sdk/README.md`; they do not advance stock byte-identity gates.

Five Bosch/ST sensor API units now compile at their authenticated declared pins. R1 ST25 bus veneers compile and pass bounded stock comparisons, while actual board/resource integration remains open. A differing LIS2DW12 checkout is preserved by materializing the declared pin from Git objects rather than moving the checkout. See `r1/components/st25/README.md`.

The software-TWI GPIO callbacks now consume Nordic `nrf_gpio.h` directly through
six thin R1 wrappers (`r1/components/software-twi/sdk_gpio.c`). The builder
checks every consumed vendor header against the authenticated SDK archive and
records all transitive input hashes. All 24 original callback copies pass
4,608 bounded MMIO comparisons. Preserve this direct upstream relationship:
adopt a later HAL fix through an explicit dependency update and rerun these
comparisons; do not duplicate the register implementation into product code.
The SDK source is attributable, while stock instruction identity, native
callback relocation, physical wire behavior and delay-provider closure remain
separate gates.

The TWI delay callbacks need a separate recovered contract: stock i2c_2/3
scale by 64 and call subtract-three loops, while i2c_4/5 use no-op bodies.
The current SDK's DWT-based delay is not a stock substitute. The local C work
loop and no-op compile and pass arithmetic/termination comparisons; exact
cycles and real elapsed timing remain unproven. Keep these source bodies
separate from the directly reused Nordic GPIO HAL.

The board memory/string candidate now consumes an unchanged musl v1.2.5 subset
at commit 0784374d561435f7c787a555aeab8ede699ed298, with primary/mirror tag
agreement, per-file hashes and the full upstream COPYRIGHT. A narrow R1 endian
bridge and EABI wrappers keep upstream bodies directly replaceable. Adopt fixes
through an explicit pin update and rerun runtime/consumer stock comparisons;
do not treat this candidate as original Arm library identity. The board oracle
now needs no binary C runtime, while other runtime/math and exact-image gates
remain open.


## LLVM integer runtime candidate

R1 reuses unchanged `udivmoddi4.c` and its headers from LLVM compiler-rt
20.1.8, commit `87f0227cb60147a26a1eeb4fb06e3b505e9c7261`. The existing shared
cache stays unchanged; `r1/source-config/runtime/llvm_integer_provenance.json`
authenticates these files against the immutable upstream commit and retains the
compiler-rt-specific license separately. Keeping nonzero arithmetic upstream
allows later compiler-rt updates to be evaluated without rewriting the R1 ABI
or stock edge behavior. An update requires fresh hash authentication and the
stock differential oracle; no automatic improvement or equivalence is assumed.

`r1/components/runtime/integer_eabi.c` supplies the EABI quotient/remainder
register glue and recovered zero-divisor and extended shift-count contracts.
Four entries pass 50,822 comparisons; 211 WDT SDK cases also execute the real
C division provider. These are attributable replacements, with original Arm
runtime source/compiler identity and whole-image byte equality still gated.


## Nordic SoftDevice NVIC source selection

R1 selects the unchanged SDK 17.1.0 `app_util_platform.c` critical-region
wrappers and the inline S140 `nrf_nvic.h` implementation, with all SDK source
and included headers authenticated against the pinned SDK archive. The selected
object owns just the two tested functions and 12-byte NVIC state. Keeping the
upstream functions unchanged makes later upstream fixes reviewable separately
from R1 address placement and stock-equivalence tests. Stock runtime contracts
pass 52,464 comparisons. The whole firmware remains locked to its original
baseline; updated SDK semantics require a fresh differential evaluation.


## WDT integration policy and error strings

The unchanged Nordic WDT source now has a separate R1-only nrfx log header.
It recovers mode gating, short-circuit/trailing reads and exact INFO descriptor
placement without patching upstream driver bodies. Upstream changes remain
reviewable against this small integration boundary; the header is supported
only for the authenticated WDT call sites. All mode bytes and 512 transition
sequences pass stock comparison. Other SDK adapters still require evidence.

The unchanged Nordic `nrf_strerror.c` provider also matches every one of the
37 stock error-code/name entries and passes 139,272 lookup/fallback comparisons.
Reusing its search/table source avoids a manually maintained substitute table.
Both variant units and their SDK headers are archive-authenticated by
`r1/tools/build_watchdog_logging.py`; source licenses remain with the SDK files.


## BAE8 dual-notification send

The R1 BAE8 send adaptation retains the Nordic NUS source license and uses the
pinned SDK's real HVX parameter type and SVC identifier. Its SDK headers and
`ble_nus.c` reference are archive-authenticated by
`r1/tools/build_native_bae8_send.py`. R1-specific dual enables/handles, log
routing, return policy and 244-byte cap stay local; the whole proprietary
service is not replaced by a generic `ble_nus_t`. This keeps upstream type/ABI
changes reviewable while preserving the locked R1 contract. The actual
`blcm_link_ctx_get` implementation in SDK `ble_link_ctx_manager.c` is the next
unchanged provider route; full service storage and connection-state configuration
still need authenticated bindings. Subsequent SDK upgrades require rerunning
the stock differential oracle and do not change the locked reconstruction pin.


## Link-context manager source reuse

The pinned SDK's `blcm_link_ctx_get` is now linked unchanged through a direct
R1-to-SDK symbol alias, with included SDK files archive-authenticated. Its
37,154 stock comparisons and BAE8/output-chain integration receipts separate
upstream lookup behavior from R1 service/storage configuration. Future upstream
changes can be reviewed at this small boundary and tested without maintaining a
local search/offset implementation. The connection-index provider and real
storage/context pool ownership still require evidence; upgrades do not alter
the locked reconstruction baseline automatically.


## Connection registry read/reset subset

The unchanged Nordic connection-state and atomic-flag source now supplies index,
validity, flag read, reset and init from a single selected SDK state instance.
Included SDK files are archive-authenticated. Stock reset code independently
establishes the 124-byte clear span; remaining field semantics and event writers
still need evidence. Read/reset tests and lookup/BAE8/output composition receipts
allow later upstream changes to be evaluated at the source boundary. Extend this
selected instance when adding writers; do not link a second full connection-state
object beside it. The live registry, service/pool configuration and hardware
concurrency remain separate from deterministic bitmap fixtures.


## Registry event and atomic source

The selected connection-state instance now includes its event writer and
unchanged Nordic atomic/flag dependencies, rather than a parallel local bitmap
implementation. R1's returning CONNECTED-error policy lives in a small header;
SDK source remains unchanged. The static callback and typed observer record
are exposed through recorded object-symbol transformations. Their source owner,
license, reset span and event/atomic comparison receipts stay attributable.
Extend this one instance when adding APIs; do not link another registry object.
Upstream updates require fresh event, exclusive-retry, read/reset and
lookup/BAE8/output composition tests. Native dispatcher/priority ranges, service
pool configuration and real stack/hardware event delivery remain gates.

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


The latest-slot KV get policy at `0x95168` is now native C with14,049
stock-differential cases and an authenticated248-byte Ghidra-MCP body read
(`research/source-build/native-kv-store-get`). Its context/driver layout and
latest-slot, header/magic, byte-count and reload rules are product-specific.
Reuse remains at the attributable C memory/runtime and Nordic SDK boundaries;
a generic upstream storage replacement would not establish this binary contract.
Lower flash-driver identification, initialization and the write provider remain
open opportunities for further analysis. Full-image compilation is still gated.


The supplemental KV erase/write callback at `0x95304` is now C and linked to
the source port table, with7,232 native differential cases and an authenticated
292-byte Ghidra-MCP read. Its fixed4KiB erase loop, configurable write stride
and driver return policy remain native R1 logic. No attributable upstream
implementation has been established for this policy; lower-driver identification
and storage initialization remain the next reuse opportunities. REA's fresh
analysis did not discover this callback as a procedure; that limitation is
recorded beside the direct instruction evidence.


The native KV initializer at `0x94e3c` now compiles and passes7,424 differential
cases, with98 source-owned zero-initialized bytes and authenticated constant
descriptors. Its FAL calls match the already attributed0.5.99 symbols bundled
with pinned FlashDB2.0.0. This preserves the upstream reuse boundary while
recovering only the native R1 mutex, lookup, geometry and scan policy. FAL
readiness/registry initialization and native flash scans remain explicit provider
requirements; passing controlled provider fixtures is not complete storage proof.


FAL readiness now uses unchanged pinned upstream `fal_init_check`, selected
with its own shared initialization byte and aliased to the R1-facing name.
Its256 byte-value differential cases pass. All448 bytes of the existing seven
compiled partition records independently match stock. The generic FAL build's
disabled assertions/diagnostics remain a concrete compatibility gate for broader
selection; future upstream integration must preserve original assertion/log
contracts and a single shared readiness state. No alternate upstream search
is needed to resolve the already-attributed FAL lineage.


The R1-only startup scrub (`0x57d0c`) and latest-slot selection (`0x64b24`)
now compile from authenticated native/pseudocode contracts. Their5,472 direct
and4,064 initializer integration cases pass. Their distinct partial-read policies
remain outside generic FAL: scrub ignores read counts and retains one header,
while selection requires a full header and clears it per candidate. The pinned
FAL boundary and lower flash driver remain the reuse route; these policies
do not justify substituting a generic database scan implementation.


`sdk-fal-core` now selects unchanged pinned `fal_init` and `fal_init_check`
together, with native error-only printf configuration and one shared readiness
byte. Its10,512 native differential cases preserve signed provider outcomes,
state transitions and all three failure printf calls. The earlier isolated
getter is replaced in the combined graph, avoiding duplicate state. Upstream
source files remain untouched. Lower flash/partition initialization and assertion
paths are still required before broader FAL selection; printf remains an explicit
runtime dependency.


Pinned FAL `fal_flash.c` now supplies device initialization and lookup with native
assertions, tested in12,338 stock comparisons including271 terminal assertions.
The same-pin musl1.2.5 `strncmp` is compiled as a separate attributable runtime
provider after primary/mirror byte agreement, preserving existing runtime receipts.
No upstream FAL function body was recreated. The actual R1 device record/driver
remains an explicit unresolved provider; folding of the singleton C table does
not establish original table section identity. Partition providers remain next.


Pinned FAL partition init/find/cache validation now pass18,647 stock comparisons
and are selected unchanged from upstream. The emitted448-byte table and37
zero bytes are authenticated. Partition-only configuration records a multiline
log line145-to144 mapping, and `-O0` preserves full-byte internal initialization
semantics that Clang otherwise narrows. Both pre-fix counterexamples are retained.
These adapters preserve native behavior without forking upstream function bodies;
original compiler identity remains a separate gate. The concrete R1 flash-device
record/operations are the remaining FAL provider requirement in this graph.


The R1 FAL device record and four registry adapters now compile, using the
official pinned FAL struct and callback types. A native configuration wrapper
retains the recovered partition macros and supplies a mutable device declaration
without editing the historical generic configuration or upstream bodies.
The5933 native adapter cases and all selected FAL suites pass after rebuild.
The record/registry seam is source-owned; concrete registered flash operations
and Nordic driver integration remain the next provider boundary.


The native registered internal-flash descriptor and six policy bodies now
compile with an official Nordic `nrf_fstorage_t` context. They pass203,735
stock comparisons and retain native callback timing,16-bit transfer lengths,
36-page geometry and returning-error behavior. These are manual native
contracts rather than reconstructed Nordic library internals. Pinned SDK
fstorage, lower adapters and completion/event handling remain the provider
boundary; controlled replies do not establish real erase/write persistence.


Native lower flash adapters and completion now compile and pass26,322 stock
comparisons: page/word rounding, forward mapped reads, SDK status handling,
poll/watchdog/delay order and successful-event pending clears. The watchdog
call reuses its existing native provider. Nordic fstorage init/erase/write/busy
and SoftDevice polling remain the pinned upstream boundary, rather than locally
recreated SDK bodies. Canonical bool and nonzero page-size fixtures do not
prove real asynchronous flash or scheduler behavior.


Unchanged pinned Nordic `nrf_fstorage.c` now supplies init/erase/write/busy
facades, with native disabled parameter checks/asserts in a local contract
header. Their12,227 direct and26,322 lower-adapter integration cases pass.
Final `fs_data` extent and the second native instance remain source/link gates;
`nrf_fstorage_sd` and SoftDevice polling are the next pinned upstream providers.
Predicate optimization and callback fixtures do not prove original instructions
or real asynchronous behavior.


The full pinned Nordic SoftDevice fstorage implementation is now selected
unchanged: eight-method API, queue/chunk/retry state machine and three SDH
handlers. Its3,047 direct and3,047 facade integration cases pass with407
flash SVC calls each. Source-owned state184 bytes, API32 bytes, information12
bytes, FIFO pointer4 bytes and observer records24 bytes are authenticated.
Real FIFO/atomic and SDH providers are next; no vendor state-machine body was
locally recreated. REA confirms the queue inventory's404-byte non-contiguous
scope includes SDH continuation, which remains explicitly gated rather than
being misreported as covered by the148-byte local block.


Pinned unchanged Nordic FIFO and fetch-OR/flag-set atomic bodies now replace
their storage test fixtures in the selected graph. Separate selection avoids
duplicating existing SDK atomic AND/OR providers. Direct comparisons:33,548,
including42 controlled exclusive-store failures per implementation. Actual
FIFO/atomic fstorage integration:69 workflows,920 actions,290 SVC calls.
The dependency remains attributable to the authenticated SDK17.1.0 archive;
future upstream updates require the same ABI/configuration and differential
checks. These serialized/interleaved fixtures do not establish physical
concurrency or flash persistence. SDH polling/continuation/state and full
observer dispatch are still the next upstream source gates.


The unchanged pinned Nordic SDH continuation/enable/disable/poll closure also
compiles with the recovered legacy section ABI. Its five public entry
contracts pass3,200 bounded comparisons with the real iterator and720 SVC
calls per implementation. This remains a separate candidate pending production
observer and IRQ wiring; controlled callbacks do not prove that integration.
Native range/set bytes84 and cold-zero state3 are authenticated. Ghidra-MCP
authenticates the entry spans; REA no-procedure result is preserved explicitly.


SDH core is now selected once in the combined source graph. Typed stack/state
records supplement storage-owned observers without replacing SDK bodies.
Actual SDK critical/NVIC execution passes4,704 comparisons with784 SVC calls
per implementation;84 range/set bytes,32 pointer-normalized observer bytes and
three cold-zero state bytes match native evidence. Two native state callbacks,
SOC polling and fault handling remain unresolved bodies. Original instruction
identity, physical interrupt behavior and whole-image linkage remain open.


Pinned Nordic SOC event polling now joins the combined graph unchanged, using
the recovered legacy iterator ABI and local returning-error contract. Typed
observer rows preserve real clock/DFU dependencies; section selection removes
the SDK's duplicate stack registration. Direct comparisons2,456; actual
SOC-through-fstorage workflows69/920actions,748 SOC fetches and290 flash calls.
28 range/set bytes and16 pointer-normalized observer bytes match native
evidence. The remaining clock observer routes to the same pinned SDK's
`nrf_drv_clock.c::soc_evt_handler`; dependency/control-block work remains.
Physical IRQ execution, complete asynchronous SDH integration, final image
linking and byte equality are unproven.

The pinned legacy Nordic clock source now supplies both native clock observers,
initialization, LF request/release and queue notification helpers. Local macros
preserve R1's structured logging and disabled-assert contract without changing
upstream function bodies. One20-byte SDK-owned state block replaces the clock
observer test boundary in the shared source graph. Direct comparisons3,444;
real-critical comparisons3,468; real SOC/storage/clock workflows72 over941
actions. Four nrfx hardware providers remain a direct route to the same SDK's
`nrfx_clock.c`. Notify's34-byte native span conflicts with the older32-byte
manual inventory; that gate is retained, with no ledger rewrite or promotion.
Physical behavior, original compiler identity and whole-image equality remain
unproven.

Four hardware APIs from unchanged pinned `nrfx_clock.c` now resolve the legacy
clock provider, including actual HAL/NVIC helpers. Scoped configuration restores
native RC source0, calibration-state storage and priority6 after the SDK legacy
defaults had replaced the recovered values. `-O0` preserves the eight-byte
control block; original compiler identity remains open. Direct comparisons858;
legacy integration with actual nrfx/critical instructions3,468. Register traces
and bounded LFSTAT transitions match native execution. Clock/shared IRQ dispatch,
calibration runtime, physical oscillator/IRQ behavior, startup and full-image
linking/byte equality remain gates.

The native154-byte POWER_CLOCK IRQ0 body is now attributed to unchanged
`nrfx_clock.c::nrfx_clock_irq_handler`, exported through the SDK's shared IRQ
macros. The source graph includes it and a typed four-byte IRQ0 vector entry.
Direct comparisons4,896; actual legacy-clock callback integration4,896. The
explicit derived ownership correction preserves the original hashed CSV while
replacing its former product-specific POF routing. Application callbacks and
MMIO values are fixtures; full exception/startup behavior remains open.

The remaining SDH state callback matches the pinned buttonless-DFU example's
`buttonless_dfu_sdh_state_observer`: GPREGRET2 skip-CRC marker followed by
`nrf_pwr_mgmt_shutdown(NRF_PWR_MGMT_SHUTDOWN_GOTO_SYSOFF)`. This is an attributable
next source route, pending implementation and native differential validation.

The pinned SDK buttonless-DFU example now supplies its exact state callback as
a build-time authenticated source slice. Official headers and the original
body are compiled; unrelated example code and the temporary compile anchor are
excluded. Direct comparisons6,144;432 callback-to-real-power workflows within
1,864 combined comparisons. Native retention/write ordering is source-backed;
actual retention/bootloader behavior remains unproven.

Unchanged `nrf_pwr_mgmt.c` shutdown/process and the separately selected SDK
atomic swap now resolve that callback. R1 logging/reset differences are local
contracts. Direct comparisons1,432, including12 forced exclusive failures per
implementation;18 cold-zero state bytes match. Logger panic/dequeue, reset
capture and authenticated startup/handler tables remain real dependencies and
evidence gates, alongside full linking and original compiler/byte identity.

The pinned Nordic logger frontend now supplies panic and its real backend
helpers, with a4096-byte ring configuration and shared contiguous source state.
Panic comparisons600; real power/DFU integration1,864 with2,120 backend panic
callbacks. REA confirms its38-byte native span and state accesses. This admits
panic only: dequeue, standard serialization, initialization/registration,
production backend callbacks and transport still require evidence-backed work.

The shutdown configuration scan found no admissible initializer/table route;
its bounded negative result is preserved without treating it as absence proof
or adding unsupported SDK example configuration.

The same pinned Nordic frontend now also supplies standard0..4 and dequeue,
including its private packing/overflow/skip/saturation helpers. Twelve additional
native contracts pass4,362 comparisons; actual SDK atomic/critical code executes.
The SDK balloc declaration supplies the authenticated typed pool descriptor,
stack/control/memory layout and mask. R1 warning behavior stays in a local C
adapter, preserving upstream source reuse. Memory-object providers and backend
registration/transport remain explicit dependencies; no allocator fixture is a
production implementation. See the frontend verification receipt for boundaries.

Pinned SDK memory-object/block-pool sources now close the frontend allocator
requirements without local algorithm replacements. Unchanged allocation,
reference-counting, chained copy and rollback/free code passes3,870 comparisons;
frontend integration adds4,362 comparisons with actual providers. Existing musl
copy and SDK critical/atomic providers are reused. The SDK files remain intact
for attributable future upstream comparisons; original binary compiler/runtime
identity and complete initialization/backend wiring remain separate gates.

The unchanged SDK logger initializer/backend registration and ring-buffer
initializer now have427 native comparisons. The local configuration corrects
autoflush to the observed native value and owns the128-byte string-push buffer,
24-byte control and12-byte typed descriptor. Source files stay unchanged. Actual
production backend records/transports and unused log-constant section metadata
remain explicit gates; selected API bodies do not establish startup completion.

Pinned Nordic RTT/default-backend sources now provide their actual record/API,
registration and partial-write/retry logic. A scoped native contract selects
RTT only,4096-byte staging and three1ms retries; the cycle-delay dependency stays
explicit. The SDK embedded delay-machine-code helper is excluded.141 native
comparisons pass. SEGGER RTT init/write and serial formatting remain the next
upstream provider routes; lower fixtures do not establish debugger output.

The pinned SEGGER no-lock writer now resolves the backend write provider, with
3,230 native comparisons and141 actual-provider backend comparisons. Native
initialization differs from the bundled generic initializer; a local typed C
body preserves the full120-byte clear and reversed identifier data while using
official SEGGER types. This difference is kept explicit for future upstream
updates. Generic SDK init/read/wrapper paths are not selected merely by version
label. Serial formatting, cycle delay and physical debugger behavior remain
separate requirements.

Pinned `nrf_log_backend_serial.c` now provides the actual serial dispatcher,
verified in3,312 native comparisons with7,680 standard/hexdump formatter calls
and actual SDK memory-object/reference/copy providers. The two formatter entry
bodies remain dependencies. Native timestamp-disabled/two-word-header behavior
is scoped explicitly; unused timestamp/padding is not promoted to ABI proof.
Upstream source stays unchanged for subsequent comparison and updates.

SDK standard/hexdump/postfix formatter bodies now compile with a precisely
recorded native-prefix replacement. The R1 calendar prefix and single-letter
severity labels stay in local C; upstream bodies remain attributable.1,894
formatter comparisons and2,496 actual-formatter serial comparisons pass. ASCII
printability matches all256 hexdump byte inputs; no foreign ctype-table ABI is
assumed. Printf/flush, native calendar ABI and module-color lookup remain explicit
provider dependencies, alongside real byte-stream and physical output proof.

Pinned SDK/SEGGER-derived fprintf sources now supply the actual wrappers,
integer/string parser and byte-buffer path.3,949 comparisons match53,516 emitted
sink bytes; formatter integration adds1,625 comparisons matching84,010 bytes.
The scoped native configuration enables CR-on-LF and disables double formats.
Compiled musl strlen is reused; no opcode/runtime blob is introduced. Actual
calendar/color bindings, complete pipeline/physical output and original compiler
identity remain explicit gates for future upstream changes.

The unchanged SDK color lookup now uses32 source-owned native module records
and names.33,056 comparisons plus1,625 actual-lookup formatter comparisons pass;
256 record bytes and311 name bytes match native data. Compiled section boundaries
belong to this typed array; original end-linker-symbol identity/completeness is
still an evidence gate. SDK implementation stays intact; target metadata and
error/warning colors stay in scoped configuration for future upstream updates.

The native cached calendar ABI now reuses the existing recovered Gregorian
converter and compiled integer/copy providers, with no new opaque dependency.
2,257 native comparisons and1,625 actual-calendar formatter comparisons pass.
Its output is eight packed bytes including weekday; the prefix buffer is now
sized accordingly. This remains owner-authorized reconstructed C, not vendor
source. The contextual helper signature is internal reuse, not proof of its
native standalone ABI. Real timestamp/RTC registration and physical output
remain separate gates.

The nrfx delay contract is now represented as explicit ARM mnemonics in a C
compilation unit, retaining its16-byte alignment and three-cycle subtraction
logic. The pinned SDK header and instruction-contract slice are authenticated;
no executable-data array is selected for this provider. All21 native six-byte
clones match its compiled body.1,215 comparisons and141 actual-delay backend
comparisons pass. Separate final clone placement, hardware elapsed time and
whole-firmware identity remain gates, despite exact local instruction bytes.

The combined pinned SDK/SEGGER logger graph now runs from standard serialization
to actual RTT ring writes, using the local native prefix/calendar and compiled
runtime/delay providers.954 comparisons cover540 messages and match19,920
accepted bytes. This connects the upstream bodies beyond isolated seam tests.
Clock getter/registration and between-call host consumption remain fixtures;
physical transport, broader frontend APIs and complete firmware linking remain
explicit gates for subsequent upstream changes.

The pinned SDK now also supplies standard5/6 wrappers and the hexdump producer.
8,922 comparisons pass with both memory-object fixtures and actual providers;
complete standard0..6/hexdump-to-RTT integration passes2,034 comparisons. The
native16-bit input/ten-bit hexdump-header mismatch is retained explicitly:
large-length packing does not prove valid consumption. SDK bodies remain intact;
string-push/other frontend APIs, actual clock registration and hardware/startup
requirements remain separate source/evidence gates.

The bounded string-push search supplies no native API entry; SDK presence alone
does not authorize promoting that optional feature into a stock component.
Clock bootstrap/snapshot registration instead now has owner-authorized local C
with2,501 comparisons and typed default metadata. This is reconstructed native
code, not vendor source. Distinct snapshot/fast slots and incoming-register
quirks stay explicit. Five RTC port callbacks, real device setup and complete
initialization call-site/startup evidence remain requirements; the missing Ghidra
bootstrap boundary is retained as supplemental-evidence context.

Three default clock ports now use compiled native reconstructions: update,
64-bit request read and callback binding. All 720 comparisons use actual source
registry dispatch and memory helpers, with bounded RTC operation fixtures. No
vendor provenance is inferred for these local wrappers. The two calendar ports
remain gated pending native ABI comparison against the accumulated Gregorian
reconstruction; upstream SDK updates cannot substitute for that device contract.

The remaining default clock calendar slots now compile with three unchanged
slices of the accumulated owner-authorized Gregorian reconstruction. This code
has local reconstruction provenance, with no inferred upstream vendor identity.
45,233 native/source comparisons and fresh REA/Ghidra inverse-converter evidence
support these native contracts. The separate source-owned RTC device body and
its SDK RTC dependencies remain the next provider boundary; existing deliberate
contextual scan/null-handling changes must be reconciled against the binary.

The RTC record-write path now adds unchanged musl `src/string/memmove.c` at the
existing v1.2.5 commit, in `third-party/upstream/musl-memmove-1.2.5/`, retrieved
from the primary upstream with MIT attribution retained. A local native ABI shim
preserves the firmware helper's nonstandard R0 result. 5,344 RTC/movement native
comparisons pass, including overlap tests; standard musl pointer-return behavior
alone is not promoted as the stock helper ABI. Future improvements require an
explicit source pin and rerunning both data movement and shim/consumer contracts.

The full logger pipeline now calls the actual C RTC snapshot through registry,
timestamp adapter and default clock getter; 2,034 comparisons / 76,396 accepted
RTT bytes remain unchanged. RTC registration and counter advancement are still
controlled inputs. The next reusable upstream boundary is Nordic SDK 17.1.0
`nrfx_rtc`: native open selects RTC2, instance index0, IRQ36, four capture/compare
channels and a 4095 prescaler. Driver/configuration admission still requires
source authentication and native differential checks; these observations alone
do not prove the SDK body or hardware timing.

RTC lifecycle C now preserves the native unsigned four-year breakdown helper
and shared 32-byte buffer. The existing Gregorian converter is not an equivalent
substitute across the full epoch range. This is owner-authorized reconstruction,
not attributed vendor runtime source. 51,592 native/source comparisons pass;
the Nordic RTC initialization/tick-enable/enable and error bridges remain
explicit production providers. Their native structured-log paths must be
preserved when admitting the already pinned SDK source, including native state
and handler arrays; a generic build with logging disabled is insufficient.

Pinned Nordic `nrfx_rtc.c` now provides RTC initialization, enable and tick-enable
without changing vendor bodies. Scoped native logging/assertion adapters and
layout-checked C bridges pass 6,272 comparisons, including ordered MMIO/NVIC
writes and dynamic log modes. All included vendor files are checked against the
same authenticated SDK ZIP. Subsequent SDK improvements require an explicit
new pin and rerunning state, register-write, logging and consumer contracts.
The RTC error call reuses the existing `r1_adc_error` source through a canonical
link alias; its independent 2,560-case reference remains outside the board.
IRQ dispatch/vector and real peripheral timing remain separate admission gates.

The same unmodified Nordic RTC source now supplies its IRQ wrapper and common
dispatcher. A symbol-only rename exposes the private dispatcher for attribution;
a local C vector word supplies IRQ36. 65,536 mask/mutation comparisons pass, plus
16,384 with the actual native RTC tick/calendar callback chain. W1C behavior is
modeled, and physical delivery/concurrency remain unproven. The original wrapper
ownership row's oversized extent remains gated; native bytes and sequential
execution do not justify silently rewriting the original inventory.

RTC cached discovery now uses owner-authorized native C and the existing source
registry, with no inferred third-party origin. A 960-comparison composed startup
check reaches the pinned Nordic RTC providers, IRQ/tick/calendar chain and clock
callback. Failed cache lookups retry; non-null cached handles never refresh.
This joins existing upstream-backed providers without claiming actual boot
ordering, hardware delivery or event transport. The candidate device-initcall
pointer span is the next source-owned configuration boundary to authenticate.

The device initcall configuration is owner-authorized local source, not an
attributed SDK table. Native range literals prove13 entries beginning at
`0xc4534`; the adjacent `0xc4530` pointer is excluded. The three-stage runner,
empty post stage and IRQ-mask wrapper compile as C with explicit target mask
primitives.54 normal and12 null-target checks preserve order/status/mask quirks.
Nine table targets reuse existing providers; hardware-TWI primary/secondary,
PWM and YHM2710 registration bodies remain explicit gates. Fresh REA confirms
the22-byte post runner. No upstream is inferred merely from the initcall shape.

The two native hardware-TWI constructors now compile with216 bytes of typed,
cold-state-verified configuration and pass864 comparisons using the actual
registry and a semaphore-allocation fixture. The next RTOS boundary is the
identified `osSemaphoreNew(1,0,NULL)` call; no allocator acceptance is inferred
from a pointer fixture. TWI operation/event-callback bodies remain unresolved.
The remaining five-record registrar is GPIO-output control through GPIOTE, not
PWM; the source-owned symbol is corrected accordingly. This avoids pursuing an
unrelated PWM dependency. GPIO-output and YHM2710 registrar source remain next.

GPIO-output and YHM2710/STACMD registration/configuration now compile as local
native reconstructions. STACMD reuses the pinned Nordic GPIO HAL wrappers for
six additional native copies, with1,158 direct primitive comparisons plus408
constructor comparisons. The microsecond adapter calls the already admitted
native subtract-three kernel, preserving unsigned scaling/wrap; elapsed physical
timing remains unproven. All13 initcall registrar names resolve to C, while
`osSemaphoreNew` and the device operation bodies remain separate dependencies.
No new third-party origin is inferred for the local registrar/configuration code.

The semaphore creation boundary now consumes unchanged pinned CMSIS-FreeRTOS
source with a scoped native configuration:80-byte static control block, both
allocation modes and no wrapper queue-name registration.38,400 comparisons
cover IRQ/mask/scheduler contexts, attribute bounds, allocation routes and failed
initial-give deletion. The baseline kernel registry configuration is untouched.
Six FreeRTOS queue backends remain the next boundary; the pinned kernel source
can be selected and compared before claiming real allocation or full initcalls.

The pinned FreeRTOS10.5.1 core now also supplies unchanged generic/static and
counting/static queue creation, queue reset and list initialization to the
canonical graph (`rtos-queue-create`).372 native/source comparisons authenticate
the80-byte control block, allocation-failure path, dirty-memory writes,
waiter/yield reset behavior and10 assertion paths. Preserve the pinned source
and scoped native assertion configuration when evaluating upstream improvements;
changes require replaying these contracts. Native reset at0x97ba4 is explicitly
corrected from the original ownership label in a supplemental evidence record.
Allocator, task removal, send/delete and full scheduler integration remain gates.

The full device-initcall composition additionally executes the actual CMSIS,
queue/list and Nordic critical providers with all13 registrars (32 comparisons,
25 named records,64 allocation calls). Allocation remains a bounded return/storage
fixture. Native heap4 adds a16-byte allocated header and caller-LR tracking;
retain that extension as a source-owned evidence gate rather than replacing it
with the pinned upstream8-byte header. This stage does not establish full boot.

Native heap4-family allocation/free is now source-owned C in`native-heap`:
3165 native/source comparisons,561 fatal assertions, full51200-byte heap and
state comparisons. FreeRTOS10.5.1 heap4 remains attributable lineage; native
16-byte headers, caller LR, preserved padding, request rounding, minimum split
and fatal failure policy are retained explicitly. Upstream allocator changes
must be reviewed against these native contracts rather than copied wholesale.
The real initcall/CMSIS/queue/heap composition passes8 cases with25 named records;
scheduler suspend/resume remains a bounded fixture and the next provider gate.

Pinned FreeRTOS scheduler suspend/resume/reset-unblock and ready-list macros
now compile as unchanged byte-hashed source slices (`rtos-scheduler-resume`).
32274 native/source comparisons cover real pending/state/ready-list transfers,
priority/yield decisions and pended-tick replay decisions; tick processing and
critical hooks are fixtures in that unit. The actual prekernel device-initcall
composition additionally executes the real critical/heap/suspend/resume graph
without provider interception (8 cases,25 records). The accessed TCB prefix is
48 bytes; full TCB allocation remains separately gated. Re-run these contracts
when evaluating upstream kernel changes. Native scheduler literals also correct
the heap start-sentinel extent to12 bytes, distinct from16-byte allocation headers.

Pinned kernel tick/event-list providers now supply unchanged body/macro slices
with the original MIT notice (`rtos-scheduler-tick`).40193 native/source cases
exercise real list/timeout/event operations without provider interception.
Scheduler-resume composition adds10770 cases with3360 actual replayed ticks and
a delayed timeout. Preserve the native state addresses,48-byte accessed TCB
prefix and signed overflow-counter variant when evaluating upstream changes;
complete TCB allocation and scheduler startup/context switching remain gates.

Pinned `queue.c` send/delete/copy/unlock bodies now compile with explicit native
variants (`rtos-queue-operations`): registry size0 for delete and scoped copy
binding to the native-ABI overlap-safe musl movement provider.4875 native/source
cases cover data/control/blocking decisions; lower task boundaries are fixtures.
The canonical CMSIS/queue/heap/scheduler/critical/movement graph passes1088
nonblocking lifecycle cases without provider interception, including heap
reclamation and360 overlapping sends. Preserve these contracts for upstream
changes. Native TCB+84 stores stack-depth words after a32-byte name; this is a
source-owned R1 extension, not proof of the upstream end-of-stack option.
Task-wait/mutex providers and full TCB construction remain explicit next gates.

Pinned timeout/wait/mutex and list providers now resolve the queue-send task
boundaries (`rtos-task-wait`):18675 native/source comparisons and323 assertion
cases. Bodies and debugger-priority declaration are unchanged source slices;
R1's104-byte accessed TCB prefix preserves the stack-depth extension at+84.
The native debugger constant55 at0x2000784c is compiled from the upstream
priority expression and checked against cold RAM. Full112-byte TCB construction
remains gated. Blocking timeout composition adds2016 checks/720 real tick calls;
controlled PendSV/tick context transfer is distinct from native context-switch
execution. Re-run these contracts before adopting upstream kernel changes.

R1 task construction now combines native112-byte factories/initialization with
unchanged pinned kernel ready-list/list-setup and Nordic initial-stack/error
bodies (`native-task-construction`).788 native/source cases and144 actual-graph
two-task comparisons pass. Keep the native depth extension and full zeroing
policy explicit; the baseline92-byte `StaticTask_t` is not interchangeable.
Original upstream body slices/licenses remain intact and hash-bound. The graph
uses actual heap/critical/list/port providers; CMSIS thread wrapping, task code
execution, cleanup and native scheduler/context switching remain gates.

Unchanged CMSIS thread creation now uses the scoped112-byte R1 construction
representation (`rtos-thread-new`), with typed constructor bindings and original
Apache notice.42048 native/source boundary cases cover attrs/context/depth and
priority behavior. Actual CMSIS/kernel construction adds144 two-task checks;
the five existing application creation callbacks add2400 checks across all120
orders, with full records/stacks and no provider interception. Task execution,
cleanup, scheduler start/context switching and full-image identity remain gates.
The baseline typedef/configuration and unselected weak callbacks are preserved;
future upstream updates must revalidate the scoped native ABI and these receipts.

The task termination subset reuses unchanged licensed slices from the pinned
FreeRTOS-Kernel10.5.1 (`def7d2df2b0506d3d249334974f51e427c17a41c`) and
CMSIS-FreeRTOS (`d213f261b5be6bb29a7cce8b84071706b72f4d53`). Body byte
ranges and hashes are recorded in `rtos-task-termination/report.json`; the
frontier audit reconstructs the generated translation units exactly. This
keeps upstream changes reviewable against native contracts. Updates are not
automatically firmware-compatible: the native112-byte TCB, notification108,
allocation mode109 and scheduler word locations remain required contracts.
The baseline kernel configuration is unchanged; the ABI adaptation is scoped
to this subset. Idle cleanup/context switching remain separate evidence gates.

The same pinned task source now supplies idle reclamation and expected idle
time without body edits. The cleanup is inlined in the native idle task, so
its test binds an explicit native region rather than inventing a function
boundary. The scoped header supplies the already authenticated task/list/state
ABI; it does not change the baseline FreeRTOS configuration. Complete native
idle-hook and tickless behavior remain separate gates.

The complete `prvIdleTask` body is now selected unchanged from pinned
FreeRTOS-Kernel10.5.1 into `rtos-idle`. A scoped header enables the native idle
hook and binds already compiled cleanup/expected-time providers. A typed void
adapter calls the existing watchdog-feed thunk and discards its unused result.
Source-slice hashes, MIT notice, configuration, object and dependency hashes
are checked by the frontier audit. Tick suppression is still an explicit
provider dependency; its native flow points to the pinned Nordic RTC port in
`port_cmsis_systick.c`. Updating either upstream requires rerunning these native
contracts rather than accepting a symbol match as compatibility evidence.

The pinned Nordic SDK RTC `vPortSuppressTicksAndSleep` body now compiles
unchanged with a scoped native error/FPU header. Its original complete source
file hash and all compiler inputs are retained; section selection keeps only
the sleep body and its inline SDK primitives. Pinned FreeRTOS10.5.1 supplies
`eTaskConfirmSleepModeStatus` and `vTaskStepTick` without body edits. These three
providers resolve in the native board C graph and retain independent native
contracts. Future upstream updates must preserve the native FPU guard, returning
error continuation, NVIC state/masks,24-bit compare/delta and deferred tick at
an exact unblock boundary, or remain an explicitly different candidate.

Scheduler/timer creation now selects unchanged FreeRTOS10.5.1 startup bodies
and original timer-message typedefs. A forward-declared `Timer_t` suffices for
the pointer field used by these bodies; timer runtime layout/execution is not
claimed. Scoped headers bind native112-byte constructors, timer priority53,
32-message static queue and registry0. Existing static-memory callback bodies
compile with the typed native TCB and authenticated RAM placement. Original
MIT notices and exact source-slice ranges/hashes remain reconstructable by the
frontier audit, preserving a reviewable route for later upstream improvements.

The unchanged Nordic `xPortStartScheduler`, RTC1 `vPortSetupTimerInterrupt`,
VFP enable and unexpected-return bodies now compile as selected licensed C
slices. Their original macro/body byte ranges and complete dependency hashes
are audited. Scoped bindings reuse existing private state and preserve raw
priority2 versus BASEPRI64 semantics. The pinned GCC/nrf52 `port.c` also provides
C translation units with explicit architecture assembly for first-task/SVC/
PendSV work; its first-context contract is the next gate rather than a retained
binary implementation. Physical exception execution and exact compiler output
remain distinct from attributable source reuse.

The unchanged pinned Nordic GCC C port now supplies first-task/SVC/PendSV
source directly, including its licensed explicit architecture assembly. No
instruction byte arrays or executable reference fragments are used as firmware
providers. Pinned FreeRTOS10.5.1 supplies unchanged task-selection body/macro and
stack canary checks. Partial vector records are separately source-owned and
authenticated. Native first-task masks (BASEPRI480 lowbytee0), PendSV mask64,
software FP/core frames and ready-list behavior remain native contracts that
future upstream changes must revalidate. Actual hardware exception dispatch/
return and complete vector-table reconstruction retain their own gates.

The product-owned overflow hook now composes with the already pinned Nordic
frontend/RTT and source-owned structured logger rather than adding a reset or
an assertion substitute. Its native terminal sequence drains the existing
frontend until false and loops without an explicit interrupt-mask write.
Source descriptor strings, module28 severity and repeated mode reads retain
native contracts. The actual logger providers preserve their independent
upstream/source receipts and remain reusable across later SDK improvements.


Timer runtime staging reuses unchanged `timers.c`, `queue.c` and `tasks.c`
bodies from the existing FreeRTOS-Kernel10.5.1 pin
`def7d2df2b0506d3d249334974f51e427c17a41c`. The builders record exact upstream
slices, hashes, license bytes and scoped configuration; no alternate timer
implementation is introduced. Future upstream fixes can be evaluated against
the same native44-byte timer/16-byte command contracts and isolated tests.
Queue-copy paths reuse the existing musl-backed overlap-safe native adapter.
The stage linker resolves the timer task without adding undefined providers;
combined scheduler execution remains an admission gate.

The staged timer graph now also executes the shared pinned queue, restricted
wait and scheduler bodies together with the source heap. Its240 comparisons
include static/dynamic controls, stop/wakeup/delete, autoreload, rollover and
matching lower-provider call counts. Timer creation and generic-command APIs
remain the next upstream-body targets; fixture timer-control setup is stated
explicitly in the graph receipt.

Timer factories/private initialization/generic-command now also use unchanged
FreeRTOS10.5.1 source slices. ISR command sends reuse the same pinned queue
body with an explicit native priority-validator macro, avoiding the baseline
header-order omission. The existing Nordic board validator composes in the
480-comparison graph; a separate pinned-source build revalidates its state
contract without duplicating it in the graph. Future updates must retain the
44-byte timer,12-defined/16-total command layout, native assertions and
interrupt-priority semantics. Locked ISR task-count saturation remains an
explicit lower-provider gate.

The pinned task-count getter is now reused unchanged and reads the existing
native kernel count word rather than owning a second counter. It executes in
ISR queue saturation tests and the combined timer graph. The daemon loop is
also exercised for a full nonblocking iteration with actual receive/delete
providers; callback returns and hardware task transfer remain separately
gated. These are native contract checks, not byte identity.

Canonical timer admission now reuses all six selected FreeRTOS provider
objects with existing native state ownership. The frontier audit reconstructs
selected C from pinned source slices and explicit interface text, so an
upstream update must re-establish provenance and native contract checks.
The source getter and restored priority-validator macro close prior isolated
fixture/configuration gaps; hardware concurrency and image byte equality
remain independent gates.

CMSIS message queues now reuse the unchanged pinned CMSIS-FreeRTOS wrappers
and FreeRTOS-Kernel queue receive/query bodies. The native80-byte queue and
24-byte attributes, registry0, unchecked32-bit attribute product and ignored
name/priority semantics are explicit scoped contracts. A future upstream
update must revalidate18,240 wrapper cases,9,239 ISR receive/query cases and
the4,800-comparison canonical graph. The source frontier admits seven entries;
blocking scheduling and physical interrupt/concurrency proof remain separate.

Semaphore/mutex staging extends the pinned CMSIS wrapper reuse and selects
unchanged FreeRTOS ownership/inheritance/timeout bodies. Existing public queue
constructors/senders, the canonical current-task getter and native shared
kernel words remain single providers. No second queue/TCB state or alternative
mutex algorithm is introduced. Source slices, licenses and scoped native
interfaces are recorded for future upstream revalidation. Wrapper/task helper
unit contracts pass; kernel mutex/semaphore differential and composed graph
admission remain explicit pending work.

Semaphore/mutex source reuse is now admitted through28,916 isolated native
comparisons and the1,344-comparison composed graph. Kernel ownership,
recursive counts, inheritance/restoration and semaphore task/ISR operations
remain the pinned FreeRTOS implementations against the native interfaces.
The audit reconstructs selected sources and verifies all provenance and
composition receipts. Upstream updates must re-establish these contracts;
controlled task selection is not blocking-scheduler or hardware proof.

Notification/event/delay staging reuses unchanged pinned CMSIS and FreeRTOS
indexed notification bodies, scoped to the authenticated one-slot112-byte TCB
(value104/state108). Wrapper/kernel unit contracts pass; event-group bodies
and timer/unordered-event composition remain gates. Fresh REA body ranges and
pseudocode expose a noncontiguous event-ISR/shared timer-pend implementation,
which should map to the existing upstream event and timer sources rather than
an invented replacement or a contiguous binary span. Native ABI evidence takes
precedence over incomplete decompiler return types.

The event-group set/get-ISR/set-ISR/callback, ISR timer-pend and unordered task
wake paths now compile from unchanged pinned FreeRTOS bodies. Their isolated
native checks close the staged source dependencies of the notification
wrappers. The original noncontiguous event-stub/timer body is mapped to both
upstream functions without changing the ownership CSV or retaining executable
bytes. The native suspend-count word is shared by address. A composed timer
queue/deferred callback/event wake graph remains required for admission and
future upstream revalidation.

The notification/event stage is now canonically admitted with672 composed
comparisons,64 actual deferred callbacks and matching native/source provider
counts, in addition to51,826 isolated comparisons. The audit keeps the event
stub and shared timer-pend body mapped to their respective pinned upstream
functions, and preserves the original ownership artifact. Future upstream
updates must pass the same native interface/layout and composition checks.
Blocking resumption and hardware/original-byte proof remain separate gates.

The product delayed scheduler at0x65b4c is product-specific recovered C;
no attributable third-party implementation has been identified for that body.
Its queue, delay, mutex, timer and logging calls retain the existing pinned
CMSIS-FreeRTOS, FreeRTOS and Nordic providers. REA identifies osTimerStop
at0x7d9ea and xTimerIsTimerActive at0x98d68 as the next reusable upstream
bodies; native osTimerStop distinguishes inactive(-3) from command failure(-1).
Their source extraction, layout checks and native regression receipts remain
required before use. The product timer callback and state initialization are
separate recovery gates. Do not import a generic timer algorithm in their place.

Product immediate push0x659e8 is now recovered C with2,304 native comparisons
and1,536 real scheduler/push composition comparisons. Its eight-byte record
and CMSIS queue-call contract are retained, allowing existing upstream queue
providers to be composed later without replacing the product behavior.
No third-party provenance is claimed for the product body itself. Pinned
CMSIS `osTimerStart` and `osTimerStop` bodies are present in
`third-party/upstream/cmsis-freertos/CMSIS/RTOS2/FreeRTOS/Source/cmsis_os2.c`;
source extraction and native checks remain the next timer-control work.

Pinned CMSIS timer start/stop and FreeRTOS timer-active predicate now compile
from unchanged attributable source slices with original licenses. Their6,784
native comparisons retain the native error distinctions and44-byte timer ABI.
The two wrappers use the actual selected timer-active body; command submission
and critical boundaries remain controlled fixtures. The source audit can be
reused when considering later upstream changes, alongside the required native
and composed regressions. This does not authorize changing the native contract
or claim that later upstream revisions preserve it. Product callback recovery
and actual generic-command graph composition remain open.

Product timer callback0x65f84 now compiles as recovered C and passes7,680
native/source comparisons, half composed with the actual immediate-push body.
The product minimum-delay sentinel and update order remain native contracts;
no generic upstream timer algorithm replaces them. Selected pinned CMSIS timer
controls and FreeRTOS/Nordic queue/critical providers remain the intended lower
implementation graph. Their integration and the event-loop initialization still
need native receipts before canonical source-board admission.

The delayed-event staged graph now executes the real product bodies with
selected pinned CMSIS timer controls and FreeRTOS queue/mutex/critical/daemon
providers, passing30 native/source comparisons across12 workflows without
lower-provider interception. Product initialization remains a fixture. Native
initializer0x65740 additionally calls CMSIS timer creation and thread termination;
these lifecycle providers and its source-owned attributes must be authenticated
before replacing the fixture. The initializer/worker are supplemental coverage
gates outside the locked ownership/corpus rows, which remain unmodified.

Supplemental product initialization now compiles with source-owned typed
attributes/storage and3,072 native comparisons using factory fixtures. Pinned
CMSIS `osTimerNew` and `osThreadTerminate` are the remaining attributable
lifecycle bodies needed to compose actual initialization. The product owns
its queue/thread/timer/mutex attributes; these values should remain explicit
when revalidating upstream updates. No upstream provenance is claimed for the
product initializer or its worker, both outside the locked corpus row scope.

The product queue worker0x65ea8 is recovered C with1,512 bounded comparisons;
it dispatches successfully through the existing pinned CMSIS/FreeRTOS queue
providers in12 timer-expiry graph workflows. Its receive/error-loop behavior
is retained separately from upstream queue behavior. No physical blocked-task
resumption or provenance claim for the product body is added. Pinned timer
creation and thread termination remain the next lifecycle reuse targets.

Pinned CMSIS timer creation/callback and FreeRTOS timer-ID getter now compile
with4,778 native comparisons. The product44-byte static timer still needs an
eight-byte dynamic callback record;52-byte static storage can own it inline.
Thread termination already had a canonical provider and is reused. Keep the
native timer-ID attribution correction separate from the locked task-tag row.
The staged initializer now has no missing source providers; actual heap/lifecycle
composition and canonical board admission remain required before closure.

Actual product initialization now composes selected pinned CMSIS constructors,
FreeRTOS heap/task/queue/mutex/timer providers and the recovered product bodies,
passing60 comparisons across24 workflows including12 reinitializations. The
source heap callback record and actual CMSIS callback/ID-getter path execute;
thread termination reuses the canonical provider. Exact callback/name/allocator
and initial-stack pointer checks bound normalization, preserving upstream ABI
and layout contracts. This establishes staged composition, with canonical
admission, physical scheduling and complete original-image closure still gated.

Product cancellation0x65d64 now compiles and passes6,912 native comparisons;
12 actual-provider workflows cancel the second pending event while the first
still dispatches. It reuses pinned CMSIS/FreeRTOS mutex/timer/queue contracts
without replacing the product null-slot/wildcard semantics. Canonical layout
admission and complete image/source-startup/physical proof remain separate gates.

Delayed-event product/storage and selected timer providers are now in the
canonical source board. The selected stage reuses the canonical object rather
than linking duplicate providers; all composed and full canonical regressions
pass after admission.62 board symbols remain unresolved. This is reusable
source/ABI evidence, with complete image layout/startup, original-byte equality
and physical execution still gated. The next service/storage hardware-init
wrappers are log-only in current native evidence; their symbol names do not
prove hardware initialization.

Service/storage initialization wrappers0x45c84/0x45d00 now compile as recovered
product C and pass4,394 native comparisons against controlled log boundaries.
They log only. Existing Nordic and structured-log providers remain their lower
source graph; no third-party implementation is attributed to the product
wrappers themselves. Concrete composition/canonical admission remains open,
and binding names do not establish hardware-initialization behavior.

The two log-only wrappers are canonically integrated with their source-owned
native descriptor IDs.2,592 composed comparisons/384 workflows execute both
structured cache and selected Nordic logger/RTT providers across all log modes,
clock/export states and immediate/deferred delivery. Cortex-M-class engines
execute native IPSR directly. Export thresholds and physical concurrency remain
separate gates. The next product status-ring publisher should reuse admitted
timestamp, critical-section and event providers while recovering its product
record packing, state getters and ring configuration from native evidence.

The product status publisher and three state getters compile as recovered C
with21,008 native comparisons. The existing admitted configuration accessor
at0x7ba24 is reused through its advertising-module symbol, while timestamp,
critical and event providers remain the intended actual source graph. Native
instructions establish16-bit counter access despite a32-bit decompiler label.
No third-party provenance is claimed for these product bodies. Battery updater,
source-owned state/ring initialization and canonical composition remain open.

The product battery updater0x31fd0 compiles with2,896 native comparisons and
all four FPSCR rounding modes. Its numeric path and five-argument refresh ABI
come from native instructions; lower charger/ADC/algorithm/reporting bodies
remain explicit providers. Existing EABI memory clear and CMSIS tick providers
are reusable, and the product ADC adapter should retain the selected Nordic
internals. No third-party provenance is asserted for the updater itself.
Conditional FP side effects, source state ownership and actual provider/canonical
composition must remain part of future revalidation.

Charged-state refresh and voltage/level trimmed means now compile as recovered
product C, with5,536 direct comparisons and2,896 actual updater/statistics
comparisons. Both selected battery units use scoped packed native-width SRAM
accesses; existing EABI clear/CMSIS tick providers remain reusable. The next
small reset/flags/shared-resource contracts should retain the admitted RTOS
and Nordic interfaces. No upstream provenance is claimed for the product means
or charging policy, and physical concurrency/source-state ownership remain gates.

The battery control candidate reuses the CMSIS `osThreadFlagsSet` interface and
retains YHM register-write as an unresolved transport boundary. Six recovered
bodies pass4,504 direct comparisons and2,896 updater/statistics/control graph
comparisons. Existing `reconstructed/yhm2710` active/inactive helpers corroborate
register2 commands0xa8/0x28, but their contextual bool interface differs from the
native zero-context/raw-status ABI. They require an evidenced adapter before
reuse. Neither these product wrappers nor charging policy acquire vendor-source
provenance through that correspondence. Pinned upstream RTOS/Nordic providers
remain preferred where the recovered ABI and configuration agree.

Native charger classification and its adapter now compile with4,616 comparisons.
The contextual `yhm2710_charge_state` has the same status mapping, but its
`yhm2710_status` dependency initializes the read byte and checks transport success.
Native0x3529a can retain its pushed incoming r3 byte when register6 is not written.
Do not alias these APIs without proving the transport/input contract. This is
owner-authorized reconstruction correspondence, not attributable vendor source.

The native YHM readiness/read frontend now compiles with832 comparisons. It
preserves callback-context reloads and raw transport returns; existing contextual
YHM APIs still require an evidenced bridge. Callback-table initialization and
read-record transport0x507cc remain source ownership/provider gates. No external
vendor-source attribution is claimed for these recovered product bodies.

YHM transaction records/resource/completion now compile as recovered product C,
with2,928 direct comparisons. They reuse the previously admitted registry
08/0c/10/14 interfaces rather than duplicating dispatch semantics. The registry
is owner-authorized reconstruction, not attributable vendor source. Its actual
source composition and lower bus operations remain to be validated. Native
completion returns release/callback status and does not establish bus success;
context/request initialization and physical serialization remain gates.

The YHM transport now executes admitted registry dispatchers directly in11,712
native/source comparisons, including null handles and missing operation slots.
Matching dispatch entry counts and report hashes prove selected source reuse;
only lower bus operation callbacks remain fixtures. This closes the dispatcher
composition gate for this graph, while preserving initialization, lower-device
providers, physical concurrency and whole-image source/identity gates.

YHM handle discovery now compiles with1,536 comparisons over512 repeated-init
workflows. It reuses the admitted registry lookup and08/18 interfaces by name;
actual provider composition is still required. Device names and cache/reload
policy are recovered product evidence, with no third-party source provenance
claimed. Initialization does not establish callback ownership or lookup success.

YHM initialization now directly reuses the admitted registry and pinned musl1.2.5
strcmp source objects in3,072 composed comparisons. Native/source lookup,
dispatch and string-comparison counts match across1,024 repeated-init workflows.
This supplies attributable libc reuse and recovered registry composition without
inventing vendor provenance for product initialization. Lower device operations
and source-owned production registration/context initialization remain gates.

Four native fixed-state STACMD operation bodies now compile with1,580 comparisons.
The owner-authorized contextual YHM model corroborates retry/status policy but
adds device/null-buffer handling that the native adapters do not perform. These
new bodies preserve fixed-state and request-register ABI contracts, with no
vendor-source provenance claim. Recovery/frame/retry providers and shared typed
registration/configuration integration remain explicit gates. REA has no function
metadata for these manual-provenance entries; native Ghidra-MCP bytes and locked
ownership rows are the positive evidence used here.

The native STACMD recovery callback sequence now compiles with240 comparisons,
preserving five delay calls, callback/pin reloads and raw tail return. Existing
source-owned wire registration identifies the intended GPIO callbacks, but its
shared typed ABI and actual operation composition still need integration. Delay
and physical timing evidence remain separate gates; no vendor-source provenance
is inferred from the contextual YHM reconstruction.

The recovered native STACMD delay now compiles from209 iterations of four NOP
mnemonics, with64 direct comparisons and240 recovery-graph comparisons using
its actual body. Each recovery implementation executes1,003,200 NOPs over1,200
delay calls. This is product timing-loop reconstruction; no upstream vendor
source provenance is asserted. Compiler scheduling/cycle count, physical clock
calibration and actual GPIO/frame composition remain distinct gates.

Recovered STACMD write retry now compiles with2,574 native comparisons and1,580
adapter-graph comparisons using its actual body. It reuses admitted logger
interfaces and preserves native descriptor IDs in the direct receipt; logger
providers remain fixtures. The contextual YHM retry model returns bool, whereas
the native body forwards the complete successful frame result and performs
failure logging. No silent API substitution or vendor provenance is claimed.
Actual recovery/frame/logger composition and shared registration remain gates.

Native STACMD read/write frames now compile with15,360 comparisons. Existing
contextual YHM frame models help identify the protocol, but add input guards and
use size_t lengths; native loops compare signed32-bit lengths and preserve
partial read output before cleanup. The recovered adapters retain those native
contracts and full-width bit/parity boundaries. Lower wire providers and actual
transport composition remain gates; no upstream vendor provenance is claimed.

Four native STACMD transmit/idle/parity bodies now compile with5,792 comparisons;
write-bits executes its actual drive-bit provider. Matching4,225,728 executed NOPs
establish selected loop counts, not physical timing. Existing source-owned wire
registration identifies intended GPIO callbacks, whose actual composition and
shared typed ABI remain gates. These recovered product bodies are not claimed
as vendor source, and the contextual reconstruction is not silently aliased.

Native receive and its actual adapter now compile with1,152 comparisons over24
edge-boundary pairs. Matching1,633,824 read callbacks and119,808 NOPs establish
selected software contracts. The contextual YHM reader uses a byte output and
additional device guards; native receive always stores a32-bit sampled bit,
including timeout. Those interfaces require an evidenced bridge, not a silent
alias. Actual GPIO and full frame/transport composition remain gates; no vendor
source provenance is claimed for the recovered polling bodies.

The selected STACMD frame/wire graph now directly links nine recovered provider
bodies over480 comparisons, with only GPIO callbacks remaining fixtures. Matching
entry counts,1,132,224 NOPs and181,424 GPIO callbacks establish the selected source
composition. A scoped frame loop-alignment change removes observed compiler
padding; physical timing and original instruction scheduling remain unproven.
Typed registration, actual higher transport composition and hardware evidence
remain gates. These product bodies retain owner-authorized reconstruction
provenance, without vendor-source attribution.

The selected STACMD adapter-to-wire graph now executes13 recovered provider
bodies in192 comparisons. Native/source status and entry counts match, including
nine-attempt exhaustion and recovery from an initial failure. Only GPIO callbacks
and disabled log-mode remain fixtures; actual registry/transport/logger and GPIO
composition remain gates. Scoped adapter/retry alignment changes remove observed
padding without claiming physical timing. Product source provenance remains
owner-authorized reconstruction; typed production registration is still open.

STACMD registration and seven recovered source units now share a checked native
configuration/registry ABI. A standalone stage links their bodies against the
canonical source-owned record and providers, closing four operation symbols
while retaining the counter as an external data gate (57 stage unresolved versus
60 canonical). Canonical registration/layout and dependent runtime checks are
refreshed. Raw GPIO return/timing, executable-stage operation admission, counter
reset ownership and full image identity remain open; vendor provenance is not
inferred from this product-source integration.

The STACMD failure counter now has source-owned cold-zero initialization, supported
by explicit native scatter writes under four nonzero RAM poison patterns. Its
four-byte C initializer is linked into the standalone source stage, removing the
last new data dependency there (56 unresolved versus60 canonical). This is native
product-state recovery, not third-party provenance or full startup equivalence.
Warm-reset lifecycle, canonical admission and original whole-image byte identity
remain separate gates.

The recovered STACMD wire path now runs with its compiled108-byte configuration,
four-byte counter and14-byte name, matched to native cold initialization with
pointer normalization.192 composed comparisons pass through13 actual provider
bodies. GPIO and disabled logging remain explicit test boundaries; registration
execution, actual canonical transport/provider composition and hardware behavior
remain separate gates. This verifies selected source-owned product state without
asserting vendor provenance or whole-image completion.

The STACMD registered wire path now directly executes recovered registry
registration/dispatch and attributable pinned musl strcmp.192 comparisons
through22 provider bodies match insertion, duplicate rejection, open/close and
request dispatch, including192 actual strcmp calls per implementation. GPIO
and disabled logging remain fixtures; canonical hardware/logger and higher
transport composition remain gates. Product provenance and original Arm runtime
identity are kept separate from this verified libc reuse.

The registered STACMD path now executes the pinned nRF5 SDK17.1.0 GPIO HAL wrappers
directly, with192 comparisons through27 provider bodies and no GPIO interception.
Native/source ordered register accesses and final modeled peripheral state match.
This validates actual Nordic source reuse alongside pinned musl strcmp, preserving
separate provenance for product wire logic. Peripheral input waveforms and
disabled logging remain modeled; physical hardware timing, logger/higher
transport composition and canonical admission remain gates.

The eight recovered STACMD source modules and cold counter are now canonically
integrated with the existing source-owned configuration and admitted Nordic/
musl providers. Canonical unresolved symbols drop60→56 with no new dependency;
the full canonical suite and dependent stage checks are refreshed. This is
source-provider admission, distinct from higher transport/enabled retry logger
composition, physical proof or whole-image byte identity. Product reconstruction
and attributable SDK/libc lineage remain separately recorded.

YHM transport/request cold storage is now source-owned from40 authenticated
initial bytes under four RAM poisons. Readiness binds the existing canonical
STACMD configuration, reusing its typed record and admitted Nordic GPIO path.
832 frontend comparisons pass, and a combined YHM source stage adds no unresolved
dependency. Runtime lifecycle/executable transport composition and full startup
remain gates. These product-state recoveries do not acquire vendor provenance
through the SDK or contextual YHM model.

The selected YHM handle/transaction path now directly executes recovered registry,
STACMD and pinned Nordic GPIO plus musl strcmp in192 comparisons. Source compiler
inlining of three helper bodies is explicitly accounted for; memory, dispatcher,
peripheral and completion behavior match native execution. Raw completion return
is not interpreted as wire success. Other device bindings, enabled logger and
charger/status composition remain gates, with product versus SDK/libc provenance
kept separate.

Raw YHM status now compiles with55,296 native comparisons through its actual
classifier/adapter graph. Explicit register capture/restore preserves native
incoming-r3/no-write behavior rather than substituting the contextual reader's
initialized-byte/read-result policy. Fresh REA and native bytes support the
contract; compiler/prologue/LTO portability and actual lower-provider composition
remain gates. These register-boundary/product semantics are recovered source,
without vendor-source attribution.

The YHM system-track initializer and battery adapter now compile with80,184
comparisons, preserving initialized read-byte behavior, register1 bit1 setting,
raw return and incoming-register high bytes. Descriptor IDs match native data;
logger interfaces remain reusable admitted providers but are fixtures in this
receipt. The updater explicitly discards the raw return and its three runtime
receipts pass again. Actual provider composition and compiler/physical/full-image
identity gates remain separate from this owner-authorized product reconstruction.

### Charger status provider composition

The new144-case actual status graph reuses the existing pinned Nordic SDK GPIO and musl strcmp providers through the shared stock registry, rather than adding product-local substitutes. Hash-bound reports preserve upstream attribution. Raw status, charger classification and the incoming/return r3 boundary remain R1-specific source; successful native replay establishes selected semantic behavior, not original upstream equivalence, instruction identity or hardware proof. Fresh REA/Ghidra-MCP evidence for ADC filter0x91184 identifies the next product adapter around the Nordic acquisition boundary; SDK driver internals remain the upstream reuse target.

### R1 ADC filter around upstream acquisition and delay

`native_battery_filter.c` implements the authenticated R1-specific five-sample policy rather than replacing the ADC driver: discard the two lowest samples, retain three, and apply the observed wrapping integer conversion. Its provider seams remain the shared stock registry, Nordic `nrf_delay_ms` and CMSIS-FreeRTOS `osDelay`. Existing ownership attribution maps those delay functions to pinned Nordic SDK17.1.0 and CMSIS-FreeRTOS10.5.1; Nordic SAADC internals remain the upstream implementation target.7,104 direct comparisons and2,896 actual updater/filter/statistics/control comparisons establish selected product semantics with explicit ADC/delay fixtures. No claim of actual upstream ADC composition, whole-image byte identity or physical sampling proof is made.

### Discharge calibration belongs to the R1 product layer

The recovered discharge body and four structured voltage/weight tables are R1-specific evidence-backed source, not an upstream battery library.480 compiled table bytes match the authenticated artifact;262,687 direct comparisons and2,896 integrated updater comparisons pass. This preserves the upstream reuse boundary: Nordic acquisition and delay internals, CMSIS scheduling and the shared registry stay separate providers. The battery configuration getter and runtime state ownership remain explicit dependencies; table-byte equality does not establish code-byte or complete-image identity.

### Battery record access reuses cached-class and musl providers

The three R1 battery configuration getters now use the existing authenticated `r1_kv_class_read` body and pinned musl memory-copy implementation rather than a new record-reader substitute. Native incoming/return r3 behavior and byte/signed-half/boolean extraction are product-specific source.196,752 direct comparisons and23,040 cached-class/musl comparisons pass; the actual battery graph adds2,896 comparisons with valid four-byte records. Port callbacks, persistent handle initialization and rejected-size caller composition remain separate gates. This does not establish flash persistence, complete startup or image identity.

### Product charging cadence keeps CMSIS tick seams

The charging cadence body is R1-specific policy using existing CMSIS `osKernelGetTickCount`/`osKernelGetTickFreq` seams and the authenticated battery configuration getter. Source preserves unsigned elapsed wrapping, capped seconds and threshold-driven level advancement; it does not introduce a competing scheduler or tick model.6,616 direct and2,896 integrated comparisons pass with tick endpoints modeled. The mutable four-row threshold region remains an initialization/source-ownership gate, and the original runtime division instructions are not claimed byte-identical to the equivalent source division.

### Recovery policy composes existing product and CMSIS/Nordic seams

The R1 stuck-charge recovery body now compiles around existing CMSIS tick seams, the authenticated progress-reset provider and established Nordic/structured logging interfaces. Its120-second timeout, voltage/level checks, initial-charge estimate clamp and saved argument-register/log-stack behavior are product-specific source.11,460 direct comparisons and2,896 actual battery graph comparisons pass. The initial-charge curve remains an explicit provider gate; enabled logs are directly replayed, while the full graph uses disabled logging. No new scheduler, logger, persistent-state default or upstream ADC substitute is introduced.

### Initial-charge estimate stays in the product policy layer

The initial-charge curve now uses its own authenticated R1 calibration and unsigned interpolation rather than reusing discharge's different tables/signed arithmetic.480 structured table bytes match the locked image, including the first table's descending final interval.262,538 direct and2,896 integrated comparisons pass; the integrated graph now executes the actual curve on312 recovery paths. The shared configuration getter continues through the existing cached-class reader and pinned musl copy. Remaining upstream hardware, timing and logger composition and source-owned initialization gates remain explicit; calibration byte equality is not complete firmware byte identity.

### Battery diagnostics reuse established logging and record seams

R1 diagnostic cadence now compiles around the existing product configuration getters and structured/Nordic logging APIs. Product counter policy, descriptor text and native headers remain authenticated R1 source; logger internals stay attributable upstream providers.39,936 direct comparisons include enabled log variants and callback mutation;2,896 integrated updater comparisons use disabled logging.286 compiled descriptor bytes match the locked artifact. Enabled full-graph logger composition, initialization, hardware and original image identity remain separate gates.

### Low-battery product policy preserves shared provider seams

Low-voltage escalation is now authenticated R1 C around the established structured/Nordic logger, shared event API, time backend, device-info KV consumer and CMSIS thread-flags interface. Counter thresholds and native packed-record/register behavior are product policy, not a substitute upstream scheduler or persistence implementation.53,248 direct comparisons and2,896 integrated cases pass, including920 complete record submissions and5 event-tail paths. The downstream voltage/time/KV/event/thread endpoints remain fixtures in this graph; their existing source, attribution and exact provider composition must be verified independently before admission.104 compiled descriptor bytes match the artifact; complete firmware byte identity remains open.

### Device-info field updates reuse authenticated cached-class and musl bodies

The R1 device-info setter now compiles as C field-update logic with an explicit native stack-frame ABI boundary. It calls the existing cached-class read/write bodies and pinned musl copy provider rather than adding a separate persistence implementation.72,017 direct comparisons and2,896 integrated cases pass, including920 actual cached-node updates. The failed-read frame is preserved as raw incoming target memory; no default record is invented. Port callbacks, initialization, rejected-size caller composition and actual flash persistence remain gated, as do compiler identity and complete-image equality.

### Voltage getter reuses the product configuration and compiled battery service

The R1 voltage getter now calls the established configuration accessor and the explicit NOP-prefixed battery service rather than introducing a separate ADC/update algorithm.262,384 direct comparisons and2,896 actual service/updater graph cases pass. The prefix ownership overlaps the existing updater; its4-byte observed extent and412-byte span are recorded separately. Actual advertising/KV configuration and recursive refresh composition remain gated, with upstream CMSIS/Nordic hardware seams retained. This source milestone does not establish complete image linking or byte identity.

### Glasses battery frame preserves shared BLE dispatch seams

The R1 battery-frame wrapper now compiles around the existing connection getter and type0 BLE queue interface. It preserves the product tag bytes, two handle reads, raw return and native three-word register restoration.66,536 direct comparisons and2,896 integrated cases pass; the latter contain1,873 dispatches and950 skipped sends. Connection/queue endpoints remain fixtures, so this is not transport acceptance or device delivery proof. The lower queue should compose with existing attributable RTOS/memory/BLE providers rather than a new packet queue implementation; protocol status reporting and exact composition remain gates.

### Battery TX graph reuses existing producer and memory providers

The frame graph now executes existing connection getters, typed TX veneer, common producer and pinned musl copy, instead of adding another packet queue.2,896 native/source cases cover allocation rejection, near-full queue diagnostics with disabled logging, accepted modeled puts and failed-put ownership cleanup. The queue/heap/thread APIs remain established CMSIS/FreeRTOS seams; actual provider composition and BLE worker delivery remain separate gates. Fresh REA/Ghidra evidence attributes the shared536-byte native range to the compiled private producer and resolves one manual inventory route without modifying the locked ledger.38 source-owned initialization bytes match poisoned native cold startup; this is not full-image or hardware proof.

### Protocol battery report reuses established logger and operation transport seams

The R1 protocol-status sender now compiles around structured/Nordic logging and the operation1 phone-command provider. Product packet encoding, descriptor text and native saved-register behavior remain authenticated R1 source.160,992 direct and2,896 integrated comparisons pass, with1,071 lower operation calls in the latter.126 compiled descriptor bytes match the locked artifact. The next implementation target is the existing operation transport path, retaining shared BLE/RTOS/memory providers rather than adding a parallel reporting transport; delivery, initialization and exact image identity remain gated.

### Phone operation transport reuses the existing connection getter

The R1 operation1 and common response-header wrappers now compile around the authenticated connection getter and shared lower response-send interface.98,176 direct and2,896 integrated comparisons pass with exact header packing, null/sentinel behavior and register/return contracts. The actual phone getter is reused; no parallel connection state implementation is added. The next boundary is0x828b4 allocation/serialization, which should reuse established memory/RTOS/BLE providers where its authenticated contract permits. Lower delivery and source/whole-image admission gates remain explicit.

### Response sender retains heap, serializer and transport provider seams

The R1 response sender now compiles around shared allocation/free, connection gates, serializer and send-hook APIs, plus existing structured/Nordic logging.100,480 direct and2,896 integrated comparisons pass with the native16-bit allocation-size wrap and full32-bit serializer length preserved. The next targets are the authenticated serializer and hook/gate bodies, reusing attributable memory/RTOS/BLE or checksum code where exact contracts permit. Current fixtures prove boundary behavior and cleanup, not actual allocation bounds, delivery or complete-image identity;290 compiled descriptor bytes match the artifact.


### Encoder reuses pinned musl movement and recovered checksum

The product encoder now executes the existing pinned musl1.2.5 memmove dependency (commit0784374d561435f7c787a555aeab8ede699ed298) and recovered source CRC16-Modbus. Upstream movement remains separately attributed and replaceable subject to the native contract suite; product wire encoding and cold sequence/version state remain R1 source.6,600 direct and2,896 integrated comparisons pass. Cold initialization covers six bytes across four poisoned starts; complete startup, hardware delivery and original-image identity remain open.


### Protocol callbacks reuse shared connection state

The callback dispatcher and both handle-presence predicates now compile as authenticated product C, reusing source-owned connection fields rather than introducing a second BLE state model.8,232 dispatcher and131,072 exhaustive predicate comparisons pass; two2,896-case graphs execute the shared encoder, pinned musl movement and recovered checksum. Nordic BLE/RTOS providers remain the composition targets below the registered callback. Historical authenticated naming is not evidence of authentication. Registration/target execution, hardware delivery and byte-identical firmware remain explicit gates.


### Callback registration closes another product seam

The product callback registrar now compiles and composes with existing dispatcher/connection/encoder providers, including pinned musl movement.65,544 direct and2,896 integrated comparisons pass; null registration retains the previous callback. The next fragmenter uses already compiledCRC32 update and muslmemmove, avoiding duplicate checksum/memory implementations. REA entry absence remains explicit alongside lockedledger/nativecall/Ghidra-MCP attribution. Registered target, complete startup, physical delivery and image identity remain gated.


### Fragmentation closes onto the existing type1 BLE producer

The product fragmenter reuses recovered CastagnoliCRC32 and pinned musl1.2.5 movement, then the already compiled type1 veneer/shared BLE TX producer. It introduces no alternate queue or checksum implementation.4,957 direct and two2,896-case integrated native/source comparisons pass. Four source-owned cold callback bytes are represented by a symbolic relocation to the shared provider, matched across four SRAM poisons. Heap/RTOS queue/notification composition and physical delivery remain separate gates; upstream updates must pass the native contracts before adoption. REA boundary absence and locked-ledger/Ghidra-MCP attribution remain recorded.


### Protocol initialization composes established providers

The portinitializer and receive registrar now compile against the existing product fragmenter/sendregistrar, shared connection/TX state and logging seams.66,472 direct and2,896 integrated comparisons pass;320 descriptorbytes and4 cold receive-slotbytes are source-owned. This preserves reuse of recovered checksums, pinned musl movement and the shared type1producer rather than adding a separate transport. The ingress target remains a symbolic unexecuted provider, and actual Nordic logger/RTOS/hardware composition remains independently gated. REA entry gaps retain lockedledger/nativecall/Ghidra-MCP attribution.


### Receive dispatch retains the initialized shared callback slot

The recovered product receive dispatcher reuses the source-owned callbackslot and protocol initializer.16,848 direct and2,896 integrated comparisons pass, including tailABI, shortcircuit rejection and mutablecallback logging. It introduces no alternate receive transport; the actual registered ingress/module handlers are the next source boundaries. Existing Nordiclogger/CMSIS/FreeRTOS seams remain independently composable dependencies. Header/CRC validation, fullstartup and device delivery are not implied by callback-boundary equivalence.


### Ingress preserves shared module registration

The product ingress compiles against the existing initialized receive path, source-owned symbolic module table and logger interfaces.72,220 direct and2,896 integrated comparisons pass; module/special bodies remain explicit callbackfixtures. The16-byte module table uses Csymbolrelocations instead of executable data or a second registration framework. Downstream handlers should compose with established CMSIS/FreeRTOS, Nordiclogger and productcommand providers as authenticated bodies become available; fullstartup, device proof and byteidentity remain separate gates.


### Module wrappers share the native command lookup and symbolic tables

System, health andspecialmodulewrappers now reuse one recovered lookup, preserving nativeunsignedindexwrap instead of substituting a generic safe binarysearch.196,818 lookup and4,104 wrappercomparisons pass; a2,896-case graph exercises all35 symbolic leaf references.280 tablebytes compile from source with handlerrelocations. Those references remain explicit leafdependencies; nine targets require exact-entry ownership attribution. Existing checksum/musl/TX/RTOS/logger providers remain shared downstream; physicalfault behavior, fullstartup and imageidentity are separate gates.


### Event leaves retain the shared product event publisher

The specialregistered target andactivityrefresh leaf now compile around the existing r1_event_publish API rather than introducing another queue.154,378 direct and2,896 integrated comparisons pass, retaining the native incomingr3 eventword and raw return/tail behavior. The special24-byte body is supplementally attributed without rewriting the lockedledger; eight other exacttargets remain attributiongaps. Existing eventpublisher/CMSIS/FreeRTOS/heap/musl providers are the next composition seam, with its uninitialized leadingrecord and physical delivery kept explicit.


### Device-status replies reuse the battery getter and complete transport

The statusleaf andtwo chargepredicates now reuse the existing source-compiled charge-bytegetter, phoneoperation/header/response path, recoveredCRC andfragmenter, pinnedmuslmovement andsharedtype1TX producer.381,191 direct and2,896 integrated comparisons pass, including9 actualstatusrequests and5 encodedstatusreplies. Eight defaultrecordbytes are source-owned. No alternate status transport or duplicated getterpolicy is introduced. Rawcharger/conditionalrefresh andactual heap/RTOS/hardware remain separate composition gates.


### Device information reuses clearing and the shared response path

The device-info body and operation2wrapper reuse existing EABI/musl clearing, connection/header/response, checksum/fragment and type1TX providers.133,597 direct and2,896 integrated cases pass for the stated r0/r2/r3/payload domain; r1scratch differences remain recorded.25 fixed stockmetadata bytes are source-owned. Generic snprintf is an explicit unresolved boundary. The installed GCC9toolchain identifies Newlib3.3.0; [official Newlib source access](https://sourceware.org/newlib/download.html) supplies a sourcecandidate for future runtime work, not original Arm-runtime identity. Pin/license/build/generic-format/nativecontract gates remain before adopting it.

### Generic formatter dependency closure checkpoint

`build_newlib_stdio.py` now builds 19 unmodified Newlib 3.3.0 units, nine pinned
LLVM compiler-rt units and one local EABI comparison adapter, reusing six
hash-validated source objects for integer division and memory. The Newlib
revision is the one documented by the cached GNU Arm toolchain release.
Selected source, licenses, mirror archive, installed public/configuration
headers, private headers and emitted objects are hash-bound. snprintf/vfprintf
also match primary bytes; complete primary retrieval was rate-limited.

Only `__assert_func`, `__malloc_lock`, `__malloc_unlock` and `_sbrk_r` remain
unresolved. They are explicit boundaries in the execution experiment, not
claimed source providers. The source allocator/locale bodies actually execute.
All 35,072 core-register EABI comparison checks pass against binary64 ordering.
The native formatter experiment produces 139 matches and 86 differences across
225 cases, with zero execution errors. `%p`, `%a` and exceptional/extreme float
behavior furnish concrete counterexamples to generic equivalence. Native
startup, concurrent state, complete ABI and instruction identity remain gated.

Do not admit this candidate as a replacement for 0x38080/0x43080. Preserve its
pinned sources unchanged as attributable reusable machinery and a comparison
reference. Reconstruct the native parser/conversion behavior from the locked
corpus and authenticated body evidence, retain these counterexamples, and
repeat native comparisons after upstream repins. Compatibility with an upstream
standard library cannot establish the required stock byte-identical rebuild.

The native formatter output layer now has three recovered C providers and
hash-bound native comparisons (`native-formatter-output/`). Native disassembly
requires decrement-before-signed-test padding and volatile store ordering for
bounded output aliases; these behavior contracts differ from simply choosing
an upstream printf implementation. All225 native graph cases match with these
C helpers. The main native parser and decimal conversion remain the next
reconstruction targets; the Newlib/LLVM source candidate remains a reusable
reference rather than an admitted generic replacement.

Recovered native decimal conversion at0x3f530 now compiles and passes4,818 native
comparisons with exact binary64 helper-argument traces. It uses the existing
pinned LLVM/recovered integer division provider, while four original binary64
arithmetic entries still execute as explicit gates. The native power-of-five/
power-of-two scaling and17-digit extraction must remain distinguishable from
Newlib dtoa. The225-case mixed formatter graph matches with the C decimal body
and C output helpers; generic parser/wrapper and arithmetic source closure are
still required. REA pins the outstanding arithmetic bodies at0x27c4a (228B),
0x27d2e (222B),0x27afc (322B) and0x28334 (48B). These extents are evidence,
not source or instruction-identity completion.

The native unsigned binary64 conversion (0x28334) now uses recovered C source
and existing source shift providers. Its sign-discarding and oversized-shift
behavior passes 81,920 native comparisons. A direct C cast or generic upstream
saturating conversion would change this contract. Decimal and formatter graph
receipts in `native-formatter-unsigned/` retain 4,818 and 225 matching cases,
respectively. Three native binary64 arithmetic providers remain: multiply,
divide and add. Continue evaluating pinned compiler-rt reuse against those
actual bit contracts rather than inferring identity from standard helper names.

Native binary64 addition and its signed-shift, rounding and normalization
helpers now compile from recovered C (`native-formatter-add/`). They reuse the
existing source logical shifts. All 52,778 direct comparisons, 4,818 decimal
chain cases and 225 formatter cases pass. Native multiply/divide also call the
new C normalization/rounding providers in the mixed graph.

A direct pinned LLVM compiler-rt addition experiment records 2,441 matches and
183 counterexamples across 2,624 cases. For example, adding two smallest
positive subnormal bit patterns yields native `0x0010000000000001`, while LLVM
returns `0x0000000000000002`; signaling NaN quieting also differs. These are
observed bit contracts, not generic IEEE compliance claims. Retain the pinned
upstream implementation as a reference and upgrade candidate, but do not admit
it as native-equivalent. Original multiply/divide and parser/wrapper source
closure, complete ABI and instruction identity remain required.

Native multiply/divide now compile from recovered integer C algorithms and use
the existing source normalization/rounding helpers. The complete decimal
arithmetic dependency bundle links with no undefined symbols in
`native-formatter-math/`; its integer runtime reuses pinned LLVM unsigned
division. No native floating arithmetic import remains in the 4,818-case
decimal chain or the 225-case mixed formatter experiment. Direct product and
division comparisons pass 263,712 cases.

These native bit contracts preserve exceptional/subnormal behavior rather
than replacing it with the incompatible generic upstream behavior already
recorded. Retain the pinned Newlib/LLVM formatter candidate and counterexamples
as upgrade/reuse evidence. Main parser and variadic wrapper source, complete
ABI, original instructions and whole-image identity remain separate gates.

The recovered native formatter parser now compiles against the existing source
math and padding providers. `native-formatter-engine/` is a zero-undefined-symbol
source engine, including native format rules that differ from Newlib/LLVM.
Direct verification passes 39,002 cases and the mixed variadic-wrapper graph
passes all 225 cases. The recovered integer runtime still benefits from pinned
LLVM unsigned division. Preserve the upstream candidates and their recorded
counterexamples for future controlled repins rather than substituting generic
printf semantics. Variadic wrapper source, complete native frame/register/flag
ABI and original image identity remain required.

Bounded native formatter closure now includes source snprintf/vsnprintf. Their
C worker uses the recovered parser and output providers; source-compilable ABI
adapters preserve the native argument stream and outer frame layout. The linked
`native-formatter-runtime/` has no undefined symbols and reuses pinned LLVM
unsigned division through the integer runtime. Public native semantics are
preserved rather than substituting the incompatible Newlib/LLVM candidates.

Actual formatting replaces the device-info fixture in both the 65,637-case
direct graph and the broader 2,896-case protocol/battery graph. The latter keeps
its 655 actual encoder/CRC/fragment/TX operations. Source math/body availability
and these tests do not close zero-capacity r1 scratch, arbitrary private-stack
aliases, exact instruction identity, physical delivery or the remaining whole
firmware components. Retain upstream provenance, comparison counterexamples
and the prior fixture receipts as historical evidence.

The stdout dependency at 0x319e0 is SEGGER_RTT_Write. The recovered wrapper now
calls the existing unchanged pinned SEGGER RTT 6.18a no-lock ring implementation
and native source initializer. It preserves the native BASEPRI 32 critical
section and low-byte restoration; generic SDK lock/initializer configurations
are not substituted. New header dependencies are checked against the existing
authenticated SDK report. Native instruction evidence resolves decompiler
privilege predicates: there are no separate privilege-test branches here.

This upstream reuse closes the source stdout backend path. The four formatted
output entrypoints and RTT/memory providers link without undefined symbols.
Direct RTT tests pass 3,538 cases;972 actual-source printf cases produce9,900
matching ring writes per side. Live debugger concurrency and blocking without
available space remain gated. The 10-byte buffer-putc object section is a real
compiled instruction-byte match, explicitly separate from image placement and
full identity. Future SEGGER/memory/runtime upgrades must retain the existing
pins or regenerate provenance and repeat native contracts before admission.

Eleven additional native floating-bit helpers now compile against the existing
source arithmetic/normalization and pinned LLVM unsigned integer runtime. The
combined `native-float-bits-runtime/` has no undefined symbols. Native exponent,
NaN, signed-zero and register-shift behavior is retained: generic C casts and
upstream IEEE helpers cannot be substituted by name. Direct comparison passes
459,814 cases, plus 1,552 cases through 23 still-native math consumers. The
classifier register counterexample remains attributable evidence for future
compiler/upstream upgrades. Reuse the pinned provider graph and repeat these
contracts on repin; consumer source, complete ABI and whole-image identity
remain separate gates.

The native hard-float polynomial evaluator now reuses recovered source binary64
add/multiply and the existing pinned integer runtime instead of importing a
generic upstream polynomial/math routine. Its 3,840 direct comparisons execute
59,748 source add/multiply calls each; 1,552 native-consumer cases include 148
actual source polynomial calls. A generic libm replacement still requires
independent native semantic/ABI comparison and attributable source provenance.
The linked source bundle has no undefined symbols; the 23 consuming libm bodies
and remaining firmware source routes stay open.

Signed64-to-binary32 now has a positive upstream reuse candidate: unchanged
LLVM compiler-rt 20.1.8 `floatdisf.c`, `int_to_fp_impl.inc` and `int_to_fp.h`, pinned
to commit `87f0227cb60147a26a1eeb4fb06e3b505e9c7261` with existing licensed headers.
The upstream implementation defines conversion rounding toward even:
https://github.com/llvm/llvm-project/blob/87f0227cb60147a26a1eeb4fb06e3b505e9c7261/compiler-rt/lib/builtins/floatdisf.c
Its EABI core-register return matches 139,456 native integer samples, with stack,
callee registers and FPSCR preserved. Source/provenance/build/comparison receipts
are in `llvm-signed64-float32/`. It remains a nonselected candidate pending
complete ABI/instruction requirements; no generic exceptional floating rule is
admitted by this integer-only result. Controlled repins can repeat this contract.

The selected native conversion/integral rounding bundle reuses the already
tested `structured-float` remainder primitive and pinned LLVM integer shifts,
with recovered native binary64 rounding. Four additional routes compile; the
shared interior packer contributes no duplicate body bytes. Direct 232,492 and
native-consumer 1,552 cases pass. The linked bundle has no unresolved symbols;
full consumer source and original image identity remain separate gates.

The native binary64 square-root recurrence now compiles against the existing
source remainder-rounding provider and pinned LLVM integer shift runtime.
Its exceptional/subnormal and signed-encoding behavior is retained; a generic
libm square root is not admitted as equivalent by name. Native public sqrt and
VFP sqrtf now use the source helper and source errno cell/setter. The latter
uses the authenticated single SRAM cell rather than assuming a generic libc
thread-local errno layout. Source initialization/final placement remain open.

The complete square-root source bundle links without undefined symbols.
Raw helper comparisons pass 73,728 cases; public wrappers/setter pass 237,568,
including 48,504 native-matching float-domain errno writes. The 1,552-case graph
uses source sqrt/sqrtf; 21 other consumer bodies remain native. This extends
reuse of the pinned integer runtime while preserving native contracts, with
full ABI/instruction and whole-image gates unchanged.

The next eight recovered math routes preserve native raw compare ordering,
FPSCR-affecting directed rounding and comparison-based absolute value. The
source bundle retains pinned upstream providers through the existing runtime
graph without modifying them. Native ceilf/floorf execute their authenticated
huge-value addition and signaling comparison; comparison-based fabsf preserves
negative zero and NaN behavior. Generic libm symbol names do not establish a
substitution contract. The core-register fabs entry also returns the result in
D0; both core and FP outputs are now checked.

Direct tests pass 483,940 cases and the expanded source math graph passes
1,952. Eight of its 27 consumer bodies execute source; 19 remain native. New
literals total 20 bytes with exact native values. Zero undefined symbols does
not close original ABI/frames, final placement or firmware byte identity.
Live function metadata is absent at0x98eca; retain that gate and the negative
REA/Ghidra results with the locked corpus, exact byte spans, disassembly and
native execution evidence. Future compiler/upstream repins must repeat these
bounded contracts and preserve the unresolved identity requirements.

The recovered binary64 comparison entries at 0x27f0c/0x27f3c now compile with
native encoded-key ordering, transformed R0..R3 outputs and APSR flag results.
They are separate from the existing pinned LLVM boolean comparison adapters:
matching a generic EABI comparison name does not establish this physical
register/flag contract. C workers and small ABI adapters retain R12 and LR;
complete private-frame/architectural identity remains gated.

Direct comparisons pass 312,896 cases and the 1,952-case math graph executes
136 forward plus 84 reverse source comparisons. The zero-undefined runtime
bundle continues to reuse the existing pinned arithmetic/integer providers.
Eight graph consumer bodies are source and 19 remain native. Future upstream
or compiler repins must retain these register/flag comparisons alongside
numerical tests; whole-image byte identity is still an independent requirement.

Native double ceil/floor now compile against recovered source add,
reverse-subtract and physical binary64 comparison providers. Their one-statement
call/flag capture retains the private flag result across compiler scheduling.
The existing runtime provenance graph and upstream pins remain intact; generic
libm replacements are not inferred from API names. Source-owned constants
preserve the native huge-value and mask tables rather than importing binary
executable regions.

The direct contract passes 403,328 cases and the complete linked source bundle
has no undefined symbols. Its 1,952-case graph executes source ceil/floor,
bringing the graph to ten source and 17 native consumer bodies. Native frame,
remaining raw register/flag, physical hardware, final placement and whole-image
byte requirements remain separate from these numerical/source-build results.

Public round/roundf now compile against the recovered integral rounding and
arithmetic/physical flag providers. Double round preserves native encoded-key
comparisons rather than substituting the pinned LLVM boolean comparison
adapters. Float round retains native VFP subtraction/adjustment, signed-bit
branches and final input sign restoration. Existing upstream pins/provenance
remain intact; API names alone still do not establish native interchangeability.

Direct verification passes 376,832 cases, including halfway integers and
adjacent bit patterns. The 1,952-case graph now executes twelve source consumer
bodies with 15 still native, using a zero-undefined-symbol bundle. The double
body's 192 bytes occupy two ranges across a 194-byte span; the initial prefix
read is not promoted to full-span proof. Preserve this distinction, the source
24-byte constant table, and raw ABI/frame/whole-image gates on future compiler
or upstream repins.

Twelve exceptional-path leaf entries now compile against the existing source
math graph. Binary64 entries reuse recovered software add/multiply/divide and
its pinned integer runtime dependencies; binary32 entries retain native VFP
operations and FPSCR effects. Generic upstream exceptional helpers are not
substituted by name. Shared tanh/pow/tanhf/tanf tails remain attributable entry
contracts rather than complete parent-function source.

Direct comparisons pass 309,828 cases; the actual zero-undefined source bundle
passes the 1,952-case graph. The float self-add/pair-add C sections also match
two native six-byte instruction spans without relocations. Retain these real
section-local byte receipts separately from final image placement/identity.
Live metadata at0x3bace remains absent, with negative REA/Ghidra results retained
alongside locked pseudocode, exact bytes, disassembly and native entry tests.
The source constant spans total 56 bytes. Full ABI/private frames, parent source,
physical hardware and whole-firmware byte identity still require evidence on
future compiler or upstream repins.

Native expf/tanhf now compile with their authenticated numeric tables, VFP
operation/conversion order and source errno/special-value providers. Tanhf
calls the new source expf; its already compiled self-add tail is reused rather
than duplicated. Three native PC-relative table offsets are resolved into named
C table references. No unverified generic exp/tanh implementation is admitted
by symbol name, and the existing pinned provider provenance remains unchanged.

Direct comparisons pass 672,832 cases with 127,084 matching expf errno writes.
The zero-undefined source bundle passes the 1,952-case graph, now fourteen source
and thirteen native consumer bodies. New disjoint instructions account for
634 native bytes, with six shared bytes reused and 116 source-owned numeric
bytes. Original pointer/instruction layout, full ABI/private frames, hardware
and complete firmware identity remain separate requirements for future
compiler/upstream changes.

Native logf/log10f now compile with recovered range reduction, both polynomial
paths and named high/low tables. Their VFP zero comparisons and normalization
are retained, including flush-to-zero-dependent errno behavior. The source
kernel uses existing source special-value/errno providers and leaves all pinned
upstream provenance unchanged. A generic logarithm implementation is not
admitted by symbol name or ordinary-value agreement.

Direct comparison passes 694,592 cases with 171,856 matching errno writes per
routine/side. The zero-undefined bundle passes the 1,952-case graph, now sixteen
source and eleven native consumer bodies. Recovered data totals 208 bytes;
four native PC-relative table offsets become named C array references. Retain
original pointer/instruction layout, raw ABI/private-frame, physical hardware
and full firmware byte requirements as separate gates on future repins.

Native atanf now compiles with recovered split constants, reciprocal/half
argument reductions and explicit VFP polynomial order. It reuses the source
classifier, underflow and NaN self-add entries in the existing pinned provider
graph; no generic atan implementation is admitted by symbol name. The source
owns 56 constant bytes, authenticated independently of compiler layout.

Direct comparison passes 467,488 cases. The zero-undefined source bundle passes
the 1,952-case graph, now seventeen source and ten native consumer bodies.
Preserve native FPSCR/underflow behavior and the distinct raw ABI/private-frame,
physical hardware, final placement and full firmware identity requirements on
future compiler/upstream repins.

Native atan2f now compiles with recovered quadrant/reduction constants and
source classifier, underflow, errno and pair-add dependencies. Exceptional
integer classification updates are kept separate from live FP operands;
replacing these rules with a generic upstream atan2 by API name is not admitted.
The existing pinned provider graph remains unchanged beneath the new C body.

Direct comparison passes 942,112 binary32 pair cases, with the corrected
coverage label bound to a full replay. The zero-undefined source bundle passes
the 1,952-case graph, now eighteen source and nine native consumer bodies.
The source owns 88 numeric bytes. Retain the coverage-label counterexample,
raw ABI/private-frame, physical hardware, final placement and full firmware
identity requirements on future compiler/upstream repins.

The native float trigonometric reducer at `0x3bb04` now has a separately gated,
C-compilable implementation (`native-trig-reduce/`): 212,992 direct comparisons
and a zero-undefined partial runtime link. Its invalid-input raw S0 preservation,
signed table indexing, fixed-point product carry chain, and ordered nonfused
VFP operations are authenticated native contracts. No new upstream identity is
asserted for this body. Existing pinned compiler/runtime dependencies remain
attributable and independently replaceable; substituting a generic upstream
argument reducer would require a separate compatibility assessment. Consumer
admission and complete firmware integration are still pending.

Reducer integration checkpoint: its source object passes the 1,952-case math
consumer graph, with 48 actual compiled entries. Strict frontier admission is
now verified (701 tested, 1,372 compiled hints, 1,253 unresolved). Nine graph
consumer bodies and whole-image integration still require source work. The
remaining trigonometric parents can reuse this authenticated source dependency;
no new third-party origin claim is implied by graph equivalence.

The cosf source body now reuses authenticated source trig reduction and shared
errno/invalid/self-add providers, with 470,752 direct cases and 56 compiled
entries in the 1,952-case consumer graph. The full 280-byte entry body and
56-byte numeric block are authenticated; no additional upstream provenance is
asserted from a standard function name alone. Existing pinned LLVM and other
attributed dependencies remain distinct reusable providers. An upstream cosf
replacement would need to retain or separately assess this firmware's threshold,
four-subtraction reduction, nonfused polynomial and exceptional-value contracts.
Whole-image C integration and instruction identity remain gated.

Native sinf now reuses the source trig reducer, binary32 classifier and
underflow/invalid/self-add/errno providers. It passes 470,752 broad direct cases,
1,088 exact tiny-boundary cases and the 1,952-case graph (56 compiled entries).
Its 344-byte body and 56-byte data block are authenticated independently of
provenance. No third-party origin is inferred solely from a standard API name.
Existing attributed dependencies remain separately pinned and reusable; future
upstream math substitutions must account for the recovered tiny-input side
effects, range thresholds, nonfused operations and exceptional dispatch.

Native tanf now reuses source trig reduction, classification, low-square,
invalid/self-add and errno providers. Its direct 474,016 cases and 1,952-case
consumer graph pass (56 compiled tanf entries). Authenticated native disassembly
resolves the frozen decompiler's indirect-branch warning as conditional return
versus reciprocal, so no unknown jump-table provider is introduced. The
332-byte analyzed body includes ten bytes already owned by the shared invalid
helper; only 322 main bytes are newly covered. No upstream origin is inferred
from the API name or polynomial resemblance. Existing attributed dependencies
remain independently pinned; replacements still require native-contract and
instruction/image assessment.

The binary64 atan body now reuses the recovered source arithmetic, polynomial,
classification/absolute-value and exceptional providers. Its 37,436 direct
cases and 1,952-case consumer graph pass, with 56 compiled atan entries. The
622-byte body, 240 numeric bytes and four PC-relative table contracts are
independently authenticated. Polynomial resemblance does not by itself establish
upstream authorship; no new provenance claim is added here. Existing attributed
providers remain separately pinned and replaceable, with native arithmetic,
reduction and instruction/image compatibility still requiring explicit checks.

The binary64 tanh C body reuses existing source arithmetic, classification,
absolute-value and exceptional helpers. Its remaining internal expm1 provider
is explicitly unresolved. Bounded tests use stock expm1 as a named native
fixture; their 37,316 direct and 1,952 graph cases do not establish expm1 source
completion. REA authenticates the pending 1,092-byte provider ranges. This is
an internal implementation gate and carries no new upstream provenance claim.

Source expm1 now resolves the tanh candidate's native dependency. It reuses the
existing source raw arithmetic, integer conversion, flag comparison, polynomial,
errno and exceptional providers. The 37,696 expm1 and 37,316 source-dependent tanh
cases pass, as does the 1,952-case consumer graph (20 compiled expm1 entries).
The partial runtime has no undefined symbols or native expm1 fixture binding.
The polynomial shares eight authenticated bytes with the recovered reducer
prefix; provenance and unique-byte accounting remain explicit. No new upstream
authorship is inferred from coefficient similarity. Final source integration,
placement, original instructions and byte equality remain separate gates.

Binary64 exp now reuses the existing source raw arithmetic, integer conversion,
flag comparison, polynomial, classification, errno and exceptional providers.
Its 714-byte body, 208 numeric/padding bytes and four table-pointer contracts
are authenticated by REA/Ghidra-MCP evidence. All 37,776 direct cases and
1,952 consumer cases pass with 56 compiled exp entries and no unresolved
runtime symbols. No new upstream authorship is inferred from API or coefficient
similarity. Native two-stage subnormal scaling and exception contracts remain
requirements for any future upstream substitution; final instruction/image
identity is still unproven.

Binary64 log now reuses source raw arithmetic, signed conversion, flag
comparison, polynomial, errno and exceptional providers. Its authenticated
872-byte body and 144 numeric/padding bytes pass 37,716 direct comparisons and
the 1,952-case graph (56 compiled log entries), with no unresolved runtime
symbols. Eight zero-table bytes are shared with the existing reducer window;
three pointer contracts remain separately authenticated. No third-party origin
is inferred solely from the API name or polynomial similarity. Future upstream
substitutions still require assessment against native normalization, arithmetic,
exception and instruction/image contracts.

The powf dispatcher candidate reuses the source add, invalid, division-by-zero
and errno providers. Its reduced logarithm/exponential source provider is
explicitly unresolved; a separately labeled native core fixture supplies it
only in verification. All 427,168 pair and 1,952 fixture-graph cases pass, without
claiming full powf source completion. REA body ranges and Ghidra-MCP constant/
table reads bind the next core implementation to the locked artifact. No new
upstream provenance is inferred from the function name or tables; replacing
providers must still preserve native word/live-operand and exception contracts.

Powf's reduced logarithm/product/exponential core is now source and resolves
the dispatcher candidate's last provider. It reuses existing source floating
control, classification, errno and range-error helpers. The prior authenticated
four-table/pointer contracts support 396 core numeric bytes plus 16 dispatcher
bytes. All 427,168 broad and 67,840 targeted pair cases pass without a native
core fixture, as does the 1,952-case graph (132 compiled core entries). No new
upstream provenance is inferred from algorithm/table resemblance. Subsequent
provider updates still require native control, exceptional and instruction/image
compatibility checks; whole-firmware integration remains open.

Pow's half-exponent shortcut now has a source core-register sqrt wrapper at
`0x90e8c`, reusing the existing source integer-root recurrence and errno cell.
The 110-byte body has no new numeric data. It passes 37,436 raw R0/R1 and
independent-D0 cases plus 16 compiled entries in the 1,952-case graph. Its ABI
is distinct from the source hard-float public sqrt; replacing one with the
other would need an explicit adapter. No new upstream origin is inferred.
Pow's main source body, full firmware integration and instruction/image
identity remain open.

The binary64 pow dispatcher candidate reuses the recovered source arithmetic,
exception/error, conversion, absolute-value and raw-register sqrt providers.
Its reduced core remains one explicit source dependency, with native execution
allowed solely as a named verification fixture. The 90,708 direct pair and
1,952 fixture-graph cases pass, without claiming complete source pow. Native
range, parity and raw-helper contracts remain distinct from standard libm
semantics and any upstream attribution. The full source core and original
instruction/image integration still require evidence.

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


GXT310 shared mode control, both channel veneers and pair enable/disable now
compile from recovered R1 C. The five locked rows total 384 bytes because the
124-byte power-down row includes the 106-byte shared mode body; there are
278 unique native code bytes. REA confirms that noncontiguous ownership and
both eight-byte channel bodies. Ghidra-MCP matches the unique code spans and
308 constant bytes. The source channel veneers keep explicit tail relocations
to the shared source mode routine. No vendor source attribution is inferred.

The native mode contract initializes all four configuration bytes to 0x0000c200,
sets low-byte bit zero only for enabled==0, writes two bytes to register 1 and
normalizes any nonzero write result to success. Pair enable calls both channel
providers before logging their failures, then returns raw bitwise AND. Pair
disable calls both channels with zero and its sampled raw R0 equals the last
channel result. The 113,032-case direct receipt passes 341,482 callback
observations and 66,880 write observations per side. It covers all byte
addresses, high-width statuses/enables/modes, callback buffer mutation, logger
order, typed arguments, full observed non-stack RAM and raw R0/callee/SP.
Writes, loggers and pair-channel providers are named fixtures in this receipt.

A 16,572-workflow receipt then executes the actual source cache, bus/request
records, shared/channel modes, pair control, both ID veneers/readers and
self-check together. Only registry lookup/dispatch and logging remain fixtures.
There are 495,412 callback observations per side. Every workflow checks four
mode writes, both ID reads, cleanup order, full four-byte private words, cold C
state, NULL-handle behavior and the final self-check result. Selected graph
strings/name total 388 bytes and source state 24 bytes; folded constant words
and bounds remain authenticated in the raw source objects.

This graph comparison explicitly normalizes only the persistent write/read
pointer words in the request record after their typed buffer effects are
checked. Raw pointer equality fails: sampled native pointers are 0x2003efe0 and
0x2003efdc, while source leaves both at 0x2003efdc. Thus native pointers are
distinct and source pointers alias. Later NULL-write reuse after intervening
stack reuse remains unverified; normalization does not close that behavior.
Concrete cases are retained in graph-verification.json. An initial normalized
receipt/driver is preserved, and the stronger receipt adds raw pointer samples
without changing the compiled source object or comparison trace. O1/O2/Oz
compiler probes preserve the four-byte placement gap and remain unadmitted
code-generation observations, with their objects and hashes retained.

All named GXT imports in this startup graph now resolve to source. The broader
startup bundle has 63 transitive unresolved imports, with all thirteen direct
application imports still resolved. The frontier is 761 tested contract
candidates, 1,370 compiled hints and 1,195 unresolved routes across 3,326 rows.
This does not establish all GXT functionality, actual registry/logger source
execution in the selected graph, physical sensor/device health, full startup,
raw private ABI/persistent pointer placement, final source state/link ownership,
original compiler or byte-identical firmware. Those gates remain explicit.


The reset-reason decoder now compiles as a C kernel with a naked forwarding
bridge that preserves incoming raw register seeds. The public startup interface
remains one typed reason word; the kernel receives the incoming scratch words
explicitly so the caller diagnostic word retains its native upper R3 bytes.
Its return mask is 0x0007000f. Zero reasons log power-on/brown-out, while nonzero
unknown-only reasons return zero without that message. Recognized bits are
processed in native order, with retained PC/LR and tag/caller queries only on
software reset. Values reload after callback-capable logging and the tag is
retested after logging before the conditional caller query.

REA confirms 754 native code bytes in two ranges: 620 at 0x8198c and 134 at
0x81fb8. Ghidra-MCP matches both spans and 1,396 constant bytes, including source
pointer relocations for two shared format strings. The DIF string at 0xbdb78
overlaps 25 bytes of the earlier 257-byte ctype view at 0xbda90. This new source
view does not establish unique global image-data coverage; final shared literal
ownership/link placement must coalesce the two views. No vendor attribution is
inferred for this product-specific body.

The 114,240-case receipt passes 1,965,056 callback observations, 314,992 retained
diagnostic-provider calls and 124,400 byte-provider calls per side. It covers
all 128 recognized-flag combinations, unknown bits, getter statuses/values,
initial four-byte diagnostic words, raw incoming R3 seed bytes and in-scope
callback mutations. Native/source typed argument order, fresh PC/LR/tag loads,
conditional caller reads, return R0, callee/SP preservation and full observed
non-stack RAM match. Diagnostic-pointer addresses are normalized; retained
getters and logger bodies are named fixtures. The bridge branches only to the
compiled C kernel, with no native executable fallback.

The larger startup bundle now resolves the decoder and exposes its three
retained getters, so transitive unresolved imports rise from 63 to 65. All
thirteen direct application imports remain resolved. The frontier contains
762 tested contract candidates, 1,370 compiled hints and 1,194 unresolved source
routes across 3,326 rows. Retained provider bodies, real reset/retention and
whole startup execution, raw private frames, shared literal ownership, original
compiler and byte-identical firmware remain open. The prior GXT persistent
pointer placement/alias difference and later NULL-reuse gate remain unchanged.


Retained reset byte, return-address and program-counter getters now compile as
recovered R1 C. Their 48/94/94-byte native bodies total 236 bytes. Each byte
request rejects unsigned indexes above 12 and NULL outputs, captures the record
pointer from context+20, rejects a nonzero busy byte and compares stored CRC16
at+14 with a checksum of the first 14 bytes. PC/LR perform four separately
validated byte reads (indexes 6..9 and 2..5), assembling little-endian output
only after all succeed. They do not explicitly consume or clear the record;
caller-selected output aliasing can of course modify record storage.

The existing authenticated stock_checksums.c implementation supplies CRC16.
It is recompiled unchanged with function/data sections and selected without
CRC32/hash code. Getters plus CRC16 link with zero unresolved imports. REA and
Ghidra-MCP authenticate the three getter bodies, the reused 36-byte CRC body,
its 512-byte polynomial table and the four-byte context literal. The source
24-byte minimum context view matches verified cold scatter bytes, including
the retained record address 0x2003ffb0. The record itself has no source cold
initializer and lies outside the observed cold scatter ranges. Full context
symbol extent/ownership and writer/capture behavior remain separate gates.

The 117,750-case receipt executes actual source getters and CRC16, with 33,944
CRC calls and 125,482 byte-entry observations per side. It covers valid/corrupt
and busy records, unsigned index boundaries, NULL/unaligned/aliased outputs,
persistent alias sequences and the canonical high retained-RAM address. Explicit
CRC-entry mutations verify captured record pointers, checksum reload after the
call, no second busy check, mixed-record word reads, and early failures at every
byte position. Failure does not publish a partial output word. The initial
116,790-case receipt/driver are preserved; coverage expanded without changing
the compiled object. Source private byte slots retain four-byte stride; their
initial scratch bytes and exact frame addresses remain unproven.

A further 59,904 workflows execute the actual source decoder, all getters and
CRC16 together: 985,109 logging observations, 222,576 getter entries and 131,280
CRC calls per side. Only logger bodies are fixtures. Busy/corrupt records,
recognized flag combinations, tag cases and controlled logger/context changes
match native behavior. Return R0, callee/SP state and the full observed low and
high retained non-stack RAM match without persistent pointer normalization.
Input record bytes are explicit fixtures, not proof of physical retention or
concurrency. Selected decoder data drops 16 folded bounds/pointer-cell bytes:
1,380 decoder bytes, the reused 512-byte CRC table and 24 context bytes remain.
The raw decoder's 1,396-byte constant proof remains unchanged.

The larger startup bundle resolves all three retained-getter imports and now
has 62 transitive unresolved imports, with all thirteen direct application
imports still source-linked. The frontier contains 765 tested contract
candidates, 1,370 compiled hints and 1,191 unresolved routes across 3,326 rows.
Writer/capture bodies, physical reset/retention, whole startup execution, source
context/private-frame/final linker ownership, original compiler and byte-identical
image integration remain open. The earlier GXT persistent pointer alias/NULL-
reuse gate and shared DIF/ctype literal-placement gate remain explicit.

### Retained reset writers and capture paths

`native_reset_writer.c` adds source byte publication, address clearing, caller
and tag writers, both capture paths and the architectural PC probe. REA confirms
8 locked rows spanning 326 unique native bytes; the return-address writer is a
44-byte shared tail of the capture adapter, not a ninth row. Ghidra-MCP reads
match all spans and the context literal against the authenticated application.
The source bundle reuses the existing CRC16 and attributable EABI/memory-clear
providers and has no undefined imports. No new vendor implementation is claimed.

36,864 native/source cases compare 294,840 call observations per side, raw R0,
callee registers, SP and full observed low/high non-stack RAM. Controlled record
and context changes cover capture-before-CRC versus reload-before-clear, header
changes, stored CRC corruption/repair and context changes at clear entry. Each
byte publishes a fresh CRC. Tag value 7 skips address clearing only when the
full input word equals 7. The source PC probe compiles to the native four bytes
and is linked at its recovered address for sampled stored-PC equality.

The combined startup bundle now has 61 transitive imports remaining and all
13 direct application imports resolved. The frontier is 773 tested candidates,
1,370 compiled hints and 1,183 unresolved routes across 3,326 ownership rows.
These are contract results, not a source-complete or byte-identical image.
Private frames, source placement/compiler identity, physical reset/retention,
concurrency and whole startup execution remain open. The prior GXT persistent
pointer alias/NULL-reuse and shared DIF/ctype literal gates remain open. Clear
call arguments/order and RAM effects match; internal provider store granularity
is not claimed identical to the native clear loop.

The selected clear provider is the existing pinned musl 1.2.5 `memset` plus
the R1 EABI wrapper. Its upstream source/provenance hashes remain bound through
the runtime provider report. Future upstream updates can reuse the same seam,
but require a new differential receipt and retain the instruction-identity gate.

### Battery ADC cache source checkpoint

`native_vbat_cache.c` implements the locked 20-byte cache contract at 0x9143c.
Only the four-byte pointer cell at 0x200068a0 is source-owned; its zero initializer
matches authenticated cold scatter RAM. The nine-byte `vbat_adc` string matches
Ghidra-MCP reads and the official image. No surrounding root layout is invented.
Fresh REA analysis does not recover a procedure at this address; that tool gap
is preserved in `rea-9143c.json`, while frozen pseudocode, locked ownership and
native instruction bytes independently define the existing contract. The locked
ledger is unchanged.

1,792 three-call workflows execute actual source cache, registry and pinned
musl string comparison against native: 3,275 registry entries and 6,048 string
comparisons per side. Empty/missing/prefix/duplicate/exact name lists, nonzero
cached words, cache reset/retry and controlled registry/cache mutation fixtures
match raw R0, callee registers, SP and observed low/high non-stack RAM. A null
lookup remains null and is retried; a nonzero cached value skips lookup even if
the registry changes. Existing source registry and attributable musl providers
are reused; this product-specific wrapper has no new upstream attribution.

The zero-import cache graph links into the larger startup bundle, reducing
transitive imports to 60. The frontier is 774 tested contract candidates, 1,370
compiled hints and 1,182 unresolved routes across 3,326 rows. Physical ADC
conversion, whole startup, private frames, original compiler and byte-identical
image placement remain open, along with prior GXT pointer alias/NULL-reuse and
shared DIF/ctype literal gates. The REA boundary gap is an evidence limitation,
not a claim that source work is externally blocked.

### Daily cache metadata and signed local-day source checkpoint

`native_daily_metadata.c` adds six refreshers and six startup veneers, plus
local-day start and signed timezone access. Fourteen locked rows cover 264
unique native bytes. Individual timestamp/offset fields own only 36 bytes,
inside the authenticated startup zero-fill region; complete cache layouts,
record ownership and lifecycle remain open. HR logging owns 21-byte ring and
15-byte SDK literals, independently matching Ghidra-MCP reads. All native body,
veneer and literal spans match the authenticated application. Fresh REA recovers
the day/offset helpers but misses twelve metadata/veneer entries; the frozen
pseudocode and locked ledger remain authoritative for their existing extents.
No boundary or ownership row is rewritten.

57,344 comparisons execute source refreshers, veneers, day/offset accessors,
existing clock backend and integer runtime. The external backend and three
logging calls are named fixtures: 53,248 backend calls and 9,216 logger calls
per side. Extreme signed offsets, epoch/day boundaries, source ABI returns,
mode short-circuit/fresh reads and controlled backend/logger mutations match
native observations, callee/SP state and observed low/high non-stack RAM.
The local-day routine captures timezone before calling the backend; each
refresher reloads timezone afterward. Stress stores backend time directly.
HR logging reloads its timestamp field after callbacks and returns the native
last mode/SDK result on sampled paths.

The initial unsigned-day candidate was rejected at epoch0/offset-32768. Its
source, objects, driver, reports and counterexample are preserved under
`initial-unsigned-day-candidate/`; it was never admitted. Native 0x2754a uses
signed64 division truncating toward zero. The corrected source uses existing
signed EABI glue and unchanged LLVM compiler-rt20.1.8 unsigned magnitude division,
pinned at 87f0227cb60147a26a1eeb4fb06e3b505e9c7261 with source/license provenance.
This permits future upstream improvements through the same runtime seam after
new native/source verification, while preserving the image-identity gate.
The receipt's u64-division flag denotes this reused magnitude provider; it does
not claim unsigned day arithmetic. Product-specific metadata is reconstructed
source, not an attributed vendor implementation.

The startup bundle now has54 transitive imports, resolving all six cache
initializers and retaining all13 direct application imports as source-linked.
The frontier is788 tested contract candidates,1370 compiled hints and1168
unresolved routes across3326 rows. Logging/backend fixtures, complete startup,
private scratch/APSR/R1-R3 ABI, physical clock/cache lifecycle, compiler and
byte-identical image placement remain unproven. Prior GXT persistent pointer
alias/NULL-reuse and shared DIF/ctype literal gates remain open.

### Protocol reset and periodic reaper callback source checkpoint

`native_protocol_reset.c` implements locked reset0x82f78 (28 bytes) and arm
0x83cf4 (12 bytes), plus instruction-derived callback0x83cd0 (30 bytes). The
callback is absent from the frozen function ledger and is supplemental source;
no third row or corpus entry is invented. Ghidra-MCP reads authenticate bodies
and literals; fresh REA misses these entries and that limitation is retained.
Reset calls existing port init, clears640 workspace bytes, arms the callback,
then resets the existing sequence halfword. The callback publishes event0x10
with byte1, then schedules itself with argument0 and delay0x384000. Provider
failures do not suppress its subsequent scheduling.

4,608 comparisons cover reset, arm and callback:9,216 call observations per
side, raw R0, callee/SP and observed low/high non-stack RAM. Actual source clear
reuses pinned musl1.2.5 plus the existing EABI wrapper; sequence storage is
selected unchanged from the encoder. Init/scheduler/event are explicit named
fixtures, including workspace/sequence/payload mutations and arbitrary returns.
Only the one-byte public payload is inspected. Private pointer, upper scratch
bytes and native callback R3 behavior are unproven. The source callback section
is64 bytes including linker veneers and exceeds the native30-byte body/literal
placement. Its recovered verification address ensures pointer equality only;
this is not proof of a valid global linker layout or instruction identity.

640 zero-initialized workspace bytes lie within the previously verified scatter
zero-fill region. Surrounding state and ACK record semantics remain unresolved.
The startup bundle resolves the task's reset import but exposes port-init as a
new link dependency, retaining54 transitive imports. Port-init source already
exists; complete source port/scheduler/event integration remains separate work.
The frontier is790 tested candidates,1370 compiled hints and1166 unresolved
routes across3326 rows. Full protocol/startup execution, physical delivery,
private ABI/compiler/final image, prior GXT pointer alias/NULL-reuse and shared
DIF/ctype literal gates remain open.

### Reset through actual source protocol-port initialization

`build_native_protocol_reset_port_runtime.py` composes reset/reaper, existing
port init/receive registration, send registration, source-owned hook cells,
existing sequence and attributable source clear. A further36,864 comparisons
execute this composition:162,816 call/log observations per side, raw R0,
callee/SP and observed low/high non-stack RAM match native. Mode short-circuit,
ring/SDK logging, hook mutations during logging, workspace/sequence mutations,
clear-before-arm and final sequence reset are checked. Init and registration
are actual source, replacing the prior init fixture. Only logging, scheduling
and event providers are execution fixtures. In this bounded verification graph,
fragment/ingress addresses are opaque registration targets and never execute.

The larger startup bundle also links the actual source fragment/ingress bodies,
fragment callback state and unchanged selected CRC32 source, retaining their
source relocations. These bodies are not claimed executed by this reset-only
graph. Port-init is closed; three dispatch seams are newly exposed:
`r1_ble_event_dispatch`, `r1_eus_system_dispatch_plan_build`, and
`r1_health_registration_dispatcher`. Thus56 imports remain, compared with54
before callback expansion. The increase reflects a larger source-linked graph,
not replacement of real providers with stubs. CRC32 is selected from the
existing function-section checksum compilation; CRC16 is not duplicated.
Existing pinned musl memory and checksum source/provenance are reused.

No new ownership row is promoted by composition:790 tested candidates,1370
compiled hints and1166 unresolved routes remain across3326 rows. Actual full
callback dispatch, scheduler/event execution and whole startup remain open.
The reaper source callback's64-byte verification placement still exceeds the
native span; private pointer/scratch/R3, physical delivery, compiler and global
byte-identical image integration remain gated. Prior GXT pointer alias/NULL-
reuse and shared DIF/ctype literal gates remain explicit. Existing REA/Ghidra
provider evidence is reused unchanged; no new boundary claim is made.

### Health command group and complete bounded health dispatch

`native_health_commands.c` adds13 health-command bodies and three shared response
flag helpers:16 locked rows,844 native bytes. Daily requests send their response
then publish an8-byte event; the second word retains incoming R3. Sequence is
reloaded after the response callback without a flag recheck. Point requests
publish the same retained-seed record with their native kind and mode. HR/SpO2
measurement and sleep detail use distinct flag gates and event identifiers.
The history no-op preserves incoming R0, matching its native BX LR body.

46,080 direct/source-helper comparisons cover all256 flag bytes, full-word
header inputs/truncation, unaligned packets, provider return words, packet
sequence/flag changes during response and writable header/event fixtures.
11,520 lower responses and8,448 events per side match. Only lower response,
event and report-setting providers are fixtures; actual source flag helpers
execute. The report-setting length12 path selects address0 and reads its byte,
retained under an explicit mapped-zero fixture rather than a new guard/default.
Private event/header addresses and private-stack packet aliases remain gated.

A further43,008 workflows execute actual source health dispatcher, binary
search, all14 health-table targets (including prior activity refresh) and the
shared response helpers:5,376 responses and9,216 events per side. No handler
body is replaced by a fixture. Callback-seed words passed through the search
match native, as do R0/callee/SP and observed low/high non-stack RAM. These are
bounded valid-key health routes with lower provider fixtures, not proof of all
system commands, below-minimum search faults, physical delivery or full startup.

Fresh REA recovers the three56-byte response helpers but misses13 locked health
entries; frozen pseudocode/ownership and Ghidra-MCP spans retain their extents.
New handler definitions use the module's four-word callback shape with const
void packet and uintptr_t scratch. The earlier passing pointer-typed candidate
is preserved; alignment produced the same object bytes and trace. Legacy module
extern void declarations still require coordinated common-header migration;
full cross-translation-unit type consistency is not claimed. Raw R1-R3/APSR,
private frames/aliases and original compiler/image identity remain open.

The larger startup bundle now links all three dispatchers, their command tables,
new health bodies and available info/status/activity/special handlers. Three
parent dispatch imports close and25 leaf/data imports become explicit, leaving
78 transitive imports. All new dependencies are listed in the runtime report.
The frontier is806 tested candidates,1370 compiled hints and1150 unresolved
routes across3326 rows; graph composition adds no further row count. The source
is product-specific reconstruction with no new upstream attribution; existing
pinned SDK/runtime providers remain reused. Full lower response/event/setting
composition, remaining system handlers, physical behavior, prior GXT pointer
alias/NULL-reuse, shared DIF/ctype literal, reaper placement and byte-identical
image gates remain open.

### ACK table resolution, lazy mutex and delayed restart

`native_protocol_ack.c` adds six locked contracts (242 native bytes): mutex
lock/unlock, packet payload accessor, ACK resolver, packet ACK handler and
cancel/rearm command. A separate two-byte delayed callback is instruction-
derived supplemental source, not a new ledger row; its empty C body compiles
to the authenticated native BX LR. Four REA procedures are recovered; packet
ACK/restart and the supplemental callback remain absent in fresh analysis.
Ghidra-MCP reads plus frozen ownership/pseudocode retain existing contracts.

The resolver scans32 records of20 bytes in the existing640-byte reset workspace.
Any nonzero active byte is occupied. Its four full input words are compared to
three stored bytes and a halfword without truncating the caller's words. The
first match wins. Callback argument and address are captured before the active
byte/address/argument are cleared; unlock precedes any saved callback invocation.
Keys, padding and timestamp remain untouched. Duplicate matches are consumed
one per invocation. Mutex failure does not add an early-abort path.

10,160 workflows compare47,312 observations per side, full observed non-stack
RAM, R0/callee/SP: all32 positions, misses, duplicate records, full-word key
rejection, arbitrary callback returns, two-call persistence, lazy mutex failure,
null-created handles still passed to acquire, and controlled new/acquire/release
mutations. The accessor uses modulo16 advertised-length subtraction; length12
returnsNULL, every other length exposes byte12. ACK handling still reads all key
bytes even for short nonzero payload lengths, matching native behavior without
invented validation. Cancel/rearm always schedules callback4d2f0 with the original
handle and delay0x7800 after cancellation, regardless of its return.

New source-owned configuration is110 bytes:4 cache,80 static mutex control,
16 attributes and10 name bytes. The cache initializer matches authenticated
cold RAM, the control block lies inside verified startup zero fill, and linked
attributes/name match native bytes. The640-byte workspace is reused, not
allocated again. RTOS/delayed/arbitrary ACK callback bodies are named fixtures
in these comparisons; actual source providers remain linked in the larger
runtime, with RTOS/concurrency/physical behavior still unproven. Controlled
provider interleavings do not establish interrupt safety. Private frames/raw
R1-R3/APSR and complete callback declaration consistency remain open.

Both packet ACK and delayed restart imports close without new imports, leaving
76 transitive startup imports. The frontier is812 tested candidates,1370
compiled hints and1144 unresolved routes across3326 rows. No extra row is
counted for the supplemental callback. Existing pinned CMSIS/FreeRTOS and
source delayed providers are reused; product ACK code has no new upstream
implementation attribution. Prior GXT pointer alias/NULL-reuse, shared DIF/ctype
literal, reaper placement, compiler and byte-identical image gates remain open.

### Serial reporting, response headers and owned124-byte class

`native_protocol_serial.c` implements ACK/inverse header send, checked send and
serial reporting. Four new ownership rows are admitted as bounded contract
candidates. Three sized rows total164 bytes; the manual serial row has no frozen
size and keeps that blank. Its52-byte observed instruction span is separately
authenticated without changing the ledger. A stronger raw-frame getter variant
covers the already-counted70-byte serial accessor; it does not add another row
or replace the older advertising candidate's receipt.

18,744 comparisons cover2048 cases per header/checked helper,10,800 getter cases
and1800 serial requests:32,272 observations per side. Shared header and checked
helpers now retain native R0-R3, including provider register clobbers and header
mutations. Native eager stack-argument reads occur before invalid-handle rejection.
Protocol bit/header semantics remain C kernels; scoped frame bridges marshal
arguments and restore native output words. Copy/fill execute existing source
musl1.2.5 providers and the existing native movement-return adapter. KV read and
lower response are explicit fixtures in this tier.

The getter exposes the native124-byte raw stack view instead of inventing a
C default record on failed reads. Zero/partial/full writes, sentinel bytes,
unaligned destinations, overlapping raw-record destinations, aliased length
outputs and ignored provider statuses match. Serial output is16 zeroed bytes,
then15 copied/filled bytes sent after reloading the packet sequence. Incoming
raw record/output pointers match native for first activations. Header private
addresses, general stack aliases and full compiler/ABI identity remain open.

Cold validation also owns the148-byte `nv_r1` class and its4-byte symbolic handle
relocation, matching authenticated decoded initialization exactly. The payload
is mostly erased bytes, with zeros at74-75 and bytes112-123 equal5a followed by
11 zeros. Field16's tag is retained without inventing its semantics. This
supersedes a provisional zero handle that was behavior-tested only under
runtime fixtures and never admitted as cold source configuration. No full KV
class lifecycle or persistent factory/provisioning content is claimed.

432 further workflows execute actual source cached-class reader, getter/serial
kernels, memory helpers and response headers. Only the critical-section callbacks
and lower response are fixtures.432 cached reads and216 critical callbacks per
side match, including size mismatch, class/packet/cache mutation and invalid
send handle cases. This closes the KV-read fixture for that bounded composition,
not flash loading, actual mutex behavior or physical serial/delivery proof.

A retained four-poison two-call probe records a concrete private-history gate:
second requests still match serial response bytes, R0 and observed non-stack RAM,
but the incoming124-byte private view differs at offsets within72-123. Serial
source bytes31-45 and sentinel61 match in these probes. Full prior-stack history
is not claimed equivalent. Three superseded candidate snapshots preserve source,
objects, reports and receipts; no earlier evidence is silently overwritten.
Canonical selection between the old advertising getter and the stronger serial
variant, common interfaces and final private-frame placement remain open.

Serial handler and shared KV-handle imports close, leaving74 transitive startup
imports. The frontier is816 tested candidates,1370 compiled hints and1140
unresolved routes across3326 rows. REA recovers the four sized getter/header
bodies but misses serial's manual entry; Ghidra reads authenticate its observed
span. Prior GXT pointer alias/NULL-reuse, shared DIF/ctype literal, reaper placement,
original compiler, private history and byte-identical image gates remain open.


Protocol control source checkpoint (2026-10-16): `native-protocol-control`
and `native-protocol-control-runtime` compile the health-report setter,
connection-control and pair-role handlers, plus supplemental command 83e2c
and service-thread flag helper 33ae4. Three locked rows cover 284 native bytes;
the supplemental 52 bytes add no inventory rows. Source owns 172 bytes of
exact log text and five cold zero bytes (report flag and thread handle).
REA headless Ghidra authenticated 13 byte ranges against the locked image.
Direct Ghidra-MCP reported no running GUI instance after restart; this is an
explicit tooling limitation, not a fresh direct-MCP verification claim.

The receipt records 8,344 comparisons and 18,842 observations per side using
actual source accessor, flag, checked-send and phone helpers, including the
existing health-setting plan calling the new setter. Logging, BLE encoding,
role assignment and OS callbacks remain fixtures. Logging captures the full
setter word before storing its low byte; phone field8 and packet sequence are
fresh reads. The command delays and signals worker flag4; no physical reset,
advertising or pairing behavior is inferred. Private response-pointer identity,
full raw ABI, instruction identity and complete image reconstruction remain gated.
The initial field6 harness failure is preserved and superseded by the corrected
field8 receipt. The combined object closes four imports and exposes BLE message
encoding and phone-role assignment, leaving 72 unresolved imports.

No new third-party attribution is inferred for these product-specific bodies.
The existing pinned upstream runtime and RTOS providers remain attributable;
future upstream changes require renewed contract validation. All previous serial
private-history/canonical-getter, GXT pointer-alias/NULL-reuse, DIF/ctype literal,
reaper placement, legacy interface and compiler/full-image gates remain open.


BLE message encoder source checkpoint (2026-10-16): `native-ble-message`
compiles 33850 (306 native bytes) and owns 330 bytes of exact log text plus
the four-byte cold-zero queue cell at 20006574. The service-thread cell is
reused from protocol control, without double counting. REA headless Ghidra
procedure and ten byte receipts bind the body, literals and strings to the
locked application. Product-specific encoder ancestry remains unattributed.
The existing pinned musl memory implementation executes through the native
memory ABI adapter; it is reused rather than duplicated.

14,112 native/source comparisons (56,526 observations per side) cover null
payload/queue, zero and unaligned lengths, allocation/queue failures, all log
mode branches, callback register clobbers, queue/thread reloads and local
message-pointer changes before free. Wrapping allocation sizes are tested
with failing allocation fixtures; no huge copy or overflow safety is claimed.
Allocator, queue, thread flags and logging are fixtures in this receipt.
Their source bodies are linked in the larger 71-import object, but the full
allocator/queue/RTOS graph is not executed by this verification. The private
queue-item address, all raw registers/flags, instruction identity and byte-
identical image remain gated. One parent import closes with none exposed.
All prior reconstruction gates remain in force.


BLE control composition additionally passed 8,344 comparisons (29,647
observations per side) with actual accessor, control handlers, encoder and
source memory copy. Allocation, queue, logging, role and OS effects remain
fixtures. The larger graph is not claimed as fully executed.

The locked ledger assigns `r1_ble_thread_message_encode` to both 33850 and
33dbc. Frozen pseudocode shows distinct ABIs: 33dbc takes payload then length,
zeroes its message buffer and queries the queue. The 33850 object cannot prove
33dbc, so its symbol-only match is explicitly excluded from the frontier.
The original ledger remains intact; 33dbc stays unresolved.


Phone-role source checkpoint (2026-10-16): `native-phone-role` compiles the
430-byte 4da28 contract and owns 667 bytes of exact text. It reuses both existing
connection halfwords without claiming new cold data ownership. REA headless
Ghidra procedure metadata and 25 byte receipts authenticate body, literal words,
text and the 18-byte status-publication veneer. Ghidra's terminal-tail-call
limitations are retained; those logger calls are returning in the comparison
fixtures. No new upstream ancestry is inferred for this product-specific code.
Existing pinned source providers remain reused in the larger link.

4,800 comparisons with 36,558 observations per side include 472 assertion
boundaries, full-word handles (including 1000ffff/ffffffff), low-halfword writes,
fresh mode/connection reads, callback mutations and returning raw R0/callee/SP.
The native successful path traverses the 5e1dc veneer to status publisher 5e118;
source calls that same typed provider. Logging, delay, status publication and
the fatal transfer boundary are fixtures; their full graph is not proved here.

The native conflict assertion logs, stores e7f00000 in a stack word and BLXes
the even stack address. Source leaves `r1_phone_role_assertion_stack_transfer`
unresolved. Tests stop before that native transfer and at the source provider;
no substitute trap or executable opcode array is supplied. Exception behavior,
private stack identity, full raw ABI and byte-identical rebuild remain gated.
Closing role assignment exposes this narrower gate, retaining 71 main imports.
The pair handler's prior role callback fixture remains separate evidence; this
unit receipt does not claim an executed pair/role/status graph. All earlier
serial history, GXT alias, shared literal, placement and configuration gates
remain in force.


Status-ring source checkpoint (2026-10-16): `native-status-ring` preserves the
older `native-status-record` source/receipt and builds a raw event-return variant
with source-owned ring state: read/write bytes, dropped halfword, sixteen 8-byte
records and device-state bytes2c/2d (134 total bytes). Cold initialized-data and
zero-scatter evidence bind those cells; adjacent state padding remains unowned.
The existing four tested ownership rows are not counted again. Five fresh REA
headless Ghidra byte receipts authenticate publisher, getters and ring literals.

33,578 comparisons (165,088 observations per side) use actual source device,
peer and charge getters, compare raw R0/callee/SP/nonstack RAM, and cover full-word
configuration checks, callback changes, ring/drop wrap and observed out-of-range
write indices. These observations are not bounds-safety or hardware proof.
Configuration, battery update, timestamp, critical entry/exit and event effects
remain fixtures. The source keeps the event publisher's raw return word.

A further 4,800 role/status graph comparisons (41,284 observations per side,
472 fatal-boundary cases) execute the actual source role body and publisher.
The exact assertion stack transfer remains unresolved. Main linkage closes
status publication and charge lookup, exposes the existing battery updater,
and has 70 unresolved imports. Full battery/event/RTOS/logging execution, private
frames, raw ABI completeness, placement and image identity remain gates.

Device bytes at20016bb0/1 must alias the eventual battery context base20016b84
at44/45. No independent full battery context is allocated here; that future
composition requires one storage owner and verified aliases. Older void status
publisher declarations still need shared interface migration. No new upstream
attribution is inferred; existing pinned runtime/RTOS providers remain reused.
All prior source, history, pointer alias, literal and image gates remain open.


Battery shared-context composition checkpoint (2026-10-16):
`native-battery-context-runtime` source owns the missing device/runtime slices,
thread cells and power-client word (166 new bytes). It reuses the two status
bytes at device44/45 and four-byte ADC cache at runtime16 (six existing bytes).
The source linker configuration joins those owners into 68-byte device and
92-byte runtime views, with asserted aliases. The runtime cadence words are
explicit source constants; the initial device zero region and initialized RAM
receipt bind all cold bytes. This closes the earlier battery/status/ADC storage
alias gate for this composition, without claiming whole-scatter ownership.

The partial main link includes registered battery algorithms, control,
statistics, voltage, configuration, reporting, frame, YHM and KV-field source.
An unchanged CMSIS-FreeRTOS `osKernelGetTickFreq` body is selected from the
hash-bound RTOS provider object, keeping its upstream provenance. Future
upstream updates require renewed contract and image validation. No new product
code ancestry is inferred from algorithm similarity.

2,920 native/source comparisons include 24 cold-context cases, 336 explicit
numeric cases across four FPSCR modes, and matching executions of three
statistics plus four control entrypoints. The smaller tested graph executes
updater/statistics/control source; lower algorithms, hardware and reporting
remain fixtures there. The larger linked graph is not claimed fully executed.
Fresh REA headless Ghidra reads bind the406-byte updater and16-byte literal
range. Earlier77- and74-import compositions/receipts remain manifest-bound.

The broader main object has73 imports: it closes the prior updater and charger
state imports and exposes delay, battery/device-info KV handles, YHM readiness
and timestamp-thunk requirements. This expands source coverage rather than
using import count as a completeness metric. No new inventory rows are added.
Full battery hardware/event/RTOS behavior, fatal stack transfer, raw/private
ABI, final linker placement, remaining source configuration and byte-identical
firmware remain gated. All other earlier gates retain their existing scope.


Battery KV/source binding checkpoint (2026-10-16): `native-battery-kv-runtime`
adds source-owned cold `power` class28 and `dev_info` class76 plus symbolic
four-byte handles at20007df8/20007de8 (112 new bytes). Class values, key bytes,
flags, sizes, tag1 and opaque payload words match authenticated initialized
RAM. ABS32 relocations bind handles to their source classes; no cold NULL
handle or invented failed-read record is substituted. Existing inventory rows
and prior typed provider receipts remain unchanged, with zero new rows.

1,200 native/source workflows (640 critical callback observations per side)
execute the actual configuration getters, external-frame device-field setter,
cached-class reads/writes and pinned musl copy. Tests cover size rejection,
callback payload/size changes, fresh handle reload, input aliasing and getter
R0/R3 restoration. Setter raw return and cross-call private stack history remain
unproved; these single-call cases do not close the earlier private-history gate.
Only critical callbacks are fixtures in this smaller cached graph. Full flash,
KV initialization/commit service and concurrent access remain separate gates.

The main link also selects the already-tested YHM readiness body and aliases
`time_backend_timestamp_thunk` directly to the existing zero-argument
`r1_time_backend_timestamp` body. No duplicated code or new function row is
claimed for that alias. Four imports close without exposing new ones, leaving
69 imports. Fresh REA headless Ghidra reads authenticate readiness and timestamp
body/literal bytes. Direct Ghidra-MCP reports no running GUI instance; no fresh
direct-MCP byte-read claim is made. Existing pinned musl/RTOS provenance stays
bound; no additional third-party ancestry is inferred for product records.

Remaining delay/provider bodies, source configuration, exact fatal transfer,
private/raw ABI, final layout, full-image and physical behavior gates remain.
The battery/status/ADC alias resolution from the preceding composition is
preserved through this link; this checkpoint does not re-open or broaden it.


Nordic millisecond delay source checkpoint (2026-10-16):
`native-nordic-delay-runtime` compiles unchanged authenticated SDK17.1.0
`nrf_delay.h` through a narrow `nrfx.h` adapter. It preserves the SDK zero check
and decrementing millisecond loop, binding microseconds to64 cycles and reusing
the already source-compiled three-mnemonic delay primitive. The SDK ZIP/header
and nrfx contract hashes retain attribution/license provenance. The adapter is
source-owned configuration; no opaque executable array is added.

The locked inventory contains nine millisecond entries, totaling246 bytes:
eight direct-cycle copies and one22-byte copy through the microsecond helper.
117 direct comparisons include72 fixture request paths,27 real cycle paths
and18 three-request prefixes for very large inputs. Real cycle paths execute
1,152,063 primitive instructions per side; combined observed count including
fixture entries is1,165,833. Raw void-return scratch/APSR state is not compared.
Bounded request sequences, callee/SP/RAM and six-byte primitive body matches
are proven; elapsed hardware time, interrupt effects and complete large-count
execution are not. Ten fresh REA headless Ghidra reads bind outer bodies,
cycle-target literals and the microsecond helper. The helper/previous cycle
clones are not counted as additional new rows.

7,104 actual battery-filter/SDK-loop comparisons include35,520 ADC reads,
15,984 busy-delay calls and19,536 RTOS-delay calls. Registry, OS delay and cycle
primitive endpoints remain fixtures in that consumer tier; the direct tier
separately executes the primitive. Full ADC/RTOS/hardware execution is gated.
The main link closes `nrf_delay_ms`, leaves68 imports and adds no data bytes.
Nine existing delay entries are authenticated; eight gain new tested status.
The784f0 row retains its earlier board-seam tested contract. Original duplicate code
placement, compiler identity, full raw ABI, fatal transfer, remaining source
configuration and byte-identical firmware remain open gates.


Response graph composition checkpoint (2026-10-16):
`native-response-graph-runtime` links the registered response sender, header
wrapper and phone-operation bodies with real connection gates, encoder, CRC16,
source memory copy and send-hook dispatch. The encoder/hook variants change
only their data definitions to external declarations. Their compiled function
bytes and normalized relocations equal the original compiled source units.
Sequence and hook cells retain their prior storage owners; the existing four-
byte version map is selected from its original compiled owner. No new inventory
rows or data ownership is counted, and no duplicate storage is introduced.

3,240 comparisons (1,080 per sender/header/phone entry;8,875 observations per
side) execute that actual source graph. They cover failed allocation, null
inputs, connection gates, wrapped-zero capacity, version rejection, callback
failure, log mode and callback/header/buffer mutations. Allocator, logging and
lower callback effects remain fixtures. Raw R0/callee/SP and nonstack RAM match;
private header-pointer identity, complete scratch/APSR/private history and
physical allocation/transport behavior remain gates. The bounded case set does
not establish all length/mode cross-products or memory safety for tiny wrapped
allocations. Existing direct-unit receipts keep their broader boundary scope.

Fresh REA headless Ghidra reads authenticate the three entry bodies plus encoder
and hook bodies. Source-used checksum, musl and upstream runtime provenance
remain inherited through hash-bound provider reports; no new product ancestry
is inferred. Three main imports close without exposing new ones, leaving65.
The full allocator/BLE/RTOS/startup graph, final storage/duplicate placement,
remaining source configuration, fatal transfer and byte-identical image remain
open gates. Earlier battery/status/ADC aliases and private-history gates are
preserved with their established scope.


System event command source checkpoint (2026-10-16):
`native-system-event-commands` compiles supplemental native bodies844ec (54B),
84860 (20B) and84b24 (120B), plus locked health-mode getter4c5b8 (8B) and phone
operation3 wrapper83c62 (36B). Only the latter two add tested ledger rows;
the194 supplemental bytes are not new inventory rows. Source owns two exact
wear-status log strings (100B) and a cold-zero mode byte at2001e478 (1B).
That byte must alias the eventual health-context root2001e454+36; ownership of
that larger context remains gated. No physical wear-state interpretation is
claimed from the log label or byte mapping.

7,560 comparisons (1,512 each across event/ack/query/getter/op3;28,505
observations per side) execute the actual accessor, flag helper, new bodies,
response/header, encoder, gates, CRC, memory copy and hook. The event reads its
length byte after acknowledgement, accepts byte255 as length256, and does not
invent a packet-length check or response-error early abort. The query preserves
fresh second getter and packet sequence reads. Post-getter/accessor mutations
are explicit memory fixtures. Allocator, logging, event and lower send callback
effects remain fixtures; the whole event/BLE/RTOS graph is not executed.

Nine REA headless Ghidra byte receipts authenticate body/literal/text ranges.
REA recognizes the getter body but reports no procedure for the other four
entries; those metadata gaps remain preserved alongside native disassembly,
supplemental pseudocode observations and byte-bound execution evidence. The
frozen corpus and locked ownership ledger are not rewritten or inflated.
Private payload/header pointer identity, complete raw scratch/APSR and stack
history remain gated. Returning R0/callee/SP/nonstack memory match, and the
standalone op3 cases additionally compare its restored R2/R3 values.

Main linkage closes three command imports without exposing new ones, leaving62.
No third-party attribution is inferred for the product handlers; inherited
pinned runtime/memory provider receipts remain bound. Original image identity,
final placement and health-context aliasing, exact fatal transfer, remaining
provider/configuration bodies and all prior scoped gates remain unresolved.


NV update bounded-source checkpoint (2026-10-16): `native-nv-update` compiles
bit2 update73834, peer-address record update738a8, dirty-class scan734e8 and its
XOR1 wrapper73688 (four locked rows/272 native bytes). The supplemental844b0
command is60 bytes without a locked row; its byte contract/pseudocode do not
inflate inventory. Record helpers use external raw52-byte stack views rather
than invented uninitialized C records or failed-read defaults. The command
fills exactly six bytes of its saved frame and preserves the other bytes.

The canonical7-handle table reuses the existing dev_info/power/nv_r1 cells and
owns the four missing class/handle definitions. Source class extents include
observed zero padding; opaque health words retain numeric values. New ownership
is324 bytes (228 class bytes+16 handles+80 exact log text). Existing12 handle
bytes remain their prior owners. All7 symbolic pointers resolve to the observed
cold class addresses in verification. No actual device provisioning is inferred.

3,660 comparisons (64,576 observations per side) exercise actual raw record
frames, cached read/write, pinned musl copy/fill and dirty scanning. Once any
class is dirty, the scan invokes the lower writer for all7 fresh table entries;
errors log but do not abort the final fresh port callback(1,0). Its return1 and
wrapper return0 do not prove storage success or idle state. Response, class
writer, logging, critical callbacks and final port request are fixtures. Source
cold data and larger linked code are not proof of a fully executed flash graph.

A separate authenticated probe FAILED: when a rejected read is followed by a
fresh writable handle in the command path, different compiler-private frame
residue reaches the cached record. Raw R0 matches, store traces and nonstack RAM
do not. `failed-read-frame-probe.json` retains both results. This is an explicit
unresolved command-frame compatibility gate, not a passing contract or a
normalizable pointer difference. Cross-call private history/full raw ABI and
final image proof remain open. Fixing it requires renewed frame evidence and
probe/audit updates; do not invent a default record or suppress the write.

Eleven fresh REA headless Ghidra byte receipts authenticate code/literals/text.
REA observes scan/wrapper/bit2 extents; peer and command procedure gaps remain
recorded. The original scan row name `device_registry_module_enabled_scan` is
retained in the locked ledger; the tested source symbol describes its observed
KV dirty-scan behavior, without new upstream attribution. Main linkage closes
the command and hsync handle, exposes `r1_store_class_record_write`, and has61
imports. Existing pinned memory/RTOS provider provenance remains bound. Physical
flash/BLE, final configuration/placement, exact fatal transfer and all other
scoped history/alias/raw/image gates remain in force.


NV class writer source checkpoint (2026-10-16): `native-nv-class-writer`
implements91780 (118 native bytes), with94 bytes of exact failure log text
including the original `calss` spelling. It executes the existing source CRC16,
stores it at class offset22, packs index&3fff into flags2..15 while preserving
only flags bit1, and clears dirty bit0 before the current port write callback.
The callback receives offset=index14<<8, node, fresh size+24 and its loaded
address in the fourth argument word. Return1 denotes zero callback status;
return0 denotes nonzero callback status. Dirty flags are not rolled back on
failure. Offset22's old `reserved` field label remains a legacy interface name;
its observed CRC use is now explicit without editing hash-bound older units.

1,696 direct comparisons (9,186 observations per side) use real CRC, including
size65535, unaligned records, full-word indices, flag masks and explicit
post-CRC changes to flags/size/port/payload. Fresh port/size reads, captured CRC,
write bytes, callback R3 and failure logging match. Port writes and logs are
fixtures; this does not establish successful flash persistence or recovery.
Five fresh REA headless Ghidra byte receipts plus118-byte procedure metadata
bind code/literals/text to the authenticated application.

3,660 further caller comparisons (104,532 observations per side) execute actual
record helpers, cached copy/fill, dirty scan, serializer and CRC. Response,
logging, critical/port callbacks and final request remain fixtures. The scan's
observed return convention/log behavior is preserved rather than reinterpreted
as storage success. The main link closes the class-writer import with none
exposed, leaving60. One locked row gains a bounded tested contract.

The failed-read/fresh-valid-handle probe was repeated with the ACTUAL serializer
and CRC. It still FAILS: R0 matches, serialized port-write traces and nonstack
RAM differ because private frame residue enters the record. The new
`failed-read-caller-graph-probe.json` preserves current-graph results alongside
the earlier fixture counterexample. No default record, dirty rollback or
pointer normalization masks it. This remains an unresolved frame-compatibility
gate; the passing bounded cases do not prove that path. Full raw ABI, private
history, complete flash/commit execution, physical persistence, final placement
and byte-identical firmware remain gated. Existing runtime/checksum provenance
and all earlier source/configuration/alias/fatal-transfer gates remain bound.


Build-only native recovery envelope checkpoint (2026-10-16):
`native-nv-recovery-envelope` implements the176-byte84150 boundary under the
separate symbol `r1_native_nv_recovery_envelope_handler`, plus32-byte83c86 phone
query. It owns190 bytes of exact log text. The image-composition-only legacy
handler alias resolves to this native boundary; it does not modify or establish
runtime admission for the separately documented bounded planner. The lower
`r1_native_nv_recovery_command_dispatch` remains unresolved. Existing recovery
admission, authorized provisioning, identity handling and persistence gates in
the two NV correlation documents remain in force; no identity table is copied.

3,556 comparisons (3,472 envelope/84 query;15,722 observations per side) execute
actual payload accessor, phone getter and inverse-header helper. Native lower
dispatch, response and logs are fixtures. The boundary reads the three fields
fresh after logging and forwards the captured body pointer. Stock short-backing
reads are exercised only in mapped synthetic emulator memory; this does not
admit those packets to a live recovery interface or prove bounds safety. Null
payload returns preserve the observed log-mode/raw-log-return behavior.

The query wrapper zeros its saved R1/R2/R3 words, and returns the lower response
word's nonzero test in R0. The selected cases compare all four return registers;
this is not proof of connection readiness or BLE delivery. Post-accessor memory
changes are explicit fixtures, not observed physical interrupts. Seven fresh
REA headless Ghidra byte receipts authenticate code/literals/text; both procedure
metadata gaps are retained. The frozen corpus and locked rows stay unchanged.

Two rows gain bounded tested candidate contracts, totaling208 native bytes.
Main linkage closes the legacy handler alias and exposes the unresolved lower
native dispatcher, retaining60 imports. No hardware write or live recovery send
is executed. This is source/build evidence only. Existing failed-read frame
counterexamples remain bound; complete raw/private ABI, provisioning/rollback,
physical persistence, final layout and byte-identical image remain gated.
Product recovery ancestry remains unattributed; inherited SDK/memory/RTOS
provider provenance is preserved without new third-party inference.


Build-only recovery command-dispatch checkpoint (2026-10-16):
`native-nv-recovery-dispatch` compiles108-byte7c450 control behavior and102 bytes
of exact diagnostic text. Commands other than the full-word value2 return the
input command word without effects. Command2 selects the merge boundary only
for full-word length116 and nonzero full-word CRC; all other command2 cases
log then select the report boundary. Captured length/CRC values survive logger
clobbers, and selected target return words propagate unchanged.

6,496 comparisons (2,940 direct dispatcher,3,472 actual envelope/dispatcher,
84 query;22,696 observations per side) execute the actual native source control
graph. Lower merge, identity-report, response and logging effects are emulated
fixtures. The merge boundary observes body/length/CRC; the report boundary has
no semantic arguments. Native lower prologues are separately byte-authenticated;
complete incoming scratch-register and private-frame state is not claimed.
Short-backing envelope reads remain confined to mapped synthetic emulator data.
No identity table, report generation, merge application or hardware write is
implemented or executed. Bounded-planner/runtime admission policies remain
unchanged and independently gated by the existing correlation documents.

Six fresh REA headless Ghidra byte receipts bind dispatcher, literals/text and
bounded lower prologue observations. Procedure metadata for7c450 is missing and
remains explicit, despite the existing locked manual extent. The dispatcher has
a separate native symbol from the documented bounded planner API. Main linkage
closes the prior native-dispatch import and exposes two named effect boundaries,
leaving61 imports. This is expanded source coverage, not an import-count
completeness claim. One locked row gains a bounded tested candidate contract.

The actual-serialization failed-read frame counterexample remains open and
hash-bound. Provisioning/rollback, identity/report admission, flash effects,
full raw/private ABI, final layout and byte-identical firmware remain gates.
No new upstream ancestry is inferred for the product-specific dispatcher;
existing SDK/runtime/memory attribution remains inherited through pinned inputs.


Build-only time synchronization command checkpoint (2026-10-16):
`native-time-sync-command` compiles supplemental 846dc control flow (224 native
code bytes). It cancels timeout84c82 before packet lookup, captures timezone and
current timestamp before reading the six payload bytes, publishes a fully filled
12-byte event3, then sends flagC5 and ACK4 with the native arguments. Sequence is
read freshly after event publication. The recovery-needed provider selects the
phone query for nonzero results or the independently gated report effect for zero.
Fresh mode calls, log arguments and final raw return words are preserved.

8,192 native/source comparisons (1,920 null payload,4,704 query,1,568 report;
74,832 observations per side) execute the actual packet accessor. All lower
clock/event/ack/cancel/query/report/log effects are explicit emulator fixtures.
Mutations after cancellation, clock reads, event publication, acknowledgement
and logging verify capture versus fresh reads. Native advertised lengths13/17
can still read six payload bytes from mapped synthetic backing; this does not
establish real packet bounds or runtime admission. Callee registers, SP, rawR0,
event bytes, call order and nonstack RAM match. Complete scratch/private ABI,
cross-call stack history, timing, effects and physical behavior remain unproven.

Six REA headless Ghidra byte receipts authenticate code, literals and diagnostic
text; procedure metadata is explicitly missing. Direct Ghidra-MCP reports no
running instance. Main linkage closes846dc and exposes two source providers:
`r1_protocol_time_timeout_callback` at84c82 and the ignored-read-status7bb20
`r1_nv_recovery_needed_query_boundary`. The latter can consume private-frame
history, so no default record or guessed validity policy is substituted. Existing
UTC/timestamp, cancellation, event, ACK and phone-query sources are reused. The
report effect remains the same separate unresolved boundary. There are62 imports;
no new locked ownership row is claimed. Whole-image counts remain839 tested
candidates,1,117 unresolved routes and1,370 compiled hints across3,326 rows.

The actual-serialization failed-read frame counterexample, recovery/provisioning
admission, identity/report/merge effects, callback source, final placement and
byte-identical image remain explicit gates. No recovery admission or identity
table changed, and no hardware write ran. This product-specific command has no
new upstream ancestry evidence. It reuses pinned provider sources through the
existing dependency manifests; upstream update candidates must retain their
licenses, exact revisions and differential contracts before replacement.


Time synchronization query/timeout provider checkpoint (2026-10-16):
`native-time-sync-providers` compiles the32-byte supplemental7bb20 query plus
22-byte locked84c82 timeout callback. The query's external frame saves incoming
r3 exactly. It requests one byte from the canonical r_size cached class, ignores
read status, tests the resulting byte for0 or255, and restores the saved word
into r3. A failed read therefore tests the incoming r3 low byte; it does not
acquire a guessed default. The callback replaces that saved word's low byte with
the low byte of its argument, obtains the phone handle from field8, and enqueues
event8/length1 with the saved-byte pointer. Native lower rawR0 and restoredr3 are
preserved, while its public callback signature retains void semantics.

22,368 native/source comparisons comprise20,736 explicit cached-read boundary
fixtures,480 actual cached-read/musl workflows, and1,152 timeout/phone-accessor
cases, with23,760 observations per side. These compare rawR0/r3, callee registers,
SP, read/enqueue arguments, payload bytes and nonstack RAM. Fixture coverage
includes every incoming seed low byte, upper-word patterns, success/failure
return words, unchanged/byte/word reads, all predicate classes, size mismatches,
critical-callback changes to captured payload/handle/port and explicit byte
mutation after read/getter boundaries. BLE enqueue and critical callbacks remain
emulated effects. Source-owned cold classes and canonical handle table match the
authenticated scatter observations; no duplicate data owner is introduced.

REA headless Ghidra authenticates both byte spans. Metadata observes84c82's
complete22-byte extent, while7bb20 metadata remains explicitly unavailable.
Locked ownership therefore gains exactly one tested candidate, not two. The
partial application now has60 unresolved imports,840 tested candidates,1,116
unresolved routes and1,370 compiled hints across3,326 rows. Both provider imports
exposed by the prior time-command checkpoint are now source-linked. The boundary
suffix on the query symbol records its earlier interface; it is no longer an
undefined provider in this composition.

This does not prove the actual time-command caller's full incoming scratch or
cross-call private-stack history. The existing failed-read serialization
counterexample is retained, and native recovery admission/report/merge effects,
final placement and byte-identical whole firmware remain open. No runtime
admission, identity table or hardware writes changed. No upstream product-code
ancestry is inferred: these bodies are evidence-derived C with small ABI bridges.
Existing attributed musl and cached-class provider sources are reused through
hash-bound manifests rather than copied into new implementations.


Power-control protocol command checkpoint (2026-10-16):
`native-power-command` compiles supplemental843c8 (210 native code bytes) and
144 exact diagnostic text bytes. It uses the existing packet accessor and
canonical low-battery thread cell at20006548. Null payload returns0. Initial
command bytes outside1..3 send command18/version1/flag1 and return its raw result.
Accepted bytes send flag0 and delay100, ignoring both results, then reread the
payload byte. A changed byte outside1..3 returns that byte directly. Command1
writes reboot-caller marker1 then posts thread flag2. Command2 retains the seed
word's upper16 bits, ORs its kind bits with3, inserts the low14 voltage bits into
bits2..15, writes the timestamp word, invokes the existing KV field setter and
posts flag1. Command3 performs fresh-mode recovery logging then posts flag256.
The thread handle is loaded freshly after the preceding effects/logging.

The ABI bridge retains the native savedr2/r3 words. Paths1/3 restore the frame
before tail-calling flags; path2 calls flags first then restores the event words.
This preserves returnedr2/r3 even when lower calls clobber scratch registers.
There is no invented zero initialization of the seed upper bits. The ordinary C
kernel has additional private stack use, so full raw ABI and private history are
not implied by the bridge's external frame contract.

39,168 native/source comparisons (2,304 null,9,108 rejected,13,848 changed after
delay,4,636 each reset/off/resume;113,876 observations per side) execute the
actual packet accessor. Lower ACK, delay, reset marker, voltage/time, KV field
setter, flags and logging are explicit fixtures. Cases include all256 initial
command bytes, boundary advertised lengths, mutated commands after accessor/ACK/
delay, seed patterns, full-word voltage truncation, event mutation after reads,
fresh thread handles after marker/KV/logger effects, mode sequences and raw lower
return words. RawR0/r2/r3, callee registers, SP, ordered observations and nonstack
RAM match. This is not hardware timing, reset, persistence or delivery proof.

REA headless Ghidra byte receipts authenticate code, literals and complete text;
shorter initial text-prefix receipts are retained alongside full reads. Procedure
metadata is explicitly unavailable. No locked ownership row is added for this
supplemental table target. Main linkage closes843c8 without new imports, leaving
59. Whole-image counts remain840 tested candidates,1,116 unresolved source routes
and1,370 compiled hints across3,326 rows. Existing reset/battery/time/KV/RTOS
providers are source-linked through hash-bound parent manifests. No new storage
owner or product-specific upstream ancestry is inferred. The existing attributed
SDK/FreeRTOS/CMSIS and memory/runtime dependencies retain their pinned provenance;
this command does not replace them with another implementation.

Recovery/provisioning admission, identity/report/merge effects, the retained
failed-read serialization counterexample, caller/private history, final placement
and byte-identical image remain explicit gates. No runtime admission, identity
table, flash operation or hardware state was changed.


Device-ID command checkpoint (2026-10-16):
`native-device-id-command` compiles supplemental83e50 (156 native bytes), status
get/clear6abd8/6aadc (6+8 native code bytes) and locked operation11 wrapper838ba
(36 bytes). It owns an exact28-byte default record,40 diagnostic text bytes and
one cold status byte at20006da5. That byte must alias offset5 of the eventual
20006da0 context owner. No complete context or identity state is claimed.

The command copies the default response, reports status1 and clears the source
byte only when it equals exactly1, otherwise reports0, clears a28-byte temporary
ID view, invokes the unresolved native ID provider, and copies the first24 ID
bytes into response bytes1..24. Logging reads fresh modes/status and the temporary
ID; the sequence is read after logging. Operation11 sends exactly25 bytes with
first argument0 and fresh sequence through the existing phone getter/response
provider. Its external saved words become payload pointer/25 on nonnull input;
null input retains incomingr2/r3 and returns0.

2,192 native/source cases comprise960 command,576 two-call workflow,144 direct
operation11 and256 each status getter/clear. There are14,136 observations per
side. Actual source status accessors, operation11, phone getter and attributed
musl/EABI memory helpers execute. Identity read, response and logging effects are
fixtures. Fixture ID writes are bounded to mapped28-byte backing; native cached
length safety is not inferred. Cases compare rawR0/r2/r3, callee registers, SP,
response bytes, call order and nonstack RAM, including logger mutations, fresh
sequence/handle loads, all status-byte values and repeated one-shot consumption.

The first compiled clear helper clobberedr2 while native preserved it. Its source,
object, reports, driver and counterexample remain hash-bound under
`native-device-id-command-runtime/pre-clear-scratch-fix/`. An explicit ABI bridge
now preservesr2/r3 around the ordinary C store; the complete comparison passes.
Other raw scratch registers/private-frame history and compiler/global placement
remain unproven rather than being normalized away.

REA headless Ghidra byte receipts bind the command, wrapper, status bodies,
literals, default/text data and unresolved6ab88 provider. Initial shorter text
prefix reads are preserved alongside complete reads. Procedure metadata observes
the complete36-byte wrapper and explicitly lacks83e50. One locked row gains a
tested candidate; supplemental entries do not inflate ownership totals. The
partial application closes83e50 and exposes `r1_native_device_id_read_boundary`,
leaving59 imports,841 tested candidates,1,115 unresolved routes and1,370 compiled
hints across3,326 rows.

The existing frozen GoMore key-or-cache helper takes capacity, explicit cache
state and device/address words. Native6ab88 instead preserves incoming words,
selects an unchecked cached pointer/byte-length or SVC109 plus FICR and formatter.
The bounded helper is therefore not substituted as the raw native provider, nor
is third-party GoMore ancestry inferred from this product-specific call. Pinned
musl/EABI helpers are reused through parent manifests. Exact identity provider,
SVC/hardware behavior, cache length/ownership, eventual context alias, private
history and byte-identical whole-image gates remain open. No identity table,
provisioning/runtime admission, flash operation or hardware state changed.


Native device-ID reader checkpoint (2026-10-16):
`native-device-id-reader` compiles the58-byte6ab88 native provider as a distinct
raw-frame interface. Cached mode copies the fresh byte length from the cache
pointer without inventing a capacity check. Uncached mode invokes the existing
advertising controller-address SVC wrapper, reads the unaligned address word at
saved-frame+9, reads FICR words10000060/64, overwrites savedr0/r1 with those words,
and formats three eight-digit hexadecimal values into destination capacity25.
The external push/pop view retains actual savedr0/r1/r2/r3 contents, including
partial SVC address writes and seed bytes. The source does not substitute the
older bounded GoMore helper or claim third-party ancestry for the product body.

44 newly owned bytes comprise the exact25-byte cold cache text, one cache-valid
byte, symbolic4-byte cache pointer, one byte length24 and13-byte format text.
Cache fields at20006da4/20006e38/20006e3c match authenticated scatter bytes; the
pointer relocates to source text atc0648. These remain fields of an eventual
context owner, alongside the previous status byte. The static cold cache is
source build configuration, not authenticated provisioning or runtime identity
admission. No native recovery identity table or merge/report effect is copied.

The existing Nordic advertising SVC wrapper uses the pinned SDK17.1.0
SD_BLE_GAP_ADDR_GET enum/header and is reused unchanged. Complete source formatter
and musl copy providers execute. Main composition reuses the parent's existing
integer-runtime definitions and links seven formatter leaf objects, avoiding
duplicate integer owners. The standalone verification graph has zero imports;
the partial application closes reader and snprintf imports, leaving57.

3,616 native/source cases (3,072 cached,288 partial/full SVC,256 deterministic
random word/address cases;1,088 observations per side) compare rawR0/r1/r2/r3,
callee registers, SP, complete output and nonstack RAM. All256 cached byte lengths
execute in mapped backing, including unaligned destinations. SVC writes of0/1/4/7
bytes retain saved seed words; status values do not invent an error abort. Actual
formatter entry arguments and stacked values match native. SVC execution and
FICR contents are controlled fixtures, not physical SoftDevice/FICR evidence.
No cache capacity or overlapping-copy safety is inferred from mapped tests.

The first uncached verification omitted custom formatter tables from its source
emulator map. Arguments and restored registers matched but text differed. The
failed driver/layout/object/report/counterexample are hash-bound under
`native-device-id-reader-runtime/pre-formatter-table-map-fix/`. Loading the actual
formatter table sections resolves that harness error without changing the reader
or formatter bodies. REA headless Ghidra separately authenticates native body,
literals/cache text and the complete58-byte procedure extent.

One existing compiled symbol hint gains a tested contract:842 tested candidates,
1,115 unresolved routes and1,369 hints across3,326 rows. Native SVC success,
hardware identity, unchecked cache capacities/aliases, eventual context ownership,
private caller history, the retained NV serialization counterexample, final
placement and byte-identical firmware remain explicit gates. No hardware write,
provisioning or runtime-admission policy was changed.


Native touch-switch checkpoint (2026-10-16):
`native-touch-switch` compiles the184-byte manual84874 handler and212 exact log
text bytes. It is a separate `r1_native_touch_switch_handler` interface. Only the
research partial composition aliases the module-table import name to this body;
portable bounded-planner policy and its admission contract remain unchanged.
The documented exactly-two-backing-byte planner is not weakened to emulate native
reads. Native packet lookup accepts advertised length>12; short backing reads are
exercised only in mapped synthetic emulator memory and are not runtime approval.

Native control sends a one-byte zero response through actual checked-send/ACK
header code before inspecting payload selector. Selector1 is phone diagnostic
only. Selector2 performs diagnostics, rereads the switch byte after logs, and
selects source0 open for nonzero or close for zero. Other selectors are acknowledged
no-ops returning the selector byte. A failed response does not suppress subsequent
behavior. Logging mode reads, argument bytes and raw return words retain native
ordering; the phone branch returns the last mode shift or SDK logger result.

The external savedr1/r2/r3 view becomes response pointer/length1/zero word after
nonnull lookup. Lower response fixtures may mutate that response word and the
actual pop restores it. Null payload preserves the incoming saved words. The
ordinary C kernel uses additional private stack space; full raw scratch/APSR and
caller/private history remain separate requirements.

16,128 native/source cases comprise3,584 null,5,984 unknown-selector,3,286 phone
and3,274 glasses cases, with37,801 observations per side. Actual accessor,
checked-send and ACK-header providers execute; lower response, touch services and
logging are fixtures. Cases include all256 selector bytes, advertised boundary
lengths, full-word handle guards, switch0/1/2/255, logger modes/return words,
response-word mutation and payload changes after accessor/response/logging.
RawR0/r1/r2/r3, callee registers, SP, ordered observations and nonstack RAM match.
No touch hardware, task delivery, lease or shared-power behavior is established.

Six fresh REA headless Ghidra byte receipts bind code/literals/text. Procedure
metadata is explicitly missing, while the existing locked manual184-byte extent
remains authenticated. This body gains one tested candidate. Main linkage closes
the touch command import and exposes `r1_service_touch_open` and
`r1_service_touch_close`, leaving58 imports. No new storage owner or upstream
ancestry is inferred for this product command. Existing provider manifests retain
memory/protocol provenance instead of replacing their source bodies.

The native touch-service bodies and transitive task/hardware providers remain
source gates. Portable identity/wear/factory lease/shared-power admission,
recovery/provisioning effects, the retained NV failed-read counterexample,
private history, final layout and byte-identical firmware remain open. No
hardware write, portable policy or runtime admission changed.


Touch client-services checkpoint (2026-10-16):
`native-touch-services` compiles close8e6a0(100 bytes), open8e7d0(94) and task-event
post93504(10). It owns134 exact log-text bytes and two cold4-byte fields: clients
at200067d8 (eventual context200067c4+20) and thread handle2000666c (20006664+8).
Future context owners must alias these fields rather than allocate duplicates.
No complete service/task context initialization is claimed.

Source masks preserve native register LSLS semantics: only the low8 source bits
form the shift count, and counts>=32 yield zero. Thus source256 aliases bit0;
source32 yields no bit and may still exercise native open logging/post behavior.
No portable lease/range policy is substituted. Open returns initial clients when
its bit is already present. Otherwise it logs with fresh mode reads, posts2 only
if fresh clients are zero, rereads clients after posting, stores clients|mask and
returns that loaded pre-OR word. Close returns initial clients for an absent bit,
otherwise logs, freshly clears its bit and returns the nonzero remainder. A zero
remainder selects the still-unresolved synthetic-release dispatcher then posts4,
returning the event-post result. Task posting freshly loads its source-owned
thread cell and forwards the full flag word to the existing CMSIS provider.

42,408 native/source cases comprise20,304 each open/close,120 event posts and1,680
actual touch-command workflows;86,021 observations per side. The actual services,
task-post wrapper, command/accessor/checked/ACK-header graph execute. Synthetic
release, CMSIS flags, lower response and logging are explicit fixtures. Every
low8 shift count plus full-word aliases, client masks, logger modes, return words,
client/thread changes after logging/post/release, and saved-response mutations
are covered. RawR0, callee registers, SP and nonstack RAM match; the actual command
also checks its restoredr1/r2/r3. This does not prove the direct services' complete
scratch/APSR or private-history ABI, physical leases, task delivery or hardware.

Eleven REA headless Ghidra byte receipts authenticate code/literals/text; three
procedure receipts observe complete extents. Three locked rows gain tested
contracts:846 tested candidates,1,111 unresolved source routes and1,369 compiled
hints across3,326 rows. Main composition closes the two service imports and
exposes `r1_touch_synthetic_release_boundary`, leaving57 imports. Source-owned
client and thread fields match authenticated initialized-data observations.

No new upstream ancestry is inferred for product-specific client policy; the
existing CMSIS/FreeRTOS provider and protocol source are reused through pinned
manifests. Synthetic release and transitive effects, eventual context ownership,
portable policy/admission, retained failed-read NV counterexample, private history,
final layout and byte-identical image remain explicit gates. No hardware write,
portable planner, identity/provisioning policy or runtime admission changed.


Synthetic touch-release checkpoint (2026-10-16):
`native-touch-release` compiles93424(180 native bytes) and its934e4 timer callback
(30). It owns the complete100-byte cleared contact span at20016a60 and two cold
service-context flags at200067c4/67c6. The flags must alias offsets0/2 of the eventual
200067c4 context owner; prior client bits at+20 remain separate canonical storage.
Only authenticated contact offsets are interpreted, and all100 bytes are cleared.

When active byte+36 differs from1, native returns that byte without effects. When
active, a nonzero pending timer flag selects cancel(callback934e5,argument0) then
clears the flag regardless of cancel result. Fresh contact mode+8 selects ordinary
release or slide release. Ordinary release emits record02000000 with synthetic
flag1. Slide release computes byte-coordinate delta(+37 minus+60), direction32
for negative or64 for positive; ties use the signed last-direction byte+96. It
emits direction|release plus absolute delta(minimum1) and velocity+95(minimum1),
then emits02000000 with synthetic flag1. The flag is cleared after the final
dispatch, followed by clearing the full contact span. Native final clear returns
its advanced end pointer; the selected source preserves that rawR0 explicitly
around the existing attributed void EABI clear API. Complete clear scratch ABI
is not inferred. The timer callback zeroes44 external-frame bytes, writes word1=5
and word2=0, and forwards the message, preserving its lower raw return word.

70,656 native/source cases comprise2,160 release-state cases,all65,536 coordinate
byte pairs,80 timer,1,440 actual-close and1,440 command workflows. There are222,244
observations per side. Actual release/callback, attributed clear, client services,
command/accessor/checked/header bodies execute. Cancel, gesture dispatch, task
message, flags, lower response and logging remain explicit fixtures. Pending flag,
active/mode mutation after cancel, callback context/record mutation, signed ties,
zero velocity, all coordinate directions and clearing/order behavior are checked.
RawR0, callee registers, SP and nonstack RAM match; command restoresr1/r2/r3 too.
Private gesture-pointer values from larger caller frames are not compared.

The14-byte source callback bridge is placed at934e4 only in the verification
layout to compare cancellation pointers exactly. It executes compiled source,
not retained native instructions; this is not final-image placement proof. REA
headless Ghidra byte/procedure receipts observe both complete native extents and
literals. The literal address934d8 correctly has no procedure metadata. The locked
934e4 ledger's historical NFC/charge-oriented name is retained; the observed
44-byte message/field5 behavior does not establish that broader classification.

Two locked rows gain tested contracts:848 tested candidates,1,109 unresolved
routes and1,369 hints across3,326 rows. Main linkage closes synthetic release and
exposes `r1_touch_gesture_dispatch_boundary` and `r1_touch_task_message_boundary`,
leaving58 imports. The new control body is product-derived C with narrow ABI
bridges; existing attributed memory and CMSIS/protocol providers remain reused
through pinned manifests. No new upstream ancestry is inferred from the legacy
ledger label or event-field value.

Gesture/task effects, delayed callback delivery, eventual service-context owner,
physical touch/lease policy, retained NV failed-read counterexample, private/raw
ABI, provisioning/recovery admission, global placement and byte-identical firmware
remain explicit gates. No hardware write or portable/runtime admission changed.


Shared native task-message sender checkpoint (2026-10-16):
`native-touch-task-message` compiles93514(150 native bytes),106 exact diagnostic
text bytes and the cold4-byte queue field20006670 (context20006664+12). It reuses
the earlier thread cell at+8. Diagnostics explicitly name nfc_charge_task_msg_send;
these are shared task fields reached by touch release, not proof of an exclusively
touch task. Existing symbol names remain stable to preserve prior hash-bound
receipts; the eventual shared context owner must alias both canonical fields.

The native sender snapshots the queue pointer. A null queue logs queue-null and
returns0. Otherwise it calls the existing CMSIS queue-put with message pointer,
priority0/timeout0. Nonzero insertion status logs msg-missed and returns0. Status0
loads the thread freshly, posts0x400000, ignores that result and returns1. No
message validation, allocation, capacity, delivery guarantee or retry is invented.
Logger mode calls are fresh and logger return words cannot change the boolean.

12,672 native/source cases comprise9,216 direct sender,3,072 actual timer-callback
and384 two-call queue-state workflows, with52,665 observations per side. The
actual sender/timer/attributed clear execute; queue-put, flags and logging are
fixtures. Null message inputs are controlled lower-boundary fixtures rather than
proof that live CMSIS accepts them. Cases include null/nonnull queues and threads,
unaligned records, full-word lower statuses, logger mode sequences, thread changes
after put, queue/message mutations and repeated calls after changed queue state.
RawR0, callee registers, SP and nonstack RAM match. Timer source still uses its
14-byte verification-only bridge at934e4; full placement/private ABI is unproven.

Six fresh REA headless Ghidra byte receipts and the complete150-byte procedure
extent authenticate the body/literals/text. Main linkage closes the task-message
import with no new imports, leaving57. The existing CMSIS/FreeRTOS provider source
is reused through parent manifests; standalone RTOS calls are emulated here and
physical delivery/scheduling is not inferred. No new upstream ancestry is claimed
for this product wrapper or its diagnostic strings.

Gesture dispatch, shared context initialization/item sizing, RTOS delivery,
portable policy and recovery/provisioning admission, retained failed-read NV
counterexample, full raw/private history, final layout and byte-identical image
remain explicit gates. No hardware write or portable/runtime admission changed.


Native touch-gesture dispatcher checkpoint (2026-10-16):
`native-touch-gesture` compiles the complete690-byte3e938 dispatcher,1,236 exact
log-text bytes and15 cold state bytes (direction,count and three timestamps).
Existing contact100-byte storage, clients, pending/synthetic flags and low-battery
thread cell are reused. New fields alias offsets1/8/24/28/32 of the eventual
200067c4 service context; its other canonical source owners are not duplicated.

The body retains initial direction/timestamp capture, reset of direction tracking
for bits1..4 or unsigned inactivity>400, host-reset diagnostics/marker2/flag2,
reversal suppression after two same-direction events, 16-bit count wrap, release
timer arming(callback934e5,0,307), fresh post-effect event precedence and slide
log throttles at>1000. Tap/double/long/negative/positive/synthetic-release select
native event IDs1/2/0/4/5/8. Fresh input distance/velocity precede the tick call.
Packet fields use the external savedr1/r2/r3 view, including unaligned tick at+7.
Configuration exactly85 selects length5, otherwise11. The first full-word handle
check rejects onlyffff; the second getter is fresh and is forwarded without a
second guard. Native early-return words, including context pointer on reversal
and shifted event word on unmatched paths, are preserved.

59,328 native/source cases produce546,563 observations per side. They cover every
event byte, precedence, direction/count edges, unsigned timestamp thresholds and
wrap values, pending/contact modes, reset and logging effects, raw lower returns,
config lengths and both handle reads. Lower boundaries are explicit fixtures;
all are exercised, including5,061 schedules,20,088 each marker/flag calls,54,264
each tick/config calls,99,366 handle reads and45,102 sends. Mutations after logging,
marker/flag/schedule, tick, configuration and sending test captures/fresh reads
and the saved packet words. RawR0/r1/r2/r3, callee registers, SP and nonstack RAM
match. No native instruction executes on the source side.

The initial passing matrix correlated pending and contact-mode bits and therefore
did not exercise schedule. Its driver/report/receipt are retained hash-bound in
`native-touch-gesture-runtime/pre-independent-pending-fixture/`. Independent bits,
wrap timestamps and nonzero lower-observation assertions close that coverage gap
without changing the compiled dispatcher. This is a superseded limited proof,
not an erased counterexample or a claim about timer delivery.

Seventeen REA headless Ghidra byte receipts and a complete690-byte procedure
receipt bind code,literals and all diagnostic text. Direct Ghidra-MCP was checked
and reports no running instance; no fresh direct-GUI analysis is claimed. Main
linkage closes the gesture import with no new imports, leaving56. All needed
existing reset,CMSIS,delayed,configuration,getter and BLE providers are source-linked
through parent manifests. Tests here emulate their effects and do not upgrade
prior ABI/private-frame limits. No new third-party ancestry is inferred for the
product dispatcher; pinned Nordic/FreeRTOS/CMSIS/provider provenance is retained.

The full shared context, retained NV failed-read serialization counterexample,
advertising configuration getter's private-read history, physical timer/BLE/reset
behavior, portable policy and recovery/provisioning admission, full raw/private
ABI, global placement and byte-identical firmware remain explicit gates. No
hardware write or portable/runtime admission changed.


Native system-settings checkpoint (2026-10-16):
`native-system-settings` compiles84524(260 native bytes),73750 bit getter(36) and
73800 bit1 setter(48), plus164 exact diagnostic text bytes. All existing class,
handle, memory and protocol owners are reused; no new RAM owner is introduced.
The research partial module aliases its import to a separate native handler;
the documented exact-twelve-byte portable planner/admission is unchanged.

Get ignores cached-read status, obtains the persisted bit via an external52-byte
raw record view, emits twelve initialized response bytes with normalized state
at byte5, logs fresh output-byte reads and reads the sequence after logging.
The direct getter still reads the class for NULL destination and returns that
read status; nonnull destination receives bit1 and returns it. The setter ignores
read/write status, updates only bit1 from input low bit, uses a fresh write handle
and forwards the idle/flush helper result. No failed-read default is invented.

Set acknowledges command15/version1 before payload lookup, handles NULL payload
as raw0, logs fresh type/status fields, returns nonzero type unchanged, and
compares the raw requested status with the normalized stored Boolean. A changed
status is normalized for the bit setter, then reread and normalized again for
regulator SVC. Thus a provider mutation during persistence affects the requested
SVC mode exactly as native. No packet-backing guard is silently added to native
control; declared short backing is exercised only in mapped emulator memory.

S140 SD_POWER_DCDC_MODE_SET is taken from the actual pinned Nordic SDK17.1.0
nrf_soc.h and statically asserted63. A narrow source SVC/BX bridge preserves the
native regulator call contract; emulator code hooks intercept it before hardware
execution. The builder authenticates every consumed SDK header against sdk.zip
SHA5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061.
This reuses the upstream API/enum and existing CMSIS/KV/memory providers while
retaining attributable revisions; it does not infer a vendor implementation for
the product-specific settings logic or prove regulator configuration.

21,056 primary comparisons (10,304 handler,9,216 getter,1,536 setter) produce119,136
observations per side. Actual bit helpers, cached read/write,musl and packet
accessor execute; idle/transport/logging/critical callbacks and SVC effects are
fixtures. Cases cover all stored-byte patterns,direct helper size/read failures,
NULL/aliased outputs, bit masking,fresh handle/port callbacks, get/set flags,
raw requested values, logger mutations, fresh sequence and post-setter status.
There are4,019 SVC observations. RawR0,callee registers,SP and nonstack RAM match.

A separate192-case failed-read handler probe across six initial stack-byte seeds
also matches (78 SVC samples). Its receipt binds the same compiled graph and is
explicitly limited to those mapped samples. It does not establish cross-call
private history or close the retained NV serialization frame counterexample.
Normal handler matrix reads use complete cached records; direct failed-read
contracts and the additional caller probe are reported separately.

Eight REA headless Ghidra byte receipts and three complete procedure extents bind
native bodies,literals and text. Main linkage closes the settings import without
new imports, leaving55. Source data ownership remains canonical. The exact native
SVC wrapper instruction, complete getter/setter raw scratch, private histories,
physical persistence/flush/regulator behavior, bounded portable admission,
provisioning/recovery, final global placement and byte-identical firmware remain
separate gates. No hardware write or runtime-admission policy changed.


Native health-settings checkpoint (2026-10-16):
`native-health-settings` compiles83f24(300 native bytes),73798 flag/word getter(44)
and73868 flag0/word setter(60), plus208 exact diagnostic text bytes. Existing
class,handle and memory owners are reused, with no new RAM ownership. The research
partial module aliases its import to a distinct native handler; bounded portable
planner/backing/admission policies are not changed.

Getter output order is flag byte then word32, with rawR0 determined by the last
present output (or cached-read status when both outputs are NULL). External52-byte
views retain failed-read seed data. Setter compares the stored low bit with the
full supplied value before inserting its low bit. Equal values skip both the
word32 update and flush, returning the original flags byte. Unequal values update
only bit0 and word32, freshly load the write handle and forward idle/flush result.
No default record, pre-comparison Boolean coercion or time-only update is added.

Read commands construct twelve initialized response bytes: word32 at0..3, enable
at4, trailing zeroes. Logs read fresh scalar outputs, while sequence is read after
logging. Set commands locate payload before acknowledgement, snapshot current
flag/word, log exact requested/current values, compare raw requested enable, and
only on difference call the normalized setter then publish event100d over the
live one-byte payload status. Provider mutation after persistence therefore
changes the published byte. Timestamp-only changes can remain suppressed even
when another raw-status comparison reaches the setter, as native controls it.

21,056 primary native/source comparisons (10,304 handler,9,216 getter,1,536 setter)
produce119,496 observations per side, including4,879 event samples. Actual cached
read/write,musl,packet accessor and new helpers execute. Event,idle,transport,
logging and critical callbacks are fixtures. Normal handler workflows use full
cached records; direct helper tests include size failures, raw seed retention,
NULL/aliased outputs, all stored-byte patterns, full-word setter values, fresh
handles/port callbacks, logger mutations and conditional word writes. RawR0,
callee registers,SP and nonstack RAM match within that explicitly bounded scope.

OPEN FAILED-READ CALLER GATE:
`native-health-settings-runtime/failed-read-frame-probe.json` is a retained
counterexample, not a passing receipt. In mapped synthetic seed0/set-mode state
with initial requested byte0 and rejected size0 reads, a logger fixture changes requested state and word.
After the second failed read, an explicit fixture changes the global handle to a
valid52-byte alternate class. Both implementations return0 and select that same
write, but retained private-frame bytes0..7 differ and actual cached-write RAM
therefore differs. The first probe, where rejected writes left RAM unchanged but
write-payload traces already differed, is archived under `initial-failed-read-probe/`.
Both drivers/receipts are hash-bound. This demonstrates conditional emulated frame
propagation, not an observed physical-device defect. No zeroing, normalization,
record truncation or rejected-result concealment is used to claim closure.

The handler and helpers remain source-compiled bounded contract candidates; full
failed-read caller/private ABI is unverified. The prior NV serializer's separate
failed-read counterexample remains retained too. The new standalone audit expects
this mismatch as an open gate and does not treat it as a green behavioral proof.

Eight REA headless Ghidra byte receipts bind complete code/literals/text. Fresh
metadata observes73798, while83f24 and73868 metadata are explicitly unavailable;
the locked300/60-byte extents and authenticated bytes remain the manual evidence.
Main linkage closes the health-settings import without new imports, leaving54.
No new upstream ancestry is inferred for product logic; pinned memory/protocol/
CMSIS provider provenance remains inherited through manifests.

Persistence,event delivery,private caller history,portable admission,provisioning/
recovery policy,global placement and byte-identical firmware remain open. No
hardware write or portable/runtime-admission policy changed.


Native user-profile command checkpoint (2026-10-16):
`native-user-profile-command` compiles84a10(202 native bytes) and62 exact log-text
bytes. It reuses the actual packet accessor and flag-C acknowledgement body, with
no new RAM owner. A separate native handler is aliased only by the research
partial module; portable profile validation/event-consumer policies are unchanged.

Null payload sends command4/version1/flag1 with a fresh sequence and returns that
lower raw result. Nonnull payload logs four fields with native ordered byte and
halfword reads; logger mode and later field reads remain fresh. It then sends
flag0, ignores that return, and constructs a profile event after acknowledgement.
Event100a is published over12 bytes: input byte1, sex1 for byte0==0 or2 otherwise,
low bytes of the two halfword fields, then sixff bytes. Native writes only these
ten bytes. The external frame's remaining two bytes are retained verbatim, not
zeroed or replaced by defaults. The event publisher's raw result is returned.
Declared short backing is only exercised in mapped synthetic memory; native's
advertised length>12 lookup is not promoted to a safe six-byte backing contract.

76,384 native/source cases comprise50,176 first-byte/length/seed/mutation matrix,
18,144 field-edge and8,064 two-call workflows. There are417,004 observations per
side, including84,448 lower responses and71,904 events. All256 byte0 values, byte1
edges, halfword boundaries, four stack seeds, logger sequences/return words,
fresh sequence/payload fields after logging and acknowledgements, and last-two-
byte mutations are covered. Actual accessor and flag-C header construction
execute; lower response,event and logging are explicit fixtures. RawR0,callee
registers,SP and nonstack RAM match, and every published12-byte record is compared.
Source-side native instruction execution is forbidden by the verifier.

Six REA headless Ghidra byte receipts authenticate body,literals and text, with
initial shorter text-prefix reads retained alongside complete reads. Procedure
metadata is explicitly unavailable; the locked202-byte extent and native bytes
remain the manual evidence. Main linkage closes the profile-handler import with
no new imports, leaving53. Existing protocol/memory/SDK provider provenance is
inherited through hash-bound manifests; no new upstream ancestry is inferred for
this product handler or its profile semantics.

The external event-tail view and these two-call fixtures do not prove all real
callers' private history, full scratch/APSR ABI or final instruction placement.
The health-settings failed-read/fresh-valid-handle RAM counterexample and earlier
NV frame counterexample remain unchanged open gates. Actual profile consumer and
event delivery, portable policy/admission, provisioning/recovery, whole context
ownership and byte-identical firmware remain unproven. No hardware write or
portable/runtime-admission policy changed.


### Output GPIO five-adapter source checkpoint

Five product table adapters now compile from `native_output_gpio_drivers.c`:
0x54d8c,0x54d92,0x54f3c,0x54f42 and0x54f8a. Each loads the pin word at
record+8 and tail-transfers to an existing Nordic GPIO HAL/GPIOTE provider.
REA headless Ghidra12.1.4 supplied three fresh authenticated byte receipts;
Ghidra-MCP reported no running instance. No procedure metadata or whole-function
coverage is inferred from these byte reads. No frozen ownership row was added.

A separate explicit-section verification link reproduces all30 adapter bytes
exactly at their native addresses. Its absolute lower-provider symbols are
verification boundaries only. The partial runtime instead links actual existing
source providers, closing five parent imports and leaving48. The primitive
implementations retain existing pinned Nordic SDK17.1.0 provenance; no copied
native executable body or newly inferred upstream ancestry was introduced.
An initial verification link used the default linker script, which consumed the
input sections into generic.text and produced empty requested extractions. The
failed driver and ELF remain in `pre-explicit-section-layout/`; explicit output
sections fix the verification layout without changing the C candidate.

The registrar metadata callback declarations have not been migrated to proven
body signatures. Driver14, open/close/slot operations, init-selector table,
negative command indexing, callback side effects and timing remain evidence
gates. This adapter identity does not prove lower-provider instruction identity,
whole-image placement, peripheral behavior or a flashable firmware image. The
health-settings and NV failed-read private-frame counterexamples remain open.
No hardware writes, policy/admission changes or authenticated corpus edits.


### Output GPIO callback configuration, read and direct-toggle bodies

Source bodies now cover supplemental native entries0x54cd0(callback setup),
0x54e20(input-bit read) and0x54ea8(direct port toggle). Four fresh REA Ghidra
byte receipts authenticate their spans/literals and0x79288 port decoder. These
are supplemental functions without newly invented ownership rows. The callback
setter takes its pointer inr1, checks NULL before device lookup(return10),
returns1 for an unknown name, and writes byte20/word24/word28 sequentially.
Read returns1 for unknown/unopened records and otherwise stores one live IN bit;
it retains the saved incomingr3 on failure and normalized pin inr3 on success.
Toggle retains normalized pin inr3, returns the raw port pointer inr0, and writes
OUTSET=mask&~OUT thenOUTCLR=mask&OUT. No pointer/pin guard was introduced.

The actual pinned Nordic SDK17.1.0 inline port decoder is consumed unchanged;
every consumed SDK header is checked against the authenticated SDK ZIP. Product
operation logic is recovered independently and is not represented as upstream
Nordic source. Existing actualstrcmp and canonical five-record configuration are
selected from the parent source composition. No new RAM owner, opcode array,
policy/admission change or hardware write is involved. The registrar's metadata
function declarations remain explicitly unmigrated body-ABI gates.

The differential verifier passed11936 cases(config864/read6912/toggle4160),
including29256 actualstrcmp calls per side, all256 byte pin values plus fullword
edges, both decoded ports, output/pin/open-state aliasing, configuration read/write
overlap, fresh device-name mutation after a comparison, four stack/RAM poisons,
rawr0, read/toggle savedr3, callee registers/SP and nonstack RAM. Canonical code
pointers alone are normalized before RAM comparison. The comparison trace SHA is
b5a4225db7b06adf28ac55f97dbe6eca5858717a9889a73d7dbe9c2bd99c357a.
MMIO checks compare register bytes; write-one physical semantics and electrical
behavior are not simulated or claimed. NULL output faults, arbitrary malformed
backing, unaligned callback configuration, full scratch/APSR and real cross-call
private stack history remain unproven. The three unresolved operation pointers
in the verification graph are not executed and the verifier rejects entry into
their fixture addresses. Main source linkage closes three imports, leaving45.
Open/close/command dispatch and pre-record initialization/release tables remain;
health-settings/NV failed-read counterexamples and final image gates remain open.


### Output GPIO signed-command dispatcher

Supplemental native0x54d20 now compiles as `r1_output_gpio_slot18` from product C.
A fresh REA Ghidra byte receipt covers its108-byte body/padding/literal span.
The signed comparison rejects commands>=3 but admits negative fullwords; native
32-bit shifted/wrapping address arithmetic is preserved through integer table
addresses. There is no invented negative-command guard. Names are freshly read
at every actualstrcmp call; unknown names return1, unopened records return27.
Zero config0d selects the first three canonical drivers without delay; nonzero
selects the next three drivers then calls the existing subtract-three cycle
primitive with64000, ignoring both lower returns. The branch is selected before
the driver call and stays selected if that driver mutates config0d/open/pin.

The verifier passed11232 cases, with30960 actualstrcmp calls,5040 driver-boundary
calls and3360 delay-boundary calls per side. Tests cover all five names/unknown,
opened0/1/255, config0d0/1/255, signed positive rejection, negative mapped indices,
INT_MIN wrapping aliases, fresh name mutation, driver mutation and four RAM/stack
poisons. Trace SHA3790e3b765016f172404c4e79de5fbc4f263cbbf0eb27a33ccec5570d909a0e1.
Only driver/delay observations are fixtures; actualstrcmp and command control
flow execute. Patched valid targets make selected negative table locations
observable, not admitted real-world targets. Arbitrary negative targets/faults,
lower register residue, full scratch/APSR, timing and cross-call private history
remain gates. Actual SDK/HAL/driver/cycle source remains linked in the main
composition using existing authenticated provenance; no new upstream ancestry
is attributed to this product dispatcher. No new RAM owner or hardware writes.
Main imports fall45->44; open/close and their sixteen-byte pre-record table remain.
Existing failed-read counterexamples, metadata ABI and full-image gates remain.


### Output GPIO lifecycle and source-owned predecessor table

Six source bodies now cover native close0x54c58, open0x54d98, direct release0x54cbc,
direct initialize0x54df0, task release0x54f28 and task initialize0x54f48. The
94-byte close entry retains its frozen legacy `r1_named_gpio_output_set` label;
the C symbol is explicitly `r1_output_gpio_close`. No ledger label or extent was
rewritten; the other five entries are supplemental. Six fresh REA headless
Ghidra byte receipts authenticate their body/padding/literal spans. Existing
canonical GPIO records remain unchanged. A new mutable sixteen-byte source table
owns four symbolic function pointers at native0x20007218, immediately before
records0x20007228. Verification placement and pointer-normalized cold bytes match
all16 bytes. Final whole-image adjacency/relocation remains a linker gate.

Open looks up five names, returns1 if unknown and0 if already open; enabled
nonnull open callbacks receive their own address inr0 before a fresh selector
read and initialization dispatch. Open sets opened1 after dispatch, ignoring
lower returns. Close returns1 if unknown,0 if closed; it snapshots enabled/nonnull
close-callback presence, dispatches release, then freshly rereads the callback
address without rechecking enable, calls with that address inr0, and stores0.
Raw selectors are not clamped. Selector0 uses GPIOTE, selector1 direct GPIO.
The table-access arithmetic retains native wrapping behavior; arbitrary selector
pointees/faults and full callback scratch-register residue remain unproven.

Task helpers reuse the actual pinned Nordic SDK17.1.0 source interfaces and
short-enum3-byte output configuration at record+14. Nonzero init/out-init status
calls the existing returning `r1_adc_error` provider and continues; the logger
neither resets nor halts. Task enable, level set/clear, disable and uninit retain
fresh pin/level reads at native call boundaries. Direct helpers consume upstream
nrf_gpio_cfg/set/clear inline HAL unchanged. All newly consumed SDK headers are
checked against the authenticated SDK archive. Product lifecycle/table logic is
not attributed to Nordic. Existing error logger ownership is reused.

31104 differential cases passed(open10368/close10368/workflow10368), with221184
actualstrcmp calls per side, four stack/RAM poisons, all five/unknown names,
opened0/1/255, enable0/1/255, both selectors, callback presence combinations,
returning initialization failures and repeated open-close-open-close histories.
The actual lifecycle, all four helper bodies, strcmp and inline HAL execute;
SDK calls and returning error logging are explicit test boundaries. Tests cover
callback selfr0, fresh selector/pin/level after callbacks, changed close target
and enable after release, raw lifecycle r0, callee registers/SP, nonstack RAM and
MMIO register bytes. Trace478afff84d38597631079eb373cb2d4b013f859e6296d335d8d04ed3bc78e0b8.
Helper raw return/scratch values, callback private frames, arbitrary selector
targets, MMIO physical semantics, electrical behavior, full boot and timing are
not proved. The main partial runtime uses actual existing SDK/error providers;
the focused verification graph exposes those lower calls as fixtures. All eleven
output-GPIO operation/driver imports are now source-resolved across checkpoints,
leaving42 main imports. Native metadata prototypes remain explicitly unmigrated.
Existing health/NV failed-read private-frame counterexamples and whole-image
configuration/toolchain/byte-identity gates remain open. No hardware write,
portable-policy/admission change or firmware/corpus replacement occurred.


### Peripheral handle-binding bodies and source-owned cells

The locked24/32/48/44-byte functions0x50128(motion IRQ),0x502c4(LED/LDO),
0x50944(PPG) and0x51310(touch) now compile from product C, with the supplemental
20-byte motion-bus binder0x50150. Ten fresh REA Ghidra receipts authenticate all
five bodies and their literal/name spans. Ten individual zero-initialized handle
cells own40 bytes at authenticated addresses, with100 exact name bytes; no whole
motion/PPG/touch context or intervening fields are claimed. Actual canonical
registry/head, strcmp and slot08 dispatcher are reused from source providers.
The focused verification graph has zero unresolved imports. Main partial source
linkage closes four peripheral-module imports without new imports, leaving38.

Native PPG behavior caches i2c_4/ppg_int/ppg_reset_en then passes the last-loaded
reset handle to slot08, even if that handle isNULL. It does not substitute the
bus handle. Motion first caches i2c_1 then acc_int_1. Touch caches i2c_0, then
**touch_rdy_out at0x20006800**, then**touch_rdy_in at0x20006804**. LED/LDO caches
ppg_led_en then touch_ldo_en. Every nonzero cache is retained and every zero
cache is retried; later cells are freshly read after preceding lookups. Rawr0 is
the last cache/lookup value, except PPG returns the actual slot08 result.

6560 differential cases passed: LED640/motion-bus160/motion-IRQ640/PPG2560/
touch2560, with14240 actual find calls,5120 actual dispatch calls and1728 open
operation fixtures per side. All local registry-presence/cache masks, missing
operation callbacks, four result/stack/RAM patterns, repeated calls and cache/
registry mutation during lookup/open are covered. Actual registry/strcmp and
slot08 execute; only the target open operation is a fixture. Rawr0, callee
registers/SP and nonstack RAM match. Traceba718da8b0b15f4141d40017f61e89544ceb20abe5db569b186409bd723b0502.

The first candidate guessed the opposite touch input/output name order; the
exact-string check rejected it before behavior validation. Its source/object,
reports/test driver and failure log remain underpre-authenticated-touch-name-fix.
A subsequent verifier link omitted the standalone motion-bus root after inlining
removed it; that builder/report/failure remain underpre-motion-bus-root-fix.
The current link explicitly retains all five functions. Archive hashes are bound
in superseded-evidence.json. These are corrected candidate/test-link errors,
not evidence to normalize away. Product binders have no inferred third-party
ancestry; existing registry/provider provenance is inherited without claiming
hardware/provider identity, licensed sensor implementation or successful boot.
Full scratch/APSR/private-frame ABI, whole context ownership, malformed cached
pointers, peripheral behavior, existing failed-read counterexamples and complete
configuration/toolchain/byte-identical firmware remain gates. No hardware writes,
policy/admission changes or frozen corpus/ownership edits were made.


### Hardware-TWI completion callbacks with upstream CMSIS kernel-state query

Product callback0x70778(78 locked bytes) and supplemental0x707cc(74 bytes) now
compile from C. Three fresh REA Ghidra receipts authenticate both callback spans
and the native CMSIS kernel-state query0x7d26c(28 code bytes plus literal).
Existing216-byte hardware-TWI clusters remain the sole source owners. Event0
stores done1/result0; event1 result5; event2 result7; unknown bytes retain the
previous result. Bus0 sets error byte1 for every nonzero event and reads ready
byte2. Bus1 never writes byte1 and uses that byte as ready. A successful event
does not invent an error-flag clear. No event/handle guard was added.

Nonzero ready and semaphore invoke the existing pinned CMSIS-FreeRTOS
`osKernelGetState` source, selected unchanged from the authenticated compiled
CMSIS unit. CMSIS-FreeRTOS pin d213f261b5be6bb29a7cce8b84071706b72f4d53 and
FreeRTOS pin def7d2df2b0506d3d249334974f51e427c17a41c remain inherited from
existing provenance. The selected38-byte pre-relocation getter matches its
original source object. Its single4-byte zero-initialized KernelState cell is
placed at native0x20007870 for verification; consolidation with future CMSIS
initialization/setters and final global placement are explicit gates. The main
partial composition contains one KernelState and actual existing scheduler and
semaphore providers, closing both IRQ imports without new imports, leaving36.

66624 cases passed(matrix61440/mutation5184), with43840 scheduler observations,
18304 release observations and384 freshlyNULL release arguments per side. Both
actual product callbacks and unchanged CMSIS state-query control flow execute;
only xTaskGetSchedulerState and osSemaphoreRelease are explicit fixtures. All256
event bytes, ready0/1/255, missing/present semaphores, scheduler/kernel-state
branches, four result/stack/RAM patterns, repeated events and mutations during
state query are covered. Release occurs only for running2/locked3 and rereads
the semaphore afterward without rechecking ready. Rawr0, callee registers/SP
and nonstack RAM match. Tracec64bb7740f08b18aefb3d588b62dcd79a7f7f8ac4e7ac52dffa91fa3fe302008.
Canonical configuration code pointers alone are normalized. No physical IRQ or
semaphore delivery, callback scratch/APSR/private-frame ABI, metadata prototype
migration, native compiler equivalence or whole-image identity is claimed.

The first audit attempt used the common relocation-free section reader on this
relocation-bearing CMSIS function and was rejected. Explicit section extraction
compares its pre-relocation bytes correctly; no provider source or differential
receipt changed for this audit repair. Hardware TWI open/close/read/write and
full transfer-driver/configuration evidence remain. Existing failed-read/private
frame counterexamples and complete firmware configuration/toolchain/link gates
remain open. No hardware write, policy/admission change or corpus replacement.


### Hardware-TWI native completion-wait policy

Both locked100-byte wait bodies0x70820/0x7088c now compile from product C. Two
fresh REA Ghidra byte receipts cover each body and its two literals(108 bytes).
The source references the existing canonical hardware-TWI clusters, CMSIS
kernel-state/tick-frequency/semaphore-acquire providers and the existing Nordic
subtract-three cycle primitive. No new RAM/configuration or local RTOS/driver
implementation is introduced. Their source-linked runtime keeps36 imports: these
new bodies do not yet close a parent import, because transfer adapters remain.

Primary ready is byte2, secondary byte1. With ready and a nonnull semaphore,
kernel state2/3 selects CMSIS acquisition. Ticks use wrapping32-bit frequency*
milliseconds, then unsigned /1000, with a minimum of1. The semaphore is freshly
loaded after the frequency call. Any nonzero acquire status returns13; zero
returns the fresh full32-bit result word without checking done. Other states
fall back to polling: wrapping milliseconds*1000 limit, done checked first,
postincrement counter compared against the limit, and delay64 cycle-units per
permitted iteration. Poll success returns fresh result; timeout returns13.
No recheck switches a busy wait into the semaphore path midway through polling.

21984 differential cases passed(matrix16800/mutation5184), with10784 state,
5696 frequency,5696 acquire and531168 cycle-delay observations per side, including
864 freshlyNULL acquire arguments. Both actual wait bodies execute; CMSIS/delay
calls are explicit observation fixtures in the focused graph, while actual source
providers remain linked in the main composition. Both buses, ready0/1/255,
semaphore presence, all state branch classes, frequency/timeout wrap edges,
minimum ticks, completion before/after delays, bounded never-complete timeout,
four RAM/stack/result patterns and semaphore/result mutation during lower calls
are covered. Rawr0, callee registers/SP and nonstack RAM match. Trace
 d52ce5fe50dea40c9ad5358efd6cc3400bb0103e9496478432921a1d542305d8.
Polling timeout exhaustion was bounded to limits<=1000; larger limits include
immediate/early completion. All32-bit timeout/frequency combinations and elapsed
physical timing are not claimed. Canonical code pointers alone are normalized.

Full scratch/APSR and private-frame ABI, physical semaphore/IRQ/timing behavior,
TWI lifecycle/register/packet transfer bodies and final firmware identity remain
open. Inspection of the next transfer layer records real width differences:
primary register/read paths use halfwords where secondary paths use bytes; the
upstream nrfx_twim length is size_t while legacy nrf_drv_twi wrappers expose
uint8 lengths. These are evidence to preserve in subsequent source reduction,
not justification to coerce all transfers through one narrowed API. No hardware
write, portable-policy/admission change or corpus/ownership edit occurred.


### Four TWI register adapters and unchanged Nordic TWIM dependency

Locked native register read/write bodies0x54ff8(96),0x5505c(94),0x550c0(90) and
0x55120(90) now compile from product C, with four fresh REA Ghidra span/literal
receipts. The unchanged Nordic SDK17.1.0 `nrfx_twim.c` and every consumed SDK
header are independently checked against the authenticated SDK ZIP. Its compiled
TX/RX/xfer graph has zero unresolved providers and is source-linked with the
product adapters and existing source wait/error providers. This provides an
attributable upstream maintenance path instead of copying the TWIM engine.
Product adapters are separately attributed native recovery, not Nordic source.
The SDK control-block native identity/configuration/placement and hardware
transfer behavior remain unverified. The selected SDK object has104 bytes of
candidate m_cb BSS; these are not admitted as a proven native RAM replacement.
Main imports remain36: top-level operation/lifecycle wrappers still need bodies.

Read sends the low register byte with no-stop, clears bus0 done/error or bus1
done only, waits500(primary)/100(secondary), clears done again and receives.
Primary RX length is narrowed to8 bits; secondary retains the full size_t word.
The final timeout tests the original full length against50, selecting200/500.
Every nonzero lower result returns its low byte, including errors whose low byte
is0. The40-byte external frame preserves the register byte inside savedr3 and
returns savedr2=1; source bridges retain those exact external words/addresses.

Write rejects length>80 with9. It copies register+payload once, clears flags
once, sends with stop and retries every nonzero TX error except17, logging the
full error word each retry. Retry does not recopy input or clear flags. TX17
returns17 without waiting/logging; successful TX waits500(primary)/200(secondary)
and returns low-byte wait result. The native104-byte write frame allocates84
local bytes then savedr4: buffer starts at+4, so length80 copies its last byte
to+84, overwriting savedr4's low byte. This observable overrun is preserved, not
replaced with an invented79-byte limit. Raw callee checks explicitly expect that
changedr4; physical callers and full downstream consequences remain a gate.

30720 differential cases passed(7680 for each adapter), observing32640 TX,
1536 RX,11264 waits,7680 error logs and1920 length80 savedr4 cases per side.
Actual four product bodies execute; nrfx TX/RX, wait and returning error logger
are fixtures in the focused verification graph. The main partial graph instead
links actual pinned SDK and existing source providers. Tests cover byte/halfword/
fullword length edges, address bytes, full register values narrowed at use,
retry sequences/full error words, TX17, length rejection, read-frame raw words,
mutations during TX/wait/log, four RAM/stack patterns, rawr0, saved readr2/r3,
callee registers/SP and nonstack RAM. Trace
5937663fe1609f3ce3d697106ae3f0852b08b72e845749f9139769eeffe3c86a.
Only canonical configuration code pointers are normalized. SDK electrical/DMA
behavior, invalid backing/full address words, endless error retries, complete
scratch/APSR/private stack history, all real callers and final byte identity
remain unproven. Existing failed-read counterexamples stay open. No hardware
writes, policy/admission changes or corpus/ownership edits occurred.


### Hardware-TWI packet operations and native-call-frame repair

Supplemental device read0x55414/read0x55448 and write0x55ce0/write0x55d50 now
compile from C preparation/status kernels plus source assembly ABI bridges.
Four fresh REA Ghidra span/literal receipts bind all bodies. Existing cluster,
register/wait, SDK and error providers are reused; no new data owner or claimed
upstream ancestry for product policy is introduced. Main partial source linkage
closes all four read/write imports without new imports, leaving32. Open/close
operations remain. No new ownership row was invented for these extra entries.

Read checks NULL before opened, returning9/8; valid requests load primary
halfword register/length versus secondary bytes, use output pointer+12, and map
any fullword nonzero register-adapter result to12. The native savedr3 slot becomes
the legacy instance pointer only on the valid-open path; early returns retain
incomingr3. Write checks NULL/open returning4/10, reads a full halfword length
at+8 for the single-byte branch, and otherwise uses primary halfword register/
length versus secondary byte register/narrowed length. Register-helper failures
map to11 without truncation. The single-byte branch copies register/data into
the savedr3 word's low16 bits, clears done(and primary error), sets savedr2=0,
sends two bytes then waits500/100 only after fullword TX0. TX/wait results are
truncated before mapping to11; e.g.0x100 maps to0 and a nonzero TX does not wait.
The valid multibyte path restores savedr2 as the legacy instance pointer; early
write paths retain the incoming request pointer. Frame bytes are not zero-filled.

The initial C-kernel-call version passed46080 isolated cases but the actual
register graph exposed a raw TX-buffer-address mismatch: native0x2003efd4 versus
source0x2003efbc, with matching payload/r0/nonstack RAM. This was retained without
normalization underpre-native-call-frame-fix. Source/object, drivers/reports and
failed probe remain hash-bound. The three old tested graphs were reproduced
byte-for-byte from the preserved candidate object and checked against their
original report hashes. The repair uses a temporary32-byte preparation plan
below the native saved-word frame, returns all compiler preparation frames, then
restores nativeSP before calling actual providers. Status mapping remains C.
Write bridges also preserve the native packet pointer inr4 across the provider
call; outer savedr4 restoration retains the native80-byte inner overwrite's
bounded caller behavior. The temporary plan is never a firmware opcode blob.

The repaired candidate passed the same46080 isolated cases(11520 per wrapper),
plus5760 cases with actual register adapters, including SDK buffer addresses and
payload bytes without pointer normalization. Isolated trace remains
4da29bc35cb22586f1c9c801dccc81bcee3af9587dcbf6f9722e901bcc369996;
composed traceb65a80927d4163bb43fcf7edcb6c39e33acc4c7c11ca1bbc04b81ab605ec62a3.
The focused graph fixtures register/TX/wait calls; the composed graph executes
actual register bodies with SDK/wait/error boundaries. Cases include early paths,
width/length edges, fullword errors, one-byte versus257-byte branch selection,
four RAM/stack patterns, lower-call mutation, savedr2/r3, callee registers/SP and
nonstack RAM. Only canonical metadata code pointers are normalized. The SDK and
CMSIS providers are actual source in the main composition, not fixture aliases.

The earlier pointer counterexample is closed for the tested native call-frame
addresses; complete private-frame histories/full scratch/APSR and metadata ABI
migration remain open. Malformed/aliased arbitrary request backing, real
callbacks/RTOS/DMA/electrical behavior, SDK control-block identity/configuration,
unbounded register retries, existing health/NV failed-read counterexamples and
complete image/toolchain/placement/byte identity remain gates. No hardware write,
portable-policy/admission change or corpus/ownership edit occurred.


### Hardware-TWI lifecycle and consolidated legacy/TWIM source family

The four locked product bodies0x55180/0x551b4(close44 bytes each),0x55278(open100)
and0x552e4(open66) now compile from C kernels and explicit native config-frame
bridges. Six fresh REA Ghidra byte receipts authenticate bodies/literals and two
8-byte config tails. Source-owned readonly tails at0x9a600/0x9a620 match all16
bytes:400kbps, priority2, clear-bus0, hold-uninit1(primary)/0(secondary), padding0.
The sixteen-byte legacy instance/config layouts are statically checked against
unchanged SDK headers. No new product RAM/context owner is claimed.

Open returns0 if already opened. Both buses snapshot pin words into config at
native0x2003efe0; only primary configures both GPIO outputs first, with a fresh
second-pin read after the first GPIO call. Legacy init receives instance at
record+16, the full native16-byte config, a freshly loaded IRQ pointer andNULL
context. Nonzero status logs through the existing returning error provider and
continues. The embedded TWIM instance at record+20 is enabled and opened1 stored
unconditionally after enable. Close returns0 if closed; otherwise disable/uninit
receive record+20, then native power word0x40003ffc/0x40004ffc is written0, read
through a volatile pointer, written1, and opened0 stored. Those register operations execute only
inside the verifier emulator; no physical write was issued.

Unchanged Nordic SDK17.1.0 `nrf_drv_twi.c` now compiles beside unchanged
`nrfx_twim.c`, with all consumed source/header bytes checked against the SDK ZIP.
The runtime is recomposed from the pre-TWIM source parent and unchanged product
leaves, selecting legacy init plus TWIM init/TX/RX/enable/disable/uninit together.
This avoids appending another m_cb beside the historical TX/RX-only selected
object. Old objects/reports remain intact. The consolidated selected graph has
zero unresolved providers, exactly one104-byte TWIM m_cb and one8-byte handlers
plus one8-byte contexts array. These are candidate SDK state, not proven native
control-block address/layout replacements; native state identity/configuration,
callback/event delivery and physical initialization remain gates. This retains
the upstream implementation/license and maintenance path instead of rebuilding
the legacy driver engine locally. Product lifecycle policy is independently
recovered and is not attributed as Nordic source.

7200 differential cases passed(open2400/close2400/workflow2400), observing4000
GPIO,4000 init,3000 returning error,4000 enable,6400 disable/uninit and6400 each
power0/power1 transitions per side. The actual lifecycle/config/frame/power-word
logic executes; SDK/GPIO/error providers are explicit focused-graph fixtures.
Main linkage uses actual source providers. Both buses, early opened states,
pin/port/fullword edges, fullword init errors, four RAM/stack patterns, repeated
open-close-open-close, mutations of second pin/IRQ/config/opened during lower
calls, rawr0, callee registers/SP, nonstack RAM and MMIO bytes are checked.
Native config pointers and all16 config bytes match. Trace
22ecbf380072e9b238742b93b0d47ff85c6bdec6a61eef4052cca51d2b16fd7b.
Only authenticated configuration code pointers are normalized.

The first focused graph dropped the two unreferenced template arrays after the
compiler folded their values into code. Its builder/report/failure log remain
underpre-template-root-fix with bound hashes. Explicit verification roots retain
the data for direct byte checks; product C did not change for that repair.
All ten hardware-TWI operation/IRQ imports now resolve to source across these
checkpoints. The main partial runtime closes four lifecycle imports without new
imports, leaving28. Full metadata ABI/scratch/APSR/private-frame histories,
physical initialization/power-cycle semantics/timing, SDK state/configuration
identity, arbitrary backing/retry behavior, existing health/NV failed-read
counterexamples and complete firmware/toolchain/placement/byte identity remain
open. No physical write, portable-policy/admission change or frozen corpus/
ownership edit occurred.


### Native DFU BLE observer/auth: SDK divergence retained

Native0x52154(128 code bytes) and0x7cdc8(100 code bytes) now compile as separate
native observer and authorization bodies. Three fresh REA Ghidra receipts bind
body/literal spans and the four-byte value seed0x9c65c. The pinned SDK context
type is statically checked at28 bytes with native field offsets; a source-owned
zero context at0x2002c110 lies inside the authenticated scatter zero interval.
The source-owned4-byte seed is len2/offset0. Existing actual glasses-handle getter
and an unchanged SDK ble_srv_is_indication_enabled selection are linked, with
all consumed SDK source/headers checked against the authenticated SDK ZIP.
SVC173/176 mnemonic bridges use official SDK enum numbers; no executable bytes
or default-filled private CCCD buffers are retained.

The frozen ownership ledger's SDK-family correlation is not sufficient to
substitute the complete stock ble_dfu.c observer. Native disconnect compares the
glasses-handle getter with stored DFU conn, clearing toffff only when different;
stock compares the disconnected event handle. Native authorization stores the
new event conn before any request checks; stock rejects a different existing
conn. Native HVC also stores event conn on matching value-handle before checking
waiting/preparation, unlike stock. These three superseding bounded correlations
are explicit innative-sdk-correlation.json; the frozen ledger/corpus is preserved.
Reuse is the SDK type/SVC constants and unchanged indication helper, while event
control flow is independently recovered native C. No new upstream ancestry is
inferred for the product differences.

NULL returns0. Connect stores/returns event conn. Unknown events return their
pointer; rejected authorization returns event+6, and all those rejected writes
still retain the native conn update. Valid write authorization tail-calls the
native-frame helper. It initializes a16-byte reply and8-byte value descriptor,
retains raw CCCD backing at frame+28, executes value-get then actual SDK bit test
only on success, and sets update/status0 or status01fd. Reply retries only full
status17, freshly loading conn each iteration. After any other reply return it
reads the current reply status, not the API result: status0 forwards the original
write pointer, any nonzero status is returned raw. Matching HVC reads the full
waiting byte, calls the real boot-preparation boundary, then invokes a freshly
loaded event callback with2 if preparation returns nonzero. No callback-NULL or
packet-backing guard was invented.

34560 comparisons passed(event16128/direct-auth18432), with18624 value-get,
37248 reply,756 prepare,6214 control-write,567 event callbacks,2016 actual glasses
getters and9312 actual indication-helper calls per side. Only SVC/backend/event
callbacks are fixtures. Cases include all256 CCCD bytes, zero/partial/full value
writes, busy retries/nonzero final API returns, raw retained buffer seeds,
mutated reply status/conn/callback, event/request/handle/opcode branches,
noncanonical waiting bytes2/255, four RAM/stack patterns, exact authorization
frame addresses/reply bytes, rawr0, callee registers/SP and nonstack RAM. Trace
 ea7f9ba4a3ee1783923fad44bc69b37cbd483ab4a1e23e182f67a6786f5691e4.
The first verifier resumed past emulated SVC with an even PC and lost Thumb
state; its native-PC7cdf2 invalid-instruction diagnostic, driver and log are
retained underpre-thumb-svc-resume-fix. Resuming with Thumb bit fixes the harness;
no C candidate was changed for this repair.

Main partial linkage closes ble_dfu_buttonless_on_ble_evt/context and exposes two
honest backend imports:r1_dfu_bootloader_prepare_boundary(native5207c) and
r1_dfu_control_point_write_boundary(native521d8). Total imports remain28.
Backend execution, complete service initialization/shared backend pointer/SVCI
state, all raw scratch/APSR/private frame histories, callback metadata ABI,
arbitrary backing, real GATTS/DFU hardware behavior, existing health/NV failed-read
counterexamples and whole-image configuration/toolchain/byte identity remain
open. Source compilation does not admit DFU/provisioning/device writes. No
physical write or portable-policy/runtime-admission change occurred.


### DFU backend, response and SoC-event source closure

Six bodies now compile: native52050 finalization,5207c preparation,521d8 control
write,522d8 response,8ed5c advertising-name glue and52278 SoC event. Eight fresh
REA Ghidra receipts authenticate code/literal spans and418 exact dual-log text
bytes. The frozen preparation row reports60 bytes because its20-byte local body
shares the40-byte finalizer closure; that ledger extent/label was not rewritten
or counted as sixty new local bytes. SDK SVC IDs/types for GPREGRET/HVX/power and
the28-byte advertisement structure are statically checked. New source data owns
only the4-byte backend pointer at20007934(cold zero),28-byte adv-name object at
2002c138(cold zero) and418 readonly log bytes. The canonical28-byte service
context remains its existing owner, distinct from the backend pointer target.

The existing SDK startup-owned12-byte nrf_dfu_set_adv_name_svci_async_def at
native2002c12c is reused. A copied parent object globalizes that unique symbol;
all allocated code/data section bytes/flags/sizes/alignments, all other nm entries
and the state symbol's value/size remain identical. Only local-to-global binding
changes. The original source object/report remains intact; no duplicate SVCI
state or executable blob is introduced. A header-typed view accesses command,
SoC handler and state+8. Main linkage closes both backend boundaries and the SoC
observer without new imports, leaving25. The historical boundary names now have
actual source bodies, not runtime fixtures.

Preparation calls the current backend context's event0 then finalizes. Finalize
executes SVC61(0,ffffffff), returns any failure, then SVC60(0,b1), returns any
failure, calls event1 through the canonical service context and invokes existing
power management with2, returning0. Backend callbacks and canonical callbacks
must not be merged. Control writes retain full-byte waiting flags, reset state,
response status17 mapping and fresh backend-pointer/callback/opcode reads.
Unknown opcodes respond2 and ultimately event2; advertising lengths0/>20 respond5;
valid names copy once, then reread length after memcpy. SVCI command success sets
waiting on the fresh backend pointer. Busy returns6; forbidden15 emits native
fresh-mode dual logs and retains raw15. SoC event requires both async pointers,
returns the input event if missing, preserves pending on handler8, otherwise
clears pending and uses success/error response paths with fresh callbacks.

The response preserves the native24-byte frame: length16=3, sixteen initialized
HVX parameter bytes and three data bytes20/opcode/response. The high halfword at
frame+2 and byte23 are deliberately untouched. Successful HVX with returned
length!=3 maps to12; other statuses remain fullword. C response kernels receive
explicit external frames so API buffer addresses match native across control,
SoC and direct-response calls. No zero fill masks caller history.

74160 cases passed: control30720/sys30720/response5040/prepare512/finalize512/
adv4608/composed-HVC2048. Actual six bodies, memcpy and the prior native HVC
observer execute; SVC/SVCI targets, event callbacks, shutdown/logging are explicit
fixtures. Observations per side:41935 HVX,2560 clear,640 set,1168 command,7680
handler,72660 callbacks,160 power,524 mode,130 ring,98 SDK log and48 actual copy
calls. Coverage includes all256 control opcodes, name limits and post-copy length
mutation, separate/retargeted backend/canonical contexts, pending/busy/missing
state, raw SVC errors/returned lengths, four RAM/stack patterns, exact API-visible
HVX pointers/fields/data, direct response's entire raw frame, rawr0, callee
registers/SP and nonstack RAM. Trace
cbecbfb051392a274a9884dd39f0644680a2156f175f4d4dabbd48177eb8360e.

**OPEN raw caller-history gate:**22 composed cases have different unused HVX
frame padding, despite identical declared API-visible payload/parameters and
nonstack RAM. raw-frame-history-probe.json preserves the first counterexample:
a one-byte name operation with failed command and seedaa leaves native byte23=00
and source byte23=aa. The three API payload bytes are20/02/04 in both. No padding
normalization or invented zero store was added. API/RAM verification is bounded
and does not close full private-frame/ABI/image identity. Real service/backend
initialization, SVCI/SoftDevice/DFU/power execution, arbitrary packet backing,
callback scratch/APSR/caller histories, original placement/toolchain and existing
health/NV failed-read counterexamples remain gates. No physical device write,
portable-policy/admission change, corpus/ledger rewrite or complete-image claim.

### Existing printf provider composition

`build_native_printf_runtime.py` selects the already compiled native printf/stdout
wrappers and native RTT write wrapper into the DFU backend partial runtime.
The selected object imports only the existing formatter core, SEGGER RTT Init,
WriteNoLock and shared control block; the parent resolves all four. The unchanged
upstream SEGGER RTT provider and source-owned initializer/state are reused once.
The main partial graph now has24 unresolved imports, closing printf without
new bodies or state. Existing formatter-stream and RTT leaf verification receipts
are hash-bound by the composition report and audit. No composed execution,
private-frame/interrupt/debugger equivalence, original placement/instruction
identity or complete firmware build is claimed. The retained-log sink is still
a separate unresolved provider; historical health/NV/DFU frame counterexamples
remain open. No firmware/device write was executed.

### Retained-log sink from authenticated native evidence

Native7f030 (146 bytes) now has a compiled C sink with an explicit32-byte
variadic entry frame. REA's Ghidra dossier is retained in
`native-retained-log-rea.json`; authenticated disassembly confirms the branch,
clear order, fresh context loads,16-bit cursor wrap, newline and RTT pointer
calculation. It shares the existing reset-trace context and introduces no
retained-state initialization beyond the native stores. Oversized formatter
returns can produce an output pointer before the text buffer; this behavior
is preserved without invented guards.

2016 native/source comparisons passed with explicit clear, crash-initializer,
formatter and RTT fixtures: NULL formats, flag0/1/255, seven cursor boundaries,
negative/zero/positive/wrapping formatter results, two RAM patterns and callback
mutations of context/cursor. Observed native calls:672 clears,336 initializers,
636 formatters and424 outputs. Rawr0, callee registers/SP, external32-byte frame,
varargs pointer, context and output RAM match. Trace
2a30ec25e111a39e79a50f3d0b2feaa351f9ad676a55b697831cdd2fba866de0.

The new main partial graph closes the retained sink and exposes the actual
`r1_health_crash_record_initializer` provider, leaving24 imports. Existing
formatter/RTT providers and reset context resolve its other dependencies.
The initializer is not stubbed. Product-specific sink logic has no identified
upstream replacement; existing attributed SEGGER RTT remains reused. Actual
composed formatter/RTT/crash execution, full private-frame/alias histories,
original toolchain/placement/instruction identity and complete firmware remain
open. No physical device write or admission-policy change occurred.

### Crash initializer and shared time-status accessor

Native5a2b8 (104 bytes) and8ad98 (6 bytes) compile from C in
`native_crash_initialize.c`. The initializer shares the existing reset context;
the status accessor reads byte11 of the existing time state. Its24-byte entry
frame preserves the savedr3 upper half while the lower half carries payload
length. The record pointer is captured before callbacks; fresh record timestamp
and offset feed snapshot construction, followed by CRC over964 bytes and a
16-bit checksum store. The native copy gate remains896 bytes.

1440 initializer and256 status native/source comparisons passed, with explicit
time, payload, memcpy, snapshot and CRC fixtures. Tests include NULL payloads,
length0/736/895/896/897/65535, four status values, signed offset extrema, two
RAM patterns, and five callback mutation modes. Actual initializer/status
bodies execute; rawr0, restoredr3, callee registers/SP, external24-byte frame,
record RAM and ordered API observations match.120 copy paths are exercised
by the896-byte fixture. Trace
c8984a76fc6f18766d736f343abae3469595fb687b82331006c533cf7c2c480b.

REA bytes for6abe4 confirm that the actual getter writes736 (0x2e0), then
returns2001e054. This differs from the initializer's896-byte gate. Neither
constant was changed to make the path reachable. The payload's complete state
ownership and producer lifecycle remain unresolved; no opaque payload data was
copied into source. Snapshot construction is also an explicit provider.
The new partial runtime closes the initializer, exposing these two imports,
for25 unresolved imports. It reuses existing time, memcpy and stock CRC source
providers; this receipt does not establish their composed execution. Full
private-frame/alias histories, original compiler/placement/image equality and
hardware behavior remain gates. No physical firmware write occurred.

### Crash snapshot across both native ranges

`native_crash_snapshot.c` covers native5a324..5a3cd and its shared tail
3f47c..3f52f (350 total bytes, confirmed by REA). The C preserves52-byte
clear, signed16 offset clamp to[-720,720], wrapping timestamp adjustment,
unsigned day/hour calculation, six activity bitfield packs, HR hourly query,
SpO2 and unaligned HRV fields. Native query output pointers remain entrySP-24
and entrySP-20, with only their declared4-byte and2-byte fields initialized.
No provider payload, opaque executable data or invented upstream attribution
was added. Product cache/query providers remain explicit boundaries.

23328 comparisons passed using actual snapshot body and explicit clear/cache/
query fixtures: all24 local-hour inputs plus timestamp extrema/day wrap, nine
offset boundaries, all16 provider-presence masks, two patterns and three
mutation/alias modes. Tests cover query mutations of record and later caches,
and activity cache aliased to output. Each side observes23328 clear/activity/
HR/SpO2/HRV calls and11304 queries. Rawr0, callee registers/SP, ordered calls,
declared query bytes and exact pointer coordinates, record and cache RAM match.
Trace c6cbed58aacbd0731e6e18b7817954c5faa54ea617649f78037aa9b49808853d.

**OPEN ABI/frame counterexample:** all23328 cases differ in restoredr2/r3
and/or external24-byte history. First case timestamp0/offset-32768/mask0/
mode0/seed0 returns native r2/r3=22222222/33333333 and source=ffff8000/abcdef01.
`raw-frame-probe.json` retains both raw frames, without normalization. This
receipt proves bounded output/state behavior, not full native ABI/history.
The earlier passing driver/receipt are retained in pre-raw-probe.

The new main partial graph closes snapshot construction and exposes five
actual health-provider imports, increasing the explicit total25->29. It
reuses existing memory clear. Provider/cache state ownership, full raw ABI,
actual health-provider composition, arbitrary pointer histories, original
toolchain/placement/instruction identity and full firmware remain gates.
Existing NV/health/DFU counterexamples are unchanged; no physical write occurred.

### Native hourly accumulator snapshot and composed crash query

`native_hourly_snapshot.c` implements native5ab6c (48 bytes), with six8-byte
source-zero records (hour8/pad8/count16/sum32) at canonical20016648. The48-byte
extent lies within the authenticated cold-zero range; no opaque initialized
provider data was copied. Both output pointers must be non-NULL before either
zero store; selectors above5 return after clearing outputs. Valid records
require nonzero count and exact full-width requested-hour match. The sum store
precedes a fresh count load, preserving output/record alias behavior. Native
rawr0 is retained for NULL/invalid/empty/mismatch/success paths. REA function
and exact52-byte code/literal receipts are retained.

13824 direct native/source cases pass without provider fixtures: all six valid
selectors plus6/ffffffff, hour0/1/23/255/256/ffffffff, four stored hours, three
counts, three sums and eight output/record alias modes. Rawr0, callee registers/
SP and exact record/output RAM match. Direct trace
5ca9bcdd659bdb73d0dd821af95d50a879d73b1135471088c5f1e2023de3a776.
A further23328 cases execute actual C snapshot and hourly query together, with
cache getters and memory clear fixtures.11304 actual queries use the native
output coordinates; outputs, rawr0, callee registers/SP, record and cache RAM
match. Graph trace4c3a33338966cf3ebbcca3198b9503a0d9a4778e46ac6374f06d44f5c0eb9716.

The graph raw probe retains23328 scratch/frame differences, including the
previous snapshot counterexample. Declared outputs are not full ABI proof.
The main partial runtime closes r1_hr_hour_query with no new imports, reducing
29->28. Source-zero accumulator ownership does not establish producer/service
initialization; those bodies, remaining cache providers, arbitrary stack aliases,
full private histories and original toolchain/instruction/image identity remain
gates. This product-specific body has no authenticated upstream replacement;
existing dependency attribution is unchanged. No physical write occurred.

### Four health-cache accessors and exact-range resets

`native_health_cache.c` compiles four native accessors (5a9f0/5ace0/5baec/
5af18) and four resets (48288/7062c/90dd4/706be). REA bytes authenticate
all eight. Native clear lengths are576/72/72/144; the reset stores offset16
at those boundaries and timestamp32 at580/80/80/156. Activity/HR/SpO2/HRV
cache extents are584/84/84/160 bytes. The existing offset and timestamp cells
are reused by `native_health_cache.ld`, consolidating payload, metadata and
reserved gaps into one contiguous cache each.888 new source-zero bytes plus
24 existing metadata bytes make912 total; there is no second metadata state.
All native extents lie in cold-zero RAM. Final whole-image scatter/placement
is still a separate gate; relocatable sections include existing zero-valued
PROGBITS metadata and are not a proven final BSS image layout.

960 paired sequences execute actual eight C bodies and existing memory-clear
source, with no provider fixtures.480 sequences first reset all four caches;
2880 actual clears execute per side. Timestamp/offset extrema, truncation,
four patterns, repeated resets, getter addresses, rawr0, callee registers/SP,
full surrounding cache RAM and reserved/neighbor preservation match native.
Trace c74beaba0c5aba473ee1435a826fa79eb53e0f8134c7605c339c830ac68953f8.

The first composed test exposed a raw-return mismatch: native byte-clear
postincrementsr0 to base+length; existing C memory-clear returns base. The reset
bodies expose that native raw word despite void-style public semantics. The
failed source/object/graph/reports/driver/log remain in pre-clear-return-fix.
C resets now explicitly return base+length after actual source clearing and
the two metadata stores. No shared memory provider behavior was changed.

The main partial graph closes four cache imports with no new imports,28->24.
Source-owned cache state/reset bodies do not prove health producer/service
initialization, full private/alias histories or original toolchain/instruction/
image identity. Snapshot raw ABI/frame counterexamples remain unchanged. These
product cache bodies have no authenticated upstream replacement; no vendor
payload or firmware bytes were embedded as source. No physical write occurred.

### Crash payload getter and native-stack initializer composition

`native_crash_payload.c` implements6abe4: NULL length returns0; otherwise
write736 (16 bits), then return the source-owned736-byte extent at native
2001e054. The extent is within authenticated cold-zero RAM; no opaque payload
was copied. Producer lifecycle remains unresolved. The initializer's distinct
896-byte copy admission remains unchanged. The partial graph closes this
getter with no new imports,24->23.

**Composed call-frame repair:** the first actual initializer/snapshot/query
run returned identical record/checksum but different query pointers. Native
query outputs were2003cfd0/2003cfd4; the old single C kernel placed them16 bytes
lower,2003cfc0/2003cfc4. Exact failed driver, graphs, reports, builder and log
are preserved in pre-snapshot-frame-fix. The new C/ABI bridge completes all
preparation frames before calling snapshot construction at nativeSP. It then
calls actual CRC and stores the checksum while preserving the native24-byte
initializer frame and restoredr3 length word. The parent is cloned with only
the earlier initializer symbol weakened; all allocated bytes/sections and
all other symbol bindings match. Original source/objects and earlier receipts
remain untouched. The new strong bridge resolves all calls in the new graph.

2160 composed native/source initializer cases and24 direct getter cases pass.
Actual initializer, time offset/status getters, timestamp dispatcher, payload
getter, snapshot, four cache getters, hourly query, clear and stock CRC execute;
only the timestamp backend callback is a fixture. Tests cover timezone extrema/
clamp boundaries, wrapping timestamps, all status-byte low-bit modes, three RAM
patterns, callback mutations of context/time/record/caches, and getter NULL/
unaligned/payload/stack destinations. Observations:2160 timestamp callbacks,
2184 getter entries,2160 snapshots,1440 actual hourly queries,2160 CRC calls,
zero payload copies. Rawr0/restoredr3, callee registers/SP, exact API pointers
and record/cache/payload RAM match. Trace
adb73ee0f376bd0bc3b3cb12017998e6c0d86a6395b1a51e924301ec39279c8d.

The repaired bridge separately passes the earlier1440 fixture cases plus256
status values, including120 synthetic896-byte copy paths. Those fixtures are
not evidence that the actual736-byte getter admits a copy. Earlier snapshot
scratch-register/private-frame counterexamples, arbitrary alias histories,
producer/service/clock hardware initialization, original compiler/placement/
instruction and whole-image equality remain open. Product payload/getter logic
has no authenticated upstream replacement; existing memory/checksum source
providers are reused. No physical write occurred.

### Native stream bootstrap using existing list and CMSIS providers

`native_stream_bootstrap.c` implements native8a55c initializer,8a310 timer
front creation,8a3f0 enable,8a540 wake,8a1d0 tick selection and supplemental
8a558 keepalive. The initializer invokes existing source list initialize and
prepends a1000-tick timer, preserving the native outer frame/tail-call boundary.
Enable stores only the low byte but branches on the full input word;0x100
therefore clears enabled while still waking. Wake clears next_wakeup before
fresh callback/context reads and returns the native raw word. Tick selection
uses the configured raw callback or existing CMSIS osKernelGetTickCount.
Timer creation preserves pre-allocation arguments, fresh flag reads around
tick callbacks, context/timestamp store order, created-byte store and wake.
Allocation failure masks BASEPRI to64 and attempts a zero word store at
ffffffff before the fail-stop loop, rather than returning a fabricated error.

Existing list providers and attributed CMSIS/FreeRTOS source are reused; no
duplicate list/clock implementations were introduced. The52 new source-zero
bytes own housekeeping48 at2001a2bc and only the tick callback cell4 at
2001a2b4. Surrounding registration fields remain separate evidence gates.
The earlier high-level sensor-stream reconstruction remains useful behavior
evidence but its explicit framework/context and callback ABI are not silently
substituted for these native public entries. No attributable upstream body
for the product-specific stream framework was established.

2880 comparisons passed,480 per entry, executing actual six bodies, existing
list providers and CMSIS dispatch; allocation, clock leaves and wake callbacks
are explicit fixtures. Coverage includes raw enable values0/1/255/256/ffffffff,
configured/default tick paths, present/absent wake, failed/successful allocation,
empty/existing lists, two RAM patterns and three callback mutation modes.
Observations per side:960 allocations,960 tick leaves and832 wakes.480 fatal
cases match invalid store address/size/value and BASEPRI. On normal returns,
rawr0, callee registers/SP, housekeeping/list RAM and ordered API observations
match. Keepalive's2-byte body equals native within the verification placement.
Trace12cacf2e50662b9a2cf75fd6c8adadaed903caf550ad555cf7c817f31e4b7cd8.

The partial graph closes r1_native_stream_initialize with no new imports,
23->22. Polling, stream/sensor registration and provider bodies, real allocator/
clock/scheduler/wake execution, full private scratch/frame history, original
toolchain/placement/instruction and complete image identity remain gates.
REA's headless Ghidra bytes authenticate the native spans; Ghidra-MCP reports
no running GUI instance. No physical device write occurred.

### Native timer polling, expiry, release and shared-list removal

`native_stream_poll.c` compiles native8a45c poll,8a404 expiry,8a5e4 remaining,
8a584 stop,8a3c0 release and8a1c4 elapsed, with the5d998 unlink body. It
reuses the existing source-owned housekeeping, tick selector, list helpers
and FreeRTOS heap provider. No new state or replacement upstream library is
introduced. Product-specific timer dispatch remains reconstructed native C.

The poller preserves nonzero reentry guard, disabled exit, zero-tick counter
wrapping, pre-dispatch next-node snapshot, traversal restart only after a fired
callback plus fresh created/released byte, stopped-node filtering, unsigned
minimum and wrapping drift arithmetic. Expiry uses signed-positive repeat
decrement and saved pre-callback repeat for dispatch; fresh released/count/
flags choose stop versus unlink/free. Stop/release NULL paths preserve the
BASEPRI64/invalid-word-store fatal behavior. Freed nodes may be overwritten
by the free fixture; the graph matches without reading them afterward.

**Native correlation correction:** disassembly compares drift span with500
and branches below it, so correction runs at span>=500. The older high-level
`reconstructed/sensor_stream/sensor_stream.c` candidate uses span>500. This
receipt supersedes that boundary for native polling; it does not certify the
earlier entire high-level family or change the frozen pseudocode/ledger.

23328 paired comparisons pass:10368 polls and2592 each expiry/remaining/stop/
release/elapsed. Actual C dispatch, shared lists, unlink and tick selection
execute; only clock callback, timer callback and free are fixtures. Cases
include NULL/one/three-node lists,0/499/500/ffffffff ticks, zero/advancing
clocks, periods0/5/ffffffff, repeats0/1/ffffffff, four flag combinations,
normal/disabled/reentrant states, two RAM patterns, and three callback mutation
modes. Tests exercise actual release/free list updates and created-byte
restarts with stop mutation, without normalizing API pointers or RAM. Native
observations:19008 ticks,1216 timer callbacks,2520 frees.3456 faults match
address/size/value and BASEPRI; normal rawr0, callee registers/SP, housekeeping/
list RAM and ordered observations match. Trace
04861be03a49e214c3136b43cfa982dd35d4fbc1104d7115176838bb48e3ff9d.

Six frozen ownership entries become bounded tested candidates. The unlink
body is exercised transitively for state; its unused raw return/scratch ABI
is not promoted as a separate tested row. The main partial graph closes poll
with no new imports,22->21. Actual clock/allocator/scheduler execution, arbitrary
callback/cyclic-list histories, full private-frame/raw ABI, original toolchain/
placement/instruction and whole-image equality remain open. No hardware write
occurred; existing NV/health/DFU/snapshot counterexamples remain explicit.

### Native stream object construction, registry insertion/lookup and flag setter

`native_stream_objects.c` compiles native896f0 constructor,89d9c insertion,
89d54 lookup and8a5c0 flag setter. The constructor validates full-width nonzero
sample size but stores only16 bits. It truncates strlen to8 bits before clamping
the name copy to8 bytes (length256 copies0,257 copies1), zeroes56 object bytes,
initializes its24-byte-payload listener descriptor, and leaves context0 zero.
It returns the object even if registry-node allocation fails; no invented
rollback/free is added. Insertion initializes the shared12-byte registry at
2001a1b0 only when stride0, preserves the unused node word, and appends the
object pointer. Lookup uses actual strcmp over registry objects and rereads
the object field for return. Flag setting preserves other byte40 bits and
returns native pointer+40. NULL constructor arguments follow the native
BASEPRI64/invalid-store fatal behavior. Failure logging preserves separate
fresh mode reads and both native ring and SDK marker/text contracts.

40960 paired comparisons pass,10240 per entry. Actual C bodies, memory clear/
copy, strlen/strcmp and shared lists execute; allocation and mode/logging are
explicit fixtures. Cases include name lengths0/1/7/8/9/255/256/257/511/512,
full-width sample-size edges including10000->stored0, all two-allocation outcome
masks, initialized/uninitialized registry, empty/two-node lists, all8 log modes
and mutating mode reads, two RAM patterns, NULL guards and create-then-lookup
workflows. Observations:19312 allocations,24464 mode reads,7080 ring logs,
4504 SDK logs.4192 fatal faults match address/size/value/BASEPRI; normal rawr0,
callee registers/SP, full registry/object RAM and ordered observations match.
Trace a73b8b8faf140ec1cbf0c681d1ce86e3a427eb086b5e9cac9f7505a8fd13436f.

The registry adds12 source-zero bytes in authenticated cold-zero RAM. This
core prepares the remaining singleton and registration providers; it does not
close their imports yet, so the main partial graph remains21 imports. The
selected object graph still reaches existing unresolved logging/error consumers;
the verifier overrides only explicit allocator/logging ports and garbage-collects
unused consumers. No such fixture replacements enter the main graph. Product
framework logic has no authenticated upstream replacement; existing source
memory/string/list and attributed heap/logging providers are reused. Real heap/
logging/sensor execution, arbitrary aliases/private histories, full raw ABI,
original compiler/placement/instruction and whole-image identity remain gates.
No physical write occurred.

### Native accelerometer/temperature factories and provider tables

`native_stream_singletons.c` implements native89d88 and8a1ac factories,
918fc temperature open,918f8 close and91900 read. The factories call the
actual shared constructor with acc/188/acc_ops/0 and temp/2/temp_ops/0. They
allocate on every call; no unproven singleton caching is invented. Two typed
12-byte source-owned vtables correspond to9a590 and9a5a8. Motion entries remain
real external source providers for native6f400/6f300/6f4a0. Temperature open/
close return1; read requires non-NULL destination and exact full-width length2,
then calls the real calibrated-temperature provider boundary50e4c, writes the
low16 sample bits and returns2. No sample value or hardware action is invented.

1932 native/source cases pass:384 acc,384 temp,384 paired factory/lookup
workflows,30 each open/close and720 reads. Actual factories, object core,
memory, strings and list providers execute; allocation/logging and calibrated
temperature are explicit fixtures. Three motion provider addresses are bound
only as table contracts and are never executed in candidate tests. Coverage
includes six allocation masks, existing/empty registry, all8 log modes with
fresh-read mutation, two patterns, repeated factories and lookups, NULL and
unaligned read destinations, exact/wrong/full-width lengths, sample extremes
and sample-provider RAM mutations. Observations:2688 allocations,2192 mode
reads,696 ring logs,448 SDK logs and90 calibrated reads. Rawr0, callee registers/
SP, registry/object/read RAM and ordered observations match. Both typed tables
match all native pointer bytes in the explicit verification placement. The
4-byte open/close code sections match native locally; final image placement
and complete instruction identity remain unproven. Trace
8e53763ac48c761e96b92b4f9b7fa97368cd9b2b4c587e2c72ea80b85af198d0.

Two frozen ownership rows become bounded tested candidates; the three
additional temperature entries are supplemental, with no frozen-row inflation.
The main partial graph closes two factory imports and exposes four real
hardware-provider imports,21->23. Typed provider tables contain source symbol
references, not retained executable blobs or fabricated stub bodies. Existing
ST/Bosch/Goodix or temperature dependency attribution must be resolved by their
actual providers; factory/table correlation does not admit those implementations
or prove hardware behavior. Source/private alias histories, full ABI, real
heap/logging/sensor execution, original compiler/placement/image identity and
existing NV/health/DFU/snapshot gates remain open. No physical write occurred.

### Native motion selection dispatch and calibrated batch adapter

`native_motion_stream.c` implements selected-provider init50270, IRQ50294,
FIFO502ac, initialize wrapper6f400, close6f300, calibration bypass72b90,
calibration reader7b9c8 and batch producer6f4a0. Only the selected-pointer
cell200076ac and bypass byte20006c35 are added; both zero cold values are
bound to the authenticated initialized-data image. Surrounding records remain
separate owners. Initialize probes only when the pointer is absent, rereads it,
and tail-dispatches the open callback or returns0. IRQ and FIFO preserve native
raw tail-call arguments and NULL results (0/ffffffff). Probe is a real unresolved
provider, not a fabricated successful selector.

The batch adapter validates destination/exact full-width188 length, requests30
samples, rejects signed-negative results, then truncates nonnegative counts to
16 bits without a clamp. It reads three offsets from native KV record bytes
68..73 through the existing shared serial handle and124-byte API, retaining
failed/partial-read scratch contents. Its128-byte reader frame and8-byte
producer calibration slot retain native API pointer coordinates. Three ffff
offsets become zero only when all three match. Every sample freshly reads
the bypass byte and each component offset in native order, wraps additions
to16 bits, then stores count at180 and timestamp at184. The outer24-byte
producer frame restoresr2/r3 from the actual calibration slot.

6425 paired comparisons pass:768 each selected init/wrapper/IRQ/FIFO,5 close,
256 bypass-byte values,180 calibration reads and2912 batches. Actual eight
entries, calibration/sample kernels and existing tick selector execute; selected
sensor callbacks, probe, NV read and clock are explicit fixtures. Coverage
includes missing/alternate tables and callbacks, probe rebinding, raw callback
registers, NULL/unaligned destinations and full length checks, negative/count
truncation boundaries, counts31/32, all-zero/erased/mixed offsets, bypass0/255/
alternation and per-sample offset mutation, full/partial/failed NV reads, handle
mutation, two stack/RAM patterns and post-count clock mutation.32-sample returns
exercise calibration writes beyond nominal188 bytes within explicitly backed
RAM; no invented count30 clamp or buffer validation hides them.
Observations:512 probes,640 opens,256 IRQs,3137 FIFOs,2581 NV reads,30270 policy
reads and2401 ticks. Rawr0, batch restoredr2/r3, callee registers/SP, exact NV
scratch/offset pointers, sample/metadata/cell RAM and ordered observations
match. Trace ef7aef8e535acbf11469c5c1be3055a35fa71e43efd74c736581e58b5de89a70.

The initial candidate inlined the policy getter, so its source-side mutation
hook was absent. pre-policy-call-boundary preserves source/objects/reports/
driver/log and structured counterexample: native/source outputs match for the
first constant-zero case, but native has one policy entry and source none.
The getter is now explicitly noinline, preserving the native call boundary
for actual per-sample mutation checks. No RAM/trace normalization was used.

Six frozen rows become bounded tested candidates; close/bypass are supplemental.
Four main imports close and one probe provider is exposed,23->20. These are
owner-authorized motion/data adapters; they do not replace or admit licensed
ST/Bosch/QMA/algorithm provider bodies. Actual sensor/probe/NV/clock execution,
failed-read cross-call/private histories, arbitrary backing/counts/aliases, full
raw ABI and original compiler/placement/instruction/whole-image identity remain
gates. Existing NV/health/DFU/snapshot counterexamples are unchanged. No physical
write or provisioning-policy change occurred.

### Native motion selection, locked wrappers and three provider tables

`native_motion_selection.c` compiles selector50208, refresh5025c, acquire5017c/
release50170, and nine LIS2DW12/BMA456W/QMA wrappers at6f380/6f394/6f3b2,
6f1a8/6f1bc/6f1da and6f404/6f418/6f436. It reuses the existing selected-pointer
cell and motion bus handle. Three source-owned6-slot operation tables (72 bytes)
match native9a718/9a730/9a748. Tables hold source function references, not opaque
executable bytes. Two LIS auxiliary entries are pointer contracts only; their
call ABI remains unresolved and they are never invoked by these tests.

Selection acquires the current bus, probes LIS first (full-word0x44), then BMA
(0x16), then QMA(0x90), stores the chosen table orNULL before rereading the bus
for release, and returns the captured matching ID or0. Low-byte-only matches
are rejected; QMA0xfa/0x9f are not silently normalized to0x90. Refresh dispatches
the selected probe slot when present, otherwise reruns selection. Probe wrappers
preserve raw IDs across release; config wrappers pass25 and return the full
result's nonzero predicate; QMA IRQ returns the release result, while LIS/BMA
IRQs are native no-ops. ABI-only wrapper bridges retain native saved-ID and
tail-release sequencing around independently compiled registry dispatch.

27650 comparisons pass, including8640 each select/refresh/composed initialize,
90 per lock/probe/config/QMA-IRQ wrapper,10 per IRQ no-op and450 each composed
IRQ/FIFO. Actual thirteen bodies plus shared registry and selected dispatch
execute; only bus operations and sensor leaf providers are explicit fixtures.
Coverage includes all three priority paths and no match, full-width IDs,
missing/already-selected/empty tables, NULL device/missing/present callbacks,
raw result extrema, probe/config rebinding of the bus and release mutation
of selection, and two RAM patterns. Rawr0, callee registers/SP, selected/bus/
record RAM and ordered observations match. The72 table bytes match native
in the explicit verification layout, and the2-byte no-op sections match locally.
Trace3e755ba52288ed2c552f2221070a9805b6809988b200b79204f7811da5b44513.

The main graph closes selection and exposes12 actual provider leaves,20->31.
These leaves are three ID/configure/FIFO families, QMA IRQ and two LIS auxiliary
functions. Repository correlation confirms the owner-authorized QMA reduction
already exists; it is not a new external licensing blocker. Its documented
hardening, and the portable motion layer's over-report rejection, must not be
substituted silently for native behavior. ST/Bosch pinned upstream sources and
QMA reconstructed sources remain usable evidence/dependencies after native
ABI/configuration correlation. No new vendor source was downloaded or admitted.
Real sensor/bus execution, full private scratch/frame/ABI histories, native
provider adaptation, original compiler/placement/instruction and whole-image
identity remain open. Existing NV/health/DFU/snapshot gates are unchanged.
No physical write occurred.

### Three native FIFO normalization adapters

`native_motion_fifo.c` implements native6f1dc BMA456W,6f3b4 LIS2DW12 and
6f448 QMA normalization. Each snapshots destination/request, acquires the
current bus, invokes the real raw-FIFO provider boundary, releases the fresh
bus, then normalizes every signed-positive reported sample and returns the
unchanged raw count. It introduces no sample31 clamp, over-report rejection,
NULL guard or substituted error. Signed16 arithmetic right shift by2 is
expressed with defined unsigned operations, preserving negative rounding.
QMA reads all XYZ halves before stores; ST/BMA read/store one axis at a time.
The code owns no new state and reuses shared bus wrappers and registry dispatch.

19104 comparisons pass,6368 per provider.6144 packed exhaustive blocks cover
all65536 signed16 values on each axis for each family against both native
execution and an independent mathematical floor-division oracle. The remaining
cases cover signed return extremes, zero/positive counts through127, requested
counts0/1/30/31/ffffffff, over-reporting, NULL/unaligned/end-of-mapped-RAM
destinations, NULL/missing/present bus callbacks, provider bus rebinding and
release-time sample mutation, with two RAM patterns. Mixed-axis vectors detect
axis swaps that same-axis exhaustive vectors alone would miss.

Actual normalizers, bus wrappers and registry dispatch execute; raw FIFO and
bus operations are explicit fixtures. Observations:10464 acquire callbacks,
10464 release callbacks,19104 raw reads.4860 faults match address/size/value
and RAM.2430 partial-triple cases show ST/BMA storing normalized X before
faulting on Y, while QMA leaves X unmodified because it preloads the triple.
On normal returns rawr0, callee registers/SP and buffer/bus RAM match. These
are mapped-memory emulator observations, not hardware fault/recovery proof.
Trace76fc53281b5e02fe13009d4c409136753abf489d23e38c91d1dc3338b8effdf1.

Three imports close and three actual raw FIFO imports are exposed, leaving31.
The portable motion layer's documented over-report rejection is retained as a
separate hardened product path; it is not promoted to native ABI equivalence
or silently changed by this reduction. Existing pinned ST/Bosch sources and
owner-authorized QMA reduction remain dependencies/evidence for raw providers.
The ST FIFO-level function inspected in the pinned source writes its masked
register byte even on read failure, matching the observed native control flow;
private scratch coordinates and context/read-wrapper differences still require
correlation before source reuse is admitted as native behavior. Real FIFO/bus
execution, unbounded provider counts/backing/aliases, full private frame/raw ABI
and original compiler/placement/instruction/whole-image identity remain open.
No physical device write occurred.

### Native LIS FIFO with attributed ST kernel

`native_lis_fifo.c` closes the raw LIS FIFO provider and supplies native register
proxy, burst and FIFO-level entry contracts. The level algorithm comes from
ST's BSD-3-Clause lis2dw12-pid commit
`8d4bd522015004a9646102702901ba5a15ec6d39`; its exact source slice and full license
are retained. Three explicit adaptations place the register temporary in the
native saved-r3 slot. This is attributed upstream reuse, with future upstream
changes requiring renewed correlation; the original vendor checkout is unproven.
The native proxy deliberately preserves its unguarded callback contract, while
the modern upstream wrapper has a NULL guard.

12652 native/source comparisons pass, including1254 matching faults. Actual
proxy, burst, attributed level kernel, raw FIFO, normalizer and bus dispatch
execute; register and bus callbacks are fixtures. Tests cover every register
byte, failed/unwritten reads, raw status propagation, saved r3, exact scratch
pointers, context rebinding, NULL/unaligned pointers and count wrapping. The raw
FIFO still performs a zero-length burst when a nonzero level is clamped by a
zero request, and ignores transport status as observed. Trace
`c24624b34d55085ea5250d1e58e61071ea228d9b081c89aca80c264a864c22ae`.

The main partial link now has30 unresolved imports. Only the observed16-byte
context prefix at2001e4d8 is source-owned and zero-initialized; the full SDK
context size and native initialization remain gates. Exact API scratch pointers
do not establish full callback stack/private history. Real sensor/bus execution,
full raw ABI, instruction identity, original compiler/placement and complete
byte-identical firmware remain unproven. Existing NV/health/DFU/snapshot gates
remain open. No physical write occurred.

### LIS identity and default bus request providers

`native_lis_identity.c` supplies native754dc identity,7517c device-ID read,
50188/501c8 motion bus request builders and supplemental7f17c/7f188 default
callbacks. Identity fills only missing read/write callbacks, clears only its
saved-r3 low byte, ignores read status and returns the resulting byte. Defaults
use address0x18 and return zero regardless of bus status. Read requests store
payload/length at12/16; write requests at4/8. Both fully clear20 bytes, truncate
address/register/length to8/16/16 bits and pass their native SP-40 record pointer
to existing actual registry dispatch. The direct request result is the boolean
inverse of the raw dispatch status. No new context or bus singleton is created.

2592 native/source comparisons pass,432 per entry. Actual identity, device-ID,
defaults, requests, memory clear, read proxy and registry dispatch execute;
only bus operations and explicitly selected custom register callbacks are
fixtures. Cases cover absent/present independent context callbacks, absent bus,
missing operation slots, success/error statuses, unwritten/read-byte values and
two incoming saved-r3 histories. Request pointers and all20 record bytes, rawr0,
callee registers/SP, context and data RAM match; relocated callback identities
are compared symbolically. Trace
`4cb5489e5433a99974ede3eb56bc0dc66918077e7541ab6b790ca24d899d261b`.
REA authenticated body/byte receipts and headless Ghidra analysis are retained;
Ghidra-MCP discovery returned no running GUI instance. Main imports fall30 to29,
with zero unresolved symbols in the selected identity graph. The prior receipt
before frontier report schema enrichment remains under`pre-frontier-schema`.

The configured transport and reset/ODR/interrupt bodies still require reduction.
This proves neither live sensor execution nor full callback/private stack
histories, arbitrary alias behavior, full raw ABI, original compiler/placement
or whole-image byte identity. Existing unresolved gates remain in force. No
physical device write occurred.

### Attributed LIS single-register configuration bodies

`native-lis-registers` compiles17 ST BSD-3-Clause bodies from pinned
lis2dw12-pid commit`8d4bd522015004a9646102702901ba5a15ec6d39` plus the native
unguarded write proxy759e6. Source slices and the full license are retained.
Three explicit adaptations rename each internal kernel, externalize its local
register byte to the native16-byte saved-r3 frame, and redirect its pointer and
member accesses. ST bitfield/status algorithms remain intact. Entries cover
BDU750b8, FIFO mode753c6/watermark753f4, bandwidth75422, scale754ac,
reset set757ec/get757d2, tap X7581a/Y75848/Z75876, duration758a4, mode758d2,
quiet75900, shock7592e and thresholds X7595c/Y7598a/Z759b8.

55767 native/source comparisons pass:3276 per body and75 write-proxy cases.
Actual attributed kernels and native read/write proxies execute; transport
callbacks are fixtures. All256 parameter bytes and256 old-register bytes are
covered with adversarial companion values, plus failures/unwritten reads,
write failures, incoming saved-r3 histories, full-word scratch writes and
read-time rebinding of the following write callback/handle. Rawr0, savedr3,
callee registers/SP, exact callback data pointer/length, payload, context and
data RAM match. Observations:55692 reads,42123 writes. Trace
`8eaf8ead8309d76e4348105b2b5587c298a34f63d43ca84b8ea3e122e6313763`.

Comparisons rejected two initial upstream assignments, retained with source,
objects, reports, drivers and concrete failures. At750b8 old55/val0 native
writes55 while auto-increment writes51: native is BDU bit3, not increment bit2.
At7581a oldaa/val0 native writes2a while tap Z writes8a: native is X bit7;
75876 is Z bit5. These are attribution corrections, not altered native behavior.
The selected register graph has zero imports; the main partial stays at29
because these bodies prepare the still-unresolved configuration provider.

REA byte receipts and reset dossier authenticate native contracts. Further REA
inspection identifies multi-register ODR/filter/power bodies and a native7518a
operation on register17 bit6; pinned ST CTRL_REG7 is3f, so treating that operation
as the modern data-ready-mode body would be unsupported. Configuration remains
open. Full callback/private stack histories, arbitrary aliases/faults, full raw
ABI, live sensor/bus, original compiler/placement, instruction and whole-image
identity are unproven. Original vendor checkout is unproven. No physical write
occurred; prior unresolved evidence gates remain in force.

### LIS multi-register setup contracts

`native-lis-setup` compiles75120 data-rate and75450 filter-path bodies using
attributed BSD-3-Clause ST source from commit
`8d4bd522015004a9646102702901ba5a15ec6d39`. Two local register bytes are
externalized at native24-byte frame offsets0/4, and their exact upstream slices,
full license and three explicit adaptations are recorded. Native ODR/filter
status gates remain the same: each failed read/write suppresses later calls.

Two additional bodies are reconstructed from native evidence.7575a power setup
maps input bits0/1/2 to CTRL1 bits3/1/2 and input bit3 to CTRL6 bit2; the modern
ST enum uses a different encoding. After successful first read/write, native
always performs the second write even when its preceding read fails, then
returns the wrapping sum of second-read/write statuses. Substituting the modern
ST body would change both encoding and error behavior.7518a reads register17,
sets bit6 and writes only on read success; its semantic name remains unproven,
so it is named`r1_lis_reg17_bit6_enable` rather than given a guessed SDK meaning.

26000 native/source comparisons pass,6500 per entry. Tests cover all256 input
and register bytes with adversarial companions, all81 combinations of four
success/error statuses, unwritten reads, two incoming saved-register histories,
full-word scratch overwrites and callback/handle rebinding between reads/writes.
Actual four bodies and read/write proxies execute; only transport callbacks
are fixtures. Rawr0, restoredr2/r3 for24-byte entries (r3 for16-byte entry), callee
registers/SP, API scratch pointers/lengths, payload, context and data RAM match.
Observations:37724 reads and29516 writes. Trace
`d53fcefa6458c4852fe50e6ddf2433511f10c0749ea7f8564ab1fbbb62d850ec`.

REA byte receipts bind all four native entries. The selected graph has zero
imports; main imports remain29 while top-level configuration and interrupt
routing remain open. Original vendor checkout, full callback/private stack
histories, arbitrary aliases/faults, full raw ABI, actual sensor/bus execution,
original compiler/placement, instruction and whole-image identity remain
unproven. Prior unresolved evidence gates are retained. No physical write
occurred.

### LIS top-level configuration candidate and composed-frame gate

`native_lis_configure.c` compiles the318-byte native75510 provider contract
with a64-byte outer frame and104 exact diagnostic-text bytes. It overwrites
both context callbacks with native defaults, checks ID44, issues reset, polls
with delay2 and rejects the12th poll even if its bit just cleared, applies the
actual setup sequence, selects ODR3/4/5/6 for default/50/100/(150 or200), delays100
and drains up to five FIFO samples. Signed rate comparisons, fresh logging-mode
checks, marker1c0001 and the original ignored-status behavior are retained.
REA authenticates444 bytes covering body/literals/text. The candidate closes
configuration at link time, producing28 main imports; this is a compiled
candidate, not a replacement for the latest verified29-import parent.

Composed execution found a concrete discrepancy. For rate0, ID44, successful
transport and immediately clear reset, the first ID request matches. The next
reset-set read passes bus request2003cf80 natively versus2003cf70 in source.
Both request records contain identical20 bytes and point to register scratch
2003cfb0; return1, context, outer40 local bytes, register model and poll count
also match this case. C kernel private frames move lower bus request records,
so earlier isolated register API-scratch proofs do not establish full transport
composition. No pointer is normalized and no source/runtime claim is promoted.
The failing case, complete traces, source/objects/reports/driver/log are retained
under`pre-call-boundary-fix` with`composed-frame-probe.json`.

Configuration remains an explicit evidence gate until native call boundaries
are resolved, likely by returning from pure bit-update kernels before invoking
transport at the native caller SP. Register masks and SDK status behavior need
no invented changes. Logging, delay and bus operations are test fixtures. Full
private histories/raw ABI, actual sensors, original compiler/placement and
whole-image identity remain unproven. This is internal implementation work,
not an external blocker. No physical device write occurred.

### LIS configuration composed call-frame repair

`native-lis-call-frames` supersedes the composed transport mismatch retained in
`native-lis-configure/composed-frame-probe.json`.22 native frame bridges call
transport at the original caller SP.20 exact ST assignments from the pinned
BSD-3-Clause source are factored into pure C byte updates, with source slices,
assignments and full license retained; helpers return before transport runs.
Native power encoding/error addition and register17 behavior remain explicit
reconstructed bodies. No request pointer is normalized. The parent object is
cloned with only22 named function bindings weakened; all allocated sections
and every other symbol/address/binding are checked unchanged. New strong
bridges replace those entries without changing the historical tested sources.

51840 composed comparisons pass:46080 ID failures,1152 reset timeouts and4608
configured outcomes. The actual configuration provider, register bridges/pure
helpers, FIFO, default transports, memory clear and registry execute. Bus,
custom read, delay and logging callbacks are fixtures. Tests span signed rate
edges, ID failure/success, reset counts0/1/10/11/12, fresh logging modes including
changing modes, missing bus/slots, unwritten/error transports, context rebinding,
FIFO levels and two RAM patterns. API bus-record pointers, exact20-byte records,
register-data pointers/payloads, rawr0, callee registers/SP, context, outer40
local bytes, register model and poll counts match. Observations:65664 reads,
23616 writes,37440 custom reads,29376 delays,125952 mode queries,31488 ring and
23616 SDK log calls. Trace
`2c806975de2871743390be1f09e04d1d604e774ac99f92c0760144eb62297e1d`.

Direct regression against the replacement runtime also passes55767 register,
26000 setup and12652 FIFO comparisons, retaining their previous trace hashes.
Total146259 comparisons. Configuration is now admitted to the tested frontier;
main imports fall29 to28. The unfixed candidate, failing case, source/object
snapshot and receipts remain immutable.104 diagnostic bytes are source-owned
and byte-checked. The selected unmodified logging graph still exposes provider
imports; a fixture-linked emulator test does not establish that graph's full
runtime behavior or a zero-import whole image.

Full callback/private stack history, arbitrary faults/aliases, full raw ABI,
real sensors/bus/delay/logging, original vendor checkout, compiler/placement,
instruction and whole-image identity remain unproven. LIS auxiliary interrupt
routing, other providers and prior NV/health/DFU/snapshot gates remain open.
No physical device write occurred.

### Native LIS tap auxiliaries and interrupt routing

`native-lis-aux` compiles751b8 disable,75290 enable and756cc/756da INT1 route
get/set. The setter reads CTRL5 then CTRL_REG7, derives interrupt-enable from
fresh CTRL4/CTRL5 fields, writes CTRL4 and conditionally CTRL_REG7, preserving
all status gates,24-byte native frame and restoredr2/r3. Its pure C condition
and assignments are factored from the exact BSD-3-Clause ST route-set slice at
pin`8d4bd522015004a9646102702901ba5a15ec6d39`; full license is retained. The getter
has its native8-byte frame. All transport calls occur after the pure helper
returns, preserving native bus-request and register-data pointers.

Enable sets all three tap axes, thresholds3, duration/quiet/shock0, tap mode1,
then route bit3. Disable clears route bit3 and all axes/mode, sets full scale2
and ODR3. Both preserve their8-byte outer frame, ignore provider status, perform
fresh logging-mode checks and return1.164 exact source-owned diagnostic bytes
and marker1c0003 are authenticated. The enable diagnostic says400Hz/2g, but the
native enable body does not set ODR/full scale; no such behavior is invented.
REA has no analyzed function at75290. Its frozen manual-provenance supplement
already records170 bytes; exact REA byte reads and native disassembly support
this body without changing the frozen corpus or claiming a Ghidra dossier.

73468 direct comparisons pass:65536 exhaustively pair every CTRL4/CTRL5 byte,
4860 status/write/alias/rebinding cases,3072 getter cases. The enable bit also
matches an independent mask oracle, preserving all other CTRL_REG7 bits.108
firmware faults match. Register/status/scratch pointers, restoredr2/r3, callee
registers/SP, context and RAM match. A preliminary fixture incorrectly attempted
host memory writes to NULL; its396-count receipt/driver/log are archived under
`pre-null-fixture-guard` and are not native fault evidence. The corrected fixture
mutates only mapped non-NULL targets; actual NULL dereferences remain unguarded
in firmware and yield the108 matching emulator faults. Direct trace
`ebc15577e401c3fdf2f5ebfe6cdf966c7c6eeaa446517376ba00bab3ee637d8c`.

4320 composed auxiliary comparisons pass,2160 each. Actual wrappers, routing,
register helpers, default transport, memory clear and registry execute; bus,
custom read and logging callbacks are fixtures. Cases cover register patterns,
fresh/changing log modes, missing bus/slots, unwritten/error transports, context
rebinding and initial callback alternatives. Rawr0=1, restoredr3, context,
outer local byte/word and register model match. Observations:4500 reads,3960
writes,24840 custom reads,11520 mode queries,2880 ring and2160 SDK log calls.
Trace`a648bd55e58264d22fa1efd4dec91be5d2105257f2b7acd6ca24480ae366658c`.

Two main imports close, leaving26 with no new imports. All selected LIS native
providers are now source-linked. This does not prove live sensor setup or full
private stack histories/raw ABI. Arbitrary aliases/faults, real hardware,
original vendor checkout/compiler/placement, instruction and whole-image
identity remain gated; prior NV/health/DFU/snapshot gates persist. No physical
device write occurred.

### Native Bosch BMA interface and typed context candidate

`native-bma-interface` compiles53aec interface initialization,53ab4/53ad0
default read/write callbacks,53aa4 microsecond delay and7b61c null check. The
helper is extracted from Bosch BMA456 SensorAPI commit
`3266db2c5de15be1a00232b8c0f2fd23e07934e0` under BSD-3-Clause, renamed/exported
without algorithm changes, with exact slice and full license retained. Pinned
`struct bma4_dev` is52 bytes under the ARM short-enum ABI; offset assertions
bind interface4, enum8, status9, variant13, transfer length20, read36/write40/
delay44 and performance50 to native observations. A source-owned typed zero
context candidate is placed at2001e4e8 in tests; the full native allocation
extent remains unproven. Its bus-address word200076c0=18 is independently bound
to the authenticated initialized-data image, four source-owned bytes.

Initialization writes only observed fields in native order: interface1, default
callbacks, address pointer, delay callback, transfer length64, variant3 and
performance0. It retains every other byte. Defaults read the address byte through
the interface pointer, truncate transfer length to16 bits, call existing actual
motion request/registry dispatch and map bus success to0 or failure to raw-2.
Delay0 returns directly; nonzero delay passes wrapping`us<<6` to the existing
cycle primitive. The source contains named assembly mnemonics and typed SDK
layout checks, with no imported executable data.

4437 native/source comparisons pass:12 initialization,2160 read,2160 write,
9 delay and96 null-check cases. Actual five entries, memory clear, motion
requests and registry execute; bus and cycle callbacks are fixtures. Tests cover
NULL/unaligned contexts, all8 callback-presence combinations, missing bus/slots,
transport statuses, wide register/length values and NULL interface pointers.
1080 byte-load faults match. Rawr0, callee registers/SP, context/data bytes,
exact20-byte request records and API pointers match. Only relocated callback
function identities are mapped to native symbol identities; no data/stack
pointer is normalized. Observations:540 reads,540 writes,8 cycle calls. Trace
`130d5206b638cad71a52ee513cde69dcc59fbf1de0f7875af584894768190e2f`.

The main partial remains at26 imports; these prerequisites prepare BMA identity,
FIFO and configuration reduction. REA dossiers show generic register reads have
a feature-register5e path and private128-byte callback buffer, while FIFO reads
return signed16 byte counts and preserve asymmetric power-save failure returns.
Those contracts must be correlated before admitting upstream bodies wholesale.
Full context extent/private histories/raw ABI, real sensor/bus/cycle execution,
original compiler/placement, instruction and whole-image identity remain open.
Prior unresolved gates persist. No physical device write occurred.

### Native Bosch identity and register-read dispatcher

`native-bma-reads` compiles53b2c identity,54534 public register dispatch,
87bbc direct read and54408 advance-power-save getter. Identity initializes the
interface only when its read pointer is absent, clears only its saved-r3 low
byte, reads register0, logs failures with fresh mode reads and returns the byte
only on success.148 exact diagnostic bytes and marker1c0001 are source-owned.
The fixed context path makes native initialization failure unreachable in normal
mapped execution; that diagnostic branch is compiled but not separately
injected as a failing initializer in this receipt.

The direct read uses its native152-byte frame, including the128-byte callback
buffer, checks the actual attributed null helper and pointer, applies SPI mask
only when interface byte0, passes wrapping length+dummy to the captured callback,
stores its low status byte but branches on full rawr0. On success, a pure C copy
helper reuses the exact Bosch16-bit-index loop from pinned commit
`3266db2c5de15be1a00232b8c0f2fd23e07934e0` under BSD-3-Clause. The buffer is explicit
and the context is volatile so the dummy byte is reloaded after every possible
aliasing store. Copying runs after the callback returns, preserving actual
transport frame coordinates. No128-byte clamp or widened loop index is invented.

The public dispatcher compares the full register word to5e, retains the native
feature validation/error order, conditionally disables/re-enables power save,
and selects direct or chunked reads by feature length/transfer length. The
power getter runs through the actual register-read graph and writes only after
success. Feature-chunk87e58 and power-save-set5468e remain explicit unresolved
provider imports and bounded fixtures in their dispatch tests. One parent
identity import closes and two leaves are exposed, moving main imports26 to27.

7092 native/source comparisons pass:4348 direct,1360 dispatch,88 power getter,
1296 identity. Actual new bodies, copy loop, interface/null helper, motion
requests and registry execute; raw/bus/log callbacks and the two unresolved
feature leaves are fixtures. Cases cover missing callback combinations, NULL
contexts/destinations, unaligned/end-RAM destinations, data aliasing dummy-byte
state, zero/wide/oversized lengths, SPI/dummy values, error/unwritten reads,
callback rebinding and changing log modes.150 faults match. Full raw callback
status256 is a deliberate machine-contract stress input, beyond an int8 SDK
callback declaration. It remains an error even though stored status byte is0.
Rawr0, savedr3 where applicable, callee registers/SP, callback buffer/request
pointers, context and bounded output RAM match. Observations:5223 raw callbacks,
108 bus callbacks,130 power-save and36 chunk fixtures,3072 mode reads,768 ring
and576 SDK logs. Trace
`c9b0fb61e9cf40d338156dc2371807277f1238b2c6c51b3af84639bb8e799c96`.

Full private frame history, arbitrary oversized callback writes/aliases, full
16-bit-index wrap behavior, full raw ABI, native context extent, original vendor
checkout, live sensor/bus/log execution, compiler/placement, instruction and
whole-image identity remain unproven. Prior unresolved gates persist. No
physical device write occurred.

### Bosch power save and complete feature-register transport graph

`native-bma-feature-io` compiles seven native contracts:9756a direct write,
5475a public write,5468e power-save setter,8edd8 feature-address reset,70fda
address increment,87e58 chunk read and976b8 chunk write. Existing actual public
reads, direct copy/null check, default callbacks, motion requests and registry
compose with these bodies. Both previous feature helper imports close; no new
imports appear. Main imports fall27 to25; selected feature graph has zero.
Bosch BSD-3-Clause power-mask and four address-update assignments are factored
from exact pinned source slices into pure C helpers, preserving the native
transport call frames. Full license and pin
`3266db2c5de15be1a00232b8c0f2fd23e07934e0` attribution remain attached.

Direct writes preserve full raw callback-status testing and low-byte status
storage, then freshly load performance mode/delay callback/interface pointer;
mode exactly1 delays2us, otherwise450us. Public writes retain their extra
success guard before disabling APS, while existing public reads preserve their
own observed order. Feature reset writes context ASIC bytes23/24. Increment
reads5b/5c, adds half transfer length, splits address bytes and writes them
with native asymmetric error handling. A pure helper's address math also
matches an independent oracle. Chunk loops preserve native full loop count,
16-bit remainder/index, continue after failures, and advance the data pointer
only after both transfer and address increment succeed. No early break or
zero-transfer-size guard is invented.

11902 native/source comparisons pass:3488 direct write,4384 public write,
752 power setter,32 reset,392 increment,928 chunk read,934 chunk write and992
public read regressions with actual feature helpers.140 faults match.160 cases
observe later operations succeeding after a chunk error. Tests cover transient/
persistent failures, all callback-presence combinations, NULL inputs, raw/SPI
register words, transfer sizes0/1/2/16, remainder paths, power modes, unwritten
reads, callback-time delay/handle rebinding, actual default bus transport, and
six large-write vectors that exercise16-bit index wrap. Default emulator UDIV
behavior for zero divisor is observed, not promoted to all hardware CCR states.
Rawr0, callee registers/SP, callback data/request pointers, context/output RAM,
register model and operation ordering match. Observations:14074 reads,23637
writes,17953 delays. Trace
`bb1f5ab62c129e8d0d0114ceed1bc4f437846dd494fb2dd59ea71a1d6f9fbc07`.

Only raw/bus and delay callbacks are fixtures; feature bodies are actual source.
The earlier10910-case receipt before public-read regression expansion is
preserved. An initial test-oracle assertion incorrectly required address updates
on rejected NULL/missing-callback cases; that runner/log is archived under
`pre-oracle-guard`. The oracle now checks successful increments. Firmware source
was unchanged by that test correction.

BMA product configuration and FIFO remain open. Full private stack histories,
full raw ABI, arbitrary large lengths/backing/aliases, live sensor/bus/delay,
original vendor checkout/compiler/placement, instruction and whole-image
identity remain unproven. Prior unresolved gates persist. No physical device
write occurred.

### Native Bosch FIFO count, byte transfer and product wrapper

`native-bma-fifo` compiles54440 FIFO length,544c8 byte transfer and541a8 product
FIFO wrapper. Length clears its whole saved-r3 word, reads two bytes, masks the
high byte to6 bits and writes only after success. Its pure mask reuses the exact
Bosch assignment/header macro from BSD-3-Clause pin
`3266db2c5de15be1a00232b8c0f2fd23e07934e0`, with full license/slice retained. The
custom raw-byte API is reconstructed separately from the upstream structured
`bma4_read_fifo_data` API. It validates context/output/count, obtains length,
clamps to the full requested byte count, selects26/a6 from interface, calls the
fresh read pointer, stores low status but checks full rawr0, then returns the
fresh stack count as signed16. It does not add dummy-byte copying or a sample
count clamp absent from native code.

The product wrapper rejects NULL/zero requests with-1, disables APS, delays450,
passes wrapping low16 of`6*requested` to byte transfer, then restores APS only
after nonnegative reads. Disable/restore failures log and return0; negative
read failures log and return-1 without restoration. Success returns signed byte
count divided by6. Exact native frames and fresh logging-mode checks are
preserved.272 diagnostic bytes are source-owned and byte-checked. One parent
FIFO import closes with no new imports, moving main25 to24. Product BMA
configuration remains open.

76397 native/source comparisons pass:65984 length,3599 byte transfer,3599
product FIFO and3215 composed normalization. Every65536 wire-length pattern
also matches an independent14-bit mask oracle. Tests cover zero guards,
non-multiple-of6 counts, wide request wrapping, read/disable/restore failures,
SPI/dummy values, unwritten/partial payloads, callback rebinding, NULL/unaligned/
end-RAM outputs and FIFO-data aliases to native saved count slots. Alias tests
preserve signed negative count behavior rather than hiding it.6 emulator faults
match. Actual FIFO bodies, normalization, full read/write and APS graph, default
requests and registry execute; only transport, delay/cycle and logging callbacks
are fixtures. Rawr0, callee registers/SP, callback/request pointers, bounded
output/context RAM and final APS state match. Observations:84872 reads,6406
writes,4966 delay callbacks,3902 cycle calls,11682 mode reads,2784 ring and2784
SDK logs,3215 acquire/3213 release callbacks; faults account for incomplete
normalizer paths. Trace
`d8c352c4e5f9d2fbd6a39d9214a86b2689ecc4497c2265fc4b9c6bd96b99d4a5`.

Large count tests deliberately use bounded partial transport payloads. They do
not prove arbitrary callback writes/backing or full private-frame histories/raw
ABI. Actual sensors/bus/delay/logging, full native context extent, original
vendor checkout/compiler/placement, instruction and whole-image identity remain
unproven. Prior unresolved evidence gates persist. No physical device write
occurred.

### Bosch acceleration/FIFO setup and parameter validation

`native-bma-setup` compiles545ca acceleration config,54640 enable,546d0 FIFO
config and96820 parameter validation. Four validator bodies are extracted from
Bosch BSD-3-Clause pin`3266db2c5de15be1a00232b8c0f2fd23e07934e0` and renamed/exported
without algorithm changes. Enable-mask and FIFO configuration logic are factored
into pure helpers that return before native transport calls. Full license and
six source slices are retained. FIFO enable compares the full raw word to1;
value101(hex) is not silently truncated to a byte. Acceleration config preserves
sequential source-byte loads/stores and updates performance status after the
second write even when that write fails. Enable preserves the25000us delay after
a failed write; FIFO config preserves the1000us gap between successful first
write and second write. These behaviors are not hardened or repaired silently.

262144 standalone validator comparisons cover every ODR/bandwidth byte pair at
performance values0/1/2/255 against native execution and an independent limits
oracle. Results:95 valid,262012 out-of-range(-8),37 invalid averaging(-15).
Actual attributed validator bodies execute with no fixtures; rawr0/callee/SP
match. Trace`a10ddf6d9fe8623200f165df93194c023eda7a7d1e8825b3447338ce8c79e947`.
6966 scoped setter comparisons pass:1960 enable,3046 config,1960 FIFO config,
including729 matching faults and405 failed-write cases followed by25000us delay.
Actual setters/validator/kernels/read-write/default requests/registry execute;
raw/bus/delay callbacks are fixtures. Cases include failure/mutation histories,
missing callbacks, caller-owned RAM aliases, full enable words, parameter
limits and register-state oracles. Rawr0, callee/SP, callback/request pointers,
context and bounded RAM match. Observations:3890 reads,6772 writes,6549 delays.
Trace`a7221a9b06ed1a3b007c84622cf9b230c803afd39204ba4d09d7e0b3f814c89f`.

**Unresolved private-input frame gate:** an input pointer2003cfef lies below the
setter's frame and overlaps a nested callee return/private stack. The native
path writes00 to register40 while source writes11; return0 and final context
match. Standalone validator output equivalence does not close this composed
alias discrepancy. The full case/traces, original driver/log, source/objects and
report are retained under`pre-private-alias-scope` with
`private-input-frame-alias-probe.json`. Scoped passing tests exclude those
callee-private input addresses and explicitly carry the gate. No private byte,
input value or pointer is zeroed or normalized. Full original placement/private
frame history and raw ABI remain unproven; this is internal correlation work,
not an external blocker.

The main partial remains at24 imports; these are prerequisites for the remaining
604-byte product configuration wrapper. REA confirms that path configures ODR,
acceleration and FIFO and does not call a feature-stream upload. Variant
initialization543c4 loads8 literal bytes for a6-byte remap object; the trailing2
bytes and raw restoredr2/r3 require ownership/ABI correlation before reduction.
The6 meaningful remap fields match pinned designated defaults. Source/runtime
scope, full native context extent, live sensor/bus/delay, original vendor
checkout/compiler/placement, instruction and whole-image identity remain gated.
Prior unresolved evidence gates persist. No physical device write occurred.

### Bosch initialization and product configuration

`native-bma-initialize` compiles5447e base initialization,543c4 variant init
and604-byte53c6c product configuration. Base init preserves24-byte frame, SPI
pre-read/dummy-byte policy, status gates and chip assignment. Variant init
preserves16-byte frame, ID16 check, resolution16, feature length76, config-size
5016 and default remap. Product setup preserves32-byte frame, rates6/7/8/9 for
default/50/100/200, range2, averaging configuration, accel enable, APS disable,
FIFO clear7f/enable40/clear10 and APS restore, with exact failure/log ordering.
Fresh mode reads and marker1c0001 are retained.724 exact diagnostic bytes are
source-owned. Init/helper behavior and designated remap constants correlate to
Bosch BSD-3-Clause pin`3266db2c5de15be1a00232b8c0f2fd23e07934e0`; source slices,
headers and config-array size are authenticated. The5016-byte vendor array is
not embedded or uploaded by this native sequence; only its size is needed.

The native variant initializer reads8 bytes for6 typed remap fields. A declared
C span holds the6 Bosch designated defaults plus observed following bytes802e.
All8 bytes are authenticated at9a768 and byte-checked against the compiled
constant; restoredr2/r3 are compared without replacing those bytes with invented
padding. The semantic origin/ownership of the two following bytes beyond the
remap object remains unproven, despite their observed literal-read contract.
This separates source-owned build data from claims about original declarations.

13248 scoped native/source comparisons pass:5184 base,5184 variant,2880 product
configuration. Cases cover NULL/unaligned contexts, callback presence, SPI/I2C,
ID values, transfer failures, partial base/variant reads, request-rate edges,
changing log modes and missing bus/operation callbacks. Configuration success
scope uses complete successful reads. Actual init/configuration, full Bosch
setters/validation/read-write/default adapters/registry execute; transport,
cycle/delay and logging callbacks are fixtures.3 faults match. Rawr0, restored
r2/r3 as applicable, callee/SP, callback/request pointers, context and bounded RAM
match. Observations:13950 reads,18051 writes,22725 cycles,6320 modes,1580 ring and
1202 SDK logs. Trace
`43010b1e931a1a5bda16ea62803787b66f62269d486509a630cd88bffd982bbb`.

**Unresolved partial-read history:** a successful FIFO configuration read of2
bytes writes only its first byte. Native later writes80 to register49 while
source writes00, with identical API pointers/records and matching return1,
restored register and context values. Later FIFO writes/final register state
also differ. Full case/traces, source/objects/report/driver/log are preserved
under`pre-partial-read-scope` with`partial-read-history-probe.json`. Passing
product configuration tests exclude this partial-success history and explicitly
carry the gate. No uninitialized byte or data/stack pointer is normalized. Relocated callback
identities are compared symbolically. The earlier
private-stack input alias gate is also retained; neither is an external blocker.

One main import closes, leaving23 with no new imports. All selected Bosch native
provider bodies are now source-linked within these bounded contracts. This does
not establish full private history/raw ABI or byte-identical firmware. Full
native context extent, real sensor/bus/cycle/log execution, original vendor
checkout/compiler/placement, instruction and whole-image identity remain open.
Ghidra-MCP currently reports no GUI instance; REA headless evidence remains
available. No physical device write occurred.

### Native QMA transport, identity, interrupt and FIFO providers

`native-qma-transport` compiles8714c read retry,873f4 write retry,86e48 delay,
86e34 chip ID,86fa8 IRQ and86ff4 FIFO. These are owner-authorized reductions of
native contracts. The existing hardened reconstruction remains unchanged as
comparison evidence, with hashes bound separately from build inputs. No
unlicensed QST snapshot is compiled.12 source-owned cold bytes at20007698 hold
address12 plus independent double-tap/any-motion callback slots;144 exact FIFO
diagnostic bytes are source-owned. This runtime address is distinct from the
sensor-state address byte at2001e4b0; configuration must preserve that distinction
until its complete native contract is reduced.

Reads try five times, loading the fresh address each time, and delay5 units
after every failure including the fifth. Each unit sends64000 cycles to the
existing named cycle primitive. Writes try five times without delays and pass
one byte from their saved full value word. Chip ID does not initialize the
saved-r3 byte or propagate read status. IRQ clears its saved word, permits ten
read-retry rounds, uses any-motion bits0..2 then fresh double-tap byte1 bit5,
and freshly loads callback pointers between calls. FIFO requires level-read
success1, masks7 bits, rejects depths above64 with0, clamps to requested count,
then performs payload read and reset3e=87 even for zero samples. Payload/reset
errors are ignored and the clamped count is returned. These contracts differ
from the portable hardened path and are not silently replaced by its guards.

17074 native/source comparisons pass:3026 reads,4032 writes,4 delays,1344 IDs,
1024 IRQ,6382 FIFO and1262 composed normalization. Actual six bodies, normalizer,
motion requests and registry execute; bus, cycle, log and event callbacks are
fixtures. Tests cover retry success/failure boundaries, last-failure delay,
wide register/length words, saved-value mutation, fresh address changes,
unwritten ID bytes, IRQ callback rebinding/status mutation, every256 FIFO level
byte, zero requests, ignored payload/reset errors, missing bus operations and
bounded NULL/end-RAM inputs. Rawr0, savedr2/r3 where applicable, callee/SP,
exact request/data pointers, runtime and bounded RAM match.2 faults match.
Observations:39282 reads,10190 writes,271566 cycle callbacks,15270 modes,1440
ring/1440 SDK logs,392 any-motion/371 double-tap events,842 acquire/841 release.
Trace`09039ade6a0173324a0165df6bebcc5ca654c281ce9fec6e5c15351451bf14f9`.

The first test runner hooked a different duplicate cycle primitive, so native
execution exhausted its instruction bound inside9a6a0 before comparison. Its
runner/log are retained under`pre-cycle-fixture-address-fix`; the native86e64
literal and9a6a0 primitive are now explicitly authenticated. Firmware source
was unchanged by that fixture correction. This is cycle-argument emulator
evidence, not physical timing proof.

Three main imports close with no new imports, leaving20. QMA configuration
remains unresolved. Full sensor-state extent/private frame history/raw ABI,
arbitrary callbacks/backing/aliases, live sensor/bus/events/timing, original
compiler/placement, instruction and whole-image identity remain unproven.
Prior Bosch partial-read/private-input and NV/health/DFU/snapshot gates remain
open. No physical device write occurred.

### Native QMA configuration graph

`native-qma-configuration` compiles seven native bodies:86e68 product
configuration,86ee4 setup,86d40 any-motion,87188 range,871c4 reset,87250 steps,
and872e4 tap routing. REA Ghidra dossiers and byte receipts bind these bodies
to the authenticated application; Ghidra-MCP discovery found no running GUI
instance. The owner-authorized native source uses symbolic inline assembly
inside C translation units to preserve callback-visible frames; it contains
no executable byte array. Existing hardened QMA source remains comparison-only,
not a build dependency. No unlicensed QST source is compiled or claimed as
upstream. The previously attributable Nordic delay provider is reused. A later
upstream update must retain these native contracts rather than importing the
portable path's guards or error propagation.

The source owns a24-byte aligned sensor-state prefix at2001e4b0 (observed
fields through offset21, alignment tail22..23), with scale at4,state at8,
three sign halfwords at10 and maps at16. Full object extent remains gated.
Twelve typed axis-default bytes match9a6a6 exactly. Configuration tries copied
address bytes12 then13 in the sensor state, clears/stores ID, and acceptsFA or
high nibble9. Actual transport still freshly uses its independent address at
20007698. Configure passes the low8 rate to setup, then always clears state8
and copies orientation defaults. It does not silently make these addresses
share storage.

Setup ignores all underlying statuses and returns1. Reset clears only low
bytes of two saved words, performs writes36=B6/00, delays5/100, polls11 for80
and33 for05 with up to102 rounds each, then returns0 even on timeout. Range
stores2048/1024/512/256 for full-word2/4/8/15, otherwise4096, then tail-writes
reg0F with the input byte. Rate25/50/100/150-or200 selects native register
pairs; other full rates skip those writes. Motion, steps and tap preserve
native byte masks, unconditional writes, chip-specific branches, ignored read
failures and fresh state reads. Motion returns its restored/mutated savedr0
word rather than a synthesized status.

The selected configuration graph has no unresolved symbols. The broader main
partial runtime closes configure with no new imports, leaving19. Full private
frame history/raw ABI, exact original compiler/placement/instruction identity,
whole-image identity and physical sensor/bus/timing proof remain open. All
previous Bosch partial-read and stack-alias, DFU, NV and health evidence gates
persist. This is source/compiler/emulator evidence and authorizes no hardware
writes.

The first composed setup suite found a concrete unwritten-read private-history
difference: setup(rate25,chip90,successful bus callback leaving all read bytes
unwritten,zero seeded stack) returns1 on both sides, but trace1698 writes
register19 with nativeFB/sourceF3. Request pointers and record bytes otherwise
match. `unwritten-setup-history-probe.json` and the complete candidate, builder,
runner, objects, report and failed log under`pre-unwritten-setup-history` retain
this evidence unchanged. Passing scope explicitly excludes composed setup and
configuration with active bus callbacks that leave reads unwritten. Direct
reset, motion, steps and tap still cover unwritten reads. No payload mask or
return normalization is applied; original placement/private-history behavior
remains an unresolved gate, not source completeness or whole-image proof.

5806 scoped comparisons pass:555 configure,555 setup,1138 motion,1054 range,
228 reset,1138 steps and1138 tap. These include full-word rate/range inputs,
retry failures, failed writes, timeout boundaries, byte patterns, live address/ID
mutations and missing bus callbacks. Native/source rawr0, savedr2/r3 where
applicable, callee saves/SP, exact requests/data pointers and state match within
this scope.162035 reads,203573 writes and1123250 cycle callbacks were observed.
Trace`7fe598835eeb3fab480e878d470217b5561342b1fba273d294d3ba7cede2474f`.
The unwritten composed history gate above remains open.

### Native calibrated temperature path

`native-temperature` adds eight owner-authorized native bodies:50e4c calibrated
pair,6f600 shared sample read,6f80c/6f826 channel reads,6f738 one-shot setup,
6f818/6f832 channel one-shots and7badc calibration copy. Non-contiguous REA
Ghidra body ranges are reduced together; public six-byte veneers alone are
not treated as complete providers. Symbolic inline assembly in C translation
units preserves native frame and floating-point effects without executable
opcode arrays. Existing GXT310 bus/mode/registry, RTOS delay and NV source
providers remain linked, with no new unlicensed dependency or guessed vendor
checkout. Future dependency updates must retain authenticated contracts.

The shared read zeroes its saved word, requests2 bytes from register0 ignoring
status, reverses and sign-extends the sample, multiplies by binary32 1/128 then
1000, and converts toward zero. One-shot writes native four-byte word0000C101
as a two-byte transfer to register1, treats any nonzero transfer return as
success, and otherwise uses fresh log modes.100 exact diagnostic bytes are
source-owned. The pair acquires/enables, triggers both one-shots, delays80 via
osDelay, reads both channels, disables/releases, then reads calibration. These
statuses are ignored. Calibration reader allocates128 bytes, reads124 ignoring
status, and copies bytes62..67. The six-byte source record at200076f0 has exact
cold value000000000000. Only an all-FF observed calibration bypasses offsets;
flags0 subtract/1 add unsigned16 offsets, other flags leave the sample alone.
The wrapped sum is adjusted by its top bit then bits1..16 are returned; no
portable saturation or substituted signed-division policy is added.

69964 scoped comparisons pass:65776 shared reads,240 for each channel read,
48 for each of three one-shot entries,1782 pair reads and1782 calibration
copies. Every65536 wire word is checked against an independent integer oracle.
Selected rounding modes, failed/unwritten/partial transfers, partial124-byte
NV reads, invalid flags, all-FF positions, logging modes and callback-mutated
one-shot words are covered. Rawr0, savedr3 where applicable, callee saves/SP,
S0/S1/FPSCR, bounded data and exact typed boundary arguments/pointers match.
Bus/mode/registry/NV/RTOS/log dependencies are fixtures in this passing scope;
no end-to-end source/hardware claim follows.69820 read-transfer,3708 write-
transfer and3564 NV callbacks execute. Trace
`25954065685c7ace271e27f6234c4cdb194753b57240bf34d3e919867c42a139`.

A separate actual GXT bus/mode composition probe reaches equal raw result19795
but first dispatch write has native buffer2003cfc8/source2003cfcc (SP-56/SP-52)
with identical00C20000 word and record address. The first differing request
record and complete trace are retained in`composed-history-probe.json`; no
pointer normalization is applied. `post-cold-calibration-frame-probe` preserves
the current candidate/objects/builder report/runner/log. Prior snapshots remain
immutable. This is a concrete call-frame gate for the reused GXT source path,
not a passing composition or an external blocker.

The cold-data audit also rejected the initial all-FF source initializer. The
entire earlier candidate is preserved under`pre-cold-calibration-fix`, with
`cold-calibration-correction.json` hashes. Source now initializes zero, is
rebuilt and reverified; arbitrary seeded behavioral cases do not prove cold
initialization. Main partial imports fall19 to18 with no new imports. The
selected transitive graph still exposes11 existing imports through its NV/RTOS
consumers. Full private history/raw ABI, exact original compiler/placement,
whole-image instruction/byte identity and physical sensors remain gated;
prior QMA/Bosch/NV/health/DFU gates persist. No hardware writes occurred.

### GXT mode call-frame correction

`native-gxt-call-frames` supersedes the relocated mode implementation at five
symbols:6f648 shared switch,6f804/6f81e channels,50f9c enable pair and50f88
disable pair. Native symbolic inline-assembly bridges in C retain the16-byte
shared frame,24-byte enable frame and8-byte disable frame. They reuse the
existing source-owned308-byte GXT mode/configuration/text spans; no duplicate
constant source, executable blob or new vendor source is introduced. Existing
GXT bus/request bodies, temperature bodies, calibration state and floating-point
conversion execute in composition. Future upstream changes must preserve these
callback-visible contracts or produce new explicit evidence gates.

A copied parent object weakens exactly these five symbol bindings. Audit
compares every allocated section's type/flags/size/alignment/payload hash and
all other symbol entries to the original; the historical parent object/source
is unchanged. The final partial runtime keeps18 imports and selected NV/RTOS
transitive graph11. Existing mode contracts are strengthened, not counted as
new ownership functions; the previous69964 scoped temperature sample/calibration
comparisons remain independently bound to their original source and report.

5376 native/source comparisons pass:3456 actual temperature compositions and
384 direct cases for each of five corrected mode/pair symbols. Composition
covers the exact prior counterexample, successful and failed dispatch statuses,
read callbacks writing zero/one/two bytes, partial calibration reads, positive
and negative sample pairs, invalid and all-FF calibration flags, fresh logging
modes and mutation of the full four-byte configuration word through a two-byte
write pointer. Every observed request/data pointer and payload is compared
without normalization, along with rawr0, callee saves/SP, S0/S1/FPSCR, calibration
and bounded destination data. Observations include6912 read dispatches,23424
write dispatches,3456 acquire/release/NV/delay callbacks,56064 mode queries,
8256 structured formats,10560 one-argument and3456 zero-argument SDK logs.
Trace`7d32c628728fb2f567e1477ba017ee594f163c37d324f701067f27af13cd4781`.

The earlier native2003cfc8/source2003cfcc first-write pointer mismatch is
resolved within this composed scope, while the original unnormalized failure
and candidate remain immutable under`native-temperature`. Registry dispatch,
NV reader, RTOS delay and logging are fixtures at their explicitly named
boundaries in this proof. Complete registry/NV/RTOS execution, all private
return-address histories/raw ABI, original compiler/placement, whole-image
instruction/byte identity and physical sensors remain unproven. Prior QMA
unwritten-read, Bosch alias/partial-read and NV/health/DFU gates remain open.

### Source-owned bounded event-table prefixes

`native-event-table-prefixes` owns164 writable callback-table bytes as typed C
function-pointer relocations:17 sensor words at20006750,16 system words at
20006e54 and8 storage words at200066fc. Their relocated words match the
SHA-authenticated decompressed initialized data. These are bounded observed
prefixes, not asserted full table extents. The native dispatcher still permits
lookups outside them; no guard or fabricated table length is added. The sensor
sentinel at index0 is not admitted by the dispatcher; indices1..16 correspond
to events2..17. System indices1..15 correspond1000..100E. Storage indices1..7
correspond2000..2006, with the final slot zero.

37 non-null callbacks are explicit typed imports, each named by its original
entry address. They use symbolic function relocations and contain no retained
instructions or return stubs.
`callback-frontier.json` records each source dependency, frozen ownership
matches where available and unproven body spans. Three table anchors close,
but37 callback-body imports are newly exposed: the main link therefore grows
18 to52 unresolved imports. This makes the hidden configuration dependencies
reviewable and does not imply callback bodies are implemented. No ownership
function is upgraded or added solely because its pointer word compiles.

1824 native/source dispatch comparisons pass:768 sensor,720 system and336
storage. Every included live/null slot is tested with zero, four, five and
65535-byte lengths, four payloads and writable rebinding to null or a replacement
callback. High ID/length words are nonzero to check truncation; callback mutation
of the input record confirms cached payload/length ownership.1200 callback and
912 free observations match. The source dispatcher and source table relocations
execute; callback bodies and free are fixtures. Trace
`a3f881d47894d59563ebb655ab02edb4360859cf3a2ff2dd7b634059e0fc603d`.
The original exhaustive65536-ID broad-RAM dispatcher proof remains independently
bound; these prefix tests do not replace its out-of-prefix indexing evidence.

REA's current headless Ghidra target lacks procedure objects for several of
these callback entries and89EEC, despite native Thumb instructions/frozen
pseudocode being present. `rea-procedure-availability.json` retains the scoped
provider failures with target/profile attribution. Ghidra-MCP discovery found
no running GUI instance. This is an analysis-coverage gap, not proof that a body
is absent and not an external stop condition: frozen corpus and authenticated
byte/disassembly evidence remain available. The first prefix test runner omitted
the native free fixture; its driver/log are preserved under
`pre-native-free-fixture-fix`. Correcting the fixture changed no firmware source.

Full callback-body compilation, all table extents and neighboring data ownership,
complete dispatcher/handler composition, private/raw ABI, original compiler/
placement, byte-identical whole image and physical-device execution remain
open. All previous QMA/Bosch/NV/health/DFU gates persist. No hardware write occurs.

### Native event callback bodies and explicit service frontier

`native-event-callbacks` compiles all37 non-null callbacks exposed by the bounded
sensor/system/storage table prefixes. Native Thumb CFG traversal covers1766
reachable code bytes. External tail branches remain explicit service calls;
local branches and return paths are reduced as symbolic inline assembly inside
C translation units, not retained instruction arrays. The actual native two-byte
return-only body at428B2 is preserved rather than used as a substitute for other
callbacks. Callback definitions use the tables' compatible C signature
`void(uint32_t,uint32_t)`; raw machine register behavior is separately measured.

The source owns815 unique diagnostic bytes in31 arrays, with a32nd string
identity at42724 represented as the interior suffix42710+20. The full observed
string uses824 bytes when counted with that shared suffix twice. No duplicate
overlapping array is placed there. The initial duplicate-string candidate is
retained under`pre-text-alias-correction`. A recovery metadata field was renamed
to say that Ghidra bodies were not used for this CFG pass, rather than claiming
absence from the frozen corpus; earlier contracts/reports remain immutable under
`pre-recovery-metadata-label-fix`. `pre-callback-c-type-correction` preserves the
earlier C declaration; allocated section bytes are identical after correcting
the table/callback type compatibility. `correction-history.json` binds snapshots.

53280 direct native/source comparisons pass,1440 per callback, with792 matching
bounded faults. Zero, unaligned, valid and end-RAM payloads, wide/full lengths,
zero/nonzero/full-word service results, fresh log modes, signed and all-FF data,
service mutation and native saved-stack words are exercised. Rawr0..r3,
callee saves/SP, exact typed logging stack arguments, call order and bounded RAM
match in the passing scope.54750 service/log observations execute. Services,
logging and free are explicit fixtures, not full consumer composition. Trace
`da957f07ccedeaeb09bf91ed745d7a37b5e848c0e7306249955258fd2fded52b`.

A separate failed actual dispatcher/table/callback probe is preserved in
`dispatch-raw-abi-probe.json` and`pre-dispatch-raw-abi-scope`. Sensor event2 with
payload20010000,length0 tail-calls8B0FC with matchingr0/r1, but nativer2/r3 are
42857/98765432 while source carries100080B/0. The first difference is the native
callback address versus relocated source callback address; the dispatcher also
changes another scratch register. No register or pointer normalization is
applied. Passing receipt explicitly excludes composed dispatch; full scratch
ABI and original code placement remain open. This is an internal evidence gate,
not an external stop condition.

37 callback imports close. Fifty service targets are named:9 already have
source providers in the parent;41 newly exposed bodies remain unresolved. Main
imports therefore grow52 to56, and the selected dispatch/handler graph has49
imports. `service-frontier.json` records every target, source symbol, frozen
ownership match where available and lack of an established upstream body match.
Historical ownership/decompiler classifications are retained; they are not
promoted to third-party implementation provenance by this native-byte recovery.
No new unlicensed vendor source or guessed upstream implementation is compiled.
Attributable existing logger/registry/runtime source remains separately bound.

Full service-body compilation, actual dispatcher ABI/composition, table extents,
all private histories, original toolchain/link placement, byte-identical whole
image and physical behavior remain unproven. Prior QMA/Bosch/NV/health/DFU gates
persist. These checks execute only in Unicorn; no device or firmware write occurs.

### Native health-event consumers

`native-health-event-consumers` adds six source bodies spanning236 native bytes:
8A7F4 activity,8A80A HR,8A83E HRV,8A8AE SpO2,8A8D8 stress and8A8FC temperature.
Frozen pseudocode/ownership and Thumb disassembly are hash-bound; REA supplies
an authenticated308-byte read covering the complete code region. Current REA
procedure objects are unavailable at these entries, so no missing dossier is
presented as proof of a missing function. Symbolic native instructions compile
inside C functions with the same two-word interface used by the event callbacks.
No third-party body, opcode array, silent source fallback or new vendor checkout
is introduced. These are product wiring contracts; upstream body identity is
not asserted. Existing attributable runtime providers remain independently bound.

Activity accepts any nonzero input pointer, calls activity storage and then
notification kind4. HR accepts bytes40..220 and HRV has no NULL/range guard;
both fill only zero payload timestamps. They serialize measurement+timestamp
into savedr2/r3 words at nativeSP-16: HR writes1+4 bytes,HRV2+4. SpO2 accepts
bytes>=70, unconditionally replaces timestamp and notifies kind1; HR notifies0,
HRV5. Stress accepts bytes<=100, replaces timestamp and stores without a
notification call. Temperature accepts the unsigned16 value250..500, replaces
timestamp and packs **low byte plus6 modulo256**, followed by timestamp, rather
than a guessed portable temperature conversion. It also omits notification.
None of these bodies validates the supplied length. Actual callback wrappers
retain their separate pointer/length policies.

92320 native/source comparisons pass:88288 direct bodies and4032 actual event
callback compositions. Every65536 temperature value is checked; all256 HR,
SpO2 and stress bytes are exercised with old/zero timestamps and callback-driven
mutation. An independent oracle checks acceptance, packed fields, timestamp
policy and notification kinds. Unaligned/end-RAM/NULL inputs, clock boundaries,
full-word status returns, fresh modes, packed saved-word mutation and native
rawr0..r3/callee saves/SP are included.720 actual emulated faults match.
Observations:10657 timestamps,14699 storage,11352 notification,1792 mode,
448 ring and448 SDK callbacks. Trace
`a4b96f1ad2cc3be40ca6433d4500b13166f966c0c0ac703e458a0eda10d6f39c`.

Clock, storage, notification and logging callbacks remain fixtures. Composition
here begins at the six existing event callbacks, not the outer dispatcher;
the earlier dispatcher scratch-register/code-placement gate remains open. The
first runner attempted an unbounded host snapshot of an end-RAM storage argument.
`pre-storage-fixture-span-fix` preserves that runner/log and
`fixture-correction.json` binds the repair history. Host fixture reads/mutations
are now bounded; the native source was unchanged. Unread service pointers are
recorded as such, not claimed as actual storage faults or storage behavior.

Six main imports close and seven storage/notification bodies become explicit:
activity,HR,HRV,SpO2,stress and temperature storage plus notification throttling.
Main unresolved imports therefore grow56 to57; the selected consumer graph has
exactly those seven imports. Remaining aggregation/provider bodies, complete
dispatcher composition, all private/raw ABI, original compiler/placement,
byte-identical whole image and hardware proof remain gates. Prior QMA/Bosch/
NV/health/DFU evidence remains unchanged. No device or firmware writes occur.

### Native health notification throttle and selected byte identity

`native-health-notification-throttle` compiles8B138's72-byte native body and
owns only the4-byte last-send word at200067A4, with authenticated cold zero
initialization. The preceding context word is not claimed as source-owned;
the symbolic native-base-minus4 expression preserves the originalr5 base.
REA's76-byte receipt, frozen pseudocode, disassembly and compiler inputs are
hash-bound. No opcode array or invented whole context is used.

After the authenticated phone gate returns nonzero, the code captures the
current timestamp and freshly reads the last-send word. It sends if last is
zero, unsigned now<last, or now-last>=10800; equality10800 sends. Otherwise
rawr0 is the elapsed delta. It calls the four stages8C150,8CD60,8C750,8BAEC
withr0=0, then8B818 withr0=1/r1=0. All stage return values are ignored for
control flow. Finally it stores the previously captured timestamp, overwriting
any stage callback mutation; rawr0 remains the last stage's return. The input
kind does not select stages. Disconnection skips time lookup and every stage.
No new retries, guards, synchronization or alternate clock policy is inserted.

15852 native/source comparisons pass:13548 direct and2304 through actual
activity/HR/HRV/SpO2 consumers. An independent unsigned oracle covers threshold
neighbors, high-bit/wrapped/backwards timestamps, initial-zero state, full-word
gate results, ignored stage errors and mutation of the state by gate,clock or
stage callbacks. Stage order and exact arguments, rawr0..r3,callee saves/SP,
state and unchanged neighbor guards match.9545 sends produce47725 stage
callbacks;15852 gates,12844 clocks and2304 storage callbacks are observed.
Gate,clock,stage and storage are fixtures; this is not full dispatcher or
physical execution. Trace
`c6b724116c8b3239df47a7da2567161b7e7da77ed753cf44edb63ae8ae19cb09`.

Additional source-build verification establishes **312 byte-identical bytes
across seven code spans**: all six preceding consumer bodies(236 bytes), plus
the throttle body and literal(76 bytes). Both C objects are linked together at
the original addresses; consumer-to-throttle branches bind the actual compiled
throttle symbol. External gate,clock,storage and stage addresses are explicit
verification bindings. Every compiled span equals the authenticated application
bytes, including the throttle literal. `exact-span-verification.json` covers
that76-byte unit; `consumer-exact-spans-verification.json` covers the joint seven
spans. This is selected native-placement code identity, not a complete provider
graph, complete image or recovered original linker/toolchain proof. Earlier
relocatable/emulator reports remain immutable with their broader identity gates.

One notification import closes and five named report-stage bodies are newly
exposed, growing main imports57 to61. The selected throttle graph has exactly
those five unresolved stage imports. Native phone/runtime providers remain
linked separately; no guessed upstream body or unlicensed vendor source is
introduced. Report/storage implementation, outer dispatcher scratch ABI,
complete context/table extents, all private histories, whole-image identity and
hardware proof remain open. Prior QMA/Bosch/NV/health/DFU gates persist.

### Source health notification sync controllers

`native-health-notification-stages` compiles five controllers exposed by the
throttle:HR8C150,SpO2 8CD60,HRV8C750,activity8BAEC and status8B818. These include
3400 native instruction bytes. The four larger controllers read24-byte sync
markers, use native epoch/day/window rules, allocate128-byte caches and native
148/220/1180-byte builders, query/iterate flash, handle no-flash fast-forward,
flush buffered/offline data, finalize and free both allocations. Allocation
failures, ignored provider results and fresh log modes remain native behavior.
The status controller packs first low8 and second low16 into its saved-r3 word,
leaving byte1 from incomingr3, calls5B39C with the encoder pointer, then restores
the modified saved word. No synthesized failure return or replacement stub is
added. Iterator/encoder callback bodies remain named source dependencies.

The first translated candidate passed24336 native/source comparisons using
symbolic relocated literal loads. It is preserved immutably under
`pre-inline-literal-layout`. The final source instead retains native PC-relative
instructions, readable`.asciz` text, symbolic`.word` pointers and authenticated
zero padding in C inline assembly. It contains no opcode/instruction-byte arrays.
Five source-compiled code+literal/text spans, totaling**6313 bytes**, now match
the authenticated application exactly at verification placement. External
providers and callbacks are explicit native-address verification bindings,
not compiled-body proof or fallback providers in a completed image. After the layout correction and explicit full-word nonzero provider-return
cases,24360 behavioral comparisons pass:1446 per large controller and18576
status-packing cases. The prior byte-identical receipt and runner remain under
`pre-controller-status-fixture-coverage`. Rawr0..r3,
callee saves/SP, exact call/stack arguments, sync records, heap images, allocation/
free order and pending bytes match. Trace
`726d43c022458792b95986177f34560daca594ba1ce5e31f60468f4853aa3761`.

Only six2-byte descriptor prefixes at99BF4+i*16 are source-owned(kind/length),
not the full96-byte descriptor/callback table. Four individual cold-zero pending
bytes are owned at2000679A,2000679D,200067AD and200067AA. The controller-readable
text is2692 unique bytes; other owned readonly bytes are typed words and proven
zero padding. Full descriptor/context extents remain gated. Heap,IO,time,
database,logging and builder APIs are fixtures in behavioral verification;
iterator/builder encoder callbacks are explicitly **not executed**. Tests cover
window/day boundaries, backwards markers, no-data queries, allocation failures,
buffered/offline modes, partial/failed IO, fresh modes and mutable pending state.
No actual flash query, persistent storage or phone transmission is claimed.

Five stage imports close and34 unresolved providers/callbacks are exposed,
growing main imports61 to90. Thirteen other targets already have parent source
providers. `contracts.json` names all47 referenced targets; whole-provider
composition and all callbacks remain gates. The native-placement byte match
covers these five controller spans, not their implementations or a complete
image. Earlier broad identity gates remain immutable.

The existing`third-party/upstream/flashdb-2.0.0` Apache-2.0 corpus supplies three
specific reuse candidates:63694 maps by API shape/command6 to
`fdb_tsdb_control`/`FDB_TSDB_CTRL_GET_LAST_TIME`;63CB4 maps by db/from/to/status2
shape to`fdb_tsl_query_count`/`FDB_TSL_WRITE`;63AD8 maps by its five arguments to
`fdb_tsl_iter_by_time`. `upstream-reuse-candidates.json` binds LICENSE,headers and
source hashes. These are evidence-backed API candidates, not authenticated
native body/vendor-checkout or struct/raw-ABI matches. No upstream body is a
new build input here. Reusing that attributable source after native ABI checks
can shorten the remaining analysis and retain a path for comparing upstream
fixes without silently changing the stock contracts or byte-identity target.

Remaining callback/builders, source DB ABI, full contexts/tables, all private
histories, original whole-image compiler/placement, image identity and hardware
proof remain unproven. Prior dispatcher scratch,QMA,Bosch,NV,health and DFU
gates persist. No device, flash or external-message write occurs.

FlashDB follow-up: `native-flashdb-tsdb-kernels` now compiles five pure C
helpers from Apache-2.0 commit4e5677408256f82d47cd56a6b04605dcee35ed9a.
Original slices and native struct-field/static size checks are retained.
50,000 native/source comparisons pass for typed return/memory/callee/SP
contracts. Forward sector and both log-index helpers retain caller-saved
register differences; none is promoted to the main provider graph. This makes
upstream updates reviewable through pinned slices and contract replay, without
assuming a later release preserves the stock ABI or byte encoding.

The separate native query-count adapter preserves an observed divergence:
uninitialized DB returns0 rather than upstream FDB_INIT_FAILED. Its callback
and DB-path helper are also compiled from symbolic source. 8,192 comparisons
pass with iterator/log fixtures and actual DB-path execution. Native placement
reproduces171 bytes; this closes one main import (89 remain), not full TSDB or
whole-image source closure. Control/time iteration, callback composition,
private histories and original compiler/placement gates remain open.

The native time iterator and four navigation helpers now compile in
`native-flashdb-iterator`. Pinned FlashDB's iterator/search/navigation C explains
the source contract and remains the attributable comparison source; the main
adapter preserves native register/frame/encoding behavior through symbolic
assembly in C. Its source count -> iterator -> count-callback composition
passes468 cases within948 total comparisons.592 new native bytes and763 joint
bytes match at explicit native verification placements.87C24/87E14 sector/log
read bodies remain imports; there are90 main imports after exposing these two.
No fixture-based read result is claimed as a source implementation. Native
failed-read stale-stack and uninitialized-log-then-continue behavior remain.
Later upstream fixes require explicit contract/encoding review before adoption.

`native-flashdb-log-read/upstream-contracts.json` binds pinned Apache-2.0
FlashDB source for read_tsl, _fdb_flash_read and _fdb_get_status plus recovered
configuration. The native source adapters compile and pass29,248 direct and948
composed comparisons.126 new native code bytes match;889 bytes match jointly
with source iterator/count at native verification placements. These adapters
preserve FILE_MODE-off read errors, signed FAL return handling,32-bit status
granularity and ignored-read-error private buffer history. Partition and sector
read bodies remain explicit imports. Upstream source is the attributable
comparison contract here; symbolic native bodies are the build inputs, and
upstream upgrades require replaying native contract/encoding checks.

The sector reader87C24 now compiles in`native-flashdb-sector-read`, following
pinned FlashDB read_sector_info control flow while retaining native frame and
encoding behavior. Its independent space/layout oracle and native/source
execution pass9,615 direct cases, including83 assertion-loop observations and
all81 possible header-prefix lengths.948 further cases execute the complete
source count/iterator/sector/log/status path with partition I/O fixtures.
513 new bytes (body/data plus assertion-name text) and1,402 joint bytes match
at explicit native verification placements. Native ignored read errors,
assertions, end-info precedence and wrapped alignment are preserved. The
existing pinned FAL partition source is the next attributable comparison input;
its earlier compile-only report is not sufficient native ABI proof.89 main
imports remain, including631E8 partition read. Whole-image identity is false.

`native-fal-partition-read` now compiles the native631E8 partition read body,
with the Apache-2.0 FAL0.5.99 source bundled by pinned FlashDB2.0.0 as comparison.
6,863 direct and948 composed checks pass;460 new and1,862 joint native-placement
bytes match. Wrapping bounds, fresh offset after lookup, signed callback return,
diagnostics and actual assertion loops remain native behavior. Lookup mutation
and output aliasing to partition fields are tested. The earlier pinned FAL
compile-only object is not substituted for these frame/encoding contracts.
64F74 device-by-partition is the new explicit import; its table/cache ownership
and callback binding still require proof.89 main imports remain. Later upstream
fixes require native-contract and byte-encoding review before adoption.

FAL64F74 device lookup now compiles against the pinned initializer's existing
36-byte table/count/cache state. Only three symbols become externally visible
in a parent clone; allocated sections and other symbol entries are unchanged.
17,370 direct and948 composed comparisons pass. Native inclusive pointer bounds,
unaligned floor-index cache lookup and assertion loops are retained; no stricter
modern guard is substituted.206 new and2,068 joint native-placement bytes match.
The current main graph has88 imports. The final linker must preserve table/count
adjacency; verification placement is not whole-image layout proof. Runtime cache
values/device read callback remain fixtures. Pinned FAL source, initializer
report and prior initializer receipt are bound in the reuse manifest, allowing
future upstream changes to be reviewed against the same source-state ownership
and native contract rather than creating a duplicate configuration.

The product FAL-to-registry read adapter87AF8 and generic registry slot1085D2C
now use native frame-preserving source in`native-fal-read-frames`. These local
bodies are owner-authorized reconstruction, not attributed FAL upstream code.
The pinned upstream FAL/TSDB chain remains intact.6,144 direct and948 composed
comparisons pass;1,536 native invalid operation-table faults are preserved.
Sixteen existing state bytes are reused; only two provider symbols are weakened
in a parent clone and other providers/allocated sections remain unchanged.
66 new native-placement bytes match, bringing the joint chain to2,134 bytes.
Native driver-result ignoring and saved requested-length behavior are retained.
Concrete registry driver I/O remains a fixture;88 imports and final image,
layout/private-history gates remain open.

Local internal-flash policy54A4C and mapped byte-copy5C464 now use native
frame-preserving source. These owner-authorized local adapters complement the
pinned FlashDB/FAL dependency; they are not upstream vendor source.3,420 direct
and948 composed checks pass, including low16 length, overlapping forward byte
copy, callback mutation and420 native faults. The composed source TSDB/FAL path
now performs read I/O through the registered driver and mapped copy rather than
an I/O provider fixture. Generated emulator flash contents/runtime bindings
remain fixtures and provide no physical-device proof.92 new bytes match at
native placements,2,226 jointly;100 existing record/context bytes are reused.
88 imports, final startup/registration binding, layout/private-history and full
image gates remain open. No firmware or device writes occur.

FlashDB control63694 now compiles from symbolic native source using the pinned
Apache-2.0 fdb_tsdb_control as the attributable comparison contract.5,728 direct
comparisons pass across all command/init bytes and alias/fault paths. Its12-byte
TBB table is source-owned symbolic data; no instruction arrays are emitted.
Native exact init==1 assertion, raw-byte rollover/not-format settings, disabled
FILE_MODE logging/max-size branch and unknown-command no-ops are retained.
476 new native-placement bytes match,490 with the source DB-path helper.87 main
imports remain. Logging/zero low-ROM are fixtures; source caller composition,
full histories, original compiler/layout and whole-image identity stay open.

Five local native health sample aggregators now compile in
`native-health-sample-storage`; these are owner-authorized product reconstruction,
not third-party source.131,365 direct comparisons and2,089 native-placement
bytes pass. Five imports close and two local shared helpers become explicit,
leaving84 imports. The earlier attributable FlashDB/FAL chain remains available
below these product adapters; no upstream implementation is inferred for the
local cache algorithm. Source owns473 cold-zero prefix bytes only. Native
averaging row5 aliases the stress prefix first8 bytes at20016670; that shared
ownership must be retained when implementing the helper. Hour/average/logging
remain fixtures here; source consumer/coupled helper composition, complete
contexts, original compiler/layout and whole-image equality remain open.

Local averaging/hour helpers now compile in`native-health-average`. These are
owner-authorized native reconstructions, with no inferred vendor attribution.
35,151 direct and5,952 coupled source-storage comparisons pass, including four
FP rounding modes, count/sum wrap and HRV/stress/HRV sequences.242 new native
bytes and2,331 joint bytes match at verification placements. Only40 new cold
bytes are allocated; averaging row5 reuses8 existing stress-prefix bytes. The
native cross-family alias is preserved rather than separated into independent
contexts.82 imports remain. Offset/calendar/logging fixtures, final section
adjacency, full contexts/private histories and whole-image equality remain
explicit. Pinned FlashDB/FAL and existing calendar reconstruction remain separate
provider provenance; these tests do not establish a new upstream source match.

Calendar providers now have native frame-preserving source in
`native-calendar-frames`. Existing owner-authorized calendar reconstruction,
32-byte state,36-byte fallback and24-byte forward month table remain the sole
configuration owners. No new third-party match is claimed: old-newlib behavioral
similarity is not attributable exact source.89,407 direct and5,952 composed
checks pass. The source storage/averaging chain now executes offset/calendar/
Unix conversion, preserving wrapping timestamps and native aliased-input
weekday rereads.328 new native frame bytes and2,683 joint source bytes match
at verification placements.82 imports remain. Runtime input updates/logging,
hardware clock binding, final placement/private histories and full image
source/equality gates remain open.

Activity storage5AA14 and bucket5AC74 now compile as owner-authorized local
native reconstruction.88,406 direct and3,744 source-calendar composed checks
pass;550 new and902 joint native-placement bytes match. The existing576-byte
cache and8 metadata/gap bytes are reused, without creating a second state family.
Native12/10/10 packed counter wrapping and whole-delta start-bucket deposit are
preserved, including aliases that observe sequential word stores. Calendar and
bucket calculations execute in source; controlled input changes/logging remain
fixtures.81 imports remain. No upstream attribution is inferred for these local
product algorithms; pinned SDK/FlashDB and existing calendar provenance stay
separate. Caller/runtime initialization, private histories, compiler/layout and
whole-image equality remain gated.

Native time-update/flag services and backend snapshot now compile in
`native-time-update`. These are owner-authorized local calendar/backend adapters,
not newly attributed third-party code.17,411 comparisons and192 native-placement
bytes pass while reusing56 existing state/registration bytes. Two imports close,
leaving79. Native bitmask/XOR flag behavior, wide offset comparison, fresh backend
snapshot/context and nonzero-result cache handling are preserved. Backend
callbacks/memclear are fixtures; actual hardware/caller composition, private
histories, final compiler/layout and whole-image equality remain open.

`native-event-multicast` compiles the local product subscriber multicast body
8B028.202 symbolic instruction bytes and10 padding/literal bytes reproduce212
native verification bytes, independently bound by REA/Ghidra12.1.4.4,550
comparisons cover cache/copy behavior, callback traversal mutation, all four-node
combinations of disabled/local/two remote/unknown routes, allocation failures,
queue result independence and length truncation around65536. No hardening is
substituted for native behavior. Providers and callbacks remain fixtures.
One import closes; five explicit dependencies are exposed (lock/unlock, current
thread, roots and routes), leaving83 main imports. Root extent/initialization,
route symbolic task ownership, actual provider/caller composition, faults,
private histories, compiler/final placement and whole-image equality remain
open. No new RAM owner or hardware operation is introduced.

`native-subscriber-sync` adds local mutex lock5DCB0/unlock5DCD4 wrappers and
current-thread thunk7D814, reusing existing upstream CMSIS mutex and FreeRTOS
current-task providers.13,824 comparisons pass with independent callback/state
oracles: creation failure still passesNULL to acquire, created handles replace
creation callback state changes, acquire/release mutations persist, tail returns
and arbitrary full-word results are retained. Providers remain fixtures here.
46 code bytes plus literals/padding and the typed mutex attribute/name reproduce
88 ROM verification bytes; REA/Ghidra independently authenticates all five spans.
The4-byte handle at20006794 is initially zero in authenticated decompressed data;
the80-byte static mutex control at2001571C lies within native zero-init range.
These84 RAM bytes have typed source owners, with final scatter/placement gated.
Three imports close, leaving80. Subscriber root/route ownership, actual provider
and multicast composition, private histories, compiler/layout and whole-image
source/byte equality remain open. No new upstream attribution is inferred for
the local wrappers; CMSIS/FreeRTOS provenance stays with their existing providers.

`native-subscriber-registration` compiles local registration8AF8C and owns the
five pointer roots at20015708 (20 cold-zero RAM bytes) and two typed stride-8
route records at99BA8. The roots end at the already owned mutex control block;
registration's unsigned index<5 check establishes the bounded table. Multicast
still performs unchecked indexing; no new guard is introduced. Route pointers
reference the existing sensor/system task thread fields symbolically. Two
configuration imports close, leaving78; no new provider import is exposed.

4,800 direct comparisons include984 native allocation faults, duplicate callback
rejection, default sensor context, all valid/invalid index cases in the test set,
lock-driven root replacement and heap-callback list mutations. Native BASEPRI64
and invalid store on allocation failure are retained. A further2,430 workflows
execute actual source registration -> multicast and local mutex/current-thread
wrappers with independently checked lists/cache/inline callbacks/route masks.
These workflows include9,720 registrations and2,430 multicasts. Heap, memmove,
CMSIS, publish and current-task providers remain fixtures.172 new and472 joint
ROM bytes reproduce native verification placements. Source state/configuration
is typed; full scatter integration, arbitrary-index/fault histories, actual
provider/runtime scheduling, original compiler/final placement and whole-image
source/byte equality remain unresolved. No new upstream origin is inferred for
these product-specific algorithms; existing CMSIS/FreeRTOS source is reused.

`native-subscriber-consume` compiles packet consumer8B0FC (58 instruction bytes
and2 padding bytes,60 native verification bytes; REA/Ghidra independently bound).
It uses no new RAM owner and closes one import, leaving77. The leading packet
word is destructively advanced through fresh node.next loads. Callbacks receive
payload+6 and r1=callback function address; the packet length is not a traversal
bound. No conventional payload/length callback ABI is substituted.

27,651 direct comparisons include7,254 faults from invalid context pointers and
callback-mutated packet heads. Disabled callbacks, local/remote thread matches,
lock-driven head replacement, callback-driven link/head changes, unused packet
lengths and raw unlock results are checked against an independent traversal
oracle. A separate2,430 composed workflow receipt executes actual source
registration, multicast, sync wrappers and consumer with independent list/cache/
callback/routing checks. Nine spans reproduce532 native ROM bytes. Captured
publish packets are copied to emulate remote delivery; this is not source queue
or scheduling execution. Heap, memmove, CMSIS, publish, current-task and product
callbacks remain fixtures. Existing raw dispatcher ABI discrepancies are not
closed by these local checks. Malformed/cyclic/private histories, full provider
composition, compiler/final layout and whole-image source/byte identity remain
open. This is local product reconstruction using existing source CMSIS/FreeRTOS
providers; no new third-party attribution or hardware proof is claimed.

`native-health-daily-fixture` compiles the diagnostic daily-cache generator8B378
and temperature accessor5BE5C.786 instruction bytes plus typed inline strings,
literals and padding reproduce1,192 native verification bytes, independently
bound by REA/Ghidra. The frozen function's noncontiguous aggregate range includes
notification tails; three remain explicit imports. One import closes and three
are exposed, leaving79. The previously compiled native PRNG is selected from its
source object and linked, with no duplicate state owner; its initial seed/startup
ownership remains open. The28-record native logging prefix is represented by
__start_log_const_data+224, preserving the wider graph's shared stop symbol.

13,568 comparisons include13,312 fixture invocations and256 actual temperature
accessor checks. An independent oracle checks signed PRNG remainders (including
negative controlled provider returns), wrapped unsigned timestamps/hour ranges,
low-byte/clamped bucket indices, first-bucket metadata and later overlapping
bucket writes. Null/invalid input types, all eight log modes, missing caches and
partial prior writes are covered. Saved r0-r3 slots are reused for logging and
cache pointers; native returns and tail notification arguments retain those
writes instead of restoring conventional input values. Time/log/cache/PRNG and
notification execution remain fixtures in this receipt. No full cache extent
or extra RAM ownership is claimed; native writes can exceed24 buckets. Actual
provider/caller composition, initial PRNG state, full log/configuration layout,
malformed/private histories, original compiler/final placement and whole-image
source/byte equality remain open. These are local diagnostic product algorithms;
no new third-party origin is inferred or hardware operation performed.

`native-health-daily-logging` compiles three daily-cache diagnostic tails8D40C,
8E3F8 and8E560 (previous imports named notify; they log, not publish packets).
562 instruction bytes plus typed inline text/literals/padding reproduce912
native verification bytes, independently bound by REA/Ghidra. All three imports
close, leaving76; no new RAM owner or dependency is introduced. Existing source
logging providers and the symbolic28-record log prefix are reused.

7,104 direct comparisons independently check latest-value and24 hourly rows,
min/average/max argument order, temperature+250 display conversion, all encoded
byte values in controlled cache patterns, null caches, changing log modes and
fresh cache reads after mode-provider mutations. Native saved r1-r3 slots are
reused as outgoing stack arguments; their resulting values and the raw return
(mode shifted left30 or logger return) are retained. A further576 composed
comparisons execute the actual daily fixture and three logging tails together;
five spans reproduce2,104 joint ROM bytes. Cache, time, random, mode and log
providers remain fixtures in composition; direct temperature accessor checks
belong to the preceding fixture receipt, not this composed receipt. The earlier
scope-label receipt/driver are preserved under pre-composition-scope-label.
Actual provider/runtime execution, cache extents, PRNG initialization, log/config
layout, malformed/private histories, original compiler/final placement and
whole-image source/byte equality remain open. These are local diagnostic product
algorithms using existing source logging providers; no new upstream attribution
or hardware proof is inferred.

`native-health-service-wrappers` compiles seven bodies: sleep status logger8E154,
sleep sync guard8E1E0, SpO2/temperature state bridges8E274/8E552, no-op callback
8E55C and state publication helpers8A87E/8A896.208 instruction bytes plus typed
text/literals/padding reproduce354 native verification bytes, independently
bound by REA/Ghidra. Five imports close and backend5B6F4 is exposed explicitly,
leaving72. No new RAM owner is introduced; existing logging/publish providers
and the symbolic28-record logging prefix are reused.

18,656 comparisons independently check all low-byte state values and wide-word
variants, bridge constants, dynamic logging modes, raw returns, null/nonzero
pointer/length guards and direct backend argument forwarding. Source bridges
execute actual source publish helpers; their one-byte payload points into the
saved argument stack word. Controlled publisher mutations affect the word later
popped into r3, preserving native behavior. No-op callbacks preserve registers.
Mode/log/publish/sleep-backend execution remains fixture-backed; native address
bindings establish verification placement only. Actual provider/caller/runtime
composition, backend input semantics, malformed/private histories, full section
configuration, original compiler/final layout and whole-image source/byte
equality remain open. These are owner-authorized local product adapters using
existing source providers; no new third-party attribution or hardware proof is
inferred.

`native-sleep-sync-status` compiles backend5B6F4 and gives the authenticated
12-byte zero-initialized context prefix at200067B4 a typed source owner. Full
context and runtime callback-table ownership remain open.228 instruction bytes
plus typed inline strings/literals reproduce412 native verification bytes,
independently bound by REA/Ghidra. One import closes, leaving71; no new direct
import is exposed. No physical storage operation occurs.

34,912 comparisons split equally between direct backend and actual source guard
wrapper -> backend execution. Both objects reproduce766 joint ROM verification
bytes. Independent record/partial-read/marker oracles cover low8(length/12)
truncation (including255/0 wrap), ignored trailing bytes and read returns,
24-byte scratch cleared only once, retained unwritten header words, fresh input
comparisons after callback mutations, fresh read/write ops lookup, captured
address+20 writes and retained/callback-mutated11223344 marker values. Nonzero
write results log failures and continue. Mode/log values and packet-address
reloads match the native contracts. Read/write callbacks, memclear and logs are
fixtures; their invocations establish emulator contracts, not hardware effects.
Full context/registration, actual I/O/provider composition, malformed/private
histories, scatter integration, original compiler/final layout and whole-image
source/byte equality remain open. This is a local product storage adapter; no
new upstream attribution is inferred.

`native-sleep-record` compiles storage5B890, event wrapper8DC94, erase-all5B2F8,
sector count8FE14 and erase thunk8DD88.482 instruction bytes plus typed inline
text/literals reproduce924 native verification bytes, independently bound by
REA/Ghidra. Two event imports close and three sector allocator/writer providers
are explicitly exposed, leaving72. The existing12-byte sleep context prefix is
reused; no new state owner or upstream attribution is introduced.

17,429 comparisons independently check initialization bytes, maximum3888-byte
size and allowed zero-length requests, null inputs, at most two writes, raw
UINT32_MAX fallback selection, low8 writer sector ids and full-word log ids.
Actual event -> store -> erase-all -> sector-count bodies execute together.
Provider mutations demonstrate no recheck of initialization/length on retry,
and fresh region base/ops lookup for each erase. Count is low8(size>>12), with
all256 count values and wrap tested. The event wrapper retains low16(u16 size
atpayload+30 +32), and success calls throttle withkind6. Select/fallback/write,
indirect erase, logging and throttle are fixtures;266,616 recorded erase calls
are emulator fixture observations across both sides, not storage operations.
Actual sector provider/runtime registration, metadata/ops ownership, malformed/
private histories, original compiler/final placement and whole-image source/
byte equality remain open. No physical firmware or storage writes occur.

`native-sleep-sector-select` compiles free-selector8FE28 and oldest-sector
fallback8FC6C.346 instruction bytes plus typed inline literals/text reproduce536
native verification bytes, independently bound by REA/Ghidra. Two imports close,
leaving70; record writer8FE98 remains explicit. Existing source sector count and
sleep context prefix are reused, with no new RAM or third-party attribution.

The independent header oracle checks erased-word and magic qualification,
retained partial16-byte reads, ignored read returns, strict unsigned minimum
selection with first-tie retention, no-candidate default0 and signed-byte return
values. Fallback rereads live count before clamping, always erases (even count0),
and reloads current metadata for post-erase logs. Controlled callback mutations
replace region/ops during scanning, shrink count and change base after erase.
All256 count values and negative signed-byte sector results are exercised. The
source count helper executes; three spans reproduce556 joint ROM bytes. Read,
erase, log-mode and logging providers remain fixtures; no storage operation is
performed. Record-writer/caller/provider composition, full runtime metadata/ops
ownership, malformed/private histories, original compiler/final layout and
whole-image source/byte equality remain unresolved.

The selector receipt passes25,712 comparisons (12,856 each selector/fallback),
including4,374,256 fixture read observations across both native/source sides.
These counts are emulator evidence, not storage or runtime deployment proof.

`native-sleep-sector-write` compiles the entire contiguous writer8FE98..90093,
including success code beyond the frozen366-byte aggregate function range.
The corpus/ledger remain unchanged; new contracts describe the native span
explicitly.508 instruction bytes, inline typed strings/literals and69-byte
external success text reproduce913 native verification bytes, independently
bound by REA/Ghidra. Writer import closes and finalizer901E4 is exposed, leaving
70; no state owner is added. Existing source CRC/logging providers stay linked.

5,760 direct comparisons independently check eight-slot scanning, retained
partial24-byte reads, low16 aligned length, unsigned wrapped capacity, data and
20-byte metadata serialization, preserved header fields, low16 CRC placement,
post-data-write payload loads and fresh callback-table selection after mutations.
I/O callbacks use0 for success. Capacity failure invokes finalizer then returns0
regardless of its result; successful slot7 returns its raw result, earlier slots
return1. Exhausted slots and I/O errors return0. Writes/CRC/memclear/log/finalizer
are emulator fixtures; no storage operation occurs. Actual record/allocator/
writer/finalizer/provider composition, runtime context, malformed/private
histories, original compiler/final layout and whole-image source/byte equality
remain open. This is a local product storage algorithm; no new upstream origin
or hardware proof is inferred.

`native-sleep-sector-finalize` compiles901E4:192 instruction bytes plus typed
inline literals/text reproduce292 native verification bytes, independently
bound by REA/Ghidra. One import closes, leaving69; no new state owner or upstream
attribution is introduced. Existing source sector count and sleep context are
reused.

18,432 direct checks independently verify strict unsigned minimum header word2,
all-erased/no-sector default0 then increment, retained partial16-byte reads,
ignored read returns, captured target address despite metadata changes, captured
initial count and fresh I/O callbacks. The16-byte final header retains magic
CCFFAABB/66889977, counter and zero flag;0 write result becomes boolean1. All256
count values, counter boundaryFFFFFFFE->FFFFFFFF and callback table mutations
are covered. A further176 workflows execute actual writer -> finalizer -> count
with independent slot/header/capacity oracles. Four spans reproduce1,225 joint
ROM bytes. Capacity failure still returns0 after finalization; slot7 completion
returns actual finalizer success/failure. I/O, memclear, CRC, mode and logging
remain fixtures. Full recorder/allocator/writer/finalizer chain, runtime metadata/
ops ownership, malformed/private histories, original compiler/final layout and
whole-image source/byte equality remain open. No physical storage writes occur.

`native-sleep-storage-chain` adds a bounded full local composition receipt rather
than another body replacement. Actual source event/record/select/fallback/write/
finalize/erase/count and the already compiled C checksum provider execute in
1,152 workflows with12,384 repeated record comparisons. An independent bitwise
CRC and record/sector/image model checks every read/write/erase/log operation,
return and resulting image after each append. Cases span1..3 sectors, records
of32/64/512/3888 bytes,1/8/9/25 appends, log modes0/7 and no-error/first-data/
two-data/first-header/first-commit/first-erase failure plans. Main imports remain69.

2,665 local storage ROM bytes and1,536 generated checksum table bytes reproduce
native verification placement. Source objects, linked proof ELF/layout and test
driver are hash-bound. The source CRC text is516 bytes and uses an isolated
native-entry placement that overlaps unused native CRC32/hash code; it is not
whole-image layout or instruction equality proof. Earlier passing driver and
receipt are retained under pre-proof-artifact before adding the ELF binding.
The compiled context prefix is reused with controlled initialization inputs.
Full reads, assignment writes and erase over a mutable image are I/O fixtures,
not physical flash semantics or operations. Memclear/mode/log/throttle remain
fixtures; actual CRC source executes, and private stack/raw scratch identity is
not asserted across different CRC implementations. Runtime metadata/ops binding,
hardware/provider integration, malformed/unbounded histories, final compiler/
scatter/link placement and whole-image source/byte equality remain unresolved.
No new upstream attribution, RAM owner, firmware write or commit is introduced.

`native-sleep-report` compiles handler8DD90, including four diagnostic field
groups, unsigned3600-second duration guard, event2000 publication and storage
fallback.434 instruction bytes plus typed inline/external text/literals reproduce
1,029 native verification bytes, independently bound by REA/Ghidra. The initial
broader REA read is retained separately; the final contract binds the precise
964-byte body/data span and65-byte external string. One import closes, leaving68.

9,458 direct comparisons include two native memory faults, fresh payload fields
after mode callbacks, saved r1-r3 stack argument reuse, duration/wrap boundaries,
low16(u16 stages+32) publication length and raw publish/fallback results. A further
864 full-chain workflows compare4,320 reports against an independent image/error
model. Actual handler -> storage event/record/select/fallback/write/finalize/
erase/count and compiled C CRC execute. Cases cross3599/3600 seconds, publish
acceptance/failure, repeated appends and six I/O error plans.3,694 storage/report
bytes and1,536 generated checksum table bytes match native verification spans.
The linked proof ELF/layout are hash-bound. Publish/image I/O/memclear/mode/log/
throttle remain fixtures, not queue delivery or physical storage. The isolated
source CRC placement overlaps unused native CRC32/hash code; it does not prove
final placement or raw private histories. Runtime binding, provider/hardware
integration, original compiler/scatter layout and whole-image source/byte
equality remain unresolved. No new state owner, upstream attribution or physical
firmware operation is introduced.

`native-health-latest-samples` compiles six HR/SpO2/HRV packed and public getters,
with216 instruction bytes and230 authenticated ROM bytes. REA/Ghidra byte
receipts bind the recovered spans.67,176 direct comparisons cover all65,536
HRV sample values, byte values, null/zero/alias cases and sequential copy effects.
SpO2 clears only its sample byte and timestamp; HR and HRV clear the leading word.
864 composed workflows execute actual storage and getters over repeated updates,
checking1,446 native bytes against independent cache/sample models.

The latest graph aliases the three storage prefixes to their existing full cache
owners, reusing328 bytes and removing313 redundant backing bytes. Other allocated
sections and inherited function bytes are preserved; no new RAM is allocated.
68 main imports remain. Hour/average/mode/log providers remain fixtures in this
composition. Final compiler/layout, full runtime/private histories, hardware and
whole-image byte equality remain gated. This local recovery adds no upstream
origin claim; pinned dependency attribution and update routes remain unchanged.

`native-health-get-dispatch` compiles the health GET router8B8E8.400 instruction
bytes, an8-byte symbolic TBB table and typed strings/literals reproduce516 ROM
bytes; a28-byte uint32 template reproduces99BC8. REA/Ghidra receipts authenticate
both spans. Existing last-timestamp state is reused with no new RAM.4,320 direct
fixture comparisons check module/type routing, native SpO2 range70..100,
packet layouts, logging modes, callback command mutations and fresh request IDs.
The complete source/native register and stack observations match for these cases.

One event-service import closes and three encoder bodies become explicit,
leaving70 main imports. All providers are fixtures in these direct checks;
actual getter/offset/timestamp/notification composition remains a separate gate.
Final compiler/scatter placement, full private histories, hardware and whole-image
byte equality remain unresolved. This local router has no new upstream origin
claim. Existing dependency pins and attributable update routes remain in force.

`native-health-get-encoders` compiles HR/HRV/SpO2 reply encoders83930/83972/83C20
and shared sample sender82EF4, totaling280 authenticated instruction bytes.
REA/Ghidra receipts bind each body.9,000 direct/nested comparisons check native
headers, request truncation, flag combination, null payload replies, raw provider
results, exact invalid-handle65535 guard and preserved frames. HRV sends9 bytes;
HR and SpO2 send8. Actual compiled sample sender executes beneath the encoders.
Three imports close with no new imports or RAM owners;67 remain in the main graph.

Phone handle, flag and response providers are fixtures in this stage. End-to-end
dispatcher/getter/encoder/protocol composition, final compiler/scatter placement,
full private histories, hardware and whole-image equality remain gated. These
local product wrappers add no upstream origin claim; their existing protocol
providers and established dependency pins remain the integration route.

`native-health-get-chain` verifies actual dispatcher -> public/packed getters ->
HR/HRV/SpO2 encoders -> shared sample sender over1,296 GET workflows. An independent
packet/header/result oracle covers zero/truncated samples, SpO2 range boundaries,
offset truncation, handle65535 rejection, request-ID mutation before capture and
later phone callback mutation after capture. All three full caches remain intact.
1,054 ROM bytes match the native image;328 existing cache bytes share their single
owners. The persisted proof ELF, layout, source objects and driver are hash-bound.
An initial receipt/driver is retained under pre-cache-oracle before strengthening
the independent unchanged-cache check. Main imports remain67.

Time/offset/phone/log/flag/response providers remain fixtures; this does not prove
transport delivery or notification branches. Full raw/private histories, final
compiler/scatter placement, hardware and whole-image byte equality remain gated.
No new upstream attribution, state owner or firmware operation is introduced.

`native-health-init` compiles HR initialization8D380 and byte event helper8A866,
with92 instruction bytes and164 authenticated ROM bytes including typed diagnostic
strings/literals. REA/Ghidra receipts bind both spans.3,824 direct/nested cases
cover changing mode results, independent log-branch decisions, all256 low-byte
values plus high-word aliases, raw publish results and callback writes to the
saved argument slot later popped into r3. The service executes the actual helper
and publishes event1001 with one-byte value1. One import closes;66 remain, with
no new imports or RAM owners. Mode/log/publish providers remain fixtures; queue
delivery, runtime integration, full private histories, final compiler/scatter
layout, hardware and whole-image equality remain gated. No new upstream origin
claim or physical firmware operation is introduced.

`native-charge-notification` compiles event service838E0 and an eight-byte typed
read-only template at9A44C.76 instruction bytes plus the literal/template reproduce
88 authenticated ROM bytes, bound by REA/Ghidra receipts.27,972 direct comparisons
cover all256 charge bytes, high-word truncation, arbitrary nonzero active/full
results, full-over-active precedence, seven-byte payload, callback mutation of
that payload and raw protocol results. The source reuses already compiled state/
phone/protocol providers in the main graph; one import closes, leaving65. No RAM
owner or new provider import is introduced.

Those providers remain fixtures in direct checks; actual provider composition,
transport delivery, full private histories, final compiler/scatter placement,
hardware and whole-image equality remain gated. The local wrapper adds no
upstream origin claim; existing protocol/dependency update routes are retained.

`native-record-update` compiles validator6C640 and update service6C66C,102
instruction bytes and104 authenticated ROM bytes. REA/Ghidra receipts bind both
spans.1,540 direct/nested comparisons check every byte value in each validated
field, cross-boundary combinations, null/alias pointers, comparison returns and
callback mutation between persistence and apply. The validator accepts field0
11..99, field1 0..1, field2 101..219 and field3 31..149. The wrapper compares all
12 bytes, persists only on nonzero compare, then applies fresh data without
revalidation. Native null-path raw return values and frames are retained.

The main graph selects the already authenticated C memcmp provider from its
existing compiled unit. One event-service import closes; persistence73604 and
apply6C53C become explicit imports, leaving66. No RAM owner is added. Memcmp/
persist/apply remain fixtures in these direct checks; actual provider composition,
persistence/apply bodies, state ownership, final compiler/scatter placement,
private histories, hardware and whole-image equality remain gated. Export state
beyond the previously owned status cells remains unresolved. No speculative
third-party attribution or physical firmware operation is introduced.

`native-record-providers` compiles apply6C53C and persist73604.180 instruction
bytes plus typed strings/literals reproduce308 authenticated ROM bytes bound by
REA/Ghidra receipts. Both reuse existing owners: status byte20006DA0 and health
settings KV handle20007DF0.8,291 comparisons check per-field thresholds (>2 for
field0, any field1 change, >9 for fields2/3), low-bit status gating, logging,
null raw returns, read-result independence, fresh handle/source after callbacks,
partial reads and sequential three-word copies including stack aliases. An alias
callback can overwrite a saved register word; the independent frame oracle retains
that native effect. No new RAM owner is allocated.

Two imports close; reinitialization4C37C becomes explicit, leaving65. Mode/log/
reinitialize/KV providers remain fixtures in direct checks. Actual composed
wrapper/provider/KV execution, reinitialize body, final compiler/scatter layout,
full private histories, hardware and whole-image equality remain gated. No new
third-party origin claim or physical firmware operation is introduced.

`native-record-chain` executes actual validator/update/persist/apply and compiled
C memcmp over19,776 workflows. Independent validation, comparison, persistence
payload and threshold oracles cover identical records, invalid fields, changes
across all12 bytes, read callbacks mutating records/handles, partial reads, low-bit
status gating and raw boundary results. The proof binds412 native-span bytes;
408 are byte-identical and four at6C68A relocate the call to the28-byte compiled
C memcmp at an isolated verification address. This is explicitly not complete
instruction equality. Proof ELF/layout, source objects and driver are hash-bound.
Main imports remain65. KV/mode/log/reinitialize providers remain fixtures, and
full raw/private histories are not compared across different memcmp bodies.

The reinitializer's crash payload already has a source owner; its separate
context pointer and algorithm flag still need ownership/integration evidence.
Those gates, final compiler/scatter layout, hardware and whole-image equality
remain unresolved. No new upstream claim, state owner or firmware operation is
introduced by this composition.
