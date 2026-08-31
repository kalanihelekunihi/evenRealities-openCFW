# G2 LVGL global-storage source admission

This note records a software-only source and link admission for the default
LVGL global object required by the retained Ambiq draw-buffer object. It does
not register a production route, run an initializer, populate a handler, or
claim hardware behavior.

## Authenticated boundary

The remaining `lv_global` requirement is an Arm ELF data-object ABI, not a
function. `lv_draw_ambiq_buffer.o` contains exactly one
`R_ARM_THM_MOVW_ABS_NC` and one `R_ARM_THM_MOVT_ABS` relocation to it.

The definition `lv_global_t lv_global;` and public type come from authenticated
LVGL commit `344c7c318047b7348e1be8572a9fd4260c251cfa`, tree
`2c76db856ec570f3ee12565181e5cf52bdd33d78`:

- `src/lv_init.c`, Git blob `e0c58a2d65c835f5ea93f946b030d2c58a012dd1`;
- `src/core/lv_global.h`, Git blob
  `4515c01c9b80779a7d61701e28b4fb3554a92ba9`.

The G2 configuration/layout recovery independently fixes the object size at
`0x1EC`, the three 32-byte Ambiq handler tables at offsets `0xC8`, `0xE8`, and
`0x108`, and the stock object base at `0x2006F548`. The provider contains
compile-time assertions for all of these structural facts except placement,
which is separately asserted by the isolated linker proof.

## Result

`third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_global_storage_provider.c`
exports exactly one 492-byte `OBJECT/BSS` symbol, `lv_global`, and has no ELF
imports. Its deterministic artifacts are:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| target source object | 716 | `11ce9df99cecff701ba5ba4d8b8f3e17f6db562ac56f0c2b3a40378187c6dca3` |
| section-GC provider | 796 | `a11c7c766758ae759bd4f0fc198246d3eab4425cb1a9b57b5d12905a6687966a` |
| target ABI probe | 1,036 | `1a7890f722106fa2b0a39e8a3fbe909965f6f06fb1858cabe7bac8b001f3f211` |
| isolated placement ELF | 63,396 | `7165c79720cca1c7f333ac4eeb9d1e68ce223888ebb18722b15e7be200d0ef40` |

The placement proof maps only `.bss.lv_global`, asserts its `0x1EC` extent,
and proves the symbol value `0x2006F548`. It is evidence that the source object
can satisfy the recovered stock address; it is not a production linker-script
change. A negative target compile enables the incompatible software-mask
cache layout and proves that the provider's size assertion rejects it.

There is no callable or hostile-input surface: ordinary C static-storage
semantics supply the initial all-zero representation. The test therefore
checks exact object type, extent, absence of imports, consumer relocation ABI,
placement, and incompatible-layout rejection rather than inventing a runtime
input oracle.

This admission moves the maximal residual from 20 to 19 symbols. The sorted
residual digest is
`b40c5c6285957b316ee3444c405e255a27d9651fb82cc4c19f7d2477f1d0f2b3`.
The maximal scoped partial link is 1,362,660 bytes with SHA-256
`75cb28f5068e26a33c0ab2f653f29c8b9f05b4ec798b3a05c29bddfdd9ffa3cc`.
The later FreeType outline-event setter admission uses this object as its sole
reviewed import and moves the current residual to 18; that separate boundary
is recorded in `g2-lvgl-freetype-event-source-admission.md`.

## Remaining boundary

Production routing stays false. The canonical link must still prove that no
other `lv_global` definition collides, reserve the exact RAM extent, establish
zeroing and `lv_init`/Ambiq handler initialization order, and preserve every
other owner of the recovered global layout. This provider supplies no default
handler callbacks, decoder/cache state, scheduler state, heap ownership, MMIO,
or Nema behavior. No authorized hardware evidence was available.
