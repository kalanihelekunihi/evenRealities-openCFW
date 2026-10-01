# Instruction-grounded pseudocode: candidate C-SKY controller-to-buffer transfer `0x10000BBC`

## Scope and calling contract

Under the conditional BINH-A coordinate proposal, runtime `[0x10000BBC,0x10000C1C)` maps to child offsets `[0xBD4,0xC34)`. The 96-byte span is contiguous instructions, with no pool or gap. The image, tool, instruction semantics, caller sites, and predecessor receipt are pinned here. This is not evidence of physical loading.

Observed callers pass `(mode, output_buffer, count)`: `(3,SP+4,3)`, `(53,SP+4,1)`, `(5,SP+4,1)`, and `(53,SP+3,1)`. Nested C1C passes `(5,its-SP+3,1)`. In the byte loop, the callee reads a 32-bit word from controller +0x60, stores its low byte to the caller buffer, and increments the buffer pointer.

## Pseudocode

```text
controller_to_buffer_10000bbc(mode:u32, output:u8*, count:u32) -> u32:
    push R4-R6, LR
    R4 = output
    R5 = count
    R6 = mode
    call_10000B4C()                       // no explicit args; return ignored

    controller = 0xA2000000
    u32[controller+0x08] = 0
    u32[controller+0x4C] = 0
    u32[controller+0x00] = 3079
    u32[controller+0x04] = u32(count - 1)  // zero count stores 0xFFFFFFFF
    u32[controller+0x10] = 1
    end = u32(output + count)
    u32[controller+0x18] = 0
    u32[0xA20000F4] = 0
    u32[controller+0x08] = 1
    u32[controller+0x60] = mode

    while R1 != end:
        while (u32[controller+0x28] & 2) == 0:
            continue                            // no timeout
        data_word = u32[controller+0x60]
        u8[R1] = low8(data_word)
        R1 = u32(R1 + 1)                        // STBI.B

    status = u32[controller+0x20]
    while status != 0:
        status = u32[controller+0x20]
    call_10000B4C()                             // return ignored
    R0 = status                                 // zero on return
    pop R4-R6, PC
```

`end` is a 32-bit sum; count zero skips the byte loop but still configures registers and polls completion. Nonzero counts that cross `0xFFFFFFFF` use modular pointer progression. The routine has no null/count checks. It waits for bit 1 of controller+0x28 before each 32-bit data read, then stores the low byte at the caller pointer. It subsequently polls the 32-bit word at controller+0x20 until zero and returns that zero. Both B4C return values are ignored; neither wait has a timeout.

## Nested caller finding and limits

C1C calls BBC at C28 with its local `SP+3` as destination, then reloads that byte and tests bit 0. BBC writes the byte before returning, so the subsequent test uses received data. C1C repeats while the received byte has bit 0 set. This narrows the previously noted stack-value uncertainty in 1428; no change is made to its frozen packet.

The meaning of B4C, physical controller identity/timing, and hardware effects remain unresolved. Inherited 1309/1352 R18/table/BKPT findings and the 1408 codec.tsv conflict remain open. No canonical mapping or firmware source is changed.
