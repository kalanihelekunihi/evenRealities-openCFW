# Goodix calculation roots in the R1 application link

The strict application receipt
`build/r1-link-event-dispatch-ordered-20261111/report.json` now links with no undefined
references. The source-owned soft-ADT frame executor reaches the real NADT
calculation binding:

| Import | Stock root | Current C state |
| --- | --- | --- |
| `goodix_nadt_calc` | `0x6E008` | `native_nadt_calc.c` binds the public sample, native state/workspace, configuration views and three typed classifier cores. Bounded stock-output replay passes through 100 fresh direct and calibrated input calls at 25, 50, 100 and 200 Hz; physical-device behavior remains unverified. |

The NADT binding preserves the initialized native context, allocation,
repeated-call state and result layout through borrowed views. Its stock
configuration pointer is `0x20037E10`,
immediately after the native workspace at `0x200377DC`; its negative-offset
activity records occupy the workspace's final 68 bytes. This identifies the
native-to-typed binding surface. The binding reuses that storage and the
source-owned 253-float primary boundary-filter coefficient table.
The remaining C files with assembly syntax form a separate source-only gate.

The [NADT root replay review](goodix-nadt-root-replay-review.md) records
the early returns and 32,000 paired calls across 320 fresh-input
sequences, plus the current strict-link size. It supersedes the historical
statements below that no NADT stock-output replay had passed.

The [NADT workspace view](goodix-nadt-workspace-view-review.md) binds the
four native history banks without duplicating their storage. The native state
view maps the persistent stream fields and four statistic banks. The three
classifier callback families are now bound by `native_nadt_calc.c`.
The public NADT input also has a borrowed three-lane sample view in
`native_nadt_public_view.c`. The locked `0x36034` sample-preparation entry
reads the lane stride at public offset `+4`, direct data at `+12`, gain codes
at `+16`, the first drive halfword through `+20`, conversion mode at `+50`,
data type at `+51`, and calibrated IPD lanes through the unique pointer at
`+52` and its `+20` field. The new view exposes those exact source buffers
to the typed preparation helper, with null and four-channel bounds checks.
Its host projection check is
`build/r1-hba-calc-link-probe-20261111/test_nadt_public_view.c`.
`build/sources-r1-nadt-state-flag-20261111/report.json` compiles 955/955
application and 82/82 bootloader units without duplicate strong symbols.
The strict bootloader links; the strict application still lacks only
`goodix_nadt_calc` in that historical receipt. The current source also projects
persistent stream state, all three classifier configurations and public result.

The same source now loads and stores the native four-window classifier
configuration. The locked `0x856EC` root points at `0x20037DCC`, the final
68 bytes of the native NADT workspace, immediately before the configuration
at `0x20037E10`. It reads float metric bank `+16`, signed maxima `+32`,
signed minima `+48`, count `+64`, then level, elapsed limit, tail threshold,
transition limit, axis limit, metric threshold and spread threshold from
configuration offsets `+2`, `+4`, `+6`, `+7`, `+8`, `+0x14` and `+0x18`.
The source projects those fields into the typed classifier and commits its
mutable banks/count back to the native owner. The ignored public-view host
check covers the offsets, signed threshold and store boundary. The
classifier-specific state mappings are now present; their repeated-call
behavior still needs stock replay.

`r1_goodix_nadt_stream_state_load/store` projects the initialized marker,
status, counters, averages, classifier state and four running-statistics banks
from the native 92-byte state and workspace tail. Its store leaves the stock
allocation pointer and unknown bytes untouched. The preparation view maps
previous sequence and scale code from native offsets `+48` and `+52`.
The auxiliary configuration view maps offsets `+0x67` through `+0x6c`, and
the alternate view maps `+0x6d`, `+0x6e`, `+0x70`, `+0x72` and `+0x74`;
both borrow the shared transition count at `+7`. The typed stream now reads
classifier transient counter zero into the result flag before packing
classification bit two, because both occupy native state byte `+5`.
`test_nadt_public_view.c` and `test_nadt_window_history.c` under ignored
`build/r1-hba-calc-link-probe-20261111/` pass their host checks for these
projections and the four-window transitions. The full classifier fake-root
probe links at 691,752 of 696,320 flash bytes, leaving 4,568 bytes for a
real adapter. It remains a probe, not a firmware image.

