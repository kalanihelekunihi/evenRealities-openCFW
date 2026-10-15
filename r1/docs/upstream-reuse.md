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
