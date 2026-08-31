# G2 liblc3 source providers

SPDX-License-Identifier: Apache-2.0

This directory contains both the original production-excluded encoder candidate
and a production-capable bounded source provider around the authenticated,
unmodified Google liblc3 v1.1.3 snapshot in `third_party/liblc3`. The provider
admits one mono encoder at a time with caller-owned storage, byte-exact PCM and
output bounds, alias checks, and a sealed normalized plan. It does not allocate
memory, route an overlay entry, or perform hardware I/O. Its fail-closed source,
ABI, compile, relocation, and placement contract is recorded in
`encoder_source_admission.json`; production routing remains false.

This directory also contains a production-capable, bounded LTPF analysis
provider. It validates the complete 1160-byte analysis-state ABI, duration and
rate enums, input history and alignment, and fixed-width result ABI before
calling pristine upstream `lc3_ltpf_analyse`. It admits `ltpf.c` as maintained
Apache-2.0 source through a new subsystem entry; it does not claim byte identity
with the stock compiler output.

All seven upstream resampler dispatch slots are exercised in host behavior
tests and emitted by the Cortex-M55 compile test. The stock 16K and 48K entry
bodies at `0x00438400` and `0x00438604` remain incomplete historical boundaries
and are never routed individually. A normal source build can provide those
rates through upstream `ltpf.c` without relying on either historical extent.
`ltpf_source_admission.json` records the target profile, ABI, relocation seams,
object budgets, and fail-closed routing decision.

The candidate covers the four public APIs already authenticated in the stock G2
call graph (`lc3_frame_samples`, `lc3_frame_bytes`, `lc3_setup_encoder`, and
`lc3_encode`) and adds fail-closed checks which the upstream low-level API leaves
to its caller. The test compares a bounded interleaved-S16 encode with a pristine
direct upstream call using independent encoder states.

## Required G2 compile profile

All liblc3 translation units and this adapter must use:

- Cortex-M55 Thumb, hard-float AAPCS;
- `-fshort-enums`, because stock stores `dt`, `sr`, and `sr_pcm` at encoder
  offsets 0, 1, and 2 (the candidate also pins the 0x4ac sample-buffer offset
  and complete 0x4b0-byte fixed state);
- `-ffast-math`, matching the authenticated upstream build requirement; and
- consistent `LC3_PLUS` / `LC3_PLUS_HR` definitions (the snapshot defaults both
  to enabled).

The adapter statically rejects a normal four-byte-enum build. Its external
configuration and plan structs use only fixed-width fields, and the target
candidate state is pinned to 44 bytes.

`target_compat/math.h` and `target_compat/string.h` are declarations only. They
let the complete pristine snapshot compile with a bare Clang arm-none-eabi
frontend without pretending to provide a C library. A production link still
needs reviewed providers for:

- `memcpy`, `memmove`, and `memset` (or the compiler's corresponding Arm EABI
  lowering);
- `fabsf`, `floorf`, `fmaxf`, `fminf`, `roundf`, `sqrtf`, and `truncf`; and
- compiler-runtime `__aeabi_memclr` and `__aeabi_memclr4` for the retained
  encoder closure. `__aeabi_uldivmod` occurs only in sections discarded by the
  section-GC qualification link.

Those are link-provider seams, not opaque liblc3 algorithms. The specialized
service-audio replay now supplies ten of the exact retained seams from
`runtime_liblc3_target_runtime.[ch]` and binds `sqrtf` to the authenticated
source-owned core leaf. Both target profiles finish with zero imports and zero
relocations; this does not install the providers into a stock image. Remaining
admission gates are atomic package placement/integrity application, WCET/stack
measurement for the G2 audio cadence, recovered `service_audio.c` final patch
application, and interoperability/device qualification. The stock
ownership/lifetime adaptation and exact two-entry ABI transition are now
implemented in
`runtime_liblc3_service_audio_adapter.[ch]` and
`runtime_liblc3_service_audio_stock_shim.[ch]`; the latter accepts only the four
authenticated context addresses and only transitions a valid 24-byte stock
header whose cached encoder pointer remains zero. The latter tests are
intentionally outside this software-only candidate.

Run the isolated qualification with:

```sh
cd g2
python3 -m unittest -v tests.test_runtime_liblc3_encoder_candidate
python3 -m unittest -v tests.test_runtime_liblc3_encoder_provider
python3 -m unittest -v tests.test_runtime_liblc3_ltpf_provider
python3 -m unittest -v tests.test_runtime_liblc3_service_audio_adapter
python3 -m unittest -v tests.test_runtime_liblc3_service_audio_stock_shim
```

The complete encoder source closure has a deterministic build-only integration
at `components/apollo_main/liblc3_encoder`. It emits unplaced text, read-only
table, writable table, and relocation-bearing object artifacts while enforcing
the exact retained runtime-import allowlist. It does not emit firmware or route
the recovered audio service.

The bounded LTPF analysis route is admitted independently at
`components/apollo_main/liblc3_ltpf`. It closes the analysis-only `memmove`
and nonnegative `sqrtf` seams in Apache-2.0 source, authenticates all seven
absolute dispatch-table relocations, and replaces only the stock `lc3_encode`
BL at `0x0059145C`. Apple Clang 21 emits 7,576 source-owned bytes and
Homebrew Clang 22 emits 7,596; both profiles are independently SHA-pinned.
The historical 16/48 kHz corpus bodies remain individually unrouted.
