# Indexed word accessor: conditional C-SKY XIP 0x102058B4

Status: partial, unreviewed, not admitted to the campaign. This is reconstructed
pseudocode for understanding, not a production implementation.

The 16-byte body `[0x102058B4,0x102058C4)` has SHA-256
`6bdb07c6468e4e2d97ba7c22736df347e8f2736c8d5009f053d8958265bceb3c`.
The conditional XIP base is `0x10203004`. Child offsets are
`[0x28B0,0x28C0)`; exact codec payload offsets are `[0xEE40,0xEE50)`.
The verifier authenticates the child, tool and official codec payload, locates
the complete child at payload offset `0xC590`, and compares the body directly.

```c
/* Register contract: r0=base, r1=index, r2=output_slot.
 * All address arithmetic is 32-bit and wraps. No bounds/alignment check.
 * The memory read may have MMIO effects; no hardware identity is asserted. */
uint32_t indexed_word_read(uint32_t base, uint32_t index,
                           uint32_t *output_slot)
{
    uint32_t address = base + (index << 2);
    uint32_t word = read_word_102055ec(address);
    *output_slot = word;
    return word; /* r0 remains the helper result */
}

/* Actual two-instruction helper at 0x102055EC:
 * ld.w r0,(r0,0); jmp r15 */
uint32_t read_word_102055ec(uint32_t address)
{
    return load32(address);
}
```

Instruction chain: save r4/link; shift r1 left two; preserve output pointer in
r4; add shifted index to r0; call `0x102055EC`; store r0 through r4; restore
r4/link and return. The next body starts at `0x102058C4`; it is excluded.

The existing complete-XIP disassembly contains one direct BSR to this entry,
at `0x10205B2A`. Immediately preceding instructions load base from
`[0x20027350 + 0x5CC]`, set index to 2, and set the output slot to the current
stack pointer. Thus this call reads the word at the loaded base plus eight and
writes it to stack offset zero. Later code loads that stack word at
`0x10205B48`. Global field names, the base's dynamic value and ownership, and
the caller's higher-level NPU purpose remain unknown.

The 117 contract scope scan found no declared half-open extent overlap.
This is a conservative local ownership check, not a global assignment receipt:
contracts with incompletely declared or nonstandard scopes can still require
coordinator review. No campaign task or ownership state was changed.

Validation is static: authenticated original bytes, seven-instruction tiling,
exact two-instruction helper bytes, and the existing full-XIP direct-call
census. Four semantic fixtures cover index zero, observed index two, address
wrap, and shift wrap. They do not execute original C-SKY instructions and do
not prove runtime mapping, access permissions, hardware state or scheduling.

## Prior mapping discrepancy

The preceding `csky-recovery-5316/001/source-map.json` records child offsets
`0x28A0–0x28B0` and component start `0xC590`, but reports payload offsets
`0xF430–0xF440`. Those values are inconsistent: the stated arithmetic yields
`0xEE30–0xEE40`. This new packet verifies complete-child matching against the
official payload and uses the resulting mapping. The prior evidence was left
unchanged; independent coverage review should assess that provenance field
before admission. No implication about its decoded instruction semantics is
made from the mapping discrepancy alone.

Independent audit follow-up in
`coverage-audit-parallel-2026-10-09/CSKY-REVIEW.md` supports the new
`0xEE40–0xEE50` mapping and identifies the prior offset error as `0x600`.
The verifier now records the exact path and SHA-256 of the consumed complete
caller disassembly. Coordinator ownership and campaign identity/admission
records remain absent for this isolated packet; it remains unadmitted.
