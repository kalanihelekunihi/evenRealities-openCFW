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
