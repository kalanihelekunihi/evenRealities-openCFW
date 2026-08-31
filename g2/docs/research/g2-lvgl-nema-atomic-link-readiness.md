# G2 LVGL/Ambiq/Nema atomic-link readiness

Status date: 2026-08-30  
Target: official G2 `s200_v2.2.6.10` Apollo-main image  
Mode: bounded source/archive inventory, Cortex-M55 compile, and relocatable
link audit; no signing, firmware-image integration, flashing, MMIO, or hardware
operation

## Result

The locally actionable Nema atomic-link frontier is now quantified rather than
opaque. The audit compiles all 14 exact Ambiq LVGL translation units plus the
cache-free radius-mask provider, then derives every provider requirement from
Arm relocations. The 15 objects are warning-free and have 154 aggregate
unresolved symbols. Ninety-six are direct Nema/Ambiq requirements.

The authenticated public AmbiqSuite 5.1.0 GCC archives resolve 88 of those 96
direct requirements: 82 NemaGFX/NemaVG exports and six GPU-patch exports. A
relocatable link selects exactly 18 Nema archive members plus
`ambiq_nema_extension.o` and leaves 89 symbols, including 19 Apollo510 Nema HAL
APIs. The resulting 1,377,972-byte Arm object has SHA-256
`a713fbf4eaf8554ec4e31b431dbc833831e9c93a92ad8eb31bcc8ee25cba7346`.

A scoped Apollo510-EVB FreeRTOS HAL source candidate then closes 17 of those 19
HAL APIs, including `nema_wait_irq_brk`. The remaining 46-byte
`nema_buffer_invalidate` and 36-byte `nema_buffer_is_within_pool` functions are
now supplied by the local MIT provider in `g2-runtime`. Exact stock bytes,
public API ancestry, descriptor addresses and offsets, normal-input semantics,
and every target relocation are pinned. Hostile arithmetic, null, negative-size,
and out-of-pool inputs deliberately fail closed instead of preserving stock's
unchecked unsigned-add behavior.

The candidates also expose their real downstream boundary: five Apollo510 Ambiq
HAL calls and three FreeRTOS queue/semaphore APIs. The five Ambiq calls are now
closed by a local exact-ABI adapter over the already source-qualified G2 cache
and peripheral-power implementations. Its warning-free 11,320-byte isolated
Cortex-M55 object has no ELF imports and SHA-256
`04504e7e026eb53a08a187e037269d0f42a2e818842fc5320710c2a5952a06b7`.

With that provider, LVGL core, target C, compiler runtime, libm, and an
unused-archive helper, the complete maximal residual initially contained 73
symbols. The final three FreeRTOS queue/semaphore imports are now closed by an
exact-ABI adapter over the authenticated G2 FreeRTOS V10.5.1 queue sources. Its
warning-free 6,404-byte Cortex-M55 object has no ELF imports and SHA-256
`926b0597a2d78ea441151b2c21cfc813be29bb246606b2a6b0c5d84e5b175608`.

The next source-resolvable, software-only tranche closes 14 LVGL utility
imports: nine area operations, color-format BPP, two event accessors, and two
matrix operations. The isolated 7,452-byte Cortex-M55 provider has exactly
those exports, no ELF import or external relocation, no fixed address, and
SHA-256
`9342103b5ae256c72221216d754d21020a92218fbd3024d7e17303ed6ef7111a`.
Its source semantics are bounded by the authenticated LVGL compatibility
commit and a separate ABI probe.

An additional isolated provider closes eleven dependency-free array, cache
callback, image, font/FreeType descriptor, transform, and memory APIs. Its
6,692-byte Cortex-M55 object has exactly those exports, no ELF import or
external relocation, no fixed address, and SHA-256
`bcebd4a63cc1366be7ab0006fdab5f31e6645a3583c4aa9a0d72d9ea9ce932a4`.
The two cache operations have explicit caller-supplied indirect callback
boundaries; they are not hardware-qualified by this result.

A subsequent zero-import target-runtime provider closes `memcpy`, `memset`,
`__aeabi_memcpy4`, `__aeabi_d2lz`, and `__aeabi_f2ulz`. Its 2,736-byte
Cortex-M55 object has exactly those exports, no ELF import or external
relocation, no fixed address, and SHA-256
`c009f816e4d59547783e88272d77bf9fccaf765f5d66d6339fc3296ca4256bf7`.
The separate ABI object pins hard-float-to-base-PCS argument marshalling for
both conversion helpers.

The next zero-import scalar-math tranche closes `acosf`, `atan2f`, `atanf`,
`fmod`, and `fmodf` from authenticated musl `v1.2.5` sources. Its 6,576-byte
Cortex-M55 object has exactly those exports, no ELF import or external
relocation, no fixed address, and SHA-256
`123f1163b67fa953c3a77aa9ce3da7652fa6aae1001dc206b9f742f75f14a1af`.
The pinned invalid-input patch avoids unavailable binary64 runtime helpers in
the fmod error paths and deliberately makes no floating-exception claim.

