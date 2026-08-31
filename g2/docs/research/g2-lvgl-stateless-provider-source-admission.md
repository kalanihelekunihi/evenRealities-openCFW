# G2 LVGL stateless-provider source admission

Status date: 2026-08-30  
Scope: software-only LVGL imports retained by the Ambiq draw backend  
Mode: authenticated source semantics, bounded exact-ABI provider, hostile host
tests, and deterministic Cortex-M55 link audit; no production routing,
firmware-image integration, scheduler execution, MMIO, flashing, or hardware
operation

## Result

Eleven more residual LVGL imports are closed by the component-local
`lvgl_ambiq_lvgl_stateless_provider.c` in isolation:

- `lv_array_at` and `lv_array_init_from_buf`;
- `lv_draw_buf_flush_cache` and `lv_draw_buf_invalidate_cache`;
- `lv_draw_image_dsc_init` and `lv_image_buf_get_transformed_area`;
- `lv_font_get_glyph_bitmap`;
- `lv_freetype_is_outline_font` and `lv_freetype_outline_get_scale`; and
- `lv_memcpy` and `lv_memset`.

These symbols own 28 retained backend relocations. Twenty-seven are
`R_ARM_THM_CALL`; the second `lv_array_init_from_buf` consumer relocation is
an observed `R_ARM_THM_JUMP24` tail call. The checked manifest pins each
consumer object, relocation type, and count under
`local_lvgl_stateless_provider.closed_consumer_relocations`.

This moves the maximal residual from 56 to 45 symbols. The canonical sorted
residual digest is
`20d154a0d88c483967a1aa3b48895a1f5ee2d612c8491ed0b24a38a2db9a29bb`.
With the exact scoped AmbiqSuite and Apollo510-EVB inputs available, the new
maximal partial is 1,573,920 bytes with SHA-256
`b0b417a2f4fcd66b1fbf5613f77dab1bb0cc286d976fc43098ac92ec1407f0ed`.
This remains a source/link admission result, not a production route.

## Why this tranche

The prior 56-symbol residual contained 41 `lv_*` symbols, but those symbols do
not form one independently linkable provider. The ten FreeRTOS OSAL imports
depend on the unrecovered `LV_USE_FREERTOS_TASK_NOTIFY` selection and on task,
semaphore, notification, timeout, and scheduler state. Choosing either OSAL
mode without evidence would manufacture an ABI and runtime policy. The
allocator/draw/decoder/global/font-format groups likewise require maintained
state and broader collision-safe source admission.

The eleven functions above form the largest dependency-closed subgroup found
after following their pinned LVGL source call graph: they require no allocator,
OS, LVGL global, font engine execution, decoder registry, draw scheduler, C
library, libm, compiler runtime, fixed address, or direct hardware access. Two
cache helpers can invoke only function pointers already supplied in the caller's
draw-buffer handlers. Those indirect callbacks are enumerated in the manifest;
their implementations and any hardware effects remain caller-owned and
unqualified.

## Authenticated semantics and inputs

The semantic ceiling is official LVGL commit
`344c7c318047b7348e1be8572a9fd4260c251cfa`, tree
`2c76db856ec570f3ee12565181e5cf52bdd33d78`, under MIT. The tree record pins
these upstream blobs:

| Source | Git blob SHA-1 |
| --- | --- |
| `src/draw/lv_draw_buf.c` | `58562a86e55ca5897c3b79b3a486d3f7107aeea0` |
| `src/draw/lv_draw_image.c` | `ee29d6b7a0b468bae8ce8913d090b22ef35a17b3` |
| `src/font/lv_font.c` | `a509621cc02be9022f8e947e491e814daab5a29d` |
| `src/libs/freetype/lv_freetype_outline.c` | `f7d5edbd0ddd40e3ed6a62a66916b10c72974ac7` |
| `src/misc/lv_area.c` | `34743e8e540c5a8e8fd7607b9015cca50c6e5010` |
| `src/misc/lv_array.c` | `4f7b97a348c2bd8c210546db5e45b2c309d7ec05` |
| `src/misc/lv_math.c` | `a6d51a0555d2e33eb69ca7a5c182fc83a26cac0b` |
| `src/stdlib/builtin/lv_string_builtin.c` | `9c28592a0dfcd1dd5712630456a450f9b61ad1b4` |

