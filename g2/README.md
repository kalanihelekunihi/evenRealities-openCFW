# openCFW

`openCFW` is the source-controlled build boundary for an independently
maintainable Even Realities G2 firmware. It currently produces three pinned
profiles from the official `s200_v2.2.6.10` compatibility inputs:

- a byte-identical reference reconstruction; and
- the preserved first ring-source milestone; and
- a source-divergent build whose Apollo application appends a compiled
  multi-module Apollo overlay containing ring forwarding plus source
  replacements for UI-module registry event/data dispatch, broadcast close,
  initialization, mode lookup, display-mode switching, and startup
  application-ID policy, onboarding/input handling, and the registered main
  display-thread loop, its dynamic callback, the application-wide variadic
  logging dispatcher, conversion parser/core, divide-by-ten runtime, LVGL
  tick increment/get/elapsed runtime, zero-fill wrapper, global-state
  initializer, subsystem initialization sequence, and full-screen buffer
  synchronizer, display-driver thread/message-queue initialization, teardown,
  resource arbitration, timer lifecycle/callback, queue command 8, complete
  manager receive loop and command dispatcher, public clear/init/power/
  brightness/reflash queue senders, forced display lifecycle, and the shared
  file open/close/read/write/seek/tell/size/flush/remove/rename/mkdir/opendir/
  readdir/closedir runtime and synchronized allocation/free/reallocation
  wrappers and their two-mutex runtime initializer,
  the Apollo510 instruction-cache enable/disable and data-cache
  enable/invalidate/clean HAL,
  and
  complete integer, string, padding, width, precision, and floating-point
  formatting cluster, both
  display/input setup helpers,
  and its
  display-subsystem initializer; the complete
  lens-side initializer; both lens-side accessors; the Apollo510 GPIO
  configuration/state/interrupt control/status/clear HAL; and the EvenHub
  RLE/LZ4 decompression, container-lookup, lifecycle, page/common/UI
  callbacks, and IMU policy layer.

This is not yet a clean-room replacement firmware. The five non-Apollo
components and almost all of the Apollo application remain opaque. The current
source coverage is recorded precisely in
[`docs/source-coverage.md`](docs/source-coverage.md), so later replacements can
be measured rather than estimated. The upstream-first attribution queue and
focused configuration gaps are tracked in
[`docs/upstream-inventory.md`](docs/upstream-inventory.md).
The concise cross-domain status, percentage definitions, and current
dependency-identification estimates are maintained in
[`docs/progress.md`](docs/progress.md).
The authenticated whole-image
[`__FILE__` census](docs/research/apollo-embedded-source-path-census.md)
maps 314 of 357 retained build paths to 1,760 functions in the 64-shard
Ghidra corpus, separating 530 third-party anchors from 1,230 project/first-party
anchors without treating function counts as byte coverage.
The follow-on [Cordio WSF timer recovery](docs/research/cordio-wsf-timer-source-recovery.md)
raises the reviewed effective count to 7,378, maps the complete 536-byte
Ambiq/FreeRTOS timer cluster and its SRAM ABI, and adds a host-tested,
production-excluded eleven-function clean-room candidate. Official AmbiqSuite
2.5.1 is now pinned as the exact implementation/source family by an
archive-only saved-tick discriminator; Packetcraft r19.02 remains a public
two-function semantic oracle. Minor local text/config drift, compiler output,
and production placement remain unresolved.
The adjacent [WSF OS/queue recovery](docs/research/cordio-wsf-os-queue-source-recovery.md)
adds 18 bounded functions / 774 stock bytes, closes the effective ten-handler
64-byte task ABI and generic queue ABI, and preserves Lorelei's complete
234-row stock-ABI matrix. Both modules are behaviorally recreated and
host/ARM-compile tested, but remain production-excluded; the exact historical
ten-handler definition site and IAR output are still unresolved.

The public-host follow-on also closes the complete
[ATT CCC module](docs/research/cordio-atts-ccc-source-recovery.md): all fourteen
linked functions / 2,770 code bytes, the 24-byte three-connection control
block, six product settings, and every direct/registered callback ingress.
Exact Apache definitions are available from Packetcraft, while stock event
`0x14` selects the r20 ATT header family. Product diagnostics and exact IAR
placement remain before source promotion; package bytes are unchanged.

The adjacent
[ATT discovery module](docs/research/cordio-attc-disc-source-recovery.md)
closes fifteen linked functions / 2,908 code bytes and the full 3,012-byte
translation unit. The r20-only characteristic-match behavior selects
Packetcraft r20.05--r20.05c, while three unused included-service routines are
dead-stripped. Its state ABI, direct callers, and pointer/interior ingress are
fully bounded; package bytes remain unchanged.

The following
[legacy advertising module](docs/research/cordio-dm-adv-leg-source-recovery.md)
closes seventeen linked functions / 4,396 code bytes, both registration
tables, the two-set SRAM ABI, and the IAR-interleaved trailing literal pool.
Packetcraft supplies exact Apache definitions, while stock's inline data
payload selects Ambiq's flexible-array message ABI. Package bytes remain
unchanged.

The matching
[common advertising module](docs/research/cordio-dm-adv-source-recovery.md)
closes nine linked functions / 562 code bytes and the complete 572-byte
translation unit. Its `DmAdvSetData` producer independently proves the same
Ambiq flexible-array ABI by allocating `len+8` and copying payload inline;
the public Packetcraft pointer layout is rejected. Six unused APIs are
dead-stripped, Lorelei's two closure links have zero undefined symbols, and
package bytes remain unchanged.

## Build

Requirements are Python 3.9 or newer, POSIX `make`, a shell, and the reviewed
Clang release family shown in
[`components/apollo_main/ring_gesture/overlay.json`](components/apollo_main/ring_gesture/overlay.json).
The reviewed builds use Apple Clang 21.0.0, including the compiler shipped with
Xcode 26.6.0. Set `OPENCFW_CLANG` to an alternate executable only when it
reports that release family. Exact overlay and component hashes remain pinned,
so a patch build that changes generated bytes is still rejected.

```sh
cd openCFW
./make.sh
```

The build fails closed if a blob hash, inner checksum, vector table, region
partition, protected boundary, EVENOTA checksum, or final reference hash does
not match the reviewed layout.

Useful targets:

```sh
./make.sh vendor-snapshots
./make.sh verify
./make.sh test
./make.sh inspect
./make.sh clean
```

There is also a second, independent profile:

```sh
make -C g2 transparent
```

`transparent` does not extend the byte-exact reconstruction above. It builds an
Apollo main image in which every byte has a source unit behind it — recovered
code compiled from the Ghidra corpus, declared data arrays, or an explicit trap
where nothing was established — and reports what it did and did not establish.
The resulting image is **not known to run**: decompiler output is recovered
structure, not reviewed behavior. Read
[`docs/transparent-source.md`](docs/transparent-source.md) before drawing any
conclusion from it, and
[`docs/transparent-source-ledger.md`](docs/transparent-source-ledger.md) for the
measured result.

`vendor-snapshots` verifies the pinned TLSF, EasyLogger, littlefs,
FreeRTOS-Kernel, AmbiqSuite Apollo510, Arm CMSIS Core, CMSIS-FreeRTOS, LZ4,
FreeType, FlashDB, CmBacktrace, nanopb, Packetcraft Cordio,
FreeRTOS-Plus-CLI, LVGL, Ring-Buffer, and TinyFrame inputs, licenses, and
provenance without network access. The
FreeType 2.9.1 gate also authenticates the official annotated tag/peeled
commit chain, all 297 selected upstream files, unchanged FTL, and recovered
ten-module G2 order. It also authenticates the v40/minimal TrueType setup,
substantive GX service depth, and recovered `am_ftsystem.c` allocator and
constructor-side lifecycle seams. FreeType remains production-excluded pending
the remaining configuration toggles, exact compiler/linker details and
destructor symbols, external font payload recovery, and explicit promotion
review. The
FlashDB 2.1.1 gate authenticates the signed commit payload behind the
lightweight release tag, reconstructs the seven required Git trees to prove
the exact 14-file KVDB/FAL path/blob closure, and authenticates the recovered
G2 1-bit/4-KiB/cache/object/partition ABI. Static evidence proves there is no
live/retained TSDB subsystem, while the original `FDB_USING_TSDB` macro state
is not claimed. A production-excluded read-only port now matches the
authenticated upstream FAL partition dispatcher, enforces overflow-safe
partition bounds and the recovered CMSIS mutex, maps every nonzero MX25
status to an error, and makes write/erase unconditionally fail. The snapshot
and port remain production-excluded while golden-capture validation,
non-destructive mount policy, and schema semantics are incomplete. The
`kvbooCount` zero default and read/increment/write lifecycle are now
authenticated. Additional production-excluded snapshots
use explicitly documented openCFW compatibility choices rather than false
vendor-version claims: CmBacktrace `73714489`, nanopb 0.4.9, Cordio r20.05c,
FreeRTOS-Plus-CLI `43defa56` plus the isolated G2 blank-input patch, and LVGL
9.3-development ceiling `344c7c`. Their verifiers reconstruct the applicable
Git commit/tree/blob closure offline, and their READMEs keep Ambiq/Even ports,
generated schemas, commands, assets, and other first-party glue outside the
upstream boundary. The TLSF,
EasyLogger, and littlefs
verifiers also pin recovered G2 ABI/configuration evidence; the FreeRTOS
snapshot verifier authenticates the upstream baseline, while
`verify` also runs read-only focused analyzers for the littlefs block port and
the recovered FreeRTOS IAR `ARM_CM55_NTZ/non_secure` selection, G2
configuration, tick, interrupt-mask, heap, and TCB seams. The FreeRTOS
snapshot also retains exact V10.5.1 `heap_4.c` as an authenticated,
unselected reference; it is not compiled or linked. TLSF and the first
EasyLogger and FreeRTOS boundaries are source-integrated, including the
four-function generic queue-creation cluster, three public queue/semaphore
constructor wrappers, the exact Cortex-M55 interrupt-mask save/restore pair,
and three exact upstream task-state getters. Thirty Apollo-main and twenty-six
bootloader littlefs v2.10.1 functions are source-integrated: nineteen and
fifteen private leaves, respectively, plus eleven utility leaves in each image;
only the complete core/block-port replacement remains gated on a golden
external-flash capture. A focused AmbiqSuite 5.1 section-GC build reduces
`am_hal_mspi_interrupt_clear` to a 48-byte source-equivalent leaf matching
the stock ABI and register behavior, with no private state or unresolved
references. Its pinned Apollo510/CMSIS source closure is now vendored and
verified offline. Both production overlays compile the complete authenticated
translation unit, retain only that relocation-free function section, reject
the unrelated Ambiq state, and install authenticated main and boot redirects.
The wider `am_hal_mspi_control` ordinal mismatch remains an explicit boundary.
These upstream reuse boundaries are documented in
[`third_party/easylogger/README.openCFW.md`](third_party/easylogger/README.openCFW.md),
[`third_party/littlefs/README.openCFW.md`](third_party/littlefs/README.openCFW.md),
[`third_party/freertos-kernel/README.openCFW.md`](third_party/freertos-kernel/README.openCFW.md),
[`third_party/ambiqsuite-apollo510/README.openCFW.md`](third_party/ambiqsuite-apollo510/README.openCFW.md),
[`third_party/cmsis-core/README.openCFW.md`](third_party/cmsis-core/README.openCFW.md),
[`third_party/lz4/README.openCFW.md`](third_party/lz4/README.openCFW.md),
[`third_party/freetype/README.openCFW.md`](third_party/freetype/README.openCFW.md),
[`third_party/flashdb/README.openCFW.md`](third_party/flashdb/README.openCFW.md),
[`third_party/ring-buffer/README.openCFW.md`](third_party/ring-buffer/README.openCFW.md),
and
[`third_party/tinyframe/README.openCFW.md`](third_party/tinyframe/README.openCFW.md).

Generated files live under `build/`:

- `reference/package/g2-openCFW-s200_v2.2.6.10.evenota.bin` — the deterministic
  reference artifact. Its SHA-256 is
  `f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa`,
  byte-identical to the pinned official bundle.
- `ring-source/package/g2-openCFW-s200_v2.2.6.10-ring-source.evenota.bin` —
  the preserved first source-divergent milestone. Its pinned SHA-256 is
  `cde2fc78d14862a08211b4aedf03687e4c1b1855789f71326f9a2f496aad300f`.
- `source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin` — the
  current source profile, which also replaces the stock lens-side initializer,
  both duplicated lens-side accessors, the GPIO pin-configuration read/write
  and state read/write functions, the complete bounded GPIO interrupt HAL
  through handler registration and dispatch, the UI-module registry
  event/data dispatch, broadcast close, initialization, mode lookup, and
  display-mode/startup-application policy, onboarding-state gate, and packed
  input-event handling including ring forwarding, plus the registered main
  display-thread command loop, dynamic display callback, both display/input
  setup helpers, the dynamic-handler setter and installed handler, the
  application-wide variadic logging dispatcher, conversion parser/core, and
  its decimal, hexadecimal, string, padding, width, precision,
  floating-point, and 64-bit divide-by-ten helpers, plus the LVGL tick
  increment, dynamic getter, wrap-safe elapsed-time helpers, zero-fill
  wrapper, global-state initializer, subsystem initialization sequence, and
  full-screen buffer synchronizer, installed display synchronization
  callback, display setup sequence, and display-buffer lock/unlock/init
  cluster, plus PRIMASK enable/disable and display-task attribute primitives,
  plus display-driver thread/message-queue initialization, teardown, resource
  arbitration, timer lifecycle/callback, queue command 8, and the complete
  manager receive loop and command dispatcher plus public clear/init/power/
  brightness/reflash queue senders and forced display initialization/
  deinitialization lifecycle, shared file
  open/close/read/write/seek/tell/size/flush/remove/rename/mkdir/opendir/
  readdir/closedir runtime and synchronized allocation/free/reallocation
  wrappers and their two-mutex runtime initializer,
  the Apollo510 instruction-cache enable/disable and data-cache
  enable/invalidate/clean HAL,
  the application-wide memory comparator,
  the Apollo510 secure-OTA descriptor-addition routine,
  the BLE message-transmit thread entry, queue lifecycle, draining, clearing,
  message allocation/construction, backpressure, enqueue, wakeup, and direct
  protobuf-send, notification, guarded OTA/left-side/command-role paths,
  streaming notification, transport-three transmission, and EFS send/notify
  wrappers, plus the variadic string-scanner adapter and source input
  callback, and the littlefs directory, recovery, initialization,
  boot-count, flash read/program/erase, and sync cluster,
  plus the CMSIS event-loop queue/timer/mutex/thread initializer, blocking
  worker, queue push path, timer scheduler, delayed insertion, and delayed
  removal cluster, and the adjacent BLE connection-parameter immediate-update
  and delayed-scheduling routine, both connection-mode selectors, their
  coordinator, delayed connection callback, remote-parameter handler, and
  connection-update event state machine, connection-global initializer, and
  stream/mode control helpers, connection-event dispatcher, MRAM zero-region
  programmer, protected update-flag setter, and protected-record diagnostic
  dump, synchronizer, record-list loader, and split-transaction single-record
  programmer, plus the application record-database update and replacement
  selector, record deactivation/activation/conditional deactivation, and
  record membership/presence/traversal/count/oldest query helpers and
  threshold-evicting allocator,
  shared string-length, character-search, ASCII case-folding, integer-
  formatting, decimal power-scaling, byte-span emission, runtime zeroing,
  lookup-layout, byte-map, style initialization/reset/removal/set,
  transition/default value, style-flag, and linked-list initialization,
  head/before/tail insertion, removal, callback clearing, access,
  move-before, and link-setter primitives and
  generic ring-read/write primitives, the asynchronous four-channel
  display sink, its display-operation submit dispatcher, all four operation backends, and
  shared operation-start, lower-level operation-begin, operation-service,
  direct display FIFO reader/writer, FIFO-to-ring fill, ring-drain, event-side
  begin/service, IRQ-side transport owner, and its special-transfer MMIO,
  result, cleanup, and event-abort helpers, the shared Apollo510 microsecond
  delay primitive, its millisecond/microsecond wrappers, and its exact ITCM
  cycle-loop load image, the bounded formatting span adapter and its shared
  length-prefixed buffer writer, unsigned LEB128/prefix and signed zigzag
  encoders, shared/fixed-width append primitives, and field-key/descriptor
  encoding, plus boolean/integer/fixed scalar adapters, the two-pass
  submessage writer, bytes/string/submessage-field adapters, and the generic
  message and regular/indirect/extension/repeated field encoders,
  default-value checking, and field-value dispatch, and display-subsystem
  initializer, the division-free ARM EABI signed and unsigned 64-bit
  division/modulo runtime, the four eight-byte lens/status packet reporters,
  lens-status publication selector, and five state accessors, the SARC
  crash-report header, staging, finalization, and file-persistence helpers,
  the wrap-extending monotonic-seconds helper, the bounded wall-clock seconds
  and validity helper, the shared interrupt-disable primitive, and the
  boot reset-status and source firmware-version encoders, the EasyLogger
  tracepoint deferral/callback/begin path, bounded capture retry, reflected
  state CRC-32, filename/path parsing, directory scan, persistent-state
  load/store, storage initialization, active-file close/flush, oldest-file
  pruning, creation/header emission, append reopen, bounded write/rotation,
  commit, idempotent timer bootstrap, protobuf onboarding control-state
  update, gated wear-status notification, deferred flag persistence,
  onboarding-flag change detection/update, peer flag notification/reply, and
  peer onboarding-process synchronization, onboarding runtime and timer-
  service thread initialization, dynamic and static-control-block RTOS
  timer-object creation, their shared initializer, and signed task/ISR timer
  command submission, auto-reload catch-up, expired-timer processing, and the
  timer-service task loop, wait-or-expire processor, active-list query, and
  tick/list-switch sampler, timer-list insertion helper, and timer-command
  drain, timer-list overflow switch, timer list/queue runtime initializer,
  timer active-state query, timer callback-context getter, and pended-callback
  ISR submission, static and dynamic RTOS event-group creation, and
  RTOS event-group wait, clear-bits, clear-from-ISR, and ISR-safe
  bit-snapshot and task-context set-bits operations plus both set-bits and
  clear-bits timer callbacks, the shared wait-condition predicate, and
  set-from-ISR submission, priority-1 RTC clock initialization, and RTC
  calendar/time setting and reading, plus the private Apollo510 peripheral-
  power descriptor lookup and complete 34-entry source table, plus the
  cached Apollo510 trim-version getter, MCU HP/LP switching sequence, and
  public MCU-mode selector, GPU-mode status getter, GPU-mode selector, MCU
  memory-power configuration, ROM power-domain enable/disable, and
  shared-SRAM power configuration, the private crypto power-down quiesce
  helper, public peripheral-power enable, private disable-domain mask
  checking, public peripheral-power disable, and public peripheral
  enabled-state query, plus private INFO1 cache population and public
  low-power initialization,
  plus the FreeRTOS V10.5.1 static/dynamic generic queue creators, public
  static-mutex, static-counting-semaphore, and dynamic-counting-semaphore
  constructors, private
  new-queue and mutex initializers, public mutex-create, recursive mutex
  give/take, task-context generic-send, semaphore/mutex-take queue boundary,
  and the private queue-empty and queue-full state predicates, plus all four exact
  upstream list initialization, end-insertion, ordered-insertion, and removal
  entries, plus the exact upstream current-task-handle, task-count, and
  scheduler-state getters, plus the exact upstream littlefs private sequence
  comparator, metadata-list remove/append, filesystem disk-version getter and
  major/minor extractors, metadata-list open predicate, allocator-checkpoint/drop pair,
  file-position getter, and dual-image
  `lfs_max`/`lfs_min`/`lfs_aligndown`/`lfs_alignup` utility quartet, plus the
  source-equivalent EasyLogger output/color/format/filter and output-lock
  control cluster plus the five-slot tag-level default initializer and
  tag-level getter,
  plus the exact authenticated AmbiqSuite 5.1.0
  `am_hal_mspi_interrupt_clear` translation-unit leaf in both Apollo images,
  plus exact FreeRTOS V10.5.1 `ulSetInterruptMask` and
  `vClearInterruptMask` portable-layer assembly copied source-for-source at
  their original public addresses,
  plus
  the EvenHub RLE/LZ4
  decompression, container lookup, lifecycle, page/common/UI callbacks, and
  IMU policy layer. Its pinned SHA-256 is
  `297f2cded60e2f63ed2cf56a63842802f169ef9ff8e17045aca110edf6880483`.
- `reference/regions/` and `source/regions/` — controller- and
  function-specific raw regions. Addressed files include their target address
  in the filename.
- each profile's `flash-plan.json`, `build-report.json`, and `SHA256SUMS` —
  machine-readable mapping and reproducibility evidence.

The current source Apollo component is generated under
`components/apollo_main/core_overlay/build/`. Its compiler report pins every
source input, the mini-linked overlay, complete component, toolchain,
functions, relocations, redirects, and runtime addresses.
The bootloader uses a distinct raw-provider builder under
`components/bootloader/core_overlay/`: it appends exact-upstream littlefs
leaves and the isolated AmbiqSuite leaf below the Apollo-main boundary,
verifies every overwritten stock span, and regenerates the package-level
EVENOTA integrity fields without inventing an Apollo-main staging preamble.

The build assembles artifacts but never opens a serial port, debugger, or
flasher. Existing SybilSight recovery/OTA tools can consume the rebuilt
EVENOTA package after their own hardware and safety preflights. Package offsets
must never be treated as controller flash addresses.

### Reproducible builds without Apple clang (toolchain profiles)

The byte-exact overlay pins above assume the reviewed Apple clang, which cannot
run on Linux. An additive **toolchain-profile** layer makes the compiled
profiles reproducible under an alternate reviewed compiler (today a Linux
Homebrew clang) without disturbing the canonical `apple-clang` reference: each
profile carries its own independently recorded, fail-closed pins. Toolchain
selection is automatic — the Makefile detects a present clang and its matching
profile via `tools/detect_toolchain.py`:

```sh
./make.sh toolchain      # show the resolved compiler + profile
./make.sh reference      # byte-identical to the official bundle (any profile)
./make.sh ring-source    # compiles + verifies under the detected profile
./make.sh source verify  # full Apollo overlay + bootloader, all profiles verified
```

On a Linux Homebrew clang, `reference`, `ring-source`, and the full `source`
build (the complete Apollo overlay and bootloader) all build and `verify`
fail-closed against recorded `linux-clang` pins. The canonical Apple-clang
overlay is 116,034 bytes and records 596 functions; Linux carries its own
117,882-byte overlay pin.
blob-only `reference` reconstruction is compiler-independent and stays
byte-identical everywhere. The `apple-clang` profile remains the
provenance/reference anchor; alternate-profile artifacts are reproducible
independent builds, not the vendor-reviewed firmware. Policy, recording, and
current Linux coverage are documented in
[`docs/linux-reproducible-build.md`](docs/linux-reproducible-build.md).

## Layout

- `blobs/official/g2-2.2.6.10/` contains the six payloads extracted from the
  official bundle.
- `manifests/g2-2.2.6.10.json` is the authoritative package order, provider
  ledger, functional split, address evidence, and protected-region policy.
- `manifests/g2-2.2.6.10-ring-source.json` inherits that map and replaces only
  the Apollo-main provider and its more granular source/opaque region split.
- `manifests/g2-2.2.6.10-core-source.json` is the current profile and further
  splits out every fully replaced stock function.
- `third_party/tlsf/` contains the verified and integrated TLSF v3.1
  source-equivalent snapshot, recovered configuration ledger, license, and
  snapshot verifier used by the source allocator replacement.
- `third_party/easylogger/`, `third_party/littlefs/`, and
  `third_party/freertos-kernel/` contain authenticated upstream snapshots,
  per-file provenance pins, licenses, and offline verifiers. G2 configuration,
  port glue, and fixed-address bindings remain outside the pristine vendor
  trees.
- `tools/open_cfw.py` validates, assembles, splits, and wraps future
  source-built raw images.
- `tools/apollo_overlay.py` is the reusable freestanding compiler, mini-linker,
  branch encoder, stock-byte guard, and Apollo component generator.
- `components/` defines the replacement contract for moving each opaque
  payload to source.
- `docs/memory-map.md` explains the first-pass address map and its confidence.
- `docs/upstream-inventory.md` separates exact upstream candidates,
  configuration-fingerprint work, and genuinely proprietary boundaries.

## Current source replacement