Four notify-mode-independent LVGL FreeRTOS mutex APIs are then closed by an
isolated exact-ABI adapter. Its 2,168-byte Cortex-M55 object has exactly those
exports, zero ELF imports, and six enumerated calls to already source-owned
canonical FreeRTOS entries. Its SHA-256 is
`5067d94d102f8f6ce7090534a482657761ddee527f796db2cb330bedb36baf3a`.

The remaining four scalar math imports, `cosf`, `sinf`, `sqrt`, and `tanf`,
are closed by an isolated authenticated musl `v1.2.5` provider compiled for
the Apollo510-supported FPv5-D16 instruction set. Its 13,144-byte Cortex-M55
object exports exactly those APIs, has no ELF import, external relocation, or
fixed address, and has SHA-256
`3b67eea354a8f12f48faed3177b9d170fa7c8191ced9e30803cbe6b31b2e8c8a`.
This is source/ABI admission only; optional-DP FPU runtime state, rounding,
collision review, and hardware behavior remain unqualified.

The later authenticated heap/array provider closes five more APIs;
descriptor-owned draw-buffer destruction closes one; conservative section GC
removes only the unreferenced private glyph/UTF-8 section; and the exact
492-byte default `lv_global` storage object closes one data import. The bounded
FreeType outline-event setter then closes one callback-registration import.
Authenticated draw-buffer create/reshape then close two bounded descriptor
shape APIs. The zero-import fmt_txt bitmap provider closes one more. The
vector-task lifecycle provider closes one more, and the draw-unit creation
provider closes the exact authenticated global-list insertion API. The current
draw-dispatch request provider then closes the exact two-signal wrapper. The
task-notification-mode sync-signal provider closes its formerly residual
dependency with three source-owned fixed FreeRTOS entries. The current maximal
ledger contains 11 symbols and no Nema, Apollo HAL,
FreeRTOS queue, admitted LVGL utility/stateless/mutex/heap/array/destroy/
global-storage/FreeType-event/draw-buffer-shape/font-format/vector-destroy/
draw-unit-create/draw-dispatch-request API,
admitted memory/AEABI conversion, or admitted nine-symbol math import. Its
canonical digest is
`f9d7f5b3fc8db9a19441ec0c4991ac9161c0ae46583e56c2a2298f2794732744`.
The 1,370,696-byte maximal partial link has SHA-256
`d1c96688dfd7e7c845a9b4e0bcb2610bc239d881c89aa79e09faefc8d0bcd8cf`.

These are compile and relocation results, not production admission.

## Scoped evidence inventory

The search was deliberately bounded to this repository, `/Users/kalani/Repo`
via `rg --files`, and exact SDK roots already named by the provenance record.
No broad home-directory scan was used. This repository contains 20 MIT
clean-room GPU candidates totaling 57,754 bytes, but none exports the required
production ABI and none is counted as a provider.

The precise sibling AmbiqSuite paths contain:

- `libraries/lib_nema_apollo5x_nemagfx.a`: 1,809,800 bytes, SHA-256
  `109840f6e0bbeb8618a1a853966cdf68cf169620bcc4075ed7a1c86ab0d3286f`;
- `extensions/gpu_patch.a`: 51,902 bytes, SHA-256
  `31a0e5494cf27a3794212118c152513c16efa0424c51311c70a6f55024b4c95c`;
- `port/nema_hal.c`: 17,527 bytes, SHA-256
  `053044dd8db3a84e57ff1c55200fdfefaef3e463361ea8de3fc238c40ed51cac`.

Those public artifacts are pinned to Ambiq commit
`b853fded7e545f005727e13bf2ce83018c7e242d`. The public HAL is a Zephyr port,
not the G2 CMSIS-FreeRTOS port, and it does not implement
`nema_wait_irq_brk`. The Think Silicon implementation license is permissive;
the GPU patch is BSD-3-Clause. Binary redistribution/notice review is still an
explicit gate.

The Apollo510-EVB source is:

`ThirdParty/ApolloSDK/third_party/ThinkSi/config/apollo510_nemagfx/nema_hal.c`

It is 21,402 bytes, SHA-256
`643e5769126db273c638348c9f2aa0d7f0448a75fcc88c968c0e0bdd3a107416`,
Git blob `af266492d4dd1f117f56fd1d8481fcc7206d659f`, and carries the Think Silicon
permissive license. The source exists in sibling private-repository commit
`edbf8d8e324029f4cd9071b490dd125f97e1bf95` (introduced by
`88f3c6c4fe7da2d2c90debbc118984e2bef49071`). No public upstream commit for
that exact source was authenticated. Consequently it is an evidence-bearing
candidate, not an importable public provider.

