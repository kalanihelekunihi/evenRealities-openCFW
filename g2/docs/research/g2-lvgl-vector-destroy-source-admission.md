# G2 LVGL vector-task destruction source admission

## Result

The isolated Apollo/LVGL atomic link now has an exact-ABI provider for
`lv_vector_for_each_destroy_tasks`. The list unlink order, callback order,
vector-path array release, stroke-dash array release, task release, and final
list release follow authenticated LVGL commit
`344c7c318047b7348e1be8572a9fd4260c251cfa`, tree
`2c76db856ec570f3ee12565181e5cf52bdd33d78`.

The pinned source blobs are `src/draw/lv_draw_vector.c` at
`a33a6da02d06af20da5a523b0f15310767363bd3`, its private header at
`7b2d4e04a8b7cba5392ea73972fb002851e08f96`, `src/misc/lv_ll.c` at
`9d86f1daac5182d860debdcb1890b2277c449f1e`, and `src/misc/lv_array.c` at
`4f7b97a348c2bd8c210546db5e45b2c309d7ec05`. Their exact public headers
are pinned by the analyzer as well.

## Deterministic closure

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| target source object | 1,196 | `f0540a5bde0aa91596c7cada7e83d393375e025b0ac3502e30dd7b2c59699bd1` |
| isolated provider | 1,388 | `ed7735e3535a5f1e13760986a598be99b8703335a5acae36279acf4a0a56e72c` |
| ABI probe | 1,040 | `3245185d32527a143391078e0b9a583a92d8a8378332bf1e01fa0fe538bf7c1f` |
| allocator/array aggregate | 3,744 | `acb2421d3af2d4b6a3ba4f45169c50a2553d17d2cbc81459f6f7909998bed27a` |

The isolated provider imports only the already-reviewed `lv_array_deinit` and
`lv_free`; the aggregate has no undefined ELF symbols. It closes the single
exact call relocation from `lv_draw_ambiq_vector.o`. The ASan/UBSan host oracle
covers null and empty lists plus a three-node list mixing null/non-null paths,
owned/borrowed arrays, a callback, and exact single-release accounting.

This moves the maximal residual from 15 to 14 symbols, digest
`77f7f1022e2ea9cd79a7c638f9b0daef66903d2689d6d1b3a36d5e5b4e3680cd`.
The scoped external partial link is 1,369,220 bytes with SHA-256
`e0081a9f4309acaf7fba1191a424a6677c2c101c67cee469f4bafd41b069916b`.

## Evidence boundary

The LVGL linked-list ABI carries node size and links but no allocation extent,
node count, or provenance tag. Valid list topology and callback behavior are
therefore caller preconditions, as upstream requires. Production routing stays
false pending allocator collision and ownership, list creation/lifetime,
callback mutation rules, concurrency, placement, and full vector output
qualification. This provider owns no scheduler, cache, global, MMIO, or
hardware behavior, and no authorized hardware evidence was available.