The locked `0x6E360` through `0x6E3E6` path checks the 68-byte workspace
tail's byte `+64`, shifts four 3-word history banks when it reaches four,
sets the count back to three, updates the active running-statistics slot, and
increments the count at each 25-sample boundary. The typed
`goodix_primitives_nadt_stream_process_view` previously read that count but
never advanced or shifted it. It now shifts the four chronological statistic
slots before the first sample after a full fourth window, advances the count
at each 25-sample boundary, and rejects an out-of-range count. Its rotating
`activity_lane` remains a distinct native state byte at `+13`. The ignored
`build/r1-hba-calc-link-probe-20261111/test_nadt_window_history.c` runs 101
accepted samples through the actual typed stream and checks all count
transitions, the fourth-window shift and the invalid-count guard. Stock
output and physical-device parity for this correction remain unverified.

The HBA secondary context layout was corrected to the native descriptor
offsets: filter slots begin at `+0x04` with 16-byte spacing, packed histories
at `+0x94`, and float histories at `+0xDC`. The previous packed typed array
could not safely alias the initializer's workspace. The borrowed view checks
both allocation pointers and adds no persistent copy. The R1-only source
receipt `build/sources-r1-hba-context-view-final-20261111/report.json`
compiles all 946 application and 82 bootloader units with no duplicate strong
symbols. The strict application receipt
`build/r1-link-hba-context-view-final-20261111/report.json` still has the
same three undefined calculation roots and uses 663,720 of 696,320 flash
bytes. This view is not yet a production calculation adapter.

`native_hba_public_view.c` projects the public input's channel buffers,
accelerometer fields, data-type byte at `+0x33`, and module selector pointer
at `+0x34` into the typed HBA process input. The result projection loads and
stores only the four stock root writes: `hba_out_flag`, `hba_out`,
`valid_level` and `valid_score`. Other public result fields retain their
caller-owned bytes. The ignored host test
`build/r1-hba-public-view-20261111/test_public_view.c` checks aliases,
lengths, fields, null guards and preservation. The current R1 source receipt
`build/sources-r1-hba-public-view-20261111/report.json` compiles 947/947
application and 82/82 bootloader units; the strict application receipt
`build/r1-link-hba-public-view-20261111/report.json` still reports the three
calculation imports. This projection alone does not validate the full HBA
calculation against stock.

The stock indexed-operation table copied by `0x28AD4` is at `0xBCF5C`.
Its seven entries are Thumb targets `0x38051`, `0x3007F`, `0x417F1`, null,
null, null, and `0x30079`. The first three veneers forward to the source-owned
`quantized_runtime_goodix_executor_execute` target at `0x742E4`; selector six
branches to the distinct `quantized_runtime_goodix_second_executor_execute`
target at `0x617F8`. These target families already have typed C bodies, but
the live graph records still need typed plans and operation callbacks before
the runtime table can execute them. The table evidence does not establish
executable HBA behavior.

The production HBA mode-0 and mode-1 records now have a non-owning graph
view in `native_hba_graph_view.c`. It reads the three six-word recurrent
records at `+0x1BC`, `+0x1D8` and `+0x1F0` into typed descriptors and points
the plan at the existing 732- or 568-byte initializer allocation. The shared
`quantized_runtime_gomore_executor_plan_build_view` accepts those borrowed
bytes; the prior owned-graph API delegates to it. Focused host tests under
`build/r1-hba-borrowed-graph-view-20261111/` check both mode sizes, record
fields, descriptor pointers, plan equality with the existing builder, and
invalid view guards. `build/sources-r1-hba-native-graph-view-20261111/report.json`
compiles 948/948 application and 82/82 bootloader units with no duplicate
strong symbols. The mode-6 allocation now also has a borrowed 984-byte view,
and `quantized_runtime_goodix_second_executor_plan_build_view` builds its
typed plan without copying that allocation. The host test checks mode-6
pointer identity, plan equality with the existing owned builder and invalid
view guards. The final source receipt for these views is
`build/sources-r1-hba-all-graph-views-20261111/report.json`; its strict
application link receipt is
`build/r1-link-hba-all-graph-views-20261111/report.json`. All 948 application
and 82 bootloader units compile, but the strict link still lacks the same
three calculation roots. The operation callbacks and persistent HBA runtime
remain unimplemented.