The preserved `ring_gesture` profile compiles two freestanding Cortex-M
functions into a 160-byte overlay. The current `core_overlay` profile builds
those functions together with the host-tested lens-side policy,
`open_cfw_initialize_lens_side`, `open_cfw_lens_side`, and the EvenHub
RLE/LZ4 decompression, container lookup, page/common/UI callbacks, and
six-function lifecycle/IMU layers, plus source-built and host-tested
UI-module registry event/data dispatch, broadcast close, initialization, and
mode lookup, the adjacent display-mode transition state machine, and
startup application-ID policy, onboarding-state gate, and complete packed
input-event handler, the registered main display-thread command loop, its
dynamic callback, two display/input setup helpers, and display-subsystem
initializer, the dynamic-handler setter, and its installed forwarding handler,
plus the application-wide variadic logging dispatcher, its complete
conversion parser/formatter core, all eight width/integer/string helpers,
the bounded floating-point converter, the adjacent unsigned 64-bit
divide-by-ten runtime, and the LVGL tick increment/get/elapsed, zero-fill,
global-state/complete subsystem initialization runtime, full-screen buffer
synchronizer, installed display synchronization callback, and display setup,
plus display-buffer lock/unlock/mutex and port initialization and PRIMASK
enable/disable and display-task attribute access, plus display-driver
thread/message-queue initialization, teardown, resource arbitration, timer
lifecycle/callback, queue command 8, and complete manager receive loop and
command dispatcher plus public clear/init/power/brightness/reflash queue
senders and the forced initialization/deinitialization lifecycle, plus the
shared file open/close/read/write/seek/tell/size/flush/remove/rename/mkdir/
opendir/readdir/closedir runtime and synchronized allocation/free/
reallocation wrappers; shared
application-wide memory comparison, Apollo510 secure-OTA descriptor
addition, and the BLE message-transmit thread entry, setup-stage adapters,
queue/no-op hooks, thread creation/destruction lifecycle, nonblocking queue
drain and command router, queue clearing, message allocation/construction,
backpressure, enqueue, thread wakeup, direct protobuf-send/notification OTA
gates, guarded protobuf policy, streaming notification, transport-three
transmission, EFS send/notify wrappers, and the variadic string-scanner
adapter with its source input callback, plus the littlefs directory check,
format/mount recovery, initialization and boot-count path, flash
read/program/erase callbacks, and exact sync callback,
plus the CMSIS event-loop initializer, worker/push path, timer scheduler,
delayed insertion, delayed removal, and adjacent BLE connection-parameter
update scheduler, both mode selectors, the connection-mode coordinator, and
the delayed connection callback, remote-parameter handler, and
connection-update event state machine, connection-global initializer, and
stream/mode control helpers, connection-event dispatcher, MRAM zero-region
programmer, protected update-flag setter, and protected-record diagnostic
dump, synchronizer, record-list loader, and split-transaction single-record
programmer, plus the application record-database update and replacement
selector, record deactivation/activation/conditional deactivation, and
record membership/presence/traversal/count/oldest query helpers and
threshold-evicting allocator,
thread-flag dispatch, and wait handler,
string-length and generic
ring-read/write
primitives, asynchronous four-channel display
sink, its operation submit dispatcher and all four operation backends, and
shared operation-start, lower-level and event-side begin, transmit/event
operation service, event abort, IRQ-side transport owner and special-transfer
helpers, direct display FIFO reader/writer, FIFO-to-ring fill, and ring-drain
helpers, the shared Apollo510 microsecond delay primitive, its exact
millisecond/microsecond wrappers and six-byte ITCM cycle-loop load image, plus
the formatting span adapter, its shared length-prefixed buffer writer,
unsigned LEB128/prefix and signed zigzag encoders, and shared append primitive,
fixed-width append and field-key/descriptor writers, the shared boolean reader,
boolean/integer/fixed scalar adapters, the two-pass submessage writer, and
bytes/string/submessage-field adapters, plus the generic message,
regular/indirect/extension/repeated field encoders, default-value checker,
and field-value dispatcher, the ARM EABI signed/unsigned 64-bit
division/modulo runtime, four eight-byte lens/status packet reporters, the
lens-status publisher and state accessors, the SARC crash-report staging,
state, and persistence helpers, the wrap-extending monotonic-seconds helper,
the bounded wall-clock seconds and validity helper, the shared interrupt-
disable primitive, the boot reset-status and source firmware-version encoders,
the EasyLogger tracepoint deferral/callback/begin and bounded capture-retry
cluster, its filename grammar, directory scan, `TPS1` persistent-state
load/store, storage initializer, active-file close/flush, pruning,
creation/header emission, append reopen, bounded write/rotation, commit,
idempotent timer bootstrap, protobuf onboarding command/control-state update,
gated wear-status notification, deferred flag persistence, onboarding-flag
change detection/update, peer flag notification/reply, peer onboarding-process
synchronization, onboarding runtime/timer-service thread initialization, and
dynamic and static-control-block RTOS timer-object creation and their shared
initializer, command-submission path, auto-reload catch-up loop, and
expired-timer processor, timer-service task loop, and timer wait-or-expire
processor, active-list query, tick/list-switch sampler, timer-list insertion
helper, timer-command drain, timer-list overflow switch, timer list/queue
runtime initializer, timer active-state query, and timer callback-context
getter, plus timer pended-callback ISR submission, plus static and dynamic
RTOS event-group creation, plus the RTOS event-group wait, clear-bits, and
clear-from-ISR operations, ISR-safe bit-snapshot getter, and task-context
set-bits operation, both timer callbacks, the shared wait-condition
predicate, set-from-ISR submission, priority-1 RTC clock initialization, and
RTC calendar/time setting and reading, the Apollo510 peripheral-power
descriptor lookup and complete source table, the cached Apollo510
trim-version getter, Apollo510 MCU HP/LP switching sequence, and public
MCU-mode selector, GPU-mode status getter, GPU-mode selector, MCU
memory-power configuration, ROM power-domain enable/disable, and shared-SRAM
power configuration, the private crypto power-down quiesce helper,
peripheral-power enable, disable-domain mask checking, and peripheral-power
disable, plus the peripheral enabled-state query and INFO1 cache-population
routine, the complete public low-power initializer, the private
buck/LDO override initializer, its dynamic override updater, and the public
miscellaneous power-control dispatcher, CPDLPSTATE configurator, and
CPDLPSTATE getter, plus the public temperature-update, system-PLL
enable/disable routines, and enabled-state query, plus the SPOT-manager
timer initializer, start routine, restart routine, and stop routine, plus the
complete 13-entry SPOT-manager public callback-dispatch layer for power-state,
TempCo, SIMOBUCK, timer-interrupt, TON, LP-to-HP, and low-power-autoswitch
callbacks, plus the complete SPOT-manager initializer, including its
Apollo510 revision/trim matrix, analog-rail repair, cached flags, and callback
table selection, plus the adjacent masked status-change and configurable
equal/not-equal status-wait helpers, plus the public Apollo510 forward
word-copy wrapper with its former private-ITCM dependency removed, plus the
private Apollo510 MCUCTRL device-information collector with source-owned SKU,
RAM, MRAM, JEDEC, and CoreSight decoding, plus the public seven-command
Apollo510 MCUCTRL oscillator-control dispatcher with reviewed register,
argument, clock-request, and clock-release ordering, plus its public
external-32-MHz-clock status getter with fresh register sampling, plus
the private Apollo510 MCUCTRL trim-version decoder with INFO1 status
propagation, chip-revision qualification, and packed feature-word output,
plus the public MCUCTRL information getter with nine fresh SKU reads and
direct source-owned trim/device dispatch, plus the first post-GPIO shared
  character-search primitive with byte-truncated search semantics and the
  adjacent unconditional 32-bit ASCII case-folding primitive, complete
  64-bit integer-formatting helper, decimal power-scaling helper, runtime
  byte-span emitter, zero-fill adapter, lookup-layout predicate, dual-layout
  byte-map lookup, property-group index, style initializer/reset, public
  lookup adapter, packed property-removal and property-set routines,
  transition-descriptor
  initializer, style default-value dispatcher, style-empty predicate,
  built-in/custom property-flag lookup,
  linked-list initializer, head/before/tail insertion, unlinking,
  callback-driven clearing, head/tail/link accessors, length traversal,
  empty predicate, clear wrapper, move-before routine, and previous/next
  pointer setters, plus RGB888 mixing, packed-alpha mixing, packed-color
  brightness, and two-layer packed-alpha composition, plus public theme
  resolution/application/color access, parent-first and inheritable-class
  theme traversal, bounded and no-op output callbacks, ASCII digit
  recognition, unsigned decimal parsing, mpaland reverse-output and
  integer prefix/sign/width formatting, and bounded 32-bit and 64-bit
  integer digit conversion using source-owned division support, plus
  source-owned fixed/exponential floating-format conversion and a bounded
  string-length veneer and scanner, the complete variadic formatter core
  including the recovered G2 pointer and recursive descriptor extensions,
  public `snprintf`/`vsnprintf` wrappers, public heap allocation/free
  veneers, the primary allocation/reallocation/free adapter trio, and the
  complete generic heap descriptor initialization/allocation/aligned-
  allocation/reallocation/free coordinator with source-owned locking and
  accounting, plus the source-built TLSF allocator behind every externally
  reached allocator entry, and
  LVGL asynchronous call, cancellation, and timer
  callback lifecycle, plus Apollo510 GPIO
  configuration/state/interrupt slices.
The dual-image EasyLogger helper increment additionally source-owns
`get_fmt_enabled`, its unsigned-argument and pointer-argument predicates,
and `elog_strcpy` in both Apollo images. Shared MIT source supplies the
algorithms; image-specific source seam providers preserve each logger object
and assertion policy while keeping official strings, hook globals,
`elog_output`, and wait wrappers as explicit binary dependencies.
Apollo main additionally source-owns the FreeRTOS V10.5.1
`xTaskGetTickCount` and `xTaskGetTickCountFromISR` algorithms through a
shared source provider for the recovered `xTickCount` word at `0x20074A34`,
plus the exact upstream `vTaskMissedYield` store to the recovered
`xYieldPending` word at `0x20074A44`, `uxTaskResetEventItemValue`, and
`pvTaskIncrementMutexHeldCount`, the nested scheduler-depth increment in
`vTaskSuspendAll`, and the overflow/tick snapshot in
`vTaskInternalSetTimeOutState`, the six-function scheduler cluster, the active
authenticated upstream LZ4 v1.10.0 decoder closure, and the current
`xTaskRemoveFromEventList`, `xQueueGiveFromISR`, and
`prvTaskCheckFreeStackSpace` closure, followed by the authenticated
FreeRTOS V10.5.1 `xTaskCheckForTimeOut` implementation.

It produces a 119,204-byte source overlay at
`[0x00794324,0x007B14C8)`. The pinned overlay has SHA-256
`4b3071e64d0e183efbb59788c94dca8ae01fba6d952aecbb9682893844171a79`
and records 609 effective compiled functions and 573 replacement patches. The
complete Apollo component is 3,642,600 bytes including its staging preamble,
or 3,642,568 installed bytes, with SHA-256
`eaa59756edb47e85be46959cb2242200f51bc4a3acaea1fc4365ee1f6a59e152`.
It accounts for 119,386 source-owned bytes (including 182 fixed-address
bytes), 83,074 generated patch-site bytes, 83,256 authenticated
replaced-stock bytes, and 3,440,108 opaque base bytes.
The bootloader now carries a 622-byte overlay and 149,222-byte provider with
SHA-256 values
`fc02cf66854adace4d213e08764e435e27c8c2bc7cc4f7caac6ff286f3adf813`
and
`b4a5b0f2028842a2d6fde9424fff05fac2db3bf0e26e7f01d16a990e67ed9052`.
The resulting 4,421,054-byte package has SHA-256
`4fb13f64e81b8a6ef9bdf784ac38d5fc08ed03e4d310601a48bf4b395c20ab37`.
The installed main end leaves 256,824 bytes below the conservative
`0x007F0000` ceiling and 314,168 bytes below the protected `0x007FE000`
boundary.
The reproducibility gate performs separate output-tree rebuilds. Builds from a
linked worktree normalize its actual `openCFW` root to the selected
toolchain profile's reviewed source root, keeping vendored TLSF diagnostics
that embed `__FILE__` artifact-stable against that profile's pins. This is an
explicit per-profile normalization and does not claim global path independence
across arbitrary users or source layouts. Older release notes below that refer
to an exact-root Linux build describe historical qualification before this
normalization. The missed-yield leaf itself is byte-identical under Apple
clang 21 and Homebrew clang 22.1.8.
Its exact upstream semantics, caller closure, placements, and profile pins are
recorded in
[`docs/research/freertos-missed-yield-source-boundary-audit.md`](docs/research/freertos-missed-yield-source-boundary-audit.md).

All nine externally reached stock TLSF entries are redirected atomically to
the source allocator: pool walking, block-size and pool-overhead queries,
create-with-pool, pool access, allocation, aligned allocation, free, and
reallocation. These redirects replace 710 stock bytes. The other 2,518 bytes
in the reviewed `0x004CFD18...0x004D09B3` TLSF closure remain explicitly
mapped compatibility bytes rather than active external allocator entries.
The production source is compiled and inspected as ARM ELF32. An independent,
import-free wasm32 ILP32 module executes the same allocator through a
deterministic 5,000-iteration allocation/reallocation/free proof; the
9,018-byte module has SHA-256
`198e6d5bae33d502605ac1696f764a4bd0cf1c7653433315c79afa862228c3eb`.
The native host lane exercises allocator semantics only and is not treated as
32-bit ABI evidence.

The shared file runtime at `0x00474550...0x00474E3B` is source-replaced as
eighteen complete stock functions. Open retains the 0x60-byte object, fixed
driver, `r`/`w`/`a`/`+` flag composition, allocation, mutex, backend, and
cleanup ordering. Close/read/write retain the shared mutex and backend ABIs,
element/byte conversion, result normalization, and all recovered write
diagnostics. Seek/tell retain origin validation, signed offset and position
results, mutex sequencing, and backend result normalization. Size preserves
successful lengths and the recovered `EBADF`, `EBUSY`, and `EIO` failure
mapping. Flush preserves the null/standard-stream no-op cases, mutex and
backend sequencing, and recovered `EBUSY`/`EIO` errno mapping. Remove
preserves the filesystem-ready no-op, null-path validation, serialized backend
call, already-absent success, and recovered errno mapping. The 220-byte
diagnostic/data pool before the cluster. Rename preserves the same
filesystem-ready gate, two-path validation, serialized backend call, and
failure mapping. Directory creation preserves its ignored mode argument and
distinct `EEXIST`, `ENOENT`, and general `EIO` backend mappings. Directory
open preserves the 0x240-byte object ABI, bounded path mirror, allocation and
cleanup ordering, and `ENOENT`/`ENOMEM`/`EBUSY`/`EIO` mappings. Directory read
preserves the global dirent ABI, end-of-directory result, bounded name copy,
and file/directory type translation; directory close preserves the recovered
ready-state no-op and post-backend free. The intervening 16-byte mode-literal
pool remains pinned official compatibility data. The adjacent synchronized
allocation, free, and reallocation wrappers preserve their separate mutex and
heap handles, backend ordering, null-result behavior, and timeout diagnostics.
The runtime initializer preserves creation and publication of both mutexes,
the success/failure return ABI, and all recovered logging gates. The following
120-byte literal pool remains isolated official compatibility data.

The adjacent Apollo510 cache-control functions at
`0x00474EB4...0x00475193` are source-replaced as five complete stock
functions. They retain cache-power gating, instruction-cache barriers and
invalidations, prefetch configuration, data-cache set/way maintenance, range
maintenance, low-byte clean selection, and the recovered zero/one status ABI.
The following 52-byte register-address literal pool remains pinned official
compatibility data.
The immediately following 104-byte application-wide memory comparator at
`0x004751C8` is source-replaced too. All 64 raw callers retain the original
ABI, including exact byte-difference returns and normalized minus-one/plus-one
results for aligned word mismatches.
The adjacent 86-byte Apollo510 `am_hal_ota_add` implementation at
`0x00475230` is also source-replaced. Its sole caller retains the stock MRAM
range checks, eight-image descriptor limit, pending-bit encoding, descriptor
programming order, status propagation, and successful OTA-pointer
registration. The following ten-byte state/register literal pool remains
pinned official compatibility data.
The adjacent 120-byte BLE message-transmit thread entry at `0x00475290` is
source-replaced too. The retained thread pointer at `0x00475E68` continues to
enter the original address, where the generated redirect preserves lifecycle
hook order, all-valid flag dispatch, zero/error diagnostics, and indefinite
retry behavior.
The following two intentional no-op lifecycle hooks and intervening 40-byte
BLE TX queue initializer through `0x00475333` are source-owned too. The queue
path preserves its 150-element, four-byte item contract, state word at
`0x2000402C`, null-attribute creation, and stock fatal allocation-failure
behavior.
The adjacent setup-stage adapters and thread creator/destructor through
`0x0047538B` are source-owned too. They preserve stage index 8, stock thread
entry and attributes pointers, handle publication at `0x20004028`, fatal
creation failure, conditional termination, and handle clearing.
The following queue drain, thread-flag router, and wait handler through
`0x00475523` are source-owned too. They preserve nonblocking queue polling,
commands 1/2/4/8 and source message freeing, both TX thread-flag bits and
their order, diagnostics, and the indefinite retained-backend wait.
The adjacent queue-clear routine through `0x0047564D` is source-owned too. It
preserves null-handle behavior, queue-depth reporting, zero-timeout freeing,
and its freed-count result.
The following 1,002-byte enqueue core through `0x00475A37` is source-owned
too. It preserves four message layouts, aligned allocation and source copying,
stream reset, half-capacity backpressure, queue submission/failure cleanup,
and thread wakeup across all eight callers.
The adjacent 110-byte direct protobuf-over-BLE wrapper through `0x00475AA5`
is source-owned too. It preserves its three callers, argument truncation,
enqueue result, OTA-active suppression, diagnostic gates, and return policy.
The following 110-byte protobuf-notification counterpart through
`0x00475B13` is source-owned as well. It preserves its two callers, subtype
one, forwarding behavior, and distinct diagnostic constants.
The following 262-byte guarded protobuf sender through `0x00475C19` is
source-owned too. It preserves all 76 callers, OTA-active zero return,
left-lens status-eight rejection, exact gated diagnostics, byte/length
truncation, accepted enqueue forwarding, and enqueue-result propagation.
The following 324-byte guarded protobuf-notification sender through
`0x00475D5D` is source-owned too. It preserves all 39 callers, OTA-active zero
return, left-lens and command-role status-eight rejection, exact diagnostics,
subtype-one forwarding, truncation, and enqueue-result propagation. Its
26-byte shared literal pool remains official data.
The adjacent 96-byte streaming-notification wrapper through `0x00475DD7` is
source-owned too. It preserves its two callers, OTA diagnostic/zero-return
path, subtype-one transport-one forwarding, 16-bit length truncation, and
enqueue result. An 8-byte queue-diagnostic pool remains official data.
The following 26-byte transport-three sender through `0x00475DF9` is
source-owned and deliberately bypasses the OTA gate while preserving its six
callers and four-register truncating ABI. The adjacent EFS send and notify
wrappers at `0x00475DFA...0x00475ED3` are source-owned too, preserving their
five and one callers, transport-two subtype selection, OTA diagnostics, and
distinct zero/status-eight returns. Their 10-byte intervening literal pool
and 236-byte shared pointer table remain separately mapped official data; the
following 34-byte variadic string scanner at `0x00475FC0...0x00475FE1` is
source-owned. It preserves all seven raw callers, AAPCS variadic forwarding,
retained scan-engine ABI, return value, and the read/unread/end-of-string
semantics of its formerly stock computed callback. The adjacent 6-byte
alignment/callback literal pool remains separately mapped official data.
The following littlefs directory check, format/mount recovery, initializer,
flash read/program/erase callbacks, and exact sync callback at
`0x00475FE8...0x004764DF` are source-owned too. They preserve the four
directory paths, recovery and boot-count sequencing, external-flash
`0x01400000 + block*0x1000 + offset` mapping, failure diagnostics, and all
four config-table callback pointers. Their 138-byte dependency pool remains
separately mapped official data. The following event-loop initializer,
blocking worker, queue-push path, timer scheduler, delayed insertion, and
delayed removal at `0x004764E0...0x00476BEF` are source-owned too. They
preserve the 15-by-8 queue contract, queue timeouts, CMSIS object attributes,
64-slot delayed table, critical/mutex sequencing, tick arithmetic, and timer
rescheduling. The two-byte worker alignment and 204-byte dependency pool
remain separately mapped official data. The adjacent connection-parameter
update scheduler at `0x00476CBC...0x00476DB7` is source-owned too, preserving
the three caller ABIs, ready/armed immediate-update path, callback
identity, and 2/4-second delayed rescheduling. The adjacent mode selectors at
`0x00476DB8...0x0047720B` are source-owned too, preserving their one- and
two-caller ABIs, diagnostic records, and 25- and 72-unit thresholds. The
adjacent coordinator at `0x0047720C...0x0047761B` and delayed callback at
`0x0047761C...0x0047773D` are source-owned too, preserving pending/retry
state, both selector paths, context/controller/role gates, exact command
packets, diagnostics, endpoint forwarding, and callback return registers.
Their 54-byte literal pool remains official compatibility data. The following
remote connection-parameter handler at `0x00477774...0x00477A69` is
source-owned too, preserving received state, all diagnostics, secondary-mode
selection, state publication, and the role-gated 60-second retry. Its
114-byte literal pool remains official compatibility data. The following
connection-update event state machine at `0x00477ADC...0x004780D7` is
source-owned too, preserving status handling, 25/72-unit mode thresholds,
state publication, and all five retry-delay families. Its four-byte pointer
literal remains official compatibility data. The following connection-global
initializer at `0x004780DC...0x004780F7` is source-owned too, preserving the
endpoint byte, caller-supplied connection/state pointers, and fixed defaults
table pointer. The following five connection-mode control helpers through
`0x0047826B` are source-owned too, preserving stream readiness, short/long
scheduling, retry holdoff, diagnostics, and remote reset. Their interleaved
literal pools remain official compatibility data. The following
connection-event dispatcher at `0x004782DC...0x004786B3` is source-owned too.
It preserves null/default handling and message classes `0x27`, `0x28`, `0x29`,
`0x40`, `0xA3`, `0xA4`, and `0xB9`, including identifier-to-state mapping,
profile-selected parameter tables, callback cancellation, source-owned
remote/event/scheduling paths, coordinator forwarding, and the recovered
structured/trace diagnostics. Its 240-byte dependency pool remains official
compatibility data. The following MRAM zero-region programmer at
`0x004787A4...0x0047885F` and protected update-flag setter at
`0x00478860...0x00478965` are source-owned too. They preserve cache
invalidation, zero-fill and word-count behavior, template-backed idempotent
flag updates, exact PRIMASK restoration, and the recovered diagnostics. Their
74-byte literal pool remains official compatibility data. The following
protected-MRAM record diagnostic dump at `0x004789B0...0x004793E9` is
source-owned too, preserving byte-index selection, all record scalar/label
fields, four hex-dump ranges, both sparse halfword tables, and exact log/trace
gates. Its 46-byte front-literal pool remains official compatibility data.
The following two-pass MRAM record synchronizer at
`0x00479418...0x0047956B` is source-owned too. It preserves the ten-record
filter, both comparison passes, record-table pointer reload, flag mutation,
timestamped publication order, final-record marker, batch commit,
diagnostics, and the stock entry's unusual `r0`-through-`r3` preservation.
The following 112-byte shared protected-record diagnostic pool remains
official compatibility data. The following protected-MRAM record-list loader
at `0x004795DC...0x00479981` is source-owned too. It preserves ten-slot
iteration, 0x100-to-0xC8 stride conversion, cache invalidation, zero/erased
early termination, exact-active validation, four-key mask reconstruction and
repair, persistence ordering, invalid-slot clearing, IRK dumps, loaded-count
tracking, and all recovered diagnostics. Its byte copies and clears are now
source loops rather than retained memory-runtime calls. The following 38-byte
diagnostic continuation pool remains official compatibility data. The next
protected-MRAM single-record programmer at
`0x004799A8...0x00479AB3` is source-owned too. It preserves byte-index
truncation, whole-cache invalidation, two ordered 128-byte MRAM program
transactions, the thread-mode-only yield between halves, both returned
statuses, and exact success/error diagnostics. Its following 192-byte literal
and dependency pool remains official compatibility data. The following
protected-MRAM application record-database updater at
`0x00479B74...0x0047A461` is source-owned too. It preserves existing-record
and empty-slot selection, full-table replacement priorities, strict
timestamp ordering, type preference, per-slot diagnostic dumps, source-owned
single-record programming, cache-coherent identifier verification, all
recovered diagnostics, and the stock success return after a verification
mismatch. Its following 26-byte literal pool remains official compatibility
data. The following 32-byte record-deactivation adapter at
`0x0047A47C...0x0047A49B` is source-owned too. It clears both activity flags,
persists through the source database updater, forwards the same record to the
retained NVM verifier, and returns that verifier's status. The following
282-byte record-activation adapter at `0x0047A49C...0x0047A5B5` is
source-owned too. It preserves byte-mask logging and truncation, ordered
activity-flag mutation, the monotonic record timestamp, source database
persistence, retained verification, exact-success diagnostics, and the
original full-width mask return. Its following 10-byte padding/literal pool
remains official compatibility data. The following 16-byte conditional
deactivation adapter at `0x0047A5C0...0x0047A5CF` is source-owned too. It
forwards the record to the source deactivation path only when confirmation
byte `0x30` is zero. The following five record-query helpers through
`0x0047A6FF` are source-owned too. They preserve exact active membership,
untyped-record presence, null and arbitrary-pointer traversal, low-byte type
counting, and strict-minimum oldest-record selection. Their three literal
pools remain official compatibility data. The following 314-byte record
allocator at `0x0047A71C...0x0047A855` is source-owned too. It preserves the
per-type threshold eviction, oldest-record release/deactivation order,
first-free scan, zero/init sequence, low-byte fields, timestamp, and full
table diagnostics. Its six-byte following gap remains official compatibility
data. The following 54-byte record initialization wrapper at
`0x0047A85C...0x0047A891` is source-owned too. It preserves cache
invalidation, record-list loading, synchronization, and all ten record
diagnostic dumps. Its following 50-byte literal pool remains official
compatibility data. The following 650-byte Cordio
`AppDbResolveAndConnectByAddr` routine at
`0x0047A8C4...0x0047AB4D` is source-owned too. It preserves null rejection,
the exact resolvable-private-address gate, first-valid-IRK submission,
low-byte owner mapping, active/confirmed record filtering, six-byte address
matching, and all success/failure diagnostics. Its following 30-byte
diagnostic-pointer pool remains official compatibility data. The following
382-byte Cordio `AppDbHandleResolvedAddr` callback at
`0x0047AB6C...0x0047ACE9` is source-owned too. It preserves low-16-bit record
index handling, allocated/confirmed validation before address use, resolved
address-byte diagnostics, and the LTK-valid return contract. Its following
14-byte diagnostic-pointer pool remains official compatibility data. The
following 114-byte Cordio `AppDbDeleteAllRecords` adapter at
`0x0047ACF8...0x0047AD69` is source-owned too. It preserves the start
diagnostic, clears only the six-byte peer address and two validity bytes in
each of ten records, then reaches the source-owned protected-MRAM zero-region
programmer directly. Its following 10-byte pointer pool remains official
compatibility data. The following 82-byte Cordio address lookup at
`0x0047AD74...0x0047ADC5` is source-owned too. It preserves low-byte owner
normalization, activity/owner/address filtering, first-match selection, and
monotonic timestamp refresh. Its following 14-byte compatibility pointer pool
remains official data. The following 82-byte Cordio LTK-request lookup at
`0x0047ADD4...0x0047AE25` is source-owned too. It preserves low-16-bit
diversifier matching, the exact eight-byte random-number comparison,
first-match selection, and the same timestamp refresh. Its following 82-byte
shared pointer pool remains official compatibility data. The following
72-byte Cordio key accessor at `0x0047AE78...0x0047AEBF` is source-owned too.
It preserves all four key classes, valid-mask gating, LTK security-level
writes, null results for unsupported classes, and byte-truncated dispatch.
The adjacent eight-byte peer-address accessor and 12-byte peer-address-type
accessor through `0x0047AED3` are source-owned as well, including their null
contracts. The following 1,242-byte `AppDbSetKey`-style key writer through
`0x0047B3AD` is source-owned too, preserving local/peer LTK, IRK, and CSRK
layouts, mask updates, diagnostics, sign-counter reset, and exact-one
persistence. The following 12 Cordio application-database record-metadata
functions through `0x0047B4D3` are source-owned too: peer and device database
hash access, cache-by-hash and discovery state, CCC table writes, client
supported-features state, handle-list persistence, sign counters, and peer
address-resolution state. Their three intervening literal/alignment pools
remain official compatibility data. The following 148-byte Cordio
`AppDbReloadResolvingList` wrapper is source-owned too, preserving its two
diagnostics, retained reload request, and direct call to the source-owned MRAM
synchronizer. Its following 52-byte diagnostic-pointer pool remains official
compatibility data. The following 320-byte
`AppDbClearRecordByMacAddr` wrapper is source-owned too, preserving its
owner-byte truncation, null/miss/success diagnostics, source-owned record
lookup and deactivation, and retained record release. Its following 84-byte
pointer pool remains official compatibility data. The following 1,224-byte
`AppDbVerifyMramWrite` verifier is source-owned too, preserving whole-cache
invalidation, first protected-record matching, valid/in-use/key-mask checks,
selected local-LTK/IRK/CSRK comparisons, diagnostics, and mismatch hex dumps.
Its following 56-byte pointer pool remains official compatibility data. The
following 1,082-byte `AppDbShowAllRecordsStatus` reporter is source-owned too,
preserving its cache invalidation, both inactive classifications, active
record metadata and address order, strict oldest/newest timestamp selection,
and diagnostics. Its following 26-byte pointer pool remains official
compatibility data. The following 198-byte
`AppDbUpdateRecordTimestamp` wrapper is source-owned too, preserving its null
guard, overflow renumbering call, counter increment and record write,
diagnostics, source-owned persistence, and source-owned verification. Its
following 26-byte pointer pool remains official compatibility data. The
following 274-byte `AppDbResetRecordTimestamps` routine is source-owned too,
preserving its start/per-record/end diagnostics, ten-slot scan, allocation
and activity gates, slot-ordered counter reset and timestamp assignment, and
source-owned persistence. Its following 70-byte pointer pool remains official
compatibility data. The following 584-byte `AppDbShowNvmStatus` routine is
source-owned too, preserving whole-cache clean/invalidation, the ten-slot
protected-MRAM scan, exact valid/in-use/nonempty filtering, slot/key/address
reporting, record counts, geometry, and diagnostics. Its following 100-byte
pointer pool remains official compatibility data. The following 826-byte
`AppDbHandlePairingFailure` routine is source-owned too, preserving
connection/status truncation, NVM reporting before lookup, record validity
and key-mask filtering, all four named SMP failure classes, unknown-reason
handling, retained record clearing, direct invalid-record flag clearing, and
diagnostics. After 42 bytes of retained alignment and diagnostic pointer data,
the following 460-byte `AppDbClearRecordByConnId` routine is source-owned too,
preserving handle truncation and lookup, record qualification, direct invalid
flag clearing, source-owned MAC-address clearing and resolving-list reload,
and exact outcome diagnostics. Its following four-byte dependency pointer
remains official compatibility data. The following 34-byte record diagnostic
iterator is source-owned too, preserving the single record-table-holder read,
all ten 200-byte slots in order, source-owned diagnostic-dump calls, and no
record mutation. Its following 262-byte alignment/table/pointer pool remains
official compatibility data. The following 36-byte EFS non-reflected CRC-32C
updater and 44-byte protected-MRAM byte-program wrapper are source-owned too,
preserving the Castagnoli algorithm without the old table dependency,
byte-to-word rounding, interrupt masking/restoration, program key/arguments,
and ignored program result. Their following eight-byte literal pair remains
official compatibility data. The following 66-byte ARM EABI signed
division/modulo front end and 560-byte unsigned core are source-owned too,
including stock divide-by-zero behavior, signed quotient/remainder rules, and
the four-register result ABI. Their two-byte alignment pad remains official
compatibility data. The following three eight-byte lens/status packet
reporters are source-owned too, including their template bytes, two lens-side
samples, opposite-side mapping, state-bit encodings, and command `0x103`
send ABI. The registered command-`0x103` dispatcher that follows is now
isolated as a single 2,232-byte function-specific compatibility blob at
`0x0047CF60...0x0047D817`. Its adjacent lens-status publisher, template-4
reporter, and five state accessors through `0x0047D8FB` are source-owned.
The shared 200-byte literal pool remains compatibility data. The following
availability wrapper and selector-dependent state query through `0x0047D9F9`
are source-owned, and their two-byte alignment pad is retained. The following
SARC state-header checksum, validator, initializer, bounded variadic report
appender, payload finalizer, and crash-file persistence routine through
`0x0047DC21` are source-owned too. Its following 82-byte retired compatibility
pool remains separately mapped data. The following 64-byte wrap-extending
monotonic-seconds helper through `0x0047DCB3` is source-owned too. It preserves
interrupt-state restoration, the 32-bit tick-wrap accumulator, and division
of the resulting 64-bit millisecond count by 1,000. The following bounded
wall-clock seconds helper and shared interrupt-disable primitive through
`0x0047DCEB` are source-owned too. They preserve the conditional wall-clock
query, 2024-through-2099 validity window, exact output flag, saved `PRIMASK`,
and interrupt masking. The following reset-status word helper and firmware-
version encoder through `0x0047DD61` are source-owned too. They preserve the
16-byte reset-status staging shape and signed halfword result while moving the
`2.2.6.10` identity and three-component encoding algorithm into source. The
following EasyLogger tracepoint deferral dispatcher, one-shot timer callback,
begin helper, and bounded capture-retry worker through `0x0047DDFD` are
source-owned too. They preserve the fixed 2,000/5,000-tick rearm periods,
event-bit fallback, signed retry counter, capture-before-limit ordering, and
ten-retry ceiling. The following reflected CRC-32, tracepoint path
formatter/parser, positive
file-size query, directory extrema scan, 16-byte `TPS1` state writer/loader,
and storage initializer through `0x0047E069` are source-owned too. They
preserve the exact `/log/tp` filenames, standard 12-byte CRC window,
minimum-next-index normalization, active-file size window, and initialization
ordering. The following active-file close/callback, oldest-file pruning,
new-file header creation, append reopen, bounded write/rotation, commit, and
flush functions through `0x0047E231` are source-owned too. The three
intervening alignment/mode/prefix data islands remain explicitly mapped
compatibility bytes. The following idempotent tracepoint timer bootstrap
through `0x0047E271` is source-owned too, preserving the one-shot
`tracepoint_defer` timer ABI, fixed 2,000-tick period, handle publication,
fail-stop path, retained setup call, and initial deferral dispatch. Its
94-byte literal/data pool remains mapped compatibility data. The following
protobuf onboarding command/control-state update through `0x0047E31F` is
source-owned too, preserving the pending-state clear, command truncation,
mutex-protected configuration update, and command acknowledgement policy.
The following gated protobuf wear-status notifier through `0x0047E3E5` is
source-owned too, preserving its 12-byte event template, byte-truncated
status, notification ABI, and success/failure diagnostic policy. The following
deferred onboarding-flag persistence worker through `0x0047E46F` is
source-owned too, preserving exact pending-value gating, pre-save diagnostics,
success-only clearing, and failure retention. The following onboarding-flag
change detector/updater through `0x0047E4A5` is source-owned too, preserving
low-byte comparison, null-provider handling, deferred-persistence scheduling,
and event-bit signaling. The following peer flag notification through
`0x0047E51B` is source-owned too, preserving the two-byte RPC payload,
transport ABI, and diagnostics. The following peer flag reply through
`0x0047E58D` is source-owned too, preserving its distinct two-byte RPC
payload, transport ABI, and diagnostics. The following peer onboarding-process
synchronization through `0x0047E609` is source-owned too, preserving its
three-byte RPC payload, volatile state refresh, transport ABI, and diagnostics.
Its 106-byte state/diagnostic literal table remains compatibility data. The
following onboarding runtime initializer through `0x0047E6DB` is source-owned
too, preserving core initialization, the prerequisite gate, exact timer-service
thread arguments and publication, success return, and fail-stop behavior. The
following dynamic RTOS timer-object creator through `0x0047E711` is
source-owned too, preserving its 44-byte allocation, ownership-byte clear,
shared initializer ABI, null path, and returned object identity. The paired
static-control-block creator through `0x0047E759` is source-owned too,
preserving the 44-byte contract check, required caller-owned object,
static-ownership mark, shared initializer ABI, returned identity, and fail-stop
policy. Their shared initializer through `0x0047E7AF` is source-owned too,
preserving zero-period fail-stop, runtime initialization before mutation,
exact 32-bit object fields, and periodic flag merging. The following RTOS
timer command-submission path through `0x0047E811` is source-owned too,
preserving null-timer fail-stop, null-queue early return, exact three-word
messages, signed task/ISR routing, scheduler-dependent wait handling,
higher-priority-task-woken forwarding, and queue-send result propagation.
The following auto-reload catch-up loop through `0x0047E839` is source-owned
too, preserving unsigned deadline arithmetic, active-list insertion,
fresh-period reads, timer callback ordering, and repeated expiry processing.
The following expired-timer processor through `0x0047E877` is source-owned
too, preserving active-list-head resolution, intrusive-list removal,
periodic/one-shot status handling, direct source reload, and final callback
ordering. The following non-returning timer-service task loop through
`0x0047E88B` is source-owned too, preserving active-list query,
wait/expiry processing, command draining, and exact iteration order. The
following timer wait-or-expire processor through `0x0047E8F1` is source-owned
too, preserving scheduler suspension/resume, list-switch handling, unsigned
deadline comparison, overflow-list policy, queue blocking, and conditional
yield. The following active-list query through `0x0047E915` is source-owned
too, preserving normalized empty-list output, nonempty head-expiry lookup,
and the current-list pointer at `0x20074AA8`. The following tick/list-switch
sampler through `0x0047E93B` is source-owned too, preserving a single
current-tick sample, unsigned wrap detection against `0x20074AB8`,
source-wait integration, active/overflow-list switching, normalized switch
output, and unconditional last-tick publication. The following timer-list
insertion helper through `0x0047E979` is source-owned too, preserving exact list-item
field publication, unsigned wrap/elapsed classification, active/overflow-list
selection, and normalized expired return. The following timer-command drain
through `0x0047EA8F` is source-owned too, preserving the exact 16-byte queue
message ABI, pended callbacks, active-list removal, command-ID dispatch,
activation/deactivation, period changes, deletion, callback ordering, and
fresh volatile reads. The following timer-list overflow switch through
`0x0047EAB7` is source-owned too, draining every remaining current-list timer
at tick `0xFFFFFFFF` before swapping the current and overflow list pointers.
The following timer list/queue runtime initializer through `0x0047EAF5` is
source-owned too, preserving the critical section, one-time guard, two list
initializations, exact 50-by-16-byte static queue ABI, list-pointer
publication, and retry-on-failed-creation behavior. The following timer
active-state query through `0x0047EB25` is source-owned too, preserving the
null fail-stop, critical-section-protected status-byte read, active bit, and
normalized boolean result. The following timer callback-context getter through
`0x0047EB49` is source-owned too, preserving the null fail-stop,
critical-section-protected object-offset-`0x1C` read, and unchanged pointer
return. The following pended-callback ISR submission through `0x0047EB6B`
is source-owned too, preserving the exact four-word timer-daemon message,
queue-handle read, wake-pointer forwarding, ISR queue-send ABI, and unchanged
result. The reviewed 40-byte timer runtime literal pool at
`0x0047EB6C...0x0047EB93` remains compatibility data. The following static
and dynamic event-group constructors through `0x0047EBF7` are source-owned,
preserving the 32-byte object ABI, event-bit word, wait-list initialization,
ownership byte, allocation/null policy, and exact returned identity. The
following wait operation through `0x0047ED0F` is source-owned too, preserving
the five-argument ABI, validation, immediate and timeout paths, any/all
matching, clear-on-exit, control bits, scheduler sequencing, yield, critical
reread, and return masking. The following clear-bits operation through
`0x0047ED51` is source-owned too, preserving group/control-mask validation,
the critical section, distinct return/update reads, zero-mask behavior, and
the unchanged pre-clear snapshot return. The following clear-from-ISR
submission wrapper through `0x0047ED63` is source-owned too, preserving the
source callback, full group/mask forwarding, null wake pointer, direct
source callback and pended-submission dependencies, and unchanged result. The following
ISR-safe bit-snapshot getter through `0x0047ED75` is source-owned too,
preserving the BASEPRI save/raise, single volatile event-bit read, exact mask
restore, and unchanged 32-bit snapshot. The following task-context set-bits
operation through `0x0047EE1D` is source-owned too, preserving scheduler
suspension, any/all waiter matching, clear-on-exit accumulation, cached-next
list traversal, unblock snapshots, resume ordering, and the final event-bit
return. The following set-bits timer callback through `0x0047EE25` is
source-owned too and tail-calls the source set-bits implementation directly.
The two bytes at `0x0047EE26...0x0047EE27` remain explicit alignment; the
following clear-bits timer callback through `0x0047EE2F` is source-owned too
and tail-calls the source clear-bits implementation directly. The following
wait-condition predicate through `0x0047EE49` is source-owned too; both calls
inside the source wait routine resolve directly to it, and it preserves the
normalized any/all truth table for every 32-bit input. The following
set-bits-from-ISR wrapper through `0x0047EE59` is source-owned too, preserving
the source callback pointer, full group/mask/wake-pointer forwarding, direct
source pended-submission dependency, deliberately absent validation, and
unchanged result. The two bytes at `0x0047EE5A...0x0047EE5B` remain explicit
alignment, and the callback Thumb literal at
`0x0047EE5C...0x0047EE5F` remains separately mapped compatibility data. The
following priority-1 RTC initializer through `0x0047EE77` is source-owned.
It selects the XTAL clock through both reviewed Ambiq paths, enables the RTC
oscillator, preserves every unrelated register bit, and returns zero. Its
sole initializer-table entry and priority remain unchanged. The following RTC
calendar/time setter through `0x0047EEF9` is source-owned too. It preserves
the 2000-based input ABI, AmbiqSuite 5.1.0 weekday and validation behavior,
BCD packing, ordered `RTCCTL`/`CTRLOW`/`CTRUP` writes, zero/success and
one/failure results, and failure-only structured/trace diagnostics. The two
alignment bytes and five diagnostic pointers at
`0x0047EEFA...0x0047EF0F` remain separately mapped compatibility data. The
following RTC calendar/time getter wrapper through `0x0047EF17` is
source-owned too. Its IRQ-protected RTC-edge polling workaround, timer-14
configuration, ordered `CTRLOW`/`CTRUP` reads, read-error short circuit, and
BCD field decoding are pinned. The following private Apollo510 peripheral-
power descriptor lookup through `0x0047EF37` is source-owned too. It
preserves Ambiq status six for invalid arguments, the exact four-word ABI,
all four callers, and all 34 byte-identical source-owned records. The retired
stock table is separately mapped at `0x006BECB0...0x006BEECF`. The following
60-byte Ambiq `TrimVersionGet` helper through `0x0047EF73` is source-owned
too. It preserves one-time INFO1 word `0x244` loading, cache normalization,
null-output status six, and its sole low-power-initialization caller. The
following 300-byte private MCU HP/LP switching sequence through `0x0047F09F`
is source-owned too. It preserves SPOT preflight/rollback, HFRC2 forcing,
readiness and ACK polling, cache update, interrupt restoration, and the sole
public selector caller. The following 104-byte public MCU-mode selector
through `0x0047F107` is source-owned too. It preserves low-byte mode
validation, SIMOBUCK gating, already-selected short circuit, source switching,
status propagation, hardware-state verification, and its sole application
caller. The following 20-byte public GPU-mode status getter through
`0x0047F11B` is source-owned too. It preserves null rejection, the
`0x20074F60` cached-byte ABI, and its sole GPU-initialization caller. The
following 232-byte public GPU-mode selector through `0x0047F203` is
source-owned too. It preserves low-byte validation, HP SIMOBUCK gating,
graphics-in-use rejection, cached current/previous-mode behavior, GPU voltage
and performance-frequency sequencing, SPOT TON coordination, both settle
delays, exact PRIMASK restoration, and all three callers. The following
450-byte public MCU memory-power configuration routine through `0x0047F3C5`
is source-owned too. It preserves the short-enum configuration ABI, ROM/TCM/
NVM target computation, disable/SPOT/enable sequencing, bounded status waits,
AXI-clock forcing quirks, post-transition verification, retention updates,
and its sole low-power initialization caller. The following 82-byte ROM
power-domain enable routine through `0x0047F417` is source-owned too. It
preserves the AUTO-mode gate, SPOT desired-status publication, ignored SPOT
result, enable-bit update, exact 10,000-read poll bound, timeout status, and
its sole ROM-access caller. The paired ROM disable, shared-SRAM configuration,
crypto quiesce, peripheral enable, disable-domain mask check, peripheral
disable, and enabled-state query are source-owned through `0x0047F941`. After
an 18-byte retained island, the private INFO1 cache-population routine through
`0x0047FAB3` is source-owned and preserves all nine ordered reads and partial
commit behavior. Its following 52-byte constant island remains opaque. The
public low-power initializer at `0x0047FAE8...0x0047FE11` is source-owned too,
preserving reset/debug errata, CPDLP/WIC and OTP policy, INFO1 fallback,
memory/clock and factory-trim setup, retention, SPOT/SIMOBUCK sequencing,
exact interrupt restoration, and revision-gated MRAM policy. The following
private buck/LDO override initializer at `0x0047FE12...0x0047FE67` is
source-owned too. It preserves all ten ordered volatile read/modify/write
operations against `MCUCTRL->VRCTRL`, including the SIMOBUCK, CoreLDO, and
MemLDO override ordering while retaining unrelated register bits. Its
four-byte literal at `0x0047FE68...0x0047FE6B` remains opaque. The following
dynamic override updater at `0x0047FE6C...0x0047FE93` is source-owned too. It
preserves three fresh volatile reads, low-bit input semantics, unrelated
register bits, and the SIMOBUCK/CoreLDO/MemLDO write order. Its three-word
literal island at `0x0047FE94...0x0047FE9F` remains opaque. The following
public miscellaneous power-control dispatcher at
`0x0047FEA0...0x0047FFB9` is source-owned too. It preserves low-byte command
selection, SIMOBUCK initialization and already-active handling, conditional
crypto quiesce/disable, deep-sleep crystal power-down, and the ordered
debug/device/audio shutdown path with both bounded status checks and SPOT
updates. Its ten-byte data island at `0x0047FFBA...0x0047FFC3` remains
opaque. The following public CPDLPSTATE configurator at
`0x0047FFC4...0x00480001` is source-owned too. It preserves the packed
three-short-enum ABI, rejects RLP-off while either cache is enabled, and
writes the exact three-field CPDLP register value otherwise. Its two-byte
alignment pad at `0x00480002...0x00480003` and the four-byte compatibility
pointer at `0x00480004...0x00480007` remain opaque. The following public
CPDLPSTATE getter at `0x00480008...0x00480027` is source-owned too. It reads
the state register once and writes the RLP, ELP, and CLP two-bit fields to
three consecutive short-enum bytes. The adjacent public temperature-update
routine at `0x00480028...0x00480057` is source-owned too. It forwards the
hard-float temperature argument to the retained SPOT manager, copies both
returned thresholds on success, and normalizes every failure to status one
with two positive-zero outputs. The next opaque executable boundary begins
at `0x00480058`.

