# G2 LVGL core utility-provider source admission

Status date: 2026-08-30  
Scope: software-only LVGL imports retained by the Ambiq draw backend  
Mode: authenticated source semantics, bounded exact-ABI provider, hostile host
tests, and deterministic Cortex-M55 link audit; no production routing,
firmware image, flashing, MMIO, scheduler execution, or hardware operation

## Result

The largest coherent residual tranche that needs no allocator, operating
system, font engine, decoder, global LVGL state, C library, libm, compiler
runtime, or hardware is now closed in isolation. The provider exports exactly:

- nine `lv_area_*` functions (`get_height`, `get_width`, `increase`,
  `intersect`, `is_in`, `move`, `set`, `set_height`, and `set_width`);
- `lv_color_format_get_bpp`;
- `lv_event_get_code` and `lv_event_get_param`; and
- `lv_matrix_transform_point` and `lv_matrix_translate`.

These 14 symbols own 123 observed `R_ARM_THM_CALL` relocations across the exact
Ambiq backend objects. Every consumer, relocation type, and count is recorded
under `local_lvgl_core_provider.closed_consumer_relocations` in the checked
manifest. None of the symbols remains in the maximal missing-provider ledger.

At this admission stage, the residual moved from 70 to 56 symbols. The
remainder was exactly 41 LVGL core imports, 14 target compiler/C/libm imports,
and the private
`utf8_codepoint_size` GPU-patch helper. Its sorted canonical digest is
`635c5351196d2b87a2a2e10ffc48a70f87a7e47c8ecd4cac767b072015ecfae6`.

## Authenticated semantics and ABI

The semantic ceiling is official LVGL commit
`344c7c318047b7348e1be8572a9fd4260c251cfa`, tree
`2c76db856ec570f3ee12565181e5cf52bdd33d78`, under MIT. The pinned tree record
authenticates the exact upstream blobs for `lv_area.c`, `lv_color.c`,
`lv_event.c`, `lv_matrix.c`, and `lv_draw_vector.c`. This remains a compatible
official source ceiling, not a claim that Even used that exact checkout.

The ABI probe is compiled for `arm-none-eabi`, Cortex-M55, Thumb, hard float,
short enums, freestanding GNU C11, and warnings as errors. It checks 32-bit
pointers, the 16-byte `lv_area_t`, 36-byte `lv_matrix_t`, one-byte color-format
enum, four-byte event-code enum, and exact public function pointer types. The
896-byte probe has SHA-256
`f194076301eaed4ecabf74b3d4df75e227f443c1b33d945ee9b545cdb66d71e8`.

The provider is retained with `ld.lld -r --gc-sections`. The resulting
7,452-byte object has SHA-256
`9342103b5ae256c72221216d754d21020a92218fbd3024d7e17303ed6ef7111a`,
exactly 14 external exports, zero ELF undefined symbols, zero external
relocations, and no fixed-address dependency. This proves an isolated source
and ABI closure only; the object is not registered in the core overlay.

## Bounded failure behavior

For inputs in the defined LVGL source domain, the algorithms preserve the
pinned upstream results. The adapter defines previously undefined hostile
cases without inventing a platform dependency:

- null area and matrix mutators are no-ops;
- null area getters return zero, intersection/containment return false, a null
  event returns `LV_EVENT_ALL`/null, and a null matrix/point transform is a
  no-op;
- coordinate updates use explicit two's-complement modular arithmetic, so
  signed overflow cannot trigger C undefined behavior;
- malformed or arithmetically unrepresentable rounded holders fail closed;
  and
- unknown color-format values return zero BPP, matching upstream's default.

The host oracle covers ordinary and disjoint intersections, rounded-corner
containment, nulls, `INT32_MIN`/`INT32_MAX` coordinate updates, invalid color
formats, event preprocessing, identity translation, non-identity matrix
multiplication, and null matrices/points under AddressSanitizer and
UndefinedBehaviorSanitizer.

## Reproduction and remaining boundary

From `g2`:

```sh
python3 tools/audit_g2_lvgl_nema_link.py \
  --write-manifest tools/manifests/g2-lvgl-nema-link-admission.json
python3 -m unittest -v tests.test_runtime_lvgl_ambiq_lvgl_core_provider
python3 -m unittest -v tests.test_audit_g2_lvgl_nema_link
```

The 41 LVGL imports remaining at this stage were intentionally not guessed.
They cross one or
more unrecovered configuration boundaries: custom allocation, FreeRTOS OSAL,
LVGL global layout/state, draw-buffer handlers, decoders, FreeType/font data,
logging, vector task destruction, or full draw scheduling. Production use
requires an atomic, configuration-exact LVGL source link and collision review,
not merely registration of this isolated provider.

A subsequent independently audited stateless tranche closed eleven of those
imports and moved the residual to 45; a later target-runtime tranche moved the
current residual to 40. See `g2-lvgl-stateless-provider-source-admission.md`
and `g2-lvgl-target-runtime-provider-source-admission.md`; this document
retains the historical 70-to-56 accounting for the utility provider itself.

No physical target identity, transport, GPU trace, framebuffer capture, or
display observation was supplied. This software-only tranche has no hardware
dependency, while complete Nema/Apollo behavior remains explicitly blocked on
unavailable authorized physical evidence.