The native graph records now rewrite their 15 source-owned operator tokens
to the corresponding typed executor tokens while building a plan. Unknown
tokens remain unknown. `r1_goodix_hba_plan_set_bind_source` builds the mode-0,
mode-1 and mode-6 plans together in stable caller-owned storage; each plan
points into its borrowed view and initializer-owned graph record. Failed or
misordered record binding clears the whole set. The ignored host test
`build/r1-hba-borrowed-graph-view-20261111/test_native_graph_view.c` checks
token translation, all three plan bindings, their pointer lifetimes and
rejection of a misordered mode. The R1 source receipt
`build/sources-r1-hba-plan-bind-final-20261111/report.json` compiles
950/950 application and 82/82 bootloader units without duplicate strong
symbols. `native_hba_quantized_runtime.c` binds the existing native C fminf,
fmaxf, floorf and expf implementations and adapts the native C qsort ABI for
arena compaction. Its ignored host test checks provider identities, sort
dispatch and rejection of an oversized host request. The strict receipt above
still has three calculation roots and uses 664,008 of 696,320 flash bytes.
The corresponding strict bootloader receipt
`build/r1-boot-link-hba-plan-bind-final-20261111/report.json` links with
valid vectors and no undefined references.
These bindings alone do not make `goodix_hba_calc` executable.

`native_hba_graph_execute.c` now runs the three typed plans over their native
I/O geometry. Mode 0 uses the existing 1,935-float workspace, mode 1 copies
its input into a zeroed 7,740-byte pool scratch allocation, and mode 6 uses
the caller workspace with 4,320 temporary pool bytes. The indexed table in
`native_hba_graph_callbacks.c` binds selectors 0, 1 and 6, validates the
initializer-owned record identity, and releases each transient allocation.
Teardown and reinitialization clear the table binding. Host checks under
`build/r1-hba-borrowed-graph-view-20261111/` exercise I/O ownership,
allocation release, dispatch and rejection guards.

The locked 2.2.6.0009 application at `0x43B30` updates mode-0 record words
`+0x1E0`, `+0x1E4` and `+0x1E8` from its slot table at `+0x238` before the
indexed graph callback. `r1_goodix_hba_elapsed_bind` now points typed elapsed
state at that live table; `r1_goodix_hba_elapsed_commit` writes the three
changed words to the native record and refreshes the plan's recurrent
descriptor immediately before mode-0 execution. The host view check exercises
one slot shift and rejects a stale timestamp pointer. The source receipt
`build/sources-r1-hba-elapsed-20261111/report.json` compiles 952/952
application and 82/82 bootloader units, with no duplicate strong symbols.
`build/r1-link-hba-elapsed-20261111/report.json` still lacks exactly the three
calculation roots; `build/r1-boot-link-hba-elapsed-20261111/report.json` links
with valid vectors and no unresolved references. The HBA runtime is not yet
bound by the production initializer, so these callbacks are not yet a working
HBA calculation path.

The locked `0x5CE22` call passes that same mode-0 graph record to `0x2F65C`,
which branches to `0x36BFA`. For mode 1, `0x36BFA` clears three float buffers
whose count and pointer pairs begin at record offsets `+0x1BC`, `+0x1D8` and
`+0x1F0`. These are the recurrent descriptors already projected into the
typed graph view. `r1_goodix_hba_mode_buffers_bind` now exposes those three
borrowed spans to the typed timed dispatcher; the host check clears sample
buffers through that mapping. The production HBA runtime still needs to bind
and retain these spans. The subsequent source receipt
`build/sources-r1-hba-mode-buffers-20261111/report.json` compiles all 952
application and 82 bootloader units; its strict bootloader link passes and
its strict application link still reports the same three calculation roots.

