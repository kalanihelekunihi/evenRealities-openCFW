# G2 LVGL draw-buffer create/reshape source admission

This note records a software-only admission for `lv_draw_buf_create` and
`lv_draw_buf_reshape`. It does not register a production route, qualify the
Nema memory pools, or claim display behavior.

## Authenticated boundary

Valid-input semantics and ABI come from LVGL commit
`344c7c318047b7348e1be8572a9fd4260c251cfa`, tree
`2c76db856ec570f3ee12565181e5cf52bdd33d78`, specifically `lv_draw_buf.c`
Git blob `58562a86e55ca5897c3b79b3a486d3f7107aeea0` and its public/private
headers. The recovered Ambiq patch fixes the three handler tables at global
offsets `0xC8`, `0xE8`, and `0x108`.

Callback population is not invented. Authenticated retained
`lv_draw_ambiq_init` calls `lv_draw_ambiq_init_buf_handlers` before its first
`lv_draw_buf_create`, and that initializer writes all eight callbacks in every
table. The source provider keeps allocation, free, alignment, and stride as
indirect callback boundaries owned by that retained initializer.

The provider adds bounded malformed-input rules before an indirect call or
descriptor mutation: missing callbacks, zero or nonrepresentable 16-bit
geometry/stride, 32-bit byte-size overflow, allocation failure, null alignment,
and over-capacity reshape fail closed. Valid descriptors preserve the LVGL
header flags, magic, data/unaligned pointers, size, handler identity, unknown-
format reshape behavior, and default stride dispatch.

## Evidence

The Cortex-M55 provider exports exactly the two APIs. Its only ELF imports are
`lv_global`, `lv_malloc_zeroed`, and `lv_free`; the admitted global-storage and
heap/array providers close the aggregate with no undefined symbols.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| source object | 1,996 | `368557fddaad7fd1fc4c0da1803a659934725fa3fa0a51ff361ec4d6b154ab69` |
| isolated provider | 2,296 | `2cf520c1f7d814e9594f93520b638d15e107128c1882fadabff3342eb5448933` |
| ABI probe | 1,412 | `eb117a909d01a5efbb549229431835ef54748ff9b8581e6b521beb11518388dc` |
| heap/global/shape aggregate | 4,780 | `286aa21ed029d21e21428beccfa082c8044e2019d7d7403c5f3529b512f6e9c5` |

The retained Ambiq objects contain three exact call relocations to create and
one to reshape. The sanitizer host oracle covers callback absence, geometry
and stride limits, descriptor/buffer/alignment failures, successful automatic
stride creation, unknown-format reshape, capacity rejection, and allocation
balance.

This moves the maximal residual from 18 to 16 symbols, digest
`57df9890ebd18e5606c3f2ae0b33d0152e275cb63e8959d6f238b68b163d2d26`.
The scoped maximal partial link is 1,364,652 bytes with SHA-256
`152eedc0065609b2a18dd938bea1cf28c26ae9466718bcb48eaef3a37f39f661`.

## Remaining boundary

Production routing stays false. Live handler initialization order, Nema pool
ownership, heap/global provider collision, RAM placement, allocation under
scheduler load, callback concurrency, cache maintenance, and hardware output
remain unqualified. No authorized hardware evidence was available.
