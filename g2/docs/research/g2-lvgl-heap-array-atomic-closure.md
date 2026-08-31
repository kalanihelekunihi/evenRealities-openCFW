# G2 LVGL heap/array atomic closure

This note records a software-only admission boundary for five symbols required
by the retained Ambiq draw objects. It does not register an overlay, qualify a
live heap, or establish display/GPU behavior.

## Selected source boundary

The implementation is in
`third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_heap_array_provider.c`.
Its valid-input behavior and ABI are transcribed from the authenticated LVGL
tree at commit `344c7c318047b7348e1be8572a9fd4260c251cfa`, tree
`2c76db856ec570f3ee12565181e5cf52bdd33d78`:

- `src/stdlib/lv_mem.c`, Git blob
  `41a002d7452d0efbdda5f66ab7a28048c50792bb`;
- `src/misc/lv_array.c`, Git blob
  `4f7b97a348c2bd8c210546db5e45b2c309d7ec05`; and
- `src/misc/lv_array.h`, Git blob
  `c8a159081d64467d2d9e9a1d27bffbcb5338c05d`.

The selected custom-allocation boundary is not inferred from raw TLSF. It uses
the already source-owned synchronized G2 heap facade entries:

| Entry | Role |
|---:|---|
| `0x00474CD2` | allocate |
| `0x00474D16` | free |
| `0x00474D54` | reallocate |

This preserves the G2 facade's mutex and heap-handle ownership rather than
calling the two-argument TLSF core with an invented handle.

## Closed surface

The isolated Cortex-M55 object exports exactly `lv_malloc`,
`lv_malloc_zeroed`, `lv_free`, `lv_array_deinit`, and `lv_array_push_back`.
It has zero undefined ELF symbols. Its three fixed calls are enumerated above.
The ABI probe fixes the 20-byte ILP32 `lv_array_t` layout and has one Thumb tail
relocation to each public function. The retained draw objects contain 41
consumer relocations across this five-symbol surface.

The target provider is 3,060 bytes with SHA-256
`e37759628d884e20f3c788d7b16e21997a667fddd8a6271e2cdd818a74661458`.
The target ABI probe is 2,472 bytes with SHA-256
`028f1e607d6aac51df51f26535be9a42edc60475afa2e71c78deff7c3c81faba`.

Malformed null/inconsistent descriptors, capacity and byte overflow, pointer
overflow, external-buffer growth, overlapping copies, and reallocation failure
fail closed. Zero-sized allocations return one stable provider-local non-heap
byte, matching LVGL's observable public behavior without depending on
`lv_global`.

## Descriptor-owned draw-buffer destruction

The next independently bounded function is `lv_draw_buf_destroy`, transcribed
from authenticated `src/draw/lv_draw_buf.c` Git blob
`58562a86e55ca5897c3b79b3a486d3f7107aeea0`. Its target object exports only
that ABI and imports only the reviewed `lv_free` symbol. The isolated object is
1,192 bytes with SHA-256
`4b633e5f8f0b2fe765678d8525317aa4c8df3e10d4c22a5e216baeb6393888ca`.
The combined heap/array/lifecycle link has zero undefined symbols and is 3,584
bytes with SHA-256
`ee9e7d0d5419d12a70e3707b99bac1b6bc4ce79c536aa811d3a027ea7c303823`.

For valid allocated descriptors, the descriptor-owned `buf_free_cb` is called
with `unaligned_data` before the descriptor is released. Null, non-allocated,
and allocated/null-handler descriptors fail without an indirect or heap call.
The callback remains caller-owned, so this is an ABI and dependency-link
admission rather than callback implementation qualification.

## Residual and evidence limit

The heap/array tranche moves the exact maximal residual from 27 to 22 symbols;
descriptor-owned destruction moves it again to 21. A conservative section-GC
link then roots all 39 externally visible functions from the 15 exact Ambiq
backend objects and retains all 96 direct Nema/GPU requirements. That proof
drops the unreferenced `lv_ambiq_get_glyph` archive section and its sole private
`utf8_codepoint_size` import without selecting an unauthenticated malformed
UTF-8 policy. That intermediate residual was 20 symbols. The subsequent exact
default-global storage admission moves it to 19 symbols. The subsequent
FreeType outline-event setter admission moves it to 18; draw-buffer
create/reshape move it to 16, the zero-import fmt_txt provider moves it to 15,
and the vector-task lifecycle provider moves it to 14. The bounded draw-unit
creator then moves it to 13; the exact two-signal draw-dispatch request wrapper
moves it to 12. Its task-notification-mode sync-signal dependency is now
source-admitted through three pinned FreeRTOS fixed entries, moving the current
residual to 11. The sorted digest is
`f9d7f5b3fc8db9a19441ec0c4991ac9161c0ae46583e56c2a2298f2794732744`.

The current scoped section-GC maximal object is 1,370,696 bytes with SHA-256
`d1c96688dfd7e7c845a9b4e0bcb2610bc239d881c89aa79e09faefc8d0bcd8cf`.
The exact root-set digest is
`81c9819050afa8b9e07fd08ee11f1023bcf577b7f466fc2577d2b597bcde91f3`.
This is link admission, not a substitute UTF-8 implementation and not a claim
that the unused glyph accessor is hardware-qualified.
The draw-buffer create/reshape provider is now source-admitted behind the four
retained-Ambiq-initializer-owned indirect callbacks (`buf_malloc_cb`,
`buf_free_cb`, `align_pointer_cb`, and `width_to_stride_cb`). The still-open
draw task-selection/layer functions use global state and scheduler sync, while decoder
open/close use global decoder/cache ownership. The exact `lv_global` storage
object is source-admitted, but its initializer/handler state is not.
Copying those functions without the hidden state closure would be a false
admission.

Production routing remains false. Live mutex behavior, heap handle and RAM
placement, coexistence with any canonical LVGL allocation provider, allocation
failure under scheduler load, and all GPU/display behavior require separate
target integration and authorized-hardware evidence.