The current component replaces the contiguous 2,622-byte UI control layer at
`0x0044228A...0x00442CC7`, covering targeted event and common-data dispatch,
broadcast close, registry initialization, mode lookup, display-mode
switching, and startup application-ID selection. It preserves the shared
literal pool at `0x00442CC8...0x00442D63`, source-replaces the adjacent
34-byte onboarding-state gate at `0x00442D64`, then source-replaces the
complete 1,780-byte packed input-event handler at `0x00442D86`. The handler
now calls the ring long-press and release source functions directly, so the
two former in-body branch patches are no longer needed. After retaining that
handler's 870-byte literal pool, it replaces the complete 2,558-byte registered
main display thread at `0x004437E0`, the 18-byte display preparation helper at
`0x00444694`, the 74-byte input preparation helper at `0x004446B4`, and the
complete 300-byte display-subsystem initializer at `0x00444720`. The source
display preparation helper binds the source-replaced 12-byte dynamic callback
at `0x00444684`; the initializer calls both source helpers and passes the
source thread entry directly to the retained RTOS registration ABI. The stock
`0x004437E1` thread and `0x00444685` callback Thumb literals remain preserved
but inactive, and the original addresses still enter generated redirects.
The sole setter for the callback's `0x200742F0` dynamic-handler word is also
source-replaced at `0x00472C7C`, together with the installed handler at
`0x005415C2`. That handler now links directly to the source-replaced shared
string-length primitive at `0x0044A43C` and asynchronous selector sink at
`0x0055E7FA`. The sink links directly to the source-replaced submit dispatcher
at `0x0058E3F8`; all four of its operation backends are source-owned:
operation zero at `0x0058E454`, operation one at `0x0058E49E`, the shared
start/operation-two helper at `0x0058E4E8`, and operation three at
`0x0058E50A`. Operation one links directly to source operation three. Operation
three links directly to the source-owned event-side begin at `0x0058DF5C` and
event service at `0x0058E618`; operation one uses that same source event
service. All three polling/cleanup consumers call the exact source-owned
in-place delay entry. The sink's 10-microsecond wrapper at `0x00491102` and
the adjacent millisecond wrapper at `0x004910F4` are exact source copies too,
preserving 66 and 53 direct callers respectively.
The adjacent 12-byte formatter adapter at `0x004910E8` is exact source as
well: it forwards argument pointer `+0x1C` and 16-bit length `+0x12` to the
source-owned shared buffer writer at `0x00490DB6`. That writer emits the
unsigned length prefix through the source-owned entry `0x00490CE0`, stops on
prefix failure, and otherwise appends the original span through `0x00490616`.
The prefix entry directly emits values below 128 and otherwise calls the
source-owned full unsigned LEB128 encoder at `0x00490C84`; the shared
append primitive at `0x00490616` is source-owned as well, including capacity,
sticky-error, callback, and committed-length behavior.
The adjacent signed 64-bit adapter at `0x00490D08` is source-owned too and
performs standard zigzag mapping before using that same prefix path.
The following four-/eight-byte wrappers, protobuf-style field-key encoder, and
descriptor wire-type adapter through `0x00490DB5` are source-owned as one
continuous formatting slice.
The shared boolean reader at `0x00490678` and scalar adapters at
`0x00490E90...0x00490FA1` are source-owned too, including all reviewed
zero/sign-extension, zigzag, fixed-width, and invalid-size behavior.
The two-pass submessage writer at `0x00490DDC`, bytes adapter at `0x00490FA2`,
bounded or pointer-backed string adapter at `0x00490FE4`, and submessage-field
adapter at `0x0049104C` are source-owned too. They preserve size-first
encoding, callback/state propagation, static-capacity checks, termination
checks, extension-callback dispatch, and sticky error behavior.
The generic message encoder at `0x00490C32` is source-owned too. It preserves
all 125 direct branch sites and retains reviewed stock ABI entries only for
iterator begin/next. Its regular-field entry at `0x00490B1E` is source-owned
too, preserving required/optional/oneof omission policy and
indirect/repeated/value dispatch behavior.
The value dispatcher at `0x00490A46` is source-owned too and links directly
to all source-owned field-key and value adapters.
The indirect callback helper at `0x00490AEA` is source-owned too, including
callback-result normalization and sticky callback-error propagation.
The recursive protobuf-style default checker at `0x0049087A` is source-owned
too, covering scalar zero scans, bytes/string/span defaults, indirect
callback policy, and nested submessage iteration. The regular encoder links
to it directly.
The repeated-field encoder at `0x00490690` is source-owned too, covering
packed sizing/encoding, count limits, size-only output, unpacked values, and
pointer-backed null bytes/string entries. The regular encoder links to it
directly as well.
The default extension wrapper at `0x00490BC8` and linked extension dispatcher
at `0x00490BF8` are source-owned too, preserving iterator initialization,
custom-callback selection, low-byte result semantics, and sticky invalid-
extension error behavior.
The lower-level operation-zero/two begin helper at `0x0058DEF2` is
source-owned and receives both the handle and descriptor. The 228-byte service
at `0x0058E534` is source-owned too, including progress publication and
completion/error callbacks. Its direct
transport at `0x0058E31E` is source-owned as well; it writes bytes to the
instance-selected FIFO until hardware reports full and returns the accepted
count. The ring-drain helper at `0x0058E3A0` is source-owned too and links
directly to that writer. The generic ring read/write helpers are source-owned.
The event-side begin publishes its receive descriptor under one PRIMASK
critical section; the event service fills and consumes the receive ring or
reads the FIFO directly, updates progress, and dispatches completion/error
callbacks. The IRQ-side owner at `0x0058E860` is source-owned too: it validates
the masked handle signature, routes normal interrupt status to the source
event/operation services, publishes special-transfer progress from the
instance FIFO position register, dispatches the retained special-status
helpers and completion callback, and clears the special-mode latch. Its four
lower helpers at `0x0058DD30`, `0x0058DD5C`, `0x0058DD8A`, and `0x0058DFEE`
are source-owned too, covering MMIO teardown, prioritized error mapping, FIFO
cleanup, delay policy, and control-bit restoration. Their event-abort
primitive and the exact 92-byte duration-delay span at `0x004807A0` are
source-owned as well. The delay's six-byte Ambiq cycle loop is source-generated
too. The builder proves reset's scatter-load record at `0x0075D3E0` maps the
22-byte compressed stream at `0x0079430E` to ITCM `0x00000040`, then copies
the exact source-assembled `SUBS`/`BNE`/`BX` literal bytes into load-image
storage `0x00794310...0x00794315`. The scatter loader, table, stream header,
and neighboring compressed ITCM functions remain version-pinned opaque ABIs.
It also replaces both eight-byte stock lens-side accessors at
`0x0045A568` and `0x0045A570`, the complete 344-byte lens-side initializer at
`0x0045A578`, the 22-byte GPIO interrupt-index helper at `0x00480ED8`, the
30-byte GPIO pin-configuration reader at `0x00480EEE`, the complete 126-byte
GPIO pin-configuration writer at `0x00480F0C`, the complete 76-byte GPIO state
reader at `0x00480F8A`, all 218 bytes of the GPIO state writer at `0x00480FD6`,
all 582 bytes of GPIO interrupt control at `0x004810B0`, all 370 bytes of
interrupt status at `0x004812F6`, all 268 bytes of interrupt clear at
`0x00481468`, the 126-byte IRQ-specific status helper at `0x00481574`, the
58-byte IRQ-specific clear helper at `0x004815F2`, the 154-byte handler
registration function at `0x0048162C`, the 116-byte handler service function
at `0x004816C6`, the EvenHub mode-2 decompression adapter and complete
byte-run decoder at `0x004E0C0C...0x004E0C9F`, five adjacent lifecycle
accessors at `0x004E0CA0...0x004E0CCD`, the 108-byte container lookup at
`0x004E0CCE`, all 1,112 bytes of the EvenHub page-event callback at
`0x004E0D3A`, all 628 bytes of the common-data callback at `0x004E1192`, the
60-byte EvenHub IMU policy at `0x004E1406`, all 1,222 bytes of the registered
UI-event handler at `0x004E1490`, and the 30-byte LZ4 safe block-decoder
wrapper at `0x0054F338`, with non-linking entry branches and NOP fill. The
service-`0xE0` registry pointers at `0x006A4524` and `0x006A4528` keep their
original entry ABIs. Expected bytes for every complete patched span are
checked before any write.

The common mini-linker accepts multiple C modules, resolves internal Thumb
calls/jumps and `-fropi` PC-relative read-only data, and rejects writable
sections or any other relocation. This permits coherent source modules to grow
without unreviewed runtime relocation machinery.

The source handler functions reuse the reviewed UI-module registry/count at
`0x20066230` and `0x200744D4` plus GPIO tables at `0x20068228` and
`0x20068928`; no writable data is added to the overlay.