The auditor additionally pins the provider, header, ABI probe, hostile host
fixture, tree record, and commit record by path, byte count, SHA-256, and
license. Any identity change fails closed before compilation.

## Target ABI and import closure

The provider and ABI probe compile against the staged G2 compatibility tree
for `arm-none-eabi`, Cortex-M55, Thumb, hard float, short enums, freestanding
GNU C11, `LV_USE_OS=LV_OS_FREERTOS`, recovered
`LV_DRAW_THREAD_STACK_SIZE=32768`, custom LVGL allocation, FreeType, vector,
matrix, and float support, with all warnings as errors.

The target source object is 5,412 bytes with SHA-256
`6b1b93bad33f4710a7ec8987765b43d0fc90e0786801009eca36e7325fa5da73`.
The 908-byte ABI probe has SHA-256
`3e99b5d4ca068929d9e7e8dcae18e326da666b04c77b24589462c760b02f76b1`.
It asserts four-byte pointers, 20-byte `lv_array_t`, 28-byte `lv_draw_buf_t`,
the patched 32-byte G2 `lv_draw_buf_handlers_t`, and exact function pointer
compatibility for every export.

`ld.lld -r --gc-sections` retains the eleven APIs into a 6,692-byte object with
SHA-256
`bcebd4a63cc1366be7ab0006fdab5f31e6645a3583c4aa9a0d72d9ea9ce932a4`.
It has exactly eleven external definitions, zero undefined symbols, zero
external relocations, and zero fixed-address imports.

## Bounded hostile behavior

Defined-domain inputs preserve the pinned LVGL algorithms. Inputs for which
upstream relies on assertions or otherwise has no defined result are bounded:

- null arrays, descriptors, fonts, draw buffers, handlers, callbacks, and
  memory pointers return a neutral value or no-op;
- array index and byte-offset arithmetic is checked before pointer formation;
- a null backing buffer has zero usable capacity;
- malformed FreeType descriptors, missing cache nodes, and zero reference size
  return false or zero;
- negative image dimensions produce an empty result area; and
- transform intermediates use bounded 64-bit arithmetic and explicit
  two's-complement conversion instead of signed-overflow undefined behavior.

The host oracle exercises normal results, callback dispatch and full-area
construction, descriptor defaults, font callbacks, FreeType magic/render/scale
checks, identity and rotated/scaled transforms, nulls, zero-length memory
operations, extreme dimensions/angles, invalid indexes, and zero reference
size under AddressSanitizer and UndefinedBehaviorSanitizer.

## Reproduction and remaining boundary

From `g2`:

```sh
python3 tools/audit_g2_lvgl_nema_link.py \
  --write-manifest tools/manifests/g2-lvgl-nema-link-admission.json
python3 -m unittest -v tests.test_runtime_lvgl_ambiq_lvgl_stateless_provider
python3 -m unittest -v tests.test_audit_g2_lvgl_nema_link
```

The provider is not registered in the Apollo core overlay. The remaining 45
symbols still require an atomic configuration-exact link for allocator, OSAL,
font-format, draw, decoder, vector destruction, logging/global state, target
C/compiler/libm runtime, and the private `utf8_codepoint_size` helper.

A subsequent independently audited target-runtime tranche closes five of
those symbols and moves the current residual to 40. See
`g2-lvgl-target-runtime-provider-source-admission.md`; this document retains
the historical 56-to-45 accounting for the stateless provider itself.

No authorized physical target identity, transport, GPU trace, framebuffer
capture, or display observation was supplied. The software-only exports do not
need live hardware to establish their isolated C/ABI closure; complete
Apollo510/Nema behavior remains blocked on unavailable physical evidence.
