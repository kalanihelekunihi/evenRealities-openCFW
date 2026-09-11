# G2 bootloader compatibility trap/no-op stub source closure

Part of work item `BL-003` (`0x004155E8..0x0041A648`, 11,158 retained
bootloader bytes). This closure covers two of its eleven official regions:

- `[0x00416026,0x00416028)` -- two-byte infinite self-loop trap
- `[0x00416028,0x0041602A)` -- two-byte no-op return

Both sit between the authenticated substring-search primitive
(`[0x00415FFA,0x00416026)`, already a generated entry redirect) and the
critical-context predicate (`[0x0041602A,0x00416058)`, already a generated
entry redirect). Neither stub has any operand, memory access, or observable
state: the trap is Thumb's canonical unconditional self-branch (`b .`,
encoding `0xE7FE`), and the no-op is the canonical bare return (`bx lr`,
encoding `0x4770`). Both encodings are architecturally fixed, single-purpose
Thumb-2 idioms, not vendor-specific sequences.

## Stock identity

```
$ python3 -c "
data = open('blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin','rb').read()
print(data[0x6026:0x6028].hex(), data[0x6028:0x602A].hex())
"
fee7 7047
```

- Trap body: 2 bytes, SHA-256
  `575fc8fa9e92ffe7d57a6aef6f1168f39da04f07d6bcd5b5e17883bff7b33165`.
- No-op body: 2 bytes, SHA-256
  `c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8`
  (the same hash as the unrelated `open_cfw_bootloader_address_identity_4213d8`
  in-place leaf, which is also a bare `bx lr`; this is expected for a
  content-addressed two-byte universal idiom, not evidence of a shared
  origin).

## Clean-room C

`components/bootloader/core_overlay/runtime_trap_stubs_416026.c` defines
`open_cfw_bootloader_runtime_trap_416026` and
`open_cfw_bootloader_runtime_noop_return_416028` as `naked` functions whose
entire body is one inline-asm instruction each (`b .` / `bx lr`). `naked` is
used, matching the existing
`components/bootloader/core_overlay/runtime_address_map_4213d8.c` precedent
in this same directory, because the exact one-instruction encoding is the
whole point of the admission -- there is no C statement that reliably forces
a specific two-byte Thumb-2 encoding without it.

Compiling with the component's canonical Apple clang 21 Cortex-M55 profile
(`-mcpu=cortex-m55 -mthumb -Oz -ffreestanding -fno-jump-tables
-fomit-frame-pointer -fno-builtin -mno-unaligned-access -fno-unwind-tables
-fno-asynchronous-unwind-tables -fropi -ffunction-sections -fdata-sections
-Wall -Wextra -Werror`) and extracting each function's own `-ffunction-sections`
text section with `apollo_overlay.extract_in_place_function_section`
reproduces the stock bytes exactly: `fee7` and `7047`, matching both SHA-256
values above bit-for-bit. Both functions have zero relocations and an
eight-byte discardable `.ARM.exidx` companion, consistent with every other
in-place leaf in this component.

## Production admission

Registered as two `in_place_leaves` entries in
`components/bootloader/core_overlay/overlay.json`
(`open_cfw_bootloader_runtime_trap_416026` at runtime address `0x00416026`,
`open_cfw_bootloader_runtime_noop_return_416028` at `0x00416028`), each with
`expected` pins equal to `stock` pins (byte-identical replacement in place).
`make -C g2 bootloader-component` recompiles and overwrites the four
retained bytes with these two functions' own compiled output; no branch
redirect or relocation is used since the compiled code already fits and
matches the original span exactly.

## Tests

`tests/test_runtime_bootloader_trap_stubs_416026.py` pins the authenticated
stock bytes/hashes and statically disassembles the Cortex-M55 object to
confirm each function is exactly one instruction (`b.` self-branch / `bx lr`)
with the stock encoding. The trap's whole behavior is an infinite loop and
the no-op's whole behavior is nothing, so neither is dynamically executed on
the host; static byte/structure verification is the complete behavioral
contract for a fixed, argument-free, state-free stub.

## Scope and limits

This closes 4 of the 11,158 `BL-003` bytes. The remaining 11,154 bytes
(the 36-byte address table, the 38-byte semihosting-shaped cave, six more
literal-pool spans, and the 10,896-byte unanalyzed compatibility tail) are
tracked in
`docs/research/g2-bootloader-bl003-remaining-recon-4155e8-41a648.md`.
No hardware operation occurred.
