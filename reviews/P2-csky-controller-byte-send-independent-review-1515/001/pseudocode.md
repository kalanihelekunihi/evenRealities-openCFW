# Instruction-grounded pseudocode: controller byte sender (`0x10000B5C`)

## Scope and call contract

Conditional BINH-A mapping: runtime `[0x10000B5C,0x10000BBC)` maps to child `[0xB74,0xBD4)`, a 96-byte contiguous instruction span with no literal pool or gaps. The successor candidate BBC begins directly after the final branch. The candidate bytes, tool, full callsite sweep, local contexts, and B4C dependency are pinned. This does not validate physical loading or canonical admission.

The direct callers are C40 sites CEC, D38, and D42. They pass `(R0=6,R1=R8,R2=R8)`, `(6,R8,R8)`, and `(1,SP+4,2)`. Each ignores the return. The CEC and D38 paths reach these calls only after `R8 = received_byte & 2` and a branch away if R8 is nonzero; therefore both calls actually pass R1=R2=0. Their zero count skips memory loads.

## Pseudocode

```text
controller_byte_send(mode:u32, input:u8*, count:u32) -> u32:
    push R4-R6, LR
    R5 = count
    R4 = input
    R6 = mode
    call wait_until_word_bit0_clear()       // B4C: fresh u32[0xA2000028]&1 until zero

    controller = 0xA2000000
    u32[controller+0x08] = 0
    u32[controller+0x4C] = 0
    u32[controller+0x00] = 0x407
    u32[controller+0x04] = count
    u32[controller+0x10] = 1
    u32[controller+0x18] = u32(count << 16)
    clear_register_base = rotl32(0x000080A2, 24)  // 0xA2000080
    end = u32(input + count)                    // computed before the following MMIO writes
    u32[clear_register_base+0x74] = 0
    u32[controller+0x08] = 1
    u32[controller+0x60] = mode

    R1 = input
    while R1 != end:
        while (u32[controller+0x28] & 2) == 0:
            continue                            // no timeout
        value = zero_extend(u8[R1])
        R1 = u32(R1 + 1)                        // LDBI.B post-increments
        u32[controller+0x60] = value

    status = u32[controller+0x20]
    while status != 0:
        status = u32[controller+0x20]
    call wait_until_word_bit0_clear()           // B4C again
    R0 = status                                 // zero after poll
    pop R4-R6, PC
```

Initialization order above follows instruction order. The routine writes raw `count` at +4 and the 32-bit shifted count at +0x18. The loop bound is a 32-bit modular end pointer. For count zero it still performs both helper calls and all setup writes, but skips byte-ready polling, input loads, and byte writes. Each nonzero loop iteration first polls a new 32-bit word at +0x28 until bit 1 is set, then loads one unsigned byte and writes its zero-extended value as a 32-bit word to +0x60. After all bytes it polls the full word at +0x20 until zero, waits for bit 0 at +0x28 to clear through B4C, then returns the zero completion word. No timeout, null check, or length validation is present.

## Effects and limits

R4-R6 and LR are saved/restored. R0 is the final zero status. R1 advances by count modulo 2^32; R2/R3 are scratch. The end pointer is computed at B8A before the A20000F4 clear, controller enable, and mode write. The external wait helper is pinned in 1482 and polls a distinct predicate (bit 0 clear) from the per-byte ready predicate (bit 1 set). The path proof at CEC and D38 shows both R8-derived values are zero there. Register addresses and hardware behavior are observed from code only; physical identity and protocol meaning remain unresolved.
