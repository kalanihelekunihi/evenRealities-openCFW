# Instruction-grounded pseudocode: zero-mode wrapper at `0x10000AF8`

## Geometry and neighboring bytes

Under the conditional BINH-A source mapping, `[0x10000AF8,0x10000B02)` maps to `[0xB10,0xB1A)`, exactly 10 bytes: `PUSH R15`, `MOVI R2,0`, `BSR 0x100009CC`, `POP R15`. There are no literals inside this body. The preceding word `[0x10000AF4,0x10000AF8)` is separately pinned as little-endian `0x20001280`, referenced by `LRW R3` at AE6; it is not part of AF8. The next halfword at B02 is `BKPT`, explicitly excluded with ownership unresolved; B04 begins another push/return wrapper. No padding label is inferred.

## Exact wrapper contract

```text
wrapper_10000af8(r0:u32, r1:u32, incoming_r2:u32) -> child_result:
    push R15
    R2 = 0
    call 0x100009CC(R0, R1, R2=0)
    pop R15
    return with child-produced registers unchanged
```

AF8 itself reads no memory, writes no memory, and performs no arithmetic on R0 or R1. It forces the third child argument to zero, saves/restores only R15, and leaves post-call registers untouched. Consequently the return value and any changes to R0/R1/R2 come from 9CC; this packet does not claim the helper's behavior.

## Direct callers

The full image has four direct BSR sites. C40 calls AF8 at D5E with R0=24 and R1=4; the caller uses returned R0 by shifting it left four and ORing a constant. E84 calls at EA4 with R0 from its preceding 6A4 call and R1=R5 (entry R0 shifted left four); the result is saved in R6 and later programmed. At EB8 it passes the prior B04 return multiplied by 100 in R0 and R5 in R1; AF8's return is shifted left four and fed to the next AF8 call. At EC0 it passes that shifted result and R1=100; the returned low byte is later stored. Every AF8 call forces child R2=0, regardless of the caller's incoming R2. The static fixtures pin these forwarding/return properties using a controlled, opaque child result.

The meaning of 9CC, its output range, and the downstream peripheral remain unresolved. The mapping is conditional only; this packet changes no firmware source or canonical record.