The IAR Nema archive observed in the same scoped SDK is 2,415,368 bytes with
SHA-256 `73130c6c2bdef8151f25c7cc43d15d79bd064d8942f2b3bbd66484f06c8005a5`.
LLVM can inspect and partially link it, but emits 18 unknown floating-point
extension warnings. It is not admitted as a substitute for the clean GCC
route, and stock-IAR/GNU compatibility remains a policy and toolchain gate.

## Deterministic gate

`tools/audit_g2_lvgl_nema_link.py` authenticates source, headers, archives, EVB
source/configuration, symbol sets, archive member selection, and every pinned
transitive relocation. Default mode needs no external SDK: it reproduces the
15 backend objects, the two-symbol helper object, the isolated ten-input
Apollo HAL provider, the isolated five-object FreeRTOS provider, and the
isolated zero-import LVGL utility, stateless, target-runtime, math, and
FPv5-D16 math providers plus the fixed-source-boundary mutex, heap/array,
draw-buffer-destroy/shape, exact global-storage, and FreeType outline-event providers and
emits the complete precomputed missing-provider ledger in
`tools/manifests/g2-lvgl-nema-link-admission.json`. Any omitted or duplicate
residual symbol is a hard error.

When the exact scoped SDK roots are available, run from `g2`:

```sh
python3 tools/audit_g2_lvgl_nema_link.py \
  --sdk-root /Users/kalani/Repo/evenrealitiesg2-swiftsdk/openCFW/sdks/AmbiqSuite_v5 \
  --evb-root /Users/kalani/Repo/evenrealitiesg2-swiftsdk/openCFW/sdks/Apollo510-EVB \
  --output-dir /tmp/g2-lvgl-nema-link
python3 -m unittest -v tests.test_audit_g2_lvgl_nema_link
python3 -m unittest -v tests.test_runtime_lvgl_ambiq_nema_buffer_helpers
python3 -m unittest -v tests.test_runtime_lvgl_ambiq_apollo_hal_provider
python3 -m unittest -v tests.test_runtime_lvgl_ambiq_freertos_queue_provider
python3 -m unittest -v tests.test_runtime_lvgl_ambiq_lvgl_core_provider
python3 -m unittest -v tests.test_runtime_lvgl_ambiq_lvgl_stateless_provider
python3 -m unittest -v tests.test_runtime_lvgl_ambiq_target_runtime_provider
python3 -m unittest -v tests.test_runtime_lvgl_ambiq_math_provider
python3 -m unittest -v tests.test_runtime_lvgl_ambiq_math_dp_provider
python3 -m unittest -v tests.test_runtime_lvgl_ambiq_lvgl_mutex_provider
python3 -m unittest -v tests.test_runtime_lvgl_ambiq_lvgl_heap_array_provider
python3 -m unittest -v tests.test_runtime_lvgl_ambiq_lvgl_draw_buf_lifecycle_provider
python3 -m unittest -v tests.test_runtime_lvgl_ambiq_lvgl_global_storage_provider
python3 -m unittest -v tests.test_runtime_lvgl_ambiq_lvgl_freetype_event_provider
python3 -m unittest -v tests.test_runtime_lvgl_ambiq_lvgl_draw_buf_shape_provider
```

The EVB compile uses Arm-none-EABI Cortex-M55, Thumb, hard float, short enums,
GNU C11, the pinned EVB include/configuration closure, a 128 KiB Nema heap,
100 pending command lists, and the binary-semaphore IRQ route. The generated
HAL object is 141,144 bytes with SHA-256
`483323ec728723bf0354be8bba7bd3be74346f2fe61d15f0407efc06309ba64e`.
Paths are prefix-mapped for deterministic output. No external binary is copied
into this repository.

## Remaining gates

Production admission remains fail-closed on:

1. production-overlay registration of the locally compiled helper, Apollo HAL,
   FreeRTOS queue, LVGL utility/stateless/mutex/heap/array/destroy/global-storage,
   target-runtime, and both math providers after a deliberate G2 routing,
   FPU-state, RAM-ownership, initialization-order, and collision review;
2. scheduler-runtime validation of the FreeRTOS provider's fixed call and RAM
   dependencies, including ISR priority, wake/yield, timeout, and allocation;
3. G2-specific Nema memory-pool, IRQ, cache, power-retention, and toolchain
   configuration rather than the EVB example configuration;
4. exact configuration and atomic source admission for the remaining 16 LVGL
   thread/sync OSAL, draw scheduling/layer, decoder/cache, logging, and
   global-state initializer
   imports; in particular, the FreeRTOS task-notification selection is not
   recovered;
5. archive redistribution/notice approval and a deliberate GNU-versus-stock-
   IAR route; and
6. authorized Apollo510/G2 command-list, IRQ, cache, suspend/resume,
   antialiasing, and display-output evidence.

No authorized physical target identity, transport, captured GPU trace, or
display observation was supplied. The hardware gate is therefore explicitly
blocked by unavailable physical evidence; this audit does not claim live
hardware behavior or a complete functional firmware image.