`native_hba_calc.c` now owns one static typed runtime, one plan set and the
provider bindings. On the first public HBA calculation it borrows the
initializer's primary and secondary contexts, builds all three graph plans,
binds the live elapsed state and recurrent mode buffers, then runs the typed
HBA process over the public input/result views. Reinitialization and teardown
unbind those pointers before the native graph allocations are released. The
R1 source receipt `build/sources-r1-hba-calc-20261111/report.json` compiles
953/953 application and 82/82 bootloader units without duplicate strong
symbols. The strict app receipt `build/r1-link-hba-calc-20261111/report.json`
has only `goodix_hrv_calc` and `goodix_nadt_calc` unresolved; its partial map
uses 679,112 of 696,320 flash bytes and ends static RAM at `0x2003AA74`.
The bootloader receipt `build/r1-boot-link-hba-calc-20261111/report.json`
links with valid vectors. This establishes a source-owned HBA entry and a
buildable binding path; full stock-output parity, transient pool peak and
physical execution remain unverified.

`native_hrv_calc.c` projects the initializer's 308-byte native context and
eleven owned history buffers into a persistent typed HRV context and runtime.
It aliases the 48-byte extrema record and 696-byte decision record, retains
state between frames, copies the process counters to the native owner and
maps six typed outputs to the public result on update. Init and deinit clear
the typed binding before freeing native allocations. The ignored host projection check
`build/r1-hba-borrowed-graph-view-20261111/test_native_hrv_projection.c`
verifies all eleven native descriptor offsets and capacities, pointer
ownership, repeated calls and reset on unbind. The source receipt
`build/sources-r1-hrv-calc-final-20261111/report.json` compiles 954/954
application and 82/82 bootloader units with no duplicate strong symbols.
Its strict application receipt has only NADT unresolved; the partial map
uses 690,120 flash bytes and ends static RAM at `0x2003B328`. The strict
bootloader link passes. Native HRV output parity and live-device behavior
remain unverified.

The ignored `build/r1-hba-calc-link-probe-20261111/link.py` retains the real
HBA and HRV entries. With an invalid build-only caller that reaches only the
typed NADT stream root, it links at 694,328 flash bytes, leaving 1,992 bytes.
When the caller also reaches the real primary, auxiliary and alternate NADT
classifier cores required by the stream's window callbacks, the link uses
701,240 bytes: 4,920 beyond the 696,320-byte flash region before any real
NADT adapter code. Both probe variants have `__bss_end__=0x2003B328`, leaving
19,672 static RAM bytes. These probes are never firmware images. The full
classifier path needs flash savings as well as native configuration, state and
callback binding before it can link.

`r1_cfg_byte_get_73798` now expresses its initialized byte and NV read in C.
The stock wrapper read only that byte, so the upper saved-stack bytes were
unobserved. The latest receipt
`build/sources-r1-hba-elapsed-cfg-20261111/report.json` still compiles all
1,034 R1 units, and its strict bootloader link passes. The strict application
link still has the three calculation roots. An assembly syntax scan now finds
95 occurrences across 24 R1 C files.

The Goodix algorithm pool is 30,016 bytes (`0x7540`) and already owns the
native HBA contexts, nine filter buffers, nine packed queues, seven float
histories, three graphs and their recurrent states. The typed HBA runtime is
14,704 bytes on the Arm target and now has static storage in the source-owned
HBA entry. The mode-6 executor's 4,320-byte temporary and mode-1 scratch
use the shared Goodix pool. Their live peak lifetime and allocation behavior
remain unmeasured; the source-build and strict-link receipts do not prove
runtime fit.

