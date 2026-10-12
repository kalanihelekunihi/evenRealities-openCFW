# Four Boot catalogue entries with linked caller leads

`boot-native-frontier-current.json` has 254 entries without a mechanical
crosswalk; only four have a linked, identified caller lead. The four are not
four established missing C bodies:

| Native entry | Pseudocode role | Source status / next evidence |
|---|---|---|
| `0x00414948` | 8-byte one-child wrapper calling `0x004144dc` | Native `push {r7,lr}; bl 0x4144dc; pop {r1,pc}` returns the saved ambient `r7` through `r1`, while child produces `r0`. Caller `0x41513c` also uses `push {r7,lr}` / `pop {r1,pc}`. This is a two-register ABI contract; a plain `void` C wrapper would lose `r1`. Child identity and registration still need binding. |
| `0x0041715c` | TLSF add-pool body, control/list operations and bounds logging | Pinned TLSF v3.1 `tlsf_add_pool` is selected via allocator source. Structural source attribution is strong; native/runtime byte equivalence remains separate. |
| `0x00417208` | TLSF create control alignment check and initialization | Pinned TLSF v3.1 `tlsf_create` is selected. Need explicit address binding in crosswalk, not another implementation. |
| `0x0041b854` | Calls `0x0041f918(1,arg1,arg2)` and returns ambient `r7` | Native is `push {r7,lr}; mov r2,r1; mov r1,r0; movs r0,#1; bl 0x41f918; pop {r0,pc}`. The child return is discarded and the saved `r7` becomes `r0`. This is a nonstandard ambient-register wrapper; no guessed C success return is valid. |

The pinned TLSF provenance (`g2/components/bootloader/allocator/upstream/PROVENANCE.md`)
documents the exact 24×32 control layout, 0xC74 size, and native 0x70800 arena.
This review narrows the next actionable native ABI question to two wrappers;
it does not reduce the full 254-label attribution queue or prove full image
code/data extent.
