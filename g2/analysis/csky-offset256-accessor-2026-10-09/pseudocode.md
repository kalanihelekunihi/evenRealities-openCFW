# Conditional XIP accessor 0x102058C4

Partial/unreviewed, not admitted. Exact symbol-sized extent
`[0x102058C4,0x102058D4)` is 16 bytes, SHA-256
`01a13ea05f3c81bf438f4613e4947a6ae9d47dbed8ebfaf4b88beb5c21ab6102`.
The returned executable body occupies 14 bytes; the trailing BKPT at
`0x102058D2` is accounted separately and is not reached on ordinary return.
Conditional XIP base `0x10203004` gives child `[0x28C0,0x28D0)` and exact
payload `[0xEE50,0xEE60)` under complete-child offset `0xC590`. Adjacent body
at `0x102058D4` and shared load helper `0x102055EC` are not newly counted.

```c
/* r0=base, r1=output pointer; reconstructed semantics, not production code. */
uint32_t read_word_at_offset256(uint32_t base, uint32_t *output)
{
    uint32_t value = load32((base + 256u) & UINT32_MAX);
    *output = value;
    return value; /* r0 remains the loaded word */
}
```

Ordered instructions preserve r4/link, save output pointer in r4, add 256 to
r0, call the actual two-instruction load helper, store through r4 and pop/return.
Load precedes store even when input/output aliases. There are no checks for
pointer validity, bounds or alignment. Exceptional access behavior and physical
memory role are not established.

The consumed complete-XIP decode has one direct BSR at `0x10205B34`:
`0x10205B2E` selects stack+4 as output, `0x10205B30` loads the base from
`[0x20027350+0x5C4]`. Thus the caller reads loaded-base+256 into stack+4.
`0x10205B44` reloads that slot after an intervening accessor call, whose alias
behavior must be understood before asserting output lifetime. No semantic
global-field name or NPU/device purpose is guessed.

Fresh static verification authenticates image/payload/tool, complete-child
mapping, exact bytes, seven-instruction tiling including BKPT, helper bytes and
direct caller census. Four Python fixtures demonstrate the address/value model
including wrap-to-zero; they are not original C-SKY instruction execution.
The caller-disassembly hash, actual decoder argv and exit code are recorded.

All 117 recognized task scopes are disjoint; the independently prepared
indexed accessor ends at this entry. The scope-regex scan is supporting
ownership evidence, not a global assignment/admission receipt. Source reference
for this packet is the authenticated original instruction sequence and the
existing helper decode; KWS/AIoT semantic analogy supplies no new source
attribution. Coordinator adoption, independent review, live mapping and
higher-level field/ownership interpretation remain open.
