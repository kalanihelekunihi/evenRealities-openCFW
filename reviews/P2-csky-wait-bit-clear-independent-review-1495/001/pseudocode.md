# Instruction-grounded pseudocode: C-SKY wait until bit 0 clears (`0x10000B4C`)

## Scope

Under the conditional BINH-A child mapping, runtime `[0x10000B4C,0x10000B5C)` maps to file offsets `[0xB64,0xB74)`. This is a 16-byte span of six contiguous instructions with no data bytes. The following routine begins at B5C and calls this entry; five more direct calls were found by a full-image objdump sweep. The exact source image, mapper premise, tool, disassembly, and six call sites are pinned in this packet. Mapping remains conditional; no physical loading or canonical admission is asserted.

## Contract and pseudocode

The routine accepts no meaningful arguments. It repeatedly performs a fresh 32-bit load from `0xA2000028`, masks bit 0, and repeats while that bit is set. It returns with `R0=0` when a load has bit 0 clear. It performs no stores, stack operations, calls, or timeout checks. `R3` is clobbered to `0xA2000000`; the loaded word is replaced in `R0` by its low bit.

```text
wait_until_word_bit0_clear() -> u32:
    R3 = u32(0xA2 << 24)                    // 0xA2000000
    do:
        R0 = u32[ R3 + 0x28 ]               // fresh 32-bit load each pass
        R0 = R0 & 1                         // zero or one
    while R0 != 0                           // BNEZ back to the load
    return R0                               // 0
```

The branch uses the masked value, not the original full word or arithmetic flags. Thus values such as `0x12345678` return immediately, while any odd value causes another load. If every observed read has bit 0 set, control remains in the loop indefinitely. This body establishes only the access address, width, mask, and branch behavior; the physical identity and protocol meaning of the address remain unresolved.

## Direct call sites

A full-image disassembly found exactly six direct `BSR` sites: B64 and BA2 in the B5C routine; BC4 and C02 in BBC; DC4 and E18 in another enclosing transfer path. At B64, B5C forwards its incoming R0/R1/R2 state, which B4C ignores. At BA2, B5C has completed its status-zero polling before calling again. At BC4, BBC already saved its own incoming arguments in R4-R6; at C02, it has completed the final status-zero poll. DC4 follows a nonzero-count branch and precedes controller setup; E18 follows the caller's controller+0x24 zero poll. These callers do not establish arguments consumed by this leaf. Caller bodies and caller-level meanings remain outside this packet. Exact contexts for all sites are pinned.

## Limits

Static fixtures cover clear, odd, even, and changing read sequences. They are controlled traces over the original instructions, not MMIO execution. The routine has no timeout. No source, canonical mapping, or firmware data was changed.
