# G2 LVGL FreeType outline-event source admission

This note records a software-only admission for
`lv_freetype_outline_add_event`. It does not create or initialize the FreeType
context, register a production route, or claim GPU/display behavior.

## Source and semantics

The function and its context accessor/layout are authenticated to LVGL commit
`344c7c318047b7348e1be8572a9fd4260c251cfa`, tree
`2c76db856ec570f3ee12565181e5cf52bdd33d78`:

- `src/libs/freetype/lv_freetype_outline.c`, Git blob
  `f7d5edbd0ddd40e3ed6a62a66916b10c72974ac7`;
- `src/libs/freetype/lv_freetype.c`, Git blob
  `c6edfb80794608bdb5e8b58e007fbe8301927013`;
- `src/libs/freetype/lv_freetype.h`, Git blob
  `3bade7dbd681086a233d4fb244c43e5afcb4cbb7`;
- `src/libs/freetype/lv_freetype_private.h`, Git blob
  `f851704564afcb9e2030c7c563d2bd96563481c9`.

The 9.3-development implementation intentionally ignores `filter` and
`user_data` and stores only `event_cb` in `lv_freetype_context_t`. The local
provider preserves that valid-context behavior. It adds one bounded failure
rule: when the global FreeType context pointer is null, it returns without a
write instead of dereferencing null.

## Target and host evidence

The isolated Cortex-M55 provider exports exactly
`lv_freetype_outline_add_event`. Its sole import is `lv_global`, represented by
one MOVW/MOVT relocation pair. Linking it with the exact admitted 492-byte
global-storage provider produces an aggregate with no undefined symbols.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| source object | 1,028 | `48a7d72f38c54e98ff296df1c1630e9a0f4e8895dea41d7f74caf9934468203a` |
| isolated provider | 1,208 | `f4d90b85f22b784d3922cc16b7cb58c5f3df8c1c1b937e2a44332498eb07774e` |
| ABI probe | 1,040 | `cd6de046286a8765255f6a844a7f845289fd6e6ef33283f3b83439d277e0201e` |
| global/event aggregate | 1,340 | `1ab0eb432566d8c19d5bcf2e5621fda099d532adc123297014f480465e9ffa5a` |

The retained `lv_draw_ambiq_vector_font.o` has exactly one
`R_ARM_THM_JUMP24` consumer relocation to the function. The sanitizer-backed
host oracle covers null context, callback replacement, null callback, extreme
filter values, and ignored user data.

This moves the maximal residual from 19 to 18 symbols, digest
`f48ae4f7c5e49b2e02b0c7655123ff7691da07c619c0ac9192c74306b14efc0d`.
The scoped maximal partial link is 1,363,156 bytes with SHA-256
`43e495311ddd64ca6e2360796cec30bce7b233579b32fc58830081ad40ed413d`.
The later draw-buffer create/reshape admission moves the current residual to
16; that boundary is recorded in
`g2-lvgl-draw-buffer-shape-source-admission.md`.

## Remaining boundary

Production routing stays false. The source object does not establish
`lv_freetype_init`, context allocation/lifetime, callback concurrency,
initializer order, global-object collision/placement, or draw-thread safety.
No authorized hardware evidence was available.