Before the real HBA and HRV entries, the ignored
`build/r1-hba-memory-probe-20261111/link_probe.py` linked
build-only invalid calculation callers while retaining one typed HBA runtime,
one three-graph plan set, one quantized runtime and a 4,320-byte mode-6
temporary in static RAM. With the indexed callbacks and elapsed-state bridge
and the three mode-buffer spans reachable, it links at 692,952/696,320
flash bytes, with `__bss_end__=0x2003BB2C` and 17,620 bytes to the RAM top. This is a
reachability and storage ceiling measurement, not a working firmware image:
the three fake root calls receive null arguments, and actual adapters may
add code, RAM and stack usage. It leaves only 3,368 flash bytes under the
current link layout, so the remaining adapters require size scrutiny.

The ignored reachability probe
`build/r1-goodix-root-reachability-20261111/link_probe.py` linked an earlier
application with build-only invalid callers that make all three typed roots
and the HBA/HRV runtime binders reachable. It resolves the three imports and
links at 690,664 of 696,320 flash bytes, 26,944 bytes above the current
unbound graph. The remaining 5,656 bytes are only a provisional ceiling for
the real native adapters and any additional dependencies they reach. This
probe never calls the algorithms at runtime and is not a firmware candidate.

An Arm type-size probe under `build/r1-hba-memory-probe-20261111/` measures
the three-graph HBA plan set at 2,308 bytes, NADT typed stream state at
144 bytes, NADT plan at 44 bytes, and the owned NADT workspace at 1,400
bytes. The production NADT workspace view reuses its 1,588-byte native
owner; the typed state and plan still need source-backed native field mapping
before the public calculation entry can be linked as an algorithm.

## Size-optimized NADT reachability, 2026-11-11

The application manifest now builds 80 more application units with `-Oz` and
`-mno-global-merge`. The ignored probe in
`build/r1-hba-calc-link-probe-20261111/oz/` first recompiled the selected
units with otherwise unchanged Clang arguments and linked them under their
original object basenames, so the recovered linker's object-name wildcard
still applies. Exported symbol names, kinds, data sizes and Arm ABI attributes
match the preceding objects; function sizes and the expected optimization
attribute differ. This is a size and ABI check, not behavioral equivalence.

The authoritative manifest build
`build/sources-r1-nadt-oz-dfu-c-20261111/report.json` compiles 954/954
application and 82/82 bootloader units without duplicate strong symbols.
The strict application has only `goodix_nadt_calc` unresolved; its partial
map uses 680,536 flash bytes. The strict bootloader links with valid vectors
and no undefined references. With a **build-only invalid NADT caller** that
reaches the stream and all three real classifier cores, the current manifest
objects link at 691,656 of 696,320 flash bytes, leaving 4,664 bytes for the
production NADT binding and any further dependencies. This is not an
application image: the probe passes null algorithm inputs and is never
registered in the source manifest. `__bss_end__` is `0x2003B328`, leaving
19,672 static RAM bytes in this probe.

The DFU response entry in `native_dfu_backend.c` now uses a six-word C
automatic HVX frame and calls the existing C response worker. Its Arm object
compiles cleanly; device or stock-call parity for this changed wrapper has
not yet been measured. The assembly syntax scan falls to 94 occurrences
across 23 R1 C files.

After the four-window stream correction, the latest authoritative source
receipt is `build/sources-r1-nadt-window-view-final-20261111/report.json`:
955/955 application and 82/82 bootloader units compile, with no duplicate
strong symbols. The strict application receipt still has only
`goodix_nadt_calc` unresolved and its partial map uses 680,552 flash bytes.
The strict bootloader links. The same build-only NADT classifier reachability
probe now uses 691,736 flash bytes and ends static RAM at `0x2003B328`;
4,584 flash bytes remain before a real public calculation adapter and any
further dependencies. It is still an invalid caller, not a firmware image.

## Source-owned NADT calculation link, 2026-11-11

