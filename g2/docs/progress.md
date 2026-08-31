# openCFW reconstruction progress

Status date: 2026-08-30
Compatibility target: official G2 `s200_v2.2.6.10`

This is the concise status index for dependency provenance, byte ownership,
and controller-segment reconstruction. Detailed evidence remains in
[`upstream-inventory.md`](upstream-inventory.md),
[`source-coverage.md`](source-coverage.md), and
[`memory-map.md`](memory-map.md).
The current third-party identity and functional-gap priority is summarized in
[`research/third-party-utility-gap-priority.md`](research/third-party-utility-gap-priority.md).

## Current assessed boundary

The checked
[`assessment-data.json`](reports/openCFW-completion-2026-08-28/assessment-data.json)
is the current authority. It authenticates the assessment inputs and closes the
canonical Apple package at 4,677,796 payload bytes plus a 944-byte EVENOTA
envelope:

| Production source | Generated/reconstructible | Candidate, not routed | Typed retained/external | Unclassified | Package |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 424,703 | 426,474 | 30,636 | 3,795,983 | 0 | 4,678,740 |

The 3,826,619 release-blocking bytes remain classified rather than opaque.
`source_complete=false` and `release_authorized=false`; redistribution
authority is unresolved for all six binary-bearing components. Hardware
validation is blocked by unavailable physical evidence and the assessment records
`hardware_operations=[]`. The public deliverable is therefore the verified
source-only community archive for the hybrid source-overlay workflow. It
contains no official payload, retained firmware byte, compiled overlay, or
locally hydrated/built firmware package.

| Component | Source | Generated | Candidate | Retained/external | Unclassified | Release-blocking |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Apollo main | 394,928 | 409,348 | 0 | 3,081,392 | 0 | 3,081,392 |
| Apollo bootloader | 29,775 | 16,490 | 0 | 117,575 | 0 | 117,575 |
| GX8002 codec/DSP | 0 | 92 | 0 | 326,000 | 0 | 326,000 |
| EM9305 BLE | 0 | 0 | 1,240 | 210,708 | 0 | 211,948 |
| PSoC Touch | 0 | 512 | 14,510 | 19,442 | 0 | 33,952 |
| STM32 charging case | 0 | 32 | 14,886 | 40,866 | 0 | 55,752 |

The Touch candidate total is partitioned by six mixed-license, semantic-only
rows in
[`g2-touch-final-source-candidate-provenance.tsv`](../tools/manifests/g2-touch-final-source-candidate-provenance.tsv).
Every row records `production_elf_ownership=false`; none promotes stock bytes
or the nonproduction source image into production-source coverage. The current
source-license audit reports 778 distributable source files and zero errors,
and the project-wide MIT/upstream normalization census covers 906 targets.

The persisted
[`em9305-final-source-readiness.tsv`](../tools/manifests/em9305-final-source-readiness.tsv)
accounts for all 175 EM9305 residual spans / 33,658 bytes. Its final readiness
partition is 23 spans / 1,240 bytes of concrete but unrouted source, 25 /
8,348 bytes of typed unsupported external boundary, and 127 / 24,070 bytes of
unavailable proprietary controller code, with zero unclassified spans or
bytes. This closes residual classification only: EM9305 remains
`source_complete=false`, stock-retained, and release-blocking.

The EM9305 deployment wrapper now parses and deterministically rebuilds the
authenticated 211,948-byte record package: four canonical records, 124 bytes
of metadata, 211,824 payload bytes, and 29 erase-sector IDs. The byte-exact
round trip and hostile-input tests close the container-generation gap only.
All four production record sources, placement/redirect routing, and the
redistributable controller record remain unavailable, so the persisted audit
keeps `source_image_complete=false`, `production_routed=false`, and hardware
validation blocked by unavailable physical evidence.

## Latest milestone: Apollo-main source admissions expand without routing overclaim

The selected largest component remains Apollo main. Its canonical hybrid
source-overlay package builds and verifies at 4,678,740 bytes with SHA-256
`d569793138c6bc2ee456536daee59dcef0bb6051034ed966f7144083790a777a`.
That proves a complete build artifact, not a complete maintained-source
implementation: the checked disjoint mask still contains 3,081,392
release-blocking Apollo bytes.

Nine FreeType 2.9.1 source boundaries are now isolated and target-compilable.
CFF now has a complete 101-function / 16,718-callable-byte map (the older
47-function / 12,062-byte candidate remains an authenticated strict subset),
complete base for 182 /
20,442 (the older base candidate is only 90 / 9,736),
SFNT for 136 / 29,258, PSHinter for 79 / 9,188, and PSAux for 199 /
29,750, while PSNames adds 11 / 1,132 and the three-class smooth renderer
family adds 29 / 4,310. Autofit adds 87 functions / 23,612 callable bytes
inside its 23,704-byte authenticated envelope, and the complete TrueType map
adds 265 / 41,728 inside a 42,204-byte envelope. The pre-existing TrueType
candidate remains correctly described as a narrower 248-function / 38,828-byte
reachable graph. The complete CFF, SFNT, PSHinter, PSAux, PSNames, smooth,
autofit, and TrueType maps have zero unresolved callable bytes; base is likewise a
complete 20,676-byte physical map with only 234 classified non-callable bytes.
Their remaining physical complements are only authenticated literals, function
pointers, foreign callables, strings, and padding.
The new `freetype-*-source-closure` Make gates pin the upstream inventory,
compile for Cortex-M55, exercise host behavior where a maintained adapter
exists, and keep placement and production routing false.
The CFF route census additionally authenticates the retained
`FT_Init_FreeType` → default-module → CFF-class chain and its production-routed
LVGL font-manager consumer, while proving that no source-built CFF translation
unit, class registration, policy-adapter placement, or direct policy callsite
has yet acquired production ownership.
The CFF link/finalizer census closes all 45 imports using 35 exact retained
bindings and ten maintained providers, resolves the Apple/Linux objects to
zero undefined symbols and zero output relocations, and produces 26,794- /
26,726-byte payloads with no static RAM. It also authenticates the sole guarded
module-class pointer slot at `0x0073EF00`. The nominal 71,100-byte interval
`[0x007ECA44,0x007FE000)` is not free space: 477 current canonical flash-plan
regions occupy 66,678 bytes, leaving only 4,422. The final payloads are
therefore short by 22,372 / 22,304 bytes, so neither the payload nor the class
pointer patch is emitted and production routing remains false.
The package-backed capacity solver proves this is not merely an append-tail
estimate: all 477 occupants match their plan, artifact, component slice, and
package bytes. Even an intentionally optimistic upper bound that counts the
entire 17,284-byte unique stock-CFF envelope/tables/callback set, all 302 bytes
of alignment, and the 4,422-byte tail supplies only 22,008 bytes, still short
by 4,786 / 4,718 bytes. A contiguous placement would instead have to displace
171 live rows / 24,154 occupied bytes beginning with the IAR output closure and
including the ANCC dispatcher and Cordio security tail. No such alternate
placement is authenticated, so the solver emits no firmware or route patch.
The whole-address extension independently verifies all 6,120 application rows
and 330 bootloader rows against their artifacts and pinned package. The
application interval `[0x00438000,0x007FCEBA)` has zero internal gaps; the
separate 5,920-byte bootloader-partition headroom has neither application
placement authority nor cross-entry update atomicity. A legal optimistic
scatter pool is therefore only 21,706 bytes versus 26,780 / 26,712 minimum
loadable Apple/Linux section bytes, leaving 5,074 / 5,006 bytes. All relocation
encodings are range-compatible, but ownership and capacity are not, so the
solver correctly declines to invent an exact scatter link.
An auditable whole-translation-unit `-Oz` experiment now closes that byte-count
threshold without source edits, feature changes, LTO, or section-GC dependence:
the Apple/Linux loadable closures are 20,416 / 20,364 bytes, leaving 1,290 /
1,342 bytes inside the legal upper bound. The complete 101-function map is
accounted as 81 named emitted functions plus 20 functions proven by clang
inline remarks, all 55 address-taken callback targets remain present, and the
sole new `__aeabi_memcpy` call binds to the authenticated current-package
source redirect. An exact dual-profile scatter link now places all 4,918
rodata bytes at `[0x005ABEF8,0x005AD22E)`, divides the atomic text sections
between the remaining stock-CFF envelope and the application tail, and places
the 16-byte unwind index at `[0x007FDEC4,0x007FDED4)`. Both final ELFs close
all 36 bindings, every relocation, all 58 callback words, and the relocated
96-byte driver class without veneers or cross-entry writes; Apple/Linux leave
930 / 990 bytes of two-interval slack. The guarded class-pointer change at
`0x0073EF00` is derived but unapplied. The proof is pinned to an older
root-level package ending at `0x007FCEBA`; the current canonical Apple/Linux
entry-6 payloads end at `0x007ECA44` / `0x007B9F10`. Component integration
must therefore authenticate profile-specific `0xFF` fill through the fixed
tail destination and derive fresh length, CRC, flash-plan, and package
receipts. That canonical integration remains absent, so no route or firmware
image is emitted.

The admitted non-HR liblc3 encoder is production-capable C but still unplaced.
It closes 41 source-attributed functions / 16,128 stock bytes and builds a
101,616-byte aligned specialized closure. Source-owned capacity could
conditionally reclaim 30,676 bytes and leave 172 bytes before the protected
update record. All seven unavoidable moved suffix closures now have strict
contracts (8,910 bytes / 44 relocations), including the repaired 3,508-byte
formatter engine and its relocation-safe self-call. The minimum suffix
contract blocker set is empty. The former 404-byte writable-data gap is now
closed as five immutable pointer tables in an authenticated, 8-byte-aligned
`.lc3_table_rodata` XIP section: all 78 nonzero words have internal
`R_ARM_ABS32` relocations, the other 23 words are null, and retained code has
only six paired MOVW/MOVT load sites. It requires zero runtime-copy bytes and
zero writable RAM. Exact append-hole packing or stable-order relocation
replay is now implemented in the specialized builder through authenticated
post-link flag conversion and a synthetic-address finalizer: all 484 input
relocations (332 text, 74 rodata, 78 table) resolve to zero output
relocations, and the relocated 40,880-byte text, 60,316-byte rodata, and
404-byte table XIP images are checked before emission. Those qualification
addresses and 11 import bindings deliberately carry no stock authority;
authenticated production addresses, the 30,516-byte flash shortfall, and OTA
routing remain fail-closed.
A bounded `service_audio` adapter now closes configuration, ownership,
integrity, aliasing, and error semantics in maintained C on both reviewed
profiles. Its compact state is exactly 2,628 bytes, so all four authenticated
stock slots provide the complete 10,512-byte writable placement with zero
deficit and no additional runtime-writable allocation. The alternating slot
phases expose 2,596- or 2,600-byte aligned encoder storage, while the largest
adapter-admitted real liblc3 state is 2,596 bytes. Production routing still
requires authenticated flash placement. The exact stock-ABI shim now owns the
setup entry at `0x0057A926` and encode entry at `0x0057A940`, authenticates all
four/five whole-image ingress sites and all four fixed contexts, preserves
stock's unconditional setup-reset and encode result geometry, and rejects
unknown contexts, corrupt transitions, and aliases. Its dual-profile route
experiment replays all 515 / 521 relocations and derives the two Thumb-2
veneers, but the complete closure is still 34,084 / 35,204 bytes beyond
authenticated Apple/Linux append headroom. Those targets remain synthetic;
no firmware or entry patch is emitted. A behavior-preserving `-Oz` plus
section-GC build retains all 11 bindings, the five-table XIP policy, and the
complete admitted runtime configuration grid while reducing best-order
Apple/Linux shortfalls to 9,152 / 9,100 bytes. The older 30,676-byte full
repack remains unauthorized because it would move 206 non-strict leaves. The
exact narrower audit moves only the final 84 already-strict leaves (9,174
payload bytes) into seven authenticated stock-slot tails, replays all 288
relocations, closes all 127 exact-start branch ingresses with zero raw-pointer
ingress, and leaves 96 bytes before the update record. Actual LC3 best-order
finalization, the 11 authenticated runtime import addresses, entry routing,
and OTA integration remain absent, so routing stays false.

The authenticated LVGL Ambiq backend covers 11 linked translation units /
170,833 source bytes. A bounded cache-free radius-mask implementation, the two
Nema buffer helpers, an exact five-function Apollo cache/power HAL adapter,
an exact three-function FreeRTOS queue/semaphore adapter, a zero-import
14-function LVGL core-utility provider, a zero-import 11-function stateless
provider, a zero-import five-function memory/AEABI runtime provider, and an
authenticated zero-import five-function musl scalar-math provider (`acosf`,
`atan2f`, `atanf`, `fmod`, `fmodf`), and a four-function LVGL mutex provider
with zero ELF imports and six authenticated fixed scheduler-port calls compile
and link without unresolved Nema, Apollo HAL, `xQueue*`,
area, color-BPP, event-accessor, matrix, array, descriptor, transformed-bounds,
admitted memory/runtime, admitted scalar-math, or admitted mutex symbols. A
second zero-import FPv5-D16 provider now closes `cosf`, `sinf`, `sqrt`, and
`tanf` from the authenticated musl v1.2.5 sources plus their complete hidden
reduction/kernel/table closure: its 13,144-byte target object exports exactly
those four symbols, carries no fixed calls or external relocations, and closes
35 authenticated consumer relocations. A 3,060-byte zero-import LVGL
heap/array provider now closes `lv_malloc`, `lv_malloc_zeroed`, `lv_free`,
`lv_array_deinit`, and `lv_array_push_back` through the three authenticated
source-owned synchronized heap-facade entries. Its ABI probe fixes the 20-byte
ILP32 array layout, its target closure covers 41 authenticated consumer
relocations, and hostile descriptor, capacity, byte, pointer, overlap, and
reallocation-failure cases fail closed. A 1,192-byte single-export lifecycle
provider additionally closes `lv_draw_buf_destroy`: it invokes the
descriptor-owned buffer-free callback before the admitted `lv_free`, and its
3,584-byte heap/lifecycle aggregate has zero undefined symbols. Null,
non-allocated, or missing-handler descriptors fail closed. A conservative
section-GC link roots all 39 externally visible functions from the 15 exact
Ambiq objects and preserves all 96 direct Nema/GPU requirements; it proves the
unreferenced `lv_ambiq_get_glyph` section and its sole private
`utf8_codepoint_size` import absent without inventing UTF-8 behavior. An exact
492-byte `lv_global` OBJECT/BSS provider additionally fixes the authenticated
`0x2006F548` storage address, 0x1EC-byte ABI, and both consumer relocations
without imports. It does not claim live linker collision ownership,
initializer order, or handler contents. A bounded
`lv_freetype_outline_add_event` provider then closes its sole `lv_global`
import against that storage object and stores only the authenticated callback
field, with null context failing closed; its context lifetime, initialization,
concurrency, and global RAM ownership remain unqualified. An exact two-symbol
draw-buffer shape provider now closes `lv_draw_buf_create` and
`lv_draw_buf_reshape` against only the admitted heap/global providers and four
retained-Ambiq-initializer-owned indirect callbacks. Its 2,296-byte target
provider and 4,780-byte heap/global/shape aggregate have zero aggregate
imports, and hostile geometry, callback, allocation, and reshape failures are
sanitizer-clean. The callback contents, initializer order, live heap/global
ownership, and concurrency remain unqualified. The scoped maximal object is
now augmented by an exact-ABI, zero-import `lv_font_get_bitmap_fmt_txt`
provider. Its 4,688-byte target provider and 1,016-byte ABI object preserve
raw, plain 1/2/4/8-bpp, aligned-row, compressed prefilter/no-prefilter, and
repeated/counter RLE behavior; hostile null, stride, capacity, and BPP cases
are ASan/UBSan-clean. Cache flushing remains an explicit caller-owned
`draw_buf->handlers->flush_cache_cb` boundary and safely becomes a no-op when
absent. The scoped maximal object is now 1,368,580 bytes and the atomic
residual is 15 symbols. An exact `lv_vector_for_each_destroy_tasks` provider
then closes against only the admitted `lv_array_deinit` and `lv_free`
exports: its 1,388-byte target provider forms a 3,744-byte aggregate with
zero undefined symbols. Host sanitizer coverage proves unlink-before-callback,
owned/borrowed path and dash-array handling, and exact single-release
accounting while retaining caller-owned list topology, allocation extent, and
callback-mutation preconditions. The scoped maximal object is now 1,369,220
bytes and the atomic residual is 14 symbols, digest
`77f7f1022e2ea9cd79a7c638f9b0daef66903d2689d6d1b3a36d5e5b4e3680cd`.
An exact `lv_draw_create_unit` provider then closes its sole retained Ambiq
consumer against only the admitted `lv_malloc_zeroed` and `lv_global`
providers. Its valid path preserves zeroed allocation, head insertion,
one-based count, and signed index assignment, while undersized extents,
allocation failure, and an unrepresentable next ID fail before mutation. The
aggregate has zero undefined symbols, the scoped maximal object is now
1,369,740 bytes, and the atomic residual is 13 symbols, digest
`d6679431a206de8a8050544138a61b86dfcedbbb2e4721f11ce48db809027032`.
Initialization order, list ownership, concurrency, collision, RAM placement,
and allocation lifetime remain unqualified.
The exact `lv_draw_dispatch_request` branch now preserves the authenticated
two-signal sequence against the same `lv_global.draw_info.sync` pointer: first
a call and then a tail jump, with both results deliberately ignored. Its
`lv_global` import resolves through the admitted storage provider, while
`lv_thread_sync_signal` remains the sole explicit, unadmitted dependency. The
scoped maximal object is 1,370,240 bytes and the atomic residual is 12 symbols,
digest
`2e261ab6a646ad20004b2bd631455ee1955980a73031ee995554880b9e077eca`.
The queue adapter's
27 fixed scheduler/RAM
dependencies remain
enumerated and unrouted. Production still requires the remaining providers,
fixed-call/MMIO review, overlay registration, stack/WCET qualification, and
GNU/IAR policy. Live font,
audio, GPU, cache, power, display, and timing qualification is blocked by the
unavailable authorized physical evidence recorded in
[`hardware-validation-2026-08-30.md`](hardware-validation-2026-08-30.md).

## Historical implementation chronology

Everything below this heading records the sequence of implementation
milestones. Labels such as “latest” and “current” are contemporaneous to those
entries; they do not supersede the assessed boundary above.

## Latest milestone: IAR formatted-input production closure

The complete live formatted-input path is now source-owned C. Eleven new
Cortex-M55 leaves provide the five ARM-EABI binary64 operations required by
the parser, a field-width-bounded decimal/hexadecimal `strtod`, scanset
matching, `vsscanf`/`sscanf`, and the exact IAR soft-PCS ingress adapter. The
sole live 2,778-byte stock scanf core is guarded and redirected to that
adapter. Host behavior tests cover integer lengths/bases, strings, scansets,
suppression, `%n`, decimal/hex/Inf/NaN floating input, and the field-width
edge where an incomplete exponent must remain unconsumed; the same sources
compile freestanding for Thumb. Formatted output and dormant Annex-K
constraint-handler paths remain software work, so the broader IAR
formatted-I/O cluster is not yet complete.

The application overlay is 404,796 bytes and the installed application ends
below the authenticated protected update record at `0x007FE000`. The
4,706,686-byte package rebuild is byte-identical, with 5,863 placed regions,
two already classified unresolved physical destinations, five container-only
regions, and six protected regions. No device was accessed or flashed.

## Prior milestone: Cordio HCI event and driver software closure

The clean-room HCI event decoder now implements all 80 inventoried APIs and
production-routes all 79 linked entries, replacing 6,718 stock bytes with
23,590 compiled Cortex-M55 bytes plus 30 alignment bytes under 52 strict
relocations. The exact two-byte scan-timeout no-op is compiled in place; the
other 78 entries use guarded branches. The adjacent driver implements all 16
APIs and production-routes the nine hardware-independent entries. Its six
radio-controller operations remain explicitly blocked on future-required authorized responsive G2/EM9305 physical evidence, with stock retained for
those live paths.

The fail-closed aggregate [third-party dependency closure audit](research/third-party-dependency-closure-audit.md)
now reconciles 26 families, 25 selected public source commits/baselines, the
130,000-byte retained third-party-path opaque lower bound, zero unclassified
Cordio reusable paths, the complete seven-function / 638-byte private LVGL
display port, and FreeType lifecycle absence evidence. The 26th family is the
DaveGamble cJSON parser shared by service_android_notify.c and
service_whitelist.c, identified to version interval v1.7.9--v1.7.12 and now
admitted as an authenticated pristine MIT snapshot at interval-ceiling tag
v1.7.12 (`3c8935676a97c7c97bf006db8312875b4f292f6c`), production-excluded by
explicit decision. The audit reports zero
bounded third-party functional gaps that are still locally actionable;
residual work requires hardware, unavailable private/proprietary inputs, or
an explicit production-admission decision.

The first-party retained-path frontier is now fully closed: 234 closed /
0 open over all 234 retained paths, covering all 1,230 anchored functions
and all 485,274 anchored body bytes, with 814,534 complete-object body bytes
and 885,418 known physical bytes over 232 closure manifests.

Headless reverse-engineering throughput is now available on the 32-core,
64-thread `lorelei` worker. A version-matched Ghidra 12.1.2/JDK 21 setup and
reproducible benchmark show 2.28x higher throughput for eight independent
decompilation batches and 5.00x for the observed 16-task workstation run.
The tested safe default for independent import/decompile jobs is 16 remote
workers in one SSH command. Apollo main now has a separate 64-chunk lane that
analyzes once, reflink-clones the closed project, and decompiles all 7,370
discovered functions with zero failures. Its measured cold path is about 5.0
minutes; retained-template replay is about 2.4 minutes, and 64 workers beat the
tested 16- and 32-worker points for that workload. Full results,
hashes, caveats, and the fail-closed integration policy are in
[`research/lorelei-re-acceleration-benchmark.md`](research/lorelei-re-acceleration-benchmark.md).
The first production census used that lane to decompile 35 early-island
targets as 16 shards in about 12 seconds. Local Rizin plus a new fail-closed
analyzer separated application/DSP code from ten retained IAR runtime units:
the four memory providers, signed and unsigned 64-bit division cores and
wrappers, VFP `sqrtf`, two errno setters, and the errno-address accessor. All
ten bounded units are now source-recreated and production-integrated.
The same lane has now run the current targeted 16-shard EM9305 ARC manifest:
all isolated projects completed in 18.042--18.299 seconds and returned
hash-manifested artifacts. This is 1.46x faster by mean shard time than the
same manifest with broad auto-analysis, while retaining all bounded
instruction/decompile sections. That
pass recovered the QF/QK hook boundaries and terminal pointer-table xrefs;
GNU ARC decoding, Rizin, and the authenticated SDK oracle remain the acceptance
authorities where the experimental Ghidra ARC extension reports p-code errors.

The Apollo run is mechanical discovery rather than source completion. Equal
byte chunks 0–33 contain all currently discovered functions; chunks 34–63
cover data/resources after `0x00600FAA` and remain in the complete tiling so
missed code is not silently excluded. Upstream attribution, ABI recovery,
boundary repair, and clean source recreation remain the limiting work.

The first whole-corpus ownership pass now authenticates all 357 retained
`s200_ap510b_iar_git` C source paths and 712 raw pointer cells. It maps 314
paths to 1,760 discovered functions: 530 third-party anchors and 1,230
project/first-party anchors, with no cross-root function. The baseline leaves
43 paths without a decompiler-token anchor and 5,610 functions without a
retained-path anchor.
All seven embedded third-party directory families were already inventoried;
no new dependency family was found in the retained `__FILE__` set. These are
triage counts, not byte-ownership percentages. See the
[source-path census](research/apollo-embedded-source-path-census.md).

The parallel Cordio lane now adds a fail-closed function map over the same
authenticated replay: 36 retained translation-unit paths, 32 paths with
anchors, and 114 distinct anchored functions. The normalized map SHA-256 is
`772063dc1841dc33523e68ecca9188923e28efd5cbe6db5a22a36979c41b2623`.
It records function bounds, direct-call topology, small literal constants, and
logger/assert source-line values, while separating 22 generic Packetcraft
candidates from five Ambiq ports and nine Ambiq/application-or-Even paths.
The public r20.05--r20.05c interval remains limited to the previously audited
ATT/DM behavior and unchanged blobs; it is not an exact vendor-tree claim.
No production manifest changed. See the
[Cordio source-path/function map](research/cordio-source-path-function-map.md).

The follow-on aggregate reconciliation supersedes the older 80–85% Cordio
identity estimate for the reusable host-stack surface. All 22 retained public
Packetcraft candidates and all five retained Ambiq ports now map to focused
audits and matching tests. Repository-wide, 67 focused module analyzers match
67 tests and 67 function maps; 69 provenance manifests retain the per-module
r19/r20/R4/AmbiqSuite source-oracle distinctions. No retained reusable path or
focused third-party module remains unclassified. The exact historical mixed
tree remains unobservable, production admission and hardware/controller
validation remain, and nine application/product paths are explicitly
first-party boundary work. See the
[Cordio aggregate closure](research/cordio-aggregate-closure-audit.md).

The parallel discovery-gap lane resolves the baseline 43-path ambiguity more
carefully. Their 46 path-pointer cells have 273 exact-cell, halfword-aligned
Thumb `LDR` decode sites. Independent call/table evidence recovers eight
functions across AgingTest and Cordio WSF timer, raising the reviewed effective
discovery count from the immutable Ghidra baseline of 7,370 to 7,378. The
other 41 paths remain missed-code candidates; zero are confirmed path-only
data. Only the eight witnessed entries are promoted, and none changes
production ownership. See the
[source-path recovery audit](research/apollo-embedded-source-path-recovery.md).

The follow-on WSF timer pass names the complete 536-byte FreeRTOS port cluster,
recovers `WsfTimerInit` as the eighth missed function, closes the 16-byte timer
ABI, queue/handle/tick globals, WSF interrupt-nesting locks, and all external
dispatcher calls, and adds a host-tested clean-room behavioral candidate
covering all eleven functions / 536 code bytes. Its exhaustive
ingress audit closes 53 BL callers and the sole stored callback pointer, with
no other entry/interior branch or pointer consumers. Official Packetcraft
r19.02 is a public semantic oracle for the bool-pointer next-expiration and
expired-service bodies. Official AmbiqSuite 2.5.1 archive SHA-256
`87b03680…` supplies the exact proprietary implementation/source family, and
its 2.5.1-only saved-tick statement is present in stock; minor local
text/config drift remains. Lorelei's public-oracle matrix ran in 0.800405321
seconds; its follow-on eleven-function matrix ran 143 comparisons in
2.448108512 seconds, linked with zero unresolved symbols after 13 explicit
seams, and made 8/11 functions size-exact under bounded configs. Neither
matrix produced a raw or strict-normalized IAR match. Timer-module semantic
identification was 95–98%; the then-current 80–85% aggregate estimate is
superseded by the aggregate closure below. See the
[focused timer audit](research/cordio-wsf-timer-source-recovery.md). The eleven
timer functions are now production-routed: 11 guarded redirects replace all
536 stock body bytes with 632 compiled bytes, 14 alignment bytes, and 29 strict
relocations. The package and flash-plan gates pass; live scheduler/controller
timing is blocked by unavailable physical evidence; future qualification requires authorized responsive hardware.

The adjacent WSF OS/queue pass closes 12 OS functions / 532 bytes and six
linked queue functions / 242 bytes. The stock task is exactly 64 bytes with
ten handlers, ten byte-wide handler masks, its queue at `+0x34`, task mask at
`+0x3C`, and handler count at `+0x3D`. Official AmbiqSuite 2.5.1 supplies the
proprietary implementation family and dispatcher discriminator; later
official Ambiq source corroborates the otherwise identical ten-handler
variant, but the exact G2 definition site is unavailable. Lorelei completed
234 stock-ABI GCC comparisons in 3.521196588 seconds with zero unresolved
closure symbols and no raw/strict-normalized match. All 18 bounded functions
are production-routed as 886 compiled bytes plus 14 alignment bytes under 41
strict relocations. Live ISR/task scheduling, handler ordering, and sleep
behavior remain hardware-deferred. See the [WSF OS/queue audit](research/cordio-wsf-os-queue-source-recovery.md).

The next WSF buffer/message pass closes another ten functions / 556 bytes.
Three buffer functions are bounded over 430 bytes; initialized-SRAM recovery
pins the four pools to `{16×8, 32×4, 64×10, 480×20}`, consuming `0x2930`
of the `0x2940` region at `0x2004FA98`. The exact Ambiq FreeRTOS buffer
implementation family is proprietary and remains an oracle only. All seven
message definitions / 126 bytes instead have an exact Apache-2.0 Packetcraft
r19.02 route. Lorelei completed 78 buffer comparisons and 26 closure links in
3.463 seconds; every link closed, but no raw/strict match occurred. The
warning seam reduced the best aggregate size gap to 34 bytes and Free is
within two bytes. All ten functions are production-routed as 696 compiled
bytes plus 12 alignment bytes under 13 strict relocations. See the
[buffer/message audit](research/cordio-wsf-buffer-message-source-recovery.md).

The WSF assert/trace pass closes two more linked functions / 208 code bytes.
`WsfTrace` has 126 direct callers, a 1,024-byte stack buffer, retained source
path and line 137, and the stock double-format debug path. `WsfAssert` is the
sole overflow target and combines the Ambiq debugger-escape loop with a
downstream EasyLogger hook/reset extension at global `0x2007456C`. Lorelei
completed 26 comparisons and 13 zero-unresolved links in 2.098 seconds; zero
raw/strict matches and the pristine assert source's 118-byte size deficit
independently prove the local augmentation. Both functions are
production-routed as 170 compiled bytes under five strict relocations, while
the proprietary Ambiq files remain oracles only. See the
[assert/trace audit](research/cordio-wsf-assert-trace-source-recovery.md).

The remaining FreeRTOS-port census classifies `wsf_efs.c` and `wsf_math.c` as
unlinked with high confidence. EFS has none of its distinctive six-by-52-byte
file table, four-media callback layout, 12-caller validator, WDXS consumer
topology, strings, or retained paths. Math has neither its xorshift128 seed
quartet nor the combined 11/19/8 shift signature. No stock bytes are assigned
to either module. All 20 EFS bodies nevertheless have an exact Apache-2.0
Packetcraft r19.02 route if future images prove inclusion. The same census
identified linked `wstr.c` as the next bounded WSF target. See the
[EFS/math exclusion audit](research/cordio-wsf-efs-math-exclusion-audit.md).

The linked follow-up closes the two retained `wstr.c` reverse helpers / 118
bytes with 39 plus two direct callers and no callee, pointer, or interior
ingress. Both definitions have an exact Apache-2.0 Packetcraft route from
r19.02 through r20.05c and are production-routed as 286 compiled bytes plus
two alignment bytes. Lorelei's
26-row matrix linked with zero unresolved symbols in 2.153 seconds; its best
common `-O1` lane is ten aggregate bytes from stock, with no raw/strict match.
The WDXS-only `WstrnCpy` is explicitly dead-stripped. See the
[WSF string-helper audit](research/cordio-wstr-source-recovery.md).

The ATT client-supported-features module is now production-routed:
ten linked functions / 4,814 code bytes in `[0x0052C6C0,0x0052DA0C)`, plus
126 bytes of literal/string/data pools. Stock selects Packetcraft
r20.05--r20.05c semantics, while keeping Ambiq-era API names and adding local
connId validation and logger/assert expansion. The 13-byte-observable control
block at `0x20073E04`, three two-byte records, callback/hash offsets, 20 direct
callers, and pointer/ingress closure are exact. `AttsCsfInit` is dead-stripped
and supplied by BSS zeroing. Lorelei's two readiness builds close four provider
seams with zero undefined symbols. Ten guarded redirects now route 502 compiled
Cortex-M55 bytes plus 12 alignment bytes under one strict relocation. Host
tests cover the complete state policy and G2's `connId == 0`
false/`0x0E`/unaware/no-copy/no-op guards; all ten selectors compile
independently. Vendor logging expansion is omitted without changing
state-machine results. Live robust-caching, database-hash, service-changed,
callback, peer, and controller behavior is blocked by unavailable physical evidence; future qualification requires authorized responsive physical evidence. See the
[ATT CSF audit](research/cordio-atts-csf-source-recovery.md).

The next public-host tranche closes the complete linked `smp_db.c` module:
eleven functions / 2,952 code bytes in `[0x00541E34,0x005429F2)`, with 54
bytes of literal/alignment data and two source-only remove APIs dead-stripped.
The Apache definitions are stable from Ambiq/r19 through r20.05c, while stock
event `0x20` independently selects the r20 message ABI. The 256-byte SRAM
control block at `0x200708EC` proves ten 24-byte records versus the upstream
default three, and both the boot and normal runtime SMP configurations are
now distinguished. Lorelei's compact two-profile readiness artifact links
with zero unresolved symbols. Module identification was 95–98%; the
then-current 80–85% aggregate estimate is superseded by the aggregate closure
below, and production ownership was unchanged. See the
[SMP DB audit](research/cordio-smp-db-source-recovery.md).

The adjacent ATT CCC tranche is now complete: all fourteen `atts_ccc.c`
functions / 2,770 code bytes plus 138 bytes of inline/literal data occupy
`[0x0052BB64,0x0052C6C0)`. The exact Apache definitions are stable from
Ambiq/r19 through r20.05c; stock callback event `0x14` selects the r20 ATT
header ABI. The 24-byte control block, three connection-table pointers, six
product CCC settings, 23 direct calls, registered callback, and eight indirect
consumers are closed. Lorelei's two-profile readiness links have zero
unresolved symbols. Fourteen guarded redirects now route 784 compiled
Cortex-M55 bytes plus eight alignment bytes under fourteen strict relocations.
Host tests cover allocation, initialization, read/write/range policy,
change-only callbacks, security levels, clear/free, and product connection
guards; all fourteen selectors compile independently. Live CCC persistence,
peer, callback, security-level, and controller behavior remains blocked by
future-required authorized responsive physical evidence. See the
[ATT CCC audit](research/cordio-atts-ccc-source-recovery.md).

The ATT server-write tranche is now production-routed: all four linked
`atts_write.c` definitions / 1,220 stock body bytes are replaced by 1,644
compiled Cortex-M55 bytes plus 12 alignment bytes under 25 strict relocations.
The implementation preserves request/command response asymmetry, callback and
CCC dispatch, pending-response bearer state, configured prepare limits,
validate-before-commit execute semantics, cancellation, and the recovered
fixed-SRAM EATT ABI. The dead-stripped public `AttsContinueWriteReq` is also
implemented, host-tested, and independently ARM-compiled without claiming a
stock redirect. The strict component, manifest, deterministic package, flash
plan, host behavior, analyzer, and all five selector builds are green. Live
write/prepare/execute traffic, deferred callback completion, ATT peer behavior,
controller timing, and EM9305 interaction is blocked by unavailable physical evidence; future qualification requires authorized responsive physical evidence. See the
[ATT write audit](research/cordio-atts-write-source-recovery.md).

The common ATT server-processor tranche is now production-routed: all nine
`atts_proc.c` definitions / 2,106 stock body bytes are replaced by 1,722
compiled Cortex-M55 bytes plus 10 alignment bytes under 28 strict relocations.
The source preserves UUID conversion, group/attribute/range lookup, permission,
encryption/authentication/authorization policy, the r20 EATT MTU gate,
find-information, ordinary read, and variable-multiple-read behavior. It also
retains the authenticated G2 product peer-MTU floor of 247 that differs from
the public source default. Host behavior, all nine isolated target builds,
strict routing, component tiling, manifest, deterministic package, flash plan,
and analyzer gates are green. Live discovery/read traffic, link security state,
peer interoperability, controller timing, and EM9305 behavior remain blocked
by future-required authorized responsive physical evidence. See the
[ATT processor audit](research/cordio-atts-proc-source-recovery.md).

The ATT client-discovery tranche is also complete: fifteen common
`attc_disc.c` functions / 2,908 code bytes plus 104 bytes of literal/alignment
data occupy `[0x0056B7EC,0x0056C3B0)`. Stock's characteristic scan contains
the r20-only post-match `break`, and its retained line numbers select the
Packetcraft r20.05--r20.05c source family over AmbiqSuite 2.5.1/r19. The
20-byte state ABI, all 20 direct callers, and pointer/interior ingress are
closed; three unused included-service routines are dead-stripped. Lorelei's
two readiness profiles link with zero unresolved symbols. Module
identification is 95--98%; overall Cordio remains 80--85% and production
ownership is unchanged. See the
[ATT discovery audit](research/cordio-attc-disc-source-recovery.md).

The ATT client core is now closed as well: twenty linked `attc_main.c`
functions / 3,540 code bytes plus 140 owned data bytes occupy
`[0x00530D74,0x00531BD4)`. Stock's three-bearer-per-connection layout and
17-entry request table select the Packetcraft r20.05 EATT architecture; its
zero-length packet rejection matches the later official Ambiq R4.4.1 patch.
The analyzer closes 32 direct calls, 17 stored entries, the retained path,
and all strict-interior ingress. Only `AttcSetAutoConfirm` is source-only.
Identification is 95--98%; production ownership is unchanged. See the
[ATT client-core audit](research/cordio-attc-main-source-recovery.md).

The client PDU and optional request units now close the rest of the stock
response table. `attc_proc.c` contributes fifteen linked functions / 1,884
code bytes in `[0x004B5230,0x004B59C0)`; `attc_read.c` contributes four / 414
bytes in `[0x0056C3B0,0x0056C550)`; and `attc_write.c` contributes two / 124
bytes in `[0x00539DCC,0x00539E48)`. Nine unused APIs are dead-stripped across
the three units. The first two independently confirm the r20 per-bearer/EATT
architecture; the write bodies are release-invariant and inherit that pin.
All 24 direct calls, 13 local response-table entries, object boundaries, and
strict-interior ingress are closed. The mandatory-PDU audit also records the
inherited R4 response/minimum-length table bounds defect without treating
adjacent string bytes as owned table data. Production ownership is unchanged.
See the [PDU processor](research/cordio-attc-proc-source-recovery.md),
[client read](research/cordio-attc-read-source-recovery.md), and
[client write](research/cordio-attc-write-source-recovery.md) audits.

The optional ATT client-write unit is now production-routed. Two guarded
redirects replace its complete 124-byte linked interval with 144 compiled
Cortex-M55 bytes plus two alignment bytes under two strict relocations. All
three dead-stripped allocation, prepare-request, and execute-request helpers
are maintained and independently target-compiled without being counted as
stock coverage. Host tests exercise response continuation, value adjustment,
command encoding, copied and referenced prepare values, execute/cancel flags,
allocation alignment, ownership transfer, and failure behavior. The canonical
overlay/component/package sizes are 347,282 / 3,870,678 / 4,649,172 bytes;
the package SHA-256 is
`777a059d84671ee04460d7c9cdb9af9ab93ce7eaaced0932b0c254f9f2a53e77`.
Live ATT peer/controller, continuation, and buffer-lifetime validation is
blocked by unavailable physical evidence; future qualification requires authorized responsive G2/EM9305 physical evidence. No
image was signed, flashed, or installed.

The optional ATT client-read unit is now production-routed as well. Four
guarded redirects replace all 414 linked stock body bytes with 440 compiled
Cortex-M55 bytes plus two alignment bytes under four strict relocations. The
three dead-stripped long-read, multiple-read, and group-type request helpers
are maintained and independently target-compiled. Host coverage exercises
ordered, continuing, terminal, and malformed Find By Type responses,
per-bearer Read Long MTU/offset behavior, and all five request encoders. The
maintained parser bounds a trailing partial handle pair before decoding it.
The canonical overlay/component/package sizes are 347,724 / 3,871,120 /
4,649,614 bytes; the package SHA-256 is
`a7d2627341cd8603e607a37c19d70ed42f7f5ba501fb6c76826664cb322de06d`.
Live ATT peer/controller, negotiated-MTU, continuation, and buffer-lifetime
validation is blocked by unavailable physical evidence; future qualification requires authorized responsive G2/EM9305
physical evidence. No image was signed, flashed, or installed.

The mandatory ATT client PDU processor is now production-routed. All fifteen
linked entries / 1,884 stock body bytes are source-owned as 1,694 compiled
Cortex-M55 bytes plus 22 alignment bytes under 38 strict relocations. Thirteen
entries use guarded redirects and the two two-byte no-op leaves use exact
in-place source copies. The dead-stripped cancel API is also implemented and
target-compiled. Bounded response dispatch removes the inherited method-16/17
adjacent-table overrun; one-based connection IDs select on-deck slot
`connection_id - 1`, and cancel uses authenticated event 19. The canonical
overlay/component/package sizes are 353,336 / 3,876,732 / 4,655,226 bytes;
the deterministic package SHA-256 is
`b10166d4f1c1f91f348c3ee360afb2af1499df59715491a1256a1d0545f548bc`.
Live ATT/EATT peer, controller, timer, flow-control, and buffer-lifetime
validation is blocked by unavailable physical evidence; future qualification requires authorized responsive G2/EM9305
physical evidence. No image was signed, flashed, or installed.

Optional ATT client signing is conclusively absent. `AttcInit` leaves the
signing interface null, no later installation exists, and complete
CMAC/local-CSRK/write-wrapper caller censuses assign every candidate to other
bounded modules. All seven `attc_sign.c` definitions are therefore
source-only; this removes an optional dependency without assigning any stock
bytes. See the
[client-signing exclusion](research/cordio-attc-sign-exclusion.md).

The legacy advertising tranche closes seventeen linked `dm_adv_leg.c`
functions / 4,396 code bytes in `[0x004B9A80,0x004BAC4E)`, plus 162 inline
data bytes and a separately owned 100-byte trailing pool after one interleaved
foreign function. Function definitions are Apache-identical from r19/Ambiq
through r20.05c, but stock message offset `+8` proves Ambiq's flexible-array
payload ABI. The two-set SRAM layout, action/interface tables, and every direct
or registered entry are closed; `DmAdvModeLeg` is dead-stripped. Lorelei's two
profiles link with zero unresolved symbols. All eighteen definitions are now
maintained and target-compiled. Fourteen guarded redirects and three exact
two-byte in-place copies replace all 4,396 linked stock body bytes with 948
compiled bytes plus 26 alignment bytes under 32 strict relocations. Host
state-machine, HCI completion, callbacks, timers, private events, direct
advertising, bounds, routing, package, and flash-plan gates pass. Live BLE
peer/controller, RF, timing, and address-policy validation is deferred by
project direction; future qualification requires authorized G2/EM9305 physical
evidence. See the
[legacy advertising audit](research/cordio-dm-adv-leg-source-recovery.md).

The common advertising producer tranche closes nine linked `dm_adv.c`
functions / 562 code bytes plus its ten-byte literal pool. Exact AmbiqSuite
R2.4.2/R2.5.1 Apache source matches stock's `len+8` allocation and inline
payload copy; Packetcraft r19/r20 instead uses an incompatible payload
pointer. All eleven callers, direct providers, two-set globals, and pointer
closure are guarded. Six unused APIs are dead-stripped, and both Lorelei
profiles link with zero unresolved symbols. All fifteen definitions now have
maintained source; nine guarded redirects replace all 562 linked stock body
bytes with 1,122 compiled bytes plus 20 alignment bytes under 15 strict
relocations, and the six stripped APIs target-compile. Message/state/event,
malformed-element, bounds, routing, package, and flash-plan gates pass. See the
[common advertising audit](research/cordio-dm-adv-source-recovery.md).

The DM connection-manager tranche closes 57 linked functions / 6,216 code
bytes in `[0x004B5B24,0x004B7426)`, plus 186 interstitial bytes and an
82-byte trailing pool through `0x004B7478`. Fifty-six bodies map to the
Apache-2.0 Packetcraft r20.05 source inventory; one 62-byte helper is a
vendor-only addition, and five public APIs are dead-stripped. Action/component
tables, 209 direct callers, thirteen registered Thumb pointers, the
three-connection/196-byte SRAM ABI, and all stock spans are fail-closed.
Lorelei's corrected v2 handoff preserves two non-vacuous zero-unresolved
build closures and nine conservative anchors; local analysis expands it to the
complete linked module. The architecture is a hybrid: r20 connection-update
and peer-SCA behavior, Ambiq 2.5.1 warning suppression, and product validation
patches. Module identification is 95--98%; overall Cordio remains 80--85%,
and production ownership is unchanged. See the
[DM connection-manager audit](research/cordio-dm-conn-source-recovery.md).

The adjacent DM connection state-machine tranche closes the sole linked
`dm_conn_sm.c` dispatcher. One guarded redirect replaces all 1,598 stock body
bytes with 120 compiled Cortex-M55 bytes under two strict relocations. Its
exact five-state/eight-event r20 table and 58-byte pool remain authenticated
retained data. Exhaustive 40-transition host tests cover event masking,
next-state-before-action order, and null/invalid CCB, action-set, and action
pointer paths. Component, manifest, deterministic package, and flash-plan
gates pass. Live controller completion, role-action timing, cancellation,
disconnect, and paired-temple behavior is blocked by unavailable physical evidence; future qualification requires authorized responsive G2/EM9305 physical evidence. See the
[DM state-machine audit](research/cordio-dm-conn-sm-source-recovery.md).

The DM local-device tranche closes twelve linked functions / 626 code bytes
and 46 bytes of literal/alignment data in the complete 672-byte
`dm_dev.c` footprint. Three interface/action pointers, 29 direct calls, all
provider relocations, the 21-component message ABI, and the retained source
path are fail-closed. Official Ambiq R4.4.1 source explains the vendor-command
translator, stale-reset clear, and trace layout; six filter/whitelist APIs are
dead-stripped in stock but remain target-compiled. Twelve guarded redirects
replace all 626 linked body bytes with 448 compiled Cortex-M55 bytes plus 18
alignment bytes under nine strict relocations. Host reset/HCI/callback,
privacy/CTE bridge, allocation, address, whitelist/filter and bounds tests,
component, manifest, package, and flash-plan gates pass. Live controller
reset/timing/address/filter/privacy and paired-temple validation is
blocked by unavailable physical evidence; future qualification requires authorized responsive G2/EM9305 evidence. See the
[DM local-device audit](research/cordio-dm-dev-source-recovery.md).

The optional DM device-privacy tranche is now closed as a stock exclusion.
All 18 public `dm_dev_priv.c` functions compile and link in two Lorelei
profiles, but none is present in G2. The authenticated 21-slot boot table keeps
component 1 on `dmFcnDefault`; all nine interface-table base references and
every component install are accounted for, with no write to slot 1. There is
also no privacy action/interface table, retained path, or Start/Stop allocation
wrapper. The analyzer therefore records zero linked bytes and eighteen
source-only functions. Production ownership is unchanged. See the
[device-privacy exclusion audit](research/cordio-dm-dev-priv-exclusion.md).

Those 18 optional functions are now also maintained and behavior-tested in
local C and compile for Cortex-M55. The production route count deliberately
remains zero because installing component 1 would contradict the authenticated
product configuration.

The DM main-router tranche now closes all sixteen `dm_main.c` functions / 484
code bytes and the complete 508-byte physical interval. More importantly,
stock's 90-entry HCI route table, 92-entry callback-size table, and 21-slot
component table exactly select the official AmbiqSuite R4.4.1 source family;
r19, AmbiqSuite 2.5.1, and vanilla Packetcraft r20 have different dimensions.
Twenty-nine direct calls, fifteen stored entries, the decoded boot interface
table, and zero interior ingress are fail-closed. Lorelei preserves dual
public-r20/R4 Os/O1 lanes with four live zero-unresolved closures; the R4 lane
is explicitly a hybrid header/config build. All sixteen definitions are now
production-owned: fourteen guarded redirects plus two exact two-byte copies
cover all 484 stock body bytes with 524 compiled Cortex-M55 bytes plus 20
alignment bytes under two strict relocations. Host router/registration/data/
privacy/address/event-size/PHY behavior, all selector builds, routing,
manifest, deterministic package, and flash-plan gates pass. Live
HCI/controller/peer/timing and paired-temple validation is deferred by project
direction; future qualification requires authorized G2/EM9305 physical
evidence.
See the [DM router audit](research/cordio-dm-main-source-recovery.md).

The adjacent DM privacy tranche closes 21 linked `dm_priv.c` functions / 980
code bytes and the full 1,008-byte physical interval. Its seven-entry main
action table, two-entry AES action table, and component-6/component-15
interface installs select the Packetcraft r20.05/Ambiq R4 split architecture.
Four unused public APIs are dead-stripped; nineteen direct calls, thirteen
stored entry pointers, and zero interior pointers close ingress. All 25 source
definitions are now maintained and Cortex-M55 compiled. Twenty-one guarded
redirects replace all 980 stock body bytes with 1,688 compiled bytes plus 20
alignment bytes under 25 strict relocations; the four dead-stripped APIs are
source-only build products. Host behavior, exact routing, component, manifest,
deterministic package, and flash-plan gates pass. Live controller privacy,
address, RF/timing, and paired-temple validation is blocked by unavailable physical evidence; future qualification requires authorized responsive G2/EM9305 physical evidence. See the
[DM privacy audit](research/cordio-dm-priv-source-recovery.md).

The adjacent DM security tranche closes eight linked `dm_sec.c` functions /
462 code bytes and the full 488-byte physical object. Stock's nonzero
EDIV/Rand LTK rejection while LESC is enabled is the decisive Packetcraft
r20/Ambiq R4 behavior and excludes r19/AmbiqSuite 2.x. Four unused APIs are
dead-stripped; the three registered interface entries and all direct ingress
are fail-closed. Production ownership is unchanged. See the
[DM security audit](research/cordio-dm-sec-source-recovery.md).

The component-8 LESC tranche closes seven linked `dm_sec_lesc.c` functions /
222 code bytes in a 248-byte object and four dead APIs. Its source bodies are
release-invariant, while the exact `0x40/0x41` message values pin the r20/R4
shift-three ABI. The interface, ECC-key storage, calls, and interior ingress
are fail-closed. See the
[DM LESC audit](research/cordio-dm-sec-lesc-source-recovery.md).

The component-9 PHY tranche closes six linked `dm_phy.c` functions / 308
code bytes in a 320-byte object and two dead APIs. `DmPhyInit` uses the
widened 64-bit `HciSetLeSupFeat(0x900, TRUE)` ABI under the task lock, which
decisively selects Packetcraft r20/Ambiq R4 over r19/AmbiqSuite 2.x. The
registered interface, five direct calls, callback ABI, and zero interior
ingress are fail-closed. Six guarded redirects now replace all 308 stock body
bytes with 378 compiled Cortex-M55 bytes plus four alignment bytes under
eleven strict relocations. Both dead-stripped public APIs target-compile.
Host HCI/callback/command/init behavior, routing, manifest, deterministic
package, and flash-plan gates pass. Live controller PHY negotiation,
peer/RF/timing, and paired-temple validation is blocked by unavailable physical evidence; future qualification requires authorized responsive G2/EM9305 physical evidence. See the
[DM PHY audit](research/cordio-dm-phy-source-recovery.md).

The slave-security tranche closes all three `dm_sec_slave.c` wrappers / 148
code bytes in a 152-byte object. Six direct callers, no stored pointers, and
zero interior ingress are fail-closed. The bodies are release-invariant, but
the LTK-response event `0x29` independently selects the r20/R4 three-bit
message ABI over r19's `0x51`. See the
[DM slave-security audit](research/cordio-dm-sec-slave-source-recovery.md).

The master-security tranche likewise closes all three `dm_sec_master.c`
functions / 144 code bytes in a 152-byte object. Four direct callers and zero
stored/interior pointers close ingress; event `0x28` selects r20/R4. This
tranche also proves `dmSecCb=0x20074114` and
`calc128Zeros=0x007856B0`. See the
[DM master-security audit](research/cordio-dm-sec-master-source-recovery.md).

The master-connection tranche closes five linked `dm_conn_master.c`
functions / 138 code bytes in a 140-byte span; only `DmConnSetAddrType` is
dead-stripped. Event `0x72`, component 14, and `dmConnUpdExecute` decisively
select r20/R4's separated update architecture. Two direct calls, three action
pointers, and zero interior ingress are fail-closed. See the
[DM master-connection audit](research/cordio-dm-conn-master-source-recovery.md).

All six definitions are now maintained and Cortex-M55 compiled. Five guarded
redirects replace every linked body byte, and the component/package/flash-plan
contract is pinned. Live controller/L2CAP/privacy/peer/RF and paired-temple
behavior remains hardware-deferred by future-required authorized responsive
evidence.

The legacy-master connection tranche closes all three
`dm_conn_master_leg.c` functions / 136 code bytes and its 24-byte pool. The
r20 two-table locked initializer and two-entry main table exactly match stock
and exclude r19's unlocked four-entry architecture. Two direct calls, one
registered pointer, and zero interior ingress are fail-closed. See the
[legacy-master audit](research/cordio-dm-conn-master-leg-source-recovery.md).

The adjacent legacy-slave tranche closes all five
`dm_conn_slave_leg.c` functions / 104 code bytes and its 16-byte pool. Its
four-entry main table and separate two-entry update table are installed under
the task lock, excluding r19's unlocked six-entry architecture. One direct
call, four registered pointers, and zero interior ingress are fail-closed.
All functions are maintained in C and target-compiled; five guarded redirects
replace every bounded body byte, and component/package/flash-plan ownership is
pinned. Live controller, peer, RF, and paired-temple behavior remains blocked
by future-required authorized responsive hardware.
See the [legacy-slave audit](research/cordio-dm-conn-slave-leg-source-recovery.md).

The core slave-connection tranche closes five linked `dm_conn_slave.c`
functions / 206 code bytes in a 212-byte object; only `DmConnAccept` is
dead-stripped. The exact two-entry action table, component-14 event `0x73`,
and `dmConnUpdExecute` route independently select r20/R4. Five direct calls,
two registered pointers, and zero interior ingress are fail-closed. See the
[slave-connection audit](research/cordio-dm-conn-slave-source-recovery.md).

All six definitions are now maintained and Cortex-M55 compiled. Five guarded
redirects replace every linked body byte; host behavior, disjoint route
namespaces, component tiling, deterministic package, and flash-plan pins are
green. Live controller/L2CAP/peer/RF and paired-temple behavior remains
hardware-deferred by future-required authorized responsive evidence.

The L2CAP slave tranche closes six linked `l2c_slave.c` functions / 1,078
code bytes in a complete 1,148-byte object; only `L2cDmSigReq` is
dead-stripped. Stock contains r20's connection-ID validation and `connId-1`
state indexing, excluding AmbiqSuite 2.x. Four direct calls, two stored
pointers, and zero interior ingress are fail-closed. See the
[L2CAP slave audit](research/cordio-l2c-slave-source-recovery.md).

The adjacent L2CAP master tranche closes all three `l2c_master.c` functions /
658 code bytes in a complete 700-byte object. Its bodies are release-invariant,
so it is qualified through exact Apache definitions plus the neighboring
r20/R4 DM ABI rather than treated as an independent version discriminator.
Three calls, one stored callback, and zero interior ingress are fail-closed.
See the [L2CAP master audit](research/cordio-l2c-master-source-recovery.md).

The L2CAP core tranche closes all 11 `l2c_main.c` definitions / 1,636 code
bytes in the corrected 1,736-byte object ending at `0x00530C00`. Sixteen direct
calls, six registered callback entries, and zero interior pointers are
fail-closed. Its bodies are release-invariant, so exact r20 Apache definitions
are qualified by the neighboring r20/R4 DM architecture. See the
[L2CAP core audit](research/cordio-l2c-main-source-recovery.md).

The remaining optional `l2c_coc.c` unit is positively excluded: all 67 public
definitions are source-only. Stock has only the three known `l2cCb` literals
and three non-CoC `DmConnRegister` callers, while mandatory `L2cCocInit`
requires both. No CoC path, API, or diagnostic marker survives. See the
[L2CAP CoC exclusion](research/cordio-l2c-coc-exclusion.md).

The secure-connections SMP-main tranche closes 18 linked `smp_sc_main.c`
functions / 2,626 code bytes in the complete 2,820-byte object at
`[0x0056CDC0,0x0056D8C4)`. Four unused public definitions are source-only.
The retained cleanup-event name at value `0x1F` independently selects the r20
message ABI. One hundred eleven direct calls, no registered entry pointer, and
zero real interior ingress are fail-closed. See the
[SMP secure-connections main audit](research/cordio-smp-sc-main-source-recovery.md).

The paired secure-connections state-machine tranche closes all four
`smpi_sc_sm.c` / `smpr_sc_sm.c` functions / 598 code bytes, both physical
objects, and 1,495 scattered dispatch-data bytes. Its two interfaces lead to
106 action pointers, 78 state pointers, and all 80 common/per-state tables.
The responder's 55-action table and API-pair-request timeout/cleanup rows
exclude r19. Four direct calls and zero stored/interior function pointers are
fail-closed. See the
[SMP SC state-machine audit](research/cordio-smp-sc-state-machines-source-recovery.md).

## Percentage definitions

The current Apple Clang core-source package is 4,444,468 bytes. The table uses
the component builder as the ownership authority and therefore applies the
1,592-byte flash-plan metadata correction proven by the origin-accounting
audit:

| Byte ownership | Bytes | Package share | Meaning |
|---|---:|---:|---|
| Source compiled | 143,245 | 3.222995% | Human-readable openCFW source emitted in `source_compiled` regions |
| Generated | 100,384 | 2.258628% | Container/wrapper/checksum/alignment/redirect bytes, including the 1,592 controlled bytes still mislabeled by the hand-partitioned flash plan |
| Controlled total | 243,629 | 5.481623% | Source compiled plus generated |
| Opaque compatibility bytes remaining | 4,200,839 | 94.518377% | Bytes still copied from official firmware or retained external payloads after metadata reconciliation |

`94.518377%` is the exact reconciled answer to “how much of the package remains
blob-backed,” but it is **not** a defensible estimate of proprietary Even
source. Opaque spans still mix identified upstream libraries, first-party Even
code/data, vendor ports, generated assets, and proprietary controller images.
The source manifest does not assign every opaque byte a fine-grained origin,
so a precise “original, non-upstream source” percentage would be false
precision. The origin-aware companion ledger supplies conservative Apollo
lower bounds without relabeling mixed residual bytes as data or first-party
source.

## Upstream dependency identification

The estimates below measure provenance/configuration identification, not byte
replacement. `100%` means an exact maintained upstream commit and required
G2 selection are pinned; a range means a compatible source interval or vendor
fork remains. Production replacement can be much lower even when identity is
complete.

| Dependency | Identification estimate | Maintained source pin | Principal remainder |
|---|---:|---|---|
| FreeRTOS-Kernel | 100% | V10.5.1 `def7d2df2b0506d3d249334974f51e427c17a41c`; recovered one-field G2 TCB patch SHA-256 `cf8c457153b75ad6a3163b9b6e6873e476e03537bb4534c9c8e4557de0eb4eb3`; scheduler/port start and complete STIMER setup/IRQ/tickless algorithms dual-profile qualified | Original private patch commit/name unobservable; atomic production binding, hardware timing/sleep validation, and first-party power/trace hooks |
| CMSIS-FreeRTOS | 100% | v10.5.1 `d213f261b5be6bb29a7cce8b84071706b72f4d53`; exact `cmsis_os2.c` blob first at `13acfbef7be85119fc6bc56832c455d4547d92c7`; all 43 linked functions and all 38 public plus five private production entries source-owned | No linked functional gap; exact historical checkout remains bounded, not unique |
| CMSIS Core | 100% | `d23a6949a0331ca96853bcd98b0fdcc4db47184c` | None for the selected header closure |
| AmbiqSuite Apollo510 | 100% | 5.1.0 `5efc0228528a8adce5eae0d226fac85d2551eb3b` | Wider HAL ordinal/port reconciliation |
| AmbiqSuite ANCC profile | 100% source lineage and stock boundary | selected 2.5.1 import `de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f`; exact 17-definition source/header; implementation identical across authenticated 2.2.0-2.5.1 imports; 12 source-derived and nine G2-local stock functions | Exact private producing release/commit is binary-unobservable; production admission and first-party G2 extension implementation |
| AmbiqSuite AMOTA profile | 100% application-skeleton lineage and G2 OTA boundary | selected 2.5.1 import `de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f`; exact source/API oracle; stable across four authenticated release imports; four skeleton-derived and three G2-local stock functions | Exact private producing release/commit is binary-unobservable; production admission and first-party Even OTA actions |
| NemaGFX / NemaVG / Ambiq GPU patch | 100% public package identity; NemaGFX stock floor exact; all stroke-cap entries source-routed | AmbiqSuite 5.1.0 revision `release_sdk5p1p0-634f7c117b`; public tree `e690768a…` at `b853fded…`; NemaGFX 1.4.12; NemaVG 1.1.8; all 11 GPU-patch exports and all 18 stock HAL functions source-qualified; `draw_start_cap`, `draw_end_cap`, and `draw_caps` production-routed (6,614 stock bytes) | Original IAR/private HAL commits, remaining internal Nema source, Ambiq bare-metal HAL binding, and authorized Apollo510 GPU/display validation; physical evidence is unavailable |
| FreeType | 100% | 2.9.1 `86bc8a95056c97a810986434a3f268cbe67f2902` | Remaining toggles, destructor closure, font payloads, IAR details |
| littlefs | 95–100% | v2.10.1-equivalent `0494ce7169f06a734a7bd7585f49a9fa91fa7318` | Exact historical checkout and golden external-flash capture |
| TLSF | 90–95% | v3.1-compatible `deff9ab509341f264addbd3c8ada533678591905` | Exact historical checkout |
| LZ4 | 90–95% | v1.10.0 `ebb370ca83af193212df4dcbadcc5d87bc0de2f0` | Stock v1.9.4/v1.10.0 discriminator and optional unreachable-stock compaction |
| nanopb | 90–95% | 0.4.9 `98bf4db69897b53434f3d0ba72e0a3ab1a902824` | Vendor 0.4.7–0.4.9.1 discriminator and schemas/generated messages; accumulated Linux/Clang 22 profile is now recorded and twice replayed |
| FlashDB | 90–95% | 2.1.1 `714d6159e7e6afb267a3953756abca445c350e61` | Vendor-checkout proof, schema/non-destructive mount policy, and golden-capture validation |
| Packetcraft Cordio | 100% retained reusable-path/module classification; production-excluded | r20.05–r20.05c public interval ending at `3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`; r19.02 `86372d84…`; later Ambiq R4 oracle `4264b930…`; R2.5.1 port archive `87b03680…`; GATT, ANCC, AMOTA lineage classified; EUS/ESS/EFS/NUS/Ring proven G2-local; all retained BLE-profile paths closed | Exact mixed producing commit is unobservable; production admission/placement and hardware/controller validation; application/product behaviors remain first-party boundary work |
| LVGL | 95–98% | official-core ceiling `344c7c318047b7348e1be8572a9fd4260c251cfa`; exact Ambiq subtree `1e774257…` at canonical `5be8e0ae…` / replay `67fd93e2…`; exact public Nema package tree `e690768a…`; all seven private display-port functions / 638 stock bytes are source-owned | Whole hybrid-tree and private display-port commits are unobservable; stock GPU/HAL admission, assets, hardware validation, and first-party input/display integration remain |
| EasyLogger | 95–97% | 2.2.99-compatible `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`; main output/hexdump integrated; all downstream `elog_async_api.c` queue, callback/consumer, and event-worker/thread algorithms dual-profile qualified | Target concurrency/hardware stress, production admission, exact historical checkout, and image-specific transports |
| FreeRTOS-Plus-CLI | 100% linked reusable behavior | exact C/H interval `43defa56…` through `1309654d…` plus isolated G2 patch; all five linked interpreter entries and console/accessor seams source-owned | Historical checkout is binary-unobservable; descriptors/commands are first-party and static allocation is a future policy choice |
| mpaland/printf | 100% linked behavior | `d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e`; all linked helpers, conversions, variadic core, wrappers, and G2 recursive-pointer extensions source-owned | Exact historical checkout only; no linked functional gap |
| TinyFrame | 99% | authenticated exact core snapshot introduced by `eb75483e035916ef9f3e9fce0d2ae389cb09785f`; checkout interval `eb75483e`…`a29167a69f052975b0e0134a73b4d31d03afa8fa`; all 31 linked functions mapped; single-instance peer-role census, G2 adapter, source-owned heap port, retained sync wrapper, no-op logging policy, and dual-profile 14-function atomic production graph closed | Hardware golden packets; exact historical checkout within the core-identical interval is binary-unobservable |
| CmBacktrace | 70–80% | compatibility selection `73714489f9d8af130aacb515586b397b604a5768` | Exact vendor commit and remaining port/config details |
| AndersKaloer/Ring-Buffer | 100% | selected `190e30bebcec22d7311fd941179d70b4f439c441`; binary-compatible interval starts at `cda00e1efb815bad5100757f0d10d117f633ced6` | Deferred hardware validation; exact Even checkout is not binary-distinguishable |
| First-party `fw_event_loop` | 100% provenance/behavior | clean-room production source; no upstream pin applies | Deferred hardware scheduling validation; retained dependency pool remains stock data |
| EM9305 QP/C | 100% release/family; 95–100% configuration | QP/C v6.5.1 `416dcec8820b9cdb5827497e645d0d9375db53c6`; 36 stock functions match the authenticated SDK archive at known addresses, three internal hooks are proven vendor-modified, the exact QK SWI port is recovered, and the compiler is MetaWare ARC T-2022.09 build 004 / LLVM 14.0.6 at `-Os`; exact private source checkout remains unproven | Named hook callees, unused time-event counter layout, private source tree, and license; see the [ARCompact](research/em9305-qpc-arcompact-audit.md) and [archive](research/em9305-sdk-archive-match-audit.md) audits |
| EM9305 Packetcraft/EM Bleu controller | 100% SDK binary artifact identity; authoritative public source commit/final runtime configuration unresolved | SDK v4.2 `lib_emb_controller.a` blob `6a1a8e3d…` supplies 1,055 address/body fingerprints; ISO, strict, and NOP-aware lanes now identify 202 link-order placements / 11,934 bytes, including 50 exact and 51 same-size or size-delta modified functions; Bluetooth 5.4 `BT_VER=13`, Packetcraft `LL_VER_NUM=28992`, exact MetaWare compiler | Packetcraft public source ends at much older r20.05c/`LL_VER_NUM=1366`; locate authoritative licensed 2024 source and reconcile final-link configuration, or retain cut-forward spans; see the [expanded census](research/em9305-expanded-sdk-archive-census.md), [link-order ledger](research/em9305-sdk-link-order-recovery.md), and [residual census](research/em9305-residual-segment-census.md) |
| EM9305 EM system/HAL/radio support | 100% for matched SDK artifacts; wider source closure incomplete | Two archive censuses pin EM HAL/system/radio, LL PAL, NVM, RC calibration, transport, app-entry/core/stack and AOAD artifacts; boundary-qualified, NOP-aware, vector-ABI, and short-prefix replay produce the 1,494-function exact map | Classify/recreate remaining modified functions and recover redistribution-safe source/configuration |
| EM9305 PML | 100% SDK artifact; source unavailable | SDK v4.2 `lib_pml.a` blob `45c88f15bc6367dc15e3cdcabb9a23be74bb9934`; 44 unique exact stock functions / 3,000 bytes | Recover or recreate proprietary source/configuration; retain exact stock spans meanwhile |
| EM9305 protocol timer | 100% SDK artifact; source unavailable | SDK v4.2 `lib_prot_timer.a` blob `cf8f1f22ea840568c83c6a2662c86e7d95b6581a`; 13 unique exact functions / 932 bytes plus one bounded vendor-modified function | Recreate source/configuration or maintain cut-forward spans |
| EM9305 sleep manager | 100% SDK artifact identity; behavior 70–80% | SDK v4.2 `lib_sleep_manager.a` blob `05af021ac9132dc8c727913c4382eba9019aebdb`; exact RC-cal callback and configured 516-byte sleep manager named | Fully reverse configured sleep policy/ROM seams or cut forward |
| EM9305 sleep timer | 100% SDK artifact; source unavailable | SDK v4.2 `lib_sleep_timer.a` blob `3713f176b7f1614920a3043c4dcb41ba730e3fe0`; three unique exact functions / 128 bytes | Recreate missing store/restore/disable closure or cut forward |
| EM9305 unitimer | 100% matched leaf; wider archive closure incomplete | SDK v4.2 `lib_unitimer.a` blob `07ed4df5a464637adf024d383bc89d2fd0b57bb0`; exact `Timer_RegisterModule` | Match/recreate remaining configured unitimer bodies |
| IAR DLIB runtime | 40–50% provenance; 100% bounded functional source | IAR family; three authenticated `Jul  6 2026` build banners; formal Cortex-M55 support implies a practical EWARM 9.20+ floor; 9.60.2 is the leading compatibility candidate; likely `m7M_tl{v|s}`/`rt7M_tl` archive families, exact release unproven; all 13 bounded runtime code units now have exact or qualified clean-room source and canonical Apple guarded production integration | Exact IAR release, VFP-library variant, Normal/Full DLIB option, release-specific archive comparison, wider DLIB census, Linux profile recording for the newest three leaves, and hardware validation; see the [runtime census](research/iar-dlib-runtime-census.md) and [`frexpf`/`ldexpf` audit](research/iar-dlib-frexpf-ldexpf-recovery.md) |

Every named third-party family in the Apollo-main build tree is identified at
least to a family. IAR DLIB remains the lowest-confidence dependency row and
is deliberately not assigned an exact release until stronger evidence exists.
The authenticated LVGL path/corpus correlation now also maps the complete
178-byte `lv_iter_create` body to `src/misc/lv_iter.c`, including allocation,
field-offset, and assertion-line evidence. It remains production-excluded:
the corpus has no direct caller token, and indirect reachability plus original
relocation/caller closure are unresolved.

## Firmware controller and segment status

| Package/controller domain | Current reconstruction state | Approximate provenance identification | Required next evidence |
|---|---|---:|---|
| Apollo510 main | Mixed: 142,760 source-owned bytes plus 98,402 generated patch bytes and a 3,424,780-byte retained base | 100% coarse origin accounting for the retained base; named upstream families remain 90–100% individually | The retained base now splits into 130,000 third-party-path, 461,468 first-party/project-path, 675,636 unanchored-function, and 2,157,676 outside-envelope bytes; prioritize the unanchored code and preserve conservative residual labels |
| Apollo510 bootloader | Mixed: 126 routed littlefs/EasyLogger/Ambiq/S200/runtime/TLSF functions; 6,931 source-owned B, 8,208 generated patch B, 140,391 retained official B | 85–90% | Continue source closure from the EasyLogger service block at `0x0041733C`; preserve authenticated transition data, distinct two-byte compatibility stubs, and the protected secure-loader boundary; physical validation remains unavailable |
| EM9305 BLE controller | Cut-forward; QP/C 6.5.1, Packetcraft/EM Bleu Bluetooth-5.4 controller, exact compiler, and 54 SDK archive lanes authenticated. Across 875 merged intervals, 1,494 exact functions cover 157,122 bytes (74.504950%); link-order, vector-ABI, and authenticated short-prefix placements raise function-provenance identification to 167,684 bytes (79.513296%). The final 175-span / 33,658-byte residual ledger has zero unclassified bytes: 1,240 concrete-source candidate, 8,348 unsupported external boundary, and 24,070 unavailable proprietary controller code | 92–95% overall provenance; QP/C 95–100% configuration; exact-function byte coverage 74.504950%; source completion false | Route and validate the 1,240-byte source candidate, resolve/recreate supported portions of the typed boundaries, and obtain licensed authoritative Packetcraft/EM source or retain explicit cut-forward boundaries |
| Audio codec/DSP | Opaque/cut-forward; proprietary NationalChip image with U-Boot-derived CLI | 25–35% | Resolve both segment destinations and isolate reusable CLI/runtime code |
| Touch controller | Opaque/cut-forward; vector base inferred | 10–20% | Identify controller SDK/library lineage and complete memory map |
| Charging case | Opaque/cut-forward; FreeRTOS family certain | 35–45% | Pin FreeRTOS/HAL versions and STM32G0 configuration |
| Secure Apollo bootloader | Protected and absent from EVENOTA | Not reconstructable from current bundle | Owned-device readout or authoritative vendor source; preserve boundary |

“Cut-forward” means the official bytes remain hash-pinned and can be carried
into a reproducible bundle while their source is unavailable. It is a
compatibility strategy, not a reverse-engineering completion claim.

The exhaustive per-address status is in [`memory-map.md`](memory-map.md).
Each emitted build also generates `build/source/flash-plan.json`, which is the
machine-readable authority for placed, unresolved, and container-only regions.

## Chronological frontier log

The entries below are retained in completion order. The authoritative current
state is the latest entry at the end of the log plus the summary tables above;
earlier size/ownership pins are historical milestones, not current totals.

The newest promoted boundary is nanopb private `read_raw_value` at
`[0x0048F6EA,0x0048F77E)`. Rizin and the fail-closed analyzer prove the
148-byte stock function, sole caller, three calls to the source-owned `pb_read`
provider, and two diagnostics. Apple Clang 21 emits a 134-byte text leaf plus
34 bytes of source-owned rodata at `[0x007B2CC4,0x007B2D6C)`; object, closure,
placement, full-span redirect, component, package, and ownership pins are
complete. The resulting overlay/component/package sizes are
125,512/3,648,908/4,427,402 bytes, with 1,040 placed and two unresolved flash
regions. The reviewed Linux/Clang 22 profile remains fail-closed pending access
to that compiler; no Linux value was inferred from Apple output.

The following `pb_make_string_substream` span at
`[0x0048F77E,0x0048F7CA)` is now source-recreated. Its 72-byte text and 24-byte
diagnostic closure occupy `[0x007B2D6C,0x007B2DCC)`; explicit field copies
remove the stock `__aeabi_memcpy` seam. Overlay/component/package sizes are
125,608/3,649,004/4,427,498 bytes with 1,042 placed flash regions. The next
nanopb boundary audit begins at `0x0048F7F4` after the already source-owned
close-substream helper.

The public `pb_decode_bool` body `[0x0049012C,0x00490150)` and private
`pb_dec_bool` adapter `[0x004901CC,0x004901D6)` are now source-recreated. Apple
places 28-byte and 6-byte leaves at `[0x007B2DCC,0x007B2DEE)`, with both
relocations resolving to source-owned nanopb providers. Current
overlay/component/package sizes at that milestone were
125,642/3,649,038/4,427,532 bytes, with 1,046 placed and two unresolved flash
regions. That milestone selected `pb_dec_varint` at
`[0x004901D6,0x00490352)` as the next low-level runtime frontier; the larger
`decode_basic_field` dispatcher at `[0x0048F7F4,0x0048F968)` remains identified
but should follow its scalar providers.

Private `pb_dec_varint` at `[0x004901D6,0x00490352)` is now also
source-recreated. Rizin and the fail-closed analyzer close the 380-byte stock
body, its sole exterior entry, all three provider calls, two diagnostic
strings, and all wide/narrow branch and stored-pointer ingress forms. Apple
places 304 text bytes and 36 diagnostic bytes at
`[0x007B2DF0,0x007B2F44)`. Current overlay/component/package sizes are
125,984/3,649,380/4,427,874 bytes, with 1,050 placed and two unresolved flash
regions. The next scalar-provider frontier is private `pb_dec_bytes` at
`[0x00490358,0x004903EA)`; the six-byte literal island at
`[0x00490352,0x00490358)` remains separately opaque and pinned.

Private `pb_dec_bytes` at `[0x00490358,0x004903EA)` is now source-recreated.
The fail-closed analyzer closes its sole direct caller, two source-owned
provider calls, three diagnostics, and all branch/pointer ingress forms. Two
raw four-byte matches were independently classified by Rizin as 16-bit pair
table records rather than executable pointers. Apple places 98 text bytes and
48 diagnostic bytes at `[0x007B2F44,0x007B2FD6)`. Current
overlay/component/package sizes are 126,130/3,649,526/4,428,020 bytes, with
1,054 placed and two unresolved flash regions. The next contiguous nanopb
frontier is private `pb_dec_string` at `[0x004903EA,0x00490488)`; the six-byte
literal island at `[0x00490352,0x00490358)` remains opaque and separately
pinned.

Private `pb_dec_string` at `[0x004903EA,0x00490488)` is now source-recreated.
The fail-closed analyzer closes its sole direct caller, two source-owned
provider calls, three diagnostics, and all branch/pointer ingress forms.
Apple places a two-byte alignment span, 114 text bytes, and 49 diagnostic
bytes at `[0x007B2FD6,0x007B307B)`. Current overlay/component/package sizes
are 126,295/3,649,691/4,428,185 bytes, with 1,058 placed and two unresolved
flash regions. After the separately pinned four-byte literal island at
`[0x00490488,0x0049048C)`, the next contiguous nanopb frontier is private
`pb_dec_submessage` at `[0x0049048C,0x00490538)`.

Private `pb_dec_submessage` at `[0x0049048C,0x00490538)` is now
source-recreated with explicitly partial closure. The fail-closed analyzer
pins its sole caller, source-owned substream make/close calls, local diagnostic,
application callback ABI, and one retained fixed stock call to
`pb_decode_inner` at `0x0048FE98`. Apple places one alignment byte, 138 text
bytes, and 25 diagnostic bytes at `[0x007B307B,0x007B311F)`. Current
overlay/component/package sizes are 126,459/3,649,855/4,428,349 bytes, with
1,063 placed and two unresolved flash regions. The next dependency frontier
is private `pb_decode_inner`; the successor literal island at
`[0x00490538,0x0049053C)` remains separately opaque.

No signing, flashing, erase, filesystem mutation, or physical device operation
is authorized by these estimates.

## Latest milestone: FreeRTOS priority-inheritance, IAR scanset, littlefs size leaf

Apollo main now source-owns `xTaskPriorityInherit` (`[0x004558CC,0x0045596E)`,
162 bytes), `vTaskPriorityDisinheritAfterTimeout` (`[0x00455A1C,0x00455ACA)`,
174 bytes), the IAR DLIB scanset matcher `open_cfw_iar_scanset_match`
(`[0x004D2112,0x004D2158)`, 70 bytes, byte-identical), and the littlefs
`lfs_file_size` public wrapper (`[0x004CFC2E,0x004CFC5C)`, 46 bytes; recovered
`lfs_t.mlist` at `0x28`).

Current overlay/component/package sizes are `142986 / 3666382 / 4444876`. The
apple-clang canonical build, byte-identical package, manifest verify, and Apollo
origin accounting pass fail-closed; the linux-clang profile pins await a Linux
toolchain regeneration.

## Latest milestone: nanopb private decoder loop

Private `pb_decode_inner` at `[0x0048FE98,0x00490112)` is now
source-recreated with explicitly partial helper closure. Rizin and the
fail-closed analyzer authenticate the 634-byte single-entry body, both direct
callers, no interior ingress, all outgoing calls, four diagnostics, neighboring
literal/wrapper spans, and 19 non-pointer table/text collisions. Apple places
one alignment byte, 522 text bytes, and 88 diagnostic bytes at
`[0x007B311F,0x007B3382)`. The stock memory-fill dependency is eliminated and
`pb_skip_field` is source-owned; six helper families remain pinned stock seams.

Current overlay/component/package sizes are
`127070 / 3650466 / 4428960`, with 1,068 placed, two unresolved, and five
container-only regions. Package ownership is 127,832 source bytes (2.886276%),
90,501 generated bytes (2.043392%), and 4,210,627 opaque/cut-forward bytes
(95.070333%); controlled ownership is 218,333 bytes (4.929667%). The next
nanopb frontier is the retained helper family: `pb_decode_tag`, defaults,
iterator operations, extension decoding, and `decode_field`. Linux/Clang 22
and hardware validation remain deferred.

## Latest milestone: nanopb tag decoder and short-enum ABI

Public `pb_decode_tag` at `[0x0048F66C,0x0048F6A0)` is now source-recreated
and source-closed. The analyzer authenticates its 52 bytes, three callers, sole
varint32/eof provider, neighboring functions, no alternate ingress, and no
stored pointers. Three stock `STRB` sites prove G2's one-byte
`pb_wire_type_t`; correcting the decoder-loop temporary changes its Apple text
from 522 to 530 bytes. The tag leaf adds two alignment bytes and 42 text bytes
at `[0x007B338A,0x007B33B6)`.

Current overlay/component/package sizes are
`127122 / 3650518 / 4429012`, with 1,070 placed, two unresolved, and five
container-only regions. Package ownership is 127,882 source bytes (2.887371%),
90,555 generated bytes (2.044587%), and 4,210,575 opaque/cut-forward bytes
(95.068042%); controlled ownership is 218,437 bytes (4.931958%). The private
decoder loop now retains six stock calls across five helper families. The next
frontier is `pb_message_set_to_defaults` and its iterator/default-value
dependencies; Linux/Clang 22 and hardware validation remain deferred.

## Latest audit: nanopb message defaults and accelerated source inference

`pb_message_set_to_defaults` is now bounded at
`[0x0048FDF2,0x0048FE98)`: 166 stock bytes, four direct callers, no alternate
or interior ingress, and no stored-pointer ingress. Its authenticated nanopb
0.4.9 source definition is `pb_decode.c[31080:32048]`. Four of seven outgoing
call sites already resolve to source-owned `pb_istream_from_buffer` and
`pb_decode_tag`; the remaining closure is only `decode_field`,
`pb_field_iter_next`, and `pb_field_set_to_default`. Boundary, source identity,
and call closure are 100% identified; source recreation and production
integration remain 0%, so package ownership stays 2.887371% source, 2.044587%
generated, and 95.068042% opaque/cut-forward.

The workflow now explicitly uses remembered upstream lineage and intermittent
web research to generate candidates, followed by immutable Git-object/source
span pins and release/commit compile matrices for proof. Local Ghidra 12.1.2
headless/PyGhidra and Rizin 0.9.1 were inventoried. Rizin produced this audit;
Ghidra requires the installed Homebrew OpenJDK 21 through an explicit
`JAVA_HOME`. `rz-ghidra`, BinDiff/BSim, and a disposable loopback-only Ghidra
MCP evaluation are the next tooling accelerators. See
`research/reverse-engineering-acceleration-strategy.md`.

## Latest audit: nanopb field-default recursion

`pb_field_set_to_default` is now 100% bounded and upstream-identified at
`[0x0048FCE2,0x0048FDF2)`: 272 stock bytes, one direct caller, five outgoing
calls, no alternate/interior ingress, and no stored-pointer ingress. A
four-release checkout matrix proves its 2,604-byte source definition is
byte-identical at nanopb 0.4.7, 0.4.8, 0.4.9, and 0.4.9.1. This narrows the
function to an exact compatibility interval but does not uniquely prove the
vendor checkout.

Rizin and a five-second targeted Ghidra noanalysis decompile independently
match extension recursion, optional/repeated/oneof initialization, submessage
recursion, static zeroing, and pointer reset. Pairing this function with the
already audited message-defaults loop will internalize three calls and remove
the released memory-fill dependency. The paired 438-byte candidate then has
only four fixed helper families: iterator begin, iterator begin-extension,
iterator next, and `decode_field`. Source recreation/integration remain 0%, so
package ownership remains 2.887371% source, 2.044587% generated, and
95.068042% opaque/cut-forward.

## Latest milestone: nanopb iterator production integration and release correction

The complete `[0x004D916E,0x004D9522)` nanopb `pb_common.c` iterator cluster
is now 100% bounded and source-recreated: 948 stock bytes across eleven
functions, with every direct caller, sixteen fixed calls, two dynamic callback
sites, one legitimate stored function pointer, and one classified data-island
branch collision authenticated. Nine isolated source leaves now production-route
all eight live iterator/callback entries through reviewed full-span redirects.
The 536 unreachable private stock bytes remain opaque rather than overclaimed.

This cluster closes six decoder/defaults call sites across five unique
iterator entries. Its only stock fixed dependency, the released memory-fill
routine, is removed by a local loop. A multi-address Ghidra noanalysis pass
decompiled seven functions in 6.3 seconds and independently matched the compact
descriptor ABI recovered by Rizin.

The Apple overlay/component/package are now 128,264 / 3,651,660 / 4,430,154
bytes. Package ownership is 129,014 source bytes (2.912179%), 90,977 generated
bytes (2.053585%), and 4,210,163 opaque bytes (95.034236%). The manifest has
1,022 Apollo-main regions and the flash plan places 1,094 regions with two
unresolved and five container-only records.

The upstream release audit now includes nanopb 0.4.9.1. Its only runtime
behavior change from 0.4.9 is in dead-stripped `pb_decode_ex`, and the firmware
build timestamp postdates the release. The corrected pristine candidate range
is 0.4.7--0.4.9.1; selected baseline 0.4.9 remains a compatibility choice, not
claimed vendor provenance.

## Latest milestone: nanopb paired defaults production integration

Private `pb_field_set_to_default` and `pb_message_set_to_defaults` are now
100% source-recreated and production-integrated. The complete 438 stock bytes
at `[0x0048FCE2,0x0048FE98)` are full-span redirects. Apple places 158 bytes
of message-default text at `0x007B382C`, two alignment bytes, and 256 bytes of
field-default text at `0x007B38CC`. The pair internalizes recursive defaults,
uses the source-owned iterator/stream/tag leaves, and removes the released
memory-fill dependency; only `decode_field @ 0x0048FBE4` remains fixed stock.

The Apple overlay/component/package are now 128,680 / 3,652,076 / 4,430,570
bytes. The 1,027-region Apollo manifest and 1,099 placed flash records account
for 129,428 source bytes (2.921249%), 91,417 generated bytes (2.063324%), and
4,209,725 opaque bytes (95.015427%). Two flash records remain unresolved and
five are container-only. Linux/Clang 22 replay and hardware execution remain
deferred; the next contiguous nanopb frontier is `decode_field` and its
extension/dispatch closure.

## Latest milestone: nanopb dispatch and extension production integration

Private `decode_field`, `default_extension_decoder`, and `decode_extension`
are now 100% bounded, upstream-identified, source-recreated, and
production-integrated. This corrects the old boundary label at `0x0048FC26`:
that entry is `default_extension_decoder`; `decode_extension` begins at
`0x0048FC88`. Three guarded redirects cover the executable stock spans, while
the 16-byte literal island `[0x0048FC78,0x0048FC88)` remains explicitly
opaque/cut-forward.

The source definitions are pinned to nanopb 0.4.9 commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`. Official-tag comparison shows
the three exact definitions are byte-identical from 0.4.4 through 0.4.9.1;
this establishes compatibility but does not uniquely identify the vendor
checkout. Apple places the closures/leaves at `0x007B39CC`, `0x007B3A14`, and
`0x007B3A70`; only the dynamic extension callback remains an intentional ABI
seam.

The production nanopb allowlist is now 38 functions. The reviewed Apple
overlay/component/package sizes are `128924/3652320/4430814`, and the
1,035-region Apollo manifest yields 1,107 placed, two unresolved, and five
container-only flash records. Package ownership is 129,671 source bytes
(2.926573%), 91,656 generated bytes (2.068604%), and 4,209,487 opaque or
cut-forward bytes (95.004823%); total controlled ownership is 4.995177%.

The next contiguous nanopb frontier is the field-decoder cluster:
`decode_static_field @ 0x0048F968`, the no-malloc pointer stub at
`0x0048FB1C`, and `decode_callback_field @ 0x0048FB30`, with
`decode_basic_field @ 0x0048F7F4` as the likely predecessor closure. Linux
aggregate replay, signing/flashing, and hardware execution remain deferred.

## Next-frontier seed: nanopb field decoders

Rizin and targeted Ghidra have now split and semantically checked the complete
1,008-byte field-decoder cluster `[0x0048F7F4,0x0048FBE4)`. Boundary/direct
call identification is 100%, semantic recovery is approximately 95%, and
source recreation/integration remain 0%. All external executable calls already
route to source except `pb_dec_fixed_length_bytes [0x0049053C,0x004905A8)`;
the two callback `BLX` sites are intentional schema ABI.

Official-tag source comparison shows `decode_basic_field` unchanged across
0.4.4--0.4.9.1, the current static definition from 0.4.5 onward, and current
pointer/callback definitions from 0.4.6 onward. The efficient next promotion
unit is the four-function cluster plus the 108-byte fixed-length-bytes decoder.
See `research/nanopb-field-decoder-cluster-boundary-audit.md`.

## Latest milestone: nanopb field-decoder production integration

The complete four-function field-decoder cluster
`[0x0048F7F4,0x0048FBE4)` plus `pb_dec_fixed_length_bytes`
`[0x0049053C,0x004905A8)` is now 100% bounded, upstream-identified,
source-recreated, host-qualified, and Apple-production-integrated. Five
guarded full-span redirects replace 1,116 stock executable bytes. The five
selector-isolated Apple closures contribute 1,132 source bytes and eight
alignment bytes at `[0x007B3AC0,0x007B3F34)`. All fixed calls resolve to
source-owned providers; the two dynamic callback sites remain intentional
application/schema ABI.

The fail-closed analyzer authenticates five stock entries, 26 fixed outgoing
calls, eight diagnostics, both callback sequences, all upstream definitions,
no stored entry pointers, and every apparent branch/pointer collision. Ten
host and target tests pass. The production nanopb allowlist is now 43
functions.

Current overlay/component/package sizes are
`130064/3653460/4431954`. The 1,049-region Apollo manifest and current flash
plan place 1,121 regions, preserve two unresolved records, and skip five
container-only records. Package ownership is 130,803 source bytes
(2.951362%), 92,780 generated bytes (2.093433%), and 4,208,371 opaque or
cut-forward bytes (94.955205%); controlled ownership is 223,583 bytes
(5.044795%). Linux/Clang 22 replay and hardware execution remain deferred.

## Latest milestone: AndersKaloer/Ring-Buffer production integration

The complete seven-function stock cluster at
`[0x00598134,0x0059823C)` is now upstream-identified, ABI-recovered,
host-qualified, and Apple-production-integrated. The authenticated compatible
commit interval is `cda00e1...190e30b`; `190e30b` is the maintained
source-equivalent selection, not an overclaim about Even's exact checkout.
Seven guarded redirects replace all 252 callable stock-span bytes (250
instructions plus two alignment bytes). The relocated
production leaves add 248 source bytes and four generated alignment bytes at
`[0x007B3F34,0x007B4030)` while reusing the authenticated stock assertion
provider and diagnostic strings.

Current overlay/component/package sizes are
`130316/3653712/4432206`, with package SHA-256
`a5625a4bcc1ff20ff9e339f9bb0a074d999508674c7aeb315101e653c90630c2`.
The 1,067-region Apollo manifest produces 1,139 placed, two unresolved, and
five container-only flash records. Ownership is 131,051 source bytes
(2.956789%), 93,036 generated bytes (2.099090%), and 4,208,119 opaque bytes
(94.944120%); controlled ownership is 224,087 bytes (5.055880%). Linux/Clang
replay and hardware execution remain deferred.

## Latest milestone: IAR void-EABI memory providers production integration

The authenticated `__aeabi_memmove` span `[0x00439710,0x004397A6)` and
`__aeabi_memcpy` span `[0x00439BE4,0x00439C8A)` are now 100% bounded,
ABI-recovered, source-recreated, host-emulated, instruction-count-qualified,
and production-integrated. The overlapping memcpy ownership is represented as
disjoint public and aligned-entry redirects. Three relocation-free source
sections add 626 bytes at `[0x007B4030,0x007B42A2)`; 316 stock bytes move from
opaque to generated ownership.

Apple overlay/component/package pins are
`130942/3654338/4432832`, with package SHA-256
`dbd7327ff42d80c8ff3b728ff9843f3a2b6e9bde3786bd68b929588d677539d5`.
The 1,075-region Apollo manifest produces 1,147 placed, two unresolved, and
five container-only records; the 822,357-byte flash plan hashes to
`27f1d981fb4e7ede7c0d39d4dfb15a039d309b4677a02c157ae9509b7d14ea9b`.
Package ownership is 131,677 source bytes (2.970494%), 93,352 generated
(2.105922%), and 4,207,803 opaque (94.923584%); controlled ownership is
225,029 bytes (5.076416%).

Lorelei recorded and twice replayed Linux overlay/component/package pins
`132810/3656206/4434700`, with package SHA-256
`03ec13df126c98f679e6e85c79cefea447943e746e74c8652e57ff71785ce2bf`.
The Linux plan places 896 regions with two unresolved. Hardware timing remains
deferred; exact EWARM release and DLIB archive options remain unresolved.

## Latest milestone: IAR `sqrtf` and errno quartet production integration

The final four retained code units in the bounded IAR census now have
selector-isolated clean-room source: hard-float `sqrtf`, EDOM and ERANGE
setters, and the errno-address accessor. Apple Clang 21 and Lorelei Linux
Clang 22.1.8 emit identical 28/20/20/10-byte section pins. The `sqrtf` leaf has
one declared tail relocation to the candidate EDOM helper; all other sections
are relocation-free.

Lorelei Unicorn matched 4,000 float bit patterns and 500 randomized executions
for each errno helper against authenticated stock, for 5,500 executions total.
Four stock-hash-guarded full-span redirects now install the 78 source bytes,
moving the final 72 bounded IAR executable bytes from opaque to generated
ownership. Bounded IAR source recreation and production integration are both
10/10 code units; no executable unit in this census remains retained.

Apple places the leaves at `[0x007B42A2,0x007B42F0)` and twice replayed
overlay/component/package sizes `131020/3654416/4432910`. Lorelei places them
at `[0x007B49EE,0x007B4A3C)` and twice replayed
`132888/3656284/4434778`. Canonical package ownership is 131,755 source
(2.972201%), 93,424 generated (2.107510%), and 4,207,731 opaque/cut-forward
(94.920289%); controlled ownership is 225,179 bytes (5.079711%). Exact EWARM
archive provenance remains independently unresolved.

## Latest tooling decision: Ghidra MCP remains an amortized lane

A disposable evaluation pinned `clearbluejar/pyghidra-mcp` v0.2.5 at
`f29063b8636100b71e9c3aec61fe056827c556e4`. It successfully opened a Ghidra
12.1.2 project and exposed 20 initial tools over stdio, but rejects raw
`BinaryLoader` imports and fails closed on read/decompile calls until a project
is marked fully analyzed. The current authenticated-address workflow obtains
multi-function decompilation in about five seconds with `-noanalysis`, so MCP
is deferred until semantic search or repeated whole-project exploration can
amortize full analysis/indexing. Details and resolved dependency versions are
in `research/reverse-engineering-acceleration-strategy.md`.

## Latest milestone: EM9305 ARCompact QP/C release ceiling

The controller application is now analyzed as Synopsys ARC EM7D/ARCv2 EM,
matching EM Microelectronic's documented QP/C-derived ARC framework. A
disposable Apache-2.0 Ghidra ARC extension, GNU ARC binutils on Lorelei, and
local Rizin bound a
3,052-byte assertion-rich cluster, a 144-byte QK scheduling candidate, the
60-byte eight-label module table, and all 31 direct calls to the shared
assertion handler. Twenty-nine calls are assigned to six portable QP modules;
the other two are `MyApp` and `WsfOs`. All remain stock-retained; this
milestone changes provenance and semantic coverage, not package byte ownership.

The decoded QK assertion-500 path checks only `p != 0`, retaining the v6.6.0+
ceiling. The 188-byte stock `QActive_post_` body restores interrupt status for
critical assertions (v6.3.2 behavior) and moves dynamic-event reference
increment ahead of the status branch (v6.3.6 behavior). Together these set an
official portable-body ancestry floor at v6.3.6 commit
`5550cca87dedf72d45250ad01e9cdeee8c4140ba`. Seven tags in six complete
eight-file source epochs survive through v6.6.0+; a vendor backport is still
possible. This raises QP/C release/configuration identification to 90–95%.
The QK ID-189 macro callsite
also matches `qk.c:189` throughout the checked interval. Object accesses recover `QF_MAX_ACTIVE=16`,
`QF_MAX_EPOOL=2`, two-byte signals, one-byte event-queue counters, two-byte
memory-pool size/counters, a 16-bit QK ready set, disabled Q-SPY, and the ARC
`CLRI; SYNC` / `SETI` critical-section ABI. `QF_init` additionally proves
`QF_MAX_TICK_RATE=0`, a 36-byte `QActive`, and an 8-byte `QK_attr_`.
Twenty-two portable functions from eight source units now occupy 2,450
hash-pinned bytes. The 602-byte complement is independently partitioned into
23 state-labeled, hash-pinned segments without gaps or overlaps. The
fail-closed analyzer and twelve tests reproduce the
stock identity, boundaries, 22 module references, 31-call topology, complete
module assignments, and six-instruction QK fingerprint. Full evidence is in
`research/em9305-qpc-arcompact-audit.md`.

The expanded ARCv2 EM epoch builder compiles all 80 comparison objects with
Lorelei's disposable GCC 16.1.1/binutils 2.46 toolchain and reduces ten source
epochs to seven normalized code epochs in 12.63 seconds at four jobs. The
objects are comparison-only and do not claim the stock compiler or vendor
port. The `--stock-compatible-only` lane builds 48 objects across six epochs
in 8.82 seconds and reduces them to three normalized code epochs. Three
builder-helper tests, three ARCv2-wrapper tests, and twelve analyzer tests pass.

## Latest milestone: EM9305 QP/C 6.5.1 and hook closure

A hash-pinned public EM9305 SDK v4.2 source oracle now selects exact upstream
QP/C release 6.5.1, official commit
`416dcec8820b9cdb5827497e645d0d9375db53c6`, from the independently recovered
v6.3.6--v6.6.0+ binary interval. The oracle is third-party commit
`e4412bc98d4e76d441d1226ca3696e53cfae5f54`, tree
`f5cb9ba00df71c2612d6d64cf39e05615a2feb64`; it is not proof of EM's exact
private checkout and is not accepted as licensed production source.

A 16-way isolated Lorelei Ghidra batch completed all EM9305 shards in
24.714--28.462 seconds and returned hash-manifested logs/status/results. Correlated
with the SDK symbols, GNU ARC decoding, Rizin, and raw stock pointers, it names
`QF_onResume`, `QF_onStartup`, inline `QF_resume`, `QK_onIdle`, `Q_onAssert`,
all extension/internal hooks, seven RAM callback globals, and nine terminal
function-pointer entries. At this intermediate milestone, the 602-byte cluster
complement was fully partitioned but its anonymous executable remainder was
concentrated in the 280-byte pre-QP hardware/port span plus internals of named
retained hooks; the following archive-comparison milestone supersedes that
classification and reduces anonymous executable cluster bytes to zero.
The full `Q_onAssertExt` boundary and 36-byte hook table are hash-pinned.

The analyzer now authenticates the SDK commit/tree and four oracle blobs as an
optional fail-closed input. Fourteen analyzer tests plus three epoch-builder
and three ARC-wrapper tests pass; the full 20-test EM9305 group also passes.

## Latest milestone: EM9305 vendor archive and compiler fingerprint closure

The SDK oracle contains relocation-bearing ARCv2 object archives. A new
fail-closed comparator authenticates QP/C, PML, sleep-manager, sleep-timer,
protocol-timer, and unitimer archives; masks only the four known ARC relocation
types; and scans every halfword-aligned application address. Six enforced
Lorelei lanes require 98 exact stock functions/7,172 bytes. Ninety-two are
globally unique fingerprints totaling 7,146 bytes; three QP internal hooks are
separately required to remain vendor-modified.

All 22 portable QP/C bodies now match the SDK build rather than merely a source
epoch. Archive metadata pins Synopsys MetaWare ARC T-2022.09 build 004 / LLVM
14.0.6, EM-Micro ARCv2 EM, `-Os`. The exact QK SWI port occupies
`[0x00302518,0x00302664)`, and `BSP_Init` is unique at
`[0x00302E80,0x00302E8E)`.

The former 280-byte anonymous QP-cluster prefix is now a protocol-timer
closure: a vendor-modified `ProtTimer_SetHwTriggerEnable` tail, exact
`ProtTimer_StoreConfig`, alignment, and exact
`ProtTimer_UpdateRestartTime`. Consequently all 3,052 cluster bytes are
function-identified across 26 hash-pinned remainder segments; anonymous
executable cluster bytes are zero. The 516-byte idle callee is named
`SLEEP_MANAGER_GoToSleep`, and its adjacent 52-byte RC-calibration callback is
an exact archive match. Full evidence is in
`research/em9305-sdk-archive-match-audit.md`.

## Latest milestone: EM9305 two-round Packetcraft/SDK function census

The optimized relocation matcher now uses an unmasked byte-run anchor followed
by a complete normalized comparison. It remains equivalent to exhaustive
halfword scanning but reduces the enforced QP/C archive lane to 0.32 seconds
on Lorelei. A new authenticated 16-job batch applies a 16-compared-byte floor
to controller, peripheral, LL PAL, EM system/HAL, radio, NVM, RC-calibration,
transport, and support archives. All 16 lanes passed; the largest profile
completed in 12.228 seconds.

The first raw 2,180 match records collapse without body conflicts to 1,146
distinct, non-overlapping stock functions / 132,610 bytes. A second
authenticated 32-archive pass produced 8,542 records / 1,201 distinct
address-body identities. Global deduplication rejects 1,134 already-proven
identities and promotes 67 new functions / 13,078 bytes. Together with the
prior six archives, the conservative lane covers 1,311 exact functions /
152,860 bytes. An 8-byte replay yields 129 additional candidates; independent
entry-boundary/xref qualification promotes 124 / 2,106 bytes and withholds
five. Exact-neighbor link-order tiling subsequently resolves 16 more exact
functions / 784 bytes and identifies 30 non-exact functions / 1,332 bytes.
The NOP-aware extension adds 156 functions / 9,818 stock bytes, including 34
exact bodies. Vector ABI resolution adds three exact interrupt handlers / 574
bytes and identifies the 186-byte modified radio-TX handler. The current exact
map is 1,494 functions in 875 intervals / 157,122 bytes, or 74.504950% of the
complete EM9305 application. Function provenance is identified for 167,684
bytes (79.513296%). The 43,204-byte remainder is partitioned into 264 vector
bytes, 1,812 alignment bytes, 7,470 post-text table/data bytes, and 33,658
unresolved code-or-mixed bytes.

`lib_emb_controller.a` is exact at 1,057 records / 1,055 address-body
fingerprints and proves the EM Bleu/Packetcraft Bluetooth-5.4 controller
profile (`BT_VER=13`, `LL_VER_NUM=28992`). Its 77 controller-only fingerprints
exclude the Bluetooth-5.2 peripheral profile as a complete stock explanation.
The second pass's `lib_emb_controller_iso.a` adds 62 ISO/BIG functions / 12,624
bytes, while `lib_em_system_di03.a` adds four NVM functions and `lib_aoad.a`
adds `AOAD_Init`. This exact link-time evidence means the adjacent non-ISO
profile header cannot be treated as the complete stock-link configuration,
although it does not by itself prove runtime activation of every ISO path.
Packetcraft's public repository stops at r20.05c/`LL_VER_NUM=1366`, so the
exact 2024 source state is pinned only to authenticated SDK blobs and remains
proprietary/unavailable as an authoritative public commit. The dynamic
per-function map and all report hashes are enforced by
`tools/analyze_em9305_sdk_discovery.py`; full evidence is in
`research/em9305-expanded-sdk-archive-census.md`.

The link-order analyzer now enforces 156 ranges / 202 functions across strict
and NOP-aware tiers. Its first nine same-size modified placements compare 942
of 1,008 non-relocation bytes exactly; the next 29 compare 3,815 of 3,868
(98.630%). The dominant deltas remain configuration/ABI changes, including a
912-byte stock connection-context stride versus the SDK's 900-byte layout.
Full status is in `research/em9305-sdk-link-order-recovery.md` and
`research/em9305-residual-segment-census.md`.

The next 16-way Lorelei Ghidra batch assigns separate large residual gaps to
isolated projects. All lanes completed in 17.644--17.993 seconds. The
experimental ARCompact decompiler emitted unusable constructor p-code for 15
entries; those remain candidate-only. Its one coherent 12-byte result is
independently exact-matched and named
`lctrSlvCheckEncOverridePowerControl @ 0x00329554`, so no Ghidra-only semantic
claim enters the ledger. Returned hashes and paths are pinned in the
[Lorelei benchmark](research/lorelei-re-acceleration-benchmark.md).

A third 16-way Lorelei batch targeted individual NOP-aware modified-function
entries and completed all projects in 16.766–17.023 seconds. The experimental
ARC processor produced no promotable semantics, but archive/GNU comparison
confirmed the 29 same-size identities at 98.630% aggregate meaningful-byte
similarity. Returned hashes, per-state residual accounting, and the remaining
33,658-byte queue are pinned in the
[residual segment census](research/em9305-residual-segment-census.md).

A fourth 16-way Lorelei batch processed 5,922 bytes across 16 previously
unprocessed residual spans in 17.217–17.502 seconds with no process failure.
Three entry-level decompilations were coherent and 13 hit the experimental ARC
constructor defect. Vector ABI and normalized archive matching subsequently
resolve the duplicated timer/radio interrupt wrappers: three exact bodies / 574
bytes and one modified 186-byte radio-TX role. The return-12 leaf remains
candidate-only.

## Current Cordio SMP-main identification increment

The retained G2 `smp_main.c` module is now source-identified across all twenty
linked functions / 3,076 code bytes in `[0x00537278,0x00537EEC)`. The one
remaining public API, `SmpDmGetLtk`, has no stock caller, pointer, or body and
is classified dead-stripped, leaving zero linked functions opaque within this
translation unit. Stock combines Packetcraft r20.05-family `keyReady` and
LESC behavior with AmbiqSuite 2.5.1's stale-AES queue cleanup. A tracked patch
over the authenticated Apache-2.0 r20.05c source reconstructs that combined
semantic candidate without claiming exact downstream text.

Lorelei compiled both the public and patched sources under `-Os` and `-O1`.
The two patched links retain code/BSS and close all 32 provider seams; the two
base links retained no code and are explicitly rejected as vacuous closure
evidence. The returned 5,247-byte archive and distilled ledgers are now
repository-owned and fail-closed. These bytes remain cut forward in
production: linked-function identification is 100%, while source recreation
and replacement remain 0% pending exact IAR/RTOS, logger, placement, and
relocation closure. See `docs/research/cordio-smp-main-source-recovery.md`.

## Current Cordio SMP secure-connections-main identification increment

The retained G2 `smp_sc_main.c` object is now source-identified across all 18
linked functions / 2,626 code bytes in `[0x0056CDC0,0x0056D8C4)`. Four public
definitions (`SmpScFree`, both peer-public-key accessors, and `SmpScSetOobCfg`)
have no stock body, caller, or stored pointer and are classified dead-stripped.
The remaining 194 bytes are bounded alignment and literal data.

Packetcraft r20.05 through r20.05c provides an invariant Apache-2.0 source
oracle. The stock event-name table includes `SMP_MSG_INT_CLEANUP` at `0x1F`,
which excludes the r19/AmbiqSuite 2.x message layout independently of adjacent
modules. The analyzer closes 111 exact-entry calls and rejects the only two
raw interior-looking byte windows as unaligned data overlaps. Production
ownership remains zero; see
`docs/research/cordio-smp-sc-main-source-recovery.md`.

## Current Cordio SMP secure-connections state-machine increment

The paired initiator/responder state-machine units now account for 2,431
identified bytes: 598 code bytes, 338 physical literal/pointer bytes, and 1,495
scattered interface/action/state-table bytes. The initiator object is
`[0x00537F14,0x005380DC)`; the responder object is
`[0x00538104,0x005382E4)`. All four source functions link and none is
dead-stripped.

Packetcraft r20.05--r20.05c is the exact public source oracle. Stock's
responder interface selects 55 actions and its API-pair-request table contains
the r20-only response-timeout and cleanup rows; r19/AmbiqSuite 2.x has 54
actions and neither row. The analyzer traverses and hashes all 80 state tables,
closes four exact callers, and finds no stored function entry or interior.
Production ownership remains zero; see
`docs/research/cordio-smp-sc-state-machines-source-recovery.md`.

## Current Cordio SMP common-action identification increment

The retained `smp_act.c` unit is now closed across all 25 definitions and the
full `[0x0056E5CC,0x0056F178)` object: 2,924 code bytes plus 64 bytes of owned
categories, literals, and alignment. The analyzer pins 78 direct calls and 62
stored action/callback entries and proves there is no stored strict-interior
address. No source definition is dead-stripped.

Packetcraft r20.05 through r20.05c supplies one invariant Apache-2.0 source
blob. Stock retains the r20-only security-request-timeout action and guarded
SC trace logic, independently excluding r19/AmbiqSuite 2.x. Production
ownership remains zero; see
`docs/research/cordio-smp-act-source-recovery.md`.

## Current Cordio SMP responder-action identification increment

The complete stock `smpr_act.c` object is now closed at
`[0x005E38C8,0x005E3D7C)`: all ten definitions contribute 1,160 code bytes
and three owned non-code ranges contribute 44 bytes. The legacy and Secure
Connections responder tables each retain all ten action entries. The only two
direct entry calls are intentional intra-TU helper calls; the whole-image scan
finds 20 exact stored entries and no strict-interior pointer.

Packetcraft r20.05 through r20.05c and the official later AmbiqSuite R4.4.1
import share one exact Apache-2.0 blob. Stock writes `keyReady=TRUE` at
`smpCcb_t+0x44` after storing the responder STK, selecting that source family
over r19/AmbiqSuite 2.x, whose body lacks the assignment. Production ownership
remains zero; see `docs/research/cordio-smpr-act-source-recovery.md`.

## Current Cordio SMP initiator-action identification increment

The complete stock `smpi_act.c` object is closed at
`[0x005E3118,0x005E3474)`: all ten definitions contribute 852 code bytes and
the owned `pSmpCfg`/`smpCb` island contributes eight bytes. Both initiator
action tables retain all ten entries, yielding 20 exact roots and no stored
strict-interior address. A lone raw BL-like hit is explicitly rejected as the
second halfword of a wide multiply.

Stock also writes `keyReady=TRUE` at `smpCcb_t+0x44` after deriving the
initiator STK. That r20 addition independently excludes r19/AmbiqSuite 2.x;
Packetcraft r20.05--r20.05c and the later R4.4.1 import share the selected
Apache-2.0 blob. Production ownership remains zero; see
`docs/research/cordio-smpi-act-source-recovery.md`.

## Current Cordio SMP Secure Connections role-action increment

The two role-specific SC action units are now fully closed. Initiator
`smpi_sc_act.c` occupies `[0x005E3474,0x005E38C8)` with all 16 definitions,
1,070 code bytes, and 38 owned tail bytes. Responder `smpr_sc_act.c` occupies
`[0x005E3D7C,0x005E4228)` with all 20 definitions, 1,162 code bytes, and 34
owned tail bytes. Their SC action tables provide 16 and 20 exact entry roots.
The responder's four direct entry calls are internal wrappers; neither unit
has exterior direct entry ingress or a genuine body-interior pointer.

Both stock DH-key-check paths write `keyReady=TRUE` at `smpCcb_t+0x44`. That
r20 addition independently excludes r19/AmbiqSuite 2.x. Packetcraft
r20.05--r20.05c and the later official R4.4.1 import share the selected exact
Apache-2.0 files. Production ownership remains zero; see
`docs/research/cordio-smpi-sc-act-source-recovery.md` and
`docs/research/cordio-smpr-sc-act-source-recovery.md`.

## Current Cordio SMP shared Secure Connections action increment

The complete shared `smp_sc_act.c` object is closed at
`[0x005E267C,0x005E3118)`: 20 linked definitions contribute 2,662 code bytes
and the owned F5/trace/literal tail contributes 54 bytes. The qualification-only
`SmpScEnableZeroDhKey` definition is compiled out by its default-false feature
guard. Nineteen direct calls and 26 stored pointer cells reach exact entries;
no genuine stored or branched address reaches a strict body interior.

Stock retains the `smpScProcPairing` no-input/no-output MITM branch present in
Packetcraft r19/AmbiqSuite 2.x and the later official R4.4.1 import, but removed
from Packetcraft r20.05--r20.05c. Combined with the already proven r20 message
and action-table ABI, this identifies an R4-style vendor hybrid rather than an
exact Packetcraft-r20 whole file. All twenty linked definitions are now
production-routed from bounded C: 2,258 compiled bytes plus 18 alignment bytes
replace all 2,662 stock body bytes. Six host-oracle groups and the canonical
component/package build pass. Authorized G2/EM9305 pairing and interoperability
qualification is blocked by unavailable physical evidence; future qualification requires that evidence, so physical validation is blocked by unavailable physical evidence;
see `docs/research/cordio-smp-sc-act-source-recovery.md`.

## Current Cordio SMP legacy state-machine increment

The two remaining legacy role state machines are closed. `SmpiInit` and
`SmprInit` contribute 44 code bytes inside two 40-byte physical initializer
objects. Their recovered interfaces traverse 52 action pointers, 29 state
pointers, and 31 terminated state tables, raising exact identified ownership
by 785 bytes. Both stock callers land at entries and no stored or direct
branch reaches an initializer interior.

The initiator tables are release-invariant. The responder's 27th action and
API-pair-request response-timeout/cleanup transitions independently select the
Apache-2.0 Packetcraft r20.05--r20.05c behavior over r19/AmbiqSuite 2.x. The
official R4.4.1 import is byte-identical later corroboration. Production now
routes both initializers to 88 compiled bytes and installs all 705 dispatch
bytes through 37 exact placements. Canonical component/package and offline
host/Thumb/table gates pass; G2/EM9305 legacy-pairing qualification is deferred
by project direction; future qualification requires authorized evidence. See
`docs/research/cordio-smp-legacy-state-machines-source-recovery.md`.

## Current Cordio non-SMP exclusion increment

The alternative three-function `smp_non.c` implementation is positively
configuration-excluded. The image has exactly two `L2cRegister` calls: ATT
owns CID 4 and linked `SmpHandlerInit` owns CID 6 with the already recovered
full-SMP data and control callbacks. There is no alternate CID-6 registration,
stored callback pointer, or non-SMP failure-response body.

This completes the source census for all 14 Packetcraft SMP translation units:
13 configured units are linked and mapped at function/table granularity, while
`smp_non.c` is the sole mutually exclusive source-only unit. Its r19 and r20/R4
definitions are identical; the selected optional public pin is Apache-2.0
Packetcraft r20.05c. Production ownership remains zero; see
`docs/research/cordio-smp-non-exclusion.md`.

## Current Ambiq Cordio HCI event-port increment

The proprietary Ambiq `hci_evt.c` boundary is now completely censused without
copying source. Stock links 79 of 80 definitions in
`[0x00569D4C,0x0056B7EC)`: 6,718 executable bytes plus 98 bytes of owned
alignment, literal, logger, and tail data. The only source-only definition is
`hciEvtGetStats`.

An 85-entry parser table roots 74 cells into 69 unique parser bodies; its
parallel 85-byte callback-size table, ten direct calls, retained path, and
absence of aligned strict-interior pointers close the remaining processors and
dispatchers. The exact 85-entry layout and retained diagnostic lines select
the later official AmbiqSuite R4.4.1 source family over R2.5.1's 67-entry
port. That later import is a proprietary reconstruction oracle, not a
historical producing-commit or reusable-source claim. Separately authored
clean-room C now production-routes all 79 linked bodies and target-compiles the
source-only getter; see `docs/research/cordio-hci-evt-source-recovery.md`.

## Current Ambiq Cordio HCI core increment

The adjacent proprietary `hci_core.c` boundary is also completely censused.
Stock links 22 of 24 definitions in `[0x0052A67C,0x0052AE38)`: 1,964 body
bytes plus a 16-byte literal pool. `hciCoreTxAclDataFragmented` and
`HciSetAclQueueWatermarks` are the only source-only definitions. Thirty-two
direct calls root every surviving entry; no aligned entry or strict-interior
pointer survives.

The 64-bit LE-feature API, three connection records, six CIS records, and
success-aware ACL transport select the later R4-era source family over
AmbiqSuite R2.5.1. Stock nevertheless omits both the later neuralSPOT send
delay and the still-later nsx priority/trace path, so no whole-file exact-text
claim is made. The file remains proprietary and contributes no production-
owned bytes. See `docs/research/cordio-hci-core-source-recovery.md`.

## Current Ambiq Cordio HCI platform-shim increment

The immediately following proprietary `hci_core_ps.c` object is now closed at
`[0x00530C00,0x00530D74)`. Nine linked definitions contribute 360 code bytes
and its literal pool contributes 12 bytes; eleven unused public getters are
source-only. Twenty-one direct calls root every linked entry, with no stored
entry or strict-interior pointer.

The handler's distinct ISO receive branch and the 64-bit LE-feature getter
independently exclude the 18-definition R2.5.1 source and select the
20-definition R4-era family. Packetcraft's public r20.05c dual-chip platform
behavior is Apache-2.0 and now supplies the reusable behavior source; the
proprietary Ambiq import remains corroboration only. All 20 definitions are
implemented over the authenticated G2 offsets. Nine linked entries replace
all 360 stock body bytes with 514 compiled bytes plus six alignment bytes
under 13 strict relocations; all eleven source-only getters target-compile.
Host tests cover initialization, completed-buffer accounting and saturation,
flow re-enable, RX queueing, timeout/event/ACL/ISO dispatch, callback absence,
unknown types, and all getter offsets. `make cordio-hci-core-ps-closure` is
green. Live controller/ISO/RF/timing validation is blocked by unavailable physical evidence; future qualification requires authorized responsive G2/EM9305 evidence. See
`docs/research/cordio-hci-core-ps-source-recovery.md`.

## Current Ambiq Cordio HCI transport increment

The proprietary `hci_tr.c` transport object is now closed at
`[0x0053013C,0x00530364)`. Three linked definitions contribute 524 code bytes
and seven receive-state literals contribute 28 bytes; only
`hciTrReceivingPacket` is source-only. Four direct callers and six outbound
provider calls close the object without any stored entry or strict-interior
pointer.

The ACL sender returns the packet length or zero, the command sender returns
success, and neither frees or completes the transmit buffer. Those ownership
semantics plus the receive length/type checks exclude AmbiqSuite R2.5.1 and
select the later R4-era behavior family. A project-original clean-room C
implementation now owns all four definitions: the three linked entries replace
all 524 stock body bytes with 454 compiled bytes under six strict relocations,
and `hciTrReceivingPacket` target-compiles as the sole source-only definition.
Host tests cover exact TX ownership, event and ACL assembly, arbitrary
chunking, back-to-back packets, oversize/invalid/allocation/null failures, and
atomic rejection-state reset. The maintained source copies no proprietary
bytes. `make cordio-hci-tr-closure` verifies the source, Cortex-M55 build,
routes, component, manifest, deterministic package, and flash plan. Live
controller/RF/timing validation is blocked by unavailable physical evidence; future qualification requires authorized
responsive G2/EM9305 evidence. See
`docs/research/cordio-hci-tr-source-recovery.md`.

## Current Ambiq Cordio HCI command increment

The shared proprietary `hci_cmd.c` object is now completely censused at
`[0x0052AE38,0x0052B8A4)`. Fifty linked definitions contribute 2,654 code
bytes and one alignment/literal island contributes 14 bytes; the remaining
22 of the later 72-definition inventory are source-only. The linked command
surface includes legacy, data-length, privacy, vendor, and peer-SCA wrappers.

The analyzer pins every body hash, 156 direct ingress calls, all 127 direct
calls issued by the TU, the queue/timer control block at `0x20073A90`, and
the absence of legitimate stored entry or strict-interior pointers. Its one
interior-looking word is independently classified as packed non-code data.
The exact later AmbiqSuite R4.4.1 source inventory is a proprietary
reconstruction oracle, not a historical commit or reusable-source claim.
All 72 command APIs are now maintained in clean-room C. Fifty guarded routes
replace all 2,654 linked stock bytes with 4,052 compiled Thumb bytes plus 68
alignment bytes under 106 strict relocations, and all 22 source-only APIs
target-compile. Host tests cover allocation bounds, queue ownership, transport
retry, completion credits, timeout recovery, queue draining, reset, standard
payload families, radio-test V3, and null/length rejection. The command-layer
software gap is closed; HCI event-port and driver admission remain. See
`docs/research/cordio-hci-cmd-source-recovery.md`.

## Current Ambiq Apollo3 HCI-driver increment

The controller-facing Apollo3 driver is now fully censused: 12 of 16 source
definitions link for 1,188 body bytes. Its main interval is
`[0x004B48A6,0x004B4D2C)`; `error_check` is separately retained at
`[0x004B47AE,0x004B47CC)`. Thirty direct ingress sites, all 66 outbound calls,
one intentional WSF handler pointer, and zero accepted strict-interior ingress
close the surviving surface. Four unused control APIs are source-only.

Stock is a mixed-version Ambiq implementation rather than an exact archived
file: the blocking transport and radio lifecycle follow the Apollo3 family,
the handler's null-message guard matches the later R3.1.1 import, and the VSC
tail uses later `0xFCC4`, `0xFC43`, and `0xFFF2` command semantics corroborated
by the R4.4.1 Cooper driver. The source carries an Ambiq BSD-style notice, but
the repository imports no implementation bytes and production ownership stays
zero. See `docs/research/cordio-hci-driver-source-recovery.md`.

The full vector-table follow-up corrects one earlier boundary assumption:
`HciDrvIntService` is retained but has no direct caller or stored/vector
pointer. Vector slot 75 is inside the OTA and instead reaches the Apollo510
`GPIO0_607F` handler below.

## Current product BLE-startup increment

The product startup boundary now closes twelve `app_ble.c` bodies plus one
interposed Apollo510 GPIO vector body, 3,236 code bytes in a 3,242-byte mixed
physical interval. The recovered prefix adds the exact DM/ATT/CCC forwarding
callbacks, delayed callback, product message state machine, and subsystem
initializer. The registered `_bleCommHandler`, handler/config initializer,
and stack-registration body close product dispatch, the runtime SMP config
pointer, connection client 3, and the six-entry CCC set.

`_bleExactleStackInit` initializes the 10,560-byte WSF pool, security, and the
HCI/DM/L2CAP/ATT/SMP/application/product/driver handler chain. The startup
wrapper performs radio shutdown, a 100-us delay, boot, stack/profile setup,
`DmDevReset`, and a 10-second delayed callback; the six-byte address getter
returns `0x200737BF`.

Nine direct entry calls, 267 outbound calls, seven stored pointers, and zero
strict-interior ingress are pinned. Ownership is intentionally discontinuous:
`[0x004B80BE,0x004B80EA)` is vector index 75 / external IRQ 59,
`GPIO0_607F_IRQn`, not product `app_ble.c` and not a BLE transport ISR. Two
unaligned interior-looking byte windows are rejected as packed data. The
R2.5.1 FIT radio task is only a semantic topology oracle; no exact product
source or historical commit is claimed. Four clean-room files now cover all
twelve product bodies / 3,192 stock code bytes and pass host plus freestanding
Thumb checks. The recovered `bleProcMsg` candidate includes its full event
switch, notification map, connection/CCC teardown, reconnect timers, security
forwarding, and delayed-start control path. The GPIO vector remains separately
owned. Production ownership remains zero while placement, logger bindings,
and redirects remain deferred.
See `docs/research/g2-app-ble-startup-recovery.md`.

## Current Ambiq HCI vendor reset-sequence increment

The adjoining vendor/reset object is closed at
`[0x00569B04,0x00569D4C)`: four linked functions contribute 546 code bytes
and a 38-byte alignment/literal tail; four trivial or bypassed hooks are
source-only. Five direct ingress calls and all 25 provider calls are pinned,
with no stored or branched strict-interior target.

The exact product chain is Reset plus custom BD-address update, followed on
completion by NVDS `0xFFF2`, RF power `0xFCC4` with parameter 6, standard
event masks and controller discovery, then four LE Random completions. This
order is a hybrid of the Apollo3 and later Cooper families and matches neither
official file wholesale. Production ownership remains zero. See
`docs/research/cordio-hci-vs-reset-sequence-recovery.md`.

## Current Cordio HCI PHY-command increment

The three-definition Apache `hci_cmd_phy.c` census is complete. Stock retains
only `HciLeSetPhyCmd` at `[0x00539E48,0x00539E94)`: 74 executable bytes plus
two alignment bytes. `HciLeReadPhyCmd` and `HciLeSetDefaultPhyCmd` are
source-only, matching the already closed DM PHY API census.

The sole `DmSetPhy` caller and exact `hciCmdAlloc(0x2032, 7)` / `hciCmdSend`
provider pair close the wrapper without stored or interior ingress. AmbiqSuite
R2.5.1 and Packetcraft r20.05c share exact definition bodies; the latter is
the safe public source route. Production ownership remains zero. See
`docs/research/cordio-hci-cmd-phy-source-recovery.md`.

## Current optional HCI command exclusion

The six modern command-only TUs `hci_cmd_ae/bis/cis/cte/iso/past.c` are now
excluded from stock with a complete 57-definition census. Every wrapper has
one mandatory `hciCmdAlloc` call; all 45 stock allocator callers are already
owned by the closed shared command object or `HciLeSetPhyCmd`. No unexplained
caller or retained source marker survives.

These findings classify the extended-advertising, broadcast/connected ISO,
CTE, ISO data-path/test, and PAST command surfaces as source-only while making
no claim about independently linked receive-event parsers. The files are
proprietary compatibility oracles and contribute no production bytes. See
`docs/research/cordio-hci-optional-command-exclusion.md`.

## Current Cordio ATT server-signing partial-inclusion increment

The retained `atts_sign.c` object is completely partitioned at
`[0x0052DA58,0x0052DBF0)`: four linked state/configuration functions contribute
370 code bytes, while 38 bytes hold alignment and owned trace/path/global
literals. The surviving three public APIs save or restore the peer CSRK,
CSRK-authentication flag, and sign counter through a 56-byte, three-record
control block at `0x2007335C`.

The signed-write CMAC worker, PDU processor, completion callback, and
`AttsSignInit` are dead-stripped. `AttsInit` leaves `signMsgCback` on
`attEmptyHandler`; the image has no later install, no signed-write CMAC call,
and none of the processing-only failure strings. This is a configuration-only
partial link, not active ATT signed-write verification.

Stock's 16-byte connection record and three-argument `AttsSetCsrk` match the
official later AmbiqSuite R4.4.1 authenticated-CSRK extension and exclude the
12-byte/two-argument Packetcraft r20 API. The later import is an Apache-2.0
reconstruction oracle, not a resolved historical producing commit. Production
ownership remains zero; see
`docs/research/cordio-atts-sign-source-recovery.md`.

## Current Cordio ATT indication/notification increment

The complete stock `atts_ind.c` object is now closed at
`[0x005338AC,0x00533EF4)`: thirteen linked functions contribute 1,552 code
bytes and three owned gaps contribute 56 category/literal bytes. The interface
table roots the control, message, and connection callbacks; the authenticated
IAR initializer independently populates method 15 with `attsProcValueCnf` in
the live SRAM ATT processor table. Twenty-two direct calls and three registered
entries land only at exact boundaries; the matching raw flash word is part of
the compressed initializer stream rather than a fourth runtime pointer cell.

Stock's nine 64-byte server CCBs, three-bearer loops, slot-aware timer/message
parameters, and client-change-awareness flow decisively select the Packetcraft
r20 EATT architecture over r19/AmbiqSuite 2.x. Packetcraft r20.05--r20.05c and
the later official AmbiqSuite R4.4.1 import share one exact Apache-2.0 source
blob. Maintained C now owns all thirteen linked entries through guarded
redirects: 1,602 compiled bytes plus 16 alignment bytes under 51 strict
relocations replace all 1,552 stock body bytes. Both dead-stripped zero-copy
wrappers are implemented and target-compiled without inventing linked stock
coverage. Host state-machine, selector, component, manifest, package, flash-
plan, and deterministic verification gates are green; live ATT/EATT peer and
controller validation is blocked by unavailable physical evidence; future qualification requires authorized responsive G2
evidence. See `docs/research/cordio-atts-ind-source-recovery.md`.

## Current Cordio ATT server-owner/dispatcher increment

The complete stock `atts_main.c` object is now closed at
`[0x0053498C,0x00535488)`: seventeen linked functions contribute 2,710 code
bytes and six owned gaps contribute 102 category, alignment, and literal
bytes. All 21 source definitions are accounted; `AttsAuthorRegister`,
`AttsSetAttr`, `AttsGetAttr`, and `AttsErrorTest` have no standalone stock
body, caller, or stored entry. Forty-five direct calls and four callback-table
entries land only at exact boundaries.

The authenticated IAR scatter record reconstructs the complete 18-entry live
`attsProcFcnTbl` at `0x2000045C`; methods 1--12 and 16 route to linked request
processors, method 15 routes to `attsProcValueCnf`, and signed-write method 17
remains null. Stock also retains the later R4.4.1 ATT data-length hardening
absent from public r20.05c. The official later import is therefore the exact
behavioral oracle while Packetcraft r20.05c remains the public ancestry base.
Maintained C now owns all seventeen linked entries through guarded redirects:
2,622 compiled bytes plus 30 alignment bytes under 44 strict relocations
replace all 2,710 stock body bytes. All four source-only public helpers are
implemented and target-compiled. Hardened dispatch, CCB, timer, prepared-
write, database-hash, group-mutation, initialization, component, manifest,
package, flash-plan, and deterministic gates are green. Live ATT/EATT peer,
controller, CMAC timing, and EM9305 behavior is blocked by unavailable physical evidence; future qualification requires authorized responsive evidence; see
`docs/research/cordio-atts-main-source-recovery.md`.

## Current Cordio common ATT server-processor increment

The complete stock `atts_proc.c` object is closed at
`[0x0056C550,0x0056CDC0)`: all nine source functions contribute 2,106 code
bytes and two owned gaps contribute 54 data bytes. Twenty-six direct calls
reach shared UUID, lookup, and permission helpers. Four additional live roots
enter the MTU, find-info, read, and read-multiple-variable processors through
methods 1, 2, 5, and 16 of the initialized SRAM dispatch table.

Packetcraft r20.05--r20.05c and the official later R4.4.1 import share one
exact Apache-2.0 blob. The EATT MTU gate and read-multiple-variable processor
exclude the smaller r19/AmbiqSuite 2.x source. No source definition is
dead-stripped and no strict-interior ingress survives. Production ownership
remains zero; see `docs/research/cordio-atts-proc-source-recovery.md`.

## Current Cordio ATT core increment

The complete stock `att_main.c` object is closed at
`[0x004B4DE0,0x004B5230)`: 21 linked definitions contribute 1,030 code
bytes and five owned gaps contribute 74 data/alignment bytes. Sixty-five
direct BL sites and 14 registered pointers reach exact entries; no decoded
branch reaches a strict interior. `attCcbByHandle` and public `AttMsgAlloc`
are the only two source-only APIs.

`AttHandlerInit` pins `attCb=0x200610AC`, the three-connection/three-bearer
layout, and exact legacy and enhanced default interfaces at `0x007851E0`
and `0x007851F0`. Message routing uses thresholds `0x20/0x40/0x60/0x80`,
excluding the r19 single-bearer source. Packetcraft r20.05c and the later
official R4.4.1 import have identical implementation text. Production
ownership remains zero; see `docs/research/cordio-att-main-source-recovery.md`.

## Current Cordio enhanced ATT server exclusion

The optional `atts_eatt.c` TU is absent: all twelve source definitions are
source-only/dead-stripped. The exact no-op EATT server interface installed at
`attCb+0x44` is never replaced, `attCcbByConnId` and the common handle-value
worker have no enhanced callers, and the separately closed L2CAP CoC census
has zero linked functions. This is a positive initialization/provider closure,
not a conclusion from missing names alone. See
`docs/research/cordio-atts-eatt-exclusion.md`.

## Current Cordio dynamic ATT service exclusion

The optional `atts_dyn.c` TU is absent: all seven definitions are
source-only/dead-stripped and its 1,280-byte private heap is not instantiated.
The exact `AttsAddGroup` and `AttsRemoveGroup` caller closures contain only
the linked static service/CSF paths, with no dynamic provider. Together with
the EATT exclusion, every ATT server TU in the selected source family is now
accounted. See `docs/research/cordio-atts-dyn-exclusion.md`.

## Current Cordio enhanced ATT core/client exclusion

The optional `att_eatt.c` and `attc_eatt.c` TUs are absent: all 26 core and
all 20 client definitions are source-only/dead-stripped. `EattInit` never
installs the handler, DM callback, or CoC transmit function at
`attCb+0x4C/+0x50/+0x54`; `EattcInit` never replaces the enhanced-client
default at `attCb+0x48`. The independently closed L2CAP CoC TU has zero linked
functions, and the exact ATT allocator/ATTC CCB provider sets contain no EATT
client callers. Together with the existing enhanced-server exclusion, no
enhanced bearer implementation survives despite the common r20/R4
multi-bearer ABI. See `docs/research/cordio-att-eatt-exclusion.md` and
`docs/research/cordio-attc-eatt-exclusion.md`.

## Current Cordio ATT UUID constant-object increment

The final unaccounted ATT-family TU, data-only `att_uuid.c`, is now completely
censused. Stock retains 11 of 152 two-byte UUID objects in the exact
source-ordered block `[0x0078F53A,0x0078F550)`, 22 bytes, while the other 141
objects are source-only/dead-stripped. A whole-image unaligned scan closes all
54 stored references to those 11 entries; every reference cell is naturally
four-byte aligned and no accidental window is accepted.

Packetcraft r20.05c and the later official R4.4.1 import share one exact
Apache-2.0 source blob. The legacy r19 source already contains every retained
object, so this TU is not independently release-discriminating even though
the surrounding ATT architecture proves r20/R4. Numeric UUID duplicates in
application service tables are explicitly excluded from TU ownership.
Production ownership remains zero; see
`docs/research/cordio-att-uuid-source-recovery.md`.

## Current Cordio optional ATT server-read increment

The complete stock `atts_read.c` object is closed at
`[0x0056D93C,0x0056E4F8)`: all seven source definitions contribute 2,984
code bytes and the owned UUID/global tail contributes 20 bytes. Nine direct
calls reach its two range helpers; methods 3, 4, 6, 7, and 8 of the decoded
live SRAM processor table root the five request processors. Fifty decoded
direct calls leave the TU, with three raw BL-like wide-instruction overlaps
explicitly excluded.

Stock retains the r20 CSF database-hash path and uses the subtraction-safe
fit-check topology found in the later official AmbiqSuite R4.4.1 source fix
for IAR high optimization. R4 is the closest behavioral oracle; its later
import is not claimed as the historical producer. No source definition is
dead-stripped and no accepted strict-interior ingress survives. Maintained C
now owns all seven entries through guarded redirects: 2,786 compiled bytes
plus eight alignment bytes under 44 strict relocations replace all 2,984 stock
body bytes. Host and selector tests plus component, manifest, package, flash-
plan, and deterministic verification are green. Live ATT peer/controller
behavior is blocked by unavailable physical evidence; future qualification requires authorized responsive physical evidence;
see `docs/research/cordio-atts-read-source-recovery.md`.

## Current Cordio ATT server-write increment

The complete stock `atts_write.c` object is closed at
`[0x005A5D94,0x005A6260)`: four linked definitions contribute 1,220 code
bytes and the owned `attsCb`/configuration tail contributes eight bytes.
Methods 9 and 10 share the write processor; methods 11 and 12 root prepare
and execute write. The authenticated live table closes all four cells.

One source API, `AttsContinueWriteReq`, is dead-stripped. Stock can record an
`ATT_RSP_PENDING` callback result, but this product does not link the public
continuation entry. Twenty-eight decoded outbound calls, one internal helper
call, and the initializer-stream entry are closed without accepted interior
ingress. Packetcraft r20.05--r20.05c and the later R4.4.1 import share one
exact Apache-2.0 source blob. All four linked entries are now guarded-routed to
1,644 compiled Cortex-M55 bytes plus 12 alignment bytes under 25 strict
relocations, replacing all 1,220 stock body bytes. The source-only continuation
API is also implemented and ARM-compiled without inventing stock coverage.
Host, component, manifest, deterministic-package, flash-plan, and analyzer
gates are green; physical peer/controller/EM9305 behavior is explicitly
is blocked by unavailable physical evidence; future qualification requires authorized responsive hardware. See
`docs/research/cordio-atts-write-source-recovery.md`.

## Current G2 BLE WSF-thread increment

The product `platform\threads\thread_ble_wsf.c` TU is now completely bounded
at `[0x004D0A4C,0x004D0D24)`: twelve linked functions contribute 656 code
bytes and the owned literal pool contributes 72 bytes. The aligned stored task
entry, 27 direct BL sites, 50 outbound calls, static CMSIS task attributes,
and every retained diagnostic are pinned; no accepted strict-interior ingress
survives.

The `ble_wsf` task uses a 16-KiB static stack and 112-byte CMSIS control block,
starts the already-closed product BLE wrapper, then runs `WsfOsDispatcher`
forever. A max-one, initially available semaphore implements transmit-ready
flow control with a twenty-iteration/400-ms diagnostic bound and duplicate
completion suppression.

The exact product source and historical generating commit remain unresolved.
CMSIS-FreeRTOS v10.5.1 authenticates provider ABIs and AmbiqSuite R2.5.1
supplies only a related WSF topology oracle. A three-file clean-room candidate
now covers all twelve entries, passes host behavioral tests, and compiles for
a freestanding Thumb target. Production integration remains zero while
placement, redirects, and retained logger bindings are deferred. See
`docs/research/g2-thread-ble-wsf-recovery.md`.

## Current G2 BLE message-thread increment

Both product BLE message-thread units are now completely bounded. The TX unit
`[0x00475290,0x00475FC0)` contains 21 bodies / 3,096 code bytes and 280 owned
data bytes; its existing clean-room replacement now has whole-object and
ingress closure. The RX unit `[0x0048EDB0,0x0048F3A4)` contains 13 bodies /
1,390 code bytes and 134 owned data bytes, ending exactly where nanopb begins.

Static task attributes, 150-entry queues, lifecycle state, queue/exit flags,
TX command types, eleven RX message classes, 163 direct entry sites, 283
outbound calls, and four genuine stored entries are pinned. All raw
strict-interior and unaligned lookalikes are rejected, including the sole RX
BL-like halfword overlap. TX ownership is unchanged. An independently
authored five-file RX candidate now covers all 13 entries and passes host and
freestanding Thumb compilation tests, but diagnostic parity and placement-
sensitive production routing remain pending; stock RX code still executes.
See
`docs/research/g2-thread-ble-message-recovery.md`.

## Current G2 NVDB buzzer increment

The complete first-party `service_nvdb_buzzer.c` object is now bounded at
`[0x0058F9D4,0x0058FAAC)`: five functions contribute 188 code bytes and its
owned literal tail contributes 28 bytes. Two stored initialization roots, five
direct entry calls, eleven outbound/internal calls, and zero accepted
strict-interior ingress close the object.

The twelve-byte `nvBuzzer` record is version 2 with boot defaults 4,000 Hz and
30% duty. Its default initializer computes CCITT-FALSE `0x9B1E` across the
first ten bytes. The exact missing/pre-v2 migration policy and its unusual
CRC-field comparison are now host-tested by a clean-room five-function
candidate that also compiles for freestanding Thumb. Production routing and
ownership remain zero pending placement, diagnostics, and guarded redirects.
See `docs/research/g2-nvdb-buzzer-recovery.md`.

## Current G2 NVDB product-mode increment

The adjacent `service_nvdb_product_mode.c` object is now closed at
`[0x004ABD90,0x004ABEC8)`: six functions / 270 code bytes and 42 owned data
bytes. Two stored roots, 54 direct entry calls, 18 provider/internal calls, and
zero strict-interior ingress are pinned. The four-byte version/mode/CRC record,
`0x2E3E` default checksum, migration policy, RAM-only setter, persistent
updater, and unvalidated read/import behavior all pass host and Thumb tests.
Production routing and ownership remain zero. See
`docs/research/g2-nvdb-product-mode-recovery.md`.

## Current G2 NVDB MAC increment

The retained `service_nvdb_mac.c` object is now closed at
`[0x005D9F48,0x005DA080)`: three functions contribute 280 code bytes and the
owned literal tail contributes 32 bytes. Two stored initialization roots, two
direct updater calls, eighteen provider/internal calls, and zero accepted
strict-interior ingress close the object.

The ten-byte `nvMAC` record is version 1. Its six-byte BLE static-random
address is device-dependent: the default builder processes little-endian
`CHIPID1 || CHIPID0`, uses reflected CRC-32 for the first four address bytes,
CCITT-FALSE for the last two, applies `(last & 0xFC) | 0xC0`, and checksums the
first eight record bytes. The exact missing/v0 migration policy is host-tested
by a clean-room three-function candidate that also compiles for freestanding
Thumb. Production routing and ownership remain zero pending placement,
diagnostics, provider binding, and guarded redirects. See
`docs/research/g2-nvdb-mac-recovery.md`.

## Current G2 NVDB advertising-magic increment

The anonymous three-function NVDB object immediately preceding the MAC helper
is now closed at `[0x005D9ED0,0x005D9F48)`: 110 code bytes and a ten-byte
alignment/literal tail. Two stored roots, two internal updater calls, six total
body calls, and zero accepted strict-interior ingress account for the complete
object.

Its four-byte `nvAdvMagic` record at `0x200038D4` is version 1 with default
magic `0x20`; initialization computes CCITT-FALSE `0x0A5C` over its first two
bytes. A clean-room three-function candidate preserves its missing/v0 rewrite
policy and unusual CRC-field comparison, passes host and Thumb tests, and
remains outside production routing. Because stock retains no path or function
name for this TU, attribution is limited to the exact key/record/table-root
closure. See `docs/research/g2-nvdb-adv-magic-recovery.md`.

## Current G2 NVDB sensor-calibration increment

The retained `service_nvdb_sensor_caldata.c` object is now completely bounded
at `[0x00509764,0x00509B48)`: eight functions contribute 900 code bytes and
96 alignment/literal bytes. Four stored initialization roots, ten direct entry
calls, fifty provider/internal calls, and no accepted strict-interior ingress
close the object.

The 92-byte `nvSCald` and 68-byte `nvSCaldAG` ABIs are pinned, including both
factory payloads, CRC offsets and initialized values (`0xD886` and `0x82FC`).
The primary non-importing v0 migration quirk, partial AG updates, direct AG
read/import path, and narrow matrix fallback pattern are host-tested by an
eight-function clean-room candidate that also compiles for freestanding Thumb.
Production routing and ownership remain zero. See
`docs/research/g2-nvdb-sensor-caldata-recovery.md`.

## Current G2 NVDB system-data increment

The retained `service_nvdb_sys_dt.c` object is now completely bounded at
`[0x004AEE28,0x004B03E0)`: thirteen functions contribute 5,084 code bytes and
seven split alignment/literal regions contribute 476 bytes. Two stored
initialization roots, 37 direct entry calls, 299 provider/internal calls, and
no accepted strict-interior ingress close the object.

The 172-byte `nvSysDt` record, exact initialized SRAM bytes, first-38-byte CRC
(`0x1DC7` after default initialization), thirteen indexed fields, 40-entry
legacy PSN table, parser, aging reset, and eight-slot OTP PSN journal are
pinned. Migration is correctly modeled as a non-importing audit: it runs the
legacy PSN scan, prefers the newest valid OTP PSN, and rewrites only missing or
pre-v2 CRC-mismatched data; it does not reset aging. A thirteen-function
clean-room candidate passes host and freestanding Thumb tests. Production
routing and ownership remain zero. See
`docs/research/g2-nvdb-sys-dt-recovery.md`.

## Current G2 KVDB temperature-unit increment

The retained `service_kvdb_temperature_unit.c` object is now completely
bounded at `[0x0049B014,0x0049B198)`: three functions contribute 338 code
bytes and the owned tail contributes 50 bytes. Two stored callback roots,
three direct entry calls, 21 provider/internal calls, and zero strict-interior
ingress close the object.

The twelve-byte `kvTemperatureUnit` factory record, version/CRC layout, default
checksum `0x76ED`, whole-record writer, and non-importing v0 migration policy
are pinned and host-tested. The candidate also compiles as exactly three
freestanding Thumb symbols. Production routing and ownership remain zero. See
`docs/research/g2-kvdb-temperature-unit-recovery.md`.

## Current G2 KVDB time-format increment

The immediately adjacent retained `service_kvdb_time_format.c` object is now
completely bounded at `[0x0049AE90,0x0049B014)`: three functions contribute
338 code bytes and the owned tail contributes 50 bytes. Two stored callback
roots, three direct entry calls, 21 provider/internal calls, and zero
strict-interior ingress close the object.

The twelve-byte `kvTimeFormat` factory record at `0x20003818`, version/CRC
layout, default checksum `0x76ED`, whole-record writer, and non-importing v0
migration policy are pinned and host-tested. The candidate also compiles as
exactly three freestanding Thumb symbols. Production routing and ownership
remain zero. See `docs/research/g2-kvdb-time-format-recovery.md`.

## Current G2 KVDB universal-setting increment

The retained `service_kvdb_universal_setting.c` object is completely bounded
at `[0x0049AD0C,0x0049AE90)`: three functions contribute 340 code bytes and
the owned tail contributes 48 bytes. Two stored roots, three direct entry
calls, 22 provider/internal calls, and zero strict-interior ingress close it.

The twenty-byte `kvUniversalSetting` record at `0x20003824` has version 3,
CRC at offset 18, initialized checksum `0xA967`, a whole-record writer, and a
non-importing pre-v3 migration policy. The host-tested candidate also compiles
as exactly three freestanding Thumb symbols. Production routing and ownership
remain zero. See `docs/research/g2-kvdb-universal-setting-recovery.md`.

## Current G2 primary KVDB setting increment

The retained `service_kvdb_setting.c` object is completely bounded at
`[0x004AEB20,0x004AECA4)`: three functions contribute 340 code bytes and the
owned tail contributes 48 bytes. Two stored roots, three direct entry calls,
22 provider/internal calls, and zero strict-interior ingress close it.

The 28-byte `kvSetting` record at `0x200037E0` has CRC at offset 24. Its
factory image is version 1 with initialized CRC `0xA288`; persistence upgrades
it to version 4 and CRC `0x4987`. The writer and non-importing pre-v4 migration
policy are host-tested, and the candidate compiles as exactly three Thumb
symbols. Production routing and ownership remain zero. See
`docs/research/g2-kvdb-setting-recovery.md`.

## Current G2 KVDB ALS-scale increment

The immediately adjacent retained `service_kvdb_als_scale.c` object is
completely bounded at `[0x004AECA4,0x004AEE28)`: three functions contribute
338 code bytes and the owned tail contributes 50 bytes. Two stored roots,
three direct entry calls, 21 provider/internal calls, and zero strict-interior
ingress close it.

The twelve-byte `kvAlsScale` record at `0x200037BC` has version 1 and CRC at
offset 8. Default initialization produces checksum `0xAA2D`; the writer copies
the whole record, forces version 1, and preserves the two CRC-excluded trailing
bytes. The non-importing v0 migration policy is host-tested, and the candidate
compiles as exactly three Thumb symbols. Production routing and ownership
remain zero. See `docs/research/g2-kvdb-als-scale-recovery.md`.

## Current G2 KVDB ALS-scale production routing

The ALS-scale candidate above is now production-routed under the reviewed
apple-clang profile: three relocated overlay leaves (28-byte default
initializer, 90-byte migration callback, 96-byte whole-record writer, with an
11-byte key-string read-only closure on each referencing leaf) plus three
`B.W` entry redirects replace the 338 stock body bytes
`[0x004AECA4,0x004AEDF6)`. Providers bind exactly to the retained CRC-16 at
`0x0049ACD4` and the blob read/write adapters at `0x004D956C`/`0x004D957E`;
the 50-byte literal tail and the fixed SRAM record at `0x200037BC` are
untouched, and both stored roots plus all three direct entry calls reach the
leaves through the redirects. Apple Clang 21 overlay/component/package pins
are `143227/3666623/4445117` (SHA-256 `200b0b33…`, `ad895f78…`, `62569df0…`).
The leaves and redirects are gated `apple-clang`; linux-clang leaf pins await
Linux toolchain regeneration. Ownership: 338 replaced stock body bytes. See
`docs/research/g2-kvdb-als-scale-recovery.md`.

## Current G2 NVDB sensor-calibration production routing

The sensor-calibration candidate is now production-routed under the reviewed
apple-clang profile: eight relocated overlay leaves (30-byte primary and AG
default initializers, 530-byte primary whole-record updater, 88-byte migration
callback, 4-byte AG migration callback compiled byte-identically to its stock
body, 370-byte AG selective updater, 284-byte suspicious-matrix checker
carrying the 36-byte default-matrix read-only closure, and 358-byte AG
reader) plus eight `B.W` entry redirects replace the 900 stock body bytes
across `[0x00509764,0x00509A3E)` and `[0x00509A40,0x00509AEA)`. Providers bind
exactly to the retained CRC-16 at `0x0049ACD4`, the NVDB blob read/write
adapters at `0x005105F0`/`0x00510602`, and the product predicate at
`0x0045A568`; the 96-byte alignment/literal island and the fixed SRAM records
at `0x200038F4`/`0x20003950` are untouched, and all four stored roots plus
all ten direct entry calls reach the leaves through the redirects. Apple
Clang 21 overlay/component/package pins are `144966/3668362/4446856` (SHA-256
`bf19ebb7…`, `7a4a3252…`, `e709d945…`). The leaves and redirects are gated
`apple-clang`; linux-clang leaf pins await Linux toolchain regeneration.
Ownership: 900 replaced stock body bytes. See
`docs/research/g2-nvdb-sensor-caldata-recovery.md`.

## Current G2 KVDB setting production routing

The primary setting candidate is now production-routed under the reviewed
apple-clang profile: three relocated overlay leaves (28-byte default
initializer, 160-byte whole-record writer, and 64-byte migration callback,
with a 10-byte key-string read-only closure on each of the two referencing
leaves) plus three `B.W` entry redirects replace the 340 stock body bytes
`[0x004AEB20,0x004AEC74)`. Providers bind exactly to the retained CRC-16 at
`0x0049ACD4` and the blob read/write adapters at `0x004D956C`/`0x004D957E`;
the 48-byte literal tail and the fixed SRAM record at `0x200037E0` are
untouched, and both stored roots plus all three direct entry calls reach the
leaves through the redirects. Apple Clang 21 overlay/component/package pins
are `145242/3668638/4447132` (SHA-256 `8f891d52…`, `15ce61e3…`, `203ecd4c…`).
The leaves and redirects are gated `apple-clang`; linux-clang leaf pins await
Linux toolchain regeneration. Ownership: 340 replaced stock body bytes. See
`docs/research/g2-kvdb-setting-recovery.md`.

## Current G2 KVDB time production routing

The time candidate is now production-routed under the reviewed apple-clang
profile: three relocated overlay leaves (28-byte default initializer,
54-byte timestamp/timezone writer, and 100-byte migration callback, with a
7-byte `kvTime` key-string read-only closure on each of the two referencing
leaves and the writer body inlined into the migration callback by the
reviewed toolchain) plus three `B.W` entry redirects replace the 494 stock
body bytes `[0x00585618,0x00585806)`. Providers bind exactly to the retained
CRC-16 at `0x0049ACD4` and the blob read/write adapters at
`0x004D956C`/`0x004D957E`; the 58-byte literal tail and the fixed SRAM
record at `0x2000380C` are untouched, and both stored roots plus all three
direct entry calls reach the leaves through the redirects. Apple Clang 21
overlay/component/package pins are `145443/3668839/4447333` (SHA-256
`9e790387…`, `ecfbc642…`, `e0f3dc6b…`). The leaves and redirects are gated
`apple-clang`; linux-clang leaf pins await Linux toolchain regeneration.
Ownership: 494 replaced stock body bytes. See
`docs/research/g2-kvdb-time-recovery.md`.

## Current G2 KVDB time-format production routing

The time-format candidate is now production-routed under the reviewed
apple-clang profile: three relocated overlay leaves (28-byte default
initializer, 96-byte whole-record writer, and 90-byte migration callback,
with a 13-byte `kvTimeFormat` key-string read-only closure on each of the
two referencing leaves and the writer body inlined into the migration
callback by the reviewed toolchain) plus three `B.W` entry redirects replace
the 338 stock body bytes `[0x0049AE90,0x0049AFE2)`. Providers bind exactly
to the retained CRC-16 at `0x0049ACD4` and the blob read/write adapters at
`0x004D956C`/`0x004D957E`; the 50-byte literal tail and the fixed SRAM
record at `0x20003818` are untouched, and both stored roots plus all three
direct entry calls reach the leaves through the redirects. Apple Clang 21
overlay/component/package pins are `145687/3669083/4447577` (SHA-256
`332daed3…`, `f345bff7…`, `432e69e1…`). The leaves and redirects are gated
`apple-clang`; linux-clang leaf pins await Linux toolchain regeneration.
Ownership: 338 replaced stock body bytes. See
`docs/research/g2-kvdb-time-format-recovery.md`.

## Current G2 KVDB temperature-unit production routing

The temperature-unit candidate is now production-routed under the reviewed
apple-clang profile: three relocated overlay leaves (28-byte default
initializer, 96-byte whole-record writer, and 90-byte migration callback,
with an 18-byte `kvTemperatureUnit` key-string read-only closure on each of
the two referencing leaves and the writer body inlined into the migration
callback by the reviewed toolchain) plus three `B.W` entry redirects replace
the 338 stock body bytes `[0x0049B014,0x0049B166)`. Providers bind exactly
to the retained CRC-16 at `0x0049ACD4` and the blob read/write adapters at
`0x004D956C`/`0x004D957E`; the 50-byte literal tail and the fixed SRAM
record at `0x200037FC` are untouched, and both stored roots plus all three
direct entry calls reach the leaves through the redirects. Apple Clang 21
overlay/component/package pins are `145940/3669336/4447830` (SHA-256
`50e4865c…`, `72f6225b…`, `7b3301d8…`). The leaves and redirects are gated
`apple-clang`; linux-clang leaf pins await Linux toolchain regeneration.
Ownership: 338 replaced stock body bytes. See
`docs/research/g2-kvdb-temperature-unit-recovery.md`.

## Current G2 KVDB universal-setting production routing

The universal-setting candidate is now production-routed under the reviewed
apple-clang profile: three relocated overlay leaves (28-byte default
initializer, 128-byte whole-record writer, and 92-byte migration callback,
with a 19-byte `kvUniversalSetting` key-string read-only closure on each of
the two referencing leaves and the writer body inlined into the migration
callback by the reviewed toolchain) plus three `B.W` entry redirects replace
the 340 stock body bytes `[0x0049AD0C,0x0049AE60)`. Providers bind exactly
to the retained CRC-16 at `0x0049ACD4` and the blob read/write adapters at
`0x004D956C`/`0x004D957E`; the 48-byte literal tail and the fixed SRAM
record at `0x20003824` are untouched, and both stored roots plus all three
direct entry calls reach the leaves through the redirects. Apple Clang 21
overlay/component/package pins are `146227/3669623/4448117` (SHA-256
`1701d7eb…`, `2042c3ea…`, `a65f3794…`). The leaves and redirects are gated
`apple-clang`; linux-clang leaf pins await Linux toolchain regeneration.
Ownership: 340 replaced stock body bytes. See
`docs/research/g2-kvdb-universal-setting-recovery.md`.

## Current G2 KVDB terminal-mode increment

The retained `service_kvdb_terminal_mode.c` object is completely bounded at
`[0x004B03E0,0x004B0560)`: three functions contribute 334 code bytes and the
owned tail contributes 50 bytes. Two stored roots, three direct entry calls,
21 provider/internal calls, and zero strict-interior ingress close it.

The four-byte `kvTerminalMode` record at `0x20003808` has version at byte zero,
mode at byte one, and CRC at offset two. Its external setter independently
confirms the mode field; default initialization produces checksum `0x2E3E`.
The whole-record writer and non-importing v0 migration policy are host-tested,
and the candidate compiles as exactly three Thumb symbols. Production routing
and ownership remain zero. See
`docs/research/g2-kvdb-terminal-mode-recovery.md`.

## Current G2 KVDB terminal-mode production routing

The terminal-mode candidate is now production-routed under the reviewed
apple-clang profile: three relocated overlay leaves (28-byte default
initializer, 52-byte whole-record writer, and 94-byte migration callback,
with a 15-byte `kvTerminalMode` key-string read-only closure on each of
the two referencing leaves and the writer body inlined into the migration
callback by the reviewed toolchain) plus three `B.W` entry redirects replace
the 334 stock body bytes `[0x004B03E0,0x004B052E)`. Providers bind exactly
to the retained CRC-16 at `0x0049ACD4` and the blob read/write adapters at
`0x004D956C`/`0x004D957E`; the 50-byte literal tail and the fixed SRAM
record at `0x20003808` are untouched, and both stored roots plus all three
direct entry calls reach the leaves through the redirects. Apple Clang 21
overlay/component/package pins are `146433/3669829/4448323` (SHA-256
`bb69a3a6…`, `ab37d9c8…`, `6f226b26…`). The leaves and redirects are gated
`apple-clang`; linux-clang leaf pins await Linux toolchain regeneration.
Ownership: 334 replaced stock body bytes. See
`docs/research/g2-kvdb-terminal-mode-recovery.md`.

## Current G2 KVDB onboarding-config production routing

The onboarding-config candidate is now production-routed under the reviewed
apple-clang profile: six relocated overlay leaves (32-byte indexed live-byte
setter, 22-byte live-byte writer, 42-byte update-and-persist wrapper, 10-byte
scalar getter, 8-byte pointer getter, and 30-byte live-record loader, with a
19-byte `kvOnboardingConfig` key-string read-only closure on each of the
three referencing leaves and the setter, writer, and pointer-getter bodies
inlined into the composing leaves by the reviewed toolchain) plus six `B.W`
entry redirects replace the 286 stock body bytes `[0x004A777C,0x004A789A)`.
Providers bind exactly to the blob read/write adapters at
`0x004D956C`/`0x004D957E`; the 54-byte literal tail and the fixed one-byte
SRAM record at `0x20000040` are untouched, and all eighteen direct entry
calls reach the leaves through the redirects. Apple Clang 21
overlay/component/package pins are `146645/3670041/4448535` (SHA-256
`4df8082f…`, `f464eb05…`, `4689b480…`). The leaves and redirects are gated
`apple-clang`; linux-clang leaf pins await Linux toolchain regeneration.
Ownership: 286 replaced stock body bytes. See
`docs/research/g2-kvdb-onboarding-config-recovery.md`.

## Current G2 KVDB ring production routing

The ring candidate is now production-routed under the reviewed apple-clang
profile: three relocated overlay leaves (28-byte default initializer,
262-byte whole-record writer, and 66-byte migration callback, with a 7-byte
`kvRing` key-string read-only closure on each of the two referencing leaves
and the writer called by the migration callback as a source-owned leaf) plus
three `B.W` entry redirects replace the 796 stock body bytes
`[0x005D9B6C,0x005D9E88)`. Providers bind exactly to the retained CRC-16 at
`0x0049ACD4` and the blob read/write adapters at `0x004D956C`/`0x004D957E`;
the 72-byte literal tail and the fixed 24-byte SRAM record at `0x200037C8`
are untouched, and both stored roots plus both direct entry calls reach the
leaves through the redirects. Apple Clang 21 overlay/component/package pins
are `147021/3670417/4448911` (SHA-256 `02c48ddc…`, `eee145e7…`, `21ba9d6c…`).
The leaves and redirects are gated `apple-clang`; linux-clang leaf pins await
Linux toolchain regeneration. Ownership: 796 replaced stock body bytes. See
`docs/research/g2-kvdb-ring-recovery.md`.

## Current G2 AT^NUS handler production routing

The pathless `AT^NUS` command handler is authored clean-room from the
recovered behavioral specification and production-routed under the reviewed
apple-clang profile: one relocated overlay leaf (the 18-byte
`open_cfw_at_nus_handler`) plus one `B.W` entry redirect with NOP fill
replace the complete sixteen-byte stock object `[0x005A5520,0x005A5530)`
(twelve body bytes plus the four-byte literal pool). The leaf passes the
retained `NUS+OK\r\n` response string at `0x0078A370` to the retained output
provider at `0x00541430` and returns one without reading its arguments; the
stored registration pointer `0x005A5521` at `0x006C92A8` — the only ingress —
reaches the leaf through the redirect. Apple Clang 21
overlay/component/package pins are `147042/3670438/4448932` (SHA-256
`b1a5bcd7…`, `76bc4a35…`, `a842e5e3…`). The leaf and redirect are gated
`apple-clang`; linux-clang leaf pins await Linux toolchain regeneration.
Ownership: 16 replaced stock object bytes. See
`docs/research/g2-at-nus-recovery.md`.

## Current G2 eAT core/sensor cluster production routing

The pathless eAT core/sensor command cluster is authored clean-room from the
recovered behavioral specification and production-routed under the reviewed
apple-clang profile: twelve relocated overlay leaves (650 bytes plus sixteen
alignment bytes) plus twelve `B.W` entry redirects with NOP fill replace the
486 stock body bytes across `[0x005A5720,0x005A595E)`. The four owned
alignment/literal islands (126 bytes) stay retained stock, and the twelve
stored registration pointers in the 192-byte command table
`[0x006C92E0,0x006C93A0)` — the only ingress — reach the leaves through the
redirects. Recovered stock quirks are reproduced exactly (`SCRN_Y` accepts
zero through 192, the PSN error reports the required length, `ALS`
acknowledges unhandled values, `BRIGHTNESS` forwards unvalidated). Apple
Clang 21 overlay/component/package pins are `147708/3671104/4449598`
(SHA-256 `bcf40980…`, `d1793fce…`, `f3655acb…`). The leaves and redirects
are gated `apple-clang`; linux-clang leaf pins await Linux toolchain
regeneration. Ownership: 486 replaced stock body bytes. See
`docs/research/g2-eat-core-sensor-recovery.md`.

## Current G2 KVDB module-configuration production routing

The retained `service_kvdb_module_configure.c` closure is production-routed
under the reviewed apple-clang profile: six relocated overlay leaves (2,428
text bytes plus six 64-byte key-string read-only closures and one two-byte
alignment pad) plus six `B.W` entry redirects with NOP fill replace the
2,286 stock body bytes across `[0x004922F8,0x00492BE6)`. Provider binding is
exact: the retained blob read/write adapters at `0x004D956C`/`0x004D957E`,
the retained dashboard mode provider at `0x0045A570` (mode two skips the
database), the retained built-in menu item lookup at `0x00460450`, and the
retained snapshot synchronization providers at `0x0046018E`/`0x004601EA`.
The 206-byte alignment/literal tail stays retained stock, the SRAM scalars,
menu record, runtime array, and external-menu globals are untouched, and the
three stored reader roots at `0x00746D24...0x00746D2C` plus the three direct
writer entry calls reach the leaves through the redirects. Apple Clang 21
overlay/component/package pins are `150522/3673918/4452412` (SHA-256
`f32aa018…`, `32413c15…`, `ab0f0b0a…`). The leaves and redirects are gated
`apple-clang`; linux-clang leaf pins await Linux toolchain regeneration.
Ownership: 2,286 replaced stock body bytes. See
`docs/research/g2-kvdb-module-configure-recovery.md`.

## Current G2 NVDB buzzer production routing

The retained `service_nvdb_buzzer.c` closure is production-routed under the
reviewed apple-clang profile: five relocated overlay leaves (168 text bytes
plus one two-byte alignment pad) plus five `B.W` entry redirects with NOP
fill replace the 188 stock body bytes across `[0x0058F9D4,0x0058FA90)`.
Provider binding is exact: the retained CRC-16 provider at `0x0049ACD4` and
the retained NVDB blob read/write adapters at `0x005105F0`/`0x00510602`;
the retained diagnostic hook stays the candidate's deliberate no-op. The
28-byte literal tail stays retained stock, the twelve-byte SRAM record at
`0x200038D8`, the `nvBuzzer` key, and the v2 4,000 Hz / 30% boot defaults
are untouched, and the two stored entry roots at
`0x006D1E84`/`0x0078F518` plus the five direct entry calls reach the
leaves through the redirects. Apple Clang 21 overlay/component/package pins
are `150692/3674088/4452582` (SHA-256 `58920545…`, `0b88c150…`,
`5d1efae3…`). The leaves and redirects are gated `apple-clang`; linux-clang
leaf pins await Linux toolchain regeneration. Ownership: 188 replaced stock
body bytes. See `docs/research/g2-nvdb-buzzer-recovery.md`.

## Current G2 NVDB product-mode production routing

The retained `service_nvdb_product_mode.c` closure is production-routed
under the reviewed apple-clang profile: six relocated overlay leaves (196
text bytes plus one two-byte alignment pad) plus six `B.W` entry redirects
with NOP fill replace the 270 stock body bytes across
`[0x004ABD90,0x004ABE9E)`. Provider binding is exact: the retained CRC-16
provider at `0x0049ACD4` and the retained NVDB blob read/write adapters at
`0x005105F0`/`0x00510602`; the retained diagnostic hook stays the
candidate's deliberate no-op. The 42-byte alignment and literal island
stays retained stock, the four-byte SRAM record at `0x200038F0`, the
`nvProdMode` key, and the version-0 boot defaults are untouched, and the
two stored entry roots at `0x006D1E94`/`0x0078F520` plus the 54 direct
entry calls reach the leaves through the redirects. Apple Clang 21
overlay/component/package pins are `150890/3674286/4452780` (SHA-256
`21b94e54…`, `2ad978b4…`, `41064778…`). The leaves and redirects are gated
`apple-clang`; linux-clang leaf pins await Linux toolchain regeneration.
Ownership: 270 replaced stock body bytes. See
`docs/research/g2-nvdb-product-mode-recovery.md`.

## Current G2 NVDB MAC production routing

The retained `service_nvdb_mac.c` closure is production-routed under the
reviewed apple-clang profile: three relocated overlay leaves (252 text
bytes plus one two-byte alignment pad) plus three `B.W` entry redirects
with NOP fill replace the 280 stock body bytes across
`[0x005D9F48,0x005DA060)`. Provider binding is exact: the source-owned
MCUCTRL information provider at `0x00480D72` (the candidate's two-word
device-identifier seam is adapted onto its selector-one 64-byte
device-record ABI by the leaf's pinned `-DOPEN_CFW_NVDB_MAC_DEVICE_IDS_GET`
binding), the retained CRC-32 provider at `0x004D34C4`, the retained CRC-16
provider at `0x0049ACD4`, and the retained NVDB blob read/write adapters at
`0x005105F0`/`0x00510602`; the retained diagnostic hook stays the
candidate's deliberate no-op. The 32-byte literal tail stays retained
stock, the ten-byte SRAM record at `0x200038E4`, the `nvMAC` key, and the
version-1 boot defaults are untouched, and the two stored entry roots at
`0x006D1E8C`/`0x0078F51C` plus the two direct entry calls reach the leaves
through the redirects. Apple Clang 21 overlay/component/package pins are
`151144/3674540/4453034` (SHA-256 `33a5109d…`, `be32048d…`, `bec30ccb…`).
The leaves and redirects are gated `apple-clang`; linux-clang leaf pins
await Linux toolchain regeneration. Ownership: 280 replaced stock body
bytes. See `docs/research/g2-nvdb-mac-recovery.md`.

## Current G2 NVDB advertising-magic production routing

The retained advertising-magic NVDB closure immediately preceding
`service_nvdb_mac.c` is production-routed under the reviewed apple-clang
profile: three relocated overlay leaves (140 text bytes plus one two-byte
alignment pad before the migration callback) plus three `B.W` entry
redirects with NOP fill replace the 110 stock body bytes across
`[0x005D9ED0,0x005D9F3E)`. Provider binding is exact: the retained CRC-16
provider at `0x0049ACD4` and the retained NVDB blob read/write adapters at
`0x005105F0`/`0x00510602`. The ten-byte alignment and literal tail stays
retained stock, the four-byte SRAM record at `0x200038D4`, the
`nvAdvMagic` key, and the boot defaults are untouched, and the two stored
entry roots at `0x006D1E7C`/`0x0078F514` reach the leaves through the
redirects. Apple Clang 21 overlay/component/package pins are
`151286/3674682/4453176` (SHA-256 `d3087982…`, `8aac36ba…`, `5fd04249…`).
The leaves and redirects are gated `apple-clang`; linux-clang leaf pins
await Linux toolchain regeneration. Ownership: 110 replaced stock body
bytes. See `docs/research/g2-nvdb-adv-magic-recovery.md`.

## Current G2 NVDB system-data production routing

The retained `service_nvdb_sys_dt.c` closure is production-routed under the
reviewed apple-clang profile: thirteen relocated overlay leaves (4,338 text
bytes plus two 23-byte read-only string closures and twelve alignment pad
bytes) plus thirteen `B.W` entry redirects with NOP fill replace the 5,084
stock body bytes across `[0x004AEE28,0x004B03E0)`. Provider binding is
exact: the retained CRC-16 provider at `0x0049ACD4`, the retained NVDB blob
read/write adapters at `0x005105F0`/`0x00510602`, the source-owned
peripheral-power enable/disable entries at `0x0047F5B8`/`0x0047F7AE` and
CMSIS delay at `0x00449376` (through the pinned
`-DOPEN_CFW_NVDB_SYS_DT_OTP_BEGIN`/`_END` gate sequences), the retained OTP
INFOC word accessors at `0x0051381A`/`0x00513850`, and the retained
40-entry legacy-PSN table at `0x006D3358` (through the pinned
`-DOPEN_CFW_NVDB_SYS_DT_LEGACY_PSNS` seam); the fourteen-field parse
diagnostic sink is compiled out by the pinned
`-DOPEN_CFW_NVDB_SYS_DT_PARSED` no-op binding. The 476 split
alignment/literal bytes stay retained stock, the 172-byte SRAM record at
`0x20003994`, the `nvSysDt` key, and the factory defaults are untouched,
and the two stored entry roots at `0x006D1EAC`/`0x0078F52C` plus the 37
direct entry calls reach the leaves through the redirects. Apple Clang 21
overlay/component/package pins are `155682/3679078/4457572` (SHA-256
`3bb04fb7…`, `5160689a…`, `f66065fe…`). The leaves and redirects are gated
`apple-clang`; linux-clang leaf pins await Linux toolchain regeneration.
Ownership: 5,084 replaced stock body bytes. See
`docs/research/g2-nvdb-sys-dt-recovery.md`.

## Current G2 ULED display-preprocess production routing

The retained `driver/uled/display_preprocess.c` closure is production-routed
under the reviewed apple-clang profile: one relocated closure leaf (242 text
bytes plus the 28-byte GPU descriptor-template read-only closure and four
alignment pad bytes) plus one `B.W` entry redirect with NOP fill replace the
584 stock body bytes at `[0x0046C73C,0x0046C984)`. Provider binding is exact:
the retained GPU start provider at `0x004B092A`, the retained
destination-channel configure/mode/enable providers at
`0x004B0730`/`0x004B1A78`/`0x004B0748`, the retained source-configuration
provider at `0x004B1608`, the retained offset provider at `0x004B1B48`, and
the retained commit provider at `0x004B0C8A`. The assertion sink is compiled
out by the pinned `-DOPEN_CFW_ULED_ASSERT` no-op fail-stop binding and the
GPU-failure diagnostic binding stays inert. The discontiguous 64-byte IAR
literal/template pool at `[0x0046CA74,0x0046CAB4)` stays retained stock data,
and the sole direct call at `0x0046CA64` reaches the leaf through the
redirect. Routing required extending the reviewed rodata local-name class in
`tools/apollo_overlay.py` to admit Clang `.L__const.<function>.<variable>`
constant-aggregate locals alongside the existing `.L.str[.N]` string class.
Apple Clang 21 overlay/component/package pins are `164912/3688308/4466802`
(SHA-256 `a437e33e…`, `4fdb5af5…`, `cc1642fd…`). The leaf and redirect are
gated `apple-clang`; linux-clang leaf pins await Linux toolchain
regeneration. Ownership: 584 replaced stock body bytes. See
`docs/research/g2-uled-display-preprocess-recovery.md`.

## Current G2 KVDB time increment

The retained `service_kvdb_time.c` object is completely bounded at
`[0x00585618,0x00585840)`: three functions contribute 494 code bytes and the
owned tail contributes 58 bytes. Two stored roots, three direct entry calls,
31 provider/internal calls, and zero legitimate strict-interior ingress close
it. One unaligned packed-string byte window is explicitly qualified as data.

The twelve-byte `kvTime` record at `0x2000380C` contains version, timestamp,
signed timezone, four preserved reserved bytes, and CRC at offset ten. Default
initialization produces checksum `0x18F0`; persistence forces version 3 and
changes the factory-values checksum to `0xC67A`. The field-specific writer and
non-importing pre-v3 migration policy are host-tested, and the candidate
compiles as exactly three Thumb symbols. Production routing and ownership
remain zero. See `docs/research/g2-kvdb-time-recovery.md`.

## Current G2 KVDB onboarding-config increment

The retained `service_kvdb_onboarding_config.c` object is completely bounded
at `[0x004A777C,0x004A78D0)`: six functions contribute 286 code bytes and the
owned tail contributes 54 bytes. Eighteen direct entry calls, 20
provider/internal calls, no stored entry pointers, and zero strict-interior
ingress close it.

The `kvOnboardingConfig` record is one byte at `0x20000040`, initialized to
zero, with no version or CRC. Only index zero is writable; its null-value case
is a successful no-op. Both pointer-getter branches return the same record,
and reads import the stored byte directly while diagnosing only a zero backend
result. All six entry contracts are host-tested and the candidate compiles as
exactly six Thumb symbols. Production routing and ownership remain zero. See
`docs/research/g2-kvdb-onboarding-config-recovery.md`.

## Current G2 KVDB ring increment

The retained `service_kvdb_ring.c` object is completely bounded at
`[0x005D9B6C,0x005D9ED0)`: three functions contribute 796 code bytes and the
owned tail contributes 72 bytes. Two stored roots, two internal writer calls,
45 provider/internal calls, and zero strict-interior ingress close it.

The 24-byte `kvRing` record at `0x200037C8` contains version, MAC, a 14-byte
name, a preserved reserved byte, and CRC at offset 22. Default initialization
produces checksum `0x06D4`. The writer's distinct null/non-null name rules and
the non-importing v0 migration policy are host-tested; the candidate compiles
as exactly three Thumb symbols. Production routing and ownership remain zero.
See `docs/research/g2-kvdb-ring-recovery.md`.

## Current G2 KVDB module-configuration increment

The retained `service_kvdb_module_configure.c` object is completely bounded at
`[0x004922F8,0x00492CB4)`: six functions contribute 2,286 code bytes and the
owned alignment/literal region contributes 206 bytes. Three direct calls,
three stored reader roots, 115 provider/internal calls, and zero legitimate
strict-interior ingress close it. Eight raw interior-looking windows are
qualified as unaligned overlaps or, at `0x58ECC8`, the second halfword of a
valid 32-bit Thumb instruction.

The candidate preserves the one-byte language payload, four-byte dashboard
value and mode-two bypass, plus the 888-byte magic/count/menu-item record. It
pins the 44-byte stored and 52-byte runtime item layouts, built-in/custom load
rules, identical-write suppression, synchronization bracket, and the stock
lack of count and text clamps. Host tests and a six-symbol Thumb build pass;
production routing and ownership remain zero. See
`docs/research/g2-kvdb-module-configure-recovery.md`.

## Current G2 ULED display-preprocess increment

The retained `driver/uled/display_preprocess.c` linked object is closed as one
584-byte function at `[0x0046C73C,0x0046C984)` plus its separate 64-byte IAR
literal/template pool at `[0x0046CA74,0x0046CAB4)`. One direct caller, 23 real
provider calls, zero legitimate strict-interior ingress, two odd-byte raw
overlaps, and one explicitly excluded `sdiv` halfword close the object.

The candidate pins all nine assertions, the `0x619` 28-byte destination
descriptor, 16-byte region, width/offset halving, format nine, GPU result gate,
and six-call success sequence. Five candidate/analyzer host tests plus a
one-symbol Thumb build pass. Production routing and ownership remain zero. See
`docs/research/g2-uled-display-preprocess-recovery.md`.

## Current G2 BQ25180 charger-driver increment

The retained `driver/chg/drv_bq25180.c` object is completely bounded at
`[0x0053A670,0x0053AFC0)`: 28 functions contribute 2,268 code bytes and the
owned literal tail contributes 116 bytes. Fifty-six direct entry calls, 93
provider/internal calls, no stored entry pointers, and zero direct, `B.W`, or
raw strict-interior ingress close the object.

The candidate pins I2C bus 7/address `0x6A`, all register-field encodings,
runtime event/state offsets `0x14/0x16`, device-ID validation, and the exact
19-call initialization sequence. Starting from the reset fixture, defaults
produce register image `0000005a24241f4406002100f0`. Nine candidate tests,
four analyzer tests, and a 22-symbol freestanding Thumb build pass. Production
routing is live under the reviewed apple-clang profile: twenty-two relocated
leaves and twenty-two entry redirects replace 1,792 stock body bytes, bound
to the retained I2C read/write backends at `0x0050436E`/`0x005044B4` and the
retained `memset` provider at `0x0043C0E4`, with the assertion sink compiled
out by the pinned no-op fail-stop binding and the diagnostic binding inert.
See `docs/research/g2-chg-bq25180-recovery.md`.

## Current G2 BQ27427 fuel-gauge increment

The retained `driver/chg/drv_bq27427.c` object is completely bounded at
`[0x0053AFC0,0x0053C2A4)`: 37 functions contribute 4,440 code bytes and six
owned non-code intervals contribute 396 bytes. Eighty-eight direct entry
calls, 287 provider/internal calls, no stored entry pointers, and zero
legitimate direct, `B.W`, or raw strict-interior ingress close the object;
the one raw BL-looking interior window lies outside authenticated code.

The candidate pins I2C bus 7/address `0x55`, split little-endian register
I/O, the 36-byte data-memory block with its exact checksum and CFGUPDATE
flow, the initialized `0x80008000` unseal key, the seven live DM descriptors,
product defaults `{240,80,3100}`, and the telemetry record at `0x20073B18`.
Twelve candidate/analyzer host tests and a 33-symbol freestanding Thumb build
pass. Production routing is live under the reviewed apple-clang profile:
thirty-three relocated leaves and thirty-two entry redirects replace 3,938
stock body bytes, bound to the retained I2C read/write backends at
`0x0050436E`/`0x005044B4`, the retained millisecond delay wrapper at
`0x004910F4`, and the retained `memcpy`/`memset` providers at
`0x00439BE4`/`0x0043C0E4`, with the diagnostic binding inert by default. The
CFGUPDATE poll helper rides as an overlay-internal local-function sibling
leaf under the reviewed `allow_local_function`/
`allow_local_relocation_targets` contracts, and the DM-descriptor-table and
product-defaults constants ride as reviewed read-only closures. See
`docs/research/g2-chg-bq27427-recovery.md`.

## Current G2 charger-common increment

The retained `platform/service/charger/charger_common.c` object is completely
bounded at `[0x004ACE10,0x004AD9B8)`: 14 functions contribute 2,764 code bytes
and three owned non-code regions contribute 220 bytes. Twenty-five direct entry
calls, 157 provider/internal calls, no stored entry pointers, and zero
legitimate strict-interior ingress close it; six raw interior-looking values
are explicitly qualified instruction/data overlaps.

The candidate pins the 24-byte aggregate runtime, eight-byte local cache,
initial retry schedule, near-full SOC compensation, charging debounce, peer
aggregation, and twelve-byte service-`0x0105` message ABI. Six candidate tests,
four analyzer tests, and an 11-symbol freestanding Thumb build pass. Production
routing is live under the reviewed apple-clang profile: eleven relocated
leaves and eleven entry redirects replace 2,400 stock body bytes, with the
five file-static state cells bound to their retained stock SRAM cells through
the new reviewed `allow_bound_static_data` relocation contract. See
`docs/research/g2-charger-common-recovery.md`.

## Current G2 BQ27427 fuel-gauge increment

The retained `driver/chg/drv_bq27427.c` object is completely bounded at
`[0x0053AFC0,0x0053C2A4)`: 37 functions contribute 4,440 code bytes and six
owned non-code regions contribute 396 bytes. Eighty-eight direct entry calls,
287 provider/internal calls, no stored entry pointers, and zero legitimate
strict-interior ingress close it.

The candidate pins I2C bus 7/address `0x55`, 36-byte data-memory blocks, the
checksum/CFGUPDATE/chemistry protocol, initialized unseal key `0x80008000`,
seven descriptors, defaults `{240,80,3100}`, and runtime offsets at
`0x20073B18`. Candidate and analyzer tests plus a freestanding Thumb build
pass. Production routing and ownership remain zero. See
`docs/research/g2-chg-bq27427-recovery.md`.

## Current G2 common ULED MSPI increment

The retained `driver/uled/drv_mspi_uled_common.c` object is completely bounded
at `[0x0059C820,0x0059D244)`: 13 functions contribute 2,358 code bytes and the
owned alignment/literal region contributes 238 bytes. Thirty direct entry
calls (11 exterior), 151 provider/internal calls, one intentional stored
completion callback, and zero legitimate strict-interior ingress close it.

The analysis pins the 28-byte request and 24-byte HAL transfer layouts,
serial/quad control request `0x18`, interrupt mask `0x1A80`, blocking timeout
1,000,000, asynchronous semaphore timeout 3,000 ms, MSPI0, IRQ 20/priority
four, and the exact initialization sequence. Both panel template families and
all 11 exterior panel calls are now closed; a clean-room implementation still
requires independently named provider bindings and product-specific HAL
control validation. Production routing and ownership remain zero. See
`docs/research/g2-uled-mspi-common-recovery.md`.

## Current G2 JBD4010 ULED increment

The retained `driver/uled/jbd4010/drv_mspi_jbd4010.c` object is completely
bounded at `[0x00592658,0x005939A0)`: 24 functions contribute 4,588 code bytes
and eight owned alignment/literal regions contribute 348 bytes. Seventy-seven
direct entry calls, 289 provider/internal calls, 14 intentional stored entry
pointers in the external ULED manager table, and zero legitimate
strict-interior ingress close it.

The analysis pins four 28-byte request templates, the common-driver seam,
640x480 four-bit framebuffer geometry, partial and asynchronous refresh,
offset and brightness behavior, chip/die identification, power and recovery
flows, and the four accepted panel modes. Historical source remains
unavailable, so this is an analysis boundary rather than a clean-room source
candidate; production routing and ownership remain zero. See
`docs/research/g2-uled-jbd4010-recovery.md`.

## Current G2 Hongshi/A6N-G ULED increment

The retained `driver/uled/hongshi_a6ng/drv_mspi_a6ng.c` object is completely
bounded at `[0x005BBD48,0x005BD3A0)`: 22 functions contribute 5,276 code
bytes and nine owned alignment/literal regions contribute 444 bytes.
Ninety-nine intra-object entry calls, 366 genuine provider/internal calls, 15
intentional stored entry pointers in the external manager table, and zero
legitimate strict-interior ingress close it. Four raw BL-looking VFP windows
and two odd-byte interior overlaps are explicitly qualified.

The analysis pins four 28-byte request templates, the 50-byte configuration
stream, eight-byte status preamble, common-driver seam, 640x480 four-bit
framebuffer geometry, brightness and offset behavior, chip/serial reads,
power/recovery flows, and the two intentional exported stubs. Historical
source remains unavailable, so this is an analysis boundary rather than a
clean-room source candidate; production routing and ownership remain zero.
See `docs/research/g2-uled-a6ng-recovery.md`.

## Current G2 ULED manager increment

The retained `driver/uled/drv_mspi_uled.c` object is completely bounded at
`[0x004C9D44,0x004CA6F8)`: 14 functions contribute 2,332 code bytes and two
alignment halfwords plus its literal pool contribute 152 bytes. Eighteen
direct entry calls (17 exterior), 97 genuine provider/internal calls, one
startup termination pointer, one runtime framebuffer-callback materialization,
and zero legitimate strict-interior ingress close it. Fifteen raw
multiply/VFP windows and one odd-byte overlap are explicitly qualified.

The analysis pins the two-entry operations linker list, type-one A6N-G and
type-zero JBD4010 selection rule, active-record pointer, complete 64-byte
callback layout, wrapper offsets, and nibble-preserving 640x480 framebuffer
clear helper. All five retained-path ULED translation units are now bounded.
Historical source remains unavailable, so this is an analysis boundary rather
than a clean-room source candidate; production routing and ownership remain
zero. See `docs/research/g2-uled-manager-recovery.md`.

## Current G2 buzzer-driver increment

The retained `driver/buzzer/drv_buzzer.c` object is completely bounded at
`[0x005026BC,0x00502D58)`: 17 bodies contribute 1,520 code bytes and four
alignment/constant/literal regions contribute 172 bytes. Thirty-five direct
entry calls (18 exterior), 88 genuine provider/internal calls, one stored
one-shot timer callback, and zero legitimate strict-interior ingress close the
object. Eleven odd-byte address overlaps are explicitly qualified as data or
instruction windows.

The analysis pins the 96 MHz PWM basis, two 28-byte pitch-reload tables, nine
50-byte predefined voice records, note/tone/beat interpreter, repeat and timer
state, queued input-thread events, single-note scratch script, and direct
start/stop path. Historical source remains unavailable, so this is an
analysis boundary rather than a clean-room source candidate; production
routing and ownership remain zero. See
`docs/research/g2-drv-buzzer-recovery.md`. Its compact watchdog follow-on is
closed below.

## Current G2 watchdog-driver increment

The retained `driver/wdt/watchdog.c` object is completely bounded at
`[0x0052F2E0,0x0052F38C)`: two exact-named bodies contribute 140 bytes and the
literal pool contributes 32 bytes. Two direct entry calls (one exterior), 13
body calls, no stored entry pointers, and zero direct, stored, or `B.W`
strict-interior ingress close it.

`watchdog_init` calls `watchdog_enable`; enable invokes the lower provider only
when selector-zero returns byte value one. A clean-room C implementation is now
production-routed: two strict-relocation leaves total 28 source bytes, and two
guarded redirects replace all 140 stock body bytes. The 32-byte diagnostic pool
remains retained. Host behavior, Thumb compilation, analyzer routing, Apple
component, and complete package gates pass. On-device enable/reset-cause timing
is blocked by unavailable physical evidence; future qualification requires authorized hardware evidence. See
`docs/research/g2-watchdog-recovery.md`. Its retained eAT buzzer consumer is
closed below.

## Current G2 eAT buzzer-command increment

The retained `platform/service/eAT/at_buzzer.c` object is completely bounded
at `[0x005A4FD0,0x005A5488)`: exact-named `_atBuzzerTest` contributes 1,014
code bytes and its alignment/literal pool contributes 194 bytes. The handler
has no direct caller; the sole ingress is the odd Thumb pointer in the
sixteen-byte `AT^BUZZER` command record. Seventy-six direct body calls, one
stored entry pointer, and zero direct, stored, or `B.W` strict-interior ingress
close the topology.

The analysis pins `note`, `play`, `start`, and `stop`, their exact parser
formats and range checks, retained help/error/success text, and calls into all
four corresponding bounded buzzer-driver APIs. It also preserves the stock
quirk that the AT layer accepts play types 0-10 while the nine-record driver
later rejects 9 and 10. Historical source remains unavailable. Independently
authored clean-room C is now production-routed as one 2,740-byte Thumb leaf
with 23 strict provider relocations; a guarded redirect replaces the entire
1,208-byte stock object. Host/parser, analyzer, component, ownership-map,
package, and flash-plan gates are green. Audible output, pitch, frequency,
duty cycle, beat timing, and stop behavior remain hardware-deferred because
physical G2 buzzer qualification is blocked by unavailable physical evidence; future qualification requires authorized evidence. See
`docs/research/g2-at-buzzer-recovery.md`. The adjacent command-table entry is
`AT^AUDIO` at `0x005A5488`; its retained `at_codec.c` handler is closed below.

## Current G2 eAT audio-control increment

The retained `platform/service/eAT/at_codec.c` object is completely bounded
at `[0x005A5488,0x005A5520)`: exact-named `_atAudioCtrl` contributes 118 code
bytes and its alignment/literal pool contributes 34 bytes. Its only ingress is
the stored odd Thumb pointer in the `AT^AUDIO` command record. Ten body calls
and zero direct, stored, or `B.W` strict-interior ingress close the topology.

A leading `1` invokes provider `0x0054F380` with selector seven; a leading `0`
invokes `0x0054F50E` with selector seven. Every path emits `AUD_AUDIO+OK` and
returns one. Historical source remains unavailable, so this is analysis-only
with zero production ownership. See `docs/research/g2-at-codec-recovery.md`.
Its retained `at_fs.c` neighbor is closed below.

## Current G2 eAT filesystem-command increment

The retained `platform/service/eAT/at_fs.c` object is completely bounded at
`[0x005A5530,0x005A5720)`: four bodies contribute 416 code bytes and the pool
contributes 80 bytes. Three stored command pointers register `AT^RM`, `AT^LS`,
and `AT^MKDIR`; two internal calls reach the recursive listing helper. The 33
body calls and absence of exterior direct or strict-interior ingress close the
topology.

The analysis pins filesystem-ready word `0x200746A8`, remove/mkdir providers,
recursive dot-entry filtering, child-path construction, directory and
byte/integer-KiB file reports, and exact success/error responses. Historical
source remains unavailable, so this is analysis-only with zero production
ownership. See `docs/research/g2-at-fs-recovery.md`. The next retained eAT
frontier, `at_tp.c`, is closed below.

## Current G2 eAT touch-panel increment

The retained `platform/service/eAT/at_tp.c` object is completely bounded at
`[0x005A5984,0x005A5D94)`: two bodies contribute 898 code bytes and the
alignment/pool regions contribute 142 bytes. The stored `AT^TP` handler
pointer and two internal helper calls are the complete entry set. Seventy body
calls and zero exterior direct or strict-interior ingress close the topology.

The analysis pins difference capture, debug flag `0x20075017`, proximity
baseline read/save, gesture configuration read/write, 1-65,535-ms threshold
validation, 100-ms write/readback verification, and every retained response.
Historical source remains unavailable, so this is analysis-only with zero
production ownership. See `docs/research/g2-at-tp-recovery.md`. All four
retained eAT source paths are now bounded. The intervening pathless cluster is
closed below.

## Current G2 pathless eAT core/sensor increment

The twelve registered handlers between `at_fs.c` and `at_tp.c` are completely
bounded at `[0x005A5720,0x005A5984)`: 486 code bytes and 126 owned
alignment/literal bytes. The table `[0x006C92E0,0x006C93A0)` registers the
commands from `AT^INFO` through `AT^BRIGHTNESS_READ`; those twelve odd Thumb
pointers are the complete entry set. Forty-nine body calls and zero direct or
strict-interior ingress close the topology.

The analysis pins the S200/product/build report, reset and 14-byte PSN
contracts, IMU raw/Euler operations, screen-X stub, screen-Y machine range,
ALS read/enable/scale behavior, and brightness write/read behavior. It also
preserves the stock quirks that screen Y accepts zero despite its 1-192 error
text and unsupported ALS values are still acknowledged. No retained path
partitions the cluster, so historical source inventory and licensing remain
unknown. This is analysis-only with zero production ownership; see
`docs/research/g2-eat-core-sensor-recovery.md`.

## Current G2 pathless eAT NUS increment

The standalone `AT^NUS` object between `at_codec.c` and `at_fs.c` is bounded
at `[0x005A5520,0x005A5530)`: a twelve-byte handler plus one four-byte
literal. Its command record supplies the only entry. The handler emits
`NUS+OK`, returns one, and has no direct or strict-interior ingress. No
retained path or historical symbol survives, so this remains analysis-only
with zero production ownership; see `docs/research/g2-at-nus-recovery.md`.

## Current G2 pathless eAT bond/connect increment

The `AT^CLEANBOND` / `AT^BLE_KEEPCONNECT` pair immediately before retained
`at_buzzer.c` is completely bounded at `[0x005A4FA4,0x005A4FD0)`: 34 code
bytes plus ten alignment/literal bytes. Two command pointers are the complete
entry set. The handlers call providers `0x004B46CE` and `0x0046F2DC`, emit
their retained acknowledgements, and return zero. No historical path or
symbols survive, so the pair remains analysis-only with zero production
ownership; see `docs/research/g2-eat-bond-connect-recovery.md`.

## Current G2 complete eAT registry increment

An exhaustive structural scan now proves that `[0x006C9260,0x006C93B0)` is
the complete stock eAT registry: exactly 21 sixteen-byte records, 336 bytes,
with no valid `AT...` record elsewhere in the image. Every record is assigned
to one of the seven closed analyses above; there are no unassigned registered
handlers. See `docs/research/g2-eat-registry-recovery.md`. This closes the
registered eAT runtime surface while leaving pathless historical source
inventories and production replacements as separate future work.

## Current G2 protobuf-service frontier census

All 15 retained `platform\protocols\pb_service_*` paths are now ranked against
the authenticated 7,370-function corpus. They anchor 119 discovered bodies /
40,844 body bytes. The completed health closure separately restores one
Ghidra-missed wrapper beyond that anchor census. The five smallest closures, `pb_service_translate.c`,
`pb_service_glasses_case.c`, `pb_service_ring.c`, `pb_service_conversate.c`,
and `pb_service_teleprompt.c`, are complete below; the Even-AI, terminal, and
device-configuration, health, setting, and onboarding closures are complete
too; notification is next.
See `docs/research/g2-pb-service-frontier-ranking.md`; the counts are lower
bounds and do not infer pathless functions or production ownership.

## Current G2 translate protobuf-service increment

The retained `pb_service_translate.c` object is completely bounded at
`[0x0059F53C,0x0059FAE0)`: four exact-named bodies / 1,324 code bytes and a
120-byte pool. Eight direct entries, 74 body calls, nanopb decode/encode
buffers, status codes, 3,000-ms duplicate suppression, message subtypes 5/6/7,
and master-gated BLE send/notify paths are pinned. Historical source remains
unavailable, so this is analysis-only with zero production ownership. See
`docs/research/g2-pb-service-translate-recovery.md`.

## Current G2 glasses-case protobuf-service increment

The retained `pb_service_glasses_case.c` object is completely bounded at
`[0x00510A0C,0x00510FD8)`: four exact-named bodies / 1,360 code bytes and a
124-byte pool. Four exact-start entries, 86 body calls, nanopb RX/TX buffers,
status codes, the command-1/nested-selector-3 message layout, five case-state
bytes, notification sequence behavior, and service-`0x81` BLE send/notify
paths are pinned. Five independently authored source functions compile to 546
text bytes plus ten alignment bytes; four guarded redirects replace all 1,360
stock body bytes while retaining the 124-byte official pool. Host behavior,
strict relocation, component, package, and deployment-plan gates are green.
Live service-`0x81` temple/case exchange and physical case-state validation are
blocked by unavailable physical evidence; future qualification requires authorized evidence. See
`docs/research/g2-pb-service-glasses-case-recovery.md`. The next bounded
protobuf-service frontier was `pb_service_ring.c`, now closed below.

## Current G2 ring protobuf-service increment

The retained `pb_service_ring.c` object is completely bounded at
`[0x005CE1DC,0x005CE7C4)`: four exact-named bodies / 1,362 code bytes and a
150-byte alignment/pool tail. Three internal exact-start calls, one stored
relay callback, 82 body calls, nanopb status/buffer contracts, bounded
six-byte MAC copying, event ID/parameter behavior, and service-`0x91` BLE
transmit are pinned. The only raw interior candidate is proven to be the
second halfword of `SDIV`, leaving zero real interior ingress. Historical
source remains unavailable, but a clean-room five-function implementation now
compiles to 594 text bytes plus four alignment bytes. Four guarded redirects
replace all 1,362 stock body bytes and retain the 150-byte official pool. Host,
analyzer, component, package, and deployment-plan gates are green. Paired-G2
BLE relay and live nanopb/ring-event validation remain explicitly blocked by
future-required authorized physical evidence. See
`docs/research/g2-pb-service-ring-recovery.md`; conversate is the next retained
protobuf-service frontier, now closed below.

## Current G2 conversate protobuf-service increment

The retained `pb_service_conversate.c` object is completely bounded at
`[0x005B1B4C,0x005B22BC)`: six exact-named bodies / 1,776 code bytes and a
128-byte pool. Ten exact-start entries, 96 body calls, caller-owned RX decode,
the 3,000-ms duplicate filter, the shared 0xFAC-byte TX message, and five
command/tag envelopes over service `0x0B` are pinned with zero stored or
strict-interior ingress. Eight clean-room source functions now compile to
1,098 text bytes plus eight alignment bytes; 33 strict relocations and six
guarded redirects replace all 1,776 stock body bytes. Software gates are green;
live BLE/peer/UI validation is blocked by unavailable physical evidence; future qualification requires authorized hardware. See
`docs/research/g2-pb-service-conversate-recovery.md`; teleprompt is closed
below.

## Current G2 teleprompt protobuf-service increment

The retained `pb_service_teleprompt.c` object is completely bounded at
`[0x005885B4,0x00588D74)`: seven exact-named bodies / 1,854 code bytes and a
130-byte alignment/literal tail. Eleven exact-start entries, 98 body calls,
caller-owned RX decode with 3,000-ms replay filtering, the shared 0xF58-byte
TX message, and six command/tag envelopes over service 6 are pinned. The
only raw interior candidate is the second halfword of a valid `MUL`, leaving
zero real strict-interior ingress. Nine clean-room source functions compile to
1,348 text bytes plus four alignment bytes; 39 strict relocations and seven
guarded redirects replace all 1,854 stock body bytes while retaining the
130-byte official tail. Software gates are green; live BLE/peer/UI validation
is blocked by unavailable physical evidence; future qualification requires authorized hardware. See
`docs/research/g2-pb-service-teleprompt-recovery.md`; Even-AI is closed below.

## Current G2 Even-AI protobuf-service increment

The retained `pb_service_even_ai.c` object expands from seven initial anchors
to a complete 25-function object at `[0x004E31CC,0x004E54C8)`: 8,404 code
bytes plus 552 distributed alignment/pool bytes. Twenty-six exact-start
entries, 494 body calls, 23 assertion records, the immediate one-byte replay
filter, ten command/tag pairs, three notification variants, and the shared
0x20C-byte message over service 7 are pinned. There is zero direct or stored
exact-entry interior ingress. Historical source remains unavailable, but the
clean-room production source supplies 27 functions, 2,832 compiled text bytes,
36 alignment bytes, and 107 strict relocations. Twenty-five redirects replace
all 8,404 stock body bytes while retaining the authenticated 552-byte gap/pool
closure. Software gates are green; live paired-temple service-7 BLE and
Even-AI UI validation is blocked by unavailable physical evidence; future qualification requires authorized
responsive hardware. See `docs/research/g2-pb-service-even-ai-recovery.md`;
terminal is closed below.

## Current G2 terminal protobuf-service increment

The retained `pb_service_terminal.c` object is completely bounded at
`[0x005CE7C4,0x005CF2B4)`: 13 exact-named bodies / 2,554 code bytes and a
246-byte alignment/literal tail. Thirty-three exact-start entries, 130 body
calls, caller-owned RX decode with 3,000-ms replay filtering, eleven supported
tag layouts, ten notify envelopes plus the command response, and the shared
0x850-byte message over service `0x30` are pinned. Direct and `B.W`
strict-interior ingress and stored exact-entry pointers are zero; 15 raw
interior-looking byte windows are retained as accidental collision evidence.
Historical source remains unavailable, but the independently authored
`pb_service_terminal.c` is production-routed: fifteen source functions emit
1,368 text bytes plus eight alignment bytes under 23 strict relocations, and
thirteen whole-body redirects replace all 2,554 stock body bytes. Host tests
exercise the complete RX/TX contract and the canonical 4,503,622-byte package
is byte-pinned. Live service-`0x30` master/peer BLE and terminal-UI qualification
is blocked by unavailable physical evidence; future qualification requires authorized G2
master/peer and terminal-UI evidence. See
`docs/research/g2-pb-service-terminal-recovery.md`; device configuration is
closed below.

## Current G2 device-config protobuf-service increment

The retained `pb_service_dev_config.c` object is completely bounded at
`[0x004D83D8,0x004D8F4C)`: three exact-named bodies / 2,646 code bytes and
286 distributed gap/pool bytes. Three exact-start entries, 172 body calls, a
14-command dispatcher, the error-code classifier, the command-10/tag-9 error
response, and the shared 0xD0-byte message over service `0x80` are pinned.
Direct and `B.W` strict-interior ingress and stored exact-entry pointers are
zero. Historical source remains unavailable, so this is analysis-only with
zero production ownership. See
`docs/research/g2-pb-service-dev-config-recovery.md`; health is closed below.

## Current G2 health protobuf-service increment

The retained `pb_service_health.c` object is completely bounded at
`[0x0055A558,0x0055B2A4)`: eight exact-named bodies / 3,092 code bytes and
312 distributed alignment/pool bytes. The closure restores the Ghidra-missed
`PB_RxHealthMultHighlight` body at `0x0055AF14`, pins eight exact-start
entries, 180 body calls, eight assertion records, four RX helper contracts,
four command/tag transmit envelopes, and the shared 0x31C-byte message over
service `0x0E`. Direct and `B.W` strict-interior ingress and stored exact-entry
pointers are zero. Historical source remains unavailable, so this is
analysis-only with zero production ownership. See
`docs/research/g2-pb-service-health-recovery.md`; setting is closed below.

## Current G2 setting protobuf-service increment

The retained `pb_service_setting.c` object expands from nine corpus anchors to
11 exact-named functions at `[0x0049B198,0x0049C070)`: 3,466 code bytes plus
334 distributed alignment/pool bytes. Two missed wrappers at `0x0049BA58`
and `0x0049BEAC`, 23 exact-start entries, 221 body calls, duplicate-magic
suppression, full device-status construction, response/local-data serializers,
and device/recalibration/silent-mode notifications over service 9 are pinned.
Direct and `B.W` strict-interior ingress and stored exact-entry pointers are
zero. Thirteen clean-room source functions now compile to 1,650 bytes plus 14
alignment bytes. Eleven guarded redirects replace all 3,466 stock bodies
through 38 strict relocations while retaining the 334 official gap/pool bytes.
Host, component, manifest, package, deployment, aggregate-service, and origin-
accounting gates are green. Live service-9 behavior remains explicitly
hardware-deferred; see `docs/research/g2-pb-service-setting-recovery.md`.

## Current G2 onboarding protobuf-service increment

The retained `pb_service_onboarding.c` object is completely bounded at
`[0x004A78D0,0x004A8560)`: nine exact-named bodies / 3,024 code bytes and
192 distributed alignment/pool bytes. Nine exact-start entries, 181 body
calls, eight assertion records, configuration/heartbeat/event command pairs,
two notification encoders, heartbeat readiness states, and the shared
16-byte message over service `0x10` are pinned. Direct and `B.W`
strict-interior ingress and stored exact-entry pointers are zero; three raw
interior-looking byte windows are retained as accidental collision evidence.
Historical source remains unavailable, but an independently authored
12-function implementation now compiles to 878 bytes plus eight alignment
bytes. Nine guarded redirects replace all 3,024 stock body bytes through 22
strict relocations while retaining the 192 official gap/pool bytes. Host,
component, manifest, package, and closure gates are green. Live service-`0x10`
behavior remains explicitly hardware-deferred; see
`docs/research/g2-pb-service-onboarding-recovery.md`. Notification is the next
software frontier below.

## Current G2 notification protobuf-service increment

The retained `pb_service_notification.c` object is completely bounded at
`[0x004D6BA8,0x004D798C)`: nine exact-named bodies / 3,318 code bytes and
238 distributed alignment/pool bytes. Ten exact-start entries, 202 body
calls, seven assertion records, control and whitelist command pairs, the
generic response, allocated app-not-whitelisted notification, CRC status
mapping, and the shared 76-byte message over service 4 are pinned. Direct and
`B.W` strict-interior ingress and stored exact-entry pointers are zero; three
raw interior-looking byte windows are accidental collisions. Historical
source remains unavailable, but 12 clean-room functions now compile to 1,326
bytes plus 16 alignment bytes. Nine guarded redirects replace all 3,318 stock
body bytes through 34 strict relocations while retaining the 238 official
gap/pool bytes. Host, component, manifest, package, deployment, complete-
service-ledger, and origin-accounting gates are green. Live service-4 behavior
is explicitly hardware-deferred; see
`docs/research/g2-pb-service-notification-recovery.md`. Three protobuf-service
software frontiers were identified there; device-setting is now production-
routed below, leaving pair-manager.

## Current G2 device-setting protobuf-service increment

The retained `pb_service_dev_setting.c` object is completely bounded at
`[0x00542DC4,0x00543C48)`: ten exact-named bodies / 3,432 code bytes and
284 distributed alignment/pool bytes. Ten exact-start entries, 222 body calls,
20 assertion records, five receive/transmit command pairs, factory-reset and
heartbeat effects, the five-byte time cache, caller-owned nanopb storage, and
service-`0x80` transport are pinned. Direct and `B.W` strict-interior ingress
and stored exact-entry pointers are zero; one raw interior-looking byte window
is an accidental collision. Historical source remains unavailable, but 12
clean-room functions now compile to 934 bytes plus six alignment bytes. Ten
guarded redirects replace all 3,432 stock body bytes through 30 strict
relocations while retaining the 284 official gap/pool bytes. Host, component,
manifest, package, deployment, aggregate-ledger, and origin-accounting gates
are green. Live destructive reset, peer BLE, heartbeat, clock-sync, and
persistence behavior remains explicitly hardware-deferred; see
`docs/research/g2-pb-service-dev-setting-recovery.md`.

## Current G2 quicklist protobuf-service increment

The retained `pb_service_quicklist.c` object is completely bounded at
`[0x0055894C,0x005597F0)`: ten exact-named bodies / 3,468 code bytes and
280 distributed alignment/pool bytes. Ten exact-start entries, 199 body calls,
eight assertion records, item/multi-item/event command pairs, separate 0x1238
decode/transmit objects, the 0x400-byte nanopb buffer, notification sequence,
and service-`0x0C` transport are pinned. Direct and `B.W` strict-interior
ingress and stored exact-entry pointers are zero; one raw interior-looking byte
window is an accidental collision. Historical source remains unavailable, but
13 clean-room functions now compile to 1,060 text bytes plus 18 alignment
bytes. Ten guarded redirects replace all 3,468 stock bodies through 26 strict
relocations while preserving the 280 official gap/pool bytes. The multi-item
notification copy rejects counts above the twenty records that fit the
workspace. Host, component, manifest, package, deployment, aggregate-ledger,
and origin-accounting gates are green. Live service-`0x0C` peer BLE and
persistent list workflows remain hardware-deferred. See
`docs/research/g2-pb-service-quicklist-recovery.md`; pair-manager is now
source-routed as described below, so the retained protobuf-service family has
no remaining software implementation gap.

## Completed G2 pair-manager and protobuf-service frontier

The retained `pb_service_pair_mgr.c` object expands from 17 path-correlated
anchors to 20 linked functions at `[0x004BB3DC,0x004BD054)`: 6,564 code bytes
and 724 distributed alignment/pool bytes. Twenty-five exact-start entries, 418
body calls, 23 assertion records, six command/tag pairs, security-auth state,
ring connection policy, BLE parameter control, disconnect/unpair cleanup, and
service-`0x80` transport are pinned. Six stored Thumb pointers intentionally
target the ring-connect notification wrapper; direct and `B.W` strict-interior
ingress remain zero and the sole other raw candidate is an accidental
collision.

Twenty-one selector-isolated clean-room functions now compile to 2,300 Thumb
text bytes plus 22 alignment bytes with 97 strict relocations. Twenty guarded
redirects replace all 6,564 stock body bytes while retaining the authenticated
724-byte gap/pool. Host behavior, selector compilation, component, manifest,
package, aggregate-ledger, frontier, and origin-accounting gates are green.
Live security-auth, pipe-role, ring-connect, BLE-parameter, disconnect, and
unpair workflows are blocked by unavailable physical evidence; future qualification
requires an authorized responsive G2 pair-manager peer.

This closes every retained `pb_service_*` software path. The original
119-function / 40,844-byte lower-bound census reconciles to 143 linked
functions, 47,644 body bytes, and 51,744 physical object bytes across all 15
services. Historical source-only inventory remains unavailable. All 15
services route all 47,644 stock body bytes through production C. See
`docs/research/g2-pb-service-pair-mgr-recovery.md` and the pinned complete
closure manifest.

## Current G2 EFS-service and first-party frontier increment

The retained `platform\protocols\efs_service\efs_service.c` object is now
completely bounded at `[0x00456722,0x00458DF0)`. Six retained anchors plus six
restored pathless functions contribute 9,276 code bytes; 658 owned pool/gap
bytes bring the physical object to 9,934 bytes. Thirty-five exact-start direct
calls, 559 body calls, ten intra-body wide branches, frame IDs `0xC4..0xC7`,
the 0x78-byte transfer state, separate 4-KiB import/export buffers, and all
import/export type and CRC contracts are pinned. Real strict-interior and
stored-entry ingress are zero. A clean-room twelve-function C reconstruction
now compiles to 2,936 text bytes plus 16 alignment bytes with 68 strict
relocations. Guarded redirects replace all 9,276 stock body bytes while
retaining the authenticated 658-byte compatibility gap/pool. Host behavior,
Cortex-M55 selectors, component, package, and flash-plan gates pass. Historical
source remains unavailable. Live EFS media qualification is deferred by project
direction; future qualification requires an authorized G2 peer/media pair.

The reproducible first-party census now partitions all 234 retained paths: 68
closed and 166 open. Closed paths anchor 361 functions / 142,762 body bytes;
open paths anchor 869 / 342,512, with no cross-status function. Complete-object
records total 183,126 body bytes, while 67 records report 199,124 known
physical bytes. These are lower-bound retained-path metrics, not whole-image
source coverage. See `docs/research/g2-efs-service-recovery.md` and
`docs/research/g2-first-party-frontier-census.md` and
`docs/research/g2-ota-service-recovery.md`.

The smallest genuinely open retained-path object,
`app\gui\PdtDistortionTest\pdt_distortion_test.c`, is now closed at
`[0x005CF2B4,0x005CF634)`: four functions / 850 body bytes / 896 physical
bytes. The audit restored a four-byte always-true predicate missed by Ghidra,
authenticated its pointer-table entry, closed the screen-ID `0x110` descriptor,
and pinned the event-2 LVGL object tree and adjacent gray-screen boundary. It
remains analysis-only with no historical source or package ownership; see
`docs/research/g2-pdt-distortion-test-recovery.md`.

The adjacent `app\gui\PdtGrayScreen\pdt_gray_screen.c` object is closed too:
three pointer-routed functions / 340 body bytes / 372 physical bytes, including
the second restored always-true predicate and the exact eight-band symmetric
grayscale pattern. See `docs/research/g2-pdt-gray-screen-recovery.md`.

The contiguous production-screen family endpoint,
`app\gui\ProductionTest\production_test.c`, is also closed: three functions /
286 body bytes / 316 physical bytes, its screen-ID `0x10B` registration, and
the exact 3×3 white-dot grid are pinned in
`docs/research/g2-production-test-screen-recovery.md`.

The retained `platform\ble\profiles\gatt\profile_gatt.c` object is no longer
opaque first-party glue. All six bodies / 322 bytes map to Packetcraft Cordio
`gatt_main.c`; exact r20.05c source/header blobs are admitted under Apache-2.0,
and the only local delta is an EasyLogger expansion before `GattDiscover`'s
unchanged upstream call. See `docs/research/cordio-gatt-profile-source-recovery.md`.

The adjacent `platform\ble\profiles\ancc\profile_ancc.c` object is also
upstream-founded rather than opaque product glue. Its complete
`[0x004BEA04,0x004BF990)` boundary has 21 bodies / 3,712 code bytes / 3,980
physical bytes. AmbiqSuite's 17-definition ANCC source explains 12 stock
functions; nine bounded functions are G2 message, synchronization, whitelist,
callback, and logging extensions. Exact 2.5.1 source/header blobs are admitted
at selected public commit `de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f`.
The implementation is source-identical from authenticated 2.2.0 through 2.5.1
imports, so no unique historical producing commit is claimed. See
`docs/research/ambiqsuite-ancc-profile-source-recovery.md`.

The immediately preceding EUS/ESS/EFS/NUS profile group is now authenticated
as first-party Cordio integration rather than hidden upstream code. Its four
contiguous objects occupy `[0x004BDE4C,0x004BEA04)`, with 21 bodies / 2,374
code bytes / 3,000 physical bytes. The common four-byte state, connection/CCC
events, send events `0xA8..0xAB`, provider handles `0x0844..0x08A4`, direct
call topology, and retained-path pointers are pinned. AmbiqSuite lacks these
profiles, and Nordic's NUS implementation has a different API/event model.
See `docs/research/g2-ble-transport-profiles-recovery.md`.

The final OTA and Ring paths complete the retained BLE-profile directory. OTA
occupies 700 physical bytes with seven functions / 620 body bytes: four retain
AmbiqSuite's stable AMOTA CCC/A0/A1/handler skeleton and three are Even-local
actions. Exact 2.5.1 application/API sources are admitted at selected public
commit `de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f`, while the generating checkout
remains unobservable across four compatible release imports. Ring occupies
1,580 physical bytes with seven G2-local functions / 1,446 body bytes,
including 128-bit service discovery and epoch-qualified delayed CCC writes.
See `docs/research/g2-ble-ota-ring-profiles-recovery.md`.

The retained `ota_service.c` object is now completely bounded at
`[0x004448F4,0x004488EC)`: 25 linked functions / 15,394 body bytes plus 982
owned gap/pool bytes. The `0xC0..0xC3` frame routes, 0x70-byte transfer state,
0x60-byte export state, 4-KiB chunk/sector behavior, MRAM/filesystem/external
flash backends, CRC and read-after-write verification, filesystem healing,
107 exact-entry direct calls, and zero strict-interior ingress are pinned.
Historical source and license remain unavailable; production ownership is zero.

The retained `service_codec_host.c` object is now completely bounded at
`[0x0057BA88,0x0057DC40)`: 26 linked functions / 7,318 body bytes plus 1,314
owned gap/pool bytes. The 14-byte `BUXX` header, CRC fields, 16-byte body cap,
sequence byte, UART staging buffers, command/retry behavior, 83 exact-entry
calls, and zero real strict-interior ingress are pinned. Twenty-three exact
names survive; three pathless leaves retain semantic labels. Historical source
and license remain unavailable, so production ownership is zero. See
`docs/research/g2-service-codec-host-recovery.md`.

The adjacent retained `service_codec_dfu.c` object is now completely bounded
at `[0x00577D7C,0x0057A46C)`: 16 linked functions / 9,052 body bytes plus 916
owned gap/pool bytes. Its `FWPK` package header and 16-byte record layout,
boot/main image allocation and CRC checks, 230,400-baud two-stage boot
download, 256-byte chunking, 8-KiB flash scratch, conditional version check,
34 exact-entry calls, and zero real strict-interior ingress are pinned.
Historical source and license remain unavailable, so production ownership is
zero. See `docs/research/g2-service-codec-dfu-recovery.md`.

The retained `service_touch_dfu.c` object is now completely bounded at
`[0x0055FCB4,0x00561810)`: 32 linked functions / 6,430 body bytes plus 574
owned gap/pool bytes. Its `/firmware/touch.bin` `FWPK` package and type-3
record, framed command/reply checksum contract, 32-byte packets, 128-byte
program blocks, version-gated update sequence, 60 exact-entry calls, and zero
real strict-interior ingress are pinned. Twelve exact names survive and twenty
pathless leaves retain semantic labels. Historical source remains unavailable,
but 32 independently authored leaves now replace all 6,430 stock body bytes.
They compile to 3,134 Thumb bytes plus 38 alignment bytes with 70 strict
relocations. CRC/framing, FWPK loading, 32/128-byte transfer, version skip and
force paths, cleanup, all selector builds, component/package/flash-plan, and
origin-accounting gates pass. Live destructive touch programming, reset,
version readback, I2C timing, and recovery qualification is deferred by project
direction; future qualification requires an authorized controller fixture or
golden capture. See
`docs/research/g2-service-touch-dfu-recovery.md`; wider firmware functional
completeness is not claimed.

## Current bootloader progress-service increment

The 228-byte primary and 198-byte secondary progress services at
`[0x00423524,0x004236CE)` are now exact maintained C under both reviewed target
toolchains. Six focused tests cover authenticated bodies, descriptor/FIFO
paths, progress mirrors, exhaustion/completion callbacks, pump/snapshot
behavior, interrupt restoration and dual compilation.

Canonical accounting is 23,329 source-owned, 16,528 generated patch, 16
alignment, and 123,967 retained official bytes across 282 source-owned
functions, five caves, 79 exact in-place leaves, and 201 patch sites. The
4,640,329-byte flash plan has SHA-256
`d9fe2b2028f168a1f3e54a1a26f0783c436173c319c143e0835b9bd5c0e7ca23`
with 6,667 placed and zero unresolved regions; provider and byte-identical
unsigned-package hashes
remain unchanged.

No hardware operation occurred. The earliest retained executable body remains
at `0x0042308E`; live FIFO/descriptor/interrupt/DMA/callback/concurrency/MMIO
qualification is blocked by unavailable physical evidence; future qualification requires authorized responsive
evidence, and firmware-wide functional completeness is not claimed.

## Current bootloader register-service increment

The 44-byte register-OR, 42-byte register-write, and 58-byte dual-register
query services around `[0x004236CE,0x00423764)` are now exact maintained C under
both reviewed target toolchains without relocations. Five focused tests cover
authenticated bodies/literals, bank selection, bit preservation, writes,
selectors, invalid types, and dual compilation.

Canonical accounting is 23,473 source-owned, 16,528 generated patch, 16
alignment, and 123,823 retained official bytes across 285 source-owned
functions, five caves, 82 exact in-place leaves, and 201 patch sites. The
4,643,183-byte flash plan has SHA-256
`9618a0d0f2ad5dfb572479320d8ec8e15a011a600edcd8d9bbd542c3625c4d66`
with 6,671 placed and zero unresolved regions; provider and byte-identical
unsigned-package hashes remain unchanged.

No hardware operation occurred. The earliest retained executable body remains
at `0x0042308E`; live register/MMIO/concurrency/peripheral qualification is
blocked by unavailable physical evidence; future qualification requires authorized responsive evidence, and
firmware-wide functional completeness is not claimed.

## Prior bootloader service-dispatch increment

The 176-byte per-instance service dispatcher at
`[0x0042377C,0x0042382C)` is now exact maintained C under both reviewed target
toolchains with six strict calls. Five focused tests cover authenticated pools,
validation, active/inactive flag routing, progress mirroring, callback
arguments, cleanup, and dual compilation.

Canonical accounting is 23,649 source-owned, 16,528 generated patch, 16
alignment, and 123,647 retained official bytes across 286 source-owned
functions, five caves, 83 exact in-place leaves, and 201 patch sites. The
4,644,623-byte flash plan has SHA-256
`8151fe29dbd1b22c69b72c96d01fc363ffbcd5e469e219cd105fe3f7172af7bd`
with 6,673 placed and zero unresolved regions; provider and byte-identical
unsigned-package hashes remain unchanged.

No hardware operation occurred. The earliest retained executable body remains
at `0x0042308E`; live interrupt/register/callback/concurrency/MMIO
qualification is blocked by unavailable physical evidence; future qualification requires authorized responsive
evidence, and firmware-wide functional completeness is not claimed.

## Prior bootloader bounded memory-exchange increment

The 86-byte two-buffer exchange and 110-byte three-buffer rotation at
`[0x00423864,0x00423928)` are now exact maintained C under both reviewed target
toolchains with seven strict copy calls. Four focused tests cover authenticated
bodies/boundaries, zero length, direct-byte operation, the 64- and 128-byte
thresholds, multi-chunk operation, untouched suffixes, and dual compilation.

Canonical accounting is 23,845 source-owned, 16,528 generated patch, 16
alignment, and 123,451 retained official bytes across 288 source-owned
functions, five caves, 85 exact in-place leaves, and 201 patch sites. The
4,646,731-byte flash plan has SHA-256
`d6ddc3470a69ae4b00ea43ae4cd8f7a511048e3934f9694d3974a634d21ed26e`
with 6,676 placed and zero unresolved regions; provider and byte-identical
unsigned-package hashes remain unchanged.

No hardware operation occurred. The earliest retained executable body remains
at `0x0042308E`, and the sequential frontier is `0x00423928`; hardware-dependent
qualification is blocked by unavailable physical evidence; future qualification requires authorized responsive evidence,
and firmware-wide functional completeness is not claimed.

## Prior bootloader rotate-to-front increment

The 74-byte rotate-to-front helper at `[0x00423928,0x00423972)` is now exact
maintained C under both reviewed target toolchains with two strict copy calls
and one strict overlap-safe move call. Four focused tests cover authenticated
boundaries, zero and first-element no-ops, threshold and multi-chunk widths,
untouched suffixes, the original-width address rule, and dual compilation.

Canonical accounting is 23,919 source-owned, 16,528 generated patch, 16
alignment, and 123,377 retained official bytes across 289 source-owned
functions, five caves, 86 exact in-place leaves, and 201 patch sites. The
4,647,450-byte flash plan has SHA-256
`99cd47d54664ac5e270fe43e987776719fb3753f53ca435fadd7e6d0fb83d0f3`
with 6,677 placed and zero unresolved regions; provider and byte-identical
unsigned-package hashes remain unchanged.

No hardware operation occurred. The earliest retained executable body remains
at `0x0042308E`, and the sequential frontier is `0x00423972`; hardware-dependent
qualification is blocked by unavailable physical evidence; future qualification requires authorized responsive evidence,
and firmware-wide functional completeness is not claimed.

## Current bootloader three-element comparator/exchange increment

The exact 80-byte helper at `[0x00423972,0x004239C2)` implements a
three-comparison exchange network. Four focused tests cover every distinct
permutation, duplicates, comparison order, successor authentication, and dual
target compilation.

Canonical accounting is 23,999 source-owned, 16,528 generated patch, 16
alignment, and 123,297 retained official bytes across 290 source-owned
functions, five caves, 87 exact in-place leaves, and 201 patch sites. The
4,648,165-byte flash plan has SHA-256
`17bc9a9a59b2902f8b25aa42a209f536c8e26be48ba051a17ab0b627a4a83606`
with 6,678 placed and zero unresolved regions. No hardware operation occurred;
the earliest retained executable remains `0x0042308E`, the sequential frontier
is `0x004239C2`, and firmware-wide completeness is not claimed.

## Current bootloader Floyd max-heap sift increment

The exact 134-byte helper at `[0x004239C2,0x00423A48)` implements Floyd's
max-heap descent and upward-repair algorithm. Seven focused tests cover the
exclusive count boundary, both-child selection, multi-level descent, upward
repair, subtree isolation, no-op behavior, comparator order, authenticated
successor, and dual target compilation.

Canonical accounting is 24,133 source-owned, 16,528 generated patch, 16
alignment, and 123,163 retained official bytes across 291 source-owned
functions, five caves, 88 exact in-place leaves, and 201 patch sites. The
4,648,863-byte flash plan has SHA-256
`34174d5c0e21d3fadf725d23a1d3a3942ee9de42428d69a32007e71647dd9cf2`
with 6,679 placed and zero unresolved regions. No hardware operation occurred;
the earliest retained executable remains `0x0042308E`, the sequential frontier
is `0x00423A48`, and firmware-wide completeness is not claimed.

## Current bootloader introspective qsort increment

The exact 704-byte core and 24-byte wrapper at
`[0x00423A48,0x00423D20)` implement sampled three-way introsort with heap-sort
fallback and small-partition insertion. Six host tests cover identity,
null/no-op behavior, whole-record movement, duplicates, deterministic arrays
across the 33-element threshold, and dual target compilation.

Canonical accounting is 24,861 source-owned, 16,528 generated patch, 16
alignment, and 122,435 retained official bytes across 293 source-owned
functions, five caves, 90 exact in-place leaves, and 201 patch sites. The
4,650,270-byte flash plan has SHA-256
`34f78e0fc343ebf1daee9a127dee83f548bc03226d8711e8b4774ed1b07eda0b`
with 6,681 placed and zero unresolved regions. No hardware operation occurred;
the earliest retained executable remains `0x0042308E`, the sequential frontier
is `0x00423D20`, and firmware-wide completeness is not claimed.

## Current bootloader global hardware-control increment

Six exact bodies totaling 228 bytes in `[0x00423D20,0x00423E0C)` implement
global initialization, register query/test, zero-index wrapping, control-bit
clearing, status normalization, and interrupt-atomic countdown/latch handling.
Six focused tests cover all software-visible paths and both target toolchains.

Canonical accounting is 25,089 source-owned, 16,528 generated patch, 16
alignment, and 122,207 retained official bytes across 299 source-owned
functions, five caves, 96 exact in-place leaves, and 201 patch sites. The
4,656,017-byte flash plan has SHA-256
`15fdf5e7b3fb0e99f62ceb0195084a37bdbe1db8a65d66bd3649f7318d3e486f`
with 6,689 placed and zero unresolved regions. No hardware operation occurred.
Live register, timer, interrupt, debug, SRAM, MMIO, and cold-boot validation is
blocked by unavailable physical evidence; future qualification requires authorized G2
physical evidence.
The earliest retained executable remains `0x0042308E`; after retained SRAM
literals, the sequential executable frontier is `0x00423E14`. Firmware-wide
completeness is not claimed.

## Current bootloader hardware-control state-mapper increment

The exact 44-byte body at `[0x00423E14,0x00423E40)` is now maintained source.
Five focused tests pin state-one advancement and flag merging, state-two
override behavior, all other state values, the authenticated successor, and
both reviewed target compilers.

Canonical accounting is 25,133 source-owned, 16,528 generated patch, 16
alignment, and 122,163 retained official bytes across 300 source-owned
functions, five caves, 97 exact in-place leaves, and 201 patch sites. The
provider and 4,745,526-byte package remain byte-identical. The 4,657,431-byte
flash plan has SHA-256
`ce6175e68c69cecbd2de52dc71a30c7a9eb607c51c224380e88786d3761f85f6`
with 6,691 placed and zero unresolved regions. No hardware operation occurred.
Live state, SRAM, MMIO, timing, interrupt, and cold-boot validation is deferred
by project direction; future qualification requires authorized G2 physical
evidence. The
earliest retained executable remains `0x0042308E`; the sequential executable
frontier is `0x00423E40`. Firmware-wide completeness is not claimed.

## Current bootloader MSPI FIFO, command-queue, and DMA-programming increment

Eight exact source-owned bodies now cover `[0x00423E40,0x004240AA)`: FIFO write
(74 bytes), FIFO read (158), command-queue init (44), term (58), enable (30),
disable (12), pause (134), and high-priority DMA programming (108). The typed host suites cover module bounds, FIFO addressing,
partial words, both timeout paths, queue configuration, handle lifecycle,
clock short-circuiting, CQ pause/designated-pause/DMA-idle behavior, provider
status propagation, DMA ring selection and register ordering, and the upstream lack of extra private-helper validation.
Both reviewed target profiles match every linked stock body exactly.

Canonical accounting is 25,751 source-owned, 16,528 generated patch, 16
alignment, and 121,545 retained official bytes across 308 source-owned
functions, five caves, 105 exact in-place leaves, and 201 patch sites. The
163,840-byte provider and 4,745,526-byte unsigned package remain byte-identical
with SHA-256 `3ae28d27...55eac` and `3c8cdcdb...c785`. The 4,663,145-byte
flash plan has SHA-256
`910dc1ab8c79edd6d7a06ced0f54d7ae0f395e6c9262f5de50f30893831d6e53`
with 6,699 placed, zero unresolved, six container-only, and six protected
regions. No hardware operation occurred.

Physical FIFO, command-queue, clock, timeout, DMA, register, SRAM, interrupt,
and cold-boot qualification is blocked by unavailable physical evidence; the specified
authorized evidence remains a future acceptance requirement.
Firmware-wide completeness is not claimed: the earliest
retained executable remains `0x0042308E`, and the sequential executable
frontier is `0x004240AA` (`sched_hiprio`).

## Current bootloader per-instance FIFO increment

The 70-byte read, 52-byte write and 14-byte drain bodies at
`[0x004232C8,0x00423350)` are exact maintained C under both reviewed target
toolchains. Five focused tests cover polling, empty/error/partial behavior,
counts, four-bank selection, drain arguments and dual compilation.

Canonical accounting is 22,463 source-owned, 16,528 generated patch, 16
alignment, and 124,833 retained official bytes across 273 source-owned
functions, five caves, 70 exact in-place leaves, and 201 patch sites. The
4,630,216-byte flash plan has SHA-256
`e72497682bb30fa59d7389f82853b14aafe094568da5aa816ea50e060824f7ae`
with 6,652 placed regions; provider and byte-identical unsigned-package hashes
remain unchanged.

No hardware operation occurred. The earliest retained executable body remains
at `0x0042308E`; live FIFO/MMIO/concurrency/peripheral qualification is
blocked by unavailable physical evidence; future qualification requires authorized responsive evidence, and
firmware-wide functional completeness is not claimed.

## Current bootloader mode-dispatch increment

All five executable bodies totaling 296 bytes in
`[0x004233E8,0x00423524)` are now exact maintained C under both reviewed target
toolchains; the intervening 20 bytes are authenticated literal/register data.
Ten focused tests cover type validation, all routes, latches, status clearing,
progress, delay, completion, timeouts and dual compilation.

Canonical accounting is 22,903 source-owned, 16,528 generated patch, 16
alignment, and 124,393 retained official bytes across 280 source-owned
functions, five caves, 77 exact in-place leaves, and 201 patch sites. The
4,636,680-byte flash plan has SHA-256
`ba2f0360217b861d0dfbcdc5895e0d9ee5c6b1f5c4c2d98315756f5abf4e6574`
with 6,661 placed regions; provider and byte-identical unsigned-package hashes
remain unchanged.

No hardware operation occurred. The earliest retained executable body remains
at `0x0042308E`; live MMIO/timer/interrupt/concurrency/peripheral qualification
is blocked by unavailable physical evidence; future qualification requires authorized responsive evidence, and
firmware-wide functional completeness is not claimed.

## Current bootloader critical-section FIFO-adapter increment

The 64-byte snapshot and 80-byte pump bodies at
`[0x00423350,0x004233E0)` are exact maintained C under both reviewed target
toolchains. Five focused tests cover authenticated boundaries, snapshot status
mapping, descriptor-to-FIFO pumping, interrupt-token restoration and dual
compilation.

Canonical accounting is 22,607 source-owned, 16,528 generated patch, 16
alignment, and 124,689 retained official bytes across 275 source-owned
functions, five caves, 72 exact in-place leaves, and 201 patch sites. The
4,631,646-byte flash plan has SHA-256
`ebcb7763eb7de396f0ed208e61807dcda6bcebb62eb3288d90a4bd54e4a4cca0`
with 6,654 placed regions; provider and byte-identical unsigned-package hashes
remain unchanged.

No hardware operation occurred. The earliest retained executable body remains
at `0x0042308E`; live FIFO/MMIO/descriptor/interrupt/concurrency/peripheral
qualification is blocked by unavailable physical evidence; future qualification requires authorized responsive
evidence, and firmware-wide functional completeness is not claimed.

## Bootloader pin-group dispatcher is production-routed (2026-08-26)

The complete two-bank pin-group dispatcher `[0x0041FADC,0x0041FCF6)` now
routes to maintained clean-room C. The 538-byte authenticated body has two
callers; host tests pin its cumulative subtype groups, all SRAM configuration
offsets and pin numbers, low-byte truncation, ordering, and no-op cases. Both
reviewed Clang profiles emit the same relocation-free 428-byte leaf.

Apple overlay/provider identities are 9,916 / 158,516 bytes with SHA-256
`f00be08414c7e4731ed8e2e61ed1f8041f105c520d941c0b26d16ba4f4e8143a`
and `5ec3947c373c9d765d8c3385c0f7d436f8c4599ddae90429bc48263f1f80783a`;
Linux identities are 9,900 / 158,500 bytes with SHA-256
`1b531362e7f7ce06225ecdc068dcc0b124eeb5c84a1570f7f071e11497acdd93`
and `06e369900458478ec088319400809d6bfb7883c3ddeb0808e3fff0f8bb52e4f5`.
The Apple/Linux packages are 4,740,094 / 4,516,088 bytes with 6,464 / 3,432
placed regions and two unresolved boundaries each. Nothing was sent to
hardware. Live pinmux/GPIO/electrical and cold-boot qualification is deferred
by project direction; future qualification requires authorized G2 physical
evidence. Retained spans after `0x0041FCF6` remain software gaps, so
firmware-wide completeness is not claimed.

## Bootloader MX25U25643G JEDEC-ID reader is production-routed (2026-08-27)

The complete authenticated `[0x0042059E,0x004205F4)` reader now routes to
maintained clean-room C. Stock and host tests pin command `0x9F`, three receive
bytes, status/failure behavior, exact diagnostic metadata, output preservation,
and identifier packing. Both reviewed profiles emit relocation-free 100-byte
leaves; the timing scan and public initializer enter through the routed stock
address.

Apple/Linux overlay/provider identities are 12,168/160,768 and
12,148/160,748 bytes. Canonical accounting is 12,153 source-owned, 13,466
generated patch, 16 alignment, and 135,133 retained official bytes across 178
functions, 159 relocated leaves, and 176 patch sites. Unsigned packages are
4,742,346 / 4,518,336 bytes with 6,507 / 3,454 placed regions and two
unresolved hardware regions each.

Nothing was signed, flashed, installed, reset, booted, or sent to hardware.
Live command acceptance, JEDEC byte order, MSPI/XIP/external-flash behavior,
and cold-boot validation is blocked by unavailable physical evidence; future qualification
requires authorized G2 physical evidence. Executable bodies at
and after `0x004205F4` remain software gaps, so functional completeness is not
claimed.

## Bootloader MX25U25643G read transfer is production-routed (2026-08-27)

The complete authenticated `[0x004205F4,0x0042069E)` wrapper now routes to
maintained clean-room C. Stock and host evidence pin handle/argument/address
validation, the exact 24-byte Ambiq transfer descriptor, read direction,
1,000,000-cycle timeout, raw HAL status, failure-only diagnostics, and five
authenticated callers. Both compilers emit the same relocation-free 172-byte
leaf; Linux adds four placement-alignment bytes.

Apple/Linux overlay/provider identities are 12,340/160,940 and
12,324/160,924 bytes. Canonical accounting is 12,325 source-owned, 13,636
generated patch, 16 alignment, and 134,963 retained official bytes across 179
functions, 160 relocated leaves, and 177 patch sites. Unsigned packages are
4,742,518 / 4,518,512 bytes with 6,509 / 3,455 placed regions and two
unresolved hardware regions each.

Nothing was signed, flashed, installed, reset, booted, or sent to hardware.
Live descriptor ABI, HAL timeout/status behavior, external-flash reads,
JEDEC/MSPI/XIP behavior, and cold-boot qualification is deferred by project
direction; future qualification requires authorized G2 physical evidence.
Executable bodies at and after `0x0042069E` remain software gaps, so
functional completeness is not claimed.

## Current bootloader LittleFS block-erase increment

The complete authenticated `[0x00421348,0x00421372)` callback now routes to a
48-byte freestanding clean-room C leaf at `[0x00421250,0x00421280)`. Five
focused tests pin the stock body, successor literal gap, configuration pointer,
source-owned erase/logger calls, address wrap, forwarding, failure diagnostic,
`LFS_ERR_IO` mapping, and Cortex-M55 compilation. The cave follows the program
leaf inside the same authenticated generated initializer tail.

Apple/Linux providers are 163,840 /
`a4a1ff23a237f05a514a73c17d068c2fc27e6eb3f06c9a030387d277c0cde99f`
and 163,824 /
`528ea3ce26d7acdf93a79be2b3cfde38663b13f85ae1a37028a85fc27ddbde84`.
Canonical accounting is 15,333 source-owned, 16,386 generated patch, 16
alignment, and 132,105 retained official bytes across 200 routed functions,
179 relocated leaves, two fixed caves, and 198 patch sites. Apple/Linux package
SHA-256 values are
`7b260362c3e5c2f3e9bb249a6a5dace696518a25bb2e65c8b2a2898dd9e471f5`
and `718e66428467cbc01a225e118e047b323d160271809b37e20872208933f0b235`.
The 4,566,262-byte flash plan SHA-256 is
`703ac616c132c39f9d2670a9a376e32a6558653c5d475bb203c53eb5ffb63c82`.

No hardware operation occurred. Live erase, allocation, persistence,
power-loss, diagnostics, and cold-boot qualification is blocked by unavailable physical evidence; future qualification requires that evidence. The next
opaque executable entry is the sync callback at `0x004213D4`; firmware-wide
functional completeness is not claimed.

## Current bootloader sync and address-index increment

The authenticated constant-success LittleFS sync callback at
`[0x004213D4,0x004213D8)` now redirects to an exact four-byte C leaf in the
third reclaimed initializer cave. The adjacent identity and thresholded
address-index helpers at `[0x004213D8,0x004213E6)` are compiled from C directly
at their stock addresses and reproduce all 14 stock bytes exactly under both
reviewed compiler profiles.

Canonical accounting is 15,351 source-owned, 16,386 generated patch, 16
alignment, and 132,087 retained official bytes, including 112 cave bytes and
14 exact in-place bytes. Apple/Linux provider SHA-256 values are
`a3b12625d63e769ab89d2bd9ea729e9b280ffa553f7c48a2e4b96974b60919e3`
and `9e4494d967a6402ba329b05e664842404289ad9688ffa00aca7c0e5bf7908f9d`;
package SHA-256 values are
`1ad64997630cb2ebd2df43ae244bda8fda3008473f254adbebde8aa9d2045f5b`
and `3aba526397878e500d0b3ccfdc38b2dd171573b6099fbdb97369fde0ee2c7f01`.
The canonical flash plan is 4,569,828 bytes /
`6570fe6cf7b172f99da733a26fe9964ea8c9f6985bfba2430359bd5fad874a4f`
with 6,567 placed regions.

No hardware operation occurred. Physical LittleFS persistence, power-loss,
diagnostic, and cold-boot qualification is blocked by unavailable physical evidence; future qualification requires that evidence; the next retained
executable body begins at `0x004213E6`, so functional completeness is not
claimed.

## Bootloader MX25U25643G write transfer is production-routed (2026-08-27)

The complete authenticated `[0x0042069E,0x0042074E)` wrapper now routes to
maintained clean-room C. Stock and host evidence pin null-handle status 2,
address and 256-byte length ceilings with status 5, accepted zero-length/null
buffer calls, the exact 24-byte write descriptor, 1,000,000-cycle timeout,
raw HAL status, failure-only diagnostics, and eight authenticated callers.
Apple clang 21 and Homebrew clang 22.1.8 emit the same relocation-free
148-byte leaf.

Apple/Linux overlay/provider identities are 12,488/161,088 and
12,472/161,072 bytes. Canonical accounting is 12,473 source-owned, 13,812
generated patch, 16 alignment, and 134,787 retained official bytes across 180
functions, 161 relocated leaves, and 178 patch sites. Unsigned packages are
4,742,666 / 4,518,660 bytes with 6,511 / 3,456 placed regions and two
unresolved hardware regions each.

Nothing was signed, flashed, installed, reset, booted, or sent to hardware.
Live descriptor/HAL behavior, external-flash writes, write-enable/program/
erase sequencing, JEDEC/MSPI/XIP behavior, and cold-boot qualification is
blocked by unavailable physical evidence; future qualification requires authorized G2
physical evidence. Executable bodies at and after `0x0042074E` remain software
gaps, so functional completeness is not claimed.

## Bootloader MX25U25643G busy status is production-routed (2026-08-27)

The complete authenticated `[0x0042074E,0x004207A2)` entry now routes to
maintained clean-room C. Stock and host evidence pin the zeroed scratch bytes,
command `0x05`, one-byte source-routed read, raw failure return and exact
diagnostic, bit-7 Boolean result, and both authenticated callers. Apple clang
21 and Homebrew clang 22.1.8 emit relocation-free 88-byte leaves with reviewed
profile-specific hashes.

Apple/Linux overlay/provider identities are 12,576/161,176 and
12,560/161,160 bytes. Canonical accounting is 12,561 source-owned, 13,896
generated patch, 16 alignment, and 134,703 retained official bytes across 181
functions, 162 relocated leaves, and 179 patch sites. Unsigned packages are
4,742,754 / 4,518,748 bytes with 6,513 / 3,457 placed regions and two
unresolved hardware regions each.

Nothing was signed, flashed, installed, reset, booted, or sent to hardware.
Live status-register/HAL/RTOS behavior, external-flash/MSPI/XIP behavior, and
cold-boot qualification is blocked by unavailable physical evidence; future qualification
requires authorized G2 physical evidence. Executable bodies at and after
`0x004207A2` remain software gaps, so functional completeness is not claimed.

## Bootloader MX25U25643G ready polling is production-routed (2026-08-27)

The complete authenticated `[0x004207A2,0x00420800)` two-function cluster now
routes to maintained clean-room C. Host and stock evidence pin 200 fast polls
with five-unit unsuccessful delays, the caller-bounded context-aware second
phase, notification value 1 for context 2, 1,000-unit delays otherwise,
success/timeout returns, the fixed bound 500, and every authenticated caller.
Both reviewed compilers emit dependency-free 88- and 12-byte leaves.

Apple/Linux overlay/provider identities are 12,676/161,276 and
12,660/161,260 bytes. Canonical accounting is 12,661 source-owned, 13,990
generated patch, 16 alignment, and 134,609 retained official bytes across 183
functions, 164 relocated leaves, and 181 patch sites. Unsigned packages are
4,742,854 / 4,518,848 bytes with 6,517 / 3,459 placed regions and two
unresolved hardware regions each.

Nothing was signed, flashed, installed, reset, booted, or sent to hardware.
Live scheduler/delay/status-register behavior, external-flash/MSPI/XIP
behavior, and cold-boot qualification is blocked by unavailable physical evidence; future
qualification requires authorized G2 physical evidence. Executable bodies at
and after `0x0042086C` remain software gaps, so functional completeness is not
claimed.

## Bootloader low-level MSPI initializer is production-routed (2026-08-27)

The complete authenticated `[0x00420254,0x00420476)` entry now routes to
maintained clean-room C. Host and stock tests pin its sole caller, busy-state
guard, HAL initialize/power/controller/device/enable order, default/custom
configuration, failure cleanup, source-owned XIP/pin/NVIC calls, interrupt
mask `0x1A80`, IRQ 21/priority 4, state publication, output pointer, and exact
diagnostics. Apple and Linux each emit a 492-byte leaf with four strict call
relocations.

Apple/Linux overlay/provider identities are 11,728/160,328 and
11,708/160,308 bytes. Accounting is 11,713 source-owned, 13,084 generated
patch, 16 alignment, and 135,515 retained official bytes across 175 functions,
156 relocated leaves, and 173 patch sites. Unsigned Apple/Linux packages are
4,741,906 / 4,517,896 bytes with SHA-256
`b440e9852e9bd24f2747249953998eb578e68043a8f66f1a70e247cb3fb01c2a`
and `8938298ab593c95da48cd0697fccbee38cf3a2a1033cb44ef275ec7495162e1f`;
their flash plans contain 6,501 / 3,451 placed regions.

Nothing was signed, flashed, installed, reset, booted, or sent to hardware.
Live HAL, interrupt, MSPI, XIP, external-flash, timing, and cold-boot validation
is blocked by unavailable physical evidence; future qualification requires authorized G2
physical evidence. Executable bodies after `0x00420476` remain
software gaps, so firmware-wide completeness is not claimed.

## Bootloader MX25U25643G public initializer is production-routed (2026-08-27)

The complete authenticated `[0x00420476,0x0042052A)` entry now routes to
maintained clean-room C. Host and stock gates pin initialization failure,
10-ms delay, device/timing preparation, JEDEC-ID read and diagnostics, final
mode selection, event-flags initialization, MSPI enable, and exact returns.
Both profiles emit a 204-byte leaf with five strict source-owned calls.

Apple/Linux overlay/provider identities are 11,932/160,532 and
11,912/160,512 bytes. Accounting is 11,917 source-owned, 13,264 generated
patch, 16 alignment, and 135,335 retained official bytes across 176 functions,
157 relocated leaves, and 174 patch sites. Unsigned packages are 4,742,110 /
4,518,100 bytes with 6,503 / 3,452 placed flash regions.

Nothing was signed, flashed, installed, reset, booted, or sent to hardware.
Live JEDEC, HAL, RTOS, interrupt, MSPI, XIP, external-flash, timing, and
cold-boot validation is blocked by unavailable physical evidence; future qualification
requires authorized G2 physical evidence. Executable bodies
after `0x0042052A` remain software gaps, so firmware-wide completeness is not
claimed.

## Bootloader MX25U25643G soft reset is production-routed (2026-08-27)

The complete authenticated `[0x0042052A,0x0042059E)` sequence now routes to
maintained clean-room C. Host tests pin commands `0x66`/`0x99`, delays 1/50
ms, failure-only logs, and the non-short-circuiting policy. Both profiles emit
a 136-byte leaf with strict delay call/tail-jump relocations.

Apple/Linux overlay/provider identities are 12,068/160,668 and
12,048/160,648 bytes. Accounting is 12,053 source-owned, 13,380 generated
patch, 16 alignment, and 135,219 retained official bytes across 177 functions,
158 relocated leaves, and 175 patch sites. Unsigned packages are 4,742,246 /
4,518,236 bytes with 6,505 / 3,453 placed flash regions.

Nothing was signed, flashed, installed, reset, booted, or sent to hardware.
Live reset, MSPI/XIP, external-flash, timing, and cold-boot validation is
blocked by unavailable physical evidence; future qualification requires authorized G2
physical evidence. Executable bodies after `0x0042059E` remain software
gaps, so firmware-wide completeness is not claimed.

## Bootloader MSPI controls are production-routed (2026-08-26)

The complete `[0x0041FE28,0x0041FE62)` enable/disable pair now routes to
maintained clean-room C. Host tests pin idempotence, retained control arguments,
state updates, and all three callers; both profiles emit the same 40-/32-byte
relocation-free leaves. With the later event-flags, guard, and XIP-config
entries included, the current cumulative Apple/Linux overlay/provider
identities are 10,500/159,100 and 10,484/159,084 bytes. Accounting is 10,487
source-owned, 11,782 generated patch, 14 alignment, and 136,817 retained
official bytes across 170 functions, 151 relocated leaves, and 168 patch sites.
Unsigned packages are 4,740,678 / 4,516,672 bytes. Nothing was sent to hardware. Live
MSPI/cold-boot behavior remains blocked, and executable bodies after
`0x0041FE62` remain software gaps; completeness is not claimed.

## Bootloader event-flags service cluster is production-routed (2026-08-27)

The complete `[0x0041FE62,0x0041FF08)` event-flags init/acquire/release cluster
now routes to maintained clean-room C. The 166 authenticated stock bytes are
replaced by three relocation-free leaves totaling 208 bytes. Host tests pin
idempotent creation, handle publication, null-handle guards, wait-forever
acquisition, release status handling, and the exact failure-only EasyLogger
records; stock scans pin all three direct callers and exact body hashes.

The later MSPI guard and XIP-config entries are now source-owned as well.
Apple overlay/provider identities are 10,500 / 159,100 bytes with SHA-256
`28c298a0ab3273a8f5ade3e900268b80b879076a33dc12e504c73e42f623ba2c`
and `d1c9554cea1418c933767ca98b93a928a978cd66ed4c7d562b918acd6e351407`.
Linux identities are 10,484 / 159,084 bytes with SHA-256
`65ecb970600c878cc4ed7916cff4c57057d7baf83ef4923630340f2e5492b3c1`
and `21636af65f7eaa7b4e20c9e5d61902dfcaf20cd9ba13a6f6edf244bfa4d19fcd`.
Accounting is 10,487 source-owned, 11,782 generated patch, 14 alignment, and
136,817 retained official bytes across 170 functions, 151 relocated leaves,
and 168 patch sites. Apple headroom is 4,740 bytes.

Unsigned Apple/Linux packages are 4,740,678 / 4,516,672 bytes with SHA-256
`81ae4b1c4f87e3d6348aa55426f6c7f3cc766aa079d94a96ec82f3ffddc76b2d`
and `bb52277456ff2d69aaa34f4639734ab5d23bcea984f153ac19795b372955de71`.
Their flash plans contain 6,490 / 3,446 placed regions, two unresolved address
regions, five container-only regions, and six protected regions. Nothing was
signed, flashed, installed, reset, booted, or sent to hardware. Live RTOS
contention, logging, and cold-boot qualification is deferred by project
direction; future qualification requires authorized G2 physical evidence.
Executable bodies after `0x0041FF60` remain software gaps, so
firmware-wide completeness is not claimed.

## Bootloader paired MSPI guards are production-routed (2026-08-27)

The complete `[0x0041FF08,0x0041FF34)` enter/exit guard pair now routes to
maintained clean-room C. The two authenticated 22-byte stock wrappers are
replaced by identical dual-profile 36- and 32-byte relocation-free leaves.
Host tests pin the `0x200271C5` bypass byte, all six callers, both conditional
paths, and exact acquire/disable versus enable/release ordering.

With the later XIP-config entry included, Apple/Linux overlay/provider
identities are 10,500/159,100 and 10,484/159,084 bytes. Accounting is 10,487
source-owned, 11,782 generated patch, 14 alignment, and 136,817 retained
official bytes across 170 functions, 151 relocated leaves, and 168 patch sites.
Unsigned packages are 4,740,678 / 4,516,672 bytes; flash plans contain 6,490 /
3,446 placed regions. Nothing was
signed, flashed, installed, reset, booted, or sent to hardware. Live RTOS
contention, MSPI timing, and cold-boot qualification is deferred by project
direction; future qualification requires authorized G2 physical evidence.
Executable bodies after `0x0041FF60` remain software gaps, so firmware-wide
completeness is not claimed.

## Bootloader MSPI timing scan is production-routed (2026-08-27)

The complete authenticated `[0x00420002,0x004201BA)` timing-scan entry now
routes to maintained clean-room C. It tests 36 coarse timing rows across all
32 fine-delay values, submits retained control request 16, accepts only a
zero-status read of packed JEDEC ID `0x002539C2`, records a pass mask per row,
chooses the first strictly longest run, computes its center through the
source-owned helper, emits the retained diagnostics, and returns the selected
six-byte configuration. Host tests execute and verify all 1,152 candidates;
stock scans pin the body, caller, table, ID, and retained call seams.

Apple/Linux Clang each emit a 420-byte leaf. The Apple leaf is at offset
10,644 with relocated SHA-256 `184a82c6…ce481`; Linux is at offset 10,612 with
relocated SHA-256 `794f106a…4c733`. Each profile has exactly two authenticated
`R_ARM_THM_CALL` relocations to the source-owned bit-run helpers. Apple/Linux
overlay/provider identities are 11,064/159,664 and 11,032/159,632 bytes.
Accounting is 11,049 source-owned, 12,384 generated patch, 16 alignment, and
136,215 retained official bytes across 173 functions, 154 relocated leaves,
and 171 patch sites.

Unsigned Apple/Linux packages are 4,741,242 / 4,517,220 bytes with SHA-256
`41ebb3212e1a8ee93e693ecd14e6eda4712310e84aaed53335a52d8bef6c9aaf`
and `3b56e6a17a41d2c20933b1a58004b8460162a21fc63e861e10ca99eceaa54b1f`.
Their flash plans contain 6,497 / 3,449 placed regions, two unresolved address
regions, five container-only regions, and six protected regions. Nothing was
signed, flashed, installed, reset, booted, or sent to hardware. Electrical
timing-window, flash-identification, XIP, and cold-boot qualification is
blocked by unavailable physical evidence; future qualification requires authorized G2
physical evidence. Executable bodies after `0x004201BA` remain software gaps,
so firmware-wide completeness is not claimed.

## Bootloader automatic MSPI timing selection is production-routed (2026-08-27)

The complete authenticated `[0x004201BA,0x00420254)` entry now routes to
maintained clean-room C. It zeroes a six-byte scan object, invokes the
source-owned exhaustive timing scan, publishes exactly six meaningful bytes on
success, preserves the active configuration on failure, and emits the retained
success/fallback diagnostics. Host tests pin both branches and prove adjacent
ABI padding is not overwritten.

Apple/Linux emit 172/184-byte leaves with one strict call relocation to the
timing scan. Their overlay/provider identities are 11,236/159,836 and
11,216/159,816 bytes. Accounting is 11,221 source-owned, 12,538 generated
patch, 16 alignment, and 136,061 retained official bytes across 174 functions,
155 relocated leaves, and 172 patch sites.

Unsigned Apple/Linux packages are 4,741,414 / 4,517,404 bytes with SHA-256
`fb425a21a6ee30862b84c48edf504d211b5e2f079b3a62461bd96fefaad33164`
and `dcce581c2f5697fce0bfb019cd2ea951f8fbbabacde0050b9a8159a5a63dece6`.
Their flash plans contain 6,499 / 3,450 placed regions, two unresolved address
regions, five container-only regions, and six protected regions. Nothing was
signed, flashed, installed, reset, booted, or sent to hardware. Electrical
timing-window, flash-identification, XIP, and cold-boot qualification is
blocked by unavailable physical evidence; future qualification requires authorized G2
physical evidence. Executable bodies after `0x00420254` remain software gaps, so
firmware-wide completeness is not claimed.

## Bootloader bit-run helpers are production-routed (2026-08-27)

The complete authenticated `[0x0041FF60,0x00420002)` pair now routes to
maintained clean-room C. The 20-byte entry computes the longest consecutive-one
run by repeated shifted intersection. The 142-byte entry preserves the exact
first-longest selection, midpoint bias, parity, bit-one, bit-30, and terminal
run adjustments. Host tests compare boundary cases and 2,048 deterministic
random words; stock scans pin both bodies and their sole callers. Apple Clang
emits 16/126-byte leaves and Linux Clang emits 16/110-byte leaves, all without
runtime relocations.

Apple/Linux overlay/provider identities are 10,642/159,242 and
10,610/159,210 bytes. Accounting is 10,629 source-owned, 11,944 generated
patch, 14 alignment, and 136,655 retained official bytes across 172 functions,
153 relocated leaves, and 170 patch sites. Unsigned packages are 4,740,820 /
4,516,798 bytes; flash plans contain 6,494 / 3,448 placed regions. Nothing was
signed, flashed, installed, reset, booted, or sent to hardware. Live mask
meaning, MSPI training/timing, external-flash, and cold-boot qualification is
blocked by unavailable physical evidence; future qualification requires authorized G2
physical evidence. Executable bodies after `0x00420002` remain software gaps, so
firmware-wide completeness is not claimed.

## Bootloader MSPI XIP configuration is production-routed (2026-08-27)

The complete authenticated `[0x0041FF34,0x0041FF60)` entry now routes to
maintained clean-room C. Host and stock-topology tests pin low-byte argument
truncation, the selector-dependent `8`/`0` write to byte five of the retained
configuration at `0x2000023C`, the write-before-control order, handle word
`0x200270DC`, request `16`, ignored status, and all three callers. Apple and
Linux Clang emit the same relocation-free 36-byte leaf.

Apple/Linux overlay/provider identities are 10,500/159,100 and
10,484/159,084 bytes. Accounting is 10,487 source-owned, 11,782 generated
patch, 14 alignment, and 136,817 retained official bytes across 170 functions,
151 relocated leaves, and 168 patch sites. Unsigned packages are 4,740,678 /
4,516,672 bytes; flash plans contain 6,490 / 3,446 placed regions. Nothing was
signed, flashed, installed, reset, booted, or sent to hardware. Live MSPI XIP,
external-flash timing, and cold-boot qualification is deferred by project
direction; future qualification requires authorized G2 physical evidence.
Executable bodies after `0x0041FF60` remain software gaps, so firmware-wide
completeness is not claimed.

## Cordio DM connection manager is production-routed

All 61 public `dm_conn.c` definitions and the adjacent vendor CCB initializer
are maintained as compilable C. Fifty-five guarded redirects plus two exact
two-byte in-place copies source-own all 57 linked stock entries / 6,216 body
bytes. The reviewed build adds 4,540 Thumb bytes and 54 alignment bytes under
92 strict relocations; five stock-dead-stripped public APIs also compile in all
target profiles.

The canonical overlay/component/package sizes are 365,448 / 3,888,844 /
4,667,338 bytes. The 3,807,191-byte flash plan has 5,475 placed, two
unresolved, five container-only, and six protected regions. Host behavior,
bounds, stock closure, target compilation, routing, manifest, deterministic
package, and flash-plan gates pass through `make cordio-dm-conn-closure`.
Live controller, peer, RF, privacy, timing, idle-state, and paired-temple
validation is blocked by unavailable physical evidence; future qualification requires authorized responsive G2/EM9305 physical
evidence. Nothing was signed, installed, or flashed, and wider firmware
functional completeness is not claimed.

## Cordio L2CAP is production-routed

All twenty linked definitions across `l2c_main.c`, `l2c_master.c`, and
`l2c_slave.c` now execute compiler-owned C. Nineteen guarded redirects and one
exact two-byte in-place copy replace all 3,372 bounded stock body bytes with
1,334 compiled Cortex-M55 bytes plus 22 alignment bytes under 28 strict
relocations. Source-only `L2cDmSigReq` also target-compiles, while all 67 CoC
definitions remain positively configuration-excluded/dead-stripped.

Host and isolated target tests cover fixed-CID and arbitrary-CID dispatch,
signaling, flow control, ACL framing, allocation failure, malformed lengths,
master/slave connection updates, one-based connection indexing, timer cleanup,
and callback initialization. The canonical overlay/component/package sizes are
354,692 / 3,878,088 / 4,656,582 bytes. The 3,501,390-byte flash plan has 5,040
placed, two unresolved, five container-only, and six protected regions.
`make cordio-l2c-runtime-closure` passes five tests. No image was signed,
flashed, or installed.

Live ATT/SMP/signaling exchange, peer/controller flow control, connection-update
timing, and buffer-lifetime qualification is blocked by unavailable physical evidence;
future qualification requires an authorized G2/EM9305 pair or golden capture.
The L2CAP software gap is
closed; wider firmware functional completeness is not claimed.

The retained `terminal_pb_msg_handler.c` object is now completely bounded at
`[0x005E8178,0x005EA224)`: 27 linked functions / 7,688 body bytes plus 676
owned gap/pool bytes. Ten retained anchors and 17 pathless restorations close
the object. Its 13-slot event dispatcher, 12 action pointers, callback ingress,
session/state gates, 2-second tool-start suppression, 56 exact-entry calls,
and zero real strict-interior ingress are pinned. The lone raw interior-call
candidate is the second halfword of a valid `UXTAB`. Nineteen exact diagnostic
names survive; historical source and license remain unavailable, so production
ownership is zero. See
`docs/research/g2-terminal-pb-msg-handler-recovery.md`.

The retained `service_whitelist.c` object is now completely bounded at
`[0x004D5930,0x004D6BA8)`: seven linked functions / 4,310 body bytes plus 418
owned gap/pool bytes. Five retained anchors and two pathless helpers close the
object. Its 8,002-byte state, five enable flags, 100 records with 64-byte IDs
and 16-byte names, filesystem/CRC cache, built-in identifiers, fail-open
disable policy, nine exact-entry calls, and zero strict-interior ingress are
pinned. Historical source and license remain unavailable, so production
ownership is zero. See `docs/research/g2-service-whitelist-recovery.md`.

The retained `teleprompt_page_data.c` object is now completely bounded at
`[0x0058A8E0,0x0058BCE0)`: 21 linked functions / 4,728 body bytes plus 392
owned gap/pool bytes. Nine retained anchors and twelve restored helpers close
the object. Its 20-slot `0x414`-stride ring, 1,036-byte page copy contract,
four-page visible window, 14-page ensure band, 500-ms debounce, 5-second
loading retry, 2.5-second preload timer, 81 exact-entry calls, and zero real
strict-interior ingress are pinned. Historical source and license remain
unavailable, so production ownership is zero. See
`docs/research/g2-teleprompt-page-data-recovery.md`.

The retained `imu_icm45608.c` object is now completely bounded at
`[0x004A35B0,0x004A6644)`: 53 linked functions / 11,674 body bytes plus 762
owned gap/pool bytes. Eleven retained anchors and 42 raw Thumb-restored entries
close the object. Its stored bus-read, bus-write, and FIFO callback entries,
20-slot `0x70` sample ring, vector/quaternion/event processing, raw-CSV capture,
two-minute automatic stop, 72 exact-entry calls, and zero external
strict-interior ingress are pinned. Historical source and license remain
unavailable, so production ownership is zero. See
`docs/research/g2-imu-icm45608-recovery.md`.

The public/canonical profile now retains the complete authenticated IMU object
byte-for-byte and removes the earlier clean-room/TDK source overlay. The stock
interval is 12,436 bytes with SHA-256 `d4946b…`; zero redirect bytes overlap it.
Twenty-nine authenticated relocations from 11 source-owned functions still
target 20 exact stock entries. The compiler and community bundle select none of
the five restricted-notice or ten dense EDMP-payload files, nor the retired
candidate/port. This preserves exact released behavior while making the
donor/source boundary explicit. Physical functional validation is deferred by
project direction.

The TinyFrame version boundary is now narrower than behavior-only comparison
allowed. Ten retained `TF_Error` `__LINE__` arguments select the exact
`TinyFrame.c`/`.h` blobs introduced by official commit `eb75483e`; repository
head `a29167a` retains the same two blobs and changes only demo content. The
reusable core source is therefore pinned to `eb75483e`, while the historical
checkout remains the honest two-commit interval `eb75483e…a29167a`. Release
2.3.0 and `44ecc068` are excluded from the minimum-patch core baseline. A
negative sweep of all 113 public upstream forks found no G2 magic/config
match. The exact upstream core, MIT license, G2 config, short-enum ABI,
`0x7158` pristine size, and `0x7160` magic-extended layout are now vendored and
verified offline. The bookended G2 boundary is now production source-owned;
only golden-packet hardware validation remains.
All 31 linked functions / 2,994 code bytes are now exactly spanned and hashed;
the intervening 124-byte pool is non-executable, and thirteen unused upstream
APIs are dead-stripped. This accounts for every byte in the 3,118-byte linked
translation unit. The routine at `0x00491838` is corrected to upstream-private
`renew_id_listener`, not `TF_DeInit`. See
`docs/research/tinyframe-send-version-recovery-audit.md` and
`docs/research/third-party-utility-gap-priority.md`.

The TinyFrame source-admission boundary is now executable and target-checked
without changing the authenticated upstream files. Stock has one dynamically
allocated instance in slot `0x200749C4`; role 1 selects master/peer bit 1 and
role 2 selects slave/peer bit 0. All application consumers treat the pointer as
opaque, permitting the adapter to return the pristine core
at allocation base `+4` inside the recovered `magic | core | magic` layout.
Host tests cover send/receive, listener and timeout callback pointer identity,
transport timeout 100, logger delivery, and bookend survival; Cortex-M55
static assertions close `0x7158`/`+4`/`+0x715C`/`0x7160`. A companion concrete
port candidate uses source-owned `heap_4` and retains the authenticated
first-party sync wrapper `[0x00541790,0x005417A4)`; exact target sections and
relocations are pinned. The stateless boundary removes the writable port table,
selects explicit no-op logging, and atomically production-routes all eight
stock-facing roots over the exact 14-function live graph. Apple and Linux
complete overlay/component/package roots and manifest ownership are pinned;
only hardware frames remain. See
`docs/research/tinyframe-source-admission-boundary-audit.md`.

The complete linked CMSIS-FreeRTOS wrapper object is now authenticated at
`[0x0044900E,0x00449ED2)`: 43 functions / 3,758 executable bytes plus 22
literal bytes account for all 3,780 physical bytes. The map separates 38
public APIs from five private helpers, closes 831 external BL callers and 41
internal calls, proves the sole stored entry is `TimerCallback`, and records
33 public APIs as dead-stripped. Three live version discriminators exclude
v10.4.6-era source, while the missing later thread-flags re-notification fix
excludes `bb8a350a` and descendants for that linked body. The maintained
baseline remains v10.5.1 commit `d213f261`; its exact `cmsis_os2.c` blob first
appeared at `13acfbef`. The new offline analyzer and six mutation/CLI tests
make this a source-admission boundary, not a production-ownership claim. See
`docs/research/cmsis-freertos-linked-function-census.md`.

The first four census-ranked CMSIS leaves are now production source-owned:
private `IRQ_Context`, `osKernelGetTickCount`, `osThreadGetId`, and
`osMessageQueueGetCapacity`. Their complete 88 stock bytes redirect atomically
to 84 Apache-2.0 source bytes plus four alignment bytes. The closure reuses the
already integrated scheduler, tick, and opaque current-task providers and the
authenticated Queue_t length offset, so it reads no TCB field and is unaffected
by the 112-byte vendor extension. Apple Clang 21 and Linux Clang 22.1.8 both
produce pinned complete overlays and packages. CMSIS production ownership is
now six public APIs plus one private helper; 32 public APIs and four private
helpers remain. See
`docs/research/cmsis-freertos-core-leaves-source-boundary-audit.md`.

The next two census-ranked leaves are also production source-owned:
`osSemaphoreGetCount` and `osMessageQueueGetCount`. Both stock entries are 36
bytes and compile from one selector-isolated Apache-2.0 adapter to identical
36-byte unrelocated target bodies. They reuse the source-owned IRQ helper and
normal/ISR queue-count providers, inspect no TCB field, and close seven
external calls. Apple and Linux complete-package pins pass. CMSIS production
ownership is now eight public APIs plus one private helper; 30 public APIs and
four private helpers remain. See
`docs/research/cmsis-freertos-count-leaves-source-boundary-audit.md`.

`osMessageQueueDelete` was the ninth source-owned public CMSIS wrapper. Its
complete 40-byte stock entry redirects to a 36-byte source body whose only
calls are the source-owned IRQ classifier and `vQueueDelete`; six external
callers are closed without reading Queue_t or TCB state. The next atomic
tranche promotes `osThreadYield`, `osKernelGetState`, `osMutexDelete`, and
`osTimerIsRunning`, all dependency-closed over already source-owned providers.
At that four-leaf milestone, CMSIS production ownership reached thirteen
public APIs plus private `IRQ_Context`; 25 public APIs and four private helpers
remained stock-backed.
Apple and Linux component and package replays are fail-closed. See
`docs/research/cmsis-freertos-message-queue-delete-source-boundary-audit.md`
and `docs/research/cmsis-freertos-thread-yield-source-candidate-audit.md`.
`osKernelGetState` calls the source-owned scheduler-state provider and reads
the authenticated CMSIS `KernelState` word at `0x20074384`; future source
admission of the wrapper-state writers remains a coupled review boundary.

The CMSIS mutex census also had one semantic label error: the linked 44-byte
entry at `0x0044986E` is `osMutexDelete`, not `osMutexGetOwner`. Its body
clears the recursive tag bit and calls `vQueueDelete`; the getter is the
dead-stripped API. The map, dead-strip ledger, family table, and analyzer are
corrected and all six mutation/CLI tests pass. A 38-byte production source
leaf now closes this wrapper over the same source-owned IRQ/delete providers.

`osTimerIsRunning` is the fourth dependency-closed candidate in this pass.
Its 26-byte target calls only source-owned IRQ classification and the already
production-integrated timer-active provider. ISR, null, inactive, and active
behavior is host-tested; production routing shares the aggregate-repin block.

The next synchronization tranche is also production source-owned:
`osMutexAcquire`, `osMutexRelease`, and `osSemaphoreRelease` replace 270 stock
bytes across 292 external callers with 220 source bytes plus two alignment
bytes. The earlier semaphore-take blocker was stale: its FreeRTOS V10.5.1
provider had already been promoted under the historical
`open_cfw_freertos_queue_semaphore_take_upstream_candidate` name. All six
unique fixed callees are source-owned, including the task/ISR give split and
PendSV request. Apple closes at `131980/3655376/4433870`; Linux closes at
`133848/3657244/4435738`. CMSIS production ownership is now sixteen public
APIs plus private `IRQ_Context`; 22 public APIs and four private helpers remain
stock-backed. See
`docs/research/cmsis-freertos-sync-ops-source-candidate-audit.md`.

The timer-operation tranche is now production source-owned as well:
`osTimerStart`, `osTimerStop`, and `osTimerDelete` replace 220 stock bytes
across 46 external callers with 234 source bytes plus four alignment bytes.
Their only fixed dependencies are the already source-owned IRQ,
timer-command/state/context, and heap-free providers. Apple closes at
`132218/3655614/4434108`; Linux closes at `134086/3657482/4435976`.
CMSIS production ownership is now nineteen public APIs plus private
`IRQ_Context`; 19 public APIs and four private helpers remain stock-backed.
See `docs/research/cmsis-freertos-timer-ops-source-candidate-audit.md`.

The complete event-flags quartet is production source-owned: constructor,
set, clear, and wait replace 388 stock bytes across 38 external callers with
334 source bytes plus four alignment bytes. All constructor, task/ISR event
group, and PendSV dependencies were already source-owned. Apple closes at
`132556/3655952/4434446`; Linux closes at `134424/3657820/4436314`.
CMSIS production ownership is now twenty-three public APIs plus private
`IRQ_Context`; 15 public APIs and four private helpers remain stock-backed.
See `docs/research/cmsis-freertos-event-flags-source-candidate-audit.md`.

`osTimerNew` and its private `TimerCallback` are now production source-owned as
one ABI unit. The 232-byte public stock entry has 12 callers; the adjacent
24-byte private callback is retained as inert authenticated evidence because
the source constructor stores only the source callback. The adapter preserves
the 44-byte `StaticTimer_t` threshold, 8-byte callback record, bit-zero dynamic
allocation tag, mixed static/dynamic record mode, and selective failure
cleanup. Apple closes at `132792/3656188/4434682`; exact-root Linux closes at
`134672/3658068/4436562`. CMSIS ownership is now 24 public APIs plus two
private helpers; 14 public APIs and three private memory-pool helpers remain.
See `docs/research/cmsis-freertos-timer-new-source-candidate-audit.md`.

`osMemoryPoolNew` is now production source-owned from the same authenticated
v10.5.1 source blob. Its complete 298-byte stock entry redirects to a 254-byte
Apple leaf (250 bytes under exact-root Linux), with all IRQ, heap_4, and static
counting-semaphore edges already source-owned. Tests preserve the recovered
116-byte control block, 32-bit allocation-size wrap, allocation flags, mixed
static/dynamic modes, and upstream v10.5.1 undersized-buffer quirks. Apple
closes at `133046/3656442/4434936`; exact-root Linux closes at
`134922/3658318/4436812`. CMSIS ownership is now 25 public APIs plus two
private helpers; 13 public APIs and three private pool helpers remain. See
`docs/research/cmsis-freertos-memory-pool-new-source-candidate-audit.md`.

The previously opaque FreeRTOS 112-byte TCB delta is now a verified minimal
source patch over authenticated V10.5.1. One 32-bit creation stack-depth word
is inserted after `pcTaskName[32]`, mirrored in `StaticTask_t`, and assigned by
`prvInitialiseNewTask`. The patch applies cleanly to pristine `tasks.c` and
`FreeRTOS.h`; a Cortex-M55 compile proves total size `0x70` and all later
trace, mutex, notification, and allocation offsets. Four stock functions and
six mutation/applicability/layout tests pin the boundary. The original vendor
identifier and private patch commit are unobservable, but no unexplained code
remains in this layout delta. See
`docs/research/freertos-g2-tcb-vendor-patch-audit.md`.

The FreeRTOS read-side ISR queue closure is now production source-owned from
Kernel V10.5.1 commit `def7d2df2b0506d3d249334974f51e427c17a41c`.
`xQueueReceiveFromISR` at `[0x00441DA6,0x00441E66)` and private
`prvCopyDataFromQueue` at `[0x00441F5E,0x00441F88)` redirect to authenticated
MIT adapters. Their queue-lock saturation, waiter wake, semaphore/null-buffer,
interrupt-mask, trace, and assertion paths are host-tested. This closes the
`xSemaphoreTakeFromISR` macro dependency used by CMSIS rather than inventing a
separate provider.

`osSemaphoreAcquire` and the complete memory-pool operation family are now
production source-owned from CMSIS-FreeRTOS v10.5.1 commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`. Public
`osMemoryPoolAlloc`/`osMemoryPoolFree` and private `CreateBlock`, `AllocBlock`,
and `FreeBlock` close every remaining private wrapper helper. The subsequent
FreeRTOS send and task-receive closures admit both `osMessageQueuePut` and
`osMessageQueueGet`; `osDelay` and its task-delay provider follow as the next
closed pair. Adding the priority-set pair and the complete
`eTaskGetState`/`prvDeleteTCB`/`vTaskDelete`/`osThreadTerminate` closure raises
CMSIS ownership to 33 of 38 linked public APIs and all five private helpers.
The following notification/thread-flags closure raises that to 35/38 while
preserving the stock pre-`bb8a350a` wait behavior; only kernel initialize,
kernel start, and thread creation remain. The Apple component is `3660486`
bytes / SHA-256
`9185ee131fcd2a40f6a3742cce0689b75a6c362e7a6f871ecf136f9125f99087`;
the package is `4438980` bytes / SHA-256
`807f1bec20e8b45e5469a0ca83ca2178ce1d2877f44fccfeb226f5adc7bad069`.
Package ownership is 137,783 source bytes, 98,034 generated bytes, and
4,203,163 opaque/cut-forward bytes. Two flash records remain unresolved;
none of this work signs, flashes, or operates hardware.

## CMSIS-FreeRTOS thread creation is production source-owned

The complete 200-byte `osThreadNew` stock entry now redirects to a strict
Apache-2.0 source leaf. Its behavior and provenance are pinned to
CMSIS-FreeRTOS v10.5.1 tag commit `d213f261`; the exact `cmsis_os2.c` blob was
first introduced by `13acfbef`. The wrapper retains authenticated FreeRTOS
V10.5.1 task creators and preserves the independently recovered `0x70` G2
static TCB threshold plus the 16-bit dynamic stack-depth cast. Seven hosted
tests cover validation, static/dynamic creation, malformed attributes,
defaults, failure, and truncation.

Apple now closes at overlay/component/package roots
`137260/3660656/4439150`; Linux closes at `139138/3662534/4441028`. Exact
canonical package ownership is 137,945 source, 98,242 generated, and
4,202,963 opaque bytes. CMSIS coverage is 36/38 public APIs and 5/5 private
helpers. Only writer-coupled `osKernelInitialize` and `osKernelStart` remain.

## CMSIS-FreeRTOS kernel lifecycle completes production wrapper ownership

The final writer-coupled `osKernelInitialize` and `osKernelStart` pair is now
source-owned. Both leaves share the authenticated CMSIS `KernelState` word at
`0x20074384` with the earlier get-state leaf, use source-owned IRQ and
scheduler-state providers, and preserve the write-to-running operation before
calling retained `vTaskStartScheduler`. The stock `SVC_Setup` is exactly the
two-byte no-op `bx lr`; no invented provider is needed.

Apple now closes at overlay/component/package roots
`137368/3660764/4439258`; Linux closes at `139248/3662644/4441138`.
Canonical package ownership is 138,051 source, 98,388 generated, and
4,202,819 opaque bytes. CMSIS production coverage is complete at 38/38 public
APIs and 5/5 private helpers. Remaining FreeRTOS work starts below the CMSIS
wrapper boundary at scheduler-global and Apollo port seams. The retained
`vTaskStartScheduler` core is subsequently source-recreated and dual-profile
qualified; it remains production-excluded until those globals and port seams
can be admitted atomically.

## FreeRTOS scheduler-start core is source-qualified

The complete retained `[0x00454CEC,0x00454D7C)` scheduler-start algorithm is
now represented by a bounded MIT V10.5.1 adaptation. The eight focused tests
pin the sole CMSIS caller, all six stock outgoing calls, static idle memory
(`0x20071E30`, `0x2005F154`, depth `0x400`), four scheduler globals, success
and failure ordering, both target objects, and all 20 relocations. Apple emits
a 156-byte function; Linux emits 160 bytes. Production remains deliberately
unchanged pending atomic global binding and Apollo scheduler-port validation.

The following port tranche closes the exact V10.5.1 `xPortStartScheduler`
algorithm and the downstream Apollo timer setup as two more production-excluded
candidates. The port preserves both SHPR3 priority writes and the four stock
tail calls. Timer setup authenticates 32 counts/tick, 1,024 Hz, maximum
suppression `0x07FFFFFB`, IRQ 32, compare A, and configuration `0x103` against
AmbiqSuite 5.1.0. Both candidates pass Apple/Linux object and relocation gates;
the elapsed-tick ISR and tickless/power path remain.

Those final two bounded STIMER algorithms are now closed by subsequent
production-excluded candidates. The IRQ/vector candidate preserves the stock
wrap formula without `+1`, four volatile tick-rate reads, compare re-arm, and
PendSV aggregation. The tickless candidate closes abort, clamp, pre/post power
hooks, optional WFI, wake re-arm, and capped `vTaskStepTick`. Their 14 focused
tests pass on both compiler profiles. No bounded STIMER algorithm remains
opaque; real timing/sleep validation and atomic production admission remain.

## FreeRTOS context switching and G2 trace ring are source-qualified

The complete 206-byte `vTaskSwitchContext` stock body now has a separate
production-excluded V10.5.1 candidate. Nine focused tests pin both callers,
both outgoing calls, seven fixed global literals, all 13 false interior-word
candidates, the 20-byte list and 112-byte TCB seams, generic priority descent,
sentinel-skipping round robin, every stack-guard word, trace ordering/wrap,
and the assertion path. Apple and Linux emit 266-byte target functions with
only the expected stack-overflow-hook and interrupt-mask relocations.

This closes the bounded scheduler-selection and G2 external trace-ring
algorithms without changing production. Atomic kernel/port admission and
on-device preemption, stack-overflow, trace-concurrency, timer, and sleep
validation remain mandatory.

## FreeRTOS scheduler-start core is production-routed

The three scheduler entries are now admitted as one production closure. Stock
`vTaskStartScheduler`, `xPortStartScheduler`, and `vTaskSwitchContext` redirect
to four strict-relocation leaves: the three recovered V10.5.1/Apollo
algorithms plus a non-returning source fail-stop. This closes the prior
software admission gap without weakening the recovered G2 globals, idle-task
memory, trace-ring, priority, exception-priority, timer, first-task, or stack
guard contracts.

Apple Clang 21 reproduces overlay/component/package roots
`165412/3688808/4467302` and package SHA-256
`88e7242268d2a5472e4c96e740dff637214940b5aa88f043bac29500eeb63d3f`.
The recorded Linux Clang 22.1.8 profile reproduces
`145180/3668576/4447070` and package SHA-256
`be5c62a97b9d31f4df257615c28ce81d79ab186feadb68262f96ac5bc35a1c25`.
The platform ledger therefore moves this row to implemented-in-source while
tracking live preemption, exception return, overflow, trace concurrency, and
STIMER behavior as a separate hardware-dependent row. That row is blocked by
future-required authorized G2/probe evidence; it is not treated as validated.

## LVGL Ambiq subtree provenance and global ABI are closed

The eleven linked `src/draw/ambiq` translation units are no longer an opaque
vendor-source family. Retained paths and line diagnostics identify exact Git
subtree `1e774257495fa43177e04fc5c8a42a77c2d7d619` in AmbiqMicro/LVGL. The
preferred default-branch commit is `5be8e0ae5077aa3880aba8a322b1487d6bc73c07`;
replay `67fd93e268f86b2ce90d4f1b14b53e36bf49ddd0` has identical subtree bytes,
so the historical commit object is deliberately left two-way ambiguous. The
next commit `6770071c…` is excluded by vector-font/letter line numbers.

Ambiq commits `d4dcd26b…` and `925470dd…` introduce and wire `clear_cb` and
`copy_cb`. Stock proves three 32-byte handler tables and all 24 callback
assignments. Combining that 24-byte ABI addition with
`LV_DRAW_SW_COMPLEX=0`, custom allocation, span, built-in object IDs, and the
previously recovered feature set reproduces `lv_global_t==0x1EC` and every
stock field offset. Six new provenance/compile tests and the existing LVGL
suite pass locally. The old unexplained 12-byte ABI delta is closed; the next
section records the now-identified Nema dependency and narrower production
gates.

## NemaGFX/NemaVG and Ambiq GPU dependency identity are closed

The hardware renderer below the recovered Ambiq LVGL subtree is now pinned to
an exact reproducible public package. The independent AmbiqSuite 5.1.0
revision `release_sdk5p1p0-634f7c117b` and Ambiq's public repository share the
same 50-file, 3,913,845-byte `NemaGFX_SDK` tree
`e690768a6e7b4d6a8d526fc75e8278a2764deff3`. Commit `b853fded…` is the first
public commit with that complete tree; `c6f54a95…` first publishes the exact
Apollo5 Nema archive and `e3eec7f3…` first publishes the exact GPU-patch
archive/header.

Stock calls the sectored-circular command-list API and retains its new error
token, independently forcing the NemaGFX 1.4.12 floor. The package supplies
NemaGFX 1.4.12 and NemaVG 1.1.8. Exact source/caller correlation maps nine
Nema command/power entries plus out-of-line Ambiq gradient and dash-line patch
bodies. It also recovers `LV_USE_DRAW_AMBIQ=1`, `LV_USE_AMBIQ_VG=1`, a
102,400-byte command list split into 100 x 1,024-byte sectors, and retained-
context GPU wake. Eight new tests authenticate stock spans, version evidence,
the 11-export/6-required GPU-patch census, manifest mutation rejection, and
the complete external SDK tree including one-byte negative mutation.

The public archives retain GCC 13.2.1 Cortex-M55 DWARF, while stock has IAR
code generation. Production therefore remains fail-closed on the original
IAR/private-source boundary, clean-room-candidate admission, stock
bare-metal HAL candidate admission, atomic integration, and Apollo510 hardware
validation. The third-party family, versions, public artifact origins, and
reproduction commit are no longer opaque.

## All 11 Ambiq GPU-patch functions are source-qualified

The exact 51,902-byte `gpu_patch.a` retains full per-function DWARF and
function sections. All 11 exports / 4,232 section bytes now have
production-excluded, independently named clean-room candidates. The
accessor sections are 16, 24, and 28 bytes at original source lines 301, 313,
and 326. Private DWARF fixes the paint (`0xE0`), path (`0x88`), vbuf (`0x60`),
bbox (`0x50`), and paint-texture (`0x30`) layouts.

Eight focused accessor tests pass, including the non-LUT branch that writes a
null palette, exact untransformed AABB selection, all four vbuf fields,
Cortex-M55 layout assertions, and relocation-free target bodies. The optional
full-SDK analyzer now parses GNU ar/ELF32 itself and authenticates these exact
sections. Seven more tests qualify the 144-byte public dash-line section and
138-byte stock IAR body, exact float truncation, and all Nema effects. All six
GPU-patch calls required by the recovered Ambiq LVGL subtree are thus
behaviorally source-transparent. A further six-test glyph candidate closes
one-to-four-byte decoding and the public 36-byte font-record lookup. Six shadow
tests pin odd/even margins, unequal horizontal/vertical sample counts, width-one
behavior, exact 668-byte section evidence, and relocation-free target output.
An exact Cortex-M55 emulation oracle plus seven tests close G2's two-stop
gradient boundary, including implicit endpoints, descending fallback,
equal-stop infinities, endpoint overwrites, and the 1,416-byte public/stock
bodies. Additional trace suites close the A8 corner mask, two-pass L8/L4
conversion, VG radial-shadow state restoration, and all four bitmap-glyph
rendering paths. No GPU-patch export remains binary-only; atomic HAL
integration, production admission, and hardware validation remain.

The adjacent stock Nema HAL is now separately closed as 18 contiguous
functions / 614 bytes at `[0x00513F34,0x0051419A)`. The exact IRQ-28 vector,
`0x40090000` register base, 1,000 ms semaphore wait, 100-command ring, three
heap descriptors, alignment/cache policy, and all 83 direct call sites are
authenticated. Public Ambiq history first exposes the related register-facing
Zephyr port on the package lineage at `4e7d4276…`; its blob and the later
`b853fded…` package port are exact provenance oracles, not claims of stock
source identity. A focused candidate/test suite closes the behavior while
leaving atomic board integration and hardware validation fail-closed.

## G2 BLE central-role and RingLink policy are object-closed

The retained `platform\ble\app_ble_central.c` path is no longer an opaque
first-party frontier item. Its initial 24 path anchors expand to a complete
44-function / 14,288-body-byte object at
`[0x0049F828,0x004A35B0)` (15,752 physical bytes). Twenty pathless functions
are admitted by Ghidra, direct-call, stored-pointer, prior-G2, and recursive
Thumb evidence; six bodies missed by the baseline sweep have pinned return and
literal-pool boundaries. The object owns scan/RPA selection, application events
`0xAE` through `0xB4`, seven RingLink states, retry escalation, dominant-hand
switching, unpair cleanup, and scene reconnect.

This is G2-local policy over already admitted Cordio DM/ATT/WSF providers, not
a remaining third-party source family. The prior G2 decompilation supplies 21
stable names and topology only; current bytes and boundaries are independently
authenticated, and the private producing commit remains unavailable. The
first-party retained-path frontier is now 71 closed / 163 open, with 389 closed
path anchors and 200,822 complete-object body bytes. Production routing remains
disabled.

## G2 BLE connection-parameter policy is object-closed

The retained `platform\ble\app_connect_params.c` path now owns the complete
`[0x00476CBC,0x004787A4)` object: 14 functions / 6,336 body bytes and eight
pool/alignment regions / 552 bytes, for 6,888 physical bytes. Ten bodies carry
the path directly; four externally rooted state/scheduling helpers preserve the
prior-G2 order. Thirty-nine direct entries, three stored `_connectParamReq`
pointers, 345 body calls, four source-path cells, both adjacent boundaries, and
all retained names are pinned. The two raw decodes to strict function interiors
are proven second-halfword artifacts within four-byte `sdiv`/`udiv`
instructions.

This is G2-local fast/slow connection policy over Cordio DM/WSF and the G2
event loop, not an additional third-party source dependency. The prior corpus
authenticates 14 stable names and one older-only log formatter but cannot reveal
the private producing commit. The aggregate retained-path frontier is now 72
closed / 162 open, with 399 closed anchors, 207,158 complete-object body bytes,
and 226,000 known physical bytes. Production routing remains disabled.

## G2 BLE peripheral-role policy is object-closed

The retained `platform\ble\app_ble_peripheral.c` object is now complete at
`[0x0046DB04,0x0046F4A4)`: 31 functions / 5,888 body bytes and 18 pool or
alignment regions / 672 bytes, for 6,560 physical bytes. Nineteen functions do
not carry the path themselves; seven of those were missing from baseline
Ghidra and are now admitted through direct-call or stored-pointer roots with
pinned returns. The complete graph has 44 direct entry sites, eight stored
Thumb pointers, 374 linked-image body calls, no strict-interior decode, and no
unrecovered direct target inside the object.

The object owns advertising payload/version policy, MTU and security handling,
events `0xAD`/`0xB5`/`0xB6`/`0xB7`, unpair and automatic restart, plus command
and left/right role decisions. Its external Cordio seam terminates at the
already admitted AmbiqSuite 2.5.1 application framework commit
`de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f`; no additional opaque third-party
definition remains in this interval. The aggregate frontier is now 73 closed /
161 open, with 411 closed anchors, 213,046 complete-object body bytes, and
232,560 known physical bytes. Production routing remains disabled.

## G2 multipart transport protocol is object- and provider-closed

The retained
`platform\protocols\transport_protocol\transport_protocol.c` object is now
complete at `[0x004B892C,0x004B9A80)`: 13 functions / 4,134 body bytes plus
four literal/alignment regions / 302 bytes, for 4,436 physical bytes. The
310-byte `_rxNextPacketTimeout` body missed by baseline Ghidra is recovered
from its stored callback pointer and pinned return. The complete graph has 26
direct entry sites, two stored callbacks, 193 body calls, no strict-interior
decode, and no unrecovered direct target.

The dependency result is stronger than the earlier shorthand: this is a
separate G2 `0xAA` multipart protocol, not TinyFrame. Its only checksum target
is the already source-owned first-party CRC-16/CCITT-FALSE leaf at
`0x0049ACD4`, called three times. It has zero calls or stored pointers into the
authenticated TinyFrame object. Remaining upstream relationships terminate at
already admitted CMSIS-FreeRTOS v10.5.1 commit `d213f261…`, Packetcraft Cordio
WSF message definitions (exact from r19.02 `86372d84…`, selected oracle ceiling
r20.05c `3656312d…`), EasyLogger 2.2.99, and TLSF v3.1 behind G2 wrappers.
There is no opaque third-party definition inside the object.

The aggregate frontier is now 74 closed / 160 open, with 418 closed anchors,
217,180 complete-object body bytes, and 236,996 known physical bytes. See
`docs/research/g2-transport-protocol-recovery.md`. Production routing remains
disabled.

## G2 settings service is object- and provider-closed

The retained `platform\service\settings\service_settings.c` object is now
complete at `[0x0046B0EC,0x0046C73C)`: 31 functions / 5,146 body bytes plus
19 literal/alignment regions / 566 bytes, for 5,712 physical bytes. Eleven
functions missing from baseline Ghidra are recovered through recursive Thumb
decoding, direct ingress, and the stored battery callback. The closed graph has
117 direct entry sites, 340 in-image body calls, one stored Thumb pointer, no
strict-interior decode, and no unrecovered direct target. Two apparent
out-of-image calls are authenticated second-halfword artifacts inside `udiv`
and `mul` instructions.

The object owns settings/version synchronization, a 28-byte settings record
with CRC over 24 bytes, KV save checks, ALS Q10 persistence, brightness and
luminance conversion, auto-brightness, terminal mode, head-up control, and
battery status propagation. It embeds no third-party definition. Its upstream
edges terminate at exact CMSIS-FreeRTOS v10.5.1 commit `d213f261…`, EasyLogger
2.2.99-equivalent `cd93d9c…a596b264`, and the already known family-level IAR
DLIB boundary. The 13 IAR memory/string calls add no exact release or archive
discriminator, so EWARM 9.20+ / leading 9.60.2 remains the honest limit.

The aggregate retained-path frontier is now 75 closed / 159 open, with 431
closed anchors, 222,326 complete-object body bytes, and 242,708 known physical
bytes. See `docs/research/g2-service-settings-recovery.md`. Production routing
remains disabled.

## G2 tracepoint settings is object- and provider-closed

The retained `app\gui\tracepoint\tracepoint_setting.c` object is now complete
at `[0x005EDADC,0x005EF0B0)`: 21 functions / 5,100 body bytes plus eight
pool/alignment regions / 488 bytes, for 5,588 physical bytes. Four bodies
missing from baseline Ghidra are recursively recovered and complete delete-all,
BLE-command, and common-data dispatch. The graph has 42 direct entry sites,
294 body calls, one stored callback, no strict-interior decode, and no
unrecovered direct target.

The object owns `/log/tp`, `tp_%u.bin`, sorted left/right file inventory, and
protobuf heartbeat, file-list, delete-file, and delete-all policy. It embeds no
third-party definition. Its provider edges terminate at EasyLogger 2.2.99,
nanopb compatible with 0.4.7 through 0.4.9.1 (selected 0.4.9 commit
`98bf4db6…`), source-owned wrappers over littlefs v2.10.1 commit `0494ce71…`,
and the existing family-level IAR DLIB seam. Neither nanopb nor DLIB calls add
an exact stock-version discriminator.

The aggregate retained-path frontier is now 76 closed / 158 open, with 440
closed anchors, 227,426 complete-object body bytes, and 248,296 known physical
bytes. See `docs/research/g2-tracepoint-setting-recovery.md`. Production routing
remains disabled.

## G2 product RTOS hooks and Ambiq HAL lineage are closed

The retained `product\s200\app\config\rtos.c` object is complete at
`[0x0046D67C,0x0046D8A0)`: 13 functions / 512 body bytes and two pool/alignment
regions / 36 bytes, for 548 physical bytes. Its single path anchor expands to
the complete 32-slot task-vote policy plus pre-sleep, post-sleep, idle,
malloc-failed, and stack-overflow hooks. Nineteen direct entry sites, 24 body
calls, both adjacent boundaries, and the absence of stored/interior targets
are pinned.

This closure resolves a previously open vendor seam. The complete stock
`am_hal_sysctrl_sleep` provider contains two `WFI` operations. Official
Apollo510 HAL 5.0.0 commit `392042e3…` contains one, whereas 5.1.0 commit
`5efc0228…` contains the same two-stage internal-timer retry behavior as
stock. The embedded build time, `2025-04-28T13:29:15Z`, predates the public
5.1.0 import on 2025-08-14, so 5.1.0 is an exact source-lineage/replay result
but the actual private pre-release commit remains unavailable. The watchdog
restart source is compatible across both releases and supplies no independent
version discriminator.

The CMSIS current-task calls land on source-owned CMSIS-FreeRTOS v10.5.1
`osThreadGetId` at commit `d213f261…`; the IRQ primitive is already
source-owned; EasyLogger and IAR DLIB are known provider seams. No opaque
third-party definition remains in the object.

The aggregate retained-path frontier is now 77 closed / 157 open, with 441
closed anchors, 227,938 complete-object body bytes, and 248,844 known physical
bytes. See `docs/research/g2-product-rtos-recovery.md`. At that audit point,
production routing had not yet been enabled.

### Product RTOS software gap promoted to production source

The complete 13-entry product RTOS object is now implemented in
`components/apollo_main/core_overlay/product_rtos.c`. Thirteen authenticated
guarded redirects replace all 512 stock function bytes with 444 bytes of
Cortex-M55 code, 14 bytes of placement alignment, and 19 strict relocations;
the 36-byte literal/alignment pool remains official and pinned. Host execution
covers state initialization, null/duplicate/reactivated votes, 32-slot
exhaustion, exact interrupt-mask restoration, current-thread wrappers,
deep/normal sleep selection, all three watchdog feeds, and malloc/stack fatal
paths. All 13 selector-isolated leaves compile as C for Cortex-M55.

The canonical component is 3,855,544 bytes (SHA-256 `df6d3b4d...`), and the
unsigned EVENOTA package is 4,634,038 bytes (SHA-256 `3953d7a5...`). No image
was signed, flashed, or installed. Live Apollo510 sleep, watchdog, tickless,
reset, and fatal behavior is blocked by unavailable physical evidence; future qualification requires authorized
responsive hardware and trace evidence.

## G2 copied Goodix application-error utility is source-closed

The retained `utils\assert\util_error_check.c` object is complete at
`[0x00509B48,0x00509C1C)`: one 178-byte handler and 34 bytes of alignment and
literals, for 212 physical bytes. Its 103 external callers, eight provider
calls, single path pointer, adjacent boundaries, and absence of stored or
strict-interior entry targets are pinned.

The handler's out-of-line `[0x006C8E60,0x006C8FB8)` table has 43 exact Goodix
SDK rows / 344 bytes. The table strings, 512-byte automatic buffer, format
strings, and control flow select the byte-exact GR551x SDK 1.7.0
`app_error.c` blob `d5027735…`; SDK V1.00 has older wording and a 1,024-byte
buffer, while 2.0.1 and official 2.0.2 use 46 rows and a static buffer. The
selected `854c43e0…` commit is the earliest located public carrier, not an
official Goodix release or Even generating commit. The copied helper does not
prove that the Apollo image links a Goodix BLE stack.

The aggregate dependency ledger is corrected to 23 families / 22 selected
source commits or baselines, with no locally actionable bounded third-party
functional gap. The retained-path frontier is now 78 closed / 156 open, with
442 closed anchors, 228,116 complete-object body bytes, and 249,056 known
physical bytes. See
`docs/research/g2-util-error-check-goodix-recovery.md`. Production routing
remains disabled.

## G2 logger settings is recursively object- and provider-closed

The retained `app\gui\logger\logger_setting.c` path was not an 84-byte
micro-object. Its repeated path pointers and recursively recovered direct-call
roots close the full `[0x00458DF0,0x0045A558)` translation unit: eight
functions / 5,574 function-envelope bytes, including 5,466 reachable
instruction bytes and 108 embedded compiler-data bytes, plus 418 outer pool
bytes, for 5,992 physical bytes. Five functions were absent from baseline
Ghidra. The graph has nine direct entry sites, one stored callback, 346
reachable body calls, zero strict-interior BL decodes, and zero unrecovered
direct object targets.

The object owns BLE-log switch/level policy, a bounded 20-entry `/log`
inventory, single/all-file deletion, role-qualified `L:/log/` and `R:/log/`
validation, compressed-log filename simplification, nanopb command IDs
`0..2,4..6`, and peer events `0x0B/0x0C`. It embeds no third-party definition.
All 338 external calls terminate at admitted EasyLogger 2.2.99, nanopb
0.4.7–0.4.9.1, littlefs v2.10.1-backed wrappers, FreeRTOS V10.5.1, known IAR
DLIB primitives, and first-party routing seams. No dependency family or exact
version discriminator is added.

The retained-path frontier is now 79 closed / 155 open, with 443 closed
anchors, 233,690 complete-object body bytes, and 255,048 known physical bytes.
See `docs/research/g2-logger-setting-recovery.md`. Production routing remains
disabled.

## G2 UX system status is recursively object- and provider-closed

The retained `app\ux\ux_system\ux_system.c` path expands from one 88-byte
baseline anchor to a complete eleven-function object at
`[0x0047CE90,0x0047D9C4)`: 2,668 reachable instruction/body bytes and one
200-byte compiler pool, for 2,868 physical bytes. The recovered 2,232-byte
`UX_LocalSystemStatusSyncHandler` is rooted by the sole stored callback. The
graph has 51 exact-entry BL sites, 163 body calls, zero strict-interior BL
decodes, and zero unrecovered object targets.

The object owns six status messages and a packed state byte for self/peer OTA,
BLE, ring, and ring-MAC state. It embeds no third-party definition. Its 95
third-party calls are diagnostics into the admitted EasyLogger 2.2.99 source-
equivalent core at selected commit `a596b264…`; all other external calls are
bounded first-party providers. No family or version discriminator is added.

The retained-path frontier is now 80 closed / 154 open, with 444 closed
anchors, 236,358 complete-object body bytes, and 257,916 known physical bytes.
See `docs/research/g2-ux-system-recovery.md`. Production routing remains
disabled.

## G2 health mutex and common-event policy is object-closed

The retained `app\gui\health\health.c` path expands from one 94-byte baseline
anchor to four functions at `[0x004FFBD8,0x004FFE14)`: 504 reachable body bytes
plus a 68-byte terminal pool, for 572 physical bytes. Two baseline-missed
functions recover the lazy mutex initializer and stored
`Health_common_data_handler`. The graph has 58 exact-entry BL sites, one
stored callback, 34 body calls, and no interior or unrecovered target.

The mutex operations land exactly on the production-source-owned
CMSIS-FreeRTOS v10.5.1 `osMutexNew`, `osMutexAcquire`, and `osMutexRelease`
wrappers at commit `d213f261…`. EasyLogger accounts for 25 diagnostics; health
protobuf, role/display, and service-send behavior remains bounded first-party
policy. No third-party definition or new version discriminator is present.

The retained-path frontier is now 81 closed / 153 open, with 445 closed
anchors, 236,862 complete-object body bytes, and 258,488 known physical bytes.
See `docs/research/g2-health-recovery.md`. Production routing remains disabled.

## G2 quicklist mutex and common-event policy is object-closed

The neighboring `app\gui\quicklist\quicklist.c` path expands from one 94-byte
anchor to four functions / 310 body bytes plus a 50-byte pool, for 360 physical
bytes. Its recovered initializer and stored common-event callback complete 25
exact-entry BL sites, 22 body calls, and the no-interior/no-unknown closure.

The three mutex calls land on production-source-owned CMSIS-FreeRTOS v10.5.1
commit `d213f261…`; diagnostics land on admitted EasyLogger, and event parsing
stops at bounded first-party quicklist providers over admitted nanopb. No
third-party body or new version discriminator is present.

The retained-path frontier is now 82 closed / 152 open, with 446 closed
anchors, 237,172 complete-object body bytes, and 258,848 known physical bytes.
See `docs/research/g2-quicklist-recovery.md`. Production routing remains
disabled.

## G2 dashboard watchface manager is object- and provider-closed

The retained `app\gui\dashboard\dashboard_watchface_manager.c` path expands
from one 98-byte anchor to a complete 17-function object at
`[0x00500410,0x00500824)`: 956 reachable body bytes and an 88-byte terminal
pool, for 1,044 physical bytes. Eight functions missed by baseline Ghidra,
24 exact-entry BL sites, 34 direct calls, 15 register-indirect calls, one
stored selector pointer, and the adjacent boundaries are fail-closed.

Four 15-word operation tables implement watchface kinds 1 through 4 with
15, 15, 11, and nine non-null Thumb targets. Every indirect call therefore
terminates in pinned first-party watchface code. Thirty direct calls reach the
admitted EasyLogger 2.2.99-equivalent commit `a596b264…`; the only other
external direct call is a bounded first-party dashboard-state getter. No
third-party definition, CMSIS-FreeRTOS call, dependency family, or new version
discriminator is present.

The retained-path frontier is now 83 closed / 151 open, with 447 closed
anchors, 238,128 complete-object body bytes, and 259,892 known physical bytes.
See `docs/research/g2-dashboard-watchface-manager-recovery.md`. Production
routing remains disabled.

## G2 EvenAI text-stream service is recursively object-closed

The retained `app\gui\EvenAI\text_stream_service.c` path expands from one
116-byte capacity helper to `[0x00552B30,0x005537CC)`: 26 functions / 3,188
reachable body bytes plus three pools / 40 bytes, for 3,228 physical bytes.
Eighteen functions missed by baseline Ghidra include the 340-byte
`animate_text` timer callback, whose Thumb address is formed PC-relatively at
`0x00552FD0`. Sixty-five direct entry sites, 144 direct calls, seven indirect
caller-callback sites, and all adjacent boundaries are fail-closed.

The 48-byte service owns two initially 512-byte growable UTF-8 buffers and
emits one complete 1-, 2-, 3-, or 4-byte code point per 100-tick timer period.
All 113 external direct calls terminate at admitted CMSIS-FreeRTOS v10.5.1,
LVGL 9.3-compatible, nanopb, TLSF-wrapper, EasyLogger, IAR DLIB, or bounded
first-party generic-animation seams. No dependency family, hidden utility
body, or new exact-version discriminator is present.

The retained-path frontier is now 84 closed / 150 open, with 448 closed
anchors, 241,316 complete-object body bytes, and 263,120 known physical bytes.
See `docs/research/g2-text-stream-service-recovery.md`. Production routing
remains disabled.

## G2 terminal core is object- and provider-closed

The retained `app\gui\terminal\terminal.c` path expands from one 122-byte
display-request anchor to `[0x005E42EC,0x005E47CC)`: nine functions / 1,144
body bytes plus a 104-byte pool, for 1,248 physical bytes. Eight baseline-
missed functions recover the action mutex, display exit path, command
dispatcher, and three stored callbacks. The graph has 68 exact-entry BL sites,
73 body calls, no indirect body call, and no interior or unknown direct target.

The object role-gates eight-byte message `0x30`, normalizes six input event
IDs, and dispatches 13 terminal command IDs. Its utility edges are 30 admitted
EasyLogger calls, the exact CMSIS-FreeRTOS v10.5.1 mutex trio at `d213f261…`,
and three bounded IAR memory calls. The other 29 calls are first-party terminal
protobuf/UI providers. No hidden utility body, dependency family, or new
version discriminator is present.

The retained-path frontier is now 85 closed / 149 open, with 449 closed
anchors, 242,460 complete-object body bytes, and 264,368 known physical bytes.
See `docs/research/g2-terminal-core-recovery.md`. Production routing remains
disabled.

## G2 RTC driver utility/HAL provenance is exact and production-routed

The retained `driver\rtc\drv_rtc.c` path closes the complete 130-byte
`DRV_RtcSetTime` body and its 22-byte diagnostic pool, for 152 physical bytes.
The sole exterior caller, all 56 instructions, seven direct calls, adjacent
RTC initializer/getter boundaries, and absence of stored or interior entries
are pinned.

The two functional providers are exact AmbiqSuite sources:
`am_util_time_computeDayofWeek` from `utils/am_util_time.c` and
`am_hal_rtc_time_set` from the Apollo510 RTC HAL. The selected source replay is
SDK 5.1.0 revision `release_sdk5p1p0-366b80e084` at public commit
`5efc022…`; exact 5.0.0 and 5.1.0 source sizes, SHA-256 values, and Git blobs
are recorded. Their executable logic is unchanged across those releases, so
the separate two-WFI sleep proof remains the 5.1.0 discriminator.

OpenCFW already production-routes the stock wrapper to
`open_cfw_rtc_time_set`, whose source and existing host tests preserve the
calendar predicate, validation, BCD packing, RTC MMIO order, diagnostics, and
return convention. Remaining risk is Apollo510 hardware validation, not opaque
third-party functionality.

The retained-path frontier is now 86 closed / 148 open, with 450 closed
anchors, 242,590 complete-object body bytes, and 264,520 known physical bytes.
See `docs/research/g2-drv-rtc-recovery.md`.

## G2 teleprompt file-list storage is object-closed

The retained `app\gui\teleprompt\teleprompt_file_list.c` path expands from one
144-byte update anchor to three functions / 166 body bytes plus a 34-byte pool,
for 200 physical bytes. The two baseline-missed helpers return and zero the
global record. Six exterior entry sites, twelve body calls, both adjacent
retained-path boundaries, and the absence of stored or interior targets are
pinned.

The object owns one `0xF52`-byte record at `0x201093D4`: update copies the
complete record after a null guard, get returns the live address, and reset
zeros it. Its only providers are ten admitted EasyLogger calls and bounded IAR
`memcpy`/`memset`. No direct nanopb definition, dependency family, or version
discriminator appears. The object is not production-routed.

The retained-path frontier is now 87 closed / 147 open, with 451 closed
anchors, 242,756 complete-object body bytes, and 264,720 known physical bytes.
See `docs/research/g2-teleprompt-file-list-recovery.md`.

## G2 EvenAI tick timers are object-closed

The retained `app\gui\EvenAI\even_ai_timer.c` path expands from two anchors /
152 bytes to thirteen functions / 856 body bytes plus a 100-byte pool, for 956
physical bytes. Ten additional source-order bodies recover the common and
heartbeat start/check/process helpers and three aggregate wrappers. Twenty-eight
BL entries, all 57 body calls, both adjacent object boundaries, and the absence
of indirect/stored/interior targets are pinned.

Both timers are private 12-byte deadline records over wrap-safe unsigned tick
subtraction. They do not use CMSIS or FreeRTOS software timers. The only RTOS
dependency is four exact, already source-owned CMSIS-FreeRTOS v10.5.1
`osKernelGetTickCount` calls at commit `d213f261…`; 30 calls reach admitted
EasyLogger and one reaches bounded IAR `memset`. The remaining ten calls are
first-party role, sync, and EvenAI service policy. No opaque third-party code
or new commit discriminator remains, and the object is not production-routed.

The retained-path frontier is now 88 closed / 146 open, with 453 closed
anchors, 243,612 complete-object body bytes, and 265,676 known physical bytes.
See `docs/research/g2-even-ai-timer-recovery.md`.

## G2 BLE-status callback facade is object-closed

The retained `platform\service\callback_mgr\cb_ble_status.c` path closes as
three functions / 168 body bytes plus a 34-byte pool, for 202 physical bytes.
The two exact diagnostic-named register/unregister anchors are followed by a
pathless 14-byte notification dispatcher. Ten exterior BL entries, all 13
body calls, both adjacent boundaries, and the absence of indirect, stored, or
strict-interior targets are pinned.

Ten calls reach admitted EasyLogger and three reach first-party generic
callback-manager register, unregister, and invoke providers over the
`BLE_STATUS` list at `0x20073F6C`. There is no CMSIS-FreeRTOS, Cordio, IAR,
allocator, or protobuf edge, no embedded upstream body, and no new version
discriminator. The object is not production-routed.

The retained-path frontier is now 89 closed / 145 open, with 455 closed
anchors, 243,780 complete-object body bytes, and 265,878 known physical bytes.
See `docs/research/g2-cb-ble-status-recovery.md`.

## G2 Conversate menu page is object-closed

The single 218-byte `conversate_ui_menu_page.c` anchor expands to eight
functions / 1,492 body bytes plus a 100-byte pool, for 1,592 physical bytes.
Six baseline-missed source-order functions restore page creation, BLE/focus/UI
callbacks, styling, and scroll policy. Five stored callback pointers, seven BL
entries, 102 calls, and both boundaries are pinned.

The 101 external calls resolve to 35 admitted EasyLogger calls, 34 LVGL
9.3-compatible calls at selected commit `344c7c3…`, and 32 first-party
Conversate/animation/page providers. No opaque third-party definition or new
version discriminator remains. The object is not production-routed.

The retained-path frontier is now 90 closed / 144 open, with 456 closed
anchors, 245,272 complete-object body bytes, and 267,470 known physical bytes.
See `docs/research/g2-conversate-ui-menu-page-recovery.md`.

## G2 legal/regulatory UI is object-closed

The 234-byte event handler and 194-byte regional legal-content pool close at
428 physical bytes. Multi-entry compiler-shared diagnostic tails are pinned,
and the immediately following function is proven to belong to the separately
audited EasyLogger async sink. Ten EasyLogger, one LVGL, two IAR, and two
first-party calls exhaust the provider graph; no opaque third-party body or
new version discriminator remains.

The retained-path frontier is now 91 closed / 143 open, with 457 closed
anchors, 245,506 complete-object body bytes, and 267,898 known physical bytes.
See `docs/research/g2-legal-regulatory-recovery.md`.

## G2 Conversate tag page is object-closed

The single 238-byte `conversate_ui_tag_page.c` path anchor expands to eleven
functions / 2,910 body bytes plus a 146-byte pool, for 3,056 physical bytes.
Eleven stored callback pointers, three BL entries, one alternate interior
entry, 204 body calls, both neighboring boundaries, and zero indirect calls
are pinned directly against the authenticated stock image.

The 202 external calls resolve to 40 admitted EasyLogger diagnostics, 113 LVGL
9.3-compatible UI calls at selected commit `344c7c3…`, two exact
CMSIS-FreeRTOS v10.5.1 tick calls at selected commit `d213f26…`, four bounded
IAR DLIB clear/copy calls, and 43 first-party Conversate/UI providers. No
opaque third-party definition or new version discriminator remains. The
object is not production-routed.

The retained-path frontier is now 92 closed / 142 open, with 458 closed
anchors, 248,416 complete-object body bytes, and 270,954 known physical bytes.
See `docs/research/g2-conversate-ui-tag-page-recovery.md`.

## G2 exit prompt is object-closed

The two retained `exit_prompt.c` anchors / 276 bytes expand to five functions /
782 body bytes plus a 118-byte pool, for 900 physical bytes. Three missed
source-order callbacks restore the hold, fade-start, and show sequence.
Seventeen BL entries, three stored callback pointers, 56 calls, both adjacent
boundaries, and zero indirect or strict-interior targets are pinned.

The 53 external calls resolve to 35 admitted EasyLogger diagnostics, 15 LVGL
9.3-compatible animation/object calls at selected commit `344c7c3…`, and
three first-party `fade_anim.c` calls. No opaque utility definition or new
version discriminator remains. The object is not production-routed.

The retained-path frontier is now 93 closed / 141 open, with 460 closed
anchors, 249,198 complete-object body bytes, and 271,854 known physical bytes.
See `docs/research/g2-exit-prompt-recovery.md`.

## G2 eAT core is object-closed

The two path-anchored `at_core.c` bodies / 302 bytes expand to five functions /
666 body bytes plus a 58-byte pool, for 724 physical bytes. The closure pins
85 direct entries, 21 direct calls, four exact indirect callback sites, both
boundaries, and no stored or strict-interior entries.

The 20 external calls resolve to 10 admitted EasyLogger diagnostics, six
bounded/source-owned IAR DLIB memory/string/format calls, and four private eAT
parser calls. Exact `AT_CoreInit` / `AT_Handler` searches found no indexed
public implementation, so no third-party origin/version/commit is claimed.
The object is not production-routed.

The retained-path frontier is now 94 closed / 140 open, with 462 closed
anchors, 249,864 complete-object body bytes, and 272,578 known physical bytes.
See `docs/research/g2-at-core-recovery.md`.

## G2 HAL I2C is object-closed

The single 308-byte `hal_i2c.c` anchor expands to nine functions / 1,584 body
bytes plus a 40-byte pool, for 1,624 physical bytes. Thirty-five BL entries,
the exact vector-table ISR pointer, 65 body calls, both boundaries, and zero
indirect or strict-interior BL targets are pinned.

Twenty-one calls map to the Apollo510 GPIO/IOM API family in AmbiqSuite 5.1.0
public replay commit `5efc0228…`; 15 reach exact source-owned CMSIS-FreeRTOS
wrappers, and the rest stop at admitted EasyLogger/nanopb/IAR or first-party
delay seams. Hardware validation and production routing remain.

The retained-path frontier is now 95 closed / 139 open, with 463 closed
anchors, 251,448 complete-object body bytes, and 274,202 known physical bytes.
See `docs/research/g2-hal-i2c-recovery.md`.

## G2 ring-battery service is object-closed

The two path-anchored `service_ring_battery.c` bodies / 306 bytes expand to
five functions / 352 body bytes plus a 44-byte pool, for 396 physical bytes.
Nine direct entries, 19 body calls, three path-pointer references, both object
boundaries, and zero stored, indirect, or strict-interior entries are pinned.

Fifteen calls reach admitted EasyLogger, two reach bounded IAR `memset`, and
two reach private first-party service-record transport. Exact public searches
for the two retained `SVC_RingBattery_*` symbols and source path returned no
source. No opaque third-party definition or new version discriminator remains.

The retained-path frontier is now 96 closed / 138 open, with 465 closed
anchors, 251,800 complete-object body bytes, and 274,598 known physical bytes.
See `docs/research/g2-service-ring-battery-recovery.md`.

## G2 OPT3007 register map is object- and specification-closed

The single exact-symbol `ti_opt3007_assignRegistermap` body is 340 bytes plus
a 20-byte pointer pool, for 360 physical bytes. Two entries, five EasyLogger
calls, both boundaries, and the absence of stored, indirect, or strict-interior
entries are pinned.

The analyzer reconstructs all 57 output bytes from the stock instruction
stream. They form 19 register-field triples that exactly match TI's official
SBOS864 OPT3007 register map, including manufacturer/device ID registers
`0x7E` and `0x7F`. Exact public implementation searches found no source, so
the data origin is TI's August 2017 specification while the code remains
private G2 construction; no source commit is applicable.

The retained-path frontier is now 97 closed / 137 open, with 466 closed
anchors, 252,140 complete-object body bytes, and 274,958 known physical bytes.
See `docs/research/g2-opt3007-registers-recovery.md`.

The exact register map is now production-routed as one clean-room 224-byte
scalar Cortex-M55 leaf with zero relocations. It replaces all 340 callable
stock bytes while retaining the 20-byte official pool. Exact-output,
null-safety, strict compile, component, package, and flash-plan gates pass.
Live OPT3007 bus validation is blocked by unavailable physical evidence; future qualification requires authorized
responsive G2 hardware; the wider ALS driver is still a software gap.

## G2 codec UART-porting seam is object-closed

The two exact-symbol `uart_init` / `uart_close` bodies total 342 bytes plus a
72-byte pointer pool, for 414 physical bytes. Seven entries, 24 calls, four
path references, both boundaries, and zero stored, indirect, or strict-interior
targets are pinned.

Twenty calls reach admitted EasyLogger and three reach first-party UART3
lifecycle/callback service. The remaining call is the exact
production-source-owned AndersKaloer `ring_buffer_init`; it remains compatible
from `cda00e1…` through selected `190e30b…` and adds no narrower discriminator.
No opaque codec-vendor implementation occurs in this porting object.

The retained-path frontier is now 98 closed / 136 open, with 468 closed
anchors, 252,482 complete-object body bytes, and 275,372 known physical bytes.
See `docs/research/g2-service-codec-porting-recovery.md`.

## G2 notification thread is object-closed

Three path anchors / 374 bytes expand to eleven functions / 702 body bytes and
114 bytes in two pools, for 816 physical bytes. Two restored bodies are the
stored thread entry and packed creation callback. Nine BL entries, two stored
pointers, 56 calls, six path references, both boundaries, and zero indirect or
strict-interior targets are pinned.

Seven calls land on exact, production-source-owned CMSIS-FreeRTOS v10.5.1
thread, flags, delay, and queue wrappers at `d213f261…`. Thirty calls reach
admitted EasyLogger and eleven reach first-party state/record/whitelist policy.
No opaque utility body or new version discriminator remains.

The retained-path frontier is now 99 closed / 135 open, with 471 closed
anchors, 253,184 complete-object body bytes, and 276,188 known physical bytes.
See `docs/research/g2-thread-notification-recovery.md`.

## G2 GX8002B host driver is object- and provider-closed

Three path anchors / 424 bytes expand to twelve functions / 1,028 body bytes
plus a 144-byte pool, for 1,172 physical bytes. Three restored bodies are
CMSIS-Core NVIC helpers; the closure also recovers the stored I2S ISR, both I2S
lifecycle functions, the DMA-buffer/timestamp helper, and a stored audio-thread
callback. Eighteen BL entries, two stored pointers, 79 calls, nine raw path
references, both boundaries, and zero indirect or strict-interior targets are
pinned.

Thirteen calls map to twelve Apollo510 I2S APIs in AmbiqSuite 5.1.0 source file
`am_hal_i2s.c`, revision `release_sdk5p1p0-366b80e084`, at public replay
commit `5efc0228…`. The source is equivalent but the later public import cannot
be the historical private generating commit. NationalChip's GX8002B/LVP SDK is
an external device dependency and contributes no linked code to this object.
Four calls reach exact CMSIS-FreeRTOS `osDelay`, 45 reach admitted EasyLogger,
and 12 reach first-party board/audio providers.

All twelve routines are now production-routed from clean-room C. The
selector-isolated Cortex-M55 build emits 608 Thumb text bytes plus eight
alignment bytes with 34 strict relocations. Twelve guarded redirects replace
all 1,028 callable stock bytes and retain only the 144-byte unreachable
diagnostic/literal pool as official data. Host oracles cover the complete NVIC,
ISR, power, I2S lifecycle, RX-buffer/cache, callback, and reboot behavior.

The canonical overlay/component/package sizes are 240,692 / 3,764,088 /
4,542,582 bytes; the 2,588,615-byte flash plan has 3,715 placed, two unresolved,
five container-only, and six protected regions. Live GX8002B rail, I2S, DMA,
interrupt, and reboot evidence is blocked by unavailable physical evidence; future qualification requires authorized responsive hardware. Wider firmware completeness is not claimed.

The retained-path frontier is now 100 closed / 134 open, with 474 closed
anchors, 254,212 complete-object body bytes, and 277,360 known physical bytes.
See `docs/research/g2-drv-gx8002b-recovery.md`.

## G2 FlashDB service adapter is object- and provider-closed

Five path anchors / 462 bytes expand to eleven functions / 908 body bytes plus
a 132-byte pool, for 1,040 physical bytes. Two missed Ghidra functions and
four additional unanchored object members restore all four FAL callbacks,
three mutex functions, both blob wrappers, the database accessor, and service
initialization. Twenty-three BL entries, six stored callback pointers, 60
calls, nine raw path references, both boundaries, and zero indirect or
strict-interior targets are pinned.

Two calls map exactly to FlashDB 2.1.1 `fdb_kv_get_blob` and
`fdb_kv_set_blob` at authenticated source baseline `714d6159…`; seven calls
reach exact CMSIS-FreeRTOS v10.5.1 tick/mutex wrappers at `d213f261…`, and 45
reach admitted EasyLogger. The object embeds no third-party definition and
adds no historical-commit discriminator. It does prove a first-party safety
seam: stock FAL callbacks return zero on device failure while FlashDB maps only
negative callback results to errors. A writable OpenCFW port must use negative
error mapping and remain gated on golden-flash and non-destructive mount
validation.

The retained-path frontier is now 101 closed / 133 open, with 479 closed
anchors, 255,120 complete-object body bytes, and 278,400 known physical bytes.
See `docs/research/g2-service-db-api-recovery.md`.

## G2 EvenAI UI is object- and provider-closed

Two path anchors / 346 bytes expand to 43 functions / 8,004 function-interval
bytes / 8,424 physical bytes. The object includes 8,000 decoded instruction
bytes, 420 bytes in 15 outer pools, and one four-byte inline literal. Twenty-
eight missed functions restore text-stream lifecycle, scroll/layout caching,
dialog construction, input forwarding, automatic refresh, and page lifecycle.
The closure pins 131 BL entries, one stored callback, 512 calls, 21 path
references, every pool, both boundaries, and no strict-interior ingress.

All 413 external calls close over 182 admitted LVGL 9.3-compatible calls at
selected ceiling `344c7c31…`, 105 EasyLogger diagnostics, 22 bounded IAR DLIB
memory/string calls, one exact CMSIS-FreeRTOS v10.5.1 tick call, and 103
first-party EvenAI/UI providers. The audit composes the already closed
text-stream and timer objects. No third-party implementation or new version
discriminator is embedded; remaining work is first-party reconstruction and
target UI/lifecycle validation.

The retained-path frontier is now 102 closed / 132 open, with 481 closed
anchors, 263,124 complete-object body bytes, and 286,824 known physical bytes.
See `docs/research/g2-ui-even-ai-recovery.md`.

## G2 time service is object- and provider-closed

Two retained-path anchors / 438 bytes expand to eleven primary functions /
1,308 body bytes plus a 76-byte trailing pool, for 1,384 physical bytes. The
closure restores the missing leading epoch-to-calendar function and preserves
one externally called alternate compiler entry inside it without
double-counting the body. Sixty-four exact BL entry sites, six stored pointers,
45 direct body calls, both boundaries, and the retained path cell are pinned.

Eight external calls terminate at bounded IAR DLIB memory helpers and sixteen
at first-party RTC, configuration, transport, and logging providers. There are
no direct CMSIS-FreeRTOS calls and no embedded third-party definitions. The
object begins after the two alignment bytes following the already closed CMSIS
object, making the ownership boundary explicit rather than introducing a new
RTOS or utility gap.

The retained-path frontier is now 103 closed / 131 open, with 483 closed
anchors, 264,432 complete-object body bytes, and 288,208 known physical bytes.
See `docs/research/g2-service-time-recovery.md`.

## G2 audio thread is object- and provider-closed

Three retained-path anchors / 394 bytes expand to 31 functions / 2,954 body
bytes / 3,258 physical bytes. Nineteen restored functions recover thread and
resource initialization, queue dispatch, watchdog policy, codec/PDM handlers,
peer synchronization, and exit. The closure pins 1,101 instructions, 203
direct calls, 43 BL entries, three stored entries, 24 path references, all
pools and boundaries, and one bounded runtime callback dispatch.

Twenty calls terminate at fourteen exact CMSIS-FreeRTOS v10.5.1 wrappers from
`d213f261…`, with FreeRTOS-Kernel V10.5.1 `def7d2df…` and CMSIS_5 5.9.0
`2b7495b…` pinned as dependencies. One call is bounded IAR `memset`, 120 are
EasyLogger diagnostics, and nineteen compose the already closed codec DFU,
codec-host, and GX8002B objects. No third-party body or NationalChip LVP code
is embedded.

The retained-path frontier is now 104 closed / 130 open, with 486 closed
anchors, 267,386 complete-object body bytes, and 291,466 known physical bytes.
See `docs/research/g2-thread-audio-recovery.md`.

## G2 compact-log core is object- and provider-closed

Two retained-path anchors / 520 bytes expand to eight functions / 2,300
contiguous executable bytes. The closure restores the missing force-sync entry,
pins 898 instructions, 78 direct calls, 5,726 whole-image BL entries, six raw
path references, and zero indirect, stored-entry, or strict-interior ingress.
Twenty-three post-body literal cells are authenticated separately because
three EasyLogger accessors are interleaved between the body and its pool; no
physical-object byte total is overclaimed.

The high-volume entry at `0x0043CE9E` is now correctly classified as a
G2-private compact-record hook backed by a private 44-byte encoder, not as
upstream EasyLogger `elog_output`. The latter remains the separately admitted
G2-adapted body at `0x0043D574`, selected from EasyLogger commit `a596b264…`.
The core's external calls close over 13 bounded IAR DLIB calls, 30 EasyLogger
control/output calls, 14 FreeRTOS kernel/port calls, two exact CMSIS-FreeRTOS
tick calls, and eight first-party providers. It embeds no third-party body and
adds no version discriminator.

The retained-path frontier is now 105 closed / 129 open, with 488 closed
anchors, 269,686 complete-object body bytes, and 291,466 known physical bytes.
See `docs/research/g2-compress-log-core-recovery.md`.

## G2 compact-log port is object- and provider-closed

Three retained-path anchors / 680 bytes expand to twelve functions / 1,324
body bytes plus 140 bytes of modes, alignment, and pool data, for 1,464
physical bytes. The closure restores the stored export-timeout callback and
pins 526 instructions, 68 calls, 23 direct BL entries, one stored odd Thumb
entry, all data regions, both boundaries, and zero strict-interior or indirect
ingress.

The port owns a five-file ring with 512,000-byte files, a 12-byte manager
record with magic `0x4C4D4752`, a fixed firmware-version header, and a
120,000-tick export timeout. All eighteen file-runtime calls already reach
production source-owned OpenCFW wrappers over littlefs v2.10.1-equivalent
commit `0494ce71…`; all three delayed-callback calls are production source-
owned too. The remaining reusable seam is two bounded IAR `snprintf` calls.
No third-party body or new version discriminator is embedded.

The retained-path frontier is now 106 closed / 128 open, with 491 closed
anchors, 271,010 complete-object body bytes, and 292,930 known physical bytes.
See `docs/research/g2-compress-log-port-recovery.md`.

## G2 shared file runtime is path-, provider-, and production-closed

Five retained-path anchors / 746 bytes expand to eighteen functions / 2,266
executable bytes plus 138 bytes of alignment, file-mode literals, and pool
data, for 2,404 physical bytes. The closure pins 864 instructions, 132 calls,
644 whole-image BL entries, three stored entries, nine path references, both
boundaries, and zero indirect or strict-interior ingress.

All eighteen file, directory, synchronized-heap, and initialization entries
already have exact OpenCFW production redirects. Their provider graph closes
over 36 exact CMSIS-FreeRTOS mutex calls, fourteen first-party adapters over
littlefs v2.10.1-equivalent commit `0494ce71…`, three exact production TLSF
calls at `deff9ab5…`, six bounded IAR string calls, and already closed logging,
errno, and assertion seams. No third-party definition or new version
discriminator is embedded.

The retained-path frontier is now 107 closed / 127 open, with 496 closed
anchors, 273,276 complete-object body bytes, and 295,334 known physical bytes.
See `docs/research/g2-file-runtime-recovery.md`.

## G2 compact audio estimator is object- and provider-closed

Two retained-path anchors / 656 bytes expand to ten functions / 1,712 body
bytes plus 136 bytes of literal-pool data, for 1,848 physical bytes. The
closure pins 574 instructions, 43 direct calls, fifteen whole-image BL entries,
all boundaries and path references, and zero indirect, stored-entry, or
strict-interior ingress.

The first-party estimator consumes 800 interleaved signed-16 stereo frames,
forms ten rolling energy windows, searches relative lags from -10 through +10,
and converts the result to a signed angle. Its provider graph closes over ten
bounded IAR calls (`memset`, `asin`, signed-64-to-double, and `sqrt`), six calls
to a source-owned 64-bit division helper, and fifteen known logging calls. No
NationalChip LVP or other DSP-library body is linked and no new third-party
version discriminator exists. Compatibility work must account for a stock
hazard: aligned non-null input sizes below 3,200 bytes can pass validation even
though the algorithm unconditionally reads the complete 3,200-byte block.

The retained-path frontier is now 108 closed / 126 open, with 498 closed
anchors, 274,988 complete-object body bytes, and 297,182 known physical bytes.
See `docs/research/g2-service-algo-recovery.md`.

## G2 UART synchronization object is path- and provider-closed

Two retained-path anchors / 688 bytes expand to five functions / 758 body
bytes plus 114 bytes of shared pool data, for 872 physical bytes. Three helpers
are restored through adjacency, pool ownership, two stored Thumb pointers, and
whole-image ingress. The closure pins 297 instructions, 63 direct calls, four
direct BL entries, one bounded indirect call, both stored entries, all path
references, and zero strict-interior ingress.

The object creates one mutex, one event-flags object, and a 24,576-byte receive
stream. Its worker explicitly handles receive, send, and TinyFrame-tick bits;
receive dispatch uses 1,024-byte chunks with a 32-iteration / `0x7FFF` byte
guard. Reusable edges terminate at exact CMSIS-FreeRTOS v10.5.1, TinyFrame
`eb75483e…a29167a`, EasyLogger `a596b264…`, bounded IAR, and the first-party
UART adapter over the AmbiqSuite SDK 5.1.0 compatibility baseline `5efc0228…`.
No third-party body or new version discriminator is embedded. One initializer
through RAM slot `0x20000658` remains a bounded first-party runtime seam.

The retained-path frontier is now 109 closed / 125 open, with 500 closed
anchors, 275,746 complete-object body bytes, and 298,054 known physical bytes.
See `docs/research/g2-uart-sync-recovery.md`.

## G2 factory NV service is object- and FlashDB-closed

Two retained-path anchors / 882 bytes expand to five functions / 930 body
bytes plus 122 alignment/pool bytes, for 1,052 physical bytes. The closure
restores the database-index-one read/write wrappers and nine-node default-table
descriptor, then pins 379 instructions, 60 calls, twenty BL entries, eight path
references, both boundaries, and zero indirect, stored, or interior ingress.

Four calls reach the authenticated FlashDB 2.1.1 core at commit `714d6159…`,
nine reach first-party database-object adapters, two reach bounded IAR memory /
string helpers, and two reach first-party serial-number policy. No third-party
body is embedded. The recovered binding is `factory@NVdb`, external-flash
offset `0x01FF8000`, length `0x8000`, with nine explicit-length defaults and
magic `nvMagic=0x55550022`. Missing or mismatched magic performs wholesale
`fdb_kv_set_default`. The stock FAL zero-on-driver-failure hazard and destructive
reset policy remain explicit gates pending a read-only golden capture.

The retained-path frontier is now 110 closed / 124 open, with 502 closed
anchors, 276,676 complete-object body bytes, and 299,106 known physical bytes.
See `docs/research/g2-service-nvdb-recovery.md`.

## G2 production microphone test is object- and provider-closed

Five retained-path anchors / 646 bytes expand to six functions / 898 body
bytes plus 102 alignment/pool bytes, for 1,000 physical bytes. The missing
252-byte `production_pcm_callback_stereo` is restored through its exact symbol
string, path reference, stored odd Thumb pointer, complete disassembly, shared
pool, and boundary. The closure pins 359 instructions, 64 calls, eight BL
entries, both callback pointers, and zero indirect or interior ingress.

The stereo and single callbacks use bounded 400-byte scratch buffers and either
forward PCM directly or perform first-party channel extraction before dispatch.
Codec mode zero and PDM mode one share listener `0x10B` but retain distinct
power/unregister/cleanup paths. The only reusable calls are five bounded IAR
memory helpers and 35 known logging calls; 24 other edges are first-party audio
providers. No direct CMSIS-FreeRTOS, NationalChip LVP, or other DSP body is
linked.

The retained-path frontier is now 111 closed / 123 open, with 507 closed
anchors, 277,574 complete-object body bytes, and 300,106 known physical bytes.
See `docs/research/g2-production-mic-recovery.md`.

## G2 audio manager is object- and provider-closed

Four retained-path anchors / 984 bytes expand to seven functions / 1,554 body
bytes plus 174 alignment/pool bytes, for 1,728 physical bytes. The complete
410-byte peer-message handler and 132-byte initializer missing from Ghidra are
restored through exact symbols, retained-path references, contiguous boundaries,
internal topology, and ingress. The closure pins 595 instructions, 112 calls,
38 BL entries, one stored callback pointer, and zero indirect or interior
ingress.

The object owns an eight-slot application table, role-two first-acquire and
last-release hardware transitions, and a four-message one-byte peer handshake
on common-data frame `0x010C`. Eighty calls reach admitted logging, one reaches
bounded IAR `memset`, and twenty reach first-party product-role, audio-power,
and transport providers. No CMSIS-FreeRTOS, DSP, or other third-party body is
embedded and no new version discriminator exists.

The retained-path frontier is now 112 closed / 122 open, with 511 closed
anchors, 279,128 complete-object body bytes, and 301,834 known physical bytes.
See `docs/research/g2-service-audio-manager-recovery.md`.

## G2 system KVDB is object-closed and resolves the boot counter

Two retained-path anchors / 1,256 bytes expand to seven functions / 1,384 body
bytes plus 156 alignment/pool bytes, for 1,540 physical bytes. Five non-anchor
helpers close the database-zero blob adapters, twelve-node descriptor,
migration dispatcher, and magic invalidator. The closure pins 550 instructions,
88 direct calls, 32 BL entries, one bounded indirect site with eleven exact
targets, and zero stored or interior ingress.

The object composes exact FlashDB 2.1.1 commit `714d6159…`, twelve calls to the
closed G2 database adapters, the closed onboarding record, and eleven separately
closed first-party migration functions. The reset-called IAR zero scatter
proves `kvbooCount@0x20074988` starts at zero; initialization reads, increments,
and persists it. That former FlashDB residual is retired. Golden media, schema,
non-destructive mount policy, and the stock zero-on-driver-failure hazard remain
explicit production gates. The clean-room lifecycle is now production-routed:
seven guarded redirects replace 1,384 callable stock bytes with 342 compiled
bytes plus eight alignment bytes and 23 exact relocations. Destructive magic
reset/invalidation is disabled; the host lifecycle oracle and canonical
4,541,570-byte package pass. Golden-media and live persistence/recovery are
blocked by unavailable physical evidence; future qualification requires authorized physical evidence.

The retained-path frontier is now 122 closed / 112 open, with 538 closed
anchors, 299,774 complete-object body bytes, and 324,134 known physical bytes.
See `docs/research/g2-service-kvdb-recovery.md`.

The next closed seam is `app\ux\ux_battery_sync\ux_battery_sync.c`: one
836-byte `UX_BatterySyncHandler` body plus its 84-byte literal pool. The stored
callback table binds it to record `0x105`; the handler validates twelve-byte
messages and dispatches IDs 1..6 across already closed charger/ring-battery
providers. Forty-five EasyLogger calls are its only third-party edge, with no
new source/version discriminator. See
`docs/research/g2-ux-battery-sync-recovery.md`.

Following that callback edge closes the formerly zero-anchor
`platform\service\callback_mgr\cb_ring_battery.c` record as five functions /
122 body bytes / 152 physical bytes. Four bodies were missed by Ghidra; the
facade owns callback list `0x20073F90` and has only admitted EasyLogger plus
first-party provider calls. See
`docs/research/g2-cb-ring-battery-recovery.md`.

The zero-anchor `cb_charge.c` and `cb_msg_notif.c` siblings are now closed as
parallel five-function / 224-physical-byte facades. Their `BAT_INFO` and
`MSG_COUNT` lists use the same first-party generic callback ABI and admitted
EasyLogger source, with no RTOS or new third-party body. See
`docs/research/g2-callback-facades-recovery.md`.

The generic `callback_manager.c` provider is closed as eight functions / 1,240
body bytes / 1,360 physical bytes. Its only dynamic call is bounded by nodes
created through registration; all direct utility edges terminate at admitted
EasyLogger or production-source-owned TLSF heap wrappers. See
`docs/research/g2-callback-manager-recovery.md`.

`app\gui\Silent_Mode\silent_mode.c` expands from four anchors / 622 bytes to
ten functions / 2,488 body bytes / 2,696 physical bytes. Its 70 LVGL, 70
EasyLogger, one exact `vTaskDelay`, and one bounded IAR `memset` calls expose no
new dependency lineage; three stored callbacks and common-data record `0x10A`
are pinned. See `docs/research/g2-silent-mode-recovery.md`.

`app\gui\onboarding\onboarding_data_manager.c` closes as seven functions / 826
body bytes plus a 106-byte owned pool, for `[0x0047E2D0,0x0047E674)`. The two
pathless helpers own the mutex-protected three-byte process record and deferred
flag-update/event policy. Its reusable graph terminates at admitted EasyLogger,
exact CMSIS-FreeRTOS mutex/event wrappers, bounded IAR `memset`, the closed
FlashDB-backed onboarding KVDB leaf, and the closed nanopb-backed onboarding
encoder. No new dependency body, version discriminator, or generating commit
is exposed. See `docs/research/g2-onboarding-data-manager-recovery.md`.

The adjacent `app\gui\onboarding\onboarding.c` controller expands from four
anchors / 2,518 bytes to twelve functions / 4,136 body bytes / 4,476 physical
bytes. Five pre-anchor helpers and three stored callbacks close recursive LVGL
color transforms, common-data dispatch, BLE disconnect/reconnect state, and UI
lifecycle. Its 165 EasyLogger, 32 LVGL, exact `osMutexNew`, and two bounded IAR
calls terminate in already selected sources; all other reusable paths reach
the closed onboarding/KVDB/protobuf/callback objects. See
`docs/research/g2-onboarding-controller-recovery.md`.

`ui_onboarding_main_page.c` expands from seven anchors / 3,648 bytes to 52
functions / 9,234 body bytes / 9,776 physical bytes. Fifteen source-order
helpers and 17 stored pointers close its UI graph. All 453 external calls are
accounted for by selected LVGL, EasyLogger, CMSIS-FreeRTOS, mpaland, bounded IAR
DLIB, the closed onboarding protobuf service, or first-party sibling-page
policy. See `docs/research/g2-onboarding-main-page-recovery.md`.

`ui_onboarding_stock_page.c` expands from ten anchors / 6,624 bytes to 17
functions / 7,500 body bytes / 7,864 physical bytes. Its complete 629-call
graph terminates at selected LVGL and EasyLogger sources, exact
CMSIS-FreeRTOS mutex wrappers, bounded IAR DLIB, or already bounded first-party
onboarding/UI seams. No embedded third-party definition or new version
discriminator remains. The retained-path frontier is now 123 closed / 111
open, with 548 closed anchors, 307,274 complete-object body bytes, and 331,998
known physical bytes. See
`docs/research/g2-onboarding-stock-page-recovery.md`.

The onboarding family now also closes `ui_onboarding_news_page.c`: nineteen
anchors expand to 35 functions / 9,346 body bytes / 10,640 physical bytes.
Two raw interior-looking BL patterns are proven overlapping decodes inside
four-byte `uxtab` instructions, leaving zero qualified interior ingress. All
470 external calls terminate at selected LVGL/EasyLogger, exact
CMSIS-FreeRTOS mutex wrappers, bounded IAR DLIB, the routed ARM EABI division
helper, the closed time service, or bounded first-party providers. The frontier
is now 124 closed / 110 open, with 567 closed anchors, 316,620 complete-object
body bytes, and 342,638 known physical bytes. See
`docs/research/g2-onboarding-news-page-recovery.md`.

`app\gui\common\lvgl_font_manager.c` is now closed as eight functions / 2,590
body bytes / 2,972 physical bytes. The object confirms the two exact LVGL
FreeType adapter entries over FreeType 2.9.1 commit `86bc8a950…`, with all
other edges reaching admitted EasyLogger, bounded IAR DLIB, the closed MSPI
lock pair, or production-routed TLSF-backed heap wrappers. The frontier is now
125 closed / 109 open, with 574 closed anchors, 319,210 complete-object body
bytes, and 345,610 known physical bytes. See
`docs/research/g2-lvgl-font-manager-recovery.md`.

`app\gui\EvenHub\common_list_container.c` expands from six anchors / 6,746
bytes to fourteen functions / 7,342 body bytes / 8,588 physical bytes. Its two
indirect selection calls are bounded through both constructor sites to the
single `0x004949C0` callback. All 419 direct external calls terminate at
selected EasyLogger/LVGL sources, bounded IAR DLIB, production-routed
TLSF-backed heap wrappers, or bounded first-party providers. The frontier is
now 126 closed / 108 open, with 580 closed anchors, 326,552 complete-object
body bytes, and 354,198 known physical bytes. See
`docs/research/g2-common-list-container-recovery.md`.

`app\gui\EvenHub\common_text_container.c` expands from nine Ghidra anchors /
4,648 bytes to thirteen functions / 6,966 body bytes / 7,740 physical bytes.
Three missed functions restore 2,318 body bytes and two additional retained-
path anchors. All four indirect navigation calls resolve through both
constructor sites to the single `0x00494A78` `evenhub_ui.c` callback. All 426
direct external calls terminate at selected EasyLogger/LVGL sources, bounded
IAR DLIB, production-routed TLSF-backed heap wrappers, or bounded first-party
providers. The frontier is now 127 closed / 107 open, with 589 closed Ghidra
anchors, 333,518 complete-object body bytes, and 361,938 known physical bytes.
See `docs/research/g2-common-text-container-recovery.md`.

`app\gui\EvenHub\evenhub_ui.c` expands from nine anchors / 3,682 bytes to
26 functions / 14,296 body bytes / 15,568 physical bytes. Sixteen Ghidra-
missed functions recover the complete side-specific construction, parsing,
container, and callback surface. Both indirect sites are bounded to three
internal targets. All 823 direct external calls terminate at selected
EasyLogger/LVGL/nanopb sources, bounded IAR DLIB, production-routed
TLSF-backed heap wrappers, closed LZ4 adapters, or first-party providers. The
frontier is now 128 closed / 106 open, with 598 closed anchors, 347,814
complete-object body bytes, and 377,506 known physical bytes. See
`docs/research/g2-evenhub-ui-recovery.md`.

`app\gui\EvenHub\evenhub_data_parser.c` expands from twelve anchors / 8,136
bytes to nineteen functions / 10,336 executable bytes / 10,874 physical bytes.
Two Ghidra-missed functions and six inline table islands complete the parser
inventory. All 541 direct external calls terminate at selected EasyLogger,
nanopb, CMSIS-FreeRTOS, and LVGL sources; bounded IAR DLIB; production-routed
TLSF-backed heap wrappers; or first-party providers. There is no indirect
dispatch. The frontier is now 129 closed / 105 open, with 610 closed anchors,
358,150 complete-object body bytes, and 388,380 known physical bytes. See
`docs/research/g2-evenhub-data-parser-recovery.md`.

`framework\sync\sync_framework.c` expands from 23 retained-path anchors /
10,954 bytes to 43 functions / 16,816 executable bytes / 18,180 physical
bytes. Twenty missed callback and listener entries recover the generic
trampoline, two direct-entry synchronization functions, and ten TinyFrame
multipart handlers. All 1,051 external direct calls terminate at the admitted
EasyLogger, CMSIS-FreeRTOS, FreeRTOS, TinyFrame, AmbiqSuite, and nanopb
sources; bounded IAR DLIB; production-routed TLSF-backed heap wrappers; or
first-party providers. Fourteen indirect sites are bounded first-party
listener/callback seams. The frontier is now 130 closed / 104 open, with 633
closed anchors, 374,966 complete-object body bytes, and 406,560 known physical
bytes. See `docs/research/g2-sync-framework-recovery.md`.

The adjacent `framework\sync\sync_interface_api.c` is closed as thirteen
functions / 6,136 body bytes / 6,432 physical bytes. Its 333 external direct
calls terminate at admitted EasyLogger, CMSIS-FreeRTOS, and FreeRTOS sources;
bounded IAR DLIB; production-routed TLSF-backed heap wrappers; or the
first-party role provider. It has no indirect call or embedded third-party
definition. The frontier is now 131 closed / 103 open, with 646 closed
anchors, 381,102 complete-object body bytes, and 412,992 known physical bytes.
See `docs/research/g2-sync-interface-api-recovery.md`.

`framework\sync\display_thread.c` expands from fourteen anchors / 8,442
bytes to 27 functions / 9,100 body bytes / 9,834 physical bytes. Thirteen
restored functions include the already production-routed stored display
callback. All 522 external direct calls terminate at admitted EasyLogger,
CMSIS-FreeRTOS, FreeRTOS, and LVGL sources; bounded IAR DLIB; a production
runtime helper; or first-party providers. The main command loop and callback
are source-routed. The frontier is now 132 closed / 102 open, with 660 closed
anchors, 390,202 complete-object body bytes, and 422,826 known physical bytes.
See `docs/research/g2-display-thread-recovery.md`.

`driver\flash\drv_mx25u25643g.c` expands from 21 retained-path anchors /
5,420 bytes to forty functions / 6,726 body bytes / 7,360 physical bytes.
All 297 external calls terminate at admitted EasyLogger, AmbiqSuite Apollo510,
CMSIS-FreeRTOS, or shared-initializer sources; bounded IAR DLIB; or source-owned
runtime and delay providers. This reuses the selected AmbiqSuite `5efc0228…`,
CMSIS-FreeRTOS `d213f261…`, FreeRTOS-Kernel `def7d2df…`, and nanopb-compatible
`98bf4db6…` commits without introducing another dependency. The frontier is
now 133 closed / 101 open, with 681 closed anchors, 396,928 complete-object
body bytes, and 430,186 known physical bytes. See
`docs/research/g2-drv-mx25u25643g-recovery.md`.

`app\gui\MessageNotify\ui_msg_notif_list.c` expands from eighteen anchors /
5,392 bytes to fifty functions / 10,808 body bytes / 11,686 physical bytes.
Thirteen functions missed across the Ghidra shard boundary complete the UI
constructor, stored callbacks, and string helpers. All 599 external direct
calls terminate at selected EasyLogger, LVGL, CMSIS-FreeRTOS, and TLSF sources;
bounded IAR DLIB; or first-party providers. The frontier is now 134 closed /
100 open, with 699 closed anchors, 407,736 complete-object body bytes, and
441,872 known physical bytes. See
`docs/research/g2-ui-msg-notif-list-recovery.md`.

The misspelled stock `ui_DashBaord_Main_Screen.c` path expands from eight
anchors / 3,458 bytes to 31 functions / 9,040 body bytes / 9,896 physical
bytes. Its complete provider boundary reuses selected EasyLogger, LVGL, and
CMSIS-FreeRTOS sources plus bounded IAR and first-party dashboard widgets. The
audit distinguishes seven real interior callback pointers from six unaligned
word coincidences inside 32-bit instructions. The frontier is now 135 closed /
99 open, with 707 closed anchors, 416,776 complete-object body bytes, and
451,768 known physical bytes. See
`docs/research/g2-dashboard-main-screen-recovery.md`.

`app\gui\teleprompt\teleprompt_ui.c` expands from eight anchors / 3,034
bytes to 55 functions / 12,228 body bytes / 13,120 physical bytes. Thirty-eight
restored bodies complete the 4-by-19 mode/event table and screen/text/scroll
policy. All reusable calls terminate at selected EasyLogger and LVGL sources
or bounded IAR/first-party providers. The frontier is now 136 closed / 98
open, with 715 closed anchors, 429,004 complete-object body bytes, and 464,888
known physical bytes. See `docs/research/g2-teleprompt-ui-recovery.md`.

`platform\service\DFU\service_em9305_dfu.c` closes as seven functions /
2,802 body bytes / 2,826 physical bytes. Despite the filename it has zero
direct EM9305/Packetcraft vendor-code calls: all 152 external calls terminate
at selected EasyLogger, source-owned file/TLSF runtime, bounded IAR, the shared
zero initializer, or first-party DFU providers. The frontier is now 137 closed
/ 97 open, with 721 closed anchors, 431,806 complete-object body bytes, and
467,714 known physical bytes. See
`docs/research/g2-service-em9305-dfu-recovery.md`.

`app\gui\conversate\conversate_tag_data.c` expands from nine anchors /
2,562 bytes to twelve functions / 2,726 body bytes / 2,876 physical bytes. It
has no nanopb, JSON, or serialization-library edge; every external call is
EasyLogger, a production TLSF wrapper, or bounded IAR DLIB. The frontier is
now 138 closed / 96 open, with 730 closed anchors, 434,532 complete-object
body bytes, and 470,590 known physical bytes. See
`docs/research/g2-conversate-tag-data-recovery.md`.

`app\gui\dashboard\dashboard_watchface_layout4.c` expands from three anchors /
2,524 bytes to 23 functions / 4,184 body bytes / 4,606 physical bytes. The
audit corrects `0x005BBD10` from a false function start to object data and
recovers the stored MSPI cleanup callback at `0x005BBD48`. All reusable edges
terminate at selected EasyLogger, LVGL, and AmbiqSuite sources or bounded IAR
and first-party providers. The frontier is now 139 closed / 95 open, with 733
closed anchors, 438,716 complete-object body bytes, and 475,196 known physical
bytes. See `docs/research/g2-dashboard-watchface-layout4-recovery.md`.

`app\gui\dashboard\dashboard_ext.c` expands from six anchors / 2,498 bytes to
sixteen functions / 5,904 body bytes / 7,806 physical bytes. Ten restored
routines complete peer-role dashboard transfer, file lifecycle, protobuf
record handling, and resource lookup. Its dependencies are the already
selected EasyLogger, littlefs, nanopb, and FreeRTOS sources plus bounded IAR
and first-party providers. The frontier is now 140 closed / 94 open, with 739
closed anchors, 444,620 complete-object body bytes, and 483,002 known physical
bytes. See `docs/research/g2-dashboard-ext-recovery.md`.

`platform\protocols\dashboard_service\dashboard_data_process.c` expands from
seven anchors / 2,492 bytes to fourteen functions / 5,706 body bytes / 6,202
physical bytes. Four restored bodies and a separately pinned switch-dispatch
island close protobuf record processing and dashboard state policy. Its
reusable edges are the selected EasyLogger, nanopb, CMSIS-FreeRTOS, and
FreeRTOS sources plus bounded IAR providers. The frontier is now 141 closed /
93 open, with 746 closed anchors, 450,326 complete-object body bytes, and
489,204 known physical bytes. See
`docs/research/g2-dashboard-data-process-recovery.md`.

`platform\display_mgr\displaydrv_manager.c` expands from twelve anchors /
2,438 bytes to nineteen functions / 2,796 body bytes / 3,070 physical bytes.
Seven restored routines complete its lifecycle and stored callback set. All
external calls terminate at selected EasyLogger and CMSIS-FreeRTOS sources,
bounded IAR, or first-party ULED/thread/display providers; there are zero
direct LVGL or AmbiqSuite calls. The frontier is now 142 closed / 92 open, with
758 closed anchors, 453,122 complete-object body bytes, and 492,274 known
physical bytes. See `docs/research/g2-displaydrv-manager-recovery.md`.

The display-driver manager is also production-closed as of 2026-08-25. Its
nineteen functions compile from five authenticated C files (4,002 compiled
function bytes), and nineteen guarded redirects cover 2,798 stock bytes while
retaining 272 compatibility bytes. The exact source/routing analyzer and all
five host behavior fixture groups pass. Physical ULED/display, lock/timing,
and power-transition validation is blocked by unavailable physical evidence; future
qualification requires a responsive authorized G2 pair or golden display trace.
Nothing was signed,
flashed, or installed.

The adjacent LVGL font-manager software boundary is production-closed as of
2026-08-25. Eight clean-room C leaves compile to 904 text bytes plus 10
alignment bytes and replace all 2,590 stock function-body bytes through eight
guarded redirects and 19 strict relocations. Host tests cover four-entry
native/FreeType chains, allocation and cleanup failures, ordered fallbacks,
XIP-header policy, MSPI locking, and background/foreground initialization.
The external font payloads were not fabricated: their identities and live
rendering remain blocked by the unavailable golden flash capture and
responsive authorized display hardware. Nothing was signed, flashed, or
installed.

`driver\npmx_driver_transplant\src\npmx_main_driver.c` expands from eleven
anchors / 2,290 bytes to thirty functions / 6,560 body bytes / 7,102 physical
bytes. Its 72 direct nPMX calls identify 42 linked Nordic entries. The stock
ADC result-register rewrite includes official commit `e1aaec53…`, while the
double-promoted logarithm excludes its adjacent successor `53de7af4…`, uniquely
selecting public state `v1.0.1-1-ge1aaec5`. A byte-identical 38-file compact
driver snapshot is now admitted. The frontier is 143 closed / 91 open, with
769 closed anchors, 459,682 complete-object body bytes, and 499,376 known
physical bytes. PMIC production routing remains gated on the nPM1300 ADK and
configuration, Apollo510 I2C/interrupt integration, G2 power policy, and
hardware validation. See `docs/research/g2-npmx-main-driver-recovery.md`.

`app\gui\navigation\navigation_data_handler.c` is now closed as 22 functions /
8,076 reachable code bytes / 8,556 physical bytes. The restored dispatcher
crosses a Ghidra shard boundary and contains two explicitly separated inline
literal pools. All 423 external calls terminate at admitted EasyLogger,
nanopb, CMSIS-FreeRTOS, bounded IAR/runtime, or first-party providers; no new
third-party implementation or version discriminator is present. The frontier
is now 144 closed / 90 open, with 776 closed anchors, 467,758 complete-object
body bytes, and 507,932 known physical bytes. See
`docs/research/g2-navigation-data-handler-recovery.md`.
### Google liblc3 source/version admission

The `platform\audio\service_audio.c` frontier exposed four linked public
Google liblc3 entries at `0x00590E64`, `0x00590F78`, `0x00591374`, and
`0x0059138A`, reached by five direct calls. Stock's SNS `FLT_MAX` fingerprint
proves commit `bb85f7d…` or later, while its encoder fields at offsets 0/1/2
exclude the `ltpf_bypass` layout introduced by `9f1e206…`. Official v1.1.3
commit `96a3af0…` is now the selected tagged baseline; the complete 38-file
Apache-2.0 source tree is admitted byte-identically under `third_party/liblc3`.
The linked surface cannot distinguish the spelling-only, dead-stripped change
at compatible successor `1de85e2…`, so the exact producing checkout remains
explicitly unclaimed. The focused verifier and four tests pass, and the
aggregate ledger now closes 25 families with 24 selected source baselines and
zero locally actionable third-party gaps. See
`docs/research/g2-liblc3-source-recovery.md`.

`platform\audio\service_audio.c` is now closed as fourteen functions / 2,676
body bytes / 2,884 physical bytes. All 104 external direct calls terminate at
admitted EasyLogger, CMSIS-FreeRTOS, Google liblc3, IAR, littlefs/file-runtime,
closed `service_algo`, or first-party notification providers. Its sole indirect
call is resolved through three static registrations to the two already closed
production-microphone callbacks at `0x0058F4E4` and `0x0058F5E0`. The next PDM
object begins at `0x0057B444`, preventing its inline CMSIS helpers from being
misclassified as audio literal data. The frontier is now 145 closed / 89 open,
with 783 closed anchors, 470,434 complete-object body bytes, and 510,816 known
physical bytes. See `docs/research/g2-service-audio-recovery.md`.

`driver\pdm\drv_pdm_production.c` is now closed as six functions / 610 body
bytes / 704 physical bytes despite having no baseline Ghidra path anchor. Its
13 HAL calls cover 12 public Apollo510 PDM APIs and independently select the
same AmbiqSuite 5.1.0 replay commit `5efc0228…`; the exact public
`am_hal_pdm.c` blob is `23a440bf…`. The object also contains three CMSIS-Core
NVIC helper definitions and no indirect or interior ingress. The frontier is
now 146 closed / 88 open, with 471,044 complete-object body bytes and 511,520
known physical bytes. See
`docs/research/g2-drv-pdm-production-recovery.md`.

The adjacent zero-anchor `driver\pdm\drv_pdm.c` object is now closed as seven
functions / 794 body bytes / 900 physical bytes. Startup cell `0x00438100`
proves its PDM0 IRQ handler, and 19 calls cover 14 APIs in the same exact
Apollo510 `am_hal_pdm.c` blob; interrupt service/status are the two APIs added
beyond the production wrapper. The frontier is now 147 closed / 87 open, with
471,838 complete-object body bytes and 512,420 known physical bytes. See
`docs/research/g2-drv-pdm-recovery.md`.

`platform\service\message_notify\service_ancc.c` is now closed as twelve
functions / 2,340 body bytes / 2,890 physical bytes. Its 129 external calls are
85 admitted EasyLogger, 17 exact CMSIS-FreeRTOS v10.5.1 mutex, ten bounded IAR,
and 17 closed first-party edges; it embeds and calls no Ambiq ANCC implementation
body. Three stored interior callbacks and six data-only pseudo-`BL` patterns are
explicitly pinned. The frontier is now 148 closed / 86 open, with 789 closed
anchors, 474,178 complete-object body bytes, and 515,310 known physical bytes.
See `docs/research/g2-service-ancc-dependency-boundary.md`.

`driver\sensor\als\als.c` is now closed as 38 functions / 3,858 body bytes /
4,232 physical bytes. Twenty-nine functions were restored beyond the nine path
anchors. Its reusable edges are admitted EasyLogger, exact CMSIS-FreeRTOS
v10.5.1 delay, bounded runtime, closed first-party policy, and six calls to the
clean-room TI OPT3007 adapter; no public OPT3007 software commit exists. One
stored callback and the bounded display-driver indirect dispatch are pinned,
and the apparent interior branch at `0x004AE09C` is an unaligned pseudo-`BL`.
The frontier is now 149 closed / 85 open, with 798 closed anchors, 478,036
complete-object body bytes, and 519,542 known physical bytes. See
`docs/research/g2-als-dependency-boundary.md`.

`platform\threads\thread_ble_production.c` is now closed as 14 functions /
2,140 body bytes / 2,368 physical bytes. A stored literal proves the previously
hidden task body at `0x005382E4`; two further restored bodies create and
terminate the CMSIS thread. The object makes 15 exact CMSIS-FreeRTOS v10.5.1
calls, three exact FreeRTOS V10.5.1 assertion-mask calls, and no embedded Cordio
calls. Its static task attributes, three-entry queue, three-block 0x104-byte
pool, production-frame header/checksum, all ingress, and two unaligned raw-value
lookalikes are pinned. The frontier is now 150 closed / 84 open, with 804 closed
anchors, 480,176 complete-object body bytes, and 521,910 known physical bytes.
See `docs/research/g2-thread-ble-production-dependency-boundary.md`.

`platform\product_test\pt_protocol_procsr.c` is now closed as 73 functions /
32,866 body bytes / 35,524 physical bytes. Sixty-nine retained-path anchors
expand through three pathless Ghidra functions and a hidden externally called
handler at `0x0056F92C`. The object's sole indirect call is bounded by a
66-entry aligned Thumb handler table. Its 1,526 external direct calls comprise
1,280 admitted EasyLogger calls, seven exact CMSIS-FreeRTOS v10.5.1 calls, one
exact FreeRTOS V10.5.1 `xTaskGetTickCount`, one selected mpaland printf call,
41 bounded IAR/runtime/fail-stop calls, and 196 first-party calls. No reusable
third-party body or new version discriminator is embedded. The frontier is now
151 closed / 83 open, with 873 closed anchors, 513,042 complete-object body
bytes, and 557,434 known physical bytes. See
`docs/research/g2-pt-protocol-procsr-dependency-boundary.md`.

`app\gui\quicklist\ui_quicklist_page.c` is now closed as 80 functions /
21,886 body bytes / 23,594 physical bytes. Seventeen functions were restored
beyond the 63-function Ghidra inventory, and fifteen aligned stored callbacks
plus 164 direct entry sites close whole-image ingress. Its 990 external calls
are 415 selected LVGL, 465 admitted EasyLogger, five exact CMSIS-FreeRTOS
`osKernelGetTickCount`, 24 bounded IAR runtime, and 81 first-party calls. It
embeds no reusable dependency body and adds no commit discriminator. The
frontier is now 152 closed / 82 open, with 916 closed anchors, 534,928
complete-object body bytes, and 581,028 known physical bytes. See
`docs/research/g2-ui-quicklist-page-dependency-boundary.md`.

`app\gui\dashboard\screens\ui_widget_news_page.c` is now closed as 45
functions / 19,058 body bytes / 20,668 physical bytes. Fourteen helpers were
restored beyond Ghidra, and 70 direct entry sites plus twelve stored callbacks
close ingress. Its 1,196 external calls are 508 selected LVGL, 565 admitted
EasyLogger, eight exact CMSIS-FreeRTOS mutex, 36 bounded IAR/EABI runtime, and
79 first-party calls. It embeds no reusable dependency body and adds no commit
discriminator. The frontier is now 153 closed / 81 open, with 938 closed
anchors, 553,986 complete-object body bytes, and 601,696 known physical bytes.
See `docs/research/g2-ui-widget-news-page-dependency-boundary.md`.

`app\gui\dashboard\screens\ui_stock_page.c` is now closed as 34 functions /
13,892 body bytes / 14,852 physical bytes. Two functions were restored beyond
Ghidra; 116 direct entry sites and two stored callbacks close ingress. Its 852
external calls are 454 selected LVGL, 355 admitted EasyLogger, ten bounded IAR
runtime, and 33 first-party calls. It has zero CMSIS-FreeRTOS/FreeRTOS calls,
embeds no reusable body, and adds no commit discriminator. The frontier is now
154 closed / 80 open, with 957 closed anchors, 567,878 complete-object body
bytes, and 616,548 known physical bytes. See
`docs/research/g2-ui-stock-page-dependency-boundary.md`.

`app\gui\navigation\navigation_ui.c` is now closed as 61 functions / 36,612
body bytes / 39,056 physical bytes. Twenty-nine entries were restored beyond
Ghidra; 152 direct entries, fourteen stored function starts, and five stored
shared-tail callback entries close ingress. Its 2,237 external calls are 702
selected LVGL, 1,245 admitted EasyLogger, twenty exact CMSIS-FreeRTOS mutex,
67 bounded IAR runtime, 22 admitted nanopb, two selected mpaland printf, and
179 first-party calls. It embeds no reusable dependency body and adds no
commit discriminator. The frontier is now 155 closed / 79 open, with 973
closed anchors, 604,490 complete-object body bytes, and 655,604 known physical
bytes. See `docs/research/g2-navigation-ui-dependency-boundary.md`.

`app\gui\menu\menu_page.c` is now closed as 34 functions / 13,906 body bytes /
15,066 physical bytes. Nine entries were restored beyond Ghidra; 98 direct
entries, eight stored function starts, and one stored shared interior entry
close ingress. Its 746 external calls are 124 selected LVGL, 445 admitted
EasyLogger, three exact CMSIS-FreeRTOS event/mutex, 24 bounded IAR runtime,
fifteen admitted nanopb, and 135 first-party calls. It embeds no reusable body
and adds no commit discriminator. The frontier is now 156 closed / 78 open,
with 987 closed anchors, 618,396 complete-object body bytes, and 670,670 known
physical bytes. See `docs/research/g2-menu-page-dependency-boundary.md`.

`app\gui\health\ui_health_page.c` is now closed as twelve functions / 9,414
body bytes / 10,054 physical bytes. One callback was restored beyond Ghidra;
nineteen direct entries and two stored pointers close ingress. Its 666 external
calls are 437 selected LVGL, 55 admitted EasyLogger, four bounded IAR, 36
selected mpaland printf, and 134 first-party calls; there are zero direct
CMSIS-FreeRTOS calls. The frontier is now 157 closed / 77 open, with 994 closed
anchors, 627,810 complete-object body bytes, and 680,724 known physical bytes.
See `docs/research/g2-ui-health-page-dependency-boundary.md`.

`platform\protocols\ring_service\ring_service.c` is now closed as eighteen
functions / 2,412 body bytes / 2,616 physical bytes. Its 121 external calls
terminate at admitted EasyLogger, CMSIS-FreeRTOS, nanopb, bounded IAR, or
first-party providers; there are zero direct Cordio calls. The frontier is now
158 closed / 76 open, with 1,003
closed anchors, 630,222 complete-object body bytes, and 683,340 known physical
bytes. See `docs/research/g2-ring-service-dependency-boundary.md`.

The same Ring-service object is now production-routed from eighteen
selector-isolated clean-room C leaves. Eighteen guarded redirects replace all
2,412 stock body bytes with 952 compiled Thumb bytes plus eighteen alignment
bytes; 38 strict relocations bind reviewed source seams. Host tests cover frame
construction, validation, touch deduplication, battery and wear reports, and
all recovered command IDs. Canonical overlay/component/package sizes are
255,686 / 3,779,082 / 4,557,576 bytes with SHA-256 values
`2def566dbf70594c89471066a7cd17f6d1fa94196f65ff48237385396e9cfd19`,
`7228edb650fe39bda63480691fe94ed59d0807ca5e30846d35ec08e134e08350`,
and `c146ea7977a5521aa1df24a1a285768d7e2396fab96f117315a5baa2dcb65998`.
Live paired-G2 qualification is blocked by unavailable physical evidence; future
qualification requires an authorized G2 pair or golden Ring capture.
`thread_ring.c` remains the Ring stack's
software gap.

`platform\input\service_input_manager.c` is now closed as ten functions /
2,242 body bytes / 2,490 physical bytes. Five path anchors expand through five
adjacent helpers; 103 external calls terminate at admitted EasyLogger,
CMSIS-FreeRTOS, nanopb, bounded memory/runtime leaves, or first-party
input/event/timer/transport providers. It directly calls neither LVGL nor
Cordio. The frontier is now 159 closed / 75 open, with 1,008 closed anchors,
632,464 complete-object body bytes, and 685,830 known physical bytes. See
`docs/research/g2-service-input-manager-dependency-boundary.md`.

`app\gui\dashboard\screens\ui_calendar_page.c` is now closed as fifteen
functions / 9,690 body bytes / 10,172 physical bytes. Five path anchors expand
through seven additional Ghidra bodies and three restored functions. Its 722
external calls are 533 admitted LVGL, 85 admitted EasyLogger, 34 exact
CMSIS-FreeRTOS mutex, twelve bounded IAR/runtime, and 58 first-party calls.
The frontier is now 160 closed / 74 open, with 1,013 closed anchors, 642,154
complete-object body bytes, and 696,002 known physical bytes. See
`docs/research/g2-ui-calendar-page-dependency-boundary.md`.

`platform\protocols\ota_service\ota_transport.c` is now closed as three
functions / 2,004 body bytes / 2,292 physical bytes. Its 86 direct calls close
over EasyLogger, bounded IAR memory, the source-owned CRC and synchronized TLSF
wrappers, closed OTA-service policy, and three first-party event providers.
Four indirect sites use two registered first-party callback slots. Three
selector-isolated clean-room functions now compile to 1,300 Thumb bytes plus
two alignment bytes; three redirects and 14 strict relocations replace all
2,004 stock body bytes while retaining the 288-byte official pool. Component,
manifest, complete-package, frontier, and origin-accounting gates are green.
Live OTA peer traffic and recovery evidence is blocked by unavailable physical evidence; future qualification requires authorized responsive G2 hardware. The frontier
is now 161 closed / 73 open, with 1,015 closed anchors, 644,158 complete-object
body bytes, and 698,294 known physical bytes. See
`docs/research/g2-ota-transport-dependency-boundary.md`.

`platform\protocols\efs_service\efs_transport.c` is now closed as two
functions / 1,990 body bytes / 2,152 physical bytes. Its 87 direct calls close
over EasyLogger, one exact CMSIS-FreeRTOS tick wrapper, bounded IAR memory,
source-owned CRC/TLSF wrappers, closed EFS-service policy, and first-party
event providers. Four indirect sites use two registered callback slots. Two
selector-isolated clean-room functions compile to 1,276 Thumb bytes; two
redirects and 15 strict relocations replace all 1,990 stock body bytes while
retaining the authenticated 162-byte pool. Host behavior, target compilation,
component, manifest, complete-package, frontier, and aggregate gates are
green. Live EFS filesystem/media traffic, timeout, disconnect, and recovery
evidence is blocked by unavailable physical evidence; future qualification requires authorized responsive G2 hardware. The
frontier is now 162 closed / 72 open, with 1,017 closed anchors, 646,148
complete-object body bytes, and 700,446 known physical bytes. See
`docs/research/g2-efs-transport-dependency-boundary.md`.

`app\gui\EvenHub\evenhub_loading_Page.c` is now closed as four functions /
2,042 body bytes / 2,328 physical bytes. Two path anchors expand through two
adjacent helpers, and the object boundary stops at the hidden first helper of
`evenhub_ui.c`. Its 137 external calls are 36 admitted LVGL, 85 admitted
EasyLogger, two bounded runtime, and fourteen first-party calls; two stored
function pointers close ingress. The frontier is now 163 closed / 71 open,
with 1,019 closed anchors, 648,190 complete-object body bytes, and 702,774
known physical bytes. See
`docs/research/g2-evenhub-loading-page-dependency-boundary.md`.

`app\gui\dashboard\dashboard_watchface_layout1.c` is now closed as nineteen
functions / 3,500 body bytes / 3,592 physical bytes. Ten callbacks and helpers
were restored beyond Ghidra; both indirect calls bind to two recovered local
callbacks. Its 215 external direct calls are 154 admitted LVGL, twenty
EasyLogger, thirteen bounded IAR, ten selected mpaland printf, and eighteen
first-party calls. The frontier is now 164 closed / 70 open, with 1,021 closed
anchors, 651,690 complete-object body bytes, and 706,366 known physical bytes.
See `docs/research/g2-dashboard-watchface-layout1-recovery.md`.

`app\gui\teleprompt\teleprompt_fsm.c` is now closed as fifteen functions /
2,994 body bytes / 3,302 physical bytes. Eight source-order handlers were
restored beyond Ghidra; one indirect dispatch is bounded to a nine-entry local
handler table. Its 172 external direct calls are 140 admitted EasyLogger,
three bounded IAR/runtime, one LVGL, two nanopb, and 26 first-party calls. The
frontier is now 165 closed / 69 open, with 1,024 closed anchors, 654,684
complete-object body bytes, and 709,668 known physical bytes. See
`docs/research/g2-teleprompt-fsm-dependency-boundary.md`.

`app\gui\health\health_data_manager.c` is now closed as ten functions / 2,644
body bytes / 2,912 physical bytes. One source-order parser was restored beyond
Ghidra. Its 136 external calls are 120 admitted EasyLogger, six bounded
IAR/runtime, and ten already closed health-lock calls; it has no direct RTOS
edge or hidden health/DSP library. The frontier is now 166 closed / 68 open,
with 1,029 closed anchors, 657,328 complete-object body bytes, and 712,580
known physical bytes. See
`docs/research/g2-health-data-manager-dependency-boundary.md`.

`app\gui\EvenHub\evenhub_main.c` is now closed as five functions / 3,130 body
bytes / 3,450 physical bytes. One source-order event routine was restored
beyond Ghidra. Its 180 external direct calls are 120 admitted EasyLogger, six
bounded IAR/EABI runtime, two LVGL, two exact CMSIS-FreeRTOS tick, three
nanopb, two production TLSF-wrapper, and 45 first-party calls. It embeds no
third-party implementation and adds no version discriminator. The frontier is
now 167 closed / 67 open, with 1,032 closed anchors, 660,458 complete-object
body bytes, and 716,030 known physical bytes. See
`docs/research/g2-evenhub-main-dependency-boundary.md`.

`app\gui\translate\translate.c` is now closed as eleven functions / 2,504
body bytes / 2,862 physical bytes. Two source-order handlers were restored
beyond Ghidra. Its 156 external calls terminate at admitted EasyLogger, LVGL,
CMSIS-FreeRTOS, and nanopb, bounded runtime, or first-party translate services.
The frontier is now 168 closed / 66 open, with 1,039 closed anchors, 662,962
complete-object body bytes, and 718,892 known physical bytes. See
`docs/research/g2-translate-dependency-boundary.md`.

`app\gui\teleprompt\teleprompt.c` is now closed as ten functions / 2,408 body
bytes / 3,900 physical bytes. Two event handlers were restored beyond Ghidra.
Its 149 external calls terminate at admitted EasyLogger, LVGL,
CMSIS-FreeRTOS, and nanopb, bounded runtime, or first-party teleprompt
providers. The frontier is now 169 closed / 65 open, with 1,046 closed
anchors, 665,370 complete-object body bytes, and 722,792 known physical bytes.
See `docs/research/g2-teleprompt-controller-dependency-boundary.md`.

`app\gui\conversate\conversate_comm_data.c` is now closed as twelve functions
/ 2,208 body bytes / 2,560 physical bytes. Its 72 external calls are sixty
EasyLogger, eleven bounded IAR memory, and one admitted LVGL text-measurement
call. The frontier is now 170 closed / 64 open, with 1,052 closed anchors,
667,578 complete-object body bytes, and 725,352 known physical bytes. See
`docs/research/g2-conversate-comm-data-dependency-boundary.md`.

`app\gui\dashboard\dashboard_watchface_layout3.c` is now closed as nineteen
functions / 3,254 body bytes / 3,648 physical bytes. Seven source-order
callbacks and helpers were restored beyond Ghidra. Its 173 external calls are
125 admitted LVGL, twenty EasyLogger, ten bounded IAR, two selected mpaland
printf, and sixteen first-party calls. Five raw apparent Thumb calls are the
second halfwords of pinned four-byte `sdiv` instructions. The frontier is now
171 closed / 63 open, with 1,053 closed anchors, 670,832 complete-object body
bytes, and 729,000 known physical bytes. See
`docs/research/g2-dashboard-watchface-layout3-recovery.md`.

`platform\threads\thread_ring.c` is now closed as seventeen functions / 2,374
body bytes / 2,632 physical bytes. Twelve source-order functions were restored,
including the CMSIS thread entry at `0x004C4CEC`; this corrects the preceding
BLE Ring-profile boundary by removing 120 bytes formerly classified as
noncode. Its 162 external calls are 110 EasyLogger, ten exact CMSIS-FreeRTOS,
two bounded FreeRTOS assert, two IAR, three production TLSF-wrapper, thirteen
closed Ring-service, sixteen event-loop, and six other first-party calls. The
frontier is now 172 closed / 62 open, with 1,058 closed anchors, 673,206
complete-object body bytes, and 731,512 known physical bytes. See
`docs/research/g2-thread-ring-dependency-boundary.md`.

The Thread Ring object is now production-routed from all seventeen
selector-isolated source leaves. Fifteen guarded redirects replace 2,370 stock
body bytes with 894 compiled Thumb bytes plus 22 generated alignment bytes;
72 strict relocations bind reviewed providers. Two unreachable two-byte empty
hook stubs and the 258-byte pool remain as 262 authenticated compatibility
bytes, while the source entry calls both source hooks directly. Host lifecycle,
queue, dispatch, delayed-event, touch/pair, record, and allocation-failure tests
and every strict Cortex-M55 selector build pass. Canonical overlay/component/
package sizes are 255,686 / 3,779,082 / 4,557,576 bytes. Physical peer behavior
is blocked by unavailable physical evidence; future qualification requires an authorized
G2 pair or golden capture;
there is no remaining known Thread Ring software implementation gap.

`framework\fw_event_loop\fw_event_loop.c` is now closed as six functions /
1,806 body bytes / 2,012 physical bytes. The 108-byte worker missed by Ghidra
completes the object. Its 104 external direct calls are eighty admitted
EasyLogger, twenty exact CMSIS-FreeRTOS, and four exact FreeRTOS critical-port
calls; one indirect call invokes a callback dequeued in a bounded event record.
All six functions were already production-routed to the clean-room event-loop
source. The frontier is now 173 closed / 61 open, with 1,063 closed anchors,
675,012 complete-object body bytes, and 733,524 known physical bytes. See
`docs/research/g2-fw-event-loop-dependency-boundary.md`.

`platform\protocols\ring_service\ring_connect_policy.c` is now closed as
fifteen functions / 1,828 body bytes / 2,056 physical bytes. The true object
starts 60 bytes before its first retained-path anchor with three pathless
tick/timeout helpers; the stored `_ringReconnectTimeoutFire` callback supplies
the fourth restoration. Its 108 external calls are 95 admitted EasyLogger,
one exact CMSIS-FreeRTOS tick wrapper, ten closed event-loop, one closed
nanopb-facade, and one closed BLE-central call, with no direct Cordio or nanopb
edge. The frontier is now 174 closed / 60 open, with 1,074 closed anchors,
676,840 complete-object body bytes, and 735,580 known physical bytes. See
`docs/research/g2-ring-connect-policy-dependency-boundary.md`.

The same Ring-connect-policy object is now production-routed through fifteen
guarded entry redirects to a complete clean-room C implementation. Its reviewed
Apple build contributes 570 text bytes plus 14 alignment bytes and 24 strict
relocations; all 1,828 stock body bytes are source-owned while the 228-byte
literal pool remains authenticated official data. Host state-machine tests,
all fifteen strict Cortex-M55 selectors, the dedicated analyzer, component,
package, flash-plan, origin-accounting, and first-party-frontier gates pass.
Live role switching, WSF timing, reconnect, and peer notification behavior are
blocked by unavailable physical evidence; future qualification requires authorized responsive paired hardware.

`app\gui\SystemClose\systemClose.c` is now closed as twenty functions / 4,960
body bytes / 5,368 physical bytes. Fifteen functions missed by Ghidra restore
the event FIFO, common-data/page handlers, selection animation, option builder,
reflash dispatch, and display lifecycle. The final 282-byte UI handler corrects
the old service-settings neighbor pin that had classified it as literal pool.
Its 271 external calls are 130 EasyLogger, 99 admitted LVGL, five bounded IAR,
and 37 first-party display/sync calls, with no CMSIS-FreeRTOS or new utility.
The frontier is now 175 closed / 59 open, with 1,079 closed anchors, 681,800
complete-object body bytes, and 740,948 known physical bytes. See
`docs/research/g2-system-close-dependency-boundary.md`.

The Translate-UI predecessor gap is now identified and functionally closed as
IAR DLIB `frexpf`, its binary32 decomposition helper, and `ldexpf`: three exact
bodies / 268 bytes at `[0x0059D244,0x0059D350)`. Selector-isolated clean-room
assembly reproduces the authenticated stock bytes after the two relocations,
and 12,000 differential executions pass. All three entries are guarded and
canonical-Apple production-routed; Linux remains excluded until its reviewed
Clang 22.1.8 environment records independent pins. The historical IAR release
and archive variant remain externally gated. See
`docs/research/iar-dlib-frexpf-ldexpf-recovery.md`.

`app\gui\translate\translate_ui.c` is now closed as 29 functions / 5,288
body bytes / 5,730 physical bytes. Twenty-two source-order or stored callbacks
were restored beyond its seven Ghidra anchors. Its 346 external direct calls
are 175 EasyLogger, 125 LVGL, ten bounded IAR DLIB, two exact
CMSIS-FreeRTOS, and 34 first-party edges; the single indirect callback is
record-bounded. It embeds no reusable implementation and adds no provenance
discriminator. See
`docs/research/g2-translate-ui-dependency-boundary.md`.

`app\gui\conversate\conversate.c` is now closed as twelve functions / 2,250
body bytes / 2,628 physical bytes. Three bodies were restored beyond its nine
Ghidra anchors. All 139 external calls terminate at selected EasyLogger,
CMSIS-FreeRTOS, LVGL, nanopb, bounded IAR/EABI, CmBacktrace, or first-party
providers. The vector-referenced CmBacktrace edge corroborates the existing
`4abadfa0…73714489` compatibility interval and OpenCFW's selected `73714489`
snapshot, but does not prove Even's historical commit. The frontier is now 177
closed / 57 open, with 1,095 closed anchors, 689,338 complete-object body bytes,
and 749,306 known physical bytes. See
`docs/research/g2-conversate-controller-dependency-boundary.md`.

`app\gui\EvenHub\common_image_container.c` is now closed as three functions /
1,554 body bytes / 1,834 physical bytes. Its 80 external calls terminate at
selected EasyLogger/LVGL, production TLSF-backed free and Apollo510 cache-clean
providers, one bounded absolute-value helper, or two first-party seams. It adds
no dependency or commit discriminator. The frontier advances again to 178
closed / 56 open and 450,446 closed anchored bytes. See
`docs/research/g2-common-image-container-dependency-boundary.md`.

`dashboard_watchface_layout2.c` is now closed as nineteen functions / 2,844
body bytes / 3,076 physical bytes, including thirteen source-order bodies
restored beyond its single anchor. Its 181 external calls terminate at selected
EasyLogger, LVGL, mpaland printf, bounded IAR, or first-party dashboard
providers. The frontier is now 179 closed / 55 open and 93.13% of anchored
bytes are closed. See
`docs/research/g2-dashboard-watchface-layout2-recovery.md`.

`app\gui\conversate\conversate_ui_main_page.c` is now closed as fifteen
functions / 4,132 body bytes / 4,492 physical bytes. Eleven source-order
routines were restored beyond Ghidra's four entries. One stored callback enters
the authenticated `0x005B305C` continuation of the large UI-construction
routine; it is pinned as an alternate interior entry, not double-counted as an
overlapping function. All 283 external calls terminate at selected EasyLogger
and LVGL, bounded/source-recreated IAR `snprintf`, or first-party conversate
providers. The frontier is now 180 closed / 54 open and 93.43% of anchored
bytes are closed. See
`docs/research/g2-conversate-ui-main-page-recovery.md`.

`platform\service\service_universal_setting\service_universal_setting.c`
is now closed as fifteen functions / 2,010 body bytes / 2,156 physical bytes.
Ten bodies missed by Ghidra restore the live-record helpers and six field
getters. Its 103 external calls terminate at selected EasyLogger, bounded IAR
memory primitives, the production source-owned CCITT-FALSE leaf, already
closed KV record writers, or first-party role/sync/scheduling providers. It
adds no dependency or commit discriminator. The frontier is now 181 closed /
53 open and 93.73% of anchored bytes are closed. See
`docs/research/g2-service-universal-setting-recovery.md`.

## G2 retained-path frontier closes completely

`app\gui\conversate\conversate_pb_msg_handler.c` is now closed as 15
functions / 3,440 body bytes / 3,764 physical bytes. All 214 external direct
calls terminate at admitted EasyLogger, bounded IAR, LVGL, and nanopb edges,
and its single indirect call is bounded. It embeds no reusable implementation.
The frontier is now 182 closed / 52 open. See
`docs/research/g2-conversate-pb-msg-handler-dependency-boundary.md`.

`app\gui\quicklist\quicklist_data_manager.c` is now closed as three functions
/ 1,350 body bytes / 1,480 physical bytes. Its 67 external calls terminate at
admitted EasyLogger, bounded IAR, and first-party leaf edges only, with no
embedded reusable implementation. The frontier is now 183 closed / 51 open.
See `docs/research/g2-quicklist-data-manager-dependency-boundary.md`.

`app\gui\EvenAI\even_ai_animation.c` is now closed as five functions / 2,036
body bytes / 2,228 physical bytes. Its 79 external calls terminate at admitted
EasyLogger, bounded IAR, and LVGL edges plus one exact CMSIS-FreeRTOS seam,
with no embedded reusable implementation. The frontier is now 184 closed /
50 open. See `docs/research/g2-even-ai-animation-dependency-boundary.md`.

`app\gui\onboarding\onboarding_animation.c` is now closed as eleven functions
/ 1,598 body bytes / 2,004 physical bytes. Its 80 external calls terminate at
admitted EasyLogger, bounded IAR, LVGL, and nanopb edges plus production
source-owned TLSF heap wrappers. The frontier is now 185 closed / 49 open.
See `docs/research/g2-onboarding-animation-dependency-boundary.md`.

`platform\threads\thread_manager.c` is now closed as 17 functions / 1,934
body bytes / 2,172 physical bytes. Its 30 exact CMSIS-FreeRTOS v10.5.1 calls
span twelve distinct osXxx APIs (osKernelInitialize/Start/GetTickCount,
osThreadNew/GetId/SetPriority/Terminate, osThreadFlagsSet/Wait, and
osEventFlagsNew/Set/Wait); remaining edges are admitted EasyLogger, the
FreeRTOS assert port, the littlefs port, and closed or bounded first-party
providers, with no IAR DLIB edge. The frontier is now 186 closed / 48 open.
See `docs/research/g2-thread-manager-dependency-boundary.md`.

`driver\touch\drv_cy8c4046fni.c` is now closed as 23 functions / 1,754 body
bytes / 1,924 physical bytes. Its edges are admitted EasyLogger, exact
CMSIS-FreeRTOS osDelay, the closed HAL I2C provider, and bounded IAR DLIB.
No public Cypress or Infineon host-side I2C driver source candidate exists,
so the object is documented as Even private first-party with negative
provenance. The frontier is now 187 closed / 47 open. See
`docs/research/g2-drv-cy8c4046fni-dependency-boundary.md`.

`framework\sync\thread_pool.c` is now closed as three functions / 1,290 body
bytes / 1,452 physical bytes. Its 78 external calls terminate at admitted
EasyLogger, exact CMSIS-FreeRTOS, the FreeRTOS assert port, and bounded IAR
DLIB, with zero first-party call edges. The frontier is now 188 closed /
46 open. See `docs/research/g2-thread-pool-dependency-boundary.md`.

`framework\page_manager\page_manager.c` is now closed as 45 functions /
4,510 body bytes / 4,656 physical bytes. Its 139 external calls terminate at
admitted EasyLogger and LVGL, TLSF-backed heap wrappers, closed first-party
providers, and bounded IAR DLIB. The frontier is now 189 closed / 45 open.
See `docs/research/g2-page-manager-dependency-boundary.md`.

`app\ux\ux_wear_detect\ux_wear_detect.c` is now closed as seven functions /
1,236 body bytes / 1,352 physical bytes. Its 71 external calls terminate at
admitted EasyLogger, bounded IAR, and nanopb edges; CMSIS-FreeRTOS
osKernelGetTickCount is the sole RTOS seam. The frontier is now 190 closed /
44 open. See `docs/research/g2-ux-wear-detect-dependency-boundary.md`.

`app\gui\anim\fade_anim.c` is now closed as eleven functions / 1,678 body
bytes / 1,802 physical bytes. Its 89 external calls terminate at admitted
EasyLogger and LVGL 9.3-compatible edges only, with no RTOS seam. The
frontier is now 191 closed / 43 open. See
`docs/research/g2-fade-anim-dependency-boundary.md`.

`app\gui\anim\list_anim.c` is now closed as eleven functions / 1,348 body
bytes / 1,460 physical bytes. Its 73 external calls terminate at admitted
EasyLogger, bounded IAR, and LVGL edges; CMSIS-FreeRTOS osKernelGetTickCount
is the sole RTOS seam. The frontier is now 192 closed / 42 open. See
`docs/research/g2-list-anim-dependency-boundary.md`.

`app\gui\common\generic_animation.c` is now closed as 17 functions / 1,622
body bytes / 1,736 physical bytes. Its 80 external calls terminate at admitted
EasyLogger, bounded IAR, and LVGL edges plus production source-owned TLSF
heap wrappers; CMSIS-FreeRTOS osKernelGetTickCount is the sole RTOS seam.
The frontier is now 193 closed / 41 open. See
`docs/research/g2-generic-animation-dependency-boundary.md`.

`app\gui\conversate\conversate_timer_mgr.c` is now closed as 24 functions /
2,204 body bytes / 2,440 physical bytes. Its 102 external calls terminate at
admitted EasyLogger, the exact CMSIS-FreeRTOS tick wrapper, and closed
first-party providers. The frontier is now 194 closed / 40 open. See
`docs/research/g2-conversate-timer-mgr-dependency-boundary.md`.

`app\gui\conversate\conversate_ui_prep_note_page.c` is now closed as 16
functions / 3,114 body bytes / 3,248 physical bytes. Its 188 external calls
terminate at admitted EasyLogger, bounded IAR, LVGL, and closed first-party
conversate providers. The frontier is now 195 closed / 39 open. See
`docs/research/g2-conversate-ui-prep-note-page-dependency-boundary.md`.

`app\gui\teleprompt\teleprompt_timer_mgr.c` is now closed as 13 functions /
1,498 body bytes / 1,660 physical bytes. Its 65 external calls terminate at
admitted EasyLogger, the exact CMSIS-FreeRTOS tick wrapper, and closed
first-party providers. The frontier is now 196 closed / 38 open. See
`docs/research/g2-teleprompt-timer-mgr-dependency-boundary.md`.

`app\gui\conversate\conversate_ui.c` is now closed as 23 functions / 3,774
body bytes / 4,084 physical bytes. Its 221 external calls terminate at
admitted EasyLogger, bounded IAR, LVGL, and closed first-party conversate
providers. The frontier is now 197 closed / 37 open. See
`docs/research/g2-conversate-ui-dependency-boundary.md`.

`app\gui\dashboard\page_state_sync.c` is now closed as eight functions /
1,244 body bytes / 1,380 physical bytes. Its 57 external calls terminate at
admitted EasyLogger, IAR DLIB, and nanopb edges only. The frontier is now
198 closed / 36 open. See
`docs/research/g2-page-state-sync-dependency-boundary.md`.

`app\gui\translate\translate_fsm.c` is now closed as eight functions / 1,304
body bytes / 1,448 physical bytes. Its single indirect `blx` is bounded by
the stored six-entry state-handler table; all 86 external direct calls
terminate at admitted EasyLogger, IAR DLIB, and nanopb edges. The frontier
is now 199 closed / 35 open. See
`docs/research/g2-translate-fsm-dependency-boundary.md`.

`platform\service\box_detect\service_box_detect.c` is now closed as 32
functions / 3,564 body bytes / 3,912 physical bytes. Its thirteen exact
CMSIS-FreeRTOS timer calls span osTimerNew/Start/Stop/IsRunning/Delete;
remaining edges are admitted EasyLogger and IAR DLIB only. The frontier is
now 200 closed / 34 open. See
`docs/research/g2-service-box-detect-dependency-boundary.md`.

`app\gui\module_configure\general_configure.c` is now closed as ten
functions / 2,376 body bytes / 2,616 physical bytes. Its 141 external calls
terminate at admitted EasyLogger, IAR DLIB, CMSIS-FreeRTOS event flags, and
nanopb edges only. The frontier is now 201 closed / 33 open. See
`docs/research/g2-general-configure-dependency-boundary.md`.

`app\gui\terminal\terminal_data.c` is now closed as 44 functions / 2,902
body bytes / 3,012 physical bytes. Its 45 external calls terminate at
admitted EasyLogger and IAR DLIB edges plus the closed time-service provider.
The frontier is now 202 closed / 32 open. See
`docs/research/g2-terminal-data-dependency-boundary.md`.

`platform\sensor_hub\sensor_hub.c` is now closed as 31 functions / 4,026
body bytes / 4,408 physical bytes. Its nine distinct exact CMSIS-FreeRTOS
v10.5.1 wrappers cover osKernelGetTickCount, osThreadNew/Terminate,
osTimerNew/Start/Stop, and osMessageQueueNew/Put/Get; remaining edges are
admitted EasyLogger, LVGL, a nanopb seam, and closed or bounded first-party
providers. Explicit negative evidence records no embedded sensor-fusion
library body. The frontier is now 203 closed / 31 open. See
`docs/research/g2-sensor-hub-dependency-boundary.md`.

The Sensor Hub object is now also production-routed. Thirty guarded redirects
replace 4,024 callable stock bytes with 1,602 selector-isolated Thumb bytes and
36 alignment bytes; 106 strict relocations bind reviewed CMSIS, sensor-driver,
NVDB, OTA, translation, LVGL, and sibling seams. The two-byte empty hook plus
382 bytes of authenticated pools remain as 384 compatibility bytes. Host tests
cover queue/thread/timer lifecycle, bounded message dispatch, role and
open/close policy, ALS polling, IMU modes and calibration, mutual exclusion,
and calibration UI feedback; all 31 strict Cortex-M55 selectors pass. Canonical
overlay/component/package sizes are 255,686 / 3,779,082 / 4,557,576 bytes; the
2,879,088-byte flash plan has 4,141 placed, two unresolved, five container-only,
and six protected regions. Live sensor, timing, calibration, and display
qualification is blocked by unavailable physical evidence; future qualification requires
an authorized G2 sensor path or golden IMU/ALS trace. Wider firmware gaps remain, so
functional completeness is not claimed.

`platform\threads\thread_input.c` is now closed as 23 functions / 2,090
body bytes / 2,296 physical bytes. Its ten exact CMSIS-FreeRTOS v10.5.1
calls span osThreadNew/Terminate, osThreadFlagsSet/Wait, osDelay, and
osMessageQueueNew/Put/Get/Delete; remaining edges are admitted EasyLogger,
IAR DLIB, a source-owned runtime wrapper, and closed or bounded first-party
providers. The frontier is now 204 closed / 30 open. See
`docs/research/g2-thread-input-dependency-boundary.md`.

`platform\service\message_notify\service_android_notify.c` is now closed as
five functions / 972 body bytes / 1,104 physical bytes. Its 65 external calls
terminate at admitted EasyLogger and IAR DLIB edges plus the closed
ANCC/profile/whitelist/sync providers. Its flagged embedded JSON-parser
candidate, shared with service_whitelist.c, is resolved by the DaveGamble
cJSON identification below. The frontier is now 205 closed / 29 open. See
`docs/research/g2-service-android-notify-dependency-boundary.md`.

`platform\device_mgr\device_mgr.c` is now closed as 20 functions / 2,484
body bytes / 2,756 physical bytes. Its ten exact CMSIS-FreeRTOS calls span
osThreadNew/Terminate, osDelay, osTimerNew/Start, and
osMessageQueueNew/Put/Get, plus one FreeRTOS kernel xTaskGetTickCount;
remaining edges are admitted EasyLogger and bounded IAR DLIB. The frontier
is now 206 closed / 28 open. See
`docs/research/g2-device-mgr-dependency-boundary.md`.

`platform\service\evenAI\service_even_ai.c` is now closed as nine functions
/ 1,984 body bytes / 2,126 physical bytes. Its 124 external calls terminate
at admitted EasyLogger, one exact CMSIS-FreeRTOS tick wrapper, and bounded
IAR DLIB edges; explicit negative evidence records no embedded AI or NN
library body. The frontier is now 207 closed / 27 open. See
`docs/research/g2-service-even-ai-dependency-boundary.md`.

`app\gui\common\ui_common_api.c` is now closed as nine functions / 892 body
bytes / 960 physical bytes. Its 41 external calls terminate at admitted
EasyLogger and bounded IAR DLIB edges only. The frontier is now 208 closed /
26 open. See `docs/research/g2-ui-common-api-dependency-boundary.md`.

`app\gui\sync_info\sync_info.c` is now closed as three functions / 780 body
bytes / 860 physical bytes. Its 55 external calls terminate at admitted
EasyLogger, the admitted nanopb runtime, and bounded IAR DLIB edges only.
The frontier is now 209 closed / 25 open. See
`docs/research/g2-sync-info-dependency-boundary.md`.

`app\gui\dashboard\dashboard.c` is now closed as 24 functions / 10,040 body
bytes / 10,856 physical bytes. Its 598 external calls terminate at admitted
LVGL, EasyLogger, IAR DLIB, CMSIS-FreeRTOS, and nanopb sources plus
first-party dashboard providers. The frontier is now 210 closed / 24 open.
See `docs/research/g2-dashboard-dependency-boundary.md`.

`app\gui\dashboard\dashboard_layout.c` is now closed as eleven functions /
2,162 body bytes / 2,332 physical bytes. Its 87 external calls terminate at
admitted EasyLogger and IAR DLIB edges plus first-party file-runtime
providers. The frontier is now 211 closed / 23 open. See
`docs/research/g2-dashboard-layout-dependency-boundary.md`.

`app\gui\terminal\terminal_session_list_ui.c` is now closed as ten functions
/ 1,966 body bytes / 2,168 physical bytes. Its 131 external calls terminate
at admitted LVGL and EasyLogger sources plus first-party terminal providers.
The frontier is now 212 closed / 22 open. See
`docs/research/g2-terminal-session-list-ui-dependency-boundary.md`.

`app\gui\terminal\terminal_ui.c` is now closed as 99 functions / 13,200
body bytes / 14,040 physical bytes, the largest anchored object in the
campaign. Its 645 external calls terminate at admitted LVGL, EasyLogger,
IAR DLIB, and CMSIS-FreeRTOS sources plus first-party terminal providers.
The frontier is now 213 closed / 21 open, with 786,254 complete-object body
bytes and 854,600 known physical bytes. See
`docs/research/g2-terminal-ui-dependency-boundary.md`.

The zero-anchor `app\gui\AgingTest\aging_test.c` object is now closed as
five functions / 856 body bytes / 972 physical bytes, linked-unanchored with
identity from eight path references and three `[aging_test]` log tags. Its
boundary against the closed compress_log.c object is exact. The frontier is
now 214 closed / 20 open. See `docs/research/g2-aging-test-recovery.md`.

The zero-anchor `app\gui\anim\bounce_anim.c` object is now closed as seven
functions / 1,114 body bytes / 1,252 physical bytes, identified by eleven
path references and eleven `[bounce.anim]` tags across a two-phase bounce
animation lifecycle. The frontier is now 215 closed / 19 open. See
`docs/research/g2-bounce-anim-recovery.md`.

The zero-anchor `platform\device_mgr\box_uart_mgr.c` object is now closed as
five functions / 1,298 body bytes / 1,410 physical bytes, identified by
eleven path references and ten `[box_uart_mgr]` tags covering the
charging-box UART unpack/CRC/flush error paths. The frontier is now 216
closed / 18 open. See `docs/research/g2-box-uart-mgr-recovery.md`.

That object is now also production source-routed. Five guarded redirects replace
1,296 callable stock bytes with 514 selector-isolated Cortex-M55 text bytes,
four alignment bytes, and 21 strict relocations; the two-byte leading alignment
and 112-byte pool/data tail remain official. Host tests cover framing,
checksum rejection, receive-slot rotation, lifecycle, response, and failure
paths. Canonical overlay/component/package sizes are 332,666 / 3,856,062 /
4,634,556 bytes. Live case-UART electrical and interoperability validation is
blocked by unavailable physical evidence; future qualification requires authorized responsive temple/case evidence; no image
was signed or flashed.

The zero-anchor `app\gui\EvenAI\even_ai.c` object is now closed as seven
functions / 3,466 body bytes / 3,646 physical bytes: a detached 42-byte
lazy-singleton helper plus a six-block main cluster identified by fourteen
path references and fourteen `[even_ai.page]` tags. The frontier is now 217
closed / 17 open. See `docs/research/g2-even-ai-recovery.md`.

The zero-anchor `app\gui\anim\expand_anim.c` object is now closed as five
functions / 638 body bytes / 688 physical bytes, with four 32-byte callbacks
registered through its own trailing table cells. It shares its corpus gap
with the anchored conversate_ui_prep_note_page.c closure; the split is
exact and guard-pinned. The frontier is now 218 closed / 16 open. See
`docs/research/g2-expand-anim-recovery.md`.

The zero-anchor `kernel\FreeRTOS-Plus-CLI\prvCommand\prvCommand_filesystem.c`
object is now closed as twelve functions / 3,200 body bytes / 3,256 physical
bytes, identified by six path references and six `[prvCommand_filesystem]`
tags across copy/move, directory-walk, and statfs-style command bodies.
Sparse static ingress is recorded as a scanned fact, with registration
presumed dynamic through a runtime-built command table. The frontier is now
219 closed / 15 open. See
`docs/research/g2-freertos-plus-cli-filesystem-recovery.md`.

The zero-anchor `app\gui\MessageNotify\message_notify.c` object is now
closed as four functions / 1,016 body bytes / 1,100 physical bytes,
identified by five path references and five `[message_notify.page]` tags
with screen-descriptor registration. The frontier is now 220 closed /
14 open. See `docs/research/g2-message-notify-recovery.md`.

The zero-anchor `app\gui\MessageNotify\msg_notif_timer.c` path is now
attested linked-unanchored with zero additional body bytes: its six
referencing blocks were previously absorbed as unanchored rows into the
sibling ui_msg_notif_list closure, which this attestation re-verifies
byte-for-byte against the official image. The frontier is now 221 closed /
13 open. See `docs/research/g2-msg-notif-timer-recovery.md`.

The zero-anchor `app\gui\navigation\navigation.c` object is now closed as
five functions / 1,744 body bytes / 1,934 physical bytes, identified by ten
path references and nine `[navigation.main]` tags with screen-descriptor
registration. The frontier is now 222 closed / 12 open. See
`docs/research/g2-navigation-recovery.md`.

The zero-anchor `platform\product_test\product_common.c` object is now
closed as four functions / 686 body bytes / 760 physical bytes, identified
by six path references and six `[product_common]` tags covering the font
CRC validation routine; its boundary against production_mic_func.c is
exact. The frontier is now 223 closed / 11 open. See
`docs/research/g2-product-common-recovery.md`.

The zero-anchor `product\s200\app\config\board_config.c` object is now
closed as one function / 118 body bytes / 700 physical bytes: a
data-dominated object whose 582-byte trailing extent carries the s200
pinmux/peripheral board configuration constants. The frontier is now 224
closed / 10 open. See `docs/research/g2-s200-board-config-recovery.md`.

The zero-anchor `product\s200\app\config\main.c` object is now closed as
six functions / 1,504 body bytes / 1,530 physical bytes, identified by
fourteen path references and ten `[mainThread]` tags. It is a product
configuration/startup grab-bag: custom LVGL widget constructors, an init
hook, and the main thread body. The frontier is now 225 closed / 9 open.
See `docs/research/g2-s200-config-main-recovery.md`.

The zero-anchor `platform\input\service_gesture_processor.c` object is now
closed as five functions / 1,236 body bytes / 1,346 physical bytes,
identified by five path references and five `[touch.ges]` tags covering
proximity/slider gesture telemetry. The frontier is now 226 closed /
8 open. See `docs/research/g2-service-gesture-processor-recovery.md`.

The zero-anchor `app\gui\setting\setting.c` object is now closed as 18
functions / 5,486 body bytes / 5,772 physical bytes, the largest
zero-anchor object in the campaign, identified by 51 path references and
51 `[setting]` tags across universal unit setting and dominant-hand
ring-mac recovery. The frontier is now 227 closed / 7 open. See
`docs/research/g2-setting-recovery.md`.

The zero-anchor `app\gui\SystemAlert\systemAlert.c` object is now closed as
seven functions / 2,176 body bytes / 2,346 physical bytes, identified by
twelve path references and twelve `[system_alert]` tags with
screen-descriptor registration. The frontier is now 228 closed / 6 open.
See `docs/research/g2-system-alert-recovery.md`.

The zero-anchor `app\gui\system\system_monitor.c` object is now closed as
one function / 510 body bytes / 592 physical bytes: a single screen block
with six path references and six `[system_monitor]` tags whose descriptor
cell is the sole entry vector. The frontier is now 229 closed / 5 open.
See `docs/research/g2-system-monitor-recovery.md`.

The zero-anchor `app\gui\terminal\terminal_query_panel_ui.c` object is now
closed as six functions / 1,186 body bytes / 1,186 physical bytes; five
helper blocks are included by contiguity and terminal-cluster caller
evidence. The frontier is now 230 closed / 4 open. See
`docs/research/g2-terminal-query-panel-ui-recovery.md`.

The zero-anchor `app\gui\terminal\terminal_timer.c` object is now closed as
six functions / 624 body bytes / 724 physical bytes, identified by six path
references and six `[terminal.timer]` tags covering ASR-result and
voice-recording timeout management; one interleaved 16-byte foreign block
is pinned and not claimed. The frontier is now 231 closed / 3 open. See
`docs/research/g2-terminal-timer-recovery.md`.

The zero-anchor `app\gui\translate\translate_data.c` path is now attested
linked-unanchored with zero additional body bytes: the sole block carrying
its five literal references was previously absorbed as an unanchored row
into the sibling translate_ui closure, re-verified byte-for-byte against
the official image. The frontier is now 232 closed / 2 open. See
`docs/research/g2-translate-data-recovery.md`.

The zero-anchor `app\ux\ux_production\ux_production.c` object is now closed
as one function / 854 body bytes / 956 physical bytes, identified by ten
path references and ten `[ux.production]` tags covering device-sync test
and production command handling; dispatch is presumed dynamic and recorded
as a scanned fact. The frontier is now 233 closed / 1 open. See
`docs/research/g2-ux-production-recovery.md`.

The zero-anchor `app\ux\ux_settings\ux_settings.c` object is now closed as
two functions / 572 body bytes / 648 physical bytes, identified by seven
path references and seven `[ux.setting]` tags across time sync,
production-mode gating, and the device settings app. The retained-path
frontier is now 234 closed / 0 open: all 1,230 anchored functions and all
485,274 anchored body bytes are closed, with 814,534 complete-object body
bytes and 885,418 known physical bytes over 232 closure manifests; the
closed manifest ledger is
`aa5eb9142e1033f785771d6c81c5db41abf1d31ef5bb446b0354dca55553efd2`. No new
version or commit discriminator was found in any of the 53 closures. See
`docs/research/g2-ux-settings-recovery.md`.

### DaveGamble cJSON family identification

The cJSON-class JSON parser previously flagged as shared by
service_android_notify.c and service_whitelist.c is now identified as
DaveGamble cJSON, version interval v1.7.9--v1.7.12, from four binary
discriminators: the >=1.7.9 issue-315 get_object_item fix, the <1.7.13
buffer_skip_whitespace offset behavior, the absent <1.7.14
parse_array/parse_object head->prev tail store, and the <1.7.19 64-byte
stack parse_number buffer. The family is 21 functions / 2,572 body bytes at
`[0x004D798C,0x004D83D8)` with 34 external caller sites. This is the 26th
third-party family; it is identified but not yet source-admitted, and no
vendored snapshot exists. See
`docs/research/g2-json-parser-source-candidate-audit.md`.

### DaveGamble cJSON snapshot admission

The cJSON family is now admitted as an authenticated vendored snapshot. The
pristine MIT three-file closure (`cJSON.c`, `cJSON.h`, `LICENSE`) at
`g2/third_party/cJSON/` selects the interval-ceiling lightweight tag v1.7.12,
commit `3c8935676a97c7c97bf006db8312875b4f292f6c`, tree
`6c770a14e7d9ac1a8fd452a32c51fa4462cf2b45`, as the reproducible OpenCFW
baseline — not a claim about the vendor checkout or vendoring path, which
remain binary-unobservable. All 21 linked parse-side functions were
re-verified byte-identical C text between v1.7.9
(`f110bd2e585394bf47baca34a06df2569a9232b6`) and v1.7.12 during admission;
the whole-file tag diff is confined to the dead-stripped
print/create/edit/utils side. The fail-closed offline
`verify_snapshot.py` pins the commit/tree/interval identities, all three file
hashes and Git blob ids, and the explicit **production-excluded** decision:
the 21 functions / 2,572 body bytes at `[0x004D798C,0x004D83D8)` remain
cut-forward pending a compiler/ABI readiness matrix and a reviewed
production-overlay admission decision. `tests/test_cjson_snapshot.py` runs
the verifier, asserts the production-exclusion decision, and adds a
Cortex-M55 freestanding compile probe proving all six public entry sections.
The shared registry (`third-party/README.md`), upstream inventory, gap
priority, closure audit, and the machine-readable closure ledger
(`selected_source_commit`, residual gates, snapshot evidence) agree. No build
profile, ownership number, or package hash changed. See
`third_party/cJSON/README.openCFW.md` and
`third_party/cJSON/PROVENANCE.json`.

### Four-component controller-boundary evidence wave

A parallel four-lane evidence pass closed one bounded increment on each
non-Apollo component without touching production ownership:

- **EM9305 BLE controller** — the intermediate provenance pass classified all
  175 residual segments / 33,658 bytes (15.96% of the application) in
  `tools/manifests/em9305-residual-provenance-map.tsv`: 130 segments /
  30,564 bytes are proprietary modern-controller or EM vendor-system source
  (retention recommended), 7 / 1,224 bytes first-party Even application,
  2 / 980 bytes toolchain/linker-generated, and 36 / 890 bytes remain
  explicitly unclassified at that intermediate evidence stage. The final
  readiness composition in `tools/manifests/em9305-final-source-readiness.tsv`
  supersedes that intermediate state without rewriting it: all 175 spans are
  now typed as 23 / 1,240 bytes concrete source available, 25 / 8,348 bytes
  unsupported external boundary, and 127 / 24,070 bytes unavailable
  proprietary controller code, with zero unclassified spans or bytes. None is
  production-routed, so source completion is still false. The MetaWare runtime
  cluster is structurally proven; the authenticated first-party hook-table
  entries, QF internal-hook stubs, and the `MyApp` ID-181 assertion site are
  pinned. See
  `docs/research/em9305-residual-provenance-audit.md` and
  `tests/test_analyze_em9305_residual_provenance.py`.
- **Audio codec/DSP** — both FWPK segment destinations are conclusively
  resolved: the 38,236-byte type-1 boot image is the NationalChip grus
  (GX8002) UART-boot container (stage1 to IRAM `0x10000000`, stage2 to
  `0x10002800`), and the 287,808-byte type-2 BINH main image targets codec
  SPI NOR offset 0 as a dual-firmware concatenation (image A
  `[0x0,0x2F3B0)` with 36,484 bytes XIP text and a 129,964-byte NPU/audio
  payload; image B `[0x2F3B0,0x46440)`); all CRCs, version chains, and the
  `serialdown 0 <size> 8192` flash command are verified. The image remains
  an explicit proprietary NationalChip boundary. See
  `docs/research/g2-codec-fwpk-segments-recovery.md` and
  `tests/test_analyze_g2_codec_fwpk_segments.py`.
- **Touch controller** — identity is proven: Infineon/Cypress PSoC 4000T
  OPN CY8C4046FNI (Cortex-M0+, 64 KiB flash, 8 KiB SRAM, 5th-gen CapSense
  MSCLP0), with every LDR-confirmed peripheral base an exact psoc4000t SVD
  block base and the retained host path `driver\touch\drv_cy8c4046fni.c`.
  A complete ten-region memory map, the polled single-handler vector model,
  FWPK type-3 framing, and the CRC-32C record and trailing-payload checksums
  (hardware-instruction-verified) are pinned. See
  `docs/research/g2-touch-identity-recovery.md` and
  `tests/test_analyze_g2_touch_identity.py`.
- **Charging case** — STM32G0Bx-class (leading STM32G0B1) is established
  from the 46-word vector table and bank-swap literals; FreeRTOS V10-line
  GCC ARM_CM0 port is instruction-matched against upstream V10.5.1 port.c
  with kernel statics pinned; STM32CubeG0 HAL/LL module presence is
  separated from G2 policy; the `5A A5 FF` UART framing and the 22-step
  OTA-box state machine (including Copy-SN) are mapped; four
  device-specific SN preservation windows are pinned as never-overwrite
  regions. See `docs/research/g2-box-stm32g0-platform-recovery.md` and
  `tests/test_analyze_g2_box_stm32g0_platform.py`.

All four lanes added fail-closed analyzers, machine-readable manifests, and
tests (42 focused tests, all passing). No build profile, ownership number,
or package hash changed; all four components remain retained behind their
declared boundaries.

### Second frontier wave: controller-cluster decompilation, codec stage2, touch protocol, case function map, Apollo unanchored census

- **EM9305 BLE controller** — the two largest high-confidence
  modern-controller clusters are now function-recovered via the
  lorelei GNU ARC lane (Ghidra ARC skipped per benchmark guidance):
  slave-connection `[0x00329888,0x0032A4BE)` and master periodic
  scan/PAwR `[0x00321C30,0x0032233C)`, ten functions / 4,930 bytes with
  an exact zero-remainder tiling, bracket-anchored against authenticated
  Packetcraft object boundaries. Three functions are opcode-exact, five
  modified (ratios 0.89–0.97), two divergent — sharpening the
  proprietary-retention verdict: stock is a newer/differently-configured
  Packetcraft build whose authoritative source is unavailable. The lane
  return is manifested at `research/corpus/em9305/cluster-recovery/`.
  See `docs/research/em9305-controller-cluster-recovery.md`.
- **Audio codec/DSP** — image-A stage2 is conclusively sectioned using
  the official `c-sky/binutils-gdb` fork (GNU 2.43.1 proven to mis-decode
  32-bit forms): 36,484 B XIP text, 12,516 B SRAM text at
  `0x10023400`, and 2,196 B SRAM data, with the combined copy closing
  exactly on `stage2_size − xip_len`. The entire 129,964 B payload is
  the LVP_KWS wake-word model: command stream `[0xF804,0x11BD0)` and
  weights `[0x11BD0,0x2F3B0)`, exact-fit to image B. See
  `docs/research/g2-codec-stage2-sections-recovery.md`.
- **Touch controller** — the SCB1 I2C protocol is closed: a 9-slot
  command switch (version/ID query, prox-baseline read/save, threshold
  read, gesture-config write, enter-DFU, sensor report), active-low
  attention line, 16 B report format, deferred EEPROM config with `UNVE`
  magic, and power entries. Architecturally decisive: the payload is the
  shipped prefix `[0,0x8680)` of a base-0 image whose resident remainder
  owns the DFU engine and boot — touch OTA depends on factory-matched
  resident flash. See `docs/research/g2-touch-i2c-protocol-recovery.md`.
- **Charging case** — a full lorelei Ghidra function map (428 functions
  / 40,664 bytes) attributes the image: 79 FreeRTOS-kernel functions /
  5,440 B (CMSIS-RTOS2 wrapper identified), 10 STM32 HAL functions /
  1,018 B, 71 first-party G2 functions, 261 unresolved helpers. Both
  open questions answered: frame checks are additive sums (no polynomial
  CRC), and logging uses direct ADR/LDR string pointers (no ID scheme).
  See `docs/research/g2-box-function-map-recovery.md`.
- **Apollo unanchored census** — the 5,610-function unanchored set is
  re-derived exactly (7,370 corpus − 1,760 anchored) and triaged with
  zero drift against the origin accounting: 27% was already reviewed by
  per-module manifests; the unreviewed core is 1,911 functions /
  299,736 bytes. Buckets pin first-party (1,782/216,564 B), LVGL
  (1,054/97,430 B), Cordio (383/27,356 B), and the smaller families;
  new identifications include the IAR DLIB formatted-I/O cluster
  (printf core `0x00481836`, scanf core `0x004D1638`) and byte-exact
  cross-validation of `FT_Done_Face`. See
  `docs/research/g2-apollo-unanchored-census.md`.

All five lanes added fail-closed analyzers, manifests, and tests (52
focused tests passing). The corpus index grew to 1,950 files / 44
manifests (EM9305 cluster-recovery lane). No build profile, ownership
number, or package hash changed; all controller components remain
retained behind their declared boundaries.

## G2 Goodix-derived application-error handler is production-routed

The exact GR551x SDK 1.7.0-derived diagnostic policy is now implemented by the
clean-room `components/apollo_main/core_overlay/util_error_check.c`. Its one
254-byte relocated leaf replaces the 178-byte stock handler at
`[0x00509B48,0x00509BFA)` and closes over the retained authenticated 43-row
table plus the recovered memset, formatter, and EasyLogger providers. The
reviewed local delta bounds the table search and maps unknown API codes to the
retained `Application error.` row instead of preserving the stock unbounded
walk.

The host oracle and freestanding Thumb closure tests pass, the analyzer pins
all eight provider relocations and the redirect, and source package assembly
and verification pass. Canonical Apollo accounting is 165,094 source-owned
bytes, 121,098 generated patch-site bytes, 32 wrapper bytes, 182 in-place
source bytes, and 3,402,084 opaque base bytes. No hardware operation was
performed; device-dependent qualification is blocked by unavailable physical evidence and
future qualification requires the specified physical evidence.

## FreeRTOS `vTaskGetInfo` closes the task/queue-private ledger row

The complete authenticated V10.5.1 `vTaskGetInfo` body at
`[0x00455728,0x004557A8)` is now redirected to a 120-byte source leaf at
`0x007BC6DC`. Static assertions pin the G2 TCB and `TaskStatus_t` layouts, and
the only four relocations target already source-owned FreeRTOS providers.
Focused host behavior, stock-span, routing, component, manifest, package, and
origin-accounting checks pass.

Current component accounting is 165,094 source-owned bytes, 121,098 generated
patch-site bytes, 32 generated wrapper bytes, 182 in-place source bytes, and
3,402,084 opaque base bytes. The Apple overlay/component/package identities are
`164912/3688308/4466802` bytes with SHA-256 values
`8c65ebb25586f80cc4eaec62fd9442c0dc28a37a897fec7349822d980cc767e0`,
`4dea653f6001fc9cf287253481ab412d9046a590bc70707fadce6afb01307b09`, and
`03292baa960e39beb368b32a0b93f3f68d13caf6db121a2bb6020363c366afa0`.
No hardware operation was performed.

## G2 system-monitor peer-reboot callback is production-routed

The descriptor-only `app\\gui\\system\\system_monitor.c` callback is now
implemented by `open_cfw_system_monitor_common_data_handler`. Its one
650-byte strict-relocation leaf replaces all 510 authenticated stock body bytes
at `[0x00584EE4,0x005850E2)` while retaining descriptor ingress at
`0x006A4674`. The clean-room source validates the six-byte reboot sentinel,
quiesces foreground/background display work, enforces the stock eleven-by-100
tick wait bound, sends master-side scheduler idle, and executes all five reset
and publication providers. NULL and short payloads are rejected before the
stock body's unchecked byte reads.

Focused behavior, Thumb surface, 43-relocation, routing, component, manifest,
and package tests pass. Canonical Apple overlay/component/package identities
are `166090/3689486/4467980` bytes and
`1120724b...43e8` / `18e578a6...d05f` / `a643e0fd...e11e9`.
On-device paired-reboot/display/scheduler qualification is blocked by unavailable physical evidence; future qualification requires authorized physical hardware.

## G2 health mutex/common-event object is production-routed

The four authenticated functions in `app\\gui\\health\\health.c` are now
implemented in clean-room freestanding C and routed through four guarded
full-span redirects. The Apple overlay adds 198 compiled bytes and replaces
504 stock bytes. Focused host tests cover mutex creation, lock/unlock, event
validation, provider dispatch, lens/display gates, and service-one record
posting; the target compile proves exactly four global Thumb text symbols.

Canonical Apple overlay/component/package identities are
`166292/3689688/4468182` bytes and
`a3de5492...958d` / `eb0e6c9b...53fb` / `0c1548c6...57d4`.
Accounting closes at 166,474 source-owned, 122,648 generated patch-site,
122,826 replaced stock-function, and 3,400,534 opaque base bytes. No hardware
operation was performed. On-device concurrency, role/display selection,
transport delivery, and visible health behavior are deferred by project
direction; future qualification requires the specified physical evidence. This
does not declare overall G2 completeness.

## Cordio `dm_sec_lesc` security unit is production-routed

All seven live LE Secure Connections functions are now compiled from the
admitted Packetcraft r20.05c Apache-2.0 behavior and routed through guarded
full-span redirects. Host tests cover ECC/OOB events, buffer lifetime, key
storage, compare-response allocation/cancel paths, formatting, and interface
registration; the Thumb gate exposes exactly seven text symbols and the route
analyzer pins all ten relocations.

Canonical Apple overlay/component/package identities are
`166576/3689972/4468466` bytes and
`1f5c6afe...1cff` / `9ca58f6d...7ff2` / `eb2d45ac...2985`.
No hardware operation was performed. Pairing/controller timing, pool pressure,
disconnect races, and peer interoperability remain explicitly blocked by
future-required authorized G2/EM9305 physical evidence. The overall security and
firmware ledgers remain incomplete.

## Cordio `dm_sec` security core is production-routed

All eight live security-core functions are compiled from the admitted
Packetcraft r20.05c Apache-2.0 behavior and routed through guarded full-span
redirects. Host tests cover HCI/message LTK paths, LESC rejection, STK fallback,
busy/idle transitions, encryption callback ordering, authentication allocation
and truncation, initialization, key accessors, and reset. The Thumb gate exposes
exactly eight text symbols and the route analyzer pins all 19 relocations.

Canonical Apple overlay/component/package identities are
`167088/3690484/4468978` bytes and `63a2dab6...81ca` /
`1f4e39b3...6e19` / `edd49b59...1c5b`. No hardware operation was performed.
Controller timing, allocation pressure, disconnect races, callback ordering,
and legacy/LESC peer interoperability is blocked by unavailable physical evidence; future qualification requires authorized G2/EM9305 evidence. `dm_sec_slave` and `dm_sec_master`, the broader
security ledger, and the firmware as a whole remain incomplete.

## Cordio `dm_sec_slave` and `dm_sec_master` roles are production-routed

All six live role functions are compiled from the admitted Packetcraft
r20.05c Apache-2.0 behavior and routed through guarded full-span redirects.
Host tests cover allocation failures, pair/security/LTK request and response
ABI, key-distribution masking, present/absent keys, CCB state, non-LTK
selection, and zero-Rand/EDIV encryption start. The Thumb gate exposes exactly
six text symbols and the two route analyzers pin all 14 relocations.

Canonical Apple overlay/component/package identities are
`167426/3690822/4469316` bytes and `303539d4...e9b9` /
`e6a69ad6...1fb4` / `39a4702c...d975`. No hardware operation was performed.
Role-specific controller timing, message ownership, disconnect races, callback
behavior, and peer interoperability is blocked by unavailable physical evidence; future qualification requires authorized G2/EM9305 evidence. The broader SMP/application-policy/cryptographic
security rows and the firmware as a whole remain incomplete.

## Cordio `smp_db` pairing database is production-routed

All eleven linked database functions are compiled from authenticated
Packetcraft r20.05c Apache-2.0 definitions while preserving the G2 ten-record
override and r20 service event. Eleven guarded redirects replace 2,952 stock
bytes with 698 compiled Thumb bytes plus 14 alignment bytes. Five host
contracts cover initialization, peer allocation/reuse, common-record fallback,
failure timers, exponential backoff/clamping, pairing-failure refresh, and
saturating service ticks; the analyzer pins all production routes.

Canonical Apple overlay/component/package identities are
`168138/3691534/4470028` bytes and `c58ed4eb...4a0e0` /
`bafeba34...d1487` / `d563e568...6b4b`. No hardware operation was performed.
WSF scheduling, controller disconnect races, repeated-attempt timing, and peer
interoperability is blocked by unavailable physical evidence; future qualification requires authorized physical
evidence. The remaining SMP state/action units, application policy,
cryptographic backend, and firmware as a whole remain incomplete.

## Cordio `smp_main` is production-routed

All twenty linked functions now route to authenticated Packetcraft r20.05c
behavior with the Ambiq stale-AES queue cleanup, and the private packet-length
helper is source-owned as a twenty-first leaf. The overlay emits 2,146 Thumb
text bytes plus 24 alignment bytes and replaces all 3,076 stock bytes. Six host
contracts cover initialization/lookups, connection lifecycle, retry timers,
L2CAP validation/queueing, legacy crypto, LTK/STK/LESC access, handler dispatch,
and stale queue cleanup.

Canonical Apple overlay/component/package identities are
`170308/3693704/4472198` bytes and `72d355eb...c3bc` / `bb4d2ee1...08f3` /
`aa849dcd...9202`. The component owns 170,490 source bytes, 129,652 generated
patch-site bytes, and 3,393,530 opaque base bytes. No hardware operation was
performed. Controller timing, disconnect races, pairing/reconnect, peer
interoperability, and stale-AES behavior remain explicitly blocked by
future-required authorized G2/EM9305 physical evidence; no completeness claim is
made.

## Cordio `smp_sc_main` is production-routed

All eighteen linked Secure Connections support functions now route to
authenticated Packetcraft r20.05c behavior through eighteen guarded leaves.
The overlay emits 2,278 Thumb text bytes plus 452 bytes of event-string rodata
and alignment closure, replacing all 2,626 authenticated stock body bytes.
Six host contracts cover scratch lifetime, allocation and CMAC cancellation,
F4 inputs, all four pairing PDUs, passkey bits, repeated-attempt behavior, and
diagnostics. The byte-array logger also fixes the upstream short-final-line
stall by consuming the actual remaining count.

Canonical Apple overlay/component/package identities are
`173038/3696434/4474928` bytes and `10fb4ab6...6eb9` /
`aae37afd...cb28` / `a79d1096...42a`. The component owns 173,220 source
bytes (including 182 in place), 132,278 generated patch-site bytes, 32 wrapper
bytes, and retains 3,390,904 opaque bytes. No hardware operation was performed.
Public-key/DH-check/passkey/OOB/reconnect/repeated-attempt controller and peer
validation is blocked by unavailable physical evidence; future qualification requires authorized G2/EM9305 physical
evidence. Remaining SMP action/state units and the firmware as a whole remain
incomplete.

## Protobuf health service is production-routed

The complete eight-entry `pb_service_health.c` object now routes to clean-room
C, backed by a ninth bounded protobuf buffer callback. Host tests cover all RX
success/failure/null mappings, all four TX command/tag envelopes, nanopb encode
failure, send arguments, compact highlight expansion, and rejection above the
three-record retained-message capacity. The analyzer authenticates all 3,092
stock body bytes, nine placements, and twenty strict relocations.

The service adds 940 compiled bytes plus eight alignment bytes. Canonical
Apple overlay/component/package identities are `184522/3707918/4486412` bytes
and `f2e2771d...6a43` / `a2c628bb...aafc` / `34e82939...8936`; the flash plan
is 1,836,839 bytes with SHA-256 `d4c0b6b3...fe139`. No hardware was accessed or
flashed. Live scheduler/transport timing, BLE delivery, phone/schema
interoperability, and persisted device-data validation remain explicitly
is blocked by unavailable physical evidence; future qualification requires authorized G2/EM9305 physical evidence. Other health UI
and algorithm-provider rows, broader protobuf services, and the firmware as a
whole remain incomplete.

## Cordio `smp_act` common actions are production-routed

All 25 linked Packetcraft `smp_act.c` functions now execute source-owned
r20.05c behavior. Twenty-four guarded redirects replace their complete stock
bodies; `smpActNone` is compiled to its exact two-byte stock encoding and
placed in situ. Six host contracts cover timers/cleanup, failures and timeout,
pairing/authentication, legacy confirmation, key distribution, attempt
lockout/completion, and dispatcher behavior. The target and route gates pin all
compiled functions, relocations, patch spans, and the narrowly reviewed
halfword-placement case.

The unit contributes 1,758 compiled bytes plus 20 alignment bytes and replaces
all 2,924 authenticated stock function bytes. Canonical Apple
overlay/component/package identities are `174816/3698212/4476706` bytes and
`b732d58c...f6bf` / `125cfeb1...55f3` / `26bf3d84...5058`; the flash plan is
1,480,138 bytes with SHA-256 `cec97a55...6a4`.

No hardware was accessed, signed for, or flashed. Legacy and Secure
Connections pairing, key distribution, timeout, cancellation, and
repeated-attempt controller/peer behavior remain explicitly blocked by
future-required authorized G2/EM9305 physical evidence. The remaining Secure
Connections action/state units and the firmware as a whole remain incomplete.

## Health data manager is production-routed

All ten authenticated `health_data_manager.c` entries now route to clean-room
production C. Host contracts cover type/slot/name mapping, full storage reset,
normal and highlight protobuf conversion, single and counted saves, truncation,
invalid/null input policy, and five-highlight capacity. The strict target gate
exposes exactly ten text symbols and the route analyzer pins fifteen external
relocations, ten complete stock spans, appended placement, component tiling,
and package identity.

The tranche replaces 2,644 stock bytes with 1,012 compiled bytes plus ten
alignment bytes. Canonical Apple overlay/component/package identities are
`183574/3706970/4485464` bytes and `c3f1e141...92947` /
`f453571d...ef32d` / `37a5607c...3b001`; the flash plan is 1,818,542 bytes
with SHA-256 `bb761c34...60365`. No hardware was accessed or flashed. Live
mutex scheduling, concurrent service traffic, persistence, schema/peer
interoperability, and display/device-data behavior remain explicitly blocked
by future-required authorized G2/EM9305 physical evidence. The protobuf health
service, health UI, broader firmware ledger, and firmware as a whole remain
incomplete.

## eAT touch-panel command is production-routed

The complete retained `platform/service/eAT/at_tp.c` object now routes to two
selector-isolated clean-room C leaves. The implementation preserves all eight
commands, the stock successful acknowledgement path (including unknown
non-null subcommands), baseline-save sequencing, the 100 ms configuration
readback delay, and distinct provider failure responses. It adds a fail-closed
null guard and bounded decimal parser. Nine host/analyzer tests cover the
software contract.

The tranche replaces all 1,040 stock object bytes with 1,548 compiled bytes
plus two alignment bytes and authenticates eighteen relocations. Current
Apple overlay/component/package identities are `193488/3716884/4495378` bytes
and `212bd4fe...3460` / `6803b1a9...e65d` / `86901153...b7f2`; the
flash plan is 1,946,868 bytes with SHA-256 `f06aee5a...fc42`. No hardware was
accessed or flashed. Live Cypress-controller, proximity-baseline persistence,
threshold write/readback, and physical gesture behavior remain explicitly
is blocked by unavailable physical evidence; future qualification requires authorized G2 touch-panel evidence. The firmware as a
whole remains incomplete.

## Gesture-processing service is production-routed

All five recovered `service_gesture_processor.c` functions now route to
selector-isolated clean-room C. Host contracts cover proximity and event-name
access, the complete mask formatter, production-mode buzzer feedback,
proximity notification, error preemption/reset, every event bit, event order,
and the single-click thresholds. The production analyzer pins the five final
leaf hashes, 53 relocations, five complete stock redirects, and the component,
manifest, package, and flash-plan ownership chain.

The tranche replaces all 1,346 stock object/pool bytes with 1,608 compiled
Thumb bytes plus six alignment bytes. Canonical Apple
overlay/component/package identities are `193488/3716884/4495378` bytes and
`212bd4fe...3460` / `6803b1a9...e65d` / `86901153...b7f2`; the flash plan
is 1,946,868 bytes with SHA-256 `f06aee5a...fc42`. Apollo main now accounts
for 193,950 source-owned bytes, 153,832 generated patch-site bytes, 154,012
replaced stock-function bytes, and 3,367,148 opaque base bytes.

No hardware was accessed or flashed. Live touch/proximity electrical behavior,
controller event delivery, debounce, timing, and physical gesture
interpretation is blocked by unavailable physical evidence; future qualification requires authorized G2
evidence. The firmware as a whole remains incomplete.

## CY8C4046FNI host touch driver is production-routed

All 23 recovered `drv_cy8c4046fni.c` executable entries now route to
selector-isolated clean-room C. Host contracts cover the HAL I2C ABI,
command/return semantics, callback-table installation, reset and DFU control,
touch-frame and difference reads, proximity-baseline operations, gesture
configuration, and exact 23-way selector isolation. The production analyzer
pins 19 relocations, 23 complete stock-body redirects, retained callback-pool
ownership, component tiling, manifest ownership, package identity, and the
hardware blocker.

The tranche replaces all 1,754 stock function bytes with 1,122 compiled Thumb
bytes plus 18 alignment bytes while retaining the directly addressed 170-byte
stock callback/string pool. Stock EasyLogger paths are intentionally omitted
as non-controlling observability; command, state, buffer, return-value, reset,
DFU, and delay behavior remains implemented. Canonical Apple
overlay/component/package identities are `193488/3716884/4495378` bytes and
`212bd4fe...3460` / `6803b1a9...e65d` / `86901153...b7f2`; the flash plan
is 1,946,868 bytes with SHA-256 `f06aee5a...fc42`.

No hardware was accessed or flashed. Physical I2C signaling, reset/DFU boot
transitions, settling time, report timing, and CapSense behavior are
blocked by unavailable physical evidence; future qualification requires authorized G2 hardware and capture evidence.
The firmware as a whole remains incomplete.

## Packetcraft Cordio GATT profile is production-routed

All six linked functions from the copied Cordio `gatt_main.c` object now route
to selector-isolated Apache-2.0 production C over the recovered G2 ABI. Host
contracts cover discovery, value updates, service-changed index and indication
routing, CCC gating, and client-supported-feature reads/writes. The production
analyzer pins six complete stock redirects, ten strict relocations, the
retained literal pool, exact r20.05c source provenance, component tiling,
manifest ownership, package identity, and the hardware blocker.

The tranche replaces all 322 stock body bytes with 254 compiled Thumb bytes
plus eight alignment bytes. Canonical Apple overlay/component/package
identities are `193488/3716884/4495378` bytes and `212bd4fe...3460` /
`6803b1a9...e65d` / `86901153...b7f2`; the flash plan is 1,946,868 bytes with
SHA-256 `f06aee5a...fc42`.

No hardware was accessed or flashed. Physical ATT discovery, CCCD state,
indication delivery, controller timing, and peer interoperability are
blocked by unavailable physical evidence; future qualification requires authorized G2/EM9305 evidence. The firmware
as a whole remains incomplete.

## G2 BLE OTA profile is production-routed

All seven linked `profile_ota.c` functions now route to selector-isolated
BSD-3-Clause C over the recovered G2 control-block and message ABIs. Host
contracts exercise the exact CCC layout, connection and role transitions,
events `0x12`, `0x14`, `0x27`, `0x28`, `0xA0`, `0xA1`, and `0xA7`, reset and
delayed disconnect requests, allocation failure, transport forwarding, and
ATT notification handle `0x0824`. The production analyzer pins the seven
source leaves, seventeen strict relocations, seven complete stock redirects,
the retained 80-byte literal/callback pool, manifest tiling, package identity,
and the physical blocker.

The tranche replaces all 620 stock body bytes with 376 compiled Thumb bytes
plus eight alignment bytes. Apollo main now accounts for 194,596 source-owned
bytes, 154,774 generated patch-site bytes, 154,954 replaced stock-function
bytes, and 3,366,206 opaque base bytes in the 3,715,608-byte component.
Canonical Apple overlay/component/package identities are
`193488/3716884/4495378` bytes and `212bd4fe...3460` /
`6803b1a9...e65d` / `86901153...b7f2`; the 1,963,573-byte flash plan hashes
to `f06aee5a...fc42`.

No hardware was accessed or flashed. OTA CCC, reset, disconnect, notification
timing, and peer interoperability is blocked by unavailable physical evidence; future qualification requires authorized G2/EM9305 evidence. The broader firmware software ledger remains
incomplete.

## G2 BLE Ring profile is production-routed

All seven linked `profile_ring.c` functions now route to selector-isolated
MIT clean-room C over the recovered control-block and message ABIs.
Host contracts exercise handler initialization, service discovery, 16-bit
epoch cancellation, the 500/700/900 delayed CCC sequence, connect/close
transitions, ATT RX forwarding, TX command and queue paths, allocation failure,
and all seven selectors. The production analyzer pins 23 strict relocations,
seven complete stock redirects, the retained 134-byte callback/literal pool,
manifest tiling, package identity, and the physical blocker.

The tranche replaces all 1,446 stock body bytes with 632 compiled Thumb bytes
plus eight alignment bytes. After the subsequent callback-facade closure,
Apollo main accounts for 195,444 source-owned bytes, 156,600 generated
patch-site bytes, 156,780 replaced stock-function bytes, and 3,364,380 opaque
base bytes in the 3,716,462-byte component.
Canonical Apple overlay/component/package identities are
`193488/3716884/4495378` bytes and `212bd4fe...3460` /
`6803b1a9...e65d` / `86901153...b7f2`; the 1,963,573-byte flash plan hashes
to `f06aee5a...fc42`.

No hardware was accessed or flashed. Service discovery, delayed CCC timing,
ATT handle behavior, controller concurrency, and peer interoperability are
blocked by unavailable physical evidence; future qualification requires authorized G2/EM9305 evidence. The OTA/Ring
profile pair has no remaining software gap; the firmware as a whole remains
incomplete.

## Charge and message callback facades are production-routed

All ten linked entries from `cb_charge.c` and `cb_msg_notif.c` now route to
selector-isolated MIT clean-room C. Host contracts cover both fixed
callback lists and retained type identities, init/deinit, null-checked
register/unregister, provider return propagation, and the notification in/out
value word. The fail-closed analyzer pins ten strict relocations, ten complete
stock redirects, both retained 34-byte diagnostic/type pools, component
tiling, manifest ownership, package identity, and flash-plan generation.

The tranche replaces 380 stock body bytes with 208 compiled Thumb bytes plus
six alignment bytes. Apollo main now accounts for 195,444 source-owned bytes,
156,600 generated patch-site bytes, 156,780 replaced stock-function bytes, and
3,364,380 opaque base bytes. Canonical Apple overlay/component/package
identities are `193488/3716884/4495378` bytes and `212bd4fe...3460` /
`6803b1a9...e65d` / `86901153...b7f2`; the 1,963,573-byte flash plan hashes
to `f06aee5a...fc42`.

These wrappers introduce no direct hardware operation, so their functional
semantics are closed without a physical-evidence claim. The broader firmware
ledger remains incomplete.

## Generic callback manager is production-routed

The shared eight-function `callback_manager.c` provider now compiles from
selector-isolated MIT clean-room C. Host contracts cover allocation
failure, null validation, duplicate-success behavior, prepend order,
head/interior removal, full deinitialization, and ordered two-argument callback
dispatch. Eight guarded redirects replace 1,240 stock body bytes with 408
compiled bytes plus 14 alignment bytes; six strict relocations terminate at
source-owned heap wrappers or the manager's redirected helper entries.

Apollo main now accounts for 195,872 source-owned bytes, 157,840 generated
patch-site bytes, 158,020 replaced stock-function bytes, and 3,363,140 opaque
base bytes. Canonical Apple overlay/component/package identities are
`193488/3716884/4495378` bytes and `5248973d...f7cc` /
`53ac8a34...0575` / `a651c50d...65a8`; the 1,963,573-byte flash plan hashes
to `85ec1cd1...3d5`. No hardware operation is introduced by this pure
in-memory manager, so its software functional gap is closed without a
physical-evidence claim. The overall G2 ledger remains incomplete.

## Ring-battery callback facade is production-routed

All five linked entries from `cb_ring_battery.c` now route to
selector-isolated MIT clean-room C. Five guarded redirects replace all
122 stock body bytes with 88 compiled Thumb bytes plus two alignment bytes;
five strict relocations bind only to the source-owned generic callback manager
and the retained ring-battery consumer. The authenticated 30-byte type,
diagnostic, path, and literal pool remains official data.

Apollo main now accounts for 195,962 source-owned bytes, 157,962 generated
patch-site bytes, 158,142 replaced stock-function bytes, and 3,363,018 opaque
base bytes. Canonical overlay/component/package identities are
`193578/3716974/4495468` bytes with SHA-256 values
`a4c7927efe625a95e3bd928e5bb75b32c057837577dd9b9bf0cc3a5c19a42183`,
`026ba2cc0c5f4dd5ca052b630edd3bbbae8addd95b53f7bd0b16c0ebb40c316a`,
and `03d4b3f7813ce41814ae821ccbdaa3a1f2802fe4a459cf20351487a18332e783`.
The 1,972,280-byte flash plan hashes to
`ef7a204c200024422defd2cb9e0064a5aa4278bb14533e4007bd0daf2db1e67f`.
This pure facade has no independent hardware-validation tail. The broader ring
service and overall firmware remain incomplete.

## UX battery-sync callback is production-routed

The service-record `0x105` handler now compiles from clean-room C. One guarded
redirect replaces all 836 stock body bytes with 158 compiled Thumb bytes plus
two alignment bytes; eleven strict relocations bind to bounded charger,
ring-battery, and callback providers. Host tests exercise validation and all six
message IDs. Apollo main now contains 196,122 source-owned bytes and 3,362,182
opaque base bytes. Canonical overlay/component/package SHA-256 values are
`a4c7927efe625a95e3bd928e5bb75b32c057837577dd9b9bf0cc3a5c19a42183`,
`026ba2cc0c5f4dd5ca052b630edd3bbbae8addd95b53f7bd0b16c0ebb40c316a`,
and `03d4b3f7813ce41814ae821ccbdaa3a1f2802fe4a459cf20351487a18332e783`.
Physical peer/charger/ring validation is blocked by unavailable physical evidence; future qualification requires authorized
hardware evidence; the wider firmware remains incomplete.

## Ring-battery state service is production-routed

All five `service_ring_battery.c` entries now compile from selector-isolated
clean-room C. Host contracts exercise cached-state clamping and normalization,
both getters, the 12-byte message ABI, local type-5 update, peer type-6 request,
and service ID `0x105`. Five exact redirects replace 352 stock body bytes with
134 compiled Thumb bytes plus four alignment bytes; two strict relocations bind
only to the bounded local and peer service-record transports. The 44-byte
diagnostic/path pool remains authenticated official data.

Apollo main now accounts for 196,260 source-owned bytes, 159,150 generated
patch-site bytes, 159,330 replaced stock-function bytes, and 3,361,830 opaque
base bytes. Canonical overlay/component/package sizes are 193,876 / 3,717,272 /
4,495,766 bytes with SHA-256 values
`a4c7927efe625a95e3bd928e5bb75b32c057837577dd9b9bf0cc3a5c19a42183`,
`026ba2cc0c5f4dd5ca052b630edd3bbbae8addd95b53f7bd0b16c0ebb40c316a`,
and `03d4b3f7813ce41814ae821ccbdaa3a1f2802fe4a459cf20351487a18332e783`.
The 1,985,178-byte deployment plan contains 2,825 placed regions and two
explicitly unresolved physical-evidence regions, and hashes to
`ef7a204c200024422defd2cb9e0064a5aa4278bb14533e4007bd0daf2db1e67f`.

No hardware was accessed. Paired-device transport, callback timing, and live
ring-state behavior is blocked by unavailable physical evidence; future qualification requires authorized physical evidence.
The service object's software gap is closed; the wider ring stack and firmware
remain incomplete.

## Protobuf Ring service is production-routed

All four linked `pb_service_ring.c` entries and the source-only bounded nanopb
output callback now compile from selector-isolated clean-room C. Four guarded
redirects replace 1,362 authenticated stock body bytes with 594 compiled Thumb
bytes plus four alignment bytes; nine strict relocations bind to source-owned
nanopb/BLE wrappers, redirected sibling entries, and recovered message globals.
The 150-byte official alignment/literal tail remains retained.

At the Ring-service stage Apollo main accounted for 197,414 source-owned bytes,
161,872 generated patch-site bytes, 162,052 replaced stock-function bytes, and
3,359,108 opaque base bytes. After the subsequent glasses-case and conversate
service tranches, canonical overlay/component/package sizes are 196,136 /
3,719,532 / 4,498,026 bytes with SHA-256 values
`a4c7927efe625a95e3bd928e5bb75b32c057837577dd9b9bf0cc3a5c19a42183`,
`026ba2cc0c5f4dd5ca052b630edd3bbbae8addd95b53f7bd0b16c0ebb40c316a`,
and `03d4b3f7813ce41814ae821ccbdaa3a1f2802fe4a459cf20351487a18332e783`.
The 2,018,179-byte deployment plan contains 2,874 placed regions, two
unresolved protected regions, and five container-only regions; it hashes to
`ef7a204c200024422defd2cb9e0064a5aa4278bb14533e4007bd0daf2db1e67f`.

Host tests cover buffer bounds, null/error statuses, decoding, command/event
routing, MAC-count behavior, encoding, transport arguments, and relay dispatch.
No hardware was accessed for this tranche. Paired-G2 relay, nanopb peer
interoperability and live Ring-event qualification are blocked by unavailable physical evidence.
The historical evidence state is recorded in `hardware-validation-2026-08-23.md`.
The protobuf object's software gap is closed; the wider ring stack and firmware
remain incomplete.

## Even-AI protobuf service is production-routed

All 25 linked `pb_service_even_ai.c` entries and two bounded nanopb helpers now
compile from selector-isolated MIT clean-room C. Twenty-five guarded
redirects replace 8,404 authenticated stock body bytes with 2,832 compiled
Thumb bytes plus 36 alignment bytes. The 552 distributed official gap/literal
pool bytes remain retained, and 107 strict relocations bind only to recovered
nanopb, BLE, provider, role/display, and sibling-source interfaces. Host tests
cover receive lengths, replay suppression, all ten command/response envelopes,
three notifications, heartbeat/configuration semantics, failures, and all 27
selector builds.

At completion of this tranche, overlay/component/package identities were
200,356 / 3,723,752 / 4,502,246 bytes with SHA-256 values
`870c2c8f63e8fbbf985244e737889d1d81c1b36a804fbb3b4cfc0d9d84eacbcd`,
`dcebf2671aaba2b11f2cff92390bd2d09e18893c8f066acdc19c1cecc92b339e`,
and `94c152805feed6d142af105f069b301517c4157e60deee6a08423b3eba419a89`.
The 2,090,502-byte deployment plan had 2,984 placed regions, two unresolved
physical-evidence regions, and five container-only regions; its SHA-256 is
`eb05d1365e4b0481599d07a8a4b3afa94f529d8c1b57ff48c7093a7ba4392fca`.
Live service-7 master/peer BLE and Even-AI UI validation remain explicitly
is blocked by unavailable physical evidence; future qualification requires authorized physical evidence. The wider firmware
remains incomplete.

## Terminal protobuf service is production-routed

All thirteen linked `pb_service_terminal.c` entries and two bounded memory
helpers now compile from selector-isolated MIT clean-room C. Thirteen
guarded redirects replace all 2,554 authenticated stock body bytes with 1,368
compiled Thumb bytes plus eight alignment bytes. The authenticated 246-byte
literal tail remains official, and 23 strict relocations bind only to recovered
nanopb, BLE, tick, role, and sibling-source interfaces. Host tests cover RX
decode/status/replay behavior, every tag/payload layout, null and role gates,
display-state normalization, and transmit-versus-notify routing.

Current overlay/component/package identities are 201,732 / 3,725,128 /
4,503,622 bytes with SHA-256 values
`3be6d30bb0c6d7087a04131c928e840b08fe2c51c32190ca33835e822911b8fb`,
`b6911484e5166c62d1d40b7ff794b03967b8af03d740cfc241bd715cd802c4df`,
and `8e7028f3e7ffcecdbe44c1eede4ffa3bbbfa593d41ce10ed7f4630aff3d7247e`.
The 2,113,044-byte deployment plan has 3,017 placed regions, two unresolved
physical-evidence regions, and five container-only regions; its SHA-256 is
`98f581f8d06685b673b91bf2522d3dbbfb8ce318b99378e5e46608c33d833a1c`.
Live service-`0x30` master/peer BLE and terminal-UI qualification is deferred
by project direction; future qualification requires authorized G2 master/peer
and terminal-UI evidence. The software gap is closed; the wider
firmware remains incomplete.

## Translate protobuf service is production-routed

All four linked `pb_service_translate.c` entries and three bounded shared
helpers now compile from selector-isolated MIT clean-room C. Four
guarded redirects replace all 1,324 authenticated stock body bytes with 748
compiled Thumb bytes plus four alignment bytes. The authenticated 120-byte
literal pool remains official, and 13 strict relocations bind only to recovered
nanopb, tick, role, BLE transport, and sibling-source interfaces. Host tests
cover buffer bounds, RX decode/status/replay behavior, all three envelope
layouts, role gates, null and encoding errors, and send-versus-notify routing.

Current overlay/component/package identities are 202,484 / 3,725,880 /
4,504,374 bytes with SHA-256 values
`0201c5d6961d87cf65fb189d6ea125a2b627ed0b5fc5cf75036fc58f8019166f`,
`37efb5b3d63c9830646a2a1c50783d60823cbb209a9118c2da224dcc0b673959`,
and `7e6b2ced0cf4adab423d2f3080de733d9bb1feb7b93890bf4cfd48972e70c6b1`.
The 2,123,068-byte deployment plan has 3,032 placed regions, two unresolved
physical-evidence regions, and five container-only regions; its SHA-256 is
`16e1c6df34a39685f9bc891ec71dd472f7078341a0bbfa1fdb034c2d74237705`.

Live service-`0x05` master/peer BLE, replay timing, peer nanopb interoperability,
and translation-UI qualification is blocked by unavailable physical evidence; future
qualification requires authorized G2 master/peer and translation-UI evidence. The
translate software gap is closed; the wider firmware remains incomplete.

## Device-config protobuf service is production-routed

All three linked `pb_service_dev_config.c` entries and two bounded memory
helpers now compile from selector-isolated MIT clean-room C. Three
guarded redirects replace all 2,646 authenticated stock body bytes with 998
compiled Thumb bytes plus four alignment bytes. The authenticated 286 bytes of
distributed gap/literal data remain official, and 33 strict relocations bind
the dispatcher only to recovered nanopb, command-provider, heartbeat-timer,
BLE-transport, and sibling-source interfaces.

Host tests cover null/decode statuses, all fourteen command IDs, provider
success gating, error classification, unknown-command error encoding, the
30-second heartbeat timer refresh, output bounds, and transmit arguments.
Current overlay/component/package identities are 203,486 / 3,726,882 /
4,505,376 bytes with SHA-256 values
`ef060f12222fcd55be84927416752e0091541b0573921a4bda1588663d46e36b`,
`70446d59e2d7080732284af9d860c78b9561dba3552b0fd696b20e9e84dbd1ab`,
and `7a6aba86acf50a5c05dfdc8039793df2f8840599af5446dbd869f0c36e584991`.
The 2,132,348-byte deployment plan has 3,046 placed regions, two unresolved
physical-evidence regions, and five container-only regions; its SHA-256 is
`8d11759463eb12bc531222dff14d8a5d01e8fa4c3c6ea8fd5fd8df53b124d098`.

Live service-`0x80` pairing, role, BLE-parameter, disconnect/unpair, restore,
heartbeat, restart, time-sync, audio-control, and peer nanopb qualification is
blocked by unavailable physical evidence; future qualification requires authorized G2
master/peer evidence. The device-config software gap is closed;
the wider firmware remains incomplete.

## Protobuf health-service ownership reconciliation

The already production-routed `pb_service_health.c` tranche is now represented
consistently in its closure, provenance, and 15-service aggregate manifests.
Its eight redirects contribute 3,092 ownership bytes, bringing the protobuf
aggregate to 24,372 production-ownership bytes across nine routed services.
The firmware image is unchanged by this evidence-only correction. The health
software gap remains closed, while live service-`0x0E` BLE, peer/schema, and
persisted-data validation is blocked by unavailable physical evidence; future qualification requires authorized
physical evidence; six retained protobuf services still require software
implementations.

## Onboarding protobuf service is production-routed

All nine linked `pb_service_onboarding.c` entries and three bounded shared
helpers now compile from selector-isolated MIT clean-room C. Nine
guarded redirects replace all 3,024 authenticated stock body bytes with 878
compiled Thumb bytes plus eight alignment bytes. The authenticated 192 bytes
of distributed alignment/literal data remain official, and 22 strict
relocations bind only to recovered nanopb, BLE transport, onboarding-control,
display/readiness globals, and redirected sibling-source interfaces.

Host tests cover output bounds, null/decode/error statuses, all three command
pairs, control forwarding, heartbeat readiness mapping, event normalization,
notification sequencing, and response-versus-notify transport. Current
overlay/component/package identities are 204,372 / 3,727,768 / 4,506,262
bytes with SHA-256 values
`913b0418cdff1bedaebd49647b9efc28f44f652267dd24d9ff746cec46d82889`,
`a2f291046d44466f561b871a7fe96c2308620f13990f08878629941bc0e6d284`,
and `33c00464d8a201df3330cb520194cd16c377dca824bb36d55d6cf53f4fdd24bb`.
The 2,151,167-byte deployment plan has 3,074 placed regions, two unresolved
physical-evidence regions, and five container-only regions; its SHA-256 is
`06dac455f13cddabae7bd2700c67199c1bffe8ebe8043d7f174d300ab599d057`.

The protobuf aggregate now records 27,396 production-ownership bytes across
ten routed services. Live service-`0x10` peer BLE, display-ready,
onboarding-control, response, and notification qualification is deferred by
project direction; future qualification requires authorized G2 peer/UI evidence.
The onboarding software gap is closed; five retained
protobuf services and the wider firmware remain incomplete.

## OTA file service is production-routed

The complete `platform/protocols/ota_service/ota_service.c` object is closed
at `[0x004448F4,0x004488EC)`: 25 linked functions / 15,394 body bytes and 982
authenticated compatibility bytes. An independently authored GPL-3.0-only
implementation now supplies those 25 service entries plus four source-owned
flash/status adapters. The selector-isolated Cortex-M55 output is 3,130 text
bytes plus 18 alignment bytes with 65 strict relocations. Twenty-five guarded
redirects replace every stock function body while retaining the object-local
alignment/literal/callback pool.

Host and target tests cover the recovered C0/C1/C2/C3 ABI, MRAM/filesystem/XIP
selection, address and size rejection, 4 KiB erase/write streaming, CRC-32C,
read-after-write failure, secure descriptor commit, filesystem probe/heal,
export, cancellation, and RPC status synchronization. The canonical overlay,
Apollo component, and complete package are 222,948 / 3,746,344 / 4,524,838
bytes with SHA-256 values
`11ccabaa7a312d1c83b8bfb246bdfdbaa4bf8f3db4494ba21623c9d92bc4341c`,
`8e262f1ecea6bf0f3696d4216895e38bfc54f590a94fb628c0132e91e0bb118f`,
and `61f5fc2763bbd2b17e6e28f09bb13bdfc38a21a9e072a51c88dbec171fcbdde3`.
The 2,407,981-byte flash plan has 3,450 placed regions, two unresolved
physical-evidence regions, and five container-only regions; its SHA-256 is
`161d3854f8de6ad154dba4e2f56f18af70ddbe99f4b9d1271dc3901bd42ebd58`.

No package was signed or flashed. Live peer-visible OTA, writable-media,
bootloader-installation, power-loss, and rollback qualification is deferred by
project direction; future qualification requires authorized G2 hardware and
writable media. The OTA-service software gap is closed; wider firmware
functional completeness is not claimed.

## GX8002 codec-host service is production-routed

All twenty-six callable entries in `platform/audio/service_codec_host.c` are
now implemented by clean-room `service_codec_host.c`. Twenty-six guarded
redirects replace all 7,318 authenticated stock function bytes. The target
build emits 4,262 Thumb text bytes plus 38 runtime alignment bytes with 111
strict relocations, while 1,314 authenticated literal-pool and alignment bytes
remain official.

The host oracle exercises BUXX framing, both CRC layers, malformed lengths,
allocation failure and release, UART init/read/write/close paths, three retries,
version, beamforming, wakeup, microphone state/gain, DMIC, I2S, fixed one-bit
delay, wrapper status checks, and three-byte voice-event bounds. Every selector
also compiles under the reviewed Cortex-M55 flags. The canonical
overlay/component/package sizes are 244,992 / 3,768,388 / 4,546,882 bytes; the
flash plan is 2,642,970 bytes with 3,795 placed and two unresolved regions.

No image was signed or flashed. Live UART3/GX8002 command, audio, DMIC, I2S,
and event qualification is blocked by unavailable physical evidence; future qualification
requires authorized G2 hardware or a golden codec/UART capture. This software gap is closed; wider
firmware functional completeness is not claimed.

## GX8002 codec-DFU service is production-routed

All sixteen callable entries in `platform/audio/service_codec_dfu.c` are now
implemented by clean-room `service_codec_dfu.c`. Sixteen guarded redirects
replace all 9,052 authenticated stock function bytes. The target build emits
3,390 Thumb text bytes plus 24 runtime alignment bytes with 71 strict
relocations; 916 authenticated literal-pool and alignment bytes remain
official.

The host oracle covers strict FWPK parsing, required boot/firmware records,
bounds, CRC and cleanup failures, both bootloader stages and their exact wire
bytes, the 1-Mbaud transition, 8-KiB `serialdown` flow control and result
tokens, full DFU cleanup, and the same-version skip/cache path. All sixteen
selectors compile under the reviewed Cortex-M55 flags. The canonical
overlay/component/package sizes are 248,406 / 3,771,802 / 4,550,296 bytes; the
flash plan has 3,840 placed and two unresolved evidence-only regions.

No image was signed or flashed. Live destructive codec upgrade, UART timing,
reboot and post-flash boot qualification is blocked by unavailable physical evidence;
future qualification requires an authorized G2 pair or golden codec/UART
capture. This software
gap is closed; wider firmware functional completeness is not claimed.

## Codec UART lifecycle is production-routed

Both callable entries in `platform/audio/service_codec_porting.c` are now
implemented by clean-room `service_codec_porting.c`. Two guarded redirects
replace 342 authenticated stock body bytes; the target build emits 126 Thumb
text bytes plus two alignment bytes with four strict relocations and preserves
the 72-byte official diagnostic/literal pool. Host tests cover one-time 64-byte
ring setup, UART3 callback installation, resume/suspend failure, active-state
idempotence, and state transitions.

The canonical overlay/component/package sizes are 240,032 / 3,763,428 /
4,541,922 bytes; the 2,567,304-byte flash plan has 3,683 placed, two unresolved,
five container-only, and six protected regions. Live UART electrical behavior,
callback timing, and GX8002B interoperability is blocked by unavailable physical evidence; future qualification requires authorized responsive G2/codec hardware. Other codec-service and wider firmware
software gaps remain, so functional completeness is not claimed.

## AT^AUDIO control is production-routed

The single `_atAudioCtrl` entry is now implemented by clean-room `at_codec.c`.
A 44-byte Cortex-M55 leaf with three strict relocations dispatches leading `1`
and `0` to audio-manager acquire/release for application seven, acknowledges
every input, and returns one. Its guarded redirect replaces all 118 callable
stock bytes while the 34-byte official pool remains.

The canonical overlay/component/package sizes are 240,076 / 3,763,472 /
4,541,966 bytes; the 2,568,527-byte flash plan has 3,685 placed, two unresolved,
five container-only, and six protected regions. Audible and codec-power
behavior is blocked by unavailable physical evidence; future qualification requires authorized responsive G2/audio
hardware. Three larger codec-service objects and wider firmware gaps remain,
so functional completeness is not claimed.

## EUS/ESS/EFS/NUS BLE profiles are production-routed

The corrected stock census includes all four registered GATT write callbacks:
25 functions / 2,698 body bytes across the contiguous 3,000-byte profile
region. `ble_transport_profiles.c` now supplies 25 selector-isolated Cortex-M55
leaves (1,240 text bytes, 10 alignment bytes, 45 strict relocations), and 25
guarded redirects replace every stock function while retaining 302 official
pool bytes. Host behavior, selector compilation, stock topology, production
routing, component/package assembly, flash planning, and the first-party
frontier all pass. Current overlay/component/package hashes are
`87dd3f57f56f8ac138e5df6d96e5dd30ff97b8197e49b21392f04260fcd8f631`,
`e27208da3a7f963f6676bedfd039b589c283ce1be679c94317a80bb8061812b1`,
and `b84e19844a7459929059111af9804203a76760bbb9f8a1093063e2bb758c4b44`.
No image was flashed; physical timing and paired interoperability are blocked
by future-required authorized responsive G2/EM9305 evidence. Wider firmware
functional completeness is not claimed.

## SystemAlert UI is production-routed

Seven selector-isolated leaves in `system_alert.c` now replace all 2,174
callable stock bytes from the complete SystemAlert object. The compiled route
adds 1,138 Thumb text bytes, 51 read-only-data bytes, nine alignment bytes,
and 85 strict relocations while retaining the authenticated entry NOP and
170-byte pool. Host behavior, exact routing, manifest assembly, package
assembly, flash planning, origin accounting, and first-party-frontier gates
pass. The canonical overlay/component/package sizes are 225,396 / 3,748,792 /
4,527,286 bytes; the flash plan is 2,464,744 bytes with 3,531 placed regions.

No image was signed or flashed. Live display, timer, IMU, notification, and
paired-temple behavior is blocked by unavailable physical evidence; future qualification requires authorized physical
evidence. The SystemAlert software gap is closed; wider firmware functional
completeness is not claimed.

## SystemClose UI is production-routed

All twenty callable entries in `app/gui/SystemClose/systemClose.c` are now
implemented by clean-room `system_close.c`. Twenty guarded redirects replace
all 4,960 authenticated stock function bytes. The target build emits 2,804
Thumb text bytes plus 22 alignment bytes with 118 strict relocations and keeps
the 408-byte official alignment/literal remainder. FIFO, data and role gates,
page actions, layout, queued animation, scroll, confirm/cancel/minimize, IMU
reflash, page-factory, and UI-lifecycle host tests pass.

The canonical overlay/component/package sizes are 228,222 / 3,751,618 /
4,530,112 bytes; the flash plan is 2,503,413 bytes with 3,589 placed, two
unresolved, five container-only, and six protected regions. No image was
signed or flashed. Live display, shutdown/minimize, IMU reflash, and paired
synchronization qualification is blocked by unavailable physical evidence; future
qualification requires authorized G2 physical evidence.
The SystemClose
software gap is closed; wider firmware functional completeness is not claimed.

## FreeRTOS+CLI filesystem is production-routed

All twelve callable entries in `app/freertos_cli/freertos_cli_filesystem.c`
are now implemented by clean-room `freertos_cli_filesystem.c`. Twelve guarded
redirects replace all 3,200 authenticated stock function bytes. The target
build emits 9,866 Thumb text bytes, 704 read-only-data bytes, and 20 alignment
bytes with 179 strict relocations; 56 official non-callable bytes remain.

The canonical overlay/component/package sizes are 238,812 / 3,762,208 /
4,540,702 bytes; the flash plan is 2,538,060 bytes with 3,639 placed, two
unresolved, five container-only, and six protected regions. No image was
signed or flashed. Live media mutation, persistence, corruption recovery,
power-loss, and concurrent CLI qualification is blocked by unavailable physical evidence;
future qualification requires authorized writable physical test media. This software gap is
closed; wider firmware functional completeness is not claimed.

## Factory NVDB lifecycle is production-routed

All five callable entries in `service_nvdb.c` are now clean-room C. Five
guarded redirects replace 930 stock body bytes with 514 compiled Thumb bytes,
four alignment bytes, and eleven strict relocations; the 122-byte official
pool remains. Valid-media mount, callbacks, schema descriptor, record
validation, and PSN reconciliation have host coverage. Missing or mismatched
magic fails closed and cannot invoke wholesale default reset.

The canonical overlay/component/package sizes are 239,330 / 3,762,726 /
4,541,220 bytes; the flash plan is 2,546,521 bytes with 3,652 placed, two
unresolved, five container-only, and six protected regions. Physical
persistence, recovery, and schema compatibility is blocked by unavailable physical evidence; future qualification requires authorized responsive G2 hardware and a golden `NVdb` capture. Wider firmware
functional completeness is not claimed.

## ALS driver is production-routed

All 38 callable entries in `driver\sensor\als\als.c` are now implemented by
clean-room `als.c`. Thirty-eight guarded redirects replace all 3,858 stock
function bytes. The selector-isolated Cortex-M55 build emits 2,216 Thumb text
bytes, a 48-byte brightness-curve closure, 30 alignment bytes, and 82 strict
relocations while retaining 374 authenticated literal/alignment bytes.

Host tests cover the OPT3007 ID/configuration sequence and lux conversion,
five- and twenty-sample windows, pitch rejection, curve buckets, Q10 scaling
and learning, extreme-dark policy, brightness synchronization, manual lockout,
timer states, and open/close behavior. Canonical overlay/component/package
sizes are 257,980 / 3,781,376 / 4,559,870 bytes; the 2,943,327-byte flash plan
has 4,239 placed, two unresolved, five container-only, and six protected
regions. No image was signed or flashed. Live sensor-bus, calibrated-lux,
display-response, and paired-temple qualification is deferred by project
direction; future qualification requires authorized G2/OPT3007 physical evidence
or a golden trace. Wider firmware functional completeness is
not claimed.

## Current bootloader MSPI device-reconfiguration increment

The complete authenticated `[0x00420E08,0x00420E8C)` body now routes to
clean-room compilable C. Host tests pin the exact disable, device-configure,
enable, and source-owned pin-group sequence; handle/state cells; configuration
offset `+8`; all failure diagnostics; and stock status collapse to `1`.

Apple/Linux emit 136/128 bytes with one strict pin-group relocation. Their
overlay identities are 14,164 /
`afd9bcfa294f66ffb92c17c5d562a7c8e1cb6d95c6bf49ebd00cb8d315e26e5a`
and 14,140 /
`cda5772f628c68390b477329eea3ccba4e4138aa0d53f1dd3485ef3086a27881`;
provider identities are 162,764 /
`dc3e8e2fecad73b3db6550353ea12317b7a5a5fe2b1a0415871f8a510d0185b5`
and 162,740 /
`3a40fd8e34da6c07eef37c1018323db537a8f8ef3bbdd062637637ca6ceba155`.
Canonical accounting is 14,149 source-owned, 15,464 generated patch, 16
alignment, and 133,135 retained official bytes across 191 functions, 172
relocated leaves, and 189 patch sites.

Apple/Linux unsigned packages are 4,744,342 / 4,520,328 bytes with SHA-256
`fd48ce7f025a78835fe08478da55b5146c359ca3ac050e092a98366c2c212a81` /
`d02f9da0600b62b85c3867cd542ce769b8d72cbe1d15ccbb98b103ad5891c6a8`.
No hardware operation occurred. Live HAL/pinmux/MSPI/XIP/external-flash and
cold-boot qualification is blocked by unavailable physical evidence; future qualification
requires authorized G2 physical evidence. The next executable entry at
`0x00420E8C` remains a software gap, so completeness is not claimed.

## Health UI page is production-routed

All twelve callable entries in `app/gui/health/ui_health_page.c` are now
implemented by clean-room C. Twelve guarded redirects replace all 9,414 stock
body bytes while 640 compatibility bytes remain official. The isolated target
build emits 3,978 Thumb text bytes, 328 authenticated string bytes, and ten
alignment bytes with 269 strict relocations.

Behavioral tests cover live health-metric formatting, goal progress, two-page
indicators, animated switching, deferred FIFO ordering, touch-coordinate
forwarding, refresh, common data, minimize, and teardown. Canonical
overlay/component/package sizes are 330,776 / 3,854,172 / 4,632,666 bytes; the
3,067,205-byte flash plan contains 4,421 placed, two unresolved, five
container-only, and six protected regions.

No image was signed or flashed. Live paired display/input qualification is
blocked by unavailable physical evidence; future qualification requires an authorized G2
pair or golden health-page UI trace. The health-page software gap is closed; wider firmware
functional completeness is not claimed.

## Touch sensing, gestures, and ACT/ALR/WOT policy are source-complete

The authenticated six-word/channel MSC loop and its maximum reduction now
compile from freestanding Cortex-M0+ C alongside all four observed power-state
transitions, left/right swipe, long press, five-fast-click, and saturating
calibration policy. Seven focused evidence, behavior, and target-build gates
are green.

Raw MSCLP/noise/timing/sleep/wake validation still requires a responsive
authorized controller and golden traces, so the shipped touch application is
retained. No device was accessed and wider firmware completeness is not
claimed.

## Cordio application framework is source-routed across every bounded anchor (2026-08-26)

The remaining 25 AmbiqSuite/G2 application-framework anchors now compile from
maintained C in four new runtime modules. Core/UI/server owns seven entries
(488 compiled B / 10 relocations replacing 3,816 stock B), master owns four
(262 B / 6 relocations replacing 1,522 B), slave owns three (698 B / 25
relocations replacing 1,944 B), and discovery owns eleven (2,064 B / 38
relocations replacing 6,186 B). Host behavior tests cover state transitions,
bounds, parser progression, bond/privacy decisions, connection handling, and
completion; every isolated Cortex-M55 selector compiles with `-Werror`.

Together with the existing 22-function MRAM database and 14-function legacy
cluster, the framework now production-owns 61 distinct functions / 29,870
stock body bytes. All 50 authenticated source-path anchors / 29,110 anchored
bytes are routed, leaving zero bounded application-framework anchors. The five
application runtime modules total 4,460 compiled bytes under 108 strict
relocations.

Canonical overlay/component/package identities are 424,732 / 3,948,128 /
4,726,622 bytes with SHA-256
`9f0dd0742bac903da275993e19c135a2508070a8baf4c462fb3d170a0a1272d9`,
`e3cfa30e77a5053d302aa3bc569cad39937d57c524c8e2e681923b70ad60b3a7`,
and `ecc49cd5b184fce9a6a25f71532eba7d1ee33ee566b131ec1b97b0a9536287d9`;
the package rebuild is byte-identical. No image was signed, flashed, or
installed. Live scan, advertising, connection, controller, concurrency, and
paired-temple qualification is blocked by unavailable physical evidence; future
qualification requires authorized G2/EM9305 physical evidence. This closes the bounded
framework software gap only; wider firmware completeness is not claimed.

## Touch-controller command/report protocol is source-complete

The shipped PSoC 4000T I2C command/report layer now compiles as eight
freestanding Cortex-M0+ APIs. The implementation covers RX bounds, all nine
slots with seven recovered bodies and two fail-closed resident targets,
replies, sensor/event reports, baseline persistence, long-press configuration,
attention timing state, FIFO descriptors, power bounds, and callback-only DFU
handoff. Seven focused gates are green.

Production still retains the shipped touch prefix. Resident flash at
`>=0x8680` is unavailable, and live I2C/IRQ/GPIO/EEPROM/sleep/DFU validation
requires a responsive authorized temple. No device was accessed and wider
firmware completeness is not claimed.

## Charging-case UART/update protocol is source-complete

The recovered case-side frame, checksum, retry, update-offer, nested-chunk,
and dual-bank OTA contracts now compile as eight freestanding Cortex-M0+ C
APIs. Nine focused gates cover malformed/truncated frames, checksum mutation,
big-endian image sums, offers and chunks, exact retry behavior, erase retry,
serial-window copy ordering, verification, result notification, and bank swap.

All erase/program/option-byte/reset work is callback-only, and the official
case payload remains packaged. Live promotion is blocked until an authorized
case, UART capture, and backups of all four serial-number windows are
available. No device was accessed and wider firmware completeness is not
claimed.

## CmBacktrace fault path is source-complete with a physical validation block

The authenticated MIT compatibility snapshot now target-compiles all six
CmBacktrace APIs for Cortex-M55 using the recovered FreeRTOS/English/M33-class
configuration. A maintained naked C entry shim compiles to the exact register
contract required by the upstream handler: `r0=lr`, `r1=sp`, call the fault
decoder, and trap on unexpected return. The closure pins the six exports, all
platform seams, the 786-byte stock fault body, and the historical exception-
frame behavior.

The production HardFault vector remains stock. Deliberate fault-injection
qualification is blocked by unavailable physical evidence; future qualification requires
authorized G2 hardware with fault-injection observability. No image
was signed, flashed, or installed. Wider firmware functional completeness is
not claimed.

## Cordio ATT client core and discovery are production-routed

All 21 `attc_main.c` definitions and all 18 `attc_disc.c` definitions now have
compilable source. Twenty core guarded redirects replace 3,540 stock body bytes
with 2,258 compiled Cortex-M55 bytes plus 12 alignment bytes under 61 strict
relocations. Fifteen discovery redirects replace 2,908 stock body bytes with
1,610 compiled bytes plus 16 alignment bytes under 18 strict relocations. The
four dead-stripped public definitions remain source-owned and target-compile.

The implementation covers serialized and continuing requests, prepared writes,
MTU, PDU/control/sign callbacks, connection lifecycle, cancellation, timeout,
service/characteristic/descriptor discovery, configuration, and malformed
response handling. Bounds hardening includes one-based connection/on-deck
indexing; the PDU procedure cancel event is corrected to authenticated value 19.

The canonical overlay/component/package sizes are 353,336 / 3,876,732 /
4,655,226 bytes; the 3,457,178-byte flash plan has 4,977 placed, two unresolved,
five container-only, and six protected regions. The aggregate ATT/WSF gate
passes 80 tests with one explicit unavailable-archive skip. No image was signed,
flashed, or installed. Live ATT peer/controller/timer/discovery qualification is
blocked by unavailable physical evidence; future qualification requires an authorized
G2/EM9305 pair or golden trace. These two software gaps are closed; wider firmware functional
completeness is not claimed.

## Cordio common HCI core is production-routed

All 24 common-core definitions now have maintained Apache-2.0/G2-ABI C.
Twenty-two guarded redirects replace all 1,964 authenticated stock function
bytes with 3,690 compiled Thumb bytes plus 26 alignment bytes under 50 strict
relocations; both source-only APIs target-compile. Host tests cover connection
and CIS lifecycle, ACL queueing/fragmentation/completion, transport refusal,
partial-header and overlong L2CAP reassembly, reset draining, 64-bit feature
state, maximum-RX policy, and validated watermarks.

The promotion/manifest prefix collision between `hci_core` and `hci_core_ps`
was fixed by most-specific ownership, and all nine platform-shim routes were
restored and regression-gated. Canonical overlay/component/package identities
are 375,186 / 3,898,582 / 4,677,076 bytes with SHA-256 `8c05945a…a3c3`,
`8dcb804c…8598`, and `e4579c12…b049`; the 3,937,595-byte flash plan hashes to
`15a2fac0…e92` and contains 5,668 placed, two unresolved, five container-only,
and six protected regions. No image was signed or flashed. Live controller
ACL/event/ISO, reset timing, RF, and peer qualification is blocked by unavailable physical evidence; future qualification requires authorized responsive G2/EM9305 hardware. The common-core software
gap is closed; wider HCI and firmware functional completeness is not claimed.

## Cordio vendor reset/NVDS sequence is production-routed

All eight vendor-sequence definitions now compile from clean-room C. Four
guarded redirects replace all 546 authenticated linked bytes with 862 compiled
Thumb bytes and six alignment bytes under 23 strict relocations; the four
source-only hooks target-compile as fail-closed no-ops. Behavioral tests cover
the exact Reset → NVDS → RF power → event-mask/capability sequence, feature
gates, state extraction, extension fallback, and four-random completion.

Canonical overlay/component/package identities are 375,186 / 3,898,582 /
4,677,076 bytes with SHA-256 `8c05945a…a3c3`, `8dcb804c…8598`, and
`e4579c12…b049`. The 3,937,595-byte flash plan hashes to `15a2fac0…e92` and
contains 5,668 placed, two unresolved, five container-only, and six protected
regions. No image was signed or flashed. Live reset, address, NVDS, RF-power,
timing, and controller evidence is blocked by unavailable physical evidence; future qualification requires authorized responsive
G2/EM9305 hardware. This software slice is closed; wider HCI and firmware
functional completeness is not claimed.

## IAR formatted output is production-routed

The sole 3,256-byte IAR printf core is now SHA-guarded and redirected from all
four unchanged stock wrappers to four maintained Cortex-M55 leaves: a 3,512-byte
freestanding formatter, 50-byte writer bridge, 84-byte validated variadic
adapter, and 14-byte soft-PCS ingress. The implementation closes the reachable
integer, pointer, string, `%n`, decimal/exponential/general float, `%a/%A`, IAR
`q`/`L`, and `%PV`/`%pV` behaviors. Every exact stock wrapper supplies
`secure=0`; nonzero mode fails closed, so Annex-K has no production ingress.

The canonical overlay/component/package identities are 408,458 / 3,931,854 /
4,710,348 bytes with SHA-256 `22a9e111…8c18`, `8e217faf…2763`, and
`fab29936…baee`. The 4,071,802-byte flash plan hashes to `fd12c956…983d` and
contains 5,864 placed, two unresolved, five container-only, and six protected
regions. Host semantics, freestanding target compilation, 11 exact engine
relocations, full core redirect, manifest tiling, and complete image identity
are gated by `make iar-format-output-closure`. No image was signed, flashed, or
installed. Live writer, termination, stream, and float-rounding qualification
is blocked by unavailable physical evidence; future qualification requires authorized G2
physical evidence. The formatted-output software gap is closed; wider firmware
functional completeness is not claimed.

## AmbiqSuite ANCC profile is production-routed

All 21 recovered ANCC entries now compile from maintained C and are guarded by
exact stock-span redirects. A portable dependency-free core implements the
1,372-byte G2 SRAM ABI, 64-entry update-first/reverse-pop list, all three ANCS
control-point commands, strict 61-byte app-ID limit, validated notification
source, and fragmented 512-byte data-source parser. The G2 adapter adds the
message scheduler, role/OTA/EFS/timestamp gate, product notification
projection, whitelist decision, dual-glasses sync, discovery, and WSF event
dispatch. Eleven thousand seven hundred sixty compiled bytes under 69 strict
relocations replace all 3,712 stock body bytes.

Tests cover exact commands, list saturation/update/removal, malformed lengths,
overflow reset, single-byte and every-split fragmentation, the distinct
one-app/eight-notification completion rules, product policy, event dispatch,
and all 21 isolated Cortex-M55 builds. The canonical overlay/component/package
identities are 420,232 / 3,943,628 / 4,722,122 bytes with SHA-256
`7e0a198a…de8d`, `cb584519…51cb`, and `39f1132a…a374`. The 4,105,447-byte
flash plan hashes to `e9432043…ee33` and contains 5,911 placed, two unresolved,
five container-only, and six protected regions. No image was signed, flashed,
or installed. Live ANCS discovery, CCC, control-point actions, controller
timing, product sync, and dual-temple qualification is deferred by project
direction; future qualification requires authorized G2/ANCS physical evidence. The
ANCC software gap is closed; wider firmware functional completeness is not
claimed.

## Cordio application-framework legacy master/slave cluster is production-routed

All 14 linked legacy master/slave entries now compile from maintained
AmbiqSuite-derived C and are guarded across the complete 1,406-byte stock
cluster. The 948 compiled bytes and 29 strict relocations preserve the fixed
G2 master/slave control blocks, configuration-pointer cells, stored callback
entry values, scan/connect API, advertising data/type/start/stop behavior, and
the G2-only WSF retry policy for transitions through extended advertising.
Host tests cover every state, callback, clamp, directed restart, set-stop
success, and 200/100 ms retry branch; all 14 isolated Cortex-M55 selectors
compile with `-Werror`.

The framework audit now reconciles prior work as well: all 22 anchored MRAM
application-database functions were already source-routed. The current total
is therefore 36 distinct functions / 16,402 stock body bytes routed, leaving
25 anchors / 13,468 bytes across app UI, master, server, slave, discovery, and
main as explicit software gaps. Canonical overlay/component/package identities
are 421,196 / 3,944,592 / 4,723,086 bytes with SHA-256 `a065d198…629a`,
`5b012836…3c5d`, and `d29b25c0…db27`. The 4,132,536-byte flash plan hashes to
`0f649619…4afe` and contains 5,948 placed, two unresolved, five container-only,
and six protected regions. No image was signed, flashed, or installed. Live
scan, advertising, connection, controller-transition, concurrency, and paired-
temple qualification is blocked by unavailable physical evidence; future qualification
requires authorized G2/EM9305 physical evidence. Framework and firmware completeness are not
claimed.

## Apollo box-detect service is production-routed (2026-08-26)

The complete `service_box_detect.c` state machine now compiles from maintained
C. A refreshed authenticated-image audit corrected two ten-byte CMSIS timer
callbacks previously counted as pool data, bringing the closed object to 34
functions / 3,584 body bytes with 328 retained literal/data bytes. The service
preserves both timers, the fixed local/case SRAM state, effective-state
intersection, force-out suppression, display transitions, ring reconnect,
device-manager events, and eight-byte glasses-case synchronization.

All 34 guarded entries route to 1,626 compiled text bytes plus 36 alignment
bytes under 77 strict relocations. Six host behavior tests and every isolated
Cortex-M55 selector pass with `-Werror`. Canonical overlay/component/package
identities are 426,394 / 3,949,790 / 4,728,284 bytes with SHA-256
`4b39c8a836154fada2b452be5f7de25c76541ed3d3cc8685571ff5d73cbfd999`,
`0548bcfe565e675ee2883961bdead6e6441b593fca755278b637ffd908e0b32c`,
and `c7c5e02c2e3ce6d1fc4fbed7fd7a06b0e01a47cf00e8dd4e040c098ca2755a86`.
The package rebuild is byte-identical with 6,124 placed and two unresolved
regions. No image was signed, flashed, or installed. Live case/box electrical,
timer/concurrency, display, ring-reconnect, and state-machine validation is
blocked by unavailable physical evidence; future qualification requires authorized hardware; wider firmware completeness is
not claimed.

## S200 product startup/main is production-routed (2026-08-26)

A refreshed authenticated-image audit corrected the stale second function
entry from `0x5CDB88` to `0x5CDBAC`; the former address is data. The resulting
six-function object contains 1,468 executable bytes and 62 retained
literal/data bytes. Maintained C now preserves the two LVGL callbacks, widget
construction, ordered platform initialization, reset-reason priority and
brown-out status clear, release registration, product-RTOS initialization,
SRAM startup hand-off, and terminal main-thread loop. Diagnostics are omitted.

All six source entries pass host semantics and isolated Cortex-M55 `-Werror`
compilation. They route to 584 compiled text bytes plus four alignment bytes
under 47 strict relocations. Canonical overlay/component/package identities
are 426,982 / 3,950,378 / 4,728,872 bytes with SHA-256
`20be6b6564d35dcaa5d4b0e6e6db659e93b7ebc287085bc5b263b8b6ccb5b4fd`,
`5e92895a86a57ece34100c494e8ec99132d20e2567734b9e4c9285c0f152fa8a`,
and `8c7bd2469ac367b6b2139798ae68d7d08cf49f79e17f8c6fc9fd0fd47cb02eba`.
The pinned rebuild is byte-identical with 6,141 placed and two unresolved
regions. No image was signed, flashed, or installed. Live startup,
reset-controller, clock/power, LVGL, and task hand-off validation is deferred by
project direction; future qualification requires authorized physical evidence.
Wider firmware completeness is not claimed.

## Cordio security API is production-routed (2026-08-26)

The former weakest-grounded “first-party Even cryptographic backend” row is
resolved: the authenticated live surface is Packetcraft Cordio r20.05c
`sec_api`, not a separate identified Even backend. Maintained Apache-2.0 C now
owns all 20 service entries / 1,392 stock body bytes while preserving 46
literal/alignment bytes and the HCI/controller primitive boundary. Random-ring
refill, AES queue completion, CMAC framing, token allocation, and ECC byte order
and completion behavior are implemented.

All 20 isolated Cortex-M55 selectors and host behavior tests pass with
`-Werror`. Production routing emits 1,952 text bytes plus 16 alignment bytes
under 65 strict relocations. Canonical overlay/component/package identities are
429,058 / 3,952,454 / 4,730,840 bytes with SHA-256
`0e3a5f42548a24be9c6be90f9d6a60031af69b6570e7d212815f6671bb6d7bcd`,
`dc578472f06af2d499b9cb771fc185df4f739a05de558098088b56da9a5e4ce0`,
and `d77d88162f777a6c9889d1813323a836d1dc140fe7488009fe485ed787d8fe70`.
The 4,299,871-byte flash plan hashes to
`6820a0dc5b6be70fdca78144fdb39d56a9f898b7b0b832c8d76b18cef33608f6`;
the package replay is byte-identical with 6,193 placed and two unresolved
regions. No image was signed, flashed, or installed. Live controller,
concurrency, timing, and paired-temple validation is blocked by unavailable physical evidence;
future qualification requires authorized G2/EM9305 physical evidence.
Firmware-wide completeness is not claimed.

## QP/C 6.5.1 source and license boundary is closed (2026-08-26)

The official Quantum Leaps commit
`416dcec8820b9cdb5827497e645d0d9375db53c6` is now vendored as the bounded
EM9305 QP/C 6.5.1 source snapshot. Its GPL-3.0-or-later option is compatible
with openCFW; every imported file and release macro is hash-pinned. Eight
portable QEP/QF/QK translation units compile with the local host compiler under
the recovered 16-priority, two-pool, zero-tick-rate, 16-bit signal/event/pool,
8-bit queue, and saved-critical-state ABI. Interrupt and ISR-context behavior
remain explicit external providers.

This does not yet production-route the 3,052-byte EM9305 cluster. A reviewed
GCC 16.1.1 ARCv2-EM container now compiles the eight portable units plus two
OpenCFW port units and deterministically links a 21,284-byte relocatable ELF
and 32,026-byte archive with zero undefined symbols and zero forbidden runtime
imports. `make em9305-qpc-component` reproduces the checked receipt. Exact
install placement/redirect records remain unresolved, and live QK scheduling,
critical-section, sleep, UART, voltage-monitor, controller, and radio-timing
qualification is blocked by unavailable physical evidence. The stock
controller blob remains the package provider and firmware-wide completeness
is not claimed.

## S200 bootloader redirect initialization is production-routed (2026-08-26)

The complete 88-byte `product/s200/bootloader/config/redirect.c`
`redirect_init` entry now routes to clean-room C. It preserves both ordered
`osMutexNew(NULL)` calls, the two SRAM handle publications, post-allocation
failure checking, exact return values, and authenticated EasyLogger identity,
levels, source lines, and messages. Adjacent IAR `FILE` wrappers remain outside
this bounded closure.

Canonical Cortex-M55 output contributes 132 text bytes and a 143-byte
diagnostic string closure under 12 strict relocations. The complete bootloader
now also production-routes the Arm EABI byte-fill and forward-copy entries
through relocation-free C leaves; the adjacent six-caller bounded comparison
is now source-owned as well. The adjacent three-caller reject-set and accept-
set string-span entries are source-owned too, as is the adjacent six-caller
reflected CRC-32 updater, sole-caller SRAM-word setter, and runtime cluster
through the TLSF public-API boundary at `0x004172DA`. It contains 126 routed functions and accounts for 6,931
source-owned bytes, 8,208 generated patch bytes, 14 alignment bytes, and
140,391 retained official bytes. The 6,944-byte overlay and 155,544-byte
provider hash to
`bb89cb1587eff14c620b34a511f47fcdaa7b5a9d030c39fe701a0014e2dc60bc`
and `7da4698d31de6079b92a6020bf7cbb6fdce98dcc2b4dcbab1e0ac9c0ebbc8ac8`.
Apple clang 21 and Homebrew clang 22.1.8 profiles preserve the reviewed
layout/relocation graph, with profile-specific binary hashes.

Host semantics, isolated builds, exact stock replacement, manifest ownership,
and the fail-closed analyzer pass offline. Unsigned packages were regenerated;
no image was signed, flashed, or installed. Live boot, mutex, failure-log, and IAR stream
serialization evidence is blocked by unavailable physical evidence; future qualification requires authorized responsive
hardware; the larger bootloader remains a software gap and firmware-wide
completeness is not claimed.

The final deployment replay produced a byte-identical 4,737,122-byte Apple
package (`099dbe07…694b`) with 6,391 placed and two unresolved regions. The accumulated
Linux-profile gap was also closed by compiling every currently registered
Apollo-main leaf with Homebrew clang 22.1.8 and recording the resulting
204,960-byte overlay / 3,728,356-byte provider. Its complete unsigned package
is 4,513,112 bytes (`924cb8d2…bbb5`) with 3,391 placed and the same two
unresolved boundaries. This is reproducible deployment evidence, not a
hardware-validation claim.

## Bootloader numeric, logging, context, gate, dispatcher, and TLSF runtime is production-routed (2026-08-26)

The numeric, float, formatter, dispatch, substring, context, gate, and next
address-identified runtime entries at `[0x00415844,0x004172DA)` now route to
84 C leaves. Their 6,756 stock bytes, 259 fail-closed topology entries, and
two registered-pointer ingress paths are authenticated. Apple clang emits
5,826 Thumb bytes with 181 strict
relocations; Homebrew clang reproduces
the reviewed ABI. Host tests cover
arithmetic, parsing, decimal/hex output, case selection, nullable destinations
and strings, repeat counts, width/precision, 32/64-bit arguments, CRLF, and
float success/error/null-output behavior.

The queue and handle leaves close `[0x0041649A,0x0041699A)`: guarded submission, runtime
object creation, event-flags set/wait/create, and tagged-handle acquire/release.
They preserve task/ISR selection, PendSV requests, storage thresholds, handle
tagging, timeout mapping, semaphore/queue construction, queue put/get, and
retained backend ABIs. The following bit-width, count-trailing-zeros,
floor-log2, twelve TLSF block-header leaves, eight TLSF topology/alignment
leaves, three TLSF request-size/class-mapping leaves, and three free-list
selection/mutation leaves, ten allocator-operation leaves, and seven public
allocator leaves preserve all
zero/nonzero, status-bit, pointer-offset, physical-link, state-propagation,
power-of-two alignment, size-bound, and class-rounding semantics. The complete
cluster's host semantics, dual-profile pins, manifest ownership, and both
unsigned packages are fail-closed. After 98 bytes of authenticated transition
data, the next body starts at `0x0041733C`.

Software closure is complete for this runtime/TLSF tranche. Live boot,
formatting/parsing/logging and caller-path qualification is deferred by project
direction; future qualification requires authorized G2 physical evidence. The logging
literal pools remain authenticated data and the remaining 140,391 retained
bootloader bytes include later executable software gaps;
firmware-wide completeness is not claimed.

## Bootloader EasyLogger control/output and lock-enable are production-routed (2026-08-26)

The ten complete EasyLogger control entries `[0x0041733C,0x004176CE)`, the
115-caller `elog_output` entry `[0x004176CE,0x00417AD0)`, and
`elog_output_lock_enabled` at `[0x00417B7C,0x00417BB8)` now route to maintained
MIT C. The output implementation preserves the G2 interrupt gate, assertions,
all filters and enabled prefix fields, colors, keyword filtering, 1,024-byte
truncation policy, locking, and three-argument sink. The lock-enable leaf
preserves all four saved-state combinations and the exact port-lock seams.

The bootloader audit now authenticates 96 runtime functions, 393 direct
callers, two registered-pointer ingresses, 7,758 compiled Thumb bytes, and 187
strict relocations. Canonical accounting is 8,863 source-owned, 10,208
generated-patch, 14 alignment, and 138,391 retained official bytes. Apple
Clang produces an 8,876-byte overlay and 157,476-byte provider with SHA-256
`e046149fbc0e1961f38cef098b9984baa39e22d3b201d6a1cf81a3d8bcee999b`
and `c404f346fda3d412e846469765de57945b2147f61026f5ad6ceeec2379a20d95`.
Linux Clang produces 8,860 / 157,460 bytes with SHA-256
`15f1c4805b1d93146cafc9c1019e077421d7717f5338922e9b4161ada741bbff`
and `ec0c5021691ff0acc1cb5e87803de7170426454a741c084d24dcfc034c4cffd4`.

The unsigned Apple package is 4,739,054 bytes, SHA-256
`9c0e1e69ce5353755229a5bf07afdd256bb72607de20c7c2617e33928dcbdc61`,
with 6,416 placed and two unresolved regions. The Linux package is 4,515,048
bytes, SHA-256
`b092ca5279fb3dc2ea77ff0d935c1cd6ef8ec98b27b9ab98adbe5691a8f12489`,
with 3,404 placed and the same two unresolved regions. No firmware was signed,
flashed, installed, reset, or booted. Live logger, mutex, scheduler, transport,
and exception-path validation is blocked by unavailable physical evidence; future qualification requires authorized responsive G2 hardware; the remaining bootloader body is still a
software gap and functional completeness is not claimed.

## Bootloader EasyLogger port is production-routed (2026-08-26)

The eleven complete callable entries in `[0x0041A648,0x0041A700)` now route
to a 12,540-byte maintained MIT EasyLogger boot-port adaptation. The source
preserves lazy CMSIS mutex creation and 1,000-tick locking, null-handle no-op
behavior, three-argument output forwarding, bounded decimal tick formatting,
and kernel-state-aware task naming. The authenticated 22-byte literal island
at `[0x0041A6DA,0x0041A6F0)` remains retained data.

Both reviewed toolchains emit the same eleven relocation-free leaves totaling
204 bytes. Canonical accounting is 9,075 source-owned, 10,370 generated patch,
14 alignment, and 138,229 retained official bytes across 149 functions and
147 patch sites. Apple produces a 9,088-byte overlay and 157,688-byte provider
with SHA-256 `aeceaf38dee61ece3a1fc9518d5d08dd5eb4148d3ff8811659fe695a24cb1578`
and `48bc79d2391b5842316fe9c045727b90da96009ecd2dbc21d70fd3af5e3acff7`;
Linux produces 9,072 / 157,672 bytes with SHA-256
`34d79ac61578fb5c189b06a15c44731506c9cf92f7642f21b531fedc0c0dc2d3` and
`9fcb060ca96964b71da9b1c6f75b1afc5d923a285ce07f6d7e43de31c311be75`.

The unsigned Apple/Linux packages are 4,739,266 / 4,515,260 bytes with
SHA-256 `f7350f9208368191553ac0c3da07a68af90d66578595b858ad62a519a6dbbc81`
and `96c1a37d4a14af132f338de523115cf614f9ef5c72da337eeb8382f1c6ea4c45`.
Nothing was signed, flashed, installed, reset, booted, or sent to a transport.
Live mutex/scheduler/task-name qualification is blocked by unavailable physical evidence;
future qualification requires authorized G2 physical evidence. The output
driver/transport and later retained bootloader bodies remain
software gaps, so firmware-wide functional completeness is not claimed.

## Bootloader EasyLogger transport is production-routed (2026-08-26)

The level-dropping channel-one driver `[0x0041B854,0x0041B862)` and complete
four-channel transfer entry `[0x0041F918,0x0041F9B6)` now route to maintained
clean-room C. Host coverage validates all four channel bounds, initialized
state, the 56-byte descriptor, completion clearing, lower-start result,
immediate/delayed completion, ten-unit waits, and the stock 1,000-poll timeout
policy. Both reviewed Clang profiles emit identical relocation-free 16-byte
and 120-byte leaves.

Apple overlay/provider identities are 9,224 / 157,824 bytes with SHA-256
`790603494de6a154f9032c4e7257b4c203e477893619c0b25325b972b39c45da` and
`ed616af6c46214891f25e3102f04554129a989fc83422700eb29d6242d3e68f5`;
Linux identities are 9,208 / 157,808 bytes with SHA-256
`ffd38e6fd268398b0c8c5cc5afd0d898e2fe3cb62d000f2c91b96e4682f8b9a8` and
`1d4c130d0e9ac6de37b8bfe9c682b096eff5d85048faaa22fd414b1da3bc622c`.
Canonical accounting is 9,211 source-owned, 10,542 generated patch, 14
alignment, and 138,057 retained official bytes.

The unsigned Apple/Linux packages are 4,739,402 / 4,515,396 bytes with
SHA-256 `4eaff8522cca172ef79c3e57686f395437e7a5877ce4c0ea6ab4831cc72e76a2`
and `d05b3c4af715097e470d33d6a7e78646d7136a80ec24d07a6ae79ba5fc0a548b`.
Their flash plans contain 6,446 / 3,421 placed regions and two unresolved
boundaries each. No signer, device, UART, debugger, transport, flasher, reset,
or boot operation was accessed. Physical qualification is deferred by project
direction; future qualification requires authorized G2 physical evidence. Later
retained executable bootloader spans remain software gaps.

## Bootloader delay and initializer services are production-routed (2026-08-26)

The complete millisecond/raw delay wrappers and initializer comparator/runner
at `[0x0041F9D8,0x0041FA40)` now route to maintained clean-room C. The four
entries replace 102 authenticated executable bytes with 96 relocation-free
Thumb bytes. Host coverage validates wrapping 32-bit millisecond conversion,
raw forwarding, priority comparison, stable sorting/dispatch, null callback
skipping, zero records, and the 256-record cap. Caller scans additionally pin
the stored odd comparator pointer.

Apple overlay/provider identities are 9,320 / 157,920 bytes with SHA-256
`aaefcef3e31df12ec06a2ee7f505430f17daba8061099677143b24505ea96dc7` and
`56350fb0fc8d663dc2202f11389573b52ddd30536e81f44539006f7810f2744d`;
Linux identities are 9,304 / 157,904 bytes with SHA-256
`6be4f564d6ef9ace9c98de17bf2cc082142440a3da3716521a9e3e529ebb017b` and
`3961d3432af2cbeb83731d79792071161980decbc6cf635c57b6a396f09f3504`.
Canonical accounting is 9,307 source-owned, 10,644 generated patch, 14
alignment, and 137,955 retained official bytes across 155 functions, 136
relocated leaves, and 153 patch sites.

The unsigned Apple/Linux packages are 4,739,498 / 4,515,492 bytes with
SHA-256 `115c5ad73e32e308287034d1b1120f8ed576ec3c3c9294cafce1bfc561b727f9`
and `e742a5b7775cf8aae0667e0a425a76a83c9032406a28bcd679bfb82529de8c92`.
Their flash plans contain 6,456 / 3,427 placed regions and two unresolved
boundaries each. `make source` passes. Nothing was signed, flashed, installed,
reset, booted, or sent to hardware. Live timing, initializer side effects, and
cold-boot qualification is blocked by unavailable physical evidence; future qualification
requires authorized G2 physical evidence. Retained bootloader spans
after `0x0041FA40` remain software gaps, so firmware-wide completeness is not
claimed.

## Bootloader guarded teardown is production-routed (2026-08-26)

The complete guarded teardown `[0x0041FA98,0x0041FAD0)` now routes to
maintained clean-room C. Host coverage validates inactive guards, both
independent status failures and fail-stop selection, the successful state-word
clear, pin-28 configuration, and final guard clear. The sole caller and
following 12-byte literal pool are authenticated. Both reviewed Clang profiles
emit the same relocation-free 72-byte leaf, replacing all 56 stock body bytes.

Apple overlay/provider identities are 9,392 / 157,992 bytes with SHA-256
`2764ebb28ccde7977522ee318869a03805dfa2e0bc718c16de51c2ce4579828f` and
`0fa99abd573ab6a8845c3807cef69d29ee29d46606f1044bae6b571971dff659`;
Linux identities are 9,376 / 157,976 bytes with SHA-256
`66bb62b17d33dbdec3f1015299fee2f04cb435a15d8a335b98c64eb6d000dac6`
and `bddf904854256b0403d5750d756ca2b98d379434362918a94f876fa7c69e3427`.
Canonical accounting is 9,379 source-owned, 10,700 generated patch, 14
alignment, and 137,899 retained official bytes across 156 functions, 137
relocated leaves, and 154 patch sites.

The unsigned Apple/Linux packages are 4,739,570 / 4,515,564 bytes with
SHA-256 `f69e3c8e9d8fc2408a48eeff99e6d96cbbf55f77e052881a3260223bf2c7b779`
and `f92667c2f10b51cbd49129924bd4bf10c77145dccdc460e18840d4ebeadf8a72`.
Their flash plans contain 6,459 / 3,429 placed regions and two unresolved
boundaries each. Nothing was signed, flashed, installed, reset, booted, or
sent to hardware. Live teardown, fail-stop, pin, power-state, and cold-boot
qualification is blocked by unavailable physical evidence; future qualification requires
authorized G2 physical evidence. Retained bootloader spans around and
after `0x0041FAD0` remain software gaps, so firmware-wide completeness is not
claimed.

## Bootloader platform setup is production-routed (2026-08-26)

The complete boot platform setup `[0x0041FA50,0x0041FA98)` now routes to
maintained clean-room C. The 72-byte authenticated body has a sole caller at
`0x0041B87E`; host tests pin guarded teardown, reset/mode, the hard-float
`25.0f` derive boundary, exact 20-byte stock configuration copy/submit, and
channel-four/five call order. Both reviewed Clang profiles emit the same
relocation-free 96-byte leaf.

Apple overlay/provider identities are 9,488 / 158,088 bytes with SHA-256
`da89534353b40e8787963c24dc0aa6209b11948cd128b8d05115525685b53adc`
and `5283432f02f86b2c62dea8eac44c567f99b3c4d261c3412ab638b67535486145`;
Linux identities are 9,472 / 158,072 bytes with SHA-256
`1b97e43f2615b0281850b16c5f14aeb31bd6af3d792008bb62a9c60cff2b4b5b`
and `991fc763c08fdf890d18840d84b6a386864dae812757035faa4e216a1c4663e3`.
Canonical accounting is 9,475 source-owned, 10,772 generated patch, 14
alignment, and 137,827 retained official bytes across 157 functions, 138
relocated leaves, and 155 patch sites.

The unsigned Apple/Linux packages are 4,739,666 / 4,515,660 bytes with
SHA-256 `761b09380b08493d69eee02b2912cb1edeb6f14c584973df52d6bcf3e058dae1`
and `8a447d867e6303ed6075ad83067c53350a1e189956d2dc8c7ae6e93b287c12ea`.
Their flash plans contain 6,461 / 3,430 placed regions and two unresolved
boundaries each. Nothing was signed, flashed, installed, reset, booted, or
sent to hardware. Live reset, VFP callee, configuration/channel side effects,
pin/power state, and cold-boot qualification is blocked by unavailable physical evidence;
future qualification requires authorized G2 physical evidence. Retained
bootloader spans after `0x0041FAD0` remain software gaps, so firmware-wide
completeness is not claimed.

## Bootloader allocator initialization is production-routed (2026-08-26)

The complete allocator initializer `[0x0041FD70,0x0041FDA8)` now routes to
maintained clean-room C. The 56-byte authenticated body has one caller at
`0x0041B89E`; host tests pin the `0x20081000` / `0x70800` pool clear, retained
TLSF creation, handle publication at `0x2002718C`, diagnostic call and
arguments, zero return, and adjacent literal pools. Both reviewed Clang
profiles emit relocation-free 88-byte leaves.

Apple overlay/provider identities are 10,004 / 158,604 bytes with SHA-256
`a27f7ba39fdfe6a7364d59577cfa387a0a601aedf773612d1cb1b77700c6538d`
and `da312bd3b1a4105f75788107d147d5397edba0014c72d11584d5c9552c24cab7`;
Linux identities are 9,988 / 158,588 bytes with SHA-256
`15784fef039b93caaa26b202c61b115b4d0947f0ec253b7232dd43e828787b50`
and `a64974dce84415f4031847e1f71b5397cd0c366a31b8786d6f6e311ff53bd7b2`.
Canonical accounting is 9,991 source-owned, 11,366 generated patch, 14
alignment, and 137,233 retained official bytes across 159 functions, 140
relocated leaves, and 157 patch sites.

Unsigned Apple/Linux packages are 4,740,182 / 4,516,176 bytes with SHA-256
`8041ac27ae80d9cb331d27363281d7dfb259024a4276e80783bcca4b3e7a04a2`
and `7591a1ab14efac218d2610f2192f1b554c1f366ceb917ba911fc9059c8965bd6`.
Their flash plans contain 6,467 / 3,434 placed regions and two unresolved
boundaries each. Nothing was signed, flashed, installed, reset, booted, or
sent to hardware. Live allocator/SRAM/logging/cold-boot qualification is
blocked by unavailable physical evidence; future qualification requires authorized G2
physical evidence. Executable spans after `0x0041FDA8` remain software
gaps, so firmware-wide completeness is not claimed.

## Bootloader IRQ services are production-routed (2026-08-26)

The three complete entries `[0x0041FDC0,0x0041FE28)` now route to maintained
clean-room C: signed NVIC interrupt enable, external/system-handler priority,
and the vector-referenced MSPI status-clear-service wrapper. The 104 stock
bytes are replaced by 112 relocation-free Thumb bytes in both reviewed
toolchains. Host tests pin index/mask arithmetic, negative IRQ behavior,
priority encoding, MSPI handle/status propagation and call order; stock scans
pin both callers and the vector-table ingress.

Apple overlay/provider identities are 10,116 / 158,716 bytes with SHA-256
`f8088800044634921e2446b45e7133e0a9d3232e5ce5ad78f31eb6990b1e32b8`
and `1594aefde3a94be29dec7c4d3ab3ac20cf57e2a6f220f7eeca8609ffb222dede`;
Linux identities are 10,100 / 158,700 bytes with SHA-256
`ae413000d796c164e5bc06f197ff9bbf2543140d2ed6a50bfc62eecb225bb213`
and `34259f9296124eed2b7cebc3488994087b3308fc26383d78f82fd9948e568eae`.
Canonical accounting is 10,103 source-owned, 11,470 generated patch, 14
alignment, and 137,129 retained official bytes across 162 functions, 143
relocated leaves, and 160 patch sites.

Unsigned Apple/Linux packages are 4,740,294 / 4,516,288 bytes with SHA-256
`b2ce7f54b0d6fb58fe46c78d715f7498d9188dba826197225ad203db0bc64181`
and `c8c34b6acf8ed5b356f61334121e5c6d3bfc8628302bd3af4398192c83403a88`.
Their flash plans contain 6,474 / 3,438 placed regions and two unresolved
boundaries each. Nothing was signed, flashed, installed, reset, booted, or
sent to hardware. Live NVIC/MSPI/interrupt/cold-boot qualification is deferred
by project direction; future qualification requires authorized G2 physical
evidence. Executable spans after `0x0041FE28` remain software gaps, so
firmware-wide completeness is not claimed.
## Current bootloader MX25U25643G address-mode increment

The complete authenticated `[0x00420800,0x0042086C)` body now routes to
clean-room compilable C. Host tests pin zero initialization, command `0x15`,
bit-5 decoding, raw transport-error preservation, both diagnostics, and the
sole caller. Apple/Linux leaves are 124 bytes; provider identities are
161,400 / 161,384 bytes. Canonical accounting is 12,785 source-owned, 14,098
generated patch, 16 alignment, and 134,501 retained official bytes across 184
functions, 165 relocated leaves, and 182 patch sites. The Apple unsigned
package is 4,742,978 bytes with 6,519 placed and two unresolved physical
regions. No hardware operation occurred; live MSPI/external-flash/cold-boot
qualification is blocked by unavailable physical evidence; future qualification requires that evidence, and executable bodies from `0x0042086C` remain
software gaps.

## Current bootloader MX25U25643G enter-four-byte-mode increment

The complete authenticated `[0x00420890,0x00420978)` body now routes to
clean-room compilable C. Host tests pin handle and busy mappings, raw
write-enable/command/write-disable failures, command `0xB7`, the ignored
post-command ready result, the permissive nonzero verification quirk, exact
diagnostics, call order, and the sole caller. The preceding 36-byte literal
region remains authenticated retained data. Apple/Linux leaves are 220 bytes;
provider identities are 161,620 / 161,604 bytes with SHA-256
`25b1d6a8b3bda1d7cd4b28dab6472d7820f800bc3690bb2306f2b5cbd661880e`
and `e54af73c579e7f2749a696cf6d1eb34a7536d6b036f09730e63e03cea44ceee2`.
Canonical accounting is 13,005 source-owned, 14,330 generated patch, 16
alignment, and 134,269 retained official bytes across 185 functions, 166
relocated leaves, and 183 patch sites. The Apple unsigned package is
4,743,198 bytes with SHA-256
`f7d74c7ae574671b3677c8b94500305482fd89180e17eaa367c9358caaff44e7`;
its flash plan has 6,522 placed and two unresolved physical regions.

No hardware operation occurred. Live MSPI/external-flash/XIP/write-latch and
cold-boot qualification is blocked by unavailable physical evidence; future qualification
requires authorized G2 physical evidence. The 12-byte pool at
`[0x00420978,0x00420984)` remains retained data, and executable bodies starting
at `0x00420984` remain software gaps, so firmware-wide completeness is not
claimed.

## Current bootloader MX25U25643G write-latch increment

The complete authenticated write-enable `[0x00420984,0x004209BE)` and
write-disable `[0x004209C4,0x004209FC)` bodies now route to clean-room
compilable C. Host tests pin commands `0x06` and `0x04`, all-zero remaining
transfer fields, raw return statuses, failure-only diagnostics, four enable
callers, three disable callers, and the three surrounding retained literal
pools. Both profiles emit two relocation-free 72-byte leaves.

Apple/Linux overlay identities are 13,164 /
`42a790b4fa16eaa0a0a200afeb13d14bd2ec5a8b065e15fb62aeeba628483500`
and 13,148 /
`ad68bad4bad5ac349fa87c3518d935d6fe9b1039cd295d97f508b1d52524412c`;
provider identities are 161,764 /
`c9d14e63c54b3813bb527691b429f287a8eebfcce83b3bc9a0df03c87df8237e`
and 161,748 /
`165152971c636da8bf7fb939b44093681017f7b797e84bc0d68d4a10e11ee70d`.
Canonical accounting is 13,149 source-owned, 14,444 generated patch, 16
alignment, and 134,155 retained official bytes across 187 functions, 168
relocated leaves, and 185 patch sites. The Apple unsigned package is 4,743,342
bytes with SHA-256
`f0fa1999e7992a0a20ea3897185447b060ae3510e38e2ba3560c8651a9f69d7c`;
its flash plan has 6,528 placed and two unresolved physical regions.

No hardware operation occurred. Live write-latch/MSPI/external-flash/XIP and
cold-boot qualification is blocked by unavailable physical evidence; future qualification
requires authorized G2 physical evidence. The next executable function is
sector erase at `0x00420A08`; it remains a software gap, so firmware-wide
completeness is not claimed.

## Current bootloader MX25U25643G sector-erase increment

The complete authenticated `[0x00420A08,0x00420ADA)` body now routes to
clean-room compilable C. Host tests pin handle, 4-KiB alignment, 32-MiB bound,
guard and mode transitions, command `0x20`, ready/write-latch sequencing,
every failure status and diagnostic, unconditional cleanup, and the sole
caller. Both reviewed profiles emit relocation-free 244-byte leaves.

Apple/Linux overlay identities are 13,408 /
`936b166f4eec07cbb3fe5d988e80593354892caf7a875c7f972ffdb24bbfc4f3`
and 13,392 /
`fc0b9409eab2105fdfa6e22fad8f90660aff9f061452c8b5064e9f07333f9303`;
provider identities are 162,008 /
`873e843b1b2dcb5c96cdaf7e42f8705563ed5a1ca436811e0c3081415d3a9a1e`
and 161,992 /
`6510e26f2f627c2424dae20b13f856ef6ea3dcdf04223339f859364d259f1958`.
Canonical accounting is 13,393 source-owned, 14,654 generated patch, 16
alignment, and 133,945 retained official bytes across 188 functions, 169
relocated leaves, and 186 patch sites. The Apple unsigned package is 4,743,586
bytes with SHA-256
`9451c86c90a52643fa43cea465f2a82419a5d345b82f4b44e41ef02a5de39da0`;
its flash plan has 6,531 placed regions and two unresolved physical regions.

No hardware operation occurred. Live erase/write-latch/MSPI/external-flash/XIP
and cold-boot qualification is blocked by unavailable physical evidence; future
qualification requires authorized G2 physical evidence. A 50-byte retained pool/gap
precedes the program service at `0x00420B0C`, which remains a software gap, so
firmware-wide completeness is not claimed.

## Current bootloader MX25U25643G page-program increment

The complete authenticated `[0x00420B0C,0x00420C14)` body now routes to
clean-room compilable C. Host tests pin handle/buffer/length validation, the
32-MiB bound, first-page and subsequent 256-byte chunk arithmetic, guarded
mode changes, command `0x02`, per-page ready/write-latch sequencing, every
failure status and diagnostic, later-page failures, cleanup, and the sole
caller. Both reviewed profiles emit the same relocation-free 256-byte leaf.

Apple/Linux overlay identities are 13,664 /
`9b72a887df63cd94a36c45d73f8c1237e34db734b2c8dd91a4797110d3d8a395`
and 13,648 /
`ff1a490411cd440468370bc2b822ffd5a1673efbaad8ba504aa0a27afff379fa`;
provider identities are 162,264 /
`d02333f0a79d6d9d3fe5918330ffaa1365691dda1420fdad2165fb956b5cb7fb`
and 162,248 /
`5b7fd6cbdf5205c1292226e6eebe21cd2a8c0bff684dc9dfb4f9af114dd79b21`.
Canonical accounting is 13,649 source-owned, 14,918 generated patch, 16
alignment, and 133,681 retained official bytes across 189 functions, 170
relocated leaves, and 187 patch sites. The Apple unsigned package is 4,743,842
bytes with SHA-256
`1f3191b816b1e30cb82cd06653f63514a2174eebd942b44b92cf43152c4769dd`;
its flash plan has 6,534 placed regions and two unresolved physical regions.

No hardware operation occurred. Live page-program/write-latch/MSPI/
external-flash/XIP and cold-boot qualification is blocked by unavailable physical evidence;
future qualification requires authorized G2 physical evidence. A 72-byte
retained pool precedes the next executable function at `0x00420C5C`, which
remains a software gap, so firmware-wide completeness is not claimed.

## Current bootloader MX25U25643G QE increment

The complete authenticated `[0x00420C5C,0x00420DFA)` body now routes to
clean-room compilable C. Seven host tests pin the fixed-handle rejection,
commands `0x05` and `0x01`, QE bit 6, protection mask `0x3C`, both deliberately
ignored ready results, raw read/enable/write failures, verification mismatch,
the low-byte non-Boolean request quirk, exact diagnostics, the sole caller,
and the 14-byte successor pool. Both reviewed profiles emit the same
relocation-free 364-byte leaf.

Apple/Linux overlay identities are 14,028 /
`ed9269c05166de01a402d2a2be5a975ea36a35d4db0edd13ac879afb836f0407`
and 14,012 /
`de523ff3514355dfccc201ca23b6f06fe95b75671f1c71835e898808d635c974`;
provider identities are 162,628 /
`bd830dafab1c1e9de59e7abce980e7461f3d440b0e5121ab27735513903ffd10`
and 162,612 /
`5d6c596921690cadc11cd902d6c21dc988d48fd6e9675b481423187a6afe35ab`.
Canonical accounting is 14,013 source-owned, 15,332 generated patch, 16
alignment, and 133,267 retained official bytes across 190 functions, 171
relocated leaves, and 188 patch sites. The Apple unsigned package is 4,744,206
bytes with SHA-256
`43022429372d51be6a9083eed987cb6fb0c38b1e4504e0fbe82e81c2f34d5971`;
its flash plan has 6,537 placed regions and two unresolved physical regions.

No hardware operation occurred. Live QE/status-register/write-latch/MSPI/
external-flash/XIP and cold-boot qualification is blocked by unavailable physical evidence;
future qualification requires authorized G2 physical evidence. The 14-byte
retained pool at `0x00420DFA` precedes the next executable function at
`0x00420E08`, which remains a software gap, so firmware-wide completeness is
not claimed.

## Current authenticated bootloader frontier

The subsequent MSPI device-reconfiguration entry
`[0x00420E08,0x00420E8C)` is now source-routed and fully gated as documented
in `research/g2-bootloader-mspi-device-reconfigure-420e08-420e8c-source-closure.md`.
Current Apple/Linux overlays are 14,164 / 14,140 bytes and providers are
162,764 / 162,740 bytes. Canonical accounting is 14,149 source-owned, 15,464
generated patch, 16 alignment, and 133,135 retained official bytes. The next
software frontier is the executable entry at `0x00420E8C`. Hardware-dependent
validation is blocked by unavailable physical evidence; future qualification requires authorized physical
evidence, and functional completeness is not claimed.

## Current bootloader MX25U25643G quad-mode increment

The complete authenticated `[0x00420E8C,0x00420F0C)` body now routes to
clean-room compilable C. Five host tests pin the exact 24-byte template clone,
the four field mutations, reconfiguration failure short-circuit, XIP enable,
HAL control request `0x18`, mode byte `0x10`, both diagnostic records, void
completion, three stock callers, and Cortex-M55 compilation. Both reviewed
profiles emit 152-byte leaves with three strict source-to-source relocations.

Apple/Linux overlay identities are 14,316 /
`b45e00780fb3b625fadbac462836f7bc2f4850d761d3f488dee4c6d2e502f59f`
and 14,292 /
`328abf5c6e1c5d592e6198e24e1d24f1e7b379eac6f72f886906289f08e0a74a`;
provider identities are 162,916 /
`d2ebed1a9d3191ab184c9405993b21de4b7c4bd9be0662b4439e0be140871f8f`
and 162,892 /
`f9f5fe87e4a8b07245dd23d8e385f359b930eedcdcb71df9c48bfb95aee6db3d`.
Canonical accounting is 14,301 source-owned, 15,592 generated patch, 16
alignment, and 133,007 retained official bytes across 192 functions, 173
relocated leaves, and 190 patch sites. The Apple unsigned package is 4,744,494
bytes with SHA-256
`caf999acbe2b7c172da62a3fbec502f4a82b9181c9e470cb07473e4c8639234f`;
its flash plan has 6,542 placed regions and two unresolved physical regions.
The Linux unsigned package is 4,520,480 bytes with SHA-256
`bfde66dc0c3457995eeffe0c11b9a8aecb6b4a325407d9400171d5666ab10af2`.

No hardware operation occurred. Live template initialization, HAL, pinmux,
MSPI, XIP, external-flash, and cold-boot qualification is deferred by project
direction; future qualification requires authorized G2 physical evidence.
The four-byte `[0x00420F0C,0x00420F10)` literal pool remains retained; the
next opaque executable entry begins at `0x00420F10`, so firmware-wide
functional completeness is not claimed.

## Current bootloader MX25U25643G serial-mode increment

The complete authenticated `[0x00420F10,0x00420F6A)` body now routes to
clean-room compilable C. Five focused tests pin its serial-configuration seam,
reconfiguration failure short-circuit, XIP disable, HAL control request
`0x18`, zero mode byte, exact diagnostic records, void completion, four stock
callers, successor gap, and Cortex-M55 compilation. Both reviewed profiles
emit 124-byte leaves with two strict source-to-source relocations.

Apple/Linux overlay identities are 14,440 /
`b238c479b5e41d1fccc07b42328636fb4cfa570b660bc44d919c6e6dda8988d2`
and 14,416 /
`e9db16d933b638422b1b798dbe9619c543d63622afe2acd5dbd61c89699b10de`;
provider identities are 163,040 /
`9afda4d9585fa153fdb38f6539069aa48e74100a20f015e72c883d7416318fae`
and 163,016 /
`a364ae072e1f76cfe71a7a5fc64bab1aa7732797cf4d29195f942d9f50d8d3ca`.
Canonical accounting is 14,425 source-owned, 15,682 generated patch, 16
alignment, and 132,917 retained official bytes across 193 functions, 174
relocated leaves, and 191 patch sites. The Apple unsigned package is 4,744,618
bytes with SHA-256
`e436759ab14c5a967632d4c993a4313c28b00f384a4e78f54cac5e804ca5dad9`;
its 4,554,031-byte flash plan has SHA-256
`e78f9e19debe8e99202faf251eb278dd90f695d53973ff165d1933fd3163f07d`,
6,545 placed regions, and two unresolved physical regions. The Linux unsigned
package is 4,520,604 bytes with SHA-256
`fa956f608b507d2429414d7cebd45f77f678953db8b3916a5975cc3e31196657`.

The complete `make bootloader-numeric-closure` gate passes 322 tests plus
snapshot, exact-routing, provider, analyzer, package, and flash-plan checks.
No hardware operation occurred. Live initialized-SRAM, HAL, pinmux, MSPI,
XIP, external-flash, and cold-boot qualification is blocked by unavailable physical evidence;
future qualification requires authorized G2 physical evidence.
The six-byte `[0x00420F6A,0x00420F70)` successor gap remains retained; the next
opaque executable entry begins at `0x00420F70`, so firmware-wide functional
completeness is not claimed.

## Current bootloader MX25U25643G guarded-read increment

The complete authenticated `[0x00420F70,0x00420FF2)` body now routes to
clean-room compilable C. Five focused tests pin the authenticated body,
predecessor gap, successor pool, direct littlefs caller, validation/status
mapping, transaction ordering, ignored ready-wait result, exact 24-byte
`0x006C` read descriptor, `1000000` timeout, raw HAL return, guard release,
and Cortex-M55 compilation. Both reviewed profiles emit 152-byte leaves with
four strict source-to-source relocations.

Apple/Linux overlay identities are 14,592 /
`b859abdddf191758b89dad26e6e4a4627da3cb4589db29d3da8dbf7d28ee82c6`
and 14,568 /
`589400cae19f47b61b388952a4c08e37f51948905bc5d7a45c314ee0d46ff045`;
provider identities are 163,192 /
`57b82aaa300029154900d1d817e565fd558a580fa6d76788cba2a8535379b37c`
and 163,168 /
`0a46478d1d7a03959f0809334f2ee1416d94983805270d093bd82d79e2edb9ae`.
Canonical accounting is 14,577 source-owned, 15,812 generated patch, 16
alignment, and 132,787 retained official bytes across 194 functions, 175
relocated leaves, and 192 patch sites. The Apple unsigned package is 4,744,770
bytes with SHA-256
`1d362e7f70d55b026361669a2b4c600a7b80c5b6a2e7570b0d386c7975e9d410`;
its 4,556,102-byte flash plan has SHA-256
`543047ab613f26906de128a6748f1ca860103e176f23eb226990313e205f7fe9`,
6,548 placed regions, and two unresolved physical regions. The Linux unsigned
package is 4,520,756 bytes with SHA-256
`8d4418b8a6e959d31ec10d5079a8ee5125950951555116029990c92ac405b0ac`.

The complete `make bootloader-numeric-closure` gate passes 327 tests plus
snapshot, littlefs-port, exact-routing, provider, analyzer, package, and
flash-plan checks. No hardware operation occurred. Live HAL, pinmux, MSPI,
XIP, external-flash read, littlefs, and cold-boot qualification is deferred by
project direction; future qualification requires authorized G2 physical
evidence. The 214-byte `[0x00420FF2,0x004210C8)`
successor pool remains retained;
the next opaque executable entry begins at `0x004210C8`, so firmware-wide
functional completeness is not claimed.

## Current bootloader LittleFS directory-bootstrap increment

The complete authenticated `[0x004210C8,0x004211B0)` body now routes to
clean-room compilable C. Five focused tests pin the predecessor pool,
successor initializer, four path literals, both callers, fixed filesystem
object, 52-byte directory handle, present/create/already-exists/nonfatal-mkdir
branches, ignored close result, fatal unexpected-open result, early stop, and
Cortex-M55 compilation. Apple/Linux emit 220/224-byte leaves with two strict
relocations to their source-owned EasyLogger output leaves.

Apple/Linux overlay identities are 14,812 /
`b905e2c189923c066846c170cea5a7cc0846d46167e7776b365fa4847b341077`
and 14,792 /
`0771eb5b5e297b6d5cb2336cd5f9b3f0ad75ac40021f30621f5c73e79b01e341`;
provider identities are 163,412 /
`bc6a6219ba7e2122b85226f4e6410fd4c3d8d12a19669ad8088efd8f5db657ff`
and 163,392 /
`a6f58437a7ed56269d11aabb89df892f1478c10601b30e0594acf66d2a640cf8`.
Canonical accounting is 14,797 source-owned, 16,044 generated patch, 16
alignment, and 132,555 retained official bytes across 195 functions, 176
relocated leaves, and 193 patch sites. The Apple unsigned package is 4,744,990
bytes with SHA-256
`c4ba624de37c01d582906ccb12e0f32754e26aa56e81cc07f64baeeb5611f4ff`;
its 4,558,294-byte flash plan has SHA-256
`dc4b362e725457613d19bb82bd2ea4280b4151ecc50617d98acce6b44eb130e8`,
6,551 placed, two unresolved, five container-only, and six protected regions.
The Linux unsigned package is 4,520,980 bytes with SHA-256
`383530bba102ce67f95626d87344cba4bc2c382904d3ff76616ad51b67b2d35c`.

The expanded `make bootloader-numeric-closure` gate passes 332 tests plus
snapshot, littlefs-port, exact-routing, provider, analyzer, package, and
flash-plan checks. No hardware operation occurred. Live mount,
directory mutation, external-flash persistence, power-loss, logging, and
cold-boot qualification is blocked by unavailable physical evidence; future qualification
requires authorized G2 physical evidence. The next opaque executable
entry begins at `0x004211B0`, so firmware-wide functional completeness is not
claimed.

## Current bootloader LittleFS format/bootstrap increment

The complete authenticated `[0x004211B0,0x00421210)` body now routes to
clean-room compilable C. Five focused tests pin the body, 200-byte successor,
six direct calls, fixed filesystem/configuration objects, sole caller,
unmount/format/mount/bootstrap sequencing, ignored unmount and format results,
mount and directory failure diagnostics, status `9`, early stop, and
Cortex-M55 compilation. Apple/Linux emit 108/112-byte leaves with two strict
source-to-source relocations.

Apple/Linux overlay identities are 14,920 /
`360c37433d555f50a9bf117e9d7c029708e2a3ef1c996892fb846b657aaaa257`
and 14,904 /
`9576b3c3024ceda0269d2a947cc9fc7f460e0730af80f4a50d122fccfbd0602f`;
provider identities are 163,520 /
`52d2d2e27cbfff363d18010650dd7751bbdbfbc0acffef731e416df47835c270`
and 163,504 /
`59f841fe1197395dcebbc0c550d4080106da2984fdd477d2fd28dc09431210b8`.
Canonical accounting is 14,905 source-owned, 16,140 generated patch, 16
alignment, and 132,459 retained official bytes across 196 functions, 177
relocated leaves, and 194 patch sites. The Apple unsigned package is 4,745,098
bytes with SHA-256
`d91b1a7aa58deb5e10499569fe12754b37bc589e9ab4df768c956cd1fc766d19`;
its 4,559,746-byte flash plan has SHA-256
`e6c01bac8cc86b4cb3f71c5a09eb3ff64b0e7563c8e7bef39903112e5f8723ad`,
6,553 placed, two unresolved, five container-only, and six protected regions.
The Linux unsigned package is 4,521,092 bytes with SHA-256
`c0e06590e74ec97dc5b7474df610d0e557013e5a0d95ef5c1f0cc972eadb2a42`.

The expanded `make bootloader-numeric-closure` gate passes 337 tests plus
snapshot, littlefs-port, exact-routing, provider, analyzer, package, and
flash-plan checks. No hardware operation occurred. Live unmount/format/mount,
external-flash erase/program/persistence, power-loss, diagnostics, and
cold-boot qualification is blocked by unavailable physical evidence; future qualification
requires authorized G2 physical evidence. The next opaque executable
entry begins at `0x00421210`, so firmware-wide functional completeness is not
claimed.

## Current bootloader LittleFS initializer/boot-counter increment

The complete authenticated `[0x00421210,0x004212D8)` body now routes to
clean-room compilable C. Six focused tests pin the 200-byte stock body, the
56-byte successor callback, sole caller, call and literal identities, first
mount success, format-and-retry behavior, second-mount failure mapping,
directory-recovery behavior, readiness publication, ignored file-operation
results, persisted `boot_count` increment, diagnostics, and Cortex-M55
compilation. Apple and Linux both emit 260-byte leaves with five strict
relocations to source-owned logging, directory-bootstrap, and recovery-format
leaves.

Apple/Linux overlay identities are 15,180 /
`18ce465a9a646bddad5cd7c663c0f4dfeb7b76fd93d1ad1cc48510f3d8dcd8e4`
and 15,164 /
`cab5d1a63bea87ea7d6d07041240cd61859a84dbb192f68a51c653124c35f22a`;
provider identities are 163,780 /
`566895485d661ce696f4bcadd396f0f1f512fae92630f4f3c5315d67849bd5bd`
and 163,764 /
`52feb01f0dc3a68d7f0c7fb4ffadb19a247f17d151fc175f97afde5f5433d4d9`.
Canonical accounting is 15,165 source-owned, 16,340 generated patch, 16
alignment, and 132,259 retained official bytes across 197 functions, 178
relocated leaves, and 195 patch sites. The Apple unsigned package is 4,745,358
bytes with SHA-256
`61a74ed44990d4fd5b2663b7fe0d68ffbef7a9f6afc3fb364854631ad6a0e15d`;
its 4,561,240-byte flash plan has SHA-256
`c17a375878bb05229f8cfad7b7c3c105633289f9c4309b08b3c95f00c56e9f79`,
6,555 placed, two unresolved, five container-only, and six protected regions.
The Linux unsigned package is 4,521,352 bytes with SHA-256
`da9d13f90cbdd353104c81dfcba426eda994dff41aefb862bb9e5580322fd85f`.

The expanded `make bootloader-numeric-closure` gate passes 343 tests plus
snapshot, littlefs-port, exact-routing, provider, analyzer, package, and
flash-plan checks. No hardware operation occurred. Live mount/format,
directory mutation, readiness visibility, boot-counter persistence,
external-flash behavior, power-loss, diagnostics, and cold-boot qualification is
blocked by unavailable physical evidence; future qualification requires authorized G2
physical evidence. The next opaque executable
entry begins at `0x004212D8`,
so firmware-wide functional completeness is not claimed.

## Current bootloader LittleFS block-read increment

The complete authenticated `[0x004212D8,0x00421310)` callback now routes to
freestanding clean-room C. Five focused tests pin the stock body, successor
program callback, LittleFS configuration pointer, device-driver and logger
calls, partition address calculation including 32-bit wrap, successful
forwarding, full failure diagnostic tuple, `LFS_ERR_IO` mapping, and
Cortex-M55 compilation. Both reviewed toolchains emit identical 60-byte raw
leaves with two strict source-to-source relocations.

Apple/Linux overlay identities are 15,240 /
`d68bca1fc09b1b734a65a706e9d5a4d5aa4201e53441f6ad1354be44f428b314`
and 15,224 /
`2dad91f7403219c30fee3130d62833c98561c8fb56387960f0654723ceed67ca`;
provider identities are 163,840 /
`d98fa4fe7f8c01ebcc29219d7cd604a16eb702df85fbb04f1c15be9808c0cfdf`
and 163,824 /
`33dfd33af4e3018e2717da8e171ce59aa7772d3fabee933c2a24240bc59b5f36`.
Canonical accounting is 15,225 source-owned, 16,396 generated patch, 16
alignment, and 132,203 retained official bytes across 198 functions, 179
relocated leaves, and 196 patch sites. The Apple unsigned package is 4,745,526
bytes with SHA-256
`41bb328e816ea68ad35b003ff63b3912a708bb72a987ec104047b79264b3a1e7`;
its 4,562,636-byte flash plan has SHA-256
`f54d4336bb011546efce564defe697e9de93b820821759ac767fd6853de3feac`,
6,557 placed, two unresolved, five container-only, and six protected regions.
The Linux unsigned package is 4,521,412 bytes with SHA-256
`50fdf76b2bc0ced7be5a817962153281cdd5823e80d94a12fcc4b2368789d876`.

The expanded `make bootloader-numeric-closure` gate passes 348 tests plus
snapshot, littlefs-port, exact-routing, provider, analyzer, package, and
flash-plan checks. No hardware operation occurred. Live MSPI/NOR reads,
partition-range behavior, filesystem reads, concurrency, diagnostics, and
cold-boot qualification is blocked by unavailable physical evidence; future qualification
requires authorized G2 physical evidence. The Apple provider now ends
exactly at `0x00438000`; future source closure must use authenticated reclaimed
body space. The next opaque executable entry begins at `0x00421310`, so
firmware-wide functional completeness is not claimed.

## Current bootloader Ambiq debug-service increment

The three-function, 268-byte cluster `[0x00422468,0x00422574)` is now
maintained BSD-3-Clause C and reproduces the installed stock bodies exactly
under both reviewed Cortex-M55 compilers. Its debug enable-count shutdown,
debug-power ownership and `DEMCR.TRCENA` release behavior matches public
AmbiqSuite SDK 5.1.0 `am_hal_debug.c`. Five focused tests cover nested/last
users, prior-domain ownership, register clearing and polling, bodies, pools,
callers, and dual-toolchain compilation. Nine strict calls are pinned.

Canonical accounting is 19,559 source-owned, 16,528 generated patch, 16
alignment, and 127,737 retained official bytes across 239 source-owned
functions, five caves, 36 exact in-place leaves, and 201 patch sites. The
4,601,055-byte flash plan has SHA-256
`86eb2b27d03838ed63186d44aa8d1077aafd8767a5b381c36fadc1ce29ed66cf`
with 6,611 placed regions; provider and package hashes remain unchanged.

No hardware operation occurred. Live debug-domain power, MCUCTRL/DCB effects,
trace quiescence and timing is blocked by unavailable physical evidence; future qualification requires authorized evidence.
After the authenticated 28-byte literal pool, the next executable body begins
at `0x00422590`; firmware-wide functional completeness is not claimed.

## Current bootloader mode-routing and all-row cleanup increment

The four-function, 320-byte cluster `[0x004222F0,0x00422430)` is now
maintained C and reproduces every installed stock byte under both reviewed
Cortex-M55 compilers. Five focused tests cover all seven enable/disable routes,
invalid kind and client-bit bounds, selective seven-row cleanup, fixed 20-byte
configuration copy, null rejection, body/successor pins, and dual-toolchain
compilation. Seventeen strict calls bind the maintained row services and bitmap
query plus the reviewed route alias and retained memcpy provider.

Canonical accounting is 19,291 source-owned, 16,528 generated patch, 16
alignment, and 128,005 retained official bytes across 236 source-owned
functions, five caves, 33 exact in-place leaves, and 201 patch sites. The
4,598,235-byte flash plan has SHA-256
`e1a4ef389dec567d8afe71061e5659cfba7a016e3ed2d5fbae7323b198115df4`
with 6,607 placed regions; provider and package hashes remain unchanged.

No hardware operation occurred. Live bitmap ownership, routed service effects,
cleanup concurrency, configuration persistence, and physical mode behavior
is blocked by unavailable physical evidence; future qualification requires authorized evidence. After the authenticated
56-byte literal pool, the next opaque executable body begins at `0x00422468`;
firmware-wide functional completeness is not claimed.

## Current bootloader row-five client-service increment

The complete two-function, 504-byte cluster
`[0x00421EBA,0x004220B2)` is now maintained C and reproduces both installed
stock bodies exactly under both reviewed Cortex-M55 compilers. Seven focused
tests cover existing-client timeout refresh, first-client selector enable and
commit, both rollback paths, absent/nonfinal/final disable, literal/successor
pins and dual-toolchain compilation. Twenty-six strict calls bind source-owned
bitmap, critical, selector-mode and cleanup services plus retained dual
switch/commit/null-commit providers.

Canonical accounting is 18,463 source-owned, 16,528 generated patch, 16
alignment, and 128,833 retained official bytes across 229 source-owned
functions, five caves, 26 exact in-place leaves and 201 patch sites. The
4,591,243-byte flash plan has SHA-256
`442828e94f28cfddc078420b99a16ae9a8a8cb888a1dcc09885b95ff9fe1c93f`
with 6,597 placed regions; provider and package hashes remain unchanged.

No hardware operation occurred. Live interrupt, retained dual-provider,
bitmap/state, selector-mode and physical row-five behavior remains blocked by
future-required authorized evidence. The next opaque executable body begins at
`0x004220B2`; firmware-wide functional completeness is not claimed.

## Current bootloader row-six and mode-dispatch increment

The 348-byte row-six enable, 110-byte disable and 50-byte mode dispatcher in
`[0x004220B2,0x004222D2)` are now maintained C and reproduce all installed
executable bytes exactly under both reviewed Cortex-M55 compilers. The two
18-byte literal seams remain retained official data. Seven focused tests cover
first/existing clients, readiness and start rollback, absent/nonfinal/final
disable, dispatcher routing, body/seam pins and dual-toolchain compilation.
Thirty-one strict calls bind maintained bitmap, critical, selector-mode and
mode-family services plus retained handle lifecycle providers.

Canonical accounting is 18,971 source-owned, 16,528 generated patch, 16
alignment, and 128,325 retained official bytes across 232 source-owned
functions, five caves, 29 exact in-place leaves and 201 patch sites. The
4,594,698-byte flash plan has SHA-256
`462379978f2f8ef4a6299a88ea98370be2911f3fbfd0a0606af9c24551e0117f`
with 6,602 placed regions; provider and package hashes remain unchanged.

No hardware operation occurred. Live interrupt, retained handle-provider,
bitmap/state, selector-mode and physical row-six behavior remains blocked by
future-required authorized evidence. After the authenticated padding/literal seam,
the next executable body begins at `0x004222F0`; firmware-wide functional
completeness is not claimed.

## Current bootloader LittleFS block-program increment

The complete authenticated `[0x00421310,0x00421348)` callback now routes to a
60-byte freestanding clean-room C leaf at `[0x00421214,0x00421250)`. Five
focused tests pin the stock body, successor erase callback, configuration
pointer, source-owned driver/logger calls, 32-bit address wrap, forwarding,
failure diagnostic tuple, `LFS_ERR_IO` mapping, and Cortex-M55 compilation.
The fixed-address placement is confined to authenticated NOP fill in the
already-replaced initializer body; negative tests reject an out-of-tail cave
and a forged NOP digest.

Apple/Linux provider identities are 163,840 /
`ef42f8f927e07a2962e4a9c9436c6cf4df24dc6cf5206f09823f5ad42afba410`
and 163,824 /
`2d09f6ba1ed39fc2f7bf3c658d2ef884c2596d6d666455b22fba1b9638ee0004`.
Canonical accounting is 15,285 source-owned, 16,392 generated patch, 16
alignment, and 132,147 retained official bytes across 199 routed functions,
179 relocated leaves, one fixed cave, and 197 patch sites. The Apple unsigned
package is 4,745,526 bytes with SHA-256
`ca6c0ac3fb5c1c7c4ef7b83cc184d671133a671cd9027310e3214e1fba2312c0`;
its 4,564,800-byte flash plan has SHA-256
`29dcb55776458fcd0a181850afba054754a3618242ca9052ce7bb22505837736`,
6,560 placed, two unresolved, five container-only, and six protected regions.
The Linux package is 4,521,412 bytes with SHA-256
`0298e63de18eaaac5874c27da786fe3113e090d2e52550f253f1930156fba901`.

No hardware operation occurred. Live MSPI/NOR programming, filesystem writes,
persistence, power-loss, diagnostics, and cold-boot qualification is deferred by
project direction; future qualification requires authorized G2 physical evidence.
The next opaque executable entry begins at `0x00421348`; firmware-wide
functional completeness is not claimed.

## Current bootloader mapped-memory selector increment

The authenticated primary selector `[0x004213E6,0x00421548)` and its
odd-selector wrapper `[0x00421548,0x0042156E)` now route to 220-byte and
30-byte clean-room C leaves placed inside the primary replacement span. Five
focused tests pin the complete stock bodies, selector/capacity matrix,
security-bit gating, 32-bit bounds behavior, exact mapped-memory roots,
identity/threshold helper calls, copy forwarding, wrapper filtering, and both
reviewed Cortex-M55 compilers.

Apple/Linux providers are 163,840 /
`8f24989979719b4c9f1273624240ba702a99decf735d099bfee1afcda16159e0`
and 163,824 /
`efef1a9b039548ab9332651921e8a7864ce8df205bfe22c9ae6e13c0c81cb635`.
Canonical accounting is 15,601 source-owned, 16,528 generated patch, 16
alignment, and 131,695 retained official bytes across 205 functions, five
authenticated fixed-address caves, two exact in-place leaves, and 201 patch
sites. Apple/Linux unsigned packages are 4,745,526 /
`3c8cdcdb4bc56b1a76b5ddabe6eb1bc79810aa6a99cf35acaec6bd019179c785`
and 4,521,412 /
`9438fb68b25110b5c03309e868e5baa78e6989a88c3597d939ef7017ef28543e`.
The 4,573,512-byte flash plan has SHA-256
`e8f4afaf8b838eaa359360309d36ae5c36b664b28973fe011cc84c51a678a58c`
and 6,572 placed regions.

No hardware operation occurred. The retained 22-byte pool through
`0x00421584` is authenticated non-executable data. Live register, security,
mapped-memory, copy, concurrency, and cold-boot qualification is blocked by unavailable physical evidence; future qualification requires authorized physical evidence. The next opaque executable body
begins at `0x00421584`; firmware-wide functional completeness is not claimed.

## Current bootloader population-count increment

The complete 42-byte helper `[0x00421584,0x004215AE)` is now maintained C and
reproduces its stock body exactly under Apple clang 21 and Homebrew clang
22.1.8. Three tests pin its sole direct caller, exercise boundary patterns and
512 deterministic random words, and verify both Cortex-M55 compilations.

Canonical accounting is 15,643 source-owned, 16,528 generated patch, 16
alignment, and 131,653 retained official bytes across 206 source-owned
functions, five caves, three exact in-place leaves, and 201 patch sites. The
provider and unsigned-package hashes are unchanged. The 4,574,891-byte flash
plan has SHA-256
`23b0b3a47a662696d5f26f05be7b375dece06726b2f5c3352f62bb199f5c814b`
with 6,574 placed regions.

No hardware operation occurred. The next opaque executable body begins at
`0x004215AE`; its table-backed behavior and physical register/memory effects
remain open. Firmware-wide functional completeness is not claimed.

## Current bootloader two-word bitmap-helper increment

The complete three-helper cluster `[0x004215AE,0x00421632)` is now maintained
C and reproduces all 132 stock bytes exactly under Apple clang 21 and Homebrew
clang 22.1.8. Five focused tests pin the bodies, table root at `0x20026E74`,
and popcount call; exercise nonempty, membership, selector narrowing, two-word
layout, and count behavior; and verify both Cortex-M55 compilations. The count
leaf's sole relocation is a strict call to the source-owned population-count
helper at `0x00421584`.

Canonical accounting is 15,775 source-owned, 16,528 generated patch, 16
alignment, and 131,521 retained official bytes across 209 source-owned
functions, five caves, six exact in-place leaves, and 201 patch sites. Provider
and unsigned-package hashes remain unchanged. The 4,577,013-byte flash plan
has SHA-256
`b3d6202b548907ee00c12279378c888dca7907405684910171dcb6af7d53ae24`
with 6,577 placed, two unresolved, five container-only, and six protected
regions.

No hardware operation occurred. Live table ownership, concurrent mutation,
and downstream register/memory qualification is blocked by unavailable physical evidence;
future qualification requires authorized G2 physical evidence. The next
opaque executable body begins at `0x00421632`; firmware-wide functional
completeness is not claimed.

## Current bootloader validated bitmap-update increment

The complete 128-byte helper `[0x00421632,0x004216B2)` is now maintained C
and reproduces its stock body exactly under Apple clang 21 and Homebrew clang
22.1.8. Five focused tests pin the body, table root and successor; exercise
selector/bit validation, low-byte narrowing, both words, boundary bits,
set/clear behavior, unrelated-bit preservation, and enable normalization; and
verify both Cortex-M55 compilations. The installed leaf has no executable
relocation.

Canonical accounting is 15,903 source-owned, 16,528 generated patch, 16
alignment, and 131,393 retained official bytes across 210 source-owned
functions, five caves, seven exact in-place leaves, and 201 patch sites.
Provider and unsigned-package hashes remain unchanged. The 4,577,708-byte
flash plan has SHA-256
`7ffaee3c38fba6872efdaf94580d199a4e4facc3d569766cb35e77777f9c2c23`
with 6,578 placed regions.

No hardware operation occurred. Live table ownership, concurrency, and
read-modify-write atomicity qualification is blocked by unavailable physical evidence;
future qualification requires authorized G2 physical evidence. The next
opaque executable body begins at `0x004216B2`; firmware-wide functional
completeness is not claimed.

## Current bootloader bounded poll-delay increment

The complete 34-byte helper `[0x004216B2,0x004216D4)` is now maintained C
and reproduces its installed stock body exactly under Apple clang 21 and
Homebrew clang 22.1.8. Five focused tests pin the body, retained delay call,
successor and three callers; exercise both short circuits, counter exhaustion,
and a flag change during delay; and verify both Cortex-M55 compilations. Its
sole relocation binds the duration-10 call to `0x0041D1C0`.

Canonical accounting is 15,937 source-owned, 16,528 generated patch, 16
alignment, and 131,359 retained official bytes across 211 source-owned
functions, five caves, eight exact in-place leaves, and 201 patch sites.
Provider and unsigned-package hashes remain unchanged. The 4,578,404-byte
flash plan has SHA-256
`9fce38cd17a480199e97cc3b624b679b98d3d5111db06af281b2f2d96eb41a13`
with 6,579 placed regions.

No hardware operation occurred. Live delay timing, asynchronous flag updates,
volatile-memory visibility, and caller integration qualification is deferred by
project direction; future qualification requires authorized G2 physical evidence.
The next opaque executable body begins at `0x004216D4`; firmware-wide
functional completeness is not claimed.

## Current bootloader mode/configuration-service increment

The complete 254-byte service `[0x004216D4,0x004217D2)` is now maintained C
and reproduces its installed stock body exactly under Apple clang 21 and
Homebrew clang 22.1.8. Seven focused tests pin the body, default/literal seams,
dispatcher caller and successor; exercise validation, query/default merge,
early query failure, busy apply/fallback, idle disable/clear, publication and
interrupt restore; and verify both Cortex-M55 compilations. Eight strict calls
bind query, critical-save, source-owned bitmap count, apply/disable, fallback,
and source-owned copy providers.

Canonical accounting is 16,191 source-owned, 16,528 generated patch, 16
alignment, and 131,105 retained official bytes across 212 source-owned
functions, five caves, nine exact in-place leaves, and 201 patch sites.
Provider and unsigned-package hashes remain unchanged. The 4,579,118-byte
flash plan has SHA-256
`a5193f45000c8cfcc122610a6e9cfe359931aacc005bb9b1d749d3f4c02300f0`
with 6,580 placed regions.

No hardware operation occurred. Live interrupt timing, controller/register
behavior, shared-state ownership, and physical-mode qualification is deferred by
project direction; future qualification requires authorized G2 physical evidence.
The next opaque executable body begins at `0x004217D2`; firmware-wide
functional completeness is not claimed.

## Current bootloader dual-mode transaction increment

The complete 422-byte service `[0x004217D2,0x00421978)` is now maintained C
and reproduces its installed stock body exactly under Apple clang 21 and
Homebrew clang 22.1.8. Eight focused tests pin its body, literals, dispatcher
caller and successor; exercise validation, both controller-query routes,
early query failure, busy incompatibility, successful enable/commit/cleanup,
and failure cleanup; and verify both Cortex-M55 compilations. Sixteen strict
calls bind query, critical-save, source-owned bitmap count and copy, both mode
enable/disable families, and commit providers.

Canonical accounting is 16,613 source-owned, 16,528 generated patch, 16
alignment, and 130,683 retained official bytes across 213 source-owned
functions, five caves, ten exact in-place leaves, and 201 patch sites.
Provider and unsigned-package hashes remain unchanged. The 4,579,844-byte
flash plan has SHA-256
`2a34cd666945adc7929451a5b56bc7432b0519a7419f4c47bc8c24da0a5aff1e`
with 6,581 placed regions.

No hardware operation occurred. Live interrupt timing, controller/register
behavior, shared-state ownership, and physical-mode qualification is deferred by
project direction; future qualification requires authorized G2 physical evidence.
The next opaque executable body begins at `0x00421978`; firmware-wide
functional completeness is not claimed.

## Current bootloader bitmap-client service increment

The complete five-function, 400-byte cluster
`[0x00421978,0x00421B08)` is now maintained C and reproduces every installed
stock body exactly under Apple clang 21 and Homebrew clang 22.1.8. Seven
focused tests cover controller query/validation, busy and failure paths,
publication, idempotent low-byte row-zero/row-one mutation, the guarded
row-one set path, and both Cortex-M55 profiles. Sixteen strict calls bind
query, critical-save, source-owned bitmap count/test/update and copy providers.

Canonical accounting is 17,013 source-owned, 16,528 generated patch, 16
alignment, and 130,283 retained official bytes across 218 source-owned
functions, five caves, 15 exact in-place leaves, and 201 patch sites. Provider
and unsigned-package hashes remain unchanged. The 4,583,419-byte flash plan
has SHA-256
`35e18ba118c505f5e13ad1f498e39a1d81b228128f594a03f761c5a557b6e270`
with 6,586 placed regions.

No hardware operation occurred. Live interrupt timing, controller/register
behavior, shared bitmap/publication ownership, and physical-client qualification
are blocked by unavailable physical evidence; future qualification requires authorized G2
physical evidence. The next opaque body begins at
`0x00421B08`; firmware-wide functional completeness is not claimed.

## Current bootloader mode-one services increment

The complete three-function, 202-byte cluster
`[0x00421B08,0x00421BD2)` is now maintained C and reproduces every installed
stock body exactly under both reviewed Cortex-M55 compilers. Five focused
tests cover missing-controller and idempotent enable, last-client disable,
poll cleanup, literal seams and dual-toolchain compilation. Eleven strict
calls bind source-owned bitmap and poll helpers, critical-save and retained
control.

Canonical accounting is 17,215 source-owned, 16,528 generated patch, 16
alignment, and 130,081 retained official bytes across 221 source-owned
functions, five caves, 18 exact in-place leaves, and 201 patch sites. The
4,585,553-byte flash plan has SHA-256
`8a5e7cf810b4769885a52161425c6e7a8fd432295337936832f152f8217dabdd`
with 6,589 placed regions; provider and package hashes remain unchanged.

No hardware operation occurred. Live interrupt, control/register, bitmap,
polling and physical mode-one behavior is blocked by unavailable physical evidence; future qualification requires authorized evidence. The next opaque executable body begins at `0x00421BD2`;
firmware-wide functional completeness is not claimed.

## Current bootloader mode-zero enable increment

The complete 252-byte service `[0x00421BD2,0x00421CCE)` is now maintained C
and reproduces the installed stock body exactly under both reviewed Cortex-M55
compilers. Six focused tests cover missing-controller status, idempotent client
refresh and cleanup, idle-state control and publication, incompatible-state
rejection, literal/successor pins and dual-toolchain compilation. Nine strict
calls bind source-owned bitmap and cleanup helpers, critical-save, and retained
state-query/control providers.

Canonical accounting is 17,467 source-owned, 16,528 generated patch, 16
alignment, and 129,829 retained official bytes across 222 source-owned
functions, five caves, 19 exact in-place leaves, and 201 patch sites. The
4,586,257-byte flash plan has SHA-256
`a7a6aa289b102cc7ac7ca622fb20fca60774cc2ca884447b4a0ed3e499fdd875`
with 6,590 placed regions; provider and package hashes remain unchanged.

No hardware operation occurred. Live interrupt, controller/register, bitmap,
state, polling and physical mode-zero behavior is blocked by unavailable physical evidence; future qualification requires authorized evidence. The next opaque executable body begins at `0x00421CCE`;
firmware-wide functional completeness is not claimed.

## Current bootloader mode-zero disable and cleanup increment

The complete two-function, 144-byte cluster
`[0x00421CCE,0x00421D5E)` is now maintained C and reproduces both installed
stock bodies exactly under both reviewed Cortex-M55 compilers. Five focused
tests cover absent-client idempotence, last-client control/state clearing,
inactive and active poll cleanup, literal/successor pins and dual-toolchain
compilation. Seven strict calls bind source-owned bitmap/poll helpers,
critical-save and retained control.

Canonical accounting is 17,611 source-owned, 16,528 generated patch, 16
alignment, and 129,685 retained official bytes across 224 source-owned
functions, five caves, 21 exact in-place leaves, and 201 patch sites. The
4,587,696-byte flash plan has SHA-256
`c715ec177e33e23be701f1f2c24683c717a22beef84be5b49dd419926368ca43`
with 6,592 placed regions; provider and package hashes remain unchanged.

No hardware operation occurred. Live interrupt, controller/register, bitmap,
state, polling and physical mode-zero shutdown is blocked by unavailable physical evidence; future qualification requires authorized evidence. The next opaque executable body begins at `0x00421D5E`;
firmware-wide functional completeness is not claimed.

## Current bootloader row-four enable increment

The complete 236-byte service `[0x00421D5E,0x00421E4A)` is now maintained C
and reproduces the installed stock body exactly under both reviewed Cortex-M55
compilers. Six focused tests cover existing-client timeout refresh, not-ready
rejection, first-client switch/apply/activation, apply rollback, exact body and
dual-toolchain compilation. Ten strict calls bind source-owned bitmap and
cleanup helpers, critical-save and retained switch/apply providers.

Canonical accounting is 17,847 source-owned, 16,528 generated patch, 16
alignment, and 129,449 retained official bytes across 225 source-owned
functions, five caves, 22 exact in-place leaves, and 201 patch sites. The
4,588,397-byte flash plan has SHA-256
`b286aa443bba236715be039559aad7af48f61923b1033dea577b256a68efc0ed`
with 6,593 placed regions; provider and package hashes remain unchanged.

No hardware operation occurred. Live interrupt, switch/apply, bitmap/state,
polling and physical row-four behavior is blocked by unavailable physical evidence; future qualification requires authorized evidence. The next opaque executable body begins at `0x00421E4A`;
firmware-wide functional completeness is not claimed.

## Current bootloader row-four disable and cleanup increment

The complete two-function, 112-byte cluster
`[0x00421E4A,0x00421EBA)` is now maintained C and reproduces both installed
stock bodies exactly under both reviewed Cortex-M55 compilers. Five focused
tests cover absent/nonfinal/last-client disable, inactive/active cleanup,
literal/successor pins and dual-toolchain compilation. Seven strict calls bind
source-owned bitmap/poll helpers, critical-save and retained switch.

Canonical accounting is 17,959 source-owned, 16,528 generated patch, 16
alignment, and 129,337 retained official bytes across 227 source-owned
functions, five caves, 24 exact in-place leaves, and 201 patch sites. The
4,589,830-byte flash plan has SHA-256
`fc0579d838469b9ad02a69ca81a7bfeff40087aceb2a2401bd93d4d235ae6361`
with 6,595 placed regions; provider and package hashes remain unchanged.

No hardware operation occurred. Live interrupt, switch, bitmap/state, polling
and physical row-four shutdown is blocked by unavailable physical evidence; future qualification requires authorized
evidence. The next opaque executable body begins at `0x00421EBA`;
firmware-wide functional completeness is not claimed.
## Current bootloader constraint-dispatch and memchr increment

The 28-byte constraint dispatcher and 88-byte `memchr` at
`[0x00422590,0x00422628)` are now maintained C and reproduce both installed
stock bodies exactly under both reviewed Cortex-M55 compilers. Five focused
tests pin the bodies, retained 36-byte handler/message pool, two direct callers
and shared Apollo-main `memchr`; they exercise registered/default/null handler
paths plus aligned, unaligned, empty and missed searches. One strict relocation
binds the retained default constraint handler.

Canonical accounting is 19,675 source-owned, 16,528 generated patch, 16
alignment, and 127,621 retained official bytes across 241 source-owned
functions, five caves, 38 exact in-place leaves, and 201 patch sites. The
4,603,816-byte flash plan has SHA-256
`208dc810d0959a9b957172d82f40a3ddaa4120652f05f915885862a31be73b56`
with 6,615 placed regions; provider and package hashes remain unchanged.

No hardware operation occurred. Live handler-cell/default-handler behavior,
memory accessibility and fault qualification is blocked by unavailable physical evidence; future qualification requires authorized evidence. The next executable body begins at `0x00422628`;
firmware-wide functional completeness is not claimed.
## Current bootloader double-runtime increment

Thirteen compiler-runtime functions / 584 executable bytes at
`[0x00422628,0x00422872)` now compile exactly under both reviewed Cortex-M55
toolchains. They close `frexp`, binary64 normalization/comparison/scaling,
signed and unsigned conversion, subtraction, division and multiplication.
Five focused tests pin bodies, alignment, callers and eleven Apollo-main
twins, exercise host semantics, and compile both profiles. Three strict
relocations bind two internal wrapper/core edges and the retained range-error
tail.

Canonical accounting is 20,259 source-owned, 16,528 generated patch, 16
alignment, and 127,037 retained official bytes across 254 source-owned
functions, five caves, 51 exact in-place leaves, and 201 patch sites. The
4,613,691-byte flash plan has SHA-256
`3c5b51bb1895ab421f3fc9117b6ce34be0898b1bb59222b05aff12cee5bec4a6`
with 6,629 placed regions; provider and package hashes remain unchanged.

No hardware operation occurred. Live VFP flags, retained range-error state and
caller ABI qualification is blocked by unavailable physical evidence; future qualification requires authorized evidence.
The next executable body begins at `0x00422874`; firmware-wide functional
completeness is not claimed.
## Current bootloader thread-pointer increment

The eight-byte IAR-compatible thread-pointer/runtime-anchor leaf at
`[0x00422874,0x0042287C)` is now exact maintained C under both reviewed
toolchains. Three focused tests pin its literal, caller and successor, verify
the host return value, and compile both profiles.

Canonical accounting is 20,267 source-owned, 16,528 generated patch, 16
alignment, and 127,029 retained official bytes across 255 source-owned
functions, five caves, 52 exact in-place leaves, and 201 patch sites. The
4,615,090-byte flash plan has SHA-256
`b20ec5bf6f36bf5263858770e082a33890575642d11b27e69f418922da7b707e`
with 6,631 placed regions; provider and package hashes remain unchanged.

No hardware operation occurred. Live SRAM-anchor lifecycle qualification is
blocked by unavailable physical evidence; future qualification requires authorized evidence. The next executable body begins
at `0x0042287C`; firmware-wide functional completeness is not claimed.
## Current bootloader unsigned 64-bit divmod increment

The complete 560-byte IAR-compatible unsigned divide/modulo runtime at
`[0x0042287C,0x00422AAC)` is now exact maintained C under both reviewed
toolchains. Five focused tests cover fast, normalized, correction,
smaller-dividend and zero-divisor paths, 500 deterministic differential cases,
callers, successor and dual compilation. One strict tail relocation binds the
retained divide-by-zero handler.

Canonical accounting is 20,827 source-owned, 16,528 generated patch, 16
alignment, and 126,469 retained official bytes across 256 source-owned
functions, five caves, 53 exact in-place leaves, and 201 patch sites. The
4,615,803-byte flash plan has SHA-256
`41cbff6234a93834d9041c8303a23d4b4b2b36fb50be37c20800acb791a509bd`
with 6,632 placed regions; provider and package hashes remain unchanged.

No hardware operation occurred. Live divide-by-zero and register-ABI
qualification is blocked by unavailable physical evidence; future qualification requires authorized evidence. The next
executable body begins at `0x00422AAC`; firmware-wide functional completeness
is not claimed.

## Current bootloader per-instance clock-divider increment

The 186-byte clock-divider service at `[0x00422E28,0x00422EE2)` is exact
maintained C under both reviewed target toolchains with one strict call to the
source-owned unsigned 64-bit divmod runtime. Seven focused tests pin its binary
seams and cover six reference modes, invalid/range failure, integer/fraction
programming, achieved rate, every bank and dual compilation.

Canonical accounting is 21,899 source-owned, 16,528 generated patch, 16
alignment, and 125,397 retained official bytes across 266 source-owned
functions, five caves, 63 exact in-place leaves, and 201 patch sites. The
4,624,387-byte flash plan has SHA-256
`bcfc9cba4e4f5e12fcb53c27a977f7c3b9d2a3a2df429d6cac2d4c86bc698788`
with 6,644 placed regions; provider and byte-identical unsigned-package hashes
remain unchanged.

No hardware operation occurred. Live reference clocks, divider MMIO effects,
rate accuracy and cold-boot qualification are blocked by unavailable physical evidence; future qualification requires authorized responsive evidence. The next executable body begins at
`0x00422EE2`; firmware-wide functional completeness is not claimed.
## Current bootloader atomic/wrapper increment

The 28-byte interrupt-atomic three-sample snapshot, two-byte no-op and
eight-byte retained-query wrapper at `[0x00422AAC,0x00422AD2)` are exact
maintained C under both reviewed toolchains. Three focused tests cover bodies,
caller/provider, host behavior, successor alignment and dual compilation.

Canonical accounting is 20,865 source-owned, 16,528 generated patch, 16
alignment, and 126,431 retained official bytes across 259 source-owned
functions, five caves, 56 exact in-place leaves, and 201 patch sites. The
4,617,928-byte flash plan has SHA-256
`d45be493c3f226ec9b567c576d08194a47f48b67c74b6d0845439f82a7b9965a`
with 6,635 placed regions; provider and package hashes remain unchanged.

No hardware operation occurred. Live interrupt/volatile/provider qualification
is blocked by unavailable physical evidence; future qualification requires authorized evidence. The next executable body begins
at `0x00422AD4`; firmware-wide functional completeness is not claimed.

## Current bootloader hardware-instance initializer increment

The complete 212-byte four-instance hardware-service initializer at
`[0x00422AD4,0x00422BA8)` is exact maintained C under both reviewed Cortex-M55
toolchains. Five focused tests cover every status path, all four `0x11C`-byte
slots, authenticated field mutation and preservation, callsite/pool/boundary
pins, and dual compilation.

Canonical accounting is 21,077 source-owned, 16,528 generated patch, 16
alignment, and 126,219 retained official bytes across 260 source-owned
functions, five caves, 57 exact in-place leaves, and 201 patch sites. The
4,619,359-byte flash plan has SHA-256
`28bc8efdfe3ce66f76001c3c7dd58190ff5e945cabff97fa7558627cdbe629a7`
with 6,637 placed regions; provider and unsigned-package hashes remain
unchanged and the package is byte-identical to its reviewed reference.

No hardware operation occurred. Live SRAM ownership, concurrent
initialization, peripheral effects and cold-boot qualification are explicitly
is blocked by unavailable physical evidence; future qualification requires authorized evidence. The next executable body begins
at `0x00422BA8`; firmware-wide functional completeness is not claimed.

## Current bootloader instance register-service increment

The complete 376-byte instance register-transfer and lifecycle service at
`[0x00422BA8,0x00422D20)` is exact maintained C under both reviewed target
toolchains with five strict call relocations. Six focused tests cover all
software-observable validation, action, transfer, register-bank, clock-gate,
mode-route and teardown-order behavior.

Canonical accounting is 21,453 source-owned, 16,528 generated patch, 16
alignment, and 125,843 retained official bytes across 261 source-owned
functions, five caves, 58 exact in-place leaves, and 201 patch sites. The
4,620,102-byte flash plan has SHA-256
`e5cbb6380db3f81e5dbb15d3e4ccfb7cefcb4e6fcf31d37b1407b8adb2746500`
with 6,638 placed regions; provider and unsigned-package hashes remain
unchanged and the package remains byte-identical.

No hardware operation occurred. Live MMIO, revision, clock, mode, teardown,
resource and cold-boot qualification is blocked by unavailable physical evidence; future qualification requires authorized evidence. The next executable body begins at `0x00422D20`;
firmware-wide functional completeness is not claimed.

## Current bootloader per-instance register-clear increment

The 44- and 46-byte register-clear leaves at
`[0x00422D20,0x00422D7A)` are exact maintained C under both reviewed target
toolchains. Four focused tests cover all four banks, exact masks/preservation,
authenticated bodies/pools/boundaries, and dual compilation.

Canonical accounting is 21,543 source-owned, 16,528 generated patch, 16
alignment, and 125,753 retained official bytes across 263 source-owned
functions, five caves, 60 exact in-place leaves, and 201 patch sites. The
4,621,559-byte flash plan has SHA-256
`d0bbd6e98171006d3dab51f657e739747995851acfb10da4d53c704177d87fb4`
with 6,640 placed regions; provider and byte-identical package hashes remain
unchanged.

No hardware operation occurred. A four-byte datum remains retained through
`0x00422D7E`; live MMIO/bank/peripheral/cold-boot qualification is explicitly
is blocked by unavailable physical evidence; future qualification requires authorized evidence. The next executable body begins at
`0x00422D7E`; firmware-wide functional completeness is not claimed.

## Current bootloader per-instance status-map increment

The 72-byte status mapper at `[0x00422D7E,0x00422DC6)` is exact maintained C
under both reviewed target toolchains without relocation. Five focused tests
pin the body, result pools, datum and successor and cover all four modeled
banks, each argument/MMIO status bit, priority, fallback, and dual compilation.

Canonical accounting is 21,615 source-owned, 16,528 generated patch, 16
alignment, and 125,681 retained official bytes across 264 source-owned
functions, five caves, 61 exact in-place leaves, and 201 patch sites. The
4,622,934-byte flash plan has SHA-256
`94d1d455c823fe27ccaffff91d44a7839c4b4b14396f5a71342849c6e1c78df9`
with 6,642 placed regions; provider and byte-identical unsigned-package hashes
remain unchanged.

No hardware operation occurred. Live MMIO status, bank ownership, peripheral
flags, controller timing and cold-boot qualification are explicitly blocked by
future-required authorized responsive G2 evidence. The next executable body begins
at `0x00422DC6`; firmware-wide functional completeness is not claimed.

## Current bootloader dual-descriptor initializer increment

The 98-byte guarded per-instance descriptor initializer at
`[0x00422DC6,0x00422E28)` is exact maintained C under both reviewed target
toolchains with two strict retained-constructor calls. Six focused tests pin
the body/caller/literal/provider/successor and cover header validation, both
optional argument-pair gates, flags, exact descriptor layouts, order and dual
compilation.

Canonical accounting is 21,713 source-owned, 16,528 generated patch, 16
alignment, and 125,583 retained official bytes across 265 source-owned
functions, five caves, 62 exact in-place leaves, and 201 patch sites. The
4,623,670-byte flash plan has SHA-256
`e15b1575d93968f623450c3ea1a021aff473beb74969b6b99ce452ebd6204590`
with 6,643 placed regions; provider and byte-identical unsigned-package hashes
remain unchanged.

No hardware operation occurred. Live SRAM/MMIO descriptor ownership,
DMA/controller timing, buffer lifetime, interrupt and cold-boot qualification
are blocked by unavailable physical evidence; future qualification requires authorized responsive evidence. The next
executable body begins at `0x00422E28`; firmware-wide functional completeness
is not claimed.

## Current bootloader per-instance configuration-latch increment

The 106-byte interrupt-atomic configuration latch at
`[0x00422EE2,0x00422F4C)` is exact maintained C under both reviewed target
toolchains with one strict call to the retained critical-section provider.
Five focused tests pin its binary seams and cover exact first-latch copying and
preservation, duplicate rejection, token restoration on both paths and dual
compilation.

Canonical accounting is 22,005 source-owned, 16,528 generated patch, 16
alignment, and 125,291 retained official bytes across 267 source-owned
functions, five caves, 64 exact in-place leaves, and 201 patch sites. The
4,625,116-byte flash plan has SHA-256
`0fdbc2c75564879fae344b05f343349cb88a34d23aaed73e530e3ada3daa8160`
with 6,645 placed regions; provider and byte-identical unsigned-package hashes
remain unchanged.

No hardware operation occurred. Live interrupt atomicity, concurrency,
instance ownership, downstream MMIO effects and cold-boot qualification are
blocked by unavailable physical evidence; future qualification requires authorized responsive evidence. The next
executable body begins at `0x00422F4C`; firmware-wide functional completeness
is not claimed.

## Current bootloader secondary configuration-latch increment

The 86-byte interrupt-atomic secondary configuration latch at
`[0x00422F4C,0x00422FA2)` is exact maintained C under both reviewed target
toolchains with one strict retained critical-section call. Five focused tests
pin the binary seams and cover exact payload copying and preservation,
duplicate rejection, token restoration on both paths and dual compilation.

Canonical accounting is 22,091 source-owned, 16,528 generated patch, 16
alignment, and 125,205 retained official bytes across 268 source-owned
functions, five caves, 65 exact in-place leaves, and 201 patch sites. The
4,625,886-byte flash plan has SHA-256
`7b4d686e47a731844e2639c5b5546512fc8c5d22c56a526b1835745fe30e3a6c`
with 6,646 placed regions; provider and byte-identical unsigned-package hashes
remain unchanged.

No hardware operation occurred. Live interrupt atomicity, concurrency,
secondary-instance ownership, downstream MMIO effects and cold-boot
qualification is blocked by unavailable physical evidence; future qualification requires authorized responsive
evidence. The next executable body begins at `0x00422FA2`; firmware-wide
functional completeness is not claimed.

## Current bootloader secondary configuration-release increment

The 60-byte interrupt-atomic secondary release at
`[0x00422FA2,0x00422FDE)` is exact maintained C under both reviewed target
toolchains with strict critical-section and memset calls. Five focused tests
pin its binary seams and cover the exact 60-byte runtime reset, noncanonical
state rejection, provider arguments, token restoration and dual compilation.

Canonical accounting is 22,151 source-owned, 16,528 generated patch, 16
alignment, and 125,145 retained official bytes across 269 source-owned
functions, five caves, 66 exact in-place leaves, and 201 patch sites. The
4,626,654-byte flash plan has SHA-256
`2fc61fd11765948d78562547efacb50ff87efcb3ebead62e911ee8a2730d0581`
with 6,647 placed regions; provider and byte-identical unsigned-package hashes
remain unchanged.

No hardware operation occurred. Live interrupt atomicity, concurrent release,
retained memset ABI, SRAM/MMIO consumers and cold-boot qualification are
blocked by unavailable physical evidence; future qualification requires authorized responsive evidence. The next
executable body begins at `0x00422FDE`; firmware-wide functional completeness
is not claimed.

## Current bootloader per-instance hardware-shutdown increment

The 176-byte register-quiesce and shutdown service at
`[0x00422FDE,0x0042308E)` is exact maintained C under both reviewed target
toolchains with four strict calls. Six focused tests pin its binary seams and
cover all banks, conditional register masks, delay calculation, provider
ordering, release/restore behavior and dual compilation.

Canonical accounting is 22,327 source-owned, 16,528 generated patch, 16
alignment, and 124,969 retained official bytes across 270 source-owned
functions, five caves, 67 exact in-place leaves, and 201 patch sites. The
4,627,385-byte flash plan has SHA-256
`19065a0b5f07435bfe09e1257f50547952ddd21010f72a94a4920f89615d938f`
with 6,648 placed regions; provider and byte-identical unsigned-package hashes
remain unchanged.

No hardware operation occurred. Live MMIO, clock/peripheral state, delay
accuracy, concurrency, provider effects and cold-boot shutdown qualification
are blocked by unavailable physical evidence; future qualification requires authorized responsive evidence. The
next executable body begins at `0x0042308E`; firmware-wide functional
completeness is not claimed.

## Community source profile closes GX8002 destination accounting

The G2 community source manifest no longer labels either codec FWPK record as
an unknown destination. The 32-byte UART boot header is retained as controller
protocol metadata; its 10,240-byte and 27,964-byte bodies are placed at GX8002
IRAM `0x10000000` and `0x10002800`. The 287,808-byte BINH record is split at
its authenticated dual-image boundary into SPI-NOR offsets `0` and `0x2F3B0`.
These placements are re-derived from the boot header, self-referential vectors,
BINH headers, and Apollo `serialdown 0 <size> 8192` command.

Two consecutive assembly runs retained the byte-identical 4,745,526-byte
package SHA-256
`3c8cdcdb4bc56b1a76b5ddabe6eb1bc79810aa6a99cf35acaec6bd019179c785`.
The deterministic flash plan is 4,640,329 bytes with SHA-256
`d9fe2b2028f168a1f3e54a1a26f0783c436173c319c143e0835b9bd5c0e7ca23`:
6,667 placed regions, zero unresolved regions, six container-only records, and
six protected regions. Seventeen focused codec tests, five KVDB tests, and two
Apollo origin-accounting tests pass. No hardware operation occurred. The codec
program bodies and KWS model remain explicitly proprietary source boundaries;
address closure does not claim them as open source.

## Bootloader per-instance hardware initializer is production source-owned

The complete 570-byte body at `[0x0042308E,0x004232C8)` now compiles from the
MIT `runtime_hw_initializer_42308e.c` translation unit under both reviewed
Cortex-M55 profiles. Every installed byte matches the authenticated body after
the two strict calls to the already source-owned mode-route and clock-divider
services are relocated. Nine focused tests cover its validation, revision/rate
gates, four banks, provider arguments and errors, global route policy, recovered
configuration fields, and both target compilers.

The Apple bootloader remains 163,840 bytes with SHA-256
`8f24989979719b4c9f1273624240ba702a99decf735d099bfee1afcda16159e0`;
the Linux-profile provider remains 163,824 bytes with SHA-256
`efef1a9b039548ab9332651921e8a7864ce8df205bfe22c9ae6e13c0c81cb635`.
Apple accounting is 28,495 source-owned, 16,490 generated, and 118,855
retained official bytes. The checked dual-profile ownership receipt moves the
same 570-byte body from retained to source in each profile without changing
either provider artifact.

No hardware operation occurred. Live chip-revision, MMIO, clock/peripheral,
interrupt/concurrency and cold-boot behavior is blocked by unavailable
physical evidence. The retained bootloader complement and the other controller
source boundaries remain release-blocking; firmware-wide functional
completeness is not claimed.

## Bootloader MSPI device configuration is structured production C

The 26-mode `mspi_device_configure` service at
`[0x00424120,0x0042488E)` no longer depends on a raw executable transcript.
`runtime_mspi_device_configure_424120.c` is structured BSD-3-Clause C and both
reviewed compilers emit the same relocation-free 284-byte body with SHA-256
`960b3d30653a94dd8b0c9037d9e0cdd53991d88c06a9d27cecf6576a0bbce97f`.
Because the bootloader partition has zero append headroom, that body is routed
in place at the authenticated entry instead of extending across `0x00438000`.

The Apple provider remains 163,840 bytes with SHA-256
`d7b14f5023a212797b67278b13fc1c9467a5686f08976e8eae98d9e1e8d80810`;
the Linux provider remains 163,824 bytes with SHA-256
`e8cc402a85122352d7e1f5a9a238d283dfe66bfc297c4c2c04a1c29a4cce1d4c`.
Apple accounting is 28,779 source-owned, 16,490 generated, and 118,571
retained official bytes. The checked ownership receipt records 423,707 source,
426,474 generated, 30,636 candidate, and 3,796,979 retained/external bytes for
Apple; Linux records 206,145 source, 136,046 generated, 30,636 candidate, and
4,097,285 retained/external bytes.

Five focused tests cover all 26 modes, both clock-on-D4 states, register-bit
preservation, access order, invalid-mode no-op behavior, source-quality gates,
both target compilers, manifest routing, and partition conservation. No
hardware operation occurred. All-mode MSPI register, pad, XIP, clock-on-D4,
and cold-boot qualification is blocked by unavailable physical evidence. The
remaining retained bootloader complement is still a release-blocking software
gap; firmware-wide functional completeness is not claimed.

## Bootloader MSPI PIO-mixed configuration is structured production C

The 232-byte stock `mspi_piomixed_configure` body at
`[0x0042488E,0x00424976)` now has a structured BSD-3-Clause implementation.
Both reviewed compilers emit an identical 84-byte, relocation-free,
2-byte-aligned body with SHA-256
`6269fba16f490f502f6d00c87e76b4fa9521b9d9e97fbf6f7a04dd02ec9f6044`.
The target uses `-mpure-code` to synthesize the MSPI base without a 4-byte
literal, allowing exact placement at the halfword-aligned stock entry.

Apple provider accounting is now 28,863 source-owned, 16,490 generated, and
118,487 retained official bytes. Provider identities are 163,840 bytes /
`a47ca96d9776b40dfc6d110abb2bba18118cb924c41e6544d8f0dbca5ffd669e`
for Apple and 163,824 bytes /
`4e63ba5c9085049e9d0d76a652f1d04866f95c7c603978bb6d5ac1ef380e3d61`
for Linux. The checked ownership receipt records 423,791 source and 3,796,895
retained/external bytes for Apple, and 206,229 source and 4,097,201 retained/
external bytes for Linux; other buckets remain unchanged.

The host oracle covers all 26 mode mappings, exact register address and access
counts, low-nibble replacement, unrelated-bit preservation, and invalid-mode
no-op behavior. The public raw-transcript census falls to six files / 6,768
executable bytes. No hardware operation occurred. Live PIO mode, pad, XIP,
module, and cold-boot qualification is blocked by unavailable physical
evidence. The next sequential executable is the already source-owned dummy
callback and sequence-loopback pair followed by the retained four-byte MSPI0
base literal; firmware-wide completeness is not claimed.

## Bootloader MSPI initializer is structured production C

The state initializer at `[0x00424A5A,0x00424AEA)` now routes an 88-byte
structured BSD-3-Clause C return path in place. Both reviewed compilers emit
the same relocation-free body SHA-256
`9476ac1668a350be0af32604c47a50476782fa21eaa7001648928feed497ef9c`.
The source covers all recovered status paths and state writes without raw
executable directives or inline assembly. Its early return leaves the final
56 stock bytes unreachable and separately retained.

Apple bootloader accounting is 28,951 source-owned, 16,490 generated, and
118,399 retained official bytes across 589 manifest intervals. Provider
identities are 163,840 bytes /
`cea034e0fddd2b2cffa144dd40ea46926303e8d5bb33fe9aed6b1468fb227369`
for Apple and 163,824 bytes /
`3a3ec57333277d277e7ff90ad7245bd7f4ef38e3671a9604b2255fade1fc72ab`
for Linux. The unsigned packages remain 4,678,740 and 4,471,056 bytes with
SHA-256 `268e7407daa1fafc9b093a3b4bf337dfc8b52f30c003bd8d97e443f8a90650f2`
and `6870d8e9486a0af9e96322a08d0537879f7146551828f375665d8c638c1f5ee3`.

The checked ownership receipt records 423,879 source and 3,796,807 retained/
external bytes for Apple, and 206,317 source and 4,097,113 retained/external
bytes for Linux; other buckets are unchanged. Six host/target tests are green,
and the public deleted-transcript census falls to five files / 6,624 executable
bytes. No hardware operation occurred. Live SRAM, module, clock, XIP-delay,
and cold-boot qualification is blocked by unavailable physical evidence. The
next sequential executable software gap is `am_hal_mspi_configure` at
`[0x00424AF0,0x00424BD4)`; firmware-wide completeness is not claimed.

## Bootloader MSPI controller configuration is structured production C

The 228-byte stock controller-configure body at
`[0x00424AF0,0x00424BD4)` now begins with a structured 152-byte BSD-3-Clause
C implementation. Apple Clang 21 and Homebrew LLVM Clang 22 emit identical,
relocation-free code SHA-256
`f48e9bead432163e13d495026fb798ea87c640638ea6ec79bfa179a3d766bad1`.
The source return leaves 76 authenticated stock bytes unreachable and retained.

Ten focused tests cover handle validation, enabled-state rejection, exact
register clearing, TCB propagation, strict TCM boundary, null TCB behavior,
unsigned-small-size arithmetic, 256-entry capacity capping, source quality,
both compilers, manifest routing, and byte conservation. Apple accounting is
29,103 source-owned, 16,490 generated, and 118,247 retained bytes across 591
intervals. The raw-transcript census is four files / 6,396 executable bytes.

The Apple/Linux providers hash to
`52a74441ebb82b7127833f6de4d1068e880ccfaa416fdbe6b33f4df05e9df118`
and `7fc80bccf1f3bd51fdffc86b0043ca7243064fff1602fbfd4f2c54203cdf9f7d`.
The checked ownership receipt records 424,031 source and 3,796,655 retained/
external bytes for Apple, and 206,469 source and 4,096,961 retained/external
bytes for Linux. No hardware operation occurred. Live register, SRAM, TCB,
clock, XIP, and cold-boot validation is blocked by unavailable physical
evidence. The next software frontier is `[0x00424BE4,0x00425066)`;
firmware-wide completeness is not claimed.

## Bootloader public MSPI device configuration is structured production C

The public `am_hal_mspi_device_configure` span at
`[0x00424BE4,0x00425066)` now routes a 672-byte structured BSD-3-Clause C
return path. Apple Clang 21 and Homebrew LLVM Clang 22 emit identical
unrelocated bytes, and six strict Thumb-call relocations produce SHA-256
`344f6705aac2638cd47e64b83a76058b16f00dc9640ccb6edd9ea9d52072cf56`.
Eight focused tests cover all 23 clock classes, module restrictions, clock
lifecycle failures, ABI offsets, guards, source quality, and conservation.

Apple boot accounting is 29,775 source-owned, 16,490 generated, and 117,575
retained bytes across 593 intervals. The public deleted-transcript census is
three files / 5,242 executable bytes. Apple/Linux providers are
`f570bbf749b16043c8ccfc6eeae66fafaabf4146d5cc55f63d5fab729775ccad`
and `e859e0ce78f8b21e8a1542701eb52b4d7d97a62902546ef451919948d4dbbf8e`;
packages are `4cef950c09d3b7e0afc3dc22199052073c889a342a8f3f438dfbcaae7de58667`
and `f7260f93e2c87f2403e14f5a8e6ae1436233cce2990c386a1cde48d2e8133e31`.
No hardware operation occurred. Live register, clock, DMA/TCB, XIP,
attached-flash, reset, and boot validation is blocked by unavailable physical
evidence. The next executable gap is `am_hal_mspi_enable` at
`[0x00425066,0x004250F0)`; firmware-wide completeness is not claimed.
