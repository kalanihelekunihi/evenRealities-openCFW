# Instruction-grounded pseudocode: controller-to-buffer receive (`0x10000BBC`), corrected attempt 003

## Scope and correction

The authenticated span remains runtime `[0x10000BBC,0x10000C1C)` / child `[0xBD4,0xC34)`, 96 contiguous instruction bytes. Attempt 002’s receipt is pinned as superseded history. Re-disassembly of its exact original body shows `0x10000C0A: LD.W R2,[R3+0x28]`, `0x10000C0C: ANDI R2,R2,8`, and `0x10000C10: BEZ R2,0x10000C0A`. Therefore the byte-ready condition is bit 3 set (mask 8); the older bit-1 prose/fixtures were incorrect. The verifier checks these exact instructions and branch destination.

## Pseudocode

```text
controller_to_buffer_10000bbc(mode:u32, output:u8*, count:u32) -> u32:
    push R4-R6, LR
    R4 = output
    R5 = count
    R6 = mode
    call_10000B4C()

    controller = 0xA2000000
    u32[controller+0x08] = 0
    u32[controller+0x4C] = 0
    u32[controller+0x00] = 3079
    u32[controller+0x04] = u32(count - 1)
    u32[controller+0x10] = 1
    end = u32(output + count)
    u32[controller+0x18] = 0
    u32[0xA20000F4] = 0
    u32[controller+0x08] = 1
    u32[controller+0x60] = mode

    while R1 != end:
        while (u32[controller+0x28] & 8) == 0:
            continue                            // exact ready test: bit 3, no timeout
        data_word = u32[controller+0x60]
        u8[R1] = low8(data_word)
        R1 = u32(R1 + 1)                        // STBI.B

    status = u32[controller+0x20]
    while status != 0:
        status = u32[controller+0x20]
    call_10000B4C()
    R0 = status
    pop R4-R6, PC
```

`end` is the 32-bit sum of output pointer and count. Count zero still runs initial wait and all setup writes, stores `0xFFFFFFFF` at +4 through count-minus-one wrap, skips byte-ready/data reads, polls +0x20 until zero, waits in B4C, then returns zero. For each byte, a new fullword at +0x28 is read until `(word & 8) != 0`; bit1-only and bit2-only values do not proceed. It then reads a fullword at +0x60, stores its low byte to output, and increments R1. Completion polls fullword +0x20 until zero. The separate B4C helper waits for bit0 of +0x28 to clear. This leaf has no timeout or argument validation.

## Caller and limits

The five pinned callers are C40 sites C8E, CC6, D06, D12 and C1C site C28, with exact tuples and uses in `edges.json`. B4C calls at BC4/C02 are separately pinned through dependencies. The 1465/002 wrong mask is preserved unchanged and explicitly superseded; no canonical mapping or firmware source changes were made. The physical peripheral identity and timing remain unvalidated.
