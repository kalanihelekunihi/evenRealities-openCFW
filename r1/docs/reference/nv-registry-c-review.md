# Persistent-class registry in C

The NV dirty scan now uses a C table of pointers to the seven existing live
handle owners, replacing its unresolved `r1_nv_handles_begin` and
`r1_nv_handles_end` linker-span imports. No class or handle is duplicated.
The stock order is `dev_info`, `ble_mult`, `health`, `hsync`, `power`,
`nv_r1`, `r_size`. REA confirms the stock span literals at `0x73578`:
`0x20007de8` through `0x20007e04`. All seven linked cold class records match
the expanded stock initialization bytes.

Each scan reads the live handles. A clean registry returns immediately;
any dirty class triggers the original complete seven-class write pass with
indices zero through six, followed by the port request `(1, 0)`. Handles
are reloaded during that pass, so callback replacements take effect. This
removes a dependency on final linker placement of separate handle sections.
It preserves the existing requirement that all seven handles are valid.

The ignored Unicorn probe executes stock instructions and the compiled C
scan for every dirty-bit mask, all eight logging modes, and workflows with
and without handle replacement by the persistence callback: 2,048 pairs,
4,096 executions. It checks call order, indices, log arguments, flush,
return, SP and callee-saved registers. Four compiled negative controls
(wrong order, omitted last class, dirty-only writes, wrong flush command)
fail behavioral assertions. Other function bodies in the source unit remain
byte-for-byte unchanged, including the private-frame adapters.

All 801 R1 units compile without failures or duplicate strong symbols;
application imports decrease from 95 to 93. The other 798 object hashes
are unchanged; two generated boot objects have unchanged allocated bytes
and relocation identities. The strict bootloader GNU link passes with no
unresolved references. R1 source checks pass. The global source check still
fails on the unrelated unlisted G2 `resident_rom_thumb_set.S`.

Persistence and logging services are modeled. Physical flash behavior,
asynchronous effects, full application final linking and boot remain
unverified. No source-plan selection changes. Exact bindings and evidence
hashes are in [the machine-readable review](nv-registry-c-review.json).