`native_nadt_calc.c` now implements the public `goodix_nadt_calc` entry. It
loads the native state and configuration views, uses the initializer-owned
workspace and filter histories, calls the typed stream, and binds the primary,
auxiliary and alternate classifier callbacks. The primary callback shares
native autocorrelation state with the alternate callback. The auxiliary and
alternate callbacks keep their native mode and consecutive counters. The
source-owned 253-float boundary-filter coefficient table matches the locked
application data at `0xB154C` byte for byte in the ignored
`test_nadt_coefficients.c` check. The primary configuration view maps the
locked `0x47240` field reads, and the alternate autocorrelation state maps
the locked `0x31624` writes at native offsets `+36` and `+68`.

The source receipt `build/sources-r1-nadt-root-fix-20261111/report.json`
compiles 957/957 application and 82/82 bootloader units with no duplicate
strong symbols. `build/r1-link-nadt-root-fix-20261111/report.json` links the
application with zero undefined references, valid vectors and 696,104 of
696,320 flash bytes used. Static RAM ends at `0x2003C570`, leaving 14,992
bytes to the top of RAM before runtime stack/pool use. The bootloader receipt
`build/r1-boot-link-nadt-root-fix-20261111/report.json` links with valid
vectors and no undefined references. All objects come from the R1 source
manifest and configured toolchain/runtime libraries; no stock executable
region is included in either strict link.

This is a source-build and link result. The new NADT binding has passed host
projection checks, but not a locked-stock output replay, allocator peak
measurement or physical-device run. The 216-byte flash margin is especially
tight. The remaining assembly syntax in R1 C sources and the repository's
byte-identity target are separate unresolved gates.

The device-ID read boundary now supplies the native worker's saved-register
scratch as a C automatic five-word frame. The cached-copy and address-format
paths still call the same worker; all source callers use its void ABI, so no
source caller consumes the old return-register side effects. The later receipt
`build/sources-r1-device-id-c-20261111/report.json` compiles the same 957
application and 82 bootloader units. Its strict application and bootloader
links pass; application flash use is 696,136 of 696,320 bytes. This removes
one handwritten assembly wrapper. The original register-level side effects
have not been replayed against stock callers.

The registered device-info handler and its response wrapper now use C stack
storage and normal C calls. An ignored host check under
`build/r1-device-info-c-20261111/` verifies the null-payload branch, packet
sequence, response arguments and 32-byte firmware/hardware payload. The
source receipt `build/sources-r1-device-info-c-20261111/report.json`
compiles 957 application and 82 bootloader units without failures or duplicate
strong symbols. Both strict links pass; application flash use returns to
696,104 bytes. This removes 13 more assembly syntax occurrences from one C
file. Raw return-register behavior remains outside this host check.

The device-ID status clear, operation-11 response and registered command
handler now use C bodies and a 64-byte C response frame. The ignored host
check under `build/r1-device-command-c-20261111/` covers the null request,
status clear, packet sequence, 25-byte response payload and source-owned
operation arguments. `build/sources-r1-device-command-c-20261111/report.json`
compiles all 1,039 R1 units; the strict application and bootloader receipts
both link. Application flash use is 696,040 bytes, leaving 280 bytes. This
removes the last three `__asm__` uses from that file. Stock register residues
and physical protocol behavior remain unverified.

The system wear-status operation-3 sender now uses a normal C call. Its
ignored host check under `build/r1-system-command-c-20261111/` verifies the
null request, packet sequence, mode-to-byte mapping and one-byte response.
`build/sources-r1-system-command-c-20261111/report.json` compiles all 1,039
R1 units, and both strict links pass. Application flash use is 696,024 bytes,
leaving 296 bytes; 75 `__asm__` occurrences remain across 19 R1 C files.

The special-target protocol event leaf `r1_protocol_command_00084cc0` now
expresses its length and publish branches directly in C. The earlier register
constraints did not emit instructions, and the final source receipt
`build/sources-r1-protocol-leaf-c-20261111/report.json` still compiles all
1,039 units. Both strict links pass; flash use remains 696,024 bytes. The
source scan falls to 65 `__asm__` occurrences across 19 R1 C files.