The ring portion of this overlay is derived from the GPL-3.0-only
[`jimrandomh/g2flash`](https://github.com/jimrandomh/g2flash) implementation;
the GPIO functions are adapted from Ambiq's BSD-3-Clause AmbiqSuite SDK 5.1.0
source. The active LZ4 decoder is now the authenticated BSD-2-Clause upstream
LZ4 v1.10.0 `LZ4_decompress_safe` source selected by openCFW. This is a
maintained replacement-source choice, not a claim that the stripped official
image contains that exact point release: the stock decoder remains compatible
with the reviewed v1.9.4/v1.10.0 family evidence. Selected source revisions,
license texts, evidence bounds, and local boundaries are documented in the
component `NOTICE.md`.

The latest increment production-routes the clean-room ALS-scale KVDB closure
(`kvdb_als_scale.c`): the factory-record default initializer, the
`_kvdbUpdataAlsScale` migration callback, and the `SVC_KvdbWriteAlsScale`
whole-record writer replace the 338 stock body bytes at
`[0x004AECA4,0x004AEDF6)` through three entry redirects, bound to the retained
CRC-16 provider at `0x0049ACD4` and the blob read/write adapters at
`0x004D956C`/`0x004D957E`, with the 50-byte literal tail and the fixed SRAM
record at `0x200037BC` untouched. Under the reviewed Apple Clang 21 profile
the overlay/component/package sizes are `143227/3666623/4445117` with SHA-256
`200b0b3385c26dbe93cfab37503d21f45d3a6a32ee2dd32451c1ce8c63308b10`,
`ad895f785a66f249a9c4d45ea353b559acebf57ad8f82fedf43af2361e79e83b`, and
`62569df0c68123922de03f482f0affae3975114186581dd30adce650d45f28f6`; the
leaves and redirects are gated `apple-clang`, so the recorded linux-clang
profile is byte-unaffected and its leaf pins await Linux toolchain
regeneration.

## Prior dual-image endian-conversion release

This historical source profile additionally replaced the byte-identical
littlefs v2.10.1 `lfs_fromle32`, `lfs_tole32`, `lfs_frombe32`, and
`lfs_tobe32` clusters at Apollo-main `[0x004CA7B6,0x004CA80A)` and
bootloader `[0x004104BE,0x00410512)`. The shared freestanding source is
`components/apollo_main/core_overlay/runtime_littlefs_util_endian.c`, SHA-256
`830d49b043181d270ac0aedda432c5e232ce8d6ce65e8e537b80b1a706fd6cac`,
adapted from authenticated littlefs v2.10.1 `lfs_util.h`.

Both reviewed targets are little-endian. The little-endian conversions
compile to two-byte identity leaves and the big-endian conversions to
four-byte byte-swap/return leaves, with no relocation, literal, undefined
symbol, configuration object, filesystem state, callback, allocation, or
hardware access. The four main leaves occupy `[0x007B0128,0x007B0138)`,
including two generated two-byte alignment gaps; the four bootloader leaves
occupy `[0x00434516,0x00434522)` without padding.

The resulting Apollo-main overlay is 114,196 bytes with SHA-256
`a111e90b993114d175aeceed74a58b89d365996fb9eefdb8d0d9cac42717f2f6`.
Its 3,637,592-byte provider has SHA-256
`0a55496307eee536a60196c7e7bcec3f2d92501418756877e790bac11756573f`
and installs 3,637,560 bytes through `0x007B0138`. The bootloader overlay is
170 bytes with SHA-256
`9c41f38d0d6fdde4dcbb40222adb637bbfe7625e6117eb1f475594bad8a613e8`;
its 148,770-byte provider has SHA-256
`b2922a93cf19d63a057c473e8937410efe32a8ad9202607972d34dac12e6f19e`
and ends at `0x00434522`, leaving 15,070 bytes before Apollo main.

The deterministic 4,415,594-byte EVENOTA package has SHA-256
`cbfc505c73900cc15c0ccfa7956f6adb27d62a0d60d2d98417ac9a516ccd0c98`.
Its ownership ledger records 114,396 source-compiled bytes, 81,187 generated
bytes, and 4,220,011 opaque compatibility bytes: 195,583 bytes, or
4.429370%, are source- or generator-controlled. The flash inventory contains
742 placed regions and the same two deliberately unresolved codec regions.

The release gate passes 55 focused source, upstream-oracle, ABI, topology,
and inherited integration tests in 41.693 seconds, all 248 Apollo-main
aggregate tests in 521.732 seconds, and all 1,800 repository tests in 916.875
seconds. `./make.sh verify` accepts every authenticated snapshot, source
overlay, read-only analyzer, provider, and manifest. Three output-isolated
lanes at `build/repro-littlefs-endian-output-{a,b,c}` reproduce both overlays,
both providers, the package, and the flash plan byte-for-byte. The independent
EVENOTA analyzer and both offline main-only inspectors accept the package; no
hardware or serial endpoint was accessed.

## Prior dual-image littlefs fallback-bitops release

That profile replaced the byte-identical littlefs v2.10.1
`lfs_npw2`, `lfs_ctz`, and `lfs_popc` fallback bodies at Apollo-main
`[0x004CA720,0x004CA7B2)` and bootloader
`[0x00410428,0x004104BA)`. The 2,795-byte shared bounded source is
`components/apollo_main/core_overlay/runtime_littlefs_util_bitops.c`,
SHA-256
`405092c6e8fc65a740f951cb2affaad8766e2553c7b8d290ff58f435e8830f47`.
It explicitly selects the authenticated `LFS_NO_INTRINSICS` expressions,
preserving `lfs_npw2(0) == 32`, `lfs_npw2(1) == 1`, and
`lfs_ctz(0) == 0`. Its sole text relocation is the source-closed
`lfs_ctz -> lfs_npw2` Thumb call; it has no external, undefined, literal,
data, filesystem-state, callback, allocation, or hardware dependency.

Apollo main places the 72-, 16-, and 42-byte post-link bodies at offsets
109,648, 109,720, and 109,736 (`0x007AEF74`, `0x007AEFBC`, and
`0x007AEFCC`), with post-link hashes beginning `ef17f9ce`, `b4282c02`, and
`7b7c7ddb`. Its 114,324-byte overlay has SHA-256
`00318de9ff51e19f77d889fa691a3a2a54e035b1287843bda857f944af58e065`;
the 3,637,720-byte provider has SHA-256
`f0da043e234dc38481059459755e091622d689313cd12e5c8d5155c7b4ba3202`.
The 3,637,688 installed bytes have SHA-256
`cfa3e79abf4ac4d932d3612ced595f950c1c2355b1890fd9a13e9635c59c2e85`,
end at `0x007B01B8`, and leave 261,704/319,048 bytes below the
`0x007F0000`/`0x007FE000` bounds. The existing isolated AmbiqSuite,
metadata-list, and endian leaves now begin at `0x007B0128`, `0x007B017C`,
and `0x007B01A8`.

The bootloader places the 56-, 16-, and 42-byte bodies at offsets 90, 146,
and 162 (`0x004344D2`, `0x0043450A`, and `0x0043451A`), with post-link
hashes beginning `1048afe6`, `a5616df4`, and `e537e00e`. Its 282-byte
overlay has SHA-256
`b934dbea7624660c3c774eb0f4edd5e73a738fc59023fc69cfac96417dfe2fee`;
the 148,882-byte provider has SHA-256
`1aa7920a16ed2857a2743394c0f62395a2f2477f95c965da47d1e29c4d2d8247`,
ends at `0x00434592`, and leaves 14,958 bytes before Apollo main. The
existing isolated AmbiqSuite, metadata-list, and endian leaves now begin at
`0x00434544`, `0x00434574`, and `0x00434586`.

The 4,415,834-byte package has SHA-256
`058782604ab6cb946aff0acedbbef7d367bb1d82114f28c9a70276bcdf178e9a`,
boot/main CRC-32C/MSB values `0x1162559F`/`0xB436A24C`, and flash-plan
SHA-256
`2015673f529e550e67c2f219d789746cceef1b022bdcf2db16f1ba451a8aa05e`.
Its 745 placed, two unresolved, and five container-only regions classify
114,638 source bytes (2.596067%), 81,477 generated bytes (1.845110%), and
4,219,719 opaque bytes (95.558823%). The controlled total is 196,115 bytes,
or 4.441177%. The new focused production gate passes 6/6 tests in 13.693
seconds, and the inherited focused gate passes 55/55 tests in 39.997 seconds:
61 tests across the two isolated suites in 53.690 seconds summed. The
relocation-repin audit reviewed 22 shifted compiled-body pins; every function
boundary and all 185 relocation records remained unchanged, and all 100
differing bytes were relocation write sites. All five rodata sections were
byte-identical and shifted by 128 bytes. The canonical repository run passed
all 1,806 tests in 1,139.177 seconds; inside that run, all 248 Apollo-main
aggregate methods passed. `./make.sh source` and `./make.sh verify` pass, the
offline analyzer and both policy-scoped main inspectors accept the package,
and three output-isolated lanes reproduce both overlays, both providers, the
package, and the flash plan byte-for-byte.

## Prior Apollo-main FreeRTOS NTZ in-place release

That historical profile source-assembled the five remaining
FreeRTOS-Kernel V10.5.1
`portable/IAR/ARM_CM55_NTZ/non_secure/portasm.s` leaves directly into their
stock Apollo-main addresses. The MIT-licensed, sectionized Clang adapter is
`components/apollo_main/core_overlay/runtime_freertos_ntz_port.S`, 5,487
bytes with SHA-256
`38c6a259ca2fbfbefb373ef5a80216f2e5f1cad998173ca2b4c9cfde6c01aee8`.
It is derived from the authenticated 11,686-byte upstream source with
SHA-256
`eaa83b3867edec5560c69f2a21facd7aff3c0f3bfcdfc5751722375ae328ee8f`
at commit `def7d2df2b0506d3d249334974f51e427c17a41c`; this is a
reconstruction baseline, not a claim about Even Realities' historical
checkout.

| Function | Stock span | Bytes | Stock SHA-256 |
|---|---|---:|---|
| `vRestoreContextOfFirstTask` | `[0x005FA058,0x005FA07E)` | 38 | `10edd4871b5f0c829e38618f1003ef0c45ec3629219317e23c62a2e255b0f4f8` |
| `vRaisePrivilege` | `[0x005FA07E,0x005FA08C)` | 14 | `29bceedf776515c291813e4eecd9a836378b81550c42d08aee35cf15df3bd8db` |
| `vStartFirstTask` | `[0x005FA08C,0x005FA0A4)` | 24 | `44ba0097fbbc1d0691837d5c51bee83e6b61509c9d89efffee9c202d930e6347` |
| `PendSV_Handler` | `[0x005FA0C8,0x005FA120)` | 88 | `d8e234bfa34805ad160e41ef54801973c9c871b36cf7ac0f365b56fe503253e3` |
| `SVC_Handler` | `[0x005FA120,0x005FA132)` | 18 | `d0fac197473b52d6ed466462d237ddb20dd8096a6507ea559e75d4bd9d88da94` |

The target ELF has five independent, two-byte-aligned executable sections
with raw adapter-body hashes `6cd49195...a1d8be`,
`29bceedf...3bd8db`, `28d1d6e4...1ae16b7`,
`12c7f208...3953ee`, and `1807cfce...96e1c4`; relocation produces the
exact stock hashes above. Its explicit six-record allowlist contains four
`R_ARM_THM_PC8` literal relocations, the `PendSV_Handler` call to
`vTaskSwitchContext` at `0x004551B4`, and the `SVC_Handler` tail branch to
`vPortSVCHandler_C` at `0x00442134`. The literal targets remain
`0x005FA134` (`204a0720`, `pxCurrentTCB=0x20074A20`) and `0x005FA138`
(`08ed00e0`, `VTOR=0xE000ED08`). SVC and PendSV vectors remain
`0x005FA121` and `0x005FA0C9`.

The `in_place_leaves` contract keeps these names out of the appended
overlay ABI and out of `patch_sites`. Each leaf is compiled separately with
the reviewed Apple Clang 21 Cortex-M55 flags, authenticated against both its
stock and expected size/hash, resolved only through its exact relocation
allowlist, checked for literal contents and nonoverlap, and installed only at
its fixed stock address. That release's appended overlay therefore remained 114,324
bytes with SHA-256
`00318de9ff51e19f77d889fa691a3a2a54e035b1287843bda857f944af58e065`;
the 3,637,720-byte provider remained
`f0da043e234dc38481059459755e091622d689313cd12e5c8d5155c7b4ba3202`;
and the 4,415,834-byte package remained
`058782604ab6cb946aff0acedbbef7d367bb1d82114f28c9a70276bcdf178e9a`.
The component report records 182 source-owned in-place bytes, 114,506 total
source-owned bytes, and 3,443,066 opaque base bytes.

That release's manifest contained 750 placed, two unresolved, and five container-only
regions. Flash-plan SHA-256 is
`eda45c2cc276bd70bc123267d9fbdc09b0ae4aa030a7557f874c259ca7f5fee8`.
It classified 114,820 source bytes (2.600188%), 81,477 generated bytes
(1.845110%), and 4,219,537 opaque bytes (95.554702%); 196,297 bytes
(4.445298%) are source- or generator-controlled.

That release's focused production gates passed 23/23 tests in 18.333 seconds.
The linker and inherited focused gates passed 21/21 tests in 0.705 seconds.
`./make.sh source` and direct verification of
`manifests/g2-2.2.6.10-core-source.json` pass. All 248 Apollo-main tests
passed in 582.904 seconds. `./make.sh test` passed all 1,838 tests in
1,038.709 seconds, including all six CMSIS constructor compile-closure tests.
Three output-isolated lanes at `build/repro-freertos-ntz-output-{a,b,c}`
byte-identically reproduce the main overlay/provider, boot overlay/provider,
package, and flash plan; their temporary manifests were moved to Trash.

The authenticated `third_party/cmsis-freertos` compile-input snapshot contains
CMSIS-FreeRTOS v10.5.1 plus its declared CMSIS_5 5.9.0 dependency. The
wrapper and headers retain Apache-2.0 notices, while the separately supplied
FreeRTOS kernel retains MIT terms. Candidate-only shims at
`components/apollo_main/core_overlay/candidates/cmsis_freertos_constructors/`
provide `{FreeRTOSConfig.h,portmacro.h,cmsis_freertos_target.h,string.h}`.
With those shims, the authenticated, unmodified CMSIS-FreeRTOS v10.5.1
`cmsis_os2.c` compiles for Cortex-M55 with `-Oz -Werror`. The garbage-collected
constructor closure retains 370 text bytes: `IRQ_Context` 46,
`osMessageQueueNew` 88, `osMutexNew` 98, and `osSemaphoreNew` 138. It retains
zero read-only or writable data and four 8-byte EHABI `.ARM.exidx` sections;
6/6 isolated proof tests pass in 0.231 seconds.

That complete-translation-unit closure remains a broad candidate proof for
unrelated CMSIS services. The narrower
`osMessageQueueNew`, `osMutexNew`, and `osSemaphoreNew` algorithms are production-integrated
through bounded source adapters with authenticated G2 configuration, ABI,
stock topology, and direct source-owned FreeRTOS dependencies.
The semaphore cleanup path is closed over a source-owned `vQueueDelete`,
which in turn reaches the now-source-owned `heap_4` free path. This does not establish Even's
historical CMSIS checkout. The unresolved RTE/device-header,
`SystemCoreClock`, MVE, broad `INCLUDE_*`, assert, NVIC, libc, and 108-byte
candidate `StaticTask_t` questions remain outside that bounded production
leaf.

## Prior dual-image littlefs disk-version-parts release

That profile source-integrated exact littlefs v2.10.1
`lfs_fs_disk_version_major` and `lfs_fs_disk_version_minor` from commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`. The shared 1,734-byte
`components/apollo_main/core_overlay/runtime_littlefs_disk_version_parts.c`
has SHA-256
`920d03e80c9d16a1d0b4299f8151eefe4d9f3ac1ba89c2d40bcc5830335eb5a7`.
Focused disassembly supplies only the authenticated non-`LFS_MULTIVERSION`
configuration seam and exact stock topology. The complete stock spans are
Apollo main `[0x004CB0CA,0x004CB0D6)` and
`[0x004CB0D6,0x004CB0E0)`, and bootloader
`[0x00410DD2,0x00410DDE)` and `[0x00410DDE,0x00410DE8)`.

Each compiler profile emits two ten-byte leaves whose sole
`R_ARM_THM_CALL` relocation closes over the existing source-owned
`open_cfw_littlefs_disk_version` provider. Apollo main places the major leaf
at `[0x007B01B8,0x007B01C2)`, two generated alignment bytes at
`[0x007B01C2,0x007B01C4)`, and the minor leaf at
`[0x007B01C4,0x007B01CE)`. The bootloader places the pair contiguously at
`[0x00434592,0x0043459C)` and `[0x0043459C,0x004345A6)`.

The main overlay is 114,346 bytes with SHA-256
`bdc1e353d1adcb0075231afb6c423616dcc0da8335b4b430afe51763a0b9df20`;
its 3,637,742-byte provider has SHA-256
`d69c4834f65b0661834f990da8167ca6989a1b1c97fda838edc488a4ed0b3e8e`.
The boot overlay is 302 bytes with SHA-256
`e94e33658aca89d3830182bc6c17c656256a194262835c041fecc93e1d72dc59`;
its 148,902-byte provider has SHA-256
`abc583d976a01e237ffa4ed29e4be1b6ff0e5ae2d9756bccec58d1779fe20239`
and leaves 14,938 bytes before Apollo main.

The 4,415,876-byte package has SHA-256
`60cd913a716266b349ce18295064f2484749a7dbad2ab9244c923c927bd56c2f`.
Its 546,404-byte flash plan has SHA-256
`52124c17205ae10e47f0b02d0cd6bae7c2b30e10d65d787aa34201a53fe0dc68`
and records 757 placed, two unresolved, and five container-only regions.
Package ownership is 114,860 source bytes (2.601069%), 81,523 generated
bytes (1.846134%), and 4,219,493 opaque bytes (95.552796%); 196,383 bytes
(4.447204%) are source- or generator-controlled.

## Prior dual-image littlefs allocator-lookahead release

That profile additionally source-integrated the exact littlefs
v2.10.1 `lfs_alloc_lookahead` algorithm from commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`. The shared source is
`components/apollo_main/core_overlay/runtime_littlefs_alloc_lookahead.c`,
SHA-256
`44ab9037747a4cb209404423d52cf817b035cbab5177a8c0cb05090df4b68491`.
Focused disassembly recovers only the four `lfs_t` ABI offsets used by the
upstream body: `lookahead.start=0x54`, `lookahead.size=0x58`,
`lookahead.buffer=0x64`, and `block_count=0x6C`.

Both official 56-byte bodies have SHA-256
`58285c138461a673be0bed2c5376f8d739e40e2aea753ad05d5061bfbc9265cf`.
The Apollo-main entry at `0x004CB0F6` redirects to a 50-byte,
four-byte-aligned source leaf at `[0x007B01D0,0x007B0202)`, after two
generated alignment bytes. Its raw target SHA-256 is
`ff36aeaff70307ae466d9f7fafacad678c706db1551b18d98d7fe68bf3dc5eef`.
The bootloader entry at `0x00410DFE` redirects to a 48-byte,
two-byte-aligned source leaf at `[0x004345A6,0x004345D6)`, SHA-256
`bd8e7c926d98a940f215cd41a2fb5932bfbf1abcf7378839dcadd537ae55324d`.
Both target leaves are call-free and relocation-free. A 20,000-case host
differential gate compares the source wrapper with the authenticated
upstream implementation across wraparound, bitmap bounds, and bit positions.

That Apollo-main overlay is 114,398 bytes with SHA-256
`2189ec69f7076e216c2ba7388f4eb9d19647feb9f89c382864012902be4e0fdf`;
its 3,637,794-byte provider has SHA-256
`557fe93fdf79c5cb332c7db731db29ed7cfc42be3daa49fb0d022f81e7fe0ba8`.
The bootloader overlay is 350 bytes with SHA-256
`1b8bb2893a33a18b8481b785a57d49c2849396cc05c5ef20d86f8cf5cef255a5`;
its 148,950-byte provider has SHA-256
`9af8b65041bbd576b49b4f88e2f7427daf7bb445981d608799d86e1987468736`.
The complete 4,415,976-byte package has SHA-256
`3d4b2f3e22a10d0755642c0544786c9a881b2ab7c2271d8a184a83f5d3d7d13f`.
Its 550,026-byte flash plan has SHA-256
`73978705e32bbb968a9741620a80e1a70f866b5e43db60f4a9f08b4404ce34d1`
and records 762 placed, two unresolved, and five container-only regions.
Package ownership is 114,958 source bytes (2.603230%), 81,637 generated
bytes (1.848674%), and 4,219,381 opaque bytes (95.548096%); 196,595 bytes
(4.451904%) are source- or generator-controlled.

## Prior CMSIS-FreeRTOS `osMessageQueueNew` release

That profile source-integrated the exact allocation and validation
algorithm from CMSIS-FreeRTOS v10.5.1 `osMessageQueueNew`, authenticated at
commit `d213f261b5be6bb29a7cce8b84071706b72f4d53`. The bounded 8,427-byte
Apache-2.0 source is
`components/apollo_main/core_overlay/runtime_cmsis_message_queue_new.c`,
SHA-256
`8897019aa7a2beca32a88dc60808fb1f99b1538933b8ab4fbd9ed4fed38d433c`.
The separately called FreeRTOS V10.5.1 queue/task functions retain MIT
terms.

Focused disassembly establishes the G2 configuration rather than recreating
the algorithm: static and dynamic allocation are enabled, the queue registry
is disabled, `StaticQueue_t` is 80 bytes, and the 32-bit
`osMessageQueueAttr_t` is 24 bytes with the upstream field layout.
Construction is rejected in handler mode, or in masked thread mode after
the scheduler starts, using the upstream `IPSR`/`PRIMASK`/`BASEPRI` policy.
Static creation requires both buffers and sufficient sizes; all-zero
attributes select dynamic creation; mixed attributes and zero message
dimensions are rejected.

The complete stock span `[0x00449A32,0x00449ABE)` is 140 bytes with SHA-256
`52d0abf097914cc84b2cdfe7f628dc61f9efb40bac880112062315d2b1bfba47`.
All 15 direct callers remain at the original entry; their ordered digest is
`7974f375f4b38120a6df7ce5416cef9fa65031d5768226b8785d2916d0f96f18`.
The generated complete-entry replacement has SHA-256
`b9e761042539e109acea61b03a522bb5795539850f0751906c6e06d0da198a47`.

The raw 124-byte, four-byte-aligned leaf has SHA-256
`543fb1ef418aeadd05e2f3b3e60c3f48c0f3521dfa995a3079a86b86ccc58eee`.
Its complete relocation allowlist is `+0x10 R_ARM_THM_CALL` to the
source-owned scheduler-state getter, `+0x44 R_ARM_THM_CALL` to the
source-owned static generic queue creator, and
`+0x78 R_ARM_THM_JUMP24` to the source-owned dynamic generic queue creator.
After two generated alignment bytes at `[0x007B0202,0x007B0204)`, the final
leaf occupies `[0x007B0204,0x007B0280)` with SHA-256
`afbba4f9f08b2df17a4350d7a7e83d99b8439283ee40c1a1604bd879dff75f04`.

That Apollo-main overlay was 114,524 bytes with SHA-256
`de76f5db2f04f48c81ea480c348a3c9151d4441c522eba68621ad812290153e2`;
its 3,637,920-byte provider has SHA-256
`874bdc621a6cd91848dee66038c3ba97d7e4b7c7ab1fb5063739bf69fc3047e1`.
The 3,637,888 installed bytes have SHA-256
`79a411508a06801619ba4ca8763f71739c728343ff00e3dc742261226c24edcb`.
The bootloader provider remains unchanged at 148,950 bytes. The complete
4,416,102-byte package has SHA-256
`c7baf50cd5386a5e27b4c284cc0084e8cf5d0b83d74eb08b8d4a997bf66474f4`;
boot/main CRC-32C/MSB values are `0xB7E2DD07`/`0xF2170DD9`.
Its 552,937-byte flash plan has SHA-256
`79da631918503c668516e1af5d3844e3dab65c9e63d8add4834a43536ef69407`
and records 766 placed, two unresolved, five container-only, and six
protected regions. Package ownership is 115,082 source bytes (2.605963%),
81,779 generated bytes (1.851837%), and 4,219,241 opaque bytes
(95.542200%); 196,861 bytes (4.457800%) are controlled.

The focused production gate passes 10/10 tests. All validation was offline;
no physical device, serial endpoint, debugger, or flasher was accessed.
At that point, `osMutexNew` and `osSemaphoreNew` remained candidate-only.

## Replacing more blobs with source

The replacement unit is a complete controller payload, not an arbitrary outer
package span. Compile a raw image with the controller's verified linker map,
then use the appropriate wrapper:

```sh
python3 tools/open_cfw.py wrap main path/to/main.raw.bin main.payload.bin
python3 tools/open_cfw.py wrap case path/to/case.raw.bin case.payload.bin \
  --case-version 1.2.58
python3 tools/open_cfw.py wrap touch path/to/touch.raw.bin touch.payload.bin
```

After a source-built payload has equivalent validation and hardware evidence:

1. add its reproducible component build under `components/<name>/`;
2. create a derived manifest and change that component's provider from
   `official_blob` to `source_build`;
3. update the provider size and SHA-256;
4. replace or remove the whole-package reference hash once divergence is
   intentional; and
5. retain the same flash boundaries until new hardware evidence changes them.

Codec and EM9305 source wrappers are intentionally absent today: their package
formats are parsed, but a source toolchain and complete install semantics have
not yet been established.

## Safety and provenance

The source-divergent artifact has passed structural checks and offline flasher
inspection, but it has not yet been installed on physical G2 hardware. The
Apollo application update is single-slot with no proven autonomous rollback.
The preceding metadata-list release carried a 148,758-byte source-built
bootloader provider with
twelve authenticated redirect sites covering 186 bytes, three generated
alignment bytes, and 156 appended source bytes. Its SHA-256 is
`0c08766d691c40d86e5bc1fefd4ab7a0abc890fbb848c8ebe249efdbcea69052`,
and it ended at `0x00434516`. The bootloader remains hardware-untested and materially
riskier to program than the application.
The endian-conversion release superseded those artifact pins, and the
fallback-bitops release superseded them again with the historical
148,882-byte bootloader and 3,637,720-byte application providers documented
above. The subsequent NTZ tranche changed only fixed-address source ownership
and the manifest partition. The disk-version-parts tranche advanced the
providers to 148,902 and 3,637,742 bytes. The allocator-lookahead tranche
advanced them to 148,950 and 3,637,794 bytes; the message-queue and task-name
tranches advanced Apollo main to 3,637,920 and 3,637,958 bytes. The mutex
tranche advanced Apollo main to 3,638,076 bytes; the historical
heap/semaphore tranche advanced it to 3,638,906 bytes. The EasyLogger helper
tranche advanced main to 3,639,306 bytes and the bootloader to 149,222 bytes.
The tick-getter tranche advanced main to 3,639,328 bytes; the missed-yield
tranche advanced it to 3,639,342 bytes. The current event-item reset and
mutex-held tranche advances it to 3,639,396 bytes without changing the
bootloader or the physical-installation risk.
Back up readable per-device state before physical experiments, preserve the
case serial-number windows, and keep the Ambiq secure bootloader and update
flag outside application artifacts.

The files under `blobs/official/` are unmodified proprietary reference
payloads extracted from a locally obtained official firmware bundle. Their
hashes and origin are recorded in
[`blobs/official/g2-2.2.6.10/PROVENANCE.md`](blobs/official/g2-2.2.6.10/PROVENANCE.md).
Do not assume the source license for this project grants redistribution rights
for those blobs.

## Prior FreeRTOS `pcTaskGetName` release

That profile promoted the exact FreeRTOS-Kernel V10.5.1
`pcTaskGetName` algorithm from authenticated commit
`def7d2df2b0506d3d249334974f51e427c17a41c`. The 3,489-byte MIT source
`runtime_freertos_pc_task_get_name.c` has SHA-256
`d46408b0bdce9622ac1fa8c694ccc790c76169b681d0c413a4ada35fbe29d21a`.
Focused disassembly supplies the fixed `pxCurrentTCB` word at `0x20074A20`,
the 32-byte task name at TCB offset `0x34`, and the G2 fail-stop assertion.

The complete official span `[0x00454F16,0x00454F38)` is 34 bytes with
SHA-256
`a25ace28ece3ca37f11da7e73945acb28f1f99d906203613e9856d2070c07817`.
Its sole caller at `0x0044AAEE` remains unchanged. The raw 38-byte leaf hashes
to
`b680e949844cca19a586fbe865837f8180e592434ac1517b29ceb1482c9dd3b6`;
its sole relocation binds directly to source-owned `ulSetInterruptMask`.
The final leaf occupies `[0x007B0280,0x007B02A6)` with SHA-256
`88edbdea558812d213013a8d319a09c63dafa86ec91a7640f427c72c77552da1`.

The final overlay/provider pins are 114,562 bytes/
`188a9b26fce7b7899e3c0eebd698552edc6a453396b9b05107841c63d488e8ee`
and 3,637,958 bytes/
`6830ed33f567b4ac8b4c401612b83b56caa38d107bb9b1fc5d210dce9add9214`.
The 4,416,140-byte package has SHA-256
`624e18cea8e36c954809f2d36b8b539275e7fa8ba9f305a166ed9e83b7a86d43`;
its 768-region flash plan hashes to
`4b1ce318c286cb7a0a83c144b149c61581ca658080c229bd7474cf84ed472b35`.
The dedicated production gate passes 7/7 tests, offline.

## Prior CMSIS-FreeRTOS `osMutexNew` release

That profile integrates the exact CMSIS-FreeRTOS v10.5.1
`osMutexNew` allocation and validation algorithm from authenticated
`cmsis_os2.c` commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`. The 9,798-byte Apache-2.0
adapter has SHA-256
`28081734a384c089635681014ed028414b75d375c22f0a52a64f53e22842cf2d`;
its source-owned FreeRTOS dependencies retain MIT terms.

Focused disassembly pins enabled static/dynamic allocation and recursive
mutexes, disabled queue registry, robust rejection, the recursive-handle low
bit, the 80-byte static control block, the 16-byte 32-bit attribute layout,
and the exact `IPSR`/`PRIMASK`/`BASEPRI` rejection policy. The complete stock
span `[0x0044971C,0x004497B6)` is 154 bytes with SHA-256
`09f88d8a6a64730936a52aa0c2f90d9bcb0152f6e2439919f6409110148999ec`.
Its 30 direct callers have ordered digest
`14d18197e409351bfa6ded1310c61c1f27246ebd93ecf86452d19ac0bdadbfd0`;
no alternate, interior, or stored entry exists.

Two generated zero bytes at `[0x007B02A6,0x007B02A8)` align the 116-byte
leaf at `[0x007B02A8,0x007B031C)`. The five relocations at
`+0x0E/+0x32/+0x56/+0x5C/+0x64` bind only to the source-owned
scheduler-state getter and static/dynamic mutex creators. The raw and final
leaf SHA-256 values are
`59e1d787a4beaa36b01d932672e43893331fc5d22a46e2371cc111ec4dacb192`
and
`4b404daca19132875236099c06bd18ab6441ade2d61a7f3c855210ddd2a28863`.

That release's 114,680-byte overlay hashes to
`7603cf2a0de6e8b05d66dc356bf3e0701f6157536d29bdac8ad692dc56e0362c`;
the 3,638,076-byte Apollo-main component hashes to
`f696c6dfbd8ab1f7b5cc44fdc06fcdc5baf44f368ad55130e7571d82ee31ec82`.
The 4,416,258-byte package has SHA-256
`11d40cd1b3648f96b5ec98c9fa2dff6de121e878978206a0a9694ede38d3a0ff`.
The focused production gate passes 10/10 tests offline. No physical device,
serial endpoint, debugger, flasher, reset, or external-flash operation was
accessed.

At that point, `osSemaphoreNew` remained candidate-only pending production
closure of `heap_4`; the following release closes both dependencies.

## Prior FreeRTOS heap and CMSIS semaphore release

That profile production-integrated the FreeRTOS-Kernel V10.5.1
`heap_4` algorithms for heap initialization, ordered free-list insertion and
coalescing, `pvPortMalloc`, and `vPortFree`. The 16,885-byte MIT adapter
`runtime_freertos_heap4.c` has SHA-256
`d848b90a00da24db963c49dbff2472314b2a76c6cf269efef46e6cac56889986`.
It preserves the recovered `0x2F000`-byte heap at `0x20004558`, the sentinel
and accounting globals at `0x20074158...0x2007466C`, and the stock scheduler
and malloc-hook seams. The four complete stock spans total 552 bytes at
`[0x00456110,0x00456338)` and now redirect to source leaves at
`[0x007B031C,0x007B057E)`, with two four-byte-alignment gaps.

The same atomic release ports FreeRTOS `vQueueDelete` through the 5,851-byte
MIT adapter, SHA-256
`fa8033f61e418dbfb304dd7443dea340bfff88958df493e276ea92db4491da2b`.
Its 34-byte stock span `[0x00441EA2,0x00441EC4)` redirects to the 38-byte
leaf `[0x007B0580,0x007B05A6)`, closed over source-owned heap free and
interrupt masking.

The 11,566-byte Apache-2.0 `runtime_cmsis_semaphore_new.c`, SHA-256
`a947868d3fbcfc7f41d021210355e0ff777d49d3db84fa0da71a255d319c1527`,
ports the exact authenticated CMSIS-FreeRTOS v10.5.1 `osSemaphoreNew`
algorithm. Focused disassembly supplies only the G2 allocation/IRQ policy,
80-byte static control-block ABI, maximum/initial-count validation, and stock
topology. The complete 180-byte stock span
`[0x0044989A,0x0044994E)` redirects to the 178-byte leaf
`[0x007B05A8,0x007B065A)`. Its seven relocations bind to the source-owned
scheduler-state getter, static/dynamic generic creators, generic send,
static/dynamic counting-semaphore creators, and `vQueueDelete`.

The final overlay is 115,510 bytes with SHA-256
`6359e4e8c824af3cea36280a1aabd6ad671027e38fb3263fe9ac0cbb292660b4`;
the 3,638,906-byte Apollo-main component hashes to
`00d112e265f40dd8bf98fc9021bba54b3bcc94f159111b2f4815d5484e91c67c`.
The 4,417,088-byte package hashes to
`064c9429352132cee2a5dfe45c2bf52349e10111b89db91f093b1ce16ed0c2b0`.
Its 570,697-byte flash plan hashes to
`8334c9308a7ae7f03d7a2a214cca946063963b1636a9088fe730a15303dd2975`
and records 791 placed, two unresolved, five container-only, and six
protected regions.
The dedicated heap, queue-delete, and semaphore gates pass 13/13, 7/7, and
8/8 tests offline. No hardware was accessed.

## Prior dual-image EasyLogger helper release

That profile replaced four source-equivalent EasyLogger helpers in
both Apollo images: `get_fmt_enabled`, the unsigned-argument and
pointer-argument format predicates, and `elog_strcpy`. The authenticated
stock spans total 320 bytes per image. Existing callers retain their original
entries; complete non-linking Thumb redirects and NOP fill branch to appended
source leaves.

The shared 4,975-byte MIT source and 6,505-byte header have SHA-256 values
`8f2850f789fba3b08bdc3e1fa8f3a4646aaef7e4b16862f3be53478071aa22b5`
and
`f3a7e9bce0f136a2ff4a76929c317aef7bbc7c29dfc60d58311d94e58f6e2393`.
The 7,068-byte MIT image-seam source hashes to
`78dc5aa9a7eb4f072b3169ae1837855007f25e1adccec7deaefecc486c8f0823`.
It binds the shared algorithms to the recovered main and boot logger objects
and preserves their distinct assertion hook, diagnostic-output, and wait
policies. The official strings, hook globals, `elog_output` entries, and wait
wrappers remain explicit binary seams; the helper algorithms and image
binding are source-owned. Both images use the authenticated tag record layout
`level +0`, `tag +1`, and `tag_use_flag +0x20`.

Apollo main appends 390 source bytes plus ten alignment bytes and now has a
115,910-byte overlay and 3,639,306-byte component with SHA-256 values
`e59da6e6753c0c8a9fa73bad8cd555313d0e2ae6ed95006c818e6697e4fbe32d`
and
`00f5f11dd18c13c56137d0f527da3ecd8ae850a9ae35dc96d671a4b998d79b61`.
The bootloader appends 270 source bytes plus two alignment bytes and now has a
622-byte overlay and 149,222-byte provider with SHA-256 values
`fc02cf66854adace4d213e08764e435e27c8c2bc7cc4f7caac6ff286f3adf813`
and
`b4a5b0f2028842a2d6fde9424fff05fac2db3bf0e26e7f01d16a990e67ed9052`.

The complete 4,417,760-byte package hashes to
`fb662322f26e06aa04eb1d3f55f8c8f18606e510fac9c35885de3e4f92864c4d`.
Its 592,687-byte flash plan hashes to
`c06c84e277bad2160479e0ec1f7a626abb804574f42ecee0709f0978657cd1b3`
and records 822 placed, two unresolved, five container-only, and six
protected regions. Validation remained offline; no hardware was accessed.

## Preceding Apollo-main FreeRTOS tick-getter release

The production profile now source-owns the exact FreeRTOS V10.5.1
`xTaskGetTickCount` and `xTaskGetTickCountFromISR` algorithms. The baseline is
upstream commit
`def7d2df2b0506d3d249334974f51e427c17a41c`; its 223,695-byte MIT
`tasks.c` hashes to
`14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463`.
The bounded 3,412-byte source adapter and 1,186-byte header hash to
`948d1b2de6026adc7cf84a34a359c859c32126b3afcafe92c2347f5f7ab56363`
and
`adc4065b3504a7eacb2e29e2d357636917e2b690afc49b265689e36d66171dae`.

Focused disassembly corrects the official boundaries to
`[0x00454EFE,0x00454F06)` for the normal getter and
`[0x00454F06,0x00454F10)` for the ISR getter. Address `0x00454F08` is the
ISR function's second instruction, not another entry. The two authenticated
stock spans are 8 and 10 bytes, hash individually to
`6dbb234e35fb86f883529c083fed0e1cabdca99d6647a95568ed1a5522310ac0`
and
`8fe0a4f494b20b340d1126b2da725919f86c53cc3c1cabf5031fffc03f6de63a`,
and have aggregate SHA-256
`d0b93ff29439d26b92dcd56fd012a9dab842364f7c5f4b4f7f39a27ed8cfe077`.
Nine normal callers and the sole ISR caller continue to enter those stock
addresses.

The appended source boundary is a relocation-free provider at
`[0x007B07EC,0x007B07F8)`, followed by four-byte normal and ISR getter leaves
at `[0x007B07F8,0x007B07FC)` and `[0x007B07FC,0x007B0800)`. The provider
encodes the recovered `xTickCount` RAM seam at `0x20074A34`; each getter has
one `R_ARM_THM_JUMP24` relocation to that provider. Two generated alignment
bytes at `[0x007B07EA,0x007B07EC)` separate the prior EasyLogger leaf from
the 20 source bytes. Complete `B.W` plus NOP redirects replace all 18 stock
bytes.

The current main overlay is 115,932 bytes with SHA-256
`272ba0e0492b0c6b721adec53a007809158d6871ccdb7ec52d4b6ceadd4b4529`.
The 3,639,328-byte component hashes to
`615304858150f5ee6b7b4c62a714629375010c6f4ab20bea1b6958daa6a5b4af`
and has a raw installed-application partition of 116,118 source, 81,622
generated, and 3,441,556 opaque bytes. Builder accounting reports 116,114
source-owned bytes including 182 in place, 81,626 generated patch-site bytes,
81,808 replaced-stock bytes, 3,441,556 opaque base bytes, and the 32-byte
wrapper.

The complete 4,417,782-byte package hashes to
`3bf635fb81439451e67642dc5ce11dde47a1773bda8ef11c12b35cd9bbbec01d`.
Ownership is 116,738 source bytes (2.642457%), 83,415 generated bytes
(1.888165%), and 4,217,629 opaque bytes (95.469378%); 200,153 bytes
(4.530622%) are controlled. Its 596,957-byte flash plan hashes to
`2b89447a0a867d1ec34f51e5798a4da7b28effe8bc5d7e27b1b7f24ce1c9cd3c`
and records 828 placed, two unresolved, five container-only, and six
protected regions, including 53 source-compiled regions, 574 generated
source-entry replacement regions, and 18 generated alignment regions.
Boot remains unchanged at 620 source, 817 generated, and 147,785 opaque
bytes. Validation remained offline; no hardware was accessed.

## Preceding Apollo-main FreeRTOS missed-yield release

FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` supplies the exact
`vTaskMissedYield` body: `xYieldPending = pdTRUE`. The complete stock span is
`[0x004555E6,0x004555F0)`, ten bytes with SHA-256
`8cada1af8ad4973f2ad647d45c8a0ac9c56fdf2d8b270607844b7940eb7d5d2d`.
Focused disassembly binds `xYieldPending` to `0x20074A44`; the only direct
callers are `0x00441FA2` and `0x00441FD8`.

Apple clang 21 and Homebrew clang 22.1.8 emit the same relocation-free
14-byte leaf, SHA-256
`2b028e0c4aa84ce41bfe4b4164a397ae4d5ba9f177900cefb3b71c5d5d339ba9`.
Canonical placement is `[0x007B0800,0x007B080E)`. The resulting
115,946-byte overlay hashes to
`a24cd67ac1d308b8812c329a294f3f07cbe9db4bc815be3fe081ba0c2fd9008c`;
the 3,639,342-byte component hashes to
`f037745e9b85d16fc048ba2fedb282f7fc498a524a90b803b652556e286cf77d`.
The overlay records 592 functions and 559 patch sites. Builder accounting is
116,128 source-owned bytes including 182 in place, 81,636 generated patch
bytes, 81,818 replaced-stock bytes, and 3,441,546 opaque bytes.

The 4,417,796-byte canonical package hashes to
`f06fdc7a1e9034e72321680b35fbd542b12dad06135e6f01f701d670dba676ae`.
It contains 116,752 source, 83,425 generated, and 4,217,619 opaque bytes;
200,177 bytes are controlled. The manifest records 831 placed, two
unresolved, and five container-only regions.

Linux places the same leaf at `[0x007B0F38,0x007B0F46)` after two alignment
bytes. Its 117,794-byte overlay, 3,641,190-byte component, and 4,419,644-byte
package hash to
`00cbcf99a63f69fa7fd2af607685179ac73edeafd0fc8c4e1ad49b6a13a02c0e`,
`f134beba731634fd81b42b143e3b1e414b4b8c07a9e3f009cc49e7c8258b1657`,
and
`13409c4d615651f1b8cb5618d6d1cb1a4d5095e8245c41b41c585a258c9114e1`.
For that historical release, the Linux aggregate required the reviewed
source-root spelling `/Users/kalani/Repo/SybilSightABCD` because TLSF embeds
absolute `__FILE__`. Validation remained offline; no hardware was accessed.

## Prior Apollo-main FreeRTOS task-leaf release

The exact FreeRTOS-Kernel V10.5.1
`uxTaskResetEventItemValue` and `pvTaskIncrementMutexHeldCount` bodies from
commit `def7d2df2b0506d3d249334974f51e427c17a41c` are now source-owned.
Their complete stock spans are `[0x00455ACA,0x00455AE0)` and
`[0x00455AE0,0x00455AF6)`, both 22 bytes, with SHA-256 values
`76463ec53fbc06884c159bf5b7d01708c06e404e9b51bdcaab307b219179c049`
and
`3cca7b821687976e59eccd737dc20b2064b86d66195c6f60f6a7cc2353f40d2f`.
Each has one direct caller, at `0x0047ECCE` and `0x00441D46`,
respectively.

Both leaves preserve the released volatile evaluations of `pxCurrentTCB` at
`0x20074A20`. Reset uses the event-list value at `+0x18`, priority at
`+0x2C`, and `configMAX_PRIORITIES=56`; mutex-held increments the field at
`+0x64` under `configUSE_MUTEXES=1`. Apple clang 21 places the 26-byte reset
leaf at `[0x007B0810,0x007B082A)` and the 24-byte mutex leaf at
`[0x007B082C,0x007B0844)`, after two alignment bytes apiece. Their SHA-256
values are
`04fee613f7c2fb46a3e6f5832f7ea61875543a30160757ffd63579b58f0c45c6`
and
`494b41afb48389988e2678920ae7e1796b41a3d568e5c01c35c12c48bf7b57bf`.

The same authenticated kernel supplies `vTaskSuspendAll` at
`[0x00454D7C,0x00454D88)` and `vTaskInternalSetTimeOutState` at
`[0x00455556,0x00455566)`. The former increments 32-bit
`uxSchedulerSuspended` at `0x20074A58`; the latter stores
`xNumOfOverflows` at `0x20074A48` and `xTickCount` at `0x20074A34` into
the two 32-bit `TimeOut_t` fields. Canonical source placement is
`[0x007B0844,0x007B0854)` and `[0x007B0854,0x007B0866)` with no
intervening padding.

The 116,034-byte canonical overlay hashes to
`d0b36ab3661f3b3487e3962bfe58d9f588f6a6f1ea14e1d9389f7e45d98094bd`
and records 596 functions and 563 patch sites. The 3,639,430-byte component
hashes to
`8a747653cc4d938e447197f2bec199933b68072318f0743e3cd85dcf656db8bc`.
Builder accounting is 116,216 source-owned bytes including 182 in place,
81,708 generated patch bytes, 81,890 replaced-stock bytes, and 3,441,474
opaque bytes.

The 4,417,884-byte canonical package hashes to
`e3b7f29a19a4b3c19a14377a8ea8a77d14458a48678955d406ef7eea274dd6e7`.
It contains 116,836 source, 83,501 generated, and 4,217,547 opaque bytes;
200,337 bytes are controlled. Its 608,608-byte flash plan hashes to
`c6cde87716d8ff407e06998aadaaa0da6e78e5689ea1ac2963f104178447cae2`
and records 844 placed, two unresolved, and five container-only regions.

Linux places reset at `[0x007B0F48,0x007B0F62)` and mutex-held at
`[0x007B0F64,0x007B0F7C)`, then suspend and timeout at
`[0x007B0F7C,0x007B0F8C)` and `[0x007B0F8C,0x007B0F9E)`. Its
117,882-byte overlay, 3,641,278-byte component, and 4,419,732-byte package
hash to
`5c3c381342bb57ec4f33192ea89c2d40e8f0018c39c7092551243be7159dc326`,
`6bead197d657c26fa6ba84210949c8e28b266fbf63a8f908edda1d64516a3163`,
and
`a801d1ecbf83780701cbb7fdc1ae14401a656ba79102877458a3a88c73bc3fc4`.
That historical aggregate used the reviewed source-root qualification
`/Users/kalani/Repo/SybilSightABCD`. Focused evidence is in the
[reset audit](docs/research/freertos-reset-event-item-value-source-boundary-audit.md)
and [mutex-held audit](docs/research/freertos-mutex-held-source-boundary-audit.md),
with scheduler-depth closure in the
[suspend audit](docs/research/freertos-suspend-all-source-boundary-audit.md).
Validation remained offline; no hardware was accessed.

## Prior Apollo-main FreeRTOS scheduler-cluster release

The production profile now source-owns six additional functions from the
authenticated FreeRTOS-Kernel V10.5.1 snapshot: `vPortYield`,
`vPortEnterCritical`, `vPortExitCritical`, `prvResetNextTaskUnblockTime`,
`xTaskIncrementTick`, and `xTaskResumeAll`. Complete `B.W` redirects and NOP
fill replace 770 stock bytes at `[0x004420BC,0x00442114)`,
`[0x00454DCC,0x00454EFE)`, `[0x0045504C,0x0045519E)`, and
`[0x00455876,0x0045589C)`. Named relocations close the scheduler graph over
the existing source-owned interrupt-mask pair and the five new dependencies.

Apple clang 21 places the six leaves at `0x007B0868`, `0x007B0880`,
`0x007B08A0`, `0x007B08D8`, `0x007B08F8`, and `0x007B0A50`. The resulting
116,816-byte overlay hashes to
`b9cb2b00d4859650d120ff713a8af9a1ca626876b46bac751098abdbca575153`;
the 3,640,212-byte component hashes to
`fcb218fd5d9a33b2398cd046550b26258ca9da90d423c50ae635203535614a58`.
It records 602 functions and 569 patch sites, with 116,998 source-owned,
82,478 generated-patch, 82,660 replaced-stock, and 3,440,704 opaque bytes.

The 4,418,666-byte canonical package hashes to
`5a31772a8a4fb746fa9eff53d618541fd38cf44a93c9d602eb88e15d142cef01`.
Its 620,534-byte flash plan hashes to
`4c71800d5c33b618ff8cfaf9c0fb4adf06d59b1dcf753b18c56c6bf7f8a2139a`
and records 861 placed, two unresolved, and five container-only regions.
Manifest ownership is 117,612 source, 84,277 generated, and 4,216,777 opaque
bytes; the three new alignment regions account for the six-byte distinction
between component overlay ownership and package `source_compiled` ownership.

The exact-root Linux profile produces a 118,660-byte overlay
(`77ae17c20117c476596c76544c397516ee561219296db4b7f5dc2d80d0907024`),
a 3,642,056-byte component
(`2c9076f817e28b776bb34538915c18097b1ea24ee1b4cdcfa22aab075797e32f`),
and a 4,420,510-byte all-Linux package
(`2692cc62f39793c3111004bc2d55b65450903b8f6164f9206c43509b7de8462b`).
Its coarse noncanonical flash plan is 558,796 bytes with SHA-256
`5c3629f259af83752a28e7da1e776fec80d5257f888303ae3effb52b6f00e013`
and 783 placed regions. Validation remained offline; nothing was flashed.

## Prior authenticated upstream LZ4 production release

The source profile now builds the maintained decompressor from the
authenticated upstream LZ4 v1.10.0 snapshot at commit
`ebb370ca83af193212df4dcbadcc5d87bc0de2f0`. Only
`LZ4_decompress_safe`, its 64-byte `inc32table`/`dec64table` read-only-data
closure, a four-byte G2 safe-ABI adapter, and the 30-byte EvenHub mode-2
adapter are active. No compressor, frame API, writable LZ4 state, or other
public LZ4 entry is linked. Selection of v1.10.0 as maintained source does not
identify the stripped stock decoder's exact point release.

| Production artifact | Apple clang 21 | Linux clang 22.1.8 |
|---|---|---|
| Apollo-main overlay | 118,574 bytes / `1a0b92e12203b78f48191969744128bfbcc2559c811ae40a1f393370eceacea9` | 120,450 bytes / `2901320d6169c2b9ad49d501cb25e7f50ceaa90b94e7d0640f80d318932d8fc7` |
| Apollo-main component | 3,641,970 bytes / `6621c7d0403e37d0598c5f2f521633afb13b98034542c8010cf9d210f576e91d` | 3,643,846 bytes / `140cac71e8ec612f2129800ee9a205c30f743dfd51664207c1661fdb337d8f8d` |
| Core-source EVENOTA package | 4,420,424 bytes / `d576be2c4626006a830593a5ad1aae21da8ee3e16d67d80c62eb8f3994bfc294` | 4,422,300 bytes / `cb1516c2c61402626a723f05f4fb315e8af91adae599818830b2f8e1ffee0bf8` |

Apple places the 1,660-byte relocated decoder text at
`[0x007B0B74,0x007B11F0)`, the 64-byte tables at
`[0x007B11F0,0x007B1230)`, the safe adapter at
`[0x007B1230,0x007B1234)`, and mode-2 at
`[0x007B1234,0x007B1252)`. Linux places its 1,690-byte text at
`[0x007B12A8,0x007B1942)`, two alignment bytes at
`[0x007B1942,0x007B1944)`, the tables at
`[0x007B1944,0x007B1984)`, and the adapters at
`[0x007B1984,0x007B1988)` and `[0x007B1988,0x007B19A6)`.

The prior hand decoder and mode-2 caller remain in their original primary
overlay positions under `_legacy` names and are unreachable; keeping those
sections avoids shifting hundreds of established functions. The stock safe
entry `0x0054F338` and mode-2 entry `0x004E0C0C` now redirect to the active
adapters. The stock generic decoder and variable-length reader remain opaque,
unreachable compatibility bytes. A whole-image branch and byte-granular
even/Thumb pointer audit found no hidden route into those bodies.

The upstream decoder retains two explicit opaque EABI dependencies:
`__aeabi_memcpy` at `0x00439BE4` and `__aeabi_memmove` at `0x00439710`.
Their complete 166-byte and 150-byte stock spans are hash-pinned and audited,
including `memmove`'s backward-copy returns and non-linking tail branch to
`memcpy`. They are void EABI providers; no C return value is assumed.

The adjacent IAR/DLIB census now also identifies a 28-byte hardware-VFP
`sqrtf`, 14-byte EDOM setter, 18-byte ERANGE setter, 12-byte errno-address
accessor, and 16-byte errno literal/alignment island. Lorelei Ghidra and local
Rizin independently classified the boundaries; the local fail-closed analyzer
authenticates their bytes and ingress topology. These remain retained stock
runtime, and the exact EWARM 9.x release is still unproven.

The follow-on [IAR memory-provider candidate](docs/research/iar-runtime-memory-source-candidate.md)
adds relocation-free public/aligned memcpy and memmove source entries. Their
exact Thumb sections passed 6,000 randomized Unicorn vectors on Lorelei;
production replacement awaits the recorded performance and overlapping-region
patch gates.

Canonical component accounting is 118,756 source-owned bytes, 82,478
generated patch bytes, 82,660 replaced-stock bytes, 3,440,704 opaque base
bytes, and a 32-byte generated wrapper. Canonical package ownership is
119,370 source, 84,277 generated, and 4,216,777 opaque bytes. This work was
built, inspected, and tested offline. No hardware was flashed or executed.

## Prior FreeRTOS queue/task closure release

That production milestone reused three more functions from authenticated
FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c`: `xTaskRemoveFromEventList`,
`xQueueGiveFromISR`, and `prvTaskCheckFreeStackSpace`. Focused disassembly is
limited to the G2-specific queue/list/TCB/global bindings and the recovered
stack policy (`0xA5`, downward growth, four-byte `StackType_t`, 16-bit
`configSTACK_DEPTH_TYPE`). Their complete stock spans are 246, 200, and 22
bytes at `[0x00455370,0x00455466)`, `[0x00441A42,0x00441B0A)`, and
`[0x00455820,0x00455836)`.

Apple places one two-byte alignment region followed by the three source leaves
at `[0x007B1254,0x007B132C)`, `[0x007B132C,0x007B1400)`, and
`[0x007B1400,0x007B143E)`. Linux uses the same order at
`[0x007B19A8,0x007B1A80)`, `[0x007B1A80,0x007B1B54)`, and
`[0x007B1B54,0x007B1B92)`. The queue leaf's only intra-translation-unit call
is an exact pinned `R_ARM_THM_CALL` to the selected task-removal leaf.

| Production artifact | Apple clang 21 | Linux clang 22.1.8 |
|---|---|---|
| Apollo-main overlay | 119,066 / `da056ac28814f1b07c90d3651b290cd459bfde5e3cbcf30fed9a75a72729a0ae` | 120,942 / `8d56bdf484f3b1d67378f53eef89d7aea88282c6d552b8b2b1ee2bb7e0cb6905` |
| Apollo-main component | 3,642,462 / `0081322ddf2222bc8f6ab3848fab05cec68f39e999ec2e6e11bca6bb7bd3293d` | 3,644,338 / `9532d9051a424453fda38d383aa303e4783c9832430d816554e2c861ea7afac0` |
| Core-source package | 4,420,916 / `1b3ea44cc1cbd8004585e0208e33605c4e5f59229fdc5cb23395d19e0ba120f2` | 4,422,792 / `b93b39eb8e6f70e144b517dd7d770adcea67f62aa1100d722d4d1d0e6f8907ea` |

Canonical component accounting is 119,248 source-owned bytes (182 in place),
82,946 generated patch bytes, 83,128 replaced-stock bytes, 3,440,236 opaque
bytes, and 32 wrapper bytes. Canonical package ownership is 119,860 source,
84,747 generated, and 4,216,309 opaque bytes. Its 630,636-byte flash plan
hashes to
`654dbb2504c20714cec9ef91a20553c238b64c4e583c6dd1d09a59c29e49a9c5`
and records 875 placed, two unresolved, and five container-only regions.

The exact-root Linux profile was reproduced by a recording pass and two normal
fail-closed builds. Its 563,117-byte coarse flash plan hashes to
`9ba2fe6f12dd487cb07ae8e1fa38cabf8320d8bd399283acb7e0bf125c0c03bb`
and records 789 placed, two unresolved, and five container-only regions.
Linux package ownership is 121,781 source, 84,702 generated, and 4,216,309
opaque bytes. All compilation, assembly, package verification, and testing
were offline; no G2 was flashed, reset, or executed.

## Preceding FreeRTOS timeout-check release

The production profile now also reuses the exact FreeRTOS-Kernel V10.5.1
`xTaskCheckForTimeOut` algorithm from authenticated commit
`def7d2df2b0506d3d249334974f51e427c17a41c`. Its complete 128-byte stock
span `[0x00455566,0x004555E6)` is replaced by one generated entry redirect
and NOP fill. Focused disassembly supplies only the G2-specific configuration
and bindings: `INCLUDE_vTaskSuspend=1`, `INCLUDE_xTaskAbortDelay=0`,
32-bit ticks with `portMAX_DELAY=UINT32_MAX`, the eight-byte `TimeOut_t`
layout, the tick and overflow words at `0x20074A34` and `0x20074A48`, and the
already source-owned critical-section and internal-timeout providers.

Apple clang 21 places a two-byte alignment region at
`[0x007B143E,0x007B1440)` and the relocation-free 136-byte source leaf at
`[0x007B1440,0x007B14C8)`. Homebrew clang 22.1.8 places the corresponding
regions at `[0x007B1B92,0x007B1B94)` and
`[0x007B1B94,0x007B1C1C)`. The profile-specific function SHA-256 values are
`33f0782fa8af468bccf78b558cc010a9f7a89f30c7c76abced9a799feb6a93f5`
and
`486515dfdbdb1e175321445df167dca27357f270421b2d00492268e8da7c815c`.

The canonical Apple overlay/component/package are 119,204, 3,642,600, and
4,421,054 bytes. Their SHA-256 values are
`4b3071e64d0e183efbb59788c94dca8ae01fba6d952aecbb9682893844171a79`,
`eaa59756edb47e85be46959cb2242200f51bc4a3acaea1fc4365ee1f6a59e152`,
and
`4fb13f64e81b8a6ef9bdf784ac38d5fc08ed03e4d310601a48bf4b395c20ab37`.
The canonical flash plan is 632,134 bytes with SHA-256
`98b8c544328ac3cecaa00c1bc15f4fb7958b9c26e2b0433852864eeec66cd86a`;
the package report is 2,322 bytes with SHA-256
`61013f4dd6a8811fdbc275a744125e0b30694398b9e80da72d678a33c9dc6179`;
and `SHA256SUMS` is 118,243 bytes with SHA-256
`5adb3bfd414cc0e65d2db8ef5193ae31e35e7f4b452d04a4768fccf98c771085`.
The manifest contains 821 Apollo-main regions and 884 whole-package regions;
the flash plan records 877 placed, two unresolved, and five container-only
regions. Canonical component accounting is 119,386 source-owned bytes (182
in place), 83,074 generated patch bytes, 83,256 replaced-stock bytes,
3,440,108 opaque bytes, and 32 wrapper bytes. Package ownership is 119,996
source, 84,877 generated, and 4,216,181 opaque bytes.

The reviewed Linux overlay and component are 121,080 and 3,644,476 bytes,
with SHA-256 values
`75054c31d8ca3e50659443c470f11a604fb715db430e08b3ad4c468042282324`
and
`29c48306a2f8fab7b87af6c90b38786e4ee36d19f9eb68122614df4b355472ce`.
Its component accounts for 121,262 source-owned bytes (182 in place), 83,240
generated patch bytes, 83,422 replaced-stock bytes, 3,439,942 opaque bytes,
and 32 wrapper bytes; package ownership is 121,917 source, 84,832 generated,
and 4,216,181 opaque bytes. Exact package and auxiliary Linux hashes are
recorded in [`docs/linux-reproducible-build.md`](docs/linux-reproducible-build.md);
the package SHA-256 is
`22c0e367882b005c1b85ee40d138e596c423d5a6335b8d93bc5a68873323c3ab`.

This is an offline structural and reproducibility result. No physical G2,
serial endpoint, debugger, signing service, flasher, reset, boot, or runtime
execution was used.

## Prior EasyLogger output/async source tranche

The production profile now source-owns the authenticated-upstream-derived
`elog_output` algorithm and the clean-room G2 asynchronous submit and stock-
compatible record-builder glue. Exact redirects replace 1,026 bytes at
`0x0043D574`, 132 bytes at `0x00448D4E`, and 24 bytes at `0x0044AA80`.
This tranche initially selected stock's observed enqueue-failure double
recycle. The corrected single-owner implementation supersedes it in the
current production overlay described below.

Apple's overlay/component/package are 121,298, 3,644,694, and 4,423,148 bytes,
hashing to
`02bfc227db4ad32c51303ea0dc49f908b277b78db1f2e5d7a5108559d863b249`,
`eecf209bf4df5f61252099b16fb0a17f4493ec5db3c29eb266d07e6cf64d956b`,
and `2b1008c2fc533f1257ee58bd6d0c08b449d2e12bc57d918f101586ba1d3e3d29`.
Exact-root Linux produces 123,170, 3,646,566, and 4,425,020 bytes, hashing to
`36479ef84126bc0075a2bcfa93c86591376eb4f18eb32983f84865f9d51e72e9`,
`43d02017caa63a2bbe96e7dda056fa61009abcdb2913a12b2298dde131eb0a9c`,
and `12386dc6f165053c3a308b4ec64bf2df90becf2b793a2404830a598b62b7a33d`.
Both profiles reproduced byte-identically twice. No hardware was operated.

## Preceding FreeRTOS semaphore-take source tranche

The production `xQueueSemaphoreTake` redirect now targets the authenticated
FreeRTOS-Kernel V10.5.1 source leaf and resolves its only relocation to an
appended source implementation of `prvGetDisinheritPriorityAfterTimeout`.
The guarded legacy body remains available only to host regression fixtures.
Assembled-image scans prove the retained stock helper has no remaining branch
or stored-pointer reference. Apple produces a 121,330-byte overlay,
3,644,726-byte component, and 4,423,180-byte package; exact-root Linux produces
123,184, 3,646,580, and 4,425,034 bytes. Package SHA-256 values are
`74278f0c7ae44e5364a6bca3abc762fcb48a0b2dcb06d816412566c5e974541d`
and `b07ee2e813356553bd5c8f0a7c2f951376f8b338be6e53b6aff75824062f47f1`.
No signing, flashing, reset, or hardware operation was performed.

## Preceding FreeRTOS queue-reset and unordered-removal source tranche

The Apollo-main overlay now production-integrates authenticated
FreeRTOS-Kernel V10.5.1 `xQueueGenericReset` and
`vTaskRemoveFromUnorderedEventList`. Their complete official spans are
`[0x00441516,0x004415CA)` (180 bytes) and
`[0x0045547C,0x00455556)` (218 bytes). Each original entry contains a
full-span `B.W` redirect followed only by NOP fill; both appended leaves are
relocation-free.

Apple places a two-byte alignment region at overlay offset 121,330, the
172-byte reset leaf at 121,332, and the 214-byte unordered-removal leaf at
121,504. Exact-root Linux places its 174-byte reset leaf at 123,184, two
alignment bytes at 123,358, and its 210-byte unordered-removal leaf at
123,360.

| Profile | Overlay | Apollo-main component | Core-source package |
|---|---|---|---|
| Apple Clang 21.0.0 | 121,718 / `76e21a06d75ed5c3beb5343014621e432726ea285e46d54978a4de43d9b6b666` | 3,645,114 / `c32ff5c5daf946812df503cfaa328c1cc22dc4206201da0b752a365f235e0108` | 4,423,568 / `0e18c7c435edaff3fa5b692e8c17251f075c472933c93b05153ac0307e6f4ca8` |
| exact-root Linux Clang 22.1.8 | 123,570 / `6885adb2da4019a5595fd14fefe7e6682e6d32e63b45c47b3436828a1238d288` | 3,646,966 / `657140490b0bd0b1f5aeb44505cc24b01377d16254f91c30e31893d1890731ca` | 4,425,420 / `d7870c13b9417f8a9866ad6b87858e712c1c6c005b0b534bdd1d4ba540b64d60` |

The canonical package partitions into 122,500 source, 86,467 generated, and
4,214,601 opaque bytes; Linux partitions into 124,409 source, 86,410
generated, and the same 4,214,601 opaque bytes. Validation was offline; no
firmware was signed or flashed and no G2 hardware was operated.

## Preceding corrected single-owner EasyLogger builder

The production redirect for the complete official builder entry
`[0x00448D4E,0x00448DD2)` now targets
`open_cfw_g2_easylogger_async_record_build_single_owner`. The corrected
builder preserves the stock ready/input checks, default metadata, 255-byte
clamp, record layout, allocation, enqueue, diagnostic, and always-zero return,
but performs exactly one recycle after enqueue failure. The stock-compatible
double-recycle implementation remains available only to host/audit tests.
Allocator, enqueue, and diagnostic providers remain reviewed binary seams;
the enqueue relocation is allowed only by the pinned consuming-ownership
contract. There is no recycle symbol or relocation in either production
closure, and the stock caller topology is unchanged.

| Profile | Overlay | Apollo-main component | Core-source package |
|---|---|---|---|
| Apple Clang 21.0.0 | 121,706 / `03dd692b55204fc36f67469ece0175e981b6281123a1b20b3db592ee2dd0b44c` | 3,645,102 / `ae123c6a119bfebd0420898aef590a9ba1fd7f7dc7da00b3d347f6573bba43ec` | 4,423,556 / `7cf86c7311b4684eb6d2fdd4f832989317c858733f8438dc01ee649fcd1cf250` |
| exact-root Linux Clang 22.1.8 | 123,558 / `f2c33def6131981c1a283968bc02bd55cde32536f4f33a7fa3cbf905d42693fc` | 3,646,954 / `5ff7dd5894b74573971912371f22d0b463c32552ea1037441e1de992a6a8d3b9` | 4,425,408 / `fe49c0d9830327a0fdd0e7815a147bb6b810e27b9a9277b3bbfe9021de247a75` |

The Apple package partitions into 122,488 source, 86,467 generated, and
4,214,601 opaque bytes; exact-root Linux partitions into 124,397 source,
86,410 generated, and the same 4,214,601 opaque bytes. All work remains
offline; no firmware was signed or flashed and no G2 hardware was operated.

## Preceding production EasyLogger hexdump tranche

Apollo main now source-owns authenticated `elog_hexdump`, its two-argument
raw-submit wrapper, and its level-less record builder. Full-span `B.W` plus
NOP-fill replacements cover `[0x0043DACC,0x0043DC88)`,
`[0x00448CCC,0x00448D4E)`, and `[0x0044AA76,0x0044AA80)`. The latter
two end exactly at the existing level-aware builder and formatted-submit
entries. Ten strict leaves preserve the 41/1/1 stock caller topology and the
hexdump literal pool.

The main function is derived from authenticated EasyLogger under MIT; bounded
formatters and the G2 transport adapter are clean-room GPL-3.0-only code.
Independent leaves use arithmetic uppercase conversion instead of sharing
unowned digit-table rodata. The raw route leaves record byte `+0x0C`
untouched and has no recycler, event-set, level-aware, or formatted-submit
route. Its enqueue dependency is consuming.

| Profile | Overlay | Apollo-main component | Core-source package |
|---|---|---|---|
| Apple Clang 21.0.0 | 123,197 / `bb870969ad9913e2cc4f012c0abec05b5a946bfbcaff4ab3cf7d7ac3b1e08966` | 3,646,593 / `24bb10715c6650429bcdbe0b2942f8b1a16ddd9b2f6aa2a65a69361df2611c7f` | 4,425,047 / `24d4b6527621c87622a5fdee96c63d266f10c3452e0a52322386ad717084b81c` |
| exact-root Linux Clang 22.1.8 | 125,023 / `47f588845f4bd202d1d184282996cf45dd2cb514b4795ac9cdd5a7835da90d02` | 3,648,419 / `df9a1b00038d07ea0137258cc879547ecc86a11a737d1954bd1f4babd259c8e3` | 4,426,873 / `2eef6375f1ac218701f438afd8f5b5752b789a20db1e73f6dfd71486acc94423` |

The canonical package accounts for 123,979 source, 87,051 generated, and
4,214,017 opaque bytes. Exact-root Linux accounts for 125,862 source, 86,994
generated, and the same 4,214,017 opaque bytes. The manifest has 864
Apollo-main regions; Apple exposes 625 functions and 581 patch sites. The
dedicated production suite executes all 256 byte-format values and boundary
cases, checks exact stock topology and relocation closure, and verifies
literal/NOP preservation. Qualification was offline; no image was signed or
flashed and no hardware was operated.

## Preceding bounded CmBacktrace production reuse

The complete CmBacktrace current-thread-name helper at
`[0x00593AF6,0x00593AFE)` is now a source replacement. A 4-byte MIT-licensed
compatibility leaf selected against authenticated commit `73714489` tail-
branches to a separate 14-byte recovered G2 adapter. The adapter preserves the
current-TCB load at `0x20074A20`, task-name offset `0x34`, and null-to-`0x34`
behavior. The snapshot and independently named candidate remain excluded from
production.

Apple Clang produces 123,620 / 3,647,016 / 4,425,470-byte overlay, component,
and package artifacts. Exact-root Linux Clang produces 125,440 / 3,648,836 /
4,427,290 bytes. The canonical manifest now has 881 Apollo-main regions and
the config registers 634 functions, 589 patches, and 65 relocated leaves;
Apple-effective output is 630/585/61. All work was offline; nothing was signed,
flashed, or executed on hardware.

## Prior phase-local bounded nanopb production reuse

The core-source profile now replaces the complete 112-byte
nanopb-compatible `pb_decode_varint` entry at
`[0x0048F5B8,0x0048F628)` with an altered Zlib-licensed source leaf. The
authenticated nanopb 0.4.9 snapshot is explicitly a compatibility baseline,
not proof of the vendor point release. Production binds only the recovered
stream ABI and reviewed stock `pb_readbyte` seam at `0x0048F454`; the broader
pristine nanopb runtime remains unregistered. The independently named
candidate stays outside every production registration.

Apple Clang 21.0.0 produces a 123,600-byte overlay, 3,646,996-byte component,
and 4,425,450-byte package, with package SHA-256
`cdbc1c41607d4623625ce25d0757457c72c550915c60d4b5ab7077c5760d0812`.
Exact-root Linux Clang 22.1.8 produces 125,420 / 3,648,816 / 4,427,270 bytes,
with package SHA-256
`81729530e02fc666dfdef831933b44ec74e45bc3412c81d7c1161e03a5055152`.
The focused production gate checks upstream/candidate/production behavior,
both compiler objects and relocations, exact entry replacement, whole-image
branch and byte-granular pointer ingress, and exact manifest ownership. No
firmware was signed or flashed and no G2 hardware was operated.

## Preceding FreeRTOS+CLI parameter-accessor-only tranche

This phase first redirected the complete authenticated
`FreeRTOS_CLIGetParameter` span `[0x005848FC,0x00584960)` to a separate
production source adaptation of the MIT FreeRTOS+CLI V1.0.4-compatible
algorithm. The 100-byte stock entry is replaced by one `B.W` followed by 48
Thumb NOPs. A two-byte source-owned fragment also changes the console
collector comparison at `0x00541708` from 128 to 127, reserving the last byte
of its 128-byte input array for NUL. The qualified candidate remains present
as an independently named, production-excluded oracle; production never
registers its filename or symbol.

The artifact and placement values in this subsection are phase-local. The
subsequent complete-console tranche retains the accessor but removes the
capacity fragment and repins the combined artifacts.

Both profiles extract the accessor as the same 252-byte, four-byte-aligned,
relocation-free leaf and the capacity fragment as the same two-byte,
two-byte-aligned leaf. Apple places them at
`[0x007B2464,0x007B2560)` and `[0x007B2560,0x007B2562)`; exact-root Linux
places them at `[0x007B2B84,0x007B2C80)` and
`[0x007B2C80,0x007B2C82)`. Whole-component ingress scanning permits exactly
the stock-entry `B.W` into the accessor, rejects branches or stored pointers
to its interior, and requires zero ingress to the copied capacity fragment.

| Profile | Overlay | Apollo-main component | Core-source package |
|---|---|---|---|
| Apple Clang 21.0.0 | 123,454 / `9e5004af49fb14a22e7e7ed7357e4c10f87dc8da3a7fb4d7b97fcffcde804c43` | 3,646,850 / `8722e5565bf54dade66fb751155c11ebd128d7a12853e3e4b8671c3c97807827` | 4,425,304 / `f2688fb35061283c05e9eb165d4f3eeb2cb2c4abd18cd28d074e58cb9da021db` |
| exact-root Linux Clang 22.1.8 | 125,278 / `a0a520069e497613b397af1d7327752201ced44c876d6925a7561ae45c91fa7c` | 3,648,674 / `8c477d28a9f58feaf722bd1e00b9767a8ca745ba618515d46339271cd0288c1a` | 4,427,128 / `5598cb1f2a3b9a8b6101f61afcc5e24de54b01c3d5aa45396bf161344b3618bb` |

Exact manifest ownership partitions the Apple package into 124,236 source,
87,305 generated, and 4,213,763 opaque bytes. Exact-root Linux partitions into
126,117 source, 87,248 generated, and the same 4,213,763 opaque bytes. The
coarser Apple flash-plan accounting is 124,221 source, 87,168 generated, and
4,213,915 opaque bytes. The Apollo-main manifest tiles 871 regions exactly.
Cross-profile overlay configuration registers 631 functions and 587 patches;
the Apple-effective build report emits 627/583 and Linux emits 631/587 because
four CRC/TinyFrame leaves are Linux-profile-only. Qualification was compile,
assembly, packaging, and offline analysis only. No firmware was signed or
flashed and no hardware was operated.

## Prior phase-local complete FreeRTOS+CLI console-task tranche

Apollo main now redirects the complete 284-byte command-console task at
`[0x00541600,0x0054171C)` to seven independently placed GPL-3.0-only
clean-room source leaves. The production closure owns G2-specific fill,
state-initialization, ordered registration, command-processing, byte-consume,
receive-once, and task-entry glue. It deliberately retains the stock
`FreeRTOS_CLIProcessCommand` ABI and all 22 proprietary setup groups / 76
command descriptors; it does not attribute that first-party glue to upstream
FreeRTOS-Plus-CLI.

The initializer's authenticated Thumb pointer at `0x0054178C` remains
unchanged and continues to enter the original task address, whose first
instruction is now the generated redirect. The source task preserves the
128-byte interpreter call boundary while limiting accepted payload to 127
bytes so the final byte remains NUL. It also consumes input only when the
retained ring read returns exactly one byte, avoiding the stock stale/undefined
stack-byte path. This complete replacement supersedes and removes the earlier
two-byte collector-capacity patch and its appended leaf.

The authenticated MIT FreeRTOS-Plus-CLI snapshot and independently named
whole-task candidate remain production-excluded. Snapshot commit `43defa56`
is an openCFW compatibility baseline, not a claim about Even Realities'
historical checkout. The earlier nanopb and CmBacktrace production leaves are
compactly repinned without widening their source or provenance boundaries.

The canonical Apple build produces a 124,212-byte overlay with SHA-256
`913d0b39126eac6d13ac05baa44c745cd2a0c7317957293e34bbf418547d96bd`,
a 3,647,608-byte Apollo-main component with SHA-256
`cbe9f7361b47ef2150f2c3a01fca6f03f82e1ff3e2c805b7bbe774ba2154a354`,
and a 4,426,062-byte core-source package with SHA-256
`0c257168dfc07a39e4603847329f6ac542d093719f0ea9c5a4cf904707b83670`.
Its 890-region Apollo-main manifest exactly tiles the component, and the
cross-profile overlay configuration registers 640 functions, 589 patch sites,
and 71 relocated leaves. Exact canonical package ownership is 124,987 source,
87,714 generated, and 4,213,361 opaque bytes.

Exact-root Linux Clang produces a 126,032-byte overlay with SHA-256
`bdc8bf69d75b7ff8354e12aa392416956a2afa04442488e7653e79b89ce62f1f`,
a 3,649,428-byte component with SHA-256
`d90824df529385ae5fba464c88b0c1e4e7d145a939024632c0806c4462d68d00`,
and a 4,427,882-byte package with SHA-256
`3aa279193bf67b50a75ad5490a8cd2e22ffb32d36f6de1e5befe0a11368fe743`.
Two ordinary exact-root builds reproduce the recorded component and package.
Exact Linux package ownership is 126,868 source, 87,653 generated, and
4,213,361 opaque bytes.

All qualification remains offline; no image was signed or flashed and no G2
hardware was operated.

## Prior phase-local FreeRTOS queue-message-count accessor tranche

Apollo main now replaces the complete official FreeRTOS
`uxQueueMessagesWaiting` and `uxQueueMessagesWaitingFromISR` spans at
`[0x00441E66,0x00441E8A)` and `[0x00441E8A,0x00441EA2)` with generated
entry redirects and Thumb NOP fill. Two separately compiled MIT-licensed
FreeRTOS-Kernel V10.5.1 adaptations preserve the recovered G2 AAPCS32 queue
ABI, including the volatile message count at `Queue_t + 0x38`, task-context
critical-section ordering, and ISR direct-load behavior. All six authenticated
CMSIS callers remain unchanged and reach the original entries.

Both compiler profiles emit identical 50-byte task and 34-byte ISR leaves,
with SHA-256 values
`fd95750405881458902725fe3e29d72367bcfe3a723a05588c74337b55202f04`
and
`38774f1d59f2cd201929d20c3370e12e167d24866477e5a661220bca25db834c`.
Apple places them at `0x007B2858` / `0x007B288C`; exact-root Linux uses
`0x007B2F74` / `0x007B2FA8`. The only intervening bytes are two generated
alignment zeros.

| Profile | Overlay | Apollo-main component | Core-source package |
|---|---|---|---|
| Apple Clang 21.0.0 | 124,298 / `09c6c86c38a88905ea389eb9c2c860d6a2e559f435d225b02bb5bdc313e828d4` | 3,647,694 / `7cc8f0b58808628e930762856ba896f5b3d9bf346fd3a5ec2e50b3a46fb6cba4` | 4,426,148 / `7209ad9da1b65c4e0c988a4af43885dc8ecf8822e26117ef047b6908d316829f` |
| exact-root Linux Clang 22.1.8 | 126,118 / `db4f80dd7caa313de96580ce10050cba2ad07bc0b7495bbc3f122a29bf9dfefa` | 3,649,514 / `45ee630ef534a524d8f8dab01af2c38412f0fa9394e7a94d0ff4f781730465c2` | 4,427,968 / `44a43f3cb4d9e36acb9ab7c1064403a9786f6657f7f6a629dfd639db7e1aacc3` |

The cross-profile config now registers 642 functions, 591 patch sites, and 73
relocated leaves. The 895-region canonical Apollo-main census is container
1/32, alignment 40/80, entry replacement 577/85,626, exact load 1/6, exact
replacement 7/134, official 177/3,437,380, and source 92/124,436. The
preceding console table is retained as a phase-local historical pin. Full
source, stock, ABI, caller, patch, and toolchain evidence is in
`docs/research/freertos-queue-messages-waiting-source-audit.md`. Qualification
was offline; no firmware was signed or flashed and no hardware was operated.

## Prior phase-local nanopb `pb_skip_varint` production tranche

Apollo main now replaces the complete 36-byte nanopb-compatible
`pb_skip_varint` body at `[0x0048F628,0x0048F64C)` with a generated `B.W`
and sixteen Thumb NOPs. The new Zlib-licensed source leaf is selected against
authenticated nanopb 0.4.9 commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824` and binds its sole call seam to
reviewed stock `pb_read` at `0x0048F3BE`. The selected release is a
compatibility baseline within the authenticated pristine 0.4.7–0.4.9 range,
not proof of Even Realities' historical nanopb revision.

The sole stock caller at `0x0048F6B6` remains unchanged. Both toolchains
produce the same 932-byte object and 36-byte unrelocated text, with SHA-256
values
`651b45c3291a106f6e930129db85af7bbcba416f9ccc260f87b4d5a417eb53d4`
and
`7e2f6a8b3dca56e4c2d0499a6d4f12ad97dc4bc7f127ff6f4c31b8d379f0ba3b`.
Apple places the leaf at `0x007B28B0`; exact-root Linux uses `0x007B2FCC`.

| Profile | Overlay | Apollo-main component | Core-source package |
|---|---|---|---|
| Apple Clang 21.0.0 | 124,336 / `97c57c110eb7b5fb7474bf945f35121432dfd713c02fcd47931da699c1da739a` | 3,647,732 / `6f58d53a7f747ef8e9f701d01eb9fe1364dd3770df23aed58d9d6f0e7f743d99` | 4,426,186 / `21becb0b47e98f4bb50a296f4e9211a8b43ee57645e0c84e6d2053a15c5340ec` |
| exact-root Linux Clang 22.1.8 | 126,156 / `e7f3d94e8a7253f761c5d535dba918b765c9f3f2aba82a5cdc5372bd0ebf9d62` | 3,649,552 / `160c431d1ff7ea9bd941583705fd2ebfb9cb6b7037298bf3d0bd8f2bd72dbd71` | 4,428,006 / `44adc5125db5e459bc0e32f258a02fbf2f564f8f4f739b542d7406741c046ab1` |

The config census is 643 functions, 592 patch sites, and 74 relocated leaves.
The 898-region canonical Apollo-main census is container 1/32, alignment
41/82, entry replacement 578/85,662, exact load 1/6, exact replacement 7/134,
official 177/3,437,344, and source 93/124,472. Exact package ownership is
125,107 / 87,814 / 4,213,265 source/generated/opaque bytes for Apple and
126,988 / 87,753 / 4,213,265 for Linux. The preceding queue-accessor table is
retained as phase-local provenance. Full evidence is in
`docs/research/nanopb-skip-varint-source-audit.md`. Qualification was offline;
no firmware was signed or flashed and no hardware was operated.

## Preceding littlefs `lfs_file_size_` production tranche

Apollo main now replaces the complete 24-byte private littlefs
`lfs_file_size_` body at `[0x004CE472,0x004CE48A)` with a generated `B.W`
and ten Thumb NOPs. The bounded BSD-3-Clause source is reused from the
authenticated littlefs v2.10.1 source-equivalent snapshot at commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`. It preserves the recovered
`lfs_file_t` ABI and writing-state maximum; its sole relocation closes directly
over the already source-owned `open_cfw_littlefs_util_max`. Both stock callers
remain unchanged, and whole-image scans find no alternate or interior ingress.

| Profile | Overlay | Apollo-main component | Core-source package |
|---|---|---|---|
| Apple Clang 21.0.0 | 124,356 / `ab16010088fc71b58ed32c7bf28867900301bd92baa871a441f18fdf10ee0b1a` | 3,647,752 / `43ad32acb3e6a09dde1d47681803400da2b7ecead348f60ae08443d2565fcc88` | 4,426,206 / `51f840accc7663cee93764068da124231ea1e26cafb2f135a43b74ca5c247040` |
| exact-root Linux Clang 22.1.8 | 126,176 / `45ddc376dc3943a1b2aaff981566cbd55a89197ddfe65ac368cedd6f607b4fd3` | 3,649,572 / `d8ae148bbb44df20a66fef2815ed2276d7bf1608a11ed833c44260e4178da4fb` | 4,428,026 / `dba4d48dccef97ad4b1559f239553b467632f6a546e0ec908977ea395b13f9b7` |

The config census is 644 functions, 593 patch sites, and 75 relocated leaves.
The canonical 901-region Apollo-main manifest is container 1/32, alignment
41/82, source-entry replacement 579/85,686, exact load 1/6, exact replacement
7/134, official 178/3,437,320, and source 94/124,492. Exact canonical package
ownership is 125,127 source, 87,838 generated, and 4,213,241 opaque bytes.

The 688,384-byte Apple flash plan hashes to
`c828571c91eb6eacd42a9ba17c7ae95c9c280f1169bedddbe9266216da403fb9`
and has 957 placed, two unresolved, and five container-only records; its coarse
ownership is 125,112/87,701/4,213,393. The 580,508-byte Linux plan hashes to
`a052ade1c8d9153a6f9fb14db33ba14dab1c42c5eca84b67c4446c7efaad1da6`
and has 813 placed, two unresolved, and five container-only records; its coarse
package-envelope view is 127,017/87,616/4,213,393. The preceding nanopb and
queue figures remain phase-local provenance. This source reuse does not add a
G2 block-device port or authorize filesystem format, erase, or other hardware
mutation. Qualification was offline; no firmware was signed or flashed and no
hardware was operated.

## Preceding FreeRTOS `prvInitialiseTaskLists` production tranche

Apollo main now replaces the complete 84-byte FreeRTOS
`prvInitialiseTaskLists` body at `[0x0045568C,0x004556E0)` with
`replace_freertos_task_lists_initialize`, a generated `B.W` and forty Thumb
NOPs targeting `open_cfw_freertos_task_lists_initialize`. The sole stock
caller at `0x00454A20` remains unchanged. The bounded MIT source is adapted
from authenticated FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c`; its six strict call relocations
bind directly to source-owned `open_cfw_freertos_list_initialise`.

Both reviewed compilers emit the same 88-byte unrelocated leaf, SHA-256
`6710533445c9aac3904152a43147d0e9ba9bec7eff8e7c5c6b72007c4c301fdb`.
Apple places it at `[0x007B28E8,0x007B2940)`; exact-root Linux places it at
`[0x007B3004,0x007B305C)`. The source and header are 3,529 and 5,886 bytes,
hashing to
`58773452256b0f44647040085bbcc7a896a1cbd3efd0c5c4b4de3ddfe1a9e857`
and
`6fe827f6d2659a784e8b3e22fa096162dfd4003146c0425222efc92c63baef9e`.

| Profile | Overlay | Apollo-main component | Core-source package |
|---|---|---|---|
| Apple Clang 21.0.0 | 124,444 / `34c6d23ea9e1c3f01440222e44fe2af38121a02309b61efb2b15a806e0e77158` | 3,647,840 / `fd4625c32ee413abe058ffabc6a719be7af0af3d0096ce4f06b8535f01463b8b` | 4,426,294 / `188702b9f1b8c52e3ea46f33765bd9555395dd3ada0aa1233503930b0e594c97` |
| exact-root Linux Clang 22.1.8 | 126,264 / `62d8e21bec02a7505a39296f2e474e703b6a3989c252c6cda3fda43e12e7d236` | 3,649,660 / `5a098690012093defe0573e7f5c4cfb20ae79f77ff3aa88ce6adda3279c73764` | 4,428,114 / `0c446de88f84b8b81049b54efc94e0c40b411bfc9b2c8655cbf5b762bb846068` |

The config census is 645 functions, 594 patch sites, and 76 relocated leaves.
The canonical 904-region Apple manifest exactly tiles the component and yields
125,215 source, 87,922 generated, and 4,213,157 opaque package bytes. The
preceding littlefs, nanopb, and queue figures remain phase-local. The separate
bootloader homolog is not patched. Qualification was offline; nothing was
signed, flashed, or executed on hardware.

## Preceding nanopb `pb_close_string_substream` production tranche

Apollo main now replaces the complete 42-byte stock
`pb_close_string_substream` body at `[0x0048F7CA,0x0048F7F4)` (SHA-256
`439bbeecb6a0b8266dc3dcd913e98793352b6b346a7a58cdd44322c734621818`)
with a generated full-span `B.W` and Thumb NOP fill. The third bounded nanopb
production leaf implements the exact compatible drain-and-parent-update
semantics selected from the authenticated pristine nanopb 0.4.7–0.4.9 range.
The nanopb 0.4.9 source at commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824` is the explicit compatibility
baseline, not proof of Even Realities' historical nanopb version.

Focused stock disassembly pins all three callers, the 16-byte G2 stream ABI,
the zero-remainder and read-failure/no-parent-copy behavior, and the sole
`pb_read` dependency at `0x0048F3BE`. The 2,061-byte Zlib source and 2,537-byte
header hash to
`736e7ec228f9282ba5b093fd482441e6e2017fff860d989dc3aadb2bdeff0fcb`
and
`851af370162d79f4bd0be8b8bb9a5731d47cf02527078b9e278019340f2d65d4`.
Both reviewed compilers emit the same 36-byte unrelocated text with one strict
call relocation to that stock-read seam.

| Profile | Leaf placement | Overlay | Apollo-main component | Core-source package |
|---|---|---|---|---|
| Apple Clang 21.0.0 | offset 124,444 / `0x007B2940`, relocated `c838be0dfb478fe7fa03d9d71069a200a6477eb5783b631d7d977cd501475438` | 124,480 / `8971dd8fdb8a5f7b703a16dea0c16f27b82739303f18b95fe0b80cf7885252a7` | 3,647,876 / `e416a5d9010c108370505c14b8115d7c9f179ea446fd6888e992c55d6a272ccc` | 4,426,330 / `c7ce9de85bceae301a60a9ef5d5d8d0d7beb62891c661980594de0ac4da22ecb` |
| exact-root Linux Clang 22.1.8 | offset 126,264 / `0x007B305C`, relocated `a90a09f0f98c5b4cf7d885af34c914ae5d492ac7352b5e359ba68ad482cb3044` | 126,300 / `3a565aa2dd24d197e04a669bb11a1b12f39b4c8cc70344c55520c922df4964d9` | 3,649,696 / `1aa883832df0a09e0c540d4c31e93331053f05048baf149c3d5dba7725d19158` | 4,428,150 / `31a7850ca003235912a32e66a31397ccabcc3486b96e7acfde1086acfba3a1f1` |

The finalized config census is 646 functions, 595 patch sites, and 77
relocated leaves. The canonical manifest contains 907 Apollo-main regions,
including 96 source-compiled leaves. Exact Apple package ownership is 125,251
source, 87,964 generated, and 4,213,115 opaque bytes; these precise numbers do
not imply that all retained firmware is source-authenticated. Qualification
was offline only; no firmware was signed or flashed and no hardware was
operated.

## Preceding littlefs private file-rewind production tranche

Apollo main now replaces the complete 18-byte private `lfs_file_rewind_`
body at `[0x004CE460,0x004CE472)` (SHA-256
`be02691b2e7339d7dd1d54b31712c3e8563e5a86f4406a469888640fad9435cd`).
The bounded BSD-3-Clause source follows authenticated littlefs v2.10.1 at
commit `0494ce7169f06a734a7bd7585f49a9fa91fa7318`: call the already retained
`lfs_file_seek_` seam with offset zero and `LFS_SEEK_SET`, preserve a negative
error, and normalize every nonnegative result to zero. Focused disassembly
supplies the G2 calling seam and topology: the sole private provider is at
`0x004CE3BC`, the sole direct caller is the public wrapper at `0x004CFC24`,
and whole-image ingress scans find no alternate entry into the stock body.

The 1,239-byte source and 1,743-byte production header hash to
`e6afb5b67671b3219971b19c20290c601568752d814064147f5ccd4118f5acc8`
and
`7430dcd1ad1ea3973d619f2d67d8d8b11a688018d48a3bc26a40e407d1fedb56`.
Both reviewed compilers emit the same 16-byte unrelocated text, SHA-256
`46e8bab056ad39ced45edb5da2612f6470674ab5a428df7f08822f6c2d9e184b`,
with one strict call relocation to the stock seek seam.

| Profile | Leaf placement | Overlay | Apollo-main component | Core-source package |
|---|---|---|---|---|
| Apple Clang 21.0.0 | offset 124,480 / `0x007B2964`, relocated `1c2e2b1fded0de515345b90fe34de51a9c0f08a02a5ad983c1120481c51c5783` | 124,496 / `9bda155bad5546bfd970b01cb565ba6dac18d4b624a9cd45bc3167cbf1793eca` | 3,647,892 / `d9b009619108909ca326319f37be94a7b90c8a7523c4650f818f7d85ef1729b3` | 4,426,346 / `aadc9dc907c58708bca95ef91f6ff63e8bb9c6ff898da9a583add8b68fb9ce94` |
| exact-root Linux Clang 22.1.8 | offset 126,300 / `0x007B3080`, relocated `9731cbf3ff15be31186591ed148d009ae8985cb18bdfca3ba365aeb0897e3fd1` | 126,316 / `eea387bf745530cb810166a4779e5b32de9578cdeb41643440a096334113995e` | 3,649,712 / `535f1d7117d36073b8153fea3334cc53c692671da91baca443e3bd82db35851d` | 4,428,166 / `6a08107f4bf3fbfcfa959056f121230488352ab5f1b89a3d2bfb07526c16776a` |

The config census is now 647 functions, 596 patch sites, and 78 relocated
leaves. The canonical 908-region manifest owns 97 source-compiled leaves;
exact Apple package ownership is 125,267 source, 87,982 generated, and
4,213,097 opaque bytes. This qualification is an offline source/build claim,
not a hardware validation: nothing was signed, flashed, erased, or run on a
G2.

## Preceding nanopb `pb_decode_fixed32` production tranche

Apollo main now replaces the complete 28-byte nanopb-compatible
`pb_decode_fixed32` body at `[0x00490190,0x004901AC)` (SHA-256
`1ee27599a8ac5b8d2a0cbaac59986fb49be7b24c348a960a216b8cbbecce5bf3`).
The Zlib-licensed source is selected from authenticated nanopb 0.4.9 commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`; its exact definition is
compatible with pristine 0.4.7, 0.4.8, and 0.4.9. That range is a compatibility
result, not proof of Even Realities' historical nanopb point release.

The 1,975-byte source and 1,750-byte header hash to
`fefd8a899174fb9332c366df691dc2c8ec6f4792f3fd464b65dbb573ace8ee19`
and
`738e4c7d4ea983b0ba967fa42cdcc61cb2e20837531bc6176b7f95a5fe8e2460`.
Both reviewed compilers reproduce the 960-byte object
`499f6ec335b62a6af9a4f2370aaa5ef831a5ec2b3e8da99bcb6f7b8a4e83fedd`
and 50-byte unrelocated text
`798f8f7cbed57f6ba11dad46a6de9d25cb1f1710eb4fa904d79b6fe449952a04`.
Its only executable relocation is one `R_ARM_THM_CALL` at text offset 10 to
reviewed stock `pb_read` at `0x0048F3BE`; this promotion does not make the
read provider source-owned.

| Profile | Leaf placement | Overlay | Apollo-main component | Core-source package |
|---|---|---|---|---|
| Apple Clang 21.0.0 | offset 124,496 / `0x007B2974`, relocated `c9fc88c025ec843fa3ad3f77b4e1bfb84126fd397a81d96c271646eb70632539` | 124,546 / `0b4de390bb5d83501dbe02b64cda88c613220bc03600cb4ddf61d5fe727e0468` | 3,647,942 / `2483965fef5d4500a67342db137d02c88ba15e259e5385ea2e7e03767b8ac909` | 4,426,396 / `91c1e61eac75321487ba275418c7f98753fce56e238a631590f6347b243272cf` |
| exact-root Linux Clang 22.1.8 | offset 126,316 / `0x007B3090`, relocated `53a1961d2df94674da6890611087ab865498084ced6a6f0c6850dcee23c7bf60` | 126,366 / `4e9a1384d9e0de525b5c0cfda765d2dc01fe7e397058cda3a261907446b04ec3` | 3,649,762 / `2469216749e322db7dcaf5e7d0c34c0441f544226771dcc0024442945dc1ca9e` | 4,428,216 / `e09df2c48feea00a281e5a874eb06fc4381403f9d38cafd9f2efff04a8ef6476` |

The config census is 648 functions, 597 patch sites, and 79 relocated leaves.
The canonical 911-region Apollo-main manifest exactly tiles the Apple
component: container 1/32; alignment 41/82; source-entry replacement
583/85,858; exact load 1/6; exact replacement 7/134; official
180/3,437,148; and source compiled 98/124,682. Exact canonical package
ownership is 125,317 source, 88,010 generated, and 4,213,069 opaque bytes.

The Apple flash plan is 695,459 bytes /
`c9bfdf074b8718ce43f33dd41bbbe68577a0c779b22d4e1f33bdc91d2cf9bd0d`
with 967 placed, two unresolved, and five container-only records; Linux is
584,883 bytes /
`96e3339d6740ad96ef15fb0888afb18ddfba958e2324f910e5d6be3f0b5fb633`
with 819/two/five records. Their coarse ownership is respectively
125,302/87,873/4,213,221 and 127,207/87,788/4,213,221.

These fixed32 figures are the preserved phase-local ledger immediately before
the littlefs tag-type promotion. All qualification was offline; no image was
signed or flashed and no G2 hardware was operated.

## Preceding littlefs `lfs_tag_type2` production tranche

Apollo main now replaces the complete eight-byte private `lfs_tag_type2`
helper at `[0x004CAE90,0x004CAE98)`. The bounded BSD-3-Clause source is an
altered scalar-only adaptation of the authenticated littlefs v2.10.1
source-equivalent baseline at commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`. Exactly two stock callers enter
the first halfword, no reviewed ingress reaches the interior, and the source
leaf has no provider, relocation, data, allocator, filesystem-object, or
hardware closure.

Both reviewed compilers emit the same ten-byte text, SHA-256
`88be40d05d37142bf0bae8306026d8c405a4f8f441aabd87ee6731557d4149fd`.
Apple places it at `[0x007B29A8,0x007B29B2)`; exact-root Linux uses
`[0x007B30C4,0x007B30CE)`. The stock entry becomes one profile-specific
`B.W` plus two Thumb NOPs.

| Profile | Overlay | Apollo-main component | Core-source package | Flash plan |
|---|---|---|---|---|
| Apple Clang 21.0.0 | 124,558 / `8dc6206e0a6ed458401de46e5fa60d0a7eebc152eab4032d087fc4e667f7f378` | 3,647,954 / `ec9f098bf69029862df63ff0929f6bbd9c345f540b3565b6cfc7cd71edbc36c4` | 4,426,408 / `f31bef6e0faf8e3655f5c92c385ebe6ee3e7f5ef5635401ceb05cf98089976fe` | 698,204 / `3ac4c2dfdce764389721b2c81f87d6bd0730cfefcdd0cfbe98bf6afa32935bcd` |
| exact-root Linux Clang 22.1.8 | 126,378 / `12ebf0aef9e1ce61c6f5f151515a8c4245b1b353ca921dcddfc6b521cf8f870a` | 3,649,774 / `eeaca07a2c4bec75f4652e9f2853a75ff45684584d5e6074d99d112a41e5ddfc` | 4,428,228 / `caa150eda201d91c8ec6046f5a9017ab87e7ee936fe0f542957bff4efdd4b37f` | 586,282 / `64522f68968b3a063fef934c0304c3d37caaff21b7650aa6d31c10f25e2cbda8` |

The shared config now contains 649 functions, 598 patch sites, and 80
relocated leaves; the Apple build report separately records 645 overlay
functions and 594 generated patch records. The 915 canonical regions classify
container 1/32, alignment 42/84, source-entry replacement 584/85,866, exact load 1/6, exact
replacement 7/134, official 181/3,437,140, and source compiled 99/124,692.
Canonical package ownership is 125,327 source, 88,020 generated, and
4,213,061 opaque bytes. Apple reports 971 placed, two unresolved, and five
container-only plan records; Linux reports 821/two/five. This remains an
offline source/build qualification and does not authorize signing, flashing,
filesystem format or erase, or any G2 hardware operation.

## Preceding dual-image littlefs `lfs_tag_chunk` production tranche

Apollo main and the bootloader now atomically replace their byte-identical
six-byte private `lfs_tag_chunk` bodies at `[0x004CAEA0,0x004CAEA6)` and
`[0x00410BA8,0x00410BAE)`. Each stock entry has exactly four authenticated
direct callers and no reviewed alternate or interior ingress. The generated
replacement in each image is a non-linking Thumb `B.W` plus one NOP, so every
existing caller is preserved while the complete stock leaf is superseded.

The shared 773-byte source and 879-byte header hash to
`71851bd05e26e703b8697b9994b556db46511c37e9500da98e3406b37a92c8da`
and
`1061f5d68ff6f81a6f1853bfefe37b77f5f3b8b09e627b1bfa0d191842d1f6f5`.
They are a bounded altered BSD-3-Clause adaptation of the exact 93-byte
`lfs_tag_chunk` definition in authenticated littlefs v2.10.1 commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`. That commit is a
source-equivalent compatibility baseline, not proof of Even Realities' exact
historical checkout. Both compilers emit the same relocation- and
provider-free six-byte text, SHA-256
`db1dfda72afb267e96cd4e11eaf5d44659195b0afecbdcd8ed8572c34049df74`.

Apple places the Apollo-main leaf at `[0x007B29B4,0x007B29BA)` after two
alignment bytes and the bootloader leaf at `[0x004346E6,0x004346EC)`.
Exact-root Linux uses `[0x007B30D0,0x007B30D6)` for Apollo main and the same
bootloader placement.

| Profile | Apollo-main overlay | Apollo-main component | Boot overlay | Boot component | Core-source package |
|---|---|---|---|---|---|
| Apple Clang 21.0.0 | 124,566 / `0339a938dd13e8b89997cd6e75d7dc56e2300125039304f751b802af1dd73da8` | 3,647,962 / `ac8b3c62d32e849bfd1e71f4950f7ee58d02dc56dd8595c6706a453fe1cf402e` | 628 / `10dce6ad20335a583b4ab2fad4b916ed335d65f126af06b77a935be9702149f6` | 149,228 / `ecfe0087fef4eab3a75f41a2db28d31b3e31c589fdaceec3c209e6e503eb295f` | 4,426,422 / `441bc7dd753518464afa0ac8ab84c26aedcd18228dbab3427d8c20ff66a8d914` |
| exact-root Linux Clang 22.1.8 | 126,386 / `5ebdb04c602ff59241f9d376caa474180f1e9c90ba2ea05581e2b247528b814a` | 3,649,782 / `3ad0a8692694132ce30b266ae8ec4ffb66617de173cb1e3d96ee90335945c70d` | 628 / `e7619c604912ded4b5ac4513287bb68560bba2a09f84cda42dd9f1cf2d080a63` | 149,228 / `64d87f89085988da184b7cf3b9758e702093e35f0e4b2afb6da22971b8532f1b` | 4,428,242 / `8f62cf0ffb7d861ca1e6f9881e3221557f0da4640491489c7468129c5d57f1ba` |

The Apollo-main config census is 650 functions, 599 patch sites, and 81
relocated leaves; the bootloader config is 29/27/10. The canonical manifest
contains 919 Apollo-main and 54 bootloader regions. Exact Apple package
ownership is 125,339 source, 88,034 generated, and 4,213,049 opaque bytes.
The Apple flash plan is 703,058 bytes, SHA-256
`31e0aae47197e0c2d06d59a1382c5bd40868c1b4e48e39e5fd102881a34219cd`,
with 978 placed, two unresolved, and five container-only records. This is an
offline source/build result only: nothing was signed, flashed, erased,
formatted, reset, booted, or exercised on G2 hardware.

## Preceding atomic dual-image littlefs tag-validity/type1 production tranche

Apollo main and the bootloader now also replace the byte-identical private
`lfs_tag_isvalid` and `lfs_tag_type1` leaves. Their stock spans are
`[0x004CAE6A,0x004CAE74)` / `[0x00410B72,0x00410B7C)` and
`[0x004CAE88,0x004CAE90)` / `[0x00410B90,0x00410B98)`. Complete-image scans
authenticate three and eight direct callers per image, respectively, with no
reviewed alternate or interior ingress. Each complete stock body becomes a
non-linking `B.W` plus NOP fill.

The shared scalar-only sources are altered BSD-3-Clause adaptations of the
exact definitions in authenticated littlefs v2.10.1 commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`. This is a source-equivalent
compatibility baseline, not proof of Even Realities' exact historical
checkout. The emitted six- and ten-byte leaves have no providers or
relocations and hash to
`65e477818b1c6002b2ceb88812da258524e438ded36dfa059e034c3bce19624e`
and `079f868da6ae04c0d4ace93e9e9d9132247224f81903b57fba51d407f49ddfcf`.

| Profile | Apollo-main overlay/component | Boot overlay/component | Core-source package | Flash plan |
|---|---|---|---|---|
| Apple Clang 21.0.0 | 124,586 / `043dbfb45fcfb9707616c486ac2e736227f7186af8b25fc71a5e355a8e0ba79a`; 3,647,982 / `1227c4953bfcaeb62fb497b8a6911462a2d25fd3ed7b2bb88eea9dd3fdf13a18` | 644 / `959923a9b5253bd6409fedb82427b7ff666e2d52bc09ac5c391bc28bfbcc70c2`; 149,244 / `e8924fe19f6f768d01fa7c6ec111a4db5790eb28c423c5be84e09b0996423e20` | 4,426,458 / `f0e7e4c5e090ea558968b6293f3eec0a7f88a6126ea164547c25c8462b60be23` | 712,116 / `3dc88a1ad27c9fd1720806e190cff629116749b2e38766d331dfee786a05f3a8` |
| exact-root Linux Clang 22.1.8 | 126,406 / `7196c0d0d456b46e125b793d7ab4c6175768067589f4153d9b3ee997011c0314`; 3,649,802 / `a8684ae43a99cc692dd6cb95c8d4835cc138492d49bf9fd4a3689d32523913ef` | 644 / `078b88569f6adb147d3c12c727f29c5f3a6ddeb2f66de7d68122b4096f6ac794`; 149,244 / `6fff06068442ab3203d124c0adfd5052f216459642f67aa32cc39afffd2c0593` | 4,428,278 / `07cee183416db26bbe13673c1123e4ef19593d6343caa63c6c94791a210dc0dc` | 594,109 / `f59945999bdff46a4d86cc0d886adafae75ba23d136b7de448adbb1f7c12f3a4` |

Apple places validity/type1 at `0x007B29BC` / `0x007B29C4`; Linux uses
`0x007B30D8` / `0x007B30E0`; boot uses `0x004346EC` / `0x004346F2` under
both profiles. The configs now contain 652/601/83 main and 31/29/12 boot
functions/patches/relocated leaves. Exact Apple package ownership is 125,371
source, 88,074 generated, and 4,213,013 opaque bytes. Offline assembly is GO;
signing, flashing, reset, boot, filesystem mutation, and hardware use remain
NO-GO.

## Preceding atomic dual-image littlefs tag-type3 production tranche

Apollo main and the bootloader now additionally source-replace the
byte-identical private `lfs_tag_type3` bodies at
`[0x004CAE98,0x004CAEA0)` and `[0x00410BA0,0x00410BA8)`. Complete-image
scans authenticate 30 and 17 direct callers and no reviewed alternate or
interior ingress. The shared BSD-3-Clause adaptation implements the exact
littlefs v2.10.1 scalar mask/shift contract; the authenticated release is a
source-equivalent baseline, not proof of Even Realities' exact checkout.

Both reviewed compilers emit the same provider- and relocation-free six-byte
text, `c0f30a507047`, SHA-256
`a6781f0a92086cca25476ca00824d8f0fd736ac7d800aa9e3f6e4d6544490921`.
Apple places it at `0x007B29D0` in main and `0x004346FC` in boot. Exact-root
Linux uses `0x007B30EC` in main and the same boot address.

| Profile | Apollo-main overlay/component | Boot overlay/component | Core-source package |
|---|---|---|---|
| Apple Clang 21.0.0 | 124,594 / `2648682a1bf736c6bce9610f38c43a0b127d46fa9f0fbec9c21bc5775c1a99a0`; 3,647,990 / `2468a250bbd2ed67e0baf8cfb3abe84269743f04003fe100d676af0f526d1de0` | 650 / `efc0bc7a5fa7351a9aa372bec40d1a88fde0284b251486db11a9877947da6d50`; 149,250 / `826358deb7400e8c25b744487979c0c7f32b7e1db63588b5a244c3375e885a62` | 4,426,472 / `96f5309c2f77834a2c034b00d04618f0fa42ea3019924d5d51047f7a54c3db4d` |
| exact-root Linux Clang 22.1.8 | 126,414 / `df3b885d5a5c952144fd50324f556e1fdf9435728bb2db8aa015183eb0f4cd4f`; 3,649,810 / `478877ed8ac940d208216d4950a423f70728571fa9f18795c1ee01d521ee858c` | 650 / `968dbeac7adef3acc5151cd15189bba3528de295147ecca60832f1cf87b425e3`; 149,250 / `bb3d7eef87a59529f67de9996324a91575d6e1218471a5330b153eb28950742a` | 4,428,292 / `e56f78421dd83283e3d4e3f4a6b61a3400260c2618719cc6051453dd9e249bc1` |

The Apple plan records 995 placed, two unresolved, and five container-only
records; Linux records 833/two/five. Focused production qualification passes
five tests. At that preceding milestone, the separately bounded
`lfs_tag_size` adaptation remained production-excluded after passing five
focused tests, while `lfs_tag_id` advanced to the now-preceding atomic
dual-image production tranche documented below. Tag-size is promoted by the
current tranche that follows it.
At that preceding milestone nanopb `pb_decode_fixed64` had passed seven
focused tests but was still awaiting promotion; it is promoted by the current
Apollo-main-only tranche at the end of this ledger.
Offline assembly is GO. Signing, flashing, filesystem mutation, reset, boot,
and hardware operation remain NO-GO.

## Preceding atomic dual-image littlefs tag-ID production tranche

Apollo main and the bootloader now source-replace the byte-identical private
`lfs_tag_id` leaves at `[0x004CAEB0,0x004CAEB8)` and
`[0x00410BB8,0x00410BC0)`. The complete stock bytes are
`800a8005800d7047`, SHA-256
`0843abb3e9ef39afac8e69ae1e181efa0b5b5c8ebf53e20844b53fdf245b1036`.
Complete-image decoding authenticates exactly 50 Apollo-main and 41
bootloader direct callers, with no reviewed alternate start, interior ingress,
stored pointer, or outgoing call.

The shared source is a bounded BSD-3-Clause adaptation of the exact 91-byte
`lfs_tag_id` definition at authenticated littlefs v2.10.1 `lfs.c` bytes
`[10702,10793)`, SHA-256
`50140c563689852013dfad180ec3b6464c6b6c5b22854f5492d63cf5de57fbe2`,
commit `0494ce7169f06a734a7bd7585f49a9fa91fa7318`. This is an
authenticated source-equivalent baseline, not proof of Even Realities' exact
historical checkout. The production C source is 845 bytes with SHA-256
`5b6c3ce0f4236d6c6bc0a12891e41929e9034a7ddc2f68bd4f6a1d5d4fa07638`;
its 872-byte header hashes to
`5d6d1c5df9a0fb31f80ad0f6a876795cb154b039fa72df17c615b38cd5e2099e`.
Both reviewed profiles emit the same provider- and relocation-free six-byte
text `c0f389207047`, SHA-256
`6194594e24288e708887a0e938b2a54401c8c732210d91af7a5927d03bd3604c`.

The final Apple and exact-root Linux placement and artifact ledger is:

| Profile | Main leaf offset/address and patch | Boot leaf offset/address and patch | Main overlay/component | Boot overlay/component | Package |
|---|---|---|---|---|---|
| Apple Clang 21.0.0 | `124,596` / `0x007B29D8`; `e7f292bd00bf00bf` | `650` / `0x00434702`; `23f0a3bd00bf00bf` | `124,602` / `229ca8faff25bd61cd21152d828275f6e1dad9883eab359056482956ea166e98`; `3,647,998` / `8dddb1f59da1319dc15815ded6258f966a6fd08d6ed7edc134122de5bca2fff6` | `656` / `432f0c91a6db142a951db076fc89a4a80e740675d63f62263f45c21e37777ad3`; `149,256` / `6d96308ea4e5851ab137831d6da991184b6611551a01fa18e4cef3f1877f4694` | `4,426,486` / `bfa8629a4c182e7448b4b6d89f875cd99f7e105876f12e4d2904d755cafc69f1` |
| exact-root Linux Clang 22.1.8 | `126,416` / `0x007B30F4`; `e8f220b900bf00bf` | `650` / `0x00434702`; `23f0a3bd00bf00bf` | `126,422` / `fcf2783a5a73474fb87cdd22cc592a12056b6a4d4080e7f8ca6120b88d82ebaa`; `3,649,818` / `40d16ee5833eae6ae3229d82fcd583fd2c3ba9fe6234978d503a57c0d88ffeff` | `656` / `4cadbf422b57b1905b38df77ab0d24932839aa28f883f57e56a09183d577edb8`; `149,256` / `a3ca91bb744c777d7d98d8b34a044e613ad251a972d6e6d54a8a48b959795ad2` | `4,428,306` / `727354ce585843f11fabec93884640fdf58c71b251f5b7067ee4c0703cb53fcd` |

The final production censuses are
`654/603/85` main and
`33/31/14` boot functions/patches/relocated leaves;
the canonical manifest region counts are
`932 main / 65 boot`. Exact package ownership is 125,397 source / 88,108
generated / 4,212,981 opaque bytes for Apple and 127,291 / 87,882 /
4,213,133 for Linux. This scalar promotion introduces no
G2 block-device, mount, format, program, or erase path. Offline source
assembly is GO; signing, flashing, filesystem mutation, reset, boot, and
hardware operation remain NO-GO.

## Preceding atomic dual-image littlefs tag-size production tranche

The current atomic littlefs tranche source-replaces the complete,
byte-identical private `lfs_tag_size` leaves at
`[0x004CAEB8,0x004CAEBE)` in Apollo main and
`[0x00410BC0,0x00410BC6)` in the bootloader. Both official bodies are
`8005800d7047`, SHA-256
`8596106584e598a657aea7fdd2e1156a748158d2d63d9c121c92587fabbdf8ca`.
Complete-image decoding authenticates exactly 15 main and 14 boot direct
callers, with no reviewed alternate start, interior ingress, stored pointer,
outgoing call, shared tail, or literal pool.

The source authority is the exact 87-byte `lfs_tag_size` definition at
authenticated littlefs v2.10.1 `lfs.c[10793:10880]`, SHA-256
`9df85bc43ca9f90ef58c425c5fd9bbbbf53585093be5fad0cc580fc88814ea5c`,
commit `0494ce7169f06a734a7bd7585f49a9fa91fa7318`. Its exact behavior is the
unsigned low-ten-bit mask `tag & 0x000003ff`. The 854-byte local source and
1,000-byte header hash to
`533bbfcbfc2440e02b79692a2a7ccff87c3cb62cbb0788c1d5bf806fd3bca849`
and `0f29febdc25b081de1821a41c9065870c02154375985bf648d8e1b63f6cc3528`.
Apple production builds emit the provider- and relocation-free six-byte text
`6ff39f207047`, SHA-256
`35890ebcdee5cb7f51b3e8d874201b7e0214f6111eebe56c772133f259cf9b54`.

The final build-dependent contract is:

| Profile | Main leaf offset/address and patch | Boot leaf offset/address and patch | Main overlay/component | Boot overlay/component | Package |
|---|---|---|---|---|---|
| Apple Clang 21.0.0 | `124604` / `0x007B29E0`; `e7f292bd00bf` | `656` / `0x00434708`; `23f0a2bd00bf` | `124610` / `3748b98f262a2db4cc38c2b0ce63ed83ee01cd945384a31fc7e132d99db79b7a`; `3648006` / `4a518e8fa6eaad8113d3ac14070ce6fdc3f2ddbf318b651bfa13423d9a0caa2a` | `662` / `7cb3c17a03dda3b8576d8288ffa61df1332d89f1f24d6c5877bf0143e233902b`; `149262` / `695688b7cc4d9583e9e5c854db44980acab9a58d367bc7e02fa5e51eb00e3267` | `4426500` / `bed7320b89d6497cc261ee948716004821e3a1c3eb92018271c27a1e4c89432f` |
| exact-root Linux Clang 22.1.8 | `126424` / `0x007B30FC`; `e8f220b900bf` | `656` / `0x00434708`; `23f0a2bd00bf` | `126430` / `8e252b96fd244107603046a4a0eb3ef17fe261e026bb52d793ccbbb764a5df56`; `3649826` / `a34fb1906c0b20702b7636866479b7680776aeda3cad7fb36a544bea78ffc6b8` | `662` / `e4c743531f56c190b7e3129768d410480a2f3433a5b680c7bf432ef0b05a7021`; `149262` / `fc3d07c8a59e1c33f26965cdb1888114412c3ca671d6137f7c3166acc81c8d74` | `4428320` / `70ec26aaf4ddb42ae04938edb4a54f3875c6d33a856e477cdf7acc461ebcff0d` |

Final function/patch/relocated-leaf config censuses are
`655/604/86` main and
`34/32/15` boot;
manifest counts are `935 main /
67 boot`. Exact canonical package
source/generated/opaque ownership remains separately pinned as
`125409 / 88122 / 4212969`
for Apple and
`127305 / 87894 / 4213121`
for Linux. These final pins close production registration; the settled tag-ID
tranche above is the preceding milestone. This scalar promotion imports no G2
block-device, mount, format, program, or erase
path and authorizes no signing, flashing, reset, boot, filesystem mutation, or
hardware operation.

## Preceding Apollo-main nanopb fixed64 production tranche

Apollo main now source-replaces the complete nanopb `pb_decode_fixed64` body
at `[0x004901AC,0x004901CC)`. The 32 stock bytes hash to
`96228dfbdfe30665d79281ba0fd5ba3b3af38701396671cd20b77623ffd82d54`;
whole-image scans authenticate the sole caller at `0x0048F8C6`, no alternate
or interior ingress, and the then-binary `pb_read` ABI entry at
`0x0048F3BE`. The current tranche source-owns that entry. No authenticated
bootloader homolog exists.

The altered Zlib-licensed leaf selects authenticated nanopb 0.4.9 commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824` as a compatibility baseline
within the source-equivalent 0.4.7--0.4.9 range. Apple places its 28-byte text
at offset 124,612 / `0x007B29E8`; Linux places 30 bytes at offset 126,432 /
`0x007B3104`. Each object has one `R_ARM_THM_CALL` relocation to the retained
stock read seam and no allocated data.

| Profile | Main overlay/component | Core-source package | Flash plan |
|---|---|---|---|
| Apple Clang 21.0.0 | `124640` / `476843181113c88594d1a766a60b91a15a3ec76a4c898c46d3176f64ea21c867`; `3648036` / `d334b5d063701af87691b2c946a315d481d2317f91293517fd16638b06182f07` | `4426530` / `a3d06dd732722859a7cd4da1582cea49464cbbfccdb90e329afa6ec9352195d4` | `725221` / `506b34cd171e5d03da34faa9431f44e57b512d5d9e211cff8e9490ab0c716897`; 1,010/two/five |
| exact-root Linux Clang 22.1.8 | `126462` / `f5d4a4e441b1185001e031d1b9d319474ffd721c1280e1611e29f08169cb46cc`; `3649858` / `0d765ead02aa3d9981fe14b4aa8663bff57f12b307a2f9ce7e6d226225523a16` | `4428352` / `75af4c1facb8c663cff2a8d4469625261ffa04d9c9587dc0db9ecf2c2f401b6d` | `599794` / `14644134ce433085cfba526710635ae6c1f769ab9cd90e27857da15779c3fc80`; 840/two/five |

Final config censuses are `656/605/87` main and `34/32/15` boot; manifest
counts are `938 main / 67 boot`. Exact source/generated/opaque package
ownership is `125437/88156/4212937` for Apple and
`127335/87928/4213089` for Linux. This is deterministic offline assembly only;
it authorizes no signing, flashing, reset, boot, or hardware operation.

## Preceding Apollo-main nanopb `pb_read` production tranche

At this preceding milestone Apollo main source-replaced the complete 150-byte
nanopb `pb_read` body at
`[0x0048F3BE,0x0048F454)`, stock SHA-256
`69aecb900c749fd98bd2d05e2229e9a3d6829bd36f3e393f624e3579a9b4af7f`.
Whole-image decoding authenticates 13 external direct callers plus two local
recursive calls and finds no external interior branch or stored pointer. The
stock ABI entry is retained, so all callers—including the preceding nanopb
leaves—now reach the source implementation through its generated redirect.
No authenticated bootloader homolog exists.

The altered Zlib source selects authenticated nanopb 0.4.9 commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824` within the source-identical
0.4.7--0.4.9 `pb_read` range. Its 2,874-byte C source and 2,059-byte header
hash to
`65f8f3cb92729e98f82f1254b18ba969cdd8a57c7ac74e8713137b5585102453`
and `aaa9847151722953498958687e91d55dc0b18cc9a60318b4f754110c66a443d6`.
Both profiles emit the same 158-byte relocated leaf, SHA-256
`8b3de44a2cf7ca2e07715c913db0fa454ef65cbc453366190b12736e455aa7a8`.
Three reviewed binary seams remain explicit: private `buf_read` Thumb identity
`0x0048F3A5`, end-of-stream string `0x00787C70`, and I/O-error string
`0x0078B690`.

| Profile | Leaf placement / entry patch | Main overlay/component | Package | Flash plan |
|---|---|---|---|---|
| Apple Clang 21.0.0 | offset `124640`, `0x007B2A04`; patch SHA `c2c44419ee24c41c8d0e8bc7f04689bb7f1c18b1f7ec3d7304e04c37579938a1` | `124798` / `dddc7836f2c8de4ae1664cb55b7e197bdf66a39b79f9a30ef236b194cf097999`; `3648194` / `3f6276b907178be9f04b64fac3a241b19197637dce4450a812b50fc8caff30ea` | `4426688` / `f861d049873d497b44f25b265bad4a6ba9409aef3ff3abb4ed6abc1a031a4804` | `727340` / `3a8eaa36c051d245c8ccc7d4c93868ab23f34e03a6113d35f6d0418185fc8702`; 1,013/two/five |
| exact-root Linux Clang 22.1.8 | offset `126464`, `0x007B3124`, after two alignment bytes; patch SHA `4dc433588344c12d1a0abfab8c5f1673c24f6702d8f285f67fb0fd8b8e6e3eab` | `126622` / `990b4d60bff7764ed6f0400c1133fdfc2869624567e1539f1734f60c88c531b9`; `3650018` / `9d92d8a9aa41c3a274c1d28be05213def2994dcea2850eefefb96d796119e1bb` | `4428512` / `0269400751d0ffa0f58c5cf8658b4dbc6e8af90a875d13bc2e5f684a436d26a9` | `601182` / `8ba103a92bcbfe060878c0091e6ef1608b3b5c2c55b1a94f5da8b4a2cf7fdcbc`; 842/two/five |

At that milestone the censuses were `657/606/88` main and unchanged
`34/32/15` boot, with
`941/67` manifest regions. Exact source/generated/opaque package ownership is
`125595/88306/4212787` for Apple and `127493/88080/4212939` for Linux.
Those values belong to the preceding `pb_read` milestone. The following
constructor milestone superseded them, and the subsequent signed-varint
section records the later signed-varint Apple aggregates and censuses. Qualification and
packaging were offline only;
no image was signed or flashed, and no reset, boot, filesystem mutation, or
hardware operation was performed.

## Preceding nanopb stream-constructor milestone

At that milestone, Apollo main source-owned the complete nanopb
`pb_istream_from_buffer` span
`[0x0048F49C,0x0048F4B8)`. The bounded Zlib adaptation selects authenticated
nanopb 0.4.9 as a compatibility baseline, not as proof of the vendor checkout.
All 30 callers kept the stock entry and callback identity `0x0048F3A5`. The
canonical Apple package at that preceding milestone was 4,426,806 bytes with
SHA-256
`062eaf5a7f301022f97162f4517d15248276e80c11a27b7c9f9b0e4cda4fbef2`.
No bootloader homolog was found; this offline build makes no hardware claim.

## Preceding nanopb signed-varint source increment

At that milestone Apollo main source-owned the complete 64-byte
`pb_decode_svarint` body at
`[0x00490150,0x00490190)`. The altered Zlib-licensed nanopb 0.4.9
compatibility leaf calls the already source-owned unsigned decoder directly,
is appended at `0x007B2B18`, and replaces the stock entry with a full-span
non-linking branch plus Thumb NOP fill. The Apple overlay/component/package
are `124970 / 3648366 / 4426860` bytes with SHA-256 values
`1cfdeb0382a10f1c9dad9d203bd2f3a0d1f56390815eafffcf925f7731bb80ec`,
`eaf24d1adce80ce958c5ff90585bc2da6a2f76634a9d2539e3a5cf2b37814bf1`,
and `e77b984d3644cade761b2aecec399ccb9249c419c2ca6e9f4963cbbbfa208cf7`.
The manifest then had 951 Apollo-main regions and nanopb's bounded production
allowlist had ten functions. The exact-root Linux Clang 22.1.8 replay emits a
50-byte leaf at `0x007B323C` and closes the overlay/component/package at
`126794 / 3650190 / 4428684` bytes with SHA-256 values
`be028b3e22b5952325965c029523dacb0b2d3bad3602c397de706a53708d88f0`,
`78ff4ac1538ad3d43076510f06a9ddb3ba1ca2a0f421d3778f96e2a40c6f1696`,
and `b5391623b98a886bf87989a5c28c5f500556866d08dbbff5c25535f6f707af06`.
No firmware was signed or flashed. See
`docs/research/nanopb-decode-svarint-source-audit.md`.

## Preceding nanopb varint32-pair source increment

Apollo main now owns private `pb_decode_varint32_eof` and public
`pb_decode_varint32` as nanopb's eleventh and twelfth bounded altered
functions. Their independent stock spans are `[0x0048F4B8,0x0048F5AE)` and
`[0x0048F5AE,0x0048F5B8)`. Apple installs separate text leaves at
`0x007B2B50` and `0x007B2C40`; the private 222-byte text closes over two
source calls to `open_cfw_nanopb_readbyte` and a 16-byte literal, while the
public 10-byte wrapper calls the private source leaf directly. The 957-region
manifest owns both patches, both alignment regions, private text and rodata,
and public text independently.

Current Apple overlay/component/package pins are `125222 / 3648618 / 4427112`
bytes with SHA-256 `a21779625714a5c029652287e38939ac4290306b3a8781045501839d385a1c62`,
`99b1718f989695a4fe39655e8cf31ea7ef19ce97ed96b70fc1796c847bd2dead`,
and `92d1d9a2f2d80b503b2b68d1533a1c990da5a215381a0a22b604e63b6f7fb229`.
Nanopb 0.4.9 is a compatibility baseline, not proof of the vendor point
release. The exact-root Linux replay places the leaves at overlay offsets
126,796 and 127,036 and closes the overlay/component/package at
127,046 / 3,650,442 / 4,428,936 bytes. No bootloader homolog was found.
No firmware was signed or flashed and no
hardware operation was performed. See
`docs/research/nanopb-decode-varint32-pair-source-audit.md`.

## Preceding nanopb skip-string source increment

Apollo main now source-owns `pb_skip_string` as the thirteenth bounded altered
nanopb function. A full 32-byte redirect at `0x0048F64C` reaches identical
34-byte Apple/Linux text closed over source-owned `pb_decode_varint32` and
`pb_read`. Apple places it at `0x007B2C4C`; exact-root Linux places it at
`0x007B336C`. At that milestone, overlay/component/package pins were
`125258/3648654/4427148` on Apple and `127082/3650478/4428972` on Linux; the
960-region manifest and both profile aggregates are fail-closed. Nanopb 0.4.9
remains a compatibility choice within authenticated 0.4.7--0.4.9, not vendor
checkout proof. No bootloader homolog exists, and nothing was signed, flashed,
booted, reset, or hardware-tested. See
`docs/research/nanopb-skip-string-source-audit.md`.

## Current nanopb skip-field source increment

Apollo main now source-owns `pb_skip_field` as the fourteenth bounded altered
nanopb function. A full 74-byte non-linking redirect at `0x0048F6A0` reaches
66 bytes of Apple-Clang text at `0x007B2C70`, followed by the source-owned
18-byte `invalid wire_type` diagnostic at `0x007B2CB2`. The leaf closes only
over source-owned `pb_read`, `pb_skip_varint`, and `pb_skip_string` providers.

The Apple overlay/component/package pins are
`125344/3648740/4427234`, and the 965-region Apollo-main manifest produces a
1,037-region placed flash plan. Effective package ownership is 126,112 source,
88,735 generated, and 4,212,387 opaque bytes. The reviewed Linux/Clang 22
profile remains fail-closed pending access to that exact compiler; its object
and aggregate pins are not inferred. No firmware was signed, flashed, booted,
reset, or hardware-tested. See
`docs/research/nanopb-skip-field-source-candidate-audit.md`.

## Current nanopb raw-value source increment

Apollo main now source-owns private `read_raw_value` as the fifteenth bounded
altered nanopb function. A full 148-byte non-linking redirect at `0x0048F6EA`
reaches 134 bytes of Apple-Clang text at `0x007B2CC4`, followed by a
source-owned 34-byte diagnostic block at `0x007B2D4A`. The leaf closes only
over source-owned `open_cfw_nanopb_read`.

The Apple overlay/component/package pins are
`125512/3648908/4427402`, and the 968-region Apollo-main manifest produces a
1,040-region placed flash plan. Effective package ownership is 126,280 source,
88,883 generated, and 4,212,239 opaque bytes. The reviewed Linux/Clang 22
profile remains fail-closed pending access to that exact compiler; its object
and aggregate pins are not inferred. No firmware was signed, flashed, booted,
reset, or hardware-tested. See
`docs/research/nanopb-raw-substream-boundary-audit.md`.

## Current nanopb make-string-substream source increment

Apollo main now source-owns `pb_make_string_substream` as the sixteenth bounded
altered nanopb function. A 76-byte stock redirect at `0x0048F77E` reaches 72
bytes of Apple text at `0x007B2D6C` and 24 bytes of diagnostic rodata at
`0x007B2DB4`. Four explicit ABI-field assignments eliminate the stock aligned
`__aeabi_memcpy` dependency. The Apple overlay/component/package pins are
`125608/3649004/4427498`; package ownership is 126,376 source, 88,959
generated, and 4,212,163 opaque bytes. Linux/Clang 22 remains pending without
inferred pins. See `docs/research/nanopb-raw-substream-boundary-audit.md`.

## Current nanopb Boolean decoder-pair source increment

Apollo main now source-owns public `pb_decode_bool` and private `pb_dec_bool`,
bringing the bounded altered nanopb allowlist to eighteen functions. Complete
36-byte and 10-byte stock spans at `0x0049012C` and `0x004901CC` redirect to
28-byte and 6-byte Apple leaves at `0x007B2DCC` and `0x007B2DE8`. Their only
relocations form a source-to-source chain through the already owned public
varint32 decoder; no stock data or helper seam remains.

The Apple overlay/component/package pins are
`125642/3649038/4427532`, with package ownership `126410` source, `89005`
generated, and `4212117` opaque bytes. The 974-region Apollo manifest produces
1,046 placed flash regions and two preserved unresolved regions. Exact-root
Linux Clang 22.1.8 remains fail-closed pending reviewed reproduction. See
`docs/research/nanopb-bool-cluster-source-audit.md`.

## Current nanopb private field-varint source increment

Apollo main now source-owns private `pb_dec_varint`, bringing the bounded
altered nanopb allowlist to nineteen functions. The complete 380-byte stock
span at `0x004901D6` redirects to 304 bytes of Apple text at `0x007B2DF0` and
36 bytes of source-owned diagnostics at `0x007B2F20`. All provider calls
remain within the source-owned nanopb closure.

The Apple overlay/component/package pins are
`125984/3649380/4427874`, with package ownership `126750` source, `89387`
generated, and `4211737` opaque bytes. The 978-region Apollo manifest produces
1,050 placed flash regions and two preserved unresolved regions. Exact-root
Linux Clang 22.1.8 remains fail-closed pending reviewed reproduction. See
`docs/research/nanopb-dec-varint-source-audit.md`.

## Current nanopb private bytes-field source increment

Apollo main now source-owns private `pb_dec_bytes`, bringing the bounded
altered nanopb allowlist to twenty functions. The complete 146-byte stock span
at `0x00490358` redirects to 98 bytes of Apple text at `0x007B2F44` and 48
bytes of local diagnostic data at `0x007B2FA6`. Both executable dependencies
resolve to source-owned nanopb leaves; two apparent raw pointer matches were
verified as 16-bit pair-table data.

The Apple overlay/component/package pins are `126130/3649526/4428020`, with
package ownership `126896` source, `89533` generated, and `4211591` opaque
bytes. The 982-region Apollo manifest produces 1,054 placed flash regions and
two preserved unresolved regions. Exact-root Linux Clang 22.1.8 remains
fail-closed pending reviewed reproduction. See
`docs/research/nanopb-dec-bytes-source-audit.md`.

## Current nanopb private string-field source increment

Apollo main now source-owns private `pb_dec_string`, bringing the bounded
altered nanopb allowlist to twenty-one functions. The complete 158-byte stock
span at `0x004903EA` redirects to 114 bytes of Apple text at `0x007B2FD8` and
49 bytes of local diagnostic data at `0x007B304A`. Both executable
dependencies resolve to source-owned nanopb leaves, and no stock pointer or
literal seam remains.

The Apple overlay/component/package pins are `126295/3649691/4428185`, with
package ownership `127059` source, `89693` generated, and `4211433` opaque
bytes. The 986-region Apollo manifest produces 1,058 placed flash regions and
two preserved unresolved regions. Exact-root Linux Clang 22.1.8 remains
fail-closed pending reviewed reproduction. See
`docs/research/nanopb-dec-string-source-audit.md`.

## Current nanopb private submessage source increment

Apollo main now source-owns the bounded private `pb_dec_submessage` body,
bringing the altered nanopb allowlist to twenty-two functions. The complete
172-byte stock span at `0x0049048C` redirects to 138 bytes of Apple text at
`0x007B307C` and 25 bytes of local diagnostic data at `0x007B3106`, after one
alignment byte. Substream make/close calls resolve to source-owned leaves;
`pb_decode_inner` remains explicitly pinned to stock `0x0048FE98`, and the
indirect message callback is an application ABI seam.

The Apple overlay/component/package pins are `126459/3649855/4428349`, with
package ownership `127222` source, `89866` generated, and `4211261` opaque
bytes. The 991-region Apollo manifest produces 1,063 placed flash regions and
two preserved unresolved regions. Exact-root Linux replay remains pending.
See `docs/research/nanopb-dec-submessage-source-audit.md`.

## Current nanopb iterator-cluster source integration

Apollo main now routes every live entry in the retained nanopb `pb_common.c`
iterator/default-callback cluster through nine selector-isolated source leaves.
Together with source-owned `pb_decode_inner` and `pb_decode_tag`, this brings
the bounded altered nanopb allowlist to thirty-three functions and closes six
decoder/defaults call sites across five iterator entries. Eight authenticated
stock-entry redirects replace 412 live bytes; 536 unreachable private stock
bytes remain deliberately opaque rather than being overclaimed.

The reviewed Apple overlay/component/package pins are
`128264/3651660/4430154`. The 1,022-region Apollo manifest accounts for
129,014 source, 90,977 generated, and 4,210,163 opaque package bytes; the flash
plan places 1,094 regions with two unresolved and five container-only records.
Linux/Clang 22 reproduction and hardware execution remain deferred. See
`docs/research/nanopb-iterator-cluster-source-audit.md`.

## Current nanopb paired-defaults source integration

Private `pb_message_set_to_defaults` and `pb_field_set_to_default` now bring
the bounded altered nanopb allowlist to thirty-five functions. Their complete
438-byte stock span redirects to 414 Apple source bytes plus two alignment
bytes. Recursive defaults, iterator, stream, and tag edges resolve to source;
only `decode_field @ 0x0048FBE4` remains fixed stock.

The reviewed Apple overlay/component/package pins are
`128680/3652076/4430570`. The 1,027-region Apollo manifest accounts for
129,428 source, 91,417 generated, and 4,209,725 opaque package bytes; the flash
plan places 1,099 regions with two unresolved and five container-only records.
Linux/Clang 22 reproduction and hardware execution remain deferred. See the
paired audits in `docs/research/nanopb-message-defaults-source-audit.md` and
`docs/research/nanopb-field-default-source-audit.md`.

## Current nanopb dispatch/extension source integration

Private `decode_field`, `default_extension_decoder`, and `decode_extension`
bring the bounded altered nanopb allowlist to 38 functions. Their three
complete executable stock entries redirect to 243 source bytes plus one
alignment byte; the intervening 16-byte literal island remains hash-pinned
opaque data. The corrected stock boundaries are `0x0048FBE4`, `0x0048FC26`,
and `0x0048FC88`.

The reviewed Apple overlay/component/package pins are
`128924/3652320/4430814`, with SHA-256 values
`555cee5a2bf43bafef750c77658b654fc72642699d5e432226d209337b69eb57`,
`60d9a28c2dc38e04d2ea3fd6109d7d26b3229d1e0b8ec04a695cde7c3146f4e8`,
and `764b752f15d7cc5a0609091a2c6852aee1a4b1892125b1ac185134ab0897a751`.
Package ownership is 129,671 source, 91,656 generated, and 4,209,487 opaque
bytes. See `docs/research/nanopb-dispatch-extension-source-audit.md`.

## Current nanopb field-decoder source integration

Private `decode_basic_field`, `decode_static_field`, the no-malloc
`decode_pointer_field`, `decode_callback_field`, and
`pb_dec_fixed_length_bytes` bring the bounded altered nanopb allowlist to 43
functions. Their complete stock entries, totaling 1,116 executable bytes,
redirect to five selector-isolated source closures. All fixed relocations bind
source-owned providers; two dynamic callbacks remain intentional schema ABI.

The reviewed Apple overlay/component/package pins are
`130064/3653460/4431954`, with SHA-256 values
`1aed0db7defff8bf547d306e417b4e783a569b63357ba9808e344c21d2e41d23`,
`a639f5d33b5db863a430fd98e98bf74ca130da3f51f9cb01947e5706c7dd1032`,
and `dc3c9dc059d32ad46c751dc7fbcc66ed371a01e15492a210fcf4a7d1a6d6bfa4`.
Package ownership is 130,803 source, 92,780 generated, and 4,208,371 opaque
bytes. See
`docs/research/nanopb-field-decoder-cluster-boundary-audit.md`.

## Current AndersKaloer/Ring-Buffer source integration

The complete seven-function dynamic-buffer cluster is now source-integrated.
The maintained upstream selection is commit `190e30b`, with the exact
binary-compatible interval honestly recorded as `cda00e1...190e30b`. Seven
guarded redirects replace all 252 callable stock-span bytes (250 instructions
plus two alignment bytes); Apple adds 248
source bytes and four alignment bytes at `[0x007B3F34,0x007B4030)`.

The reviewed Apple overlay/component/package pins are
`130316/3653712/4432206`, with package SHA-256
`a5625a4bcc1ff20ff9e339f9bb0a074d999508674c7aeb315101e653c90630c2`.
Package ownership is 131,051 source, 93,036 generated, and 4,208,119 opaque
bytes. See `docs/research/ring-buffer-lineage-recovery-audit.md`.

## Current IAR void-EABI memory-provider source integration

`components/apollo_main/core_overlay/candidates/iar_runtime_memory.S` now supplies production selector-isolated
public memcpy, aligned memcpy, and overlap-safe memmove entries. The exact
source sections are 152, 152, and 322 bytes, relocation-free, and passed 6,000
deterministic Lorelei Unicorn vectors. Their 1,024-byte instruction-count proxy
is within 5.2% of the authenticated stock providers across aligned and
mismatched-alignment cases.

Disjoint guarded redirects cover `[0x00439710,0x004397A6)`,
`[0x00439BE4,0x00439C04)`, and `[0x00439C04,0x00439C8A)`. Apple places the
source at `[0x007B4030,0x007B42A2)` and closes at
`130942/3654338/4432832`; Linux places it at `[0x007B477C,0x007B49EE)` and
closes at `132810/3656206/4434700`. Both profiles and packages were replayed
twice fail-closed. Canonical package ownership is 131,677 source, 93,352
generated, and 4,207,803 opaque bytes. See
`docs/research/iar-runtime-memory-source-candidate.md`.

## Current IAR math/errno source integration

`components/apollo_main/core_overlay/candidates/iar_runtime_math_errno.S`
recreates the remaining bounded IAR `sqrtf`, EDOM, ERANGE, and errno-address
units. Apple Clang 21 and Lorelei Linux Clang 22.1.8 emit identical sections;
5,500 Unicorn executions match authenticated stock. Four guarded redirects and
twice-replayed dual-profile placements make all ten census code units
source-recreated and production-integrated. Apple closes at
`131020/3654416/4432910`; Linux closes at `132888/3656284/4434778`.
Canonical ownership is 131,755 source, 93,424 generated, and 4,207,731 opaque
bytes. See
`docs/research/iar-runtime-math-errno-source-candidate.md`.

## Current Apollo-main 64-chunk decompilation lane

Apollo main now also has a deterministic 64-chunk Lorelei decompilation lane.
It authenticates the 3,523,396-byte OTA component, exactly tiles the installed
`[0x00438000,0x00794324)` range, vector-seeds and analyzes one Ghidra project,
then Btrfs-reflink clones that project for 64 independent decompilers. The
winning equal-byte run decompiled all 7,370 discovered functions with zero
failures in 142.780 seconds after a one-time 156.280-second analysis: about
5.0 minutes cold or 2.4 minutes with the template retained. An audit-hardened
replay that also hashes all ten analyzed-project files took 145.251 seconds.
Tested 16- and 32-worker runs took 152.329 and 163.799 seconds. The complete
returned corpus is now repository-owned at
`research/lorelei/lorelei-returned-results-20260808.tar.gz` and guarded by
`tools/verify_lorelei_returned_results.py`. Full hashes, resource observations,
and the distinction between mechanical
decompilation and source reconstruction are in the
[Lorelei acceleration benchmark](docs/research/lorelei-re-acceleration-benchmark.md).

Follow-on compact Lorelei results are also repository-owned and verified for
the WSF OS/queue, buffer, assert/trace, EFS-exclusion, string-helper, ATT
client-supported-features, and SMP pairing-database tranches. The SMP result
started from seven path anchors / 2,688 bytes; authenticated closure expands it
to all eleven linked functions / 2,952 bytes, with two unused APIs
dead-stripped. It records two zero-unresolved readiness links without retaining
firmware, source, decompilation, objects, or build caches. See
`research/lorelei/README.md` and
`docs/research/cordio-smp-db-source-recovery.md`.

## Current EM9305 parallel-analysis and SDK archive closure

The 32-core/64-thread Lorelei worker now runs the checked-in EM9305 manifest as
16 isolated headless Ghidra projects in one SSH-orchestrated batch. The current
targeted replay completed all 16 shards in 18.042--18.299 seconds and returned
hash-manifested results; it is 1.46x faster by mean shard time than broad
auto-analysis, and 32 workers reduced throughput, so 16 targeted workers are
the current default. The same tasks can run wholly on Lorelei without changing
their evidence format, while local orchestration retains the reviewed
integration and repository edits.

Relocation-normalized comparison of six authenticated EM9305 SDK v4.2 archives
now proves 98 exact stock functions / 7,172 bytes across QP/C, PML, protocol
timer, sleep manager/timer, and unitimer. Archive metadata pins Synopsys
MetaWare ARC T-2022.09 build 004 / LLVM 14.0.6, ARCv2 EM, `-Os`. QP/C is exact
v6.5.1 at official commit
`416dcec8820b9cdb5827497e645d0d9375db53c6`; its QK SWI port is exact, and the
former 280-byte anonymous cluster prefix is fully assigned to protocol-timer
code. All controller bytes remain authenticated cut-forward stock pending
source and license recovery.

The expanded 16-archive lane now pins the Packetcraft/EM Bleu Bluetooth-5.4
controller (`BT_VER=13`, `LL_VER_NUM=28992`) and EM system/HAL/radio support.
After deduplicating aggregate archive profiles and symbol aliases, it adds
1,146 exact functions / 132,610 bytes. A second 32-archive Lorelei lane adds
67 globally new functions / 13,078 bytes after discarding 1,134 duplicate
address/body identities. A subsequent 8-byte-floor replay promotes 124 of 129
new candidates only after independent entry-boundary/xref checks. Exact-neighbor
link order first resolves 16 duplicate-location bodies / 784 bytes and
identifies 30 additional functions. A NOP-aware exact-neighbor pass adds 156
placements / 9,818 bytes, including 34 exact bodies and 42 same-size or
size-delta modified functions. Exact coverage is now 1,494 functions in 875
intervals / 157,122 bytes, or 74.504950% of the application. Vector-table
resolution adds three exact interrupt bodies and one modified radio-TX body.
Six repeated four-byte EM-system return leaves are resolved by authenticated
archive order at the exact left-anchor boundary. Function provenance is
identified for 167,684 bytes (79.513296%). Of the 43,204-byte remainder, 9,546
bytes are structurally classified vectors, alignment, or post-text tables/data;
33,658 bytes remain unresolved code or
mixed content.
All remain cut-forward. The archive increment includes 62 exact ISO/BIG
controller bodies, so the non-ISO profile header is not a complete final-link
configuration claim. Packetcraft's public r20.05c
commit is much older (`LL_VER_NUM=1366`), so it is not substituted for the
proprietary 2024 source state. See
`docs/research/lorelei-re-acceleration-benchmark.md`,
`docs/research/em9305-qpc-arcompact-audit.md`, and
`docs/research/em9305-sdk-archive-match-audit.md`, plus
`docs/research/em9305-expanded-sdk-archive-census.md` and
`docs/research/em9305-sdk-link-order-recovery.md`, with the complete residual
partition in `docs/research/em9305-residual-segment-census.md`.

A second 16-way Lorelei Ghidra run now targets independent large residual code
gaps rather than the already-closed QP cluster. All lanes returned in
17.644--17.993 seconds. Fifteen experimental ARCompact decompilations remain
candidate-only because of bad constructor p-code; one coherent 12-byte helper
was independently resolved through the SDK archive as
`lctrSlvCheckEncOverridePowerControl @ 0x00329554`. This confirms the remote
fan-out/verified-return workflow while keeping GNU ARC and archive identities
as the semantic authority.

The repository-owned Lorelei handoff now also includes the complete Cordio
SMP-main tranche. Twenty linked functions / 3,076 stock bytes are bounded and
source-identified; `SmpDmGetLtk` is the sole dead-stripped public API. The
reconstruction pins Packetcraft r20.05c plus a tracked Ambiq stale-AES queue
cleanup patch, and the compact artifact preserves two valid zero-unresolved
hybrid links while explicitly rejecting two zero-code base links as vacuous.
See `docs/research/cordio-smp-main-source-recovery.md` and
`research/lorelei/README.md`.
