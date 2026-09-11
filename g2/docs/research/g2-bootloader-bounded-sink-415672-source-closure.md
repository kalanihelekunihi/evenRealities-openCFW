# G2 bootloader bounded output sink source closure

Part of work item `BL-003` (`0x004155E8..0x0041A648`, 11,158 retained
bootloader bytes). This closure covers the 26-byte official region
`[0x00415672,0x0041568C)`, retained between the authenticated Arm EABI
byte-fill (`memset`, generated entry redirect ending at `0x00415672`) and
forward-copy (`memcpy`, generated entry redirect starting at `0x0041568C`)
primitives.

## Stock identity and recovered semantics

Stock body (26 bytes), SHA-256
`e4d1a37e747c2fbecff8857afc606938f61b5d3b20f17a9b4ac78eac26550bfc`:

```
8268 521c 8260 4268 32b1 0268 531c 0360 1170 4168 491e 4160 7047
```

Disassembly (Thumb-2, entry `r0` = context pointer, `r1` = byte value):

```
ldr  r2, [r0, #8]   ; r2 = ctx->total
adds r2, r2, #1
str  r2, [r0, #8]   ; ctx->total++            (unconditional)
ldr  r2, [r0, #4]   ; r2 = ctx->remaining
cbz  r2, end        ; if (ctx->remaining == 0) return
ldr  r2, [r0]       ; r2 = ctx->cursor
adds r3, r2, #1
str  r3, [r0]       ; ctx->cursor = r2 + 1
strb r1, [r2]       ; *r2 = value
ldr  r1, [r0, #4]
subs r1, r1, #1
str  r1, [r0, #4]   ; ctx->remaining--
end:
bx lr
```

This is the classic "counted bounded sink" shape used by counting
`sprintf`/format-primitive implementations: a three-word context
`{cursor, remaining, total}` at offsets `{0, 4, 8}`. `total` is incremented
on every call regardless of space, so a caller can learn how many characters
it asked to emit even when the destination is smaller (matching the
neighboring, already-source-routed numeric formatting primitives at
`0x00415844..0x00415BF6`, which are exactly this kind of bounded formatter).
No vendor string, symbol name, or license marker survives in this leaf --
the field layout and control flow are the entire recovered contract, and
both are generic, unremarkable C idiom, so it is treated as a clean-room MIT
reconstruction rather than an attributed upstream port.

## Clean-room C

`components/bootloader/core_overlay/runtime_bounded_sink_415672.c` defines
`open_cfw_bootloader_bounded_sink_putc_415672(sink, value)` operating on
`struct open_cfw_bootloader_bounded_sink { unsigned char *cursor; u32
remaining; u32 total; }`, matching the field order and control flow above.

Compiling with the component's canonical Apple clang 21 Cortex-M55 profile
and extracting the function's own text section reproduces a 26-byte body
(SHA-256 `9c47769bed6b73115b82c3b42d5ee9f49bd9ef730649da0a54c3c0bcdc7c856f`),
the same size as the stock span but not byte-identical: the compiler
schedules the `total`/`remaining` loads together instead of interleaving
them with the increment, and uses a different register (`r3` instead of
`r2`) for the post-increment cursor value. Byte identity is not required for
an `in_place_leaves` admission (only the `expected`/`stock` sizes must
match, per `apollo_overlay.compile_in_place_leaf`); functional equivalence
is established by the differential host test instead.

## Production admission

Registered as an `in_place_leaves` entry in
`components/bootloader/core_overlay/overlay.json`
(`open_cfw_bootloader_bounded_sink_putc_415672`, runtime address
`0x00415672`, `expected` 26 bytes / `9c47769b...`, `stock` 26 bytes /
`e4d1a37e...`). `make -C g2 bootloader-component` recompiles and overwrites
the 26 retained bytes with this function's own compiled output in place; no
branch redirect or relocation is used.

## Tests

`tests/test_runtime_bootloader_bounded_sink_415672.py` pins the authenticated
stock body hash and exercises the host-compiled source through its actual C
semantics: normal bounded writes (cursor/total/remaining tracked exactly),
overflow (every offered character still counted, writing stops exactly at
capacity), and the `remaining == 0` short-circuit (verified to never
dereference a null cursor). A separate subtest cross-compiles the source for
Cortex-M55 with both reviewed toolchains present on this host.

## Scope and limits

This closes 26 of the 11,158 `BL-003` bytes. The remaining 11,132 bytes are
tracked in
`docs/research/g2-bootloader-bl003-remaining-recon-4155e8-41a648.md`. No
hardware operation occurred; this is a pure data-flow/control-flow leaf with
no MMIO, timing, or peripheral behavior to qualify.
