# Bounded ARC helper recovery: `0x0030690C`

This packet covers 22 authenticated bytes at `[0x0030690C, 0x00306922)`, decoded as seven contiguous ARCv2 EM instructions. The symbol catalog proposes `IRQ_EnableAfterRestore` for that range. Its cited SDK comparison report is absent from this workspace, so the name is treated only as a catalog seed. The candidate starts with `mov_s` and returns by non-delayed `j_s [blink]`; no global alternate-entry census was performed.

```text
function candidate_0030690c(incoming_r0):
    # incoming_r0 is not read by the observed body.
    p = M32[0x0080FB70]
    value = M8[p + 186]
    value = value & 0x0F                 # BMSK_S ..., 3
    value = value | 0x10                 # BSET_S ..., 4
    SETI(value)                          # updates STATUS32
    jump [blink]                         # no delay slot
```

The body does not validate the pointer loaded from `0x0080FB70`; pointer validity and the identity of the byte at `p+0xBA` remain external dependencies. The `SETI` instruction modifies architectural `STATUS32`; the ARCv2 EM programmer’s reference manual identifies `SETI` among the instructions that can modify that register ([manual](https://docs.alexrp.com/arc/arc_em.pdf)). This packet does not infer the loaded byte’s API meaning or claim an observed interrupt-state transition.

## Caller value and delay slot

Packet 1474 calls this helper at `0x00302CC0` with `BL.D`. Immediately before the call, its `r0` contains the caller’s `XBfu(M32[0x00F0383C],88)` result. The delay instruction at `0x00302CC4` stores that value using `ST.AS` before control transfers. The base was advanced by the prior `ST.AB` from `0x00F00840` to `0x00F008D0`, so the word-scaled displacement 72 addresses `0x00F009F0`. Once the helper begins, its first `mov_s` replaces `r0`; none of the remaining helper instructions reads the incoming argument.

The status word and store address are exact instruction-derived expressions. Their hardware meaning is unresolved. The caller packet is pinned by receipt and instruction evidence; this packet does not modify it.

## Extent and adjacent bytes

The exact catalog seed is 22 bytes. The bytes begin at the helper’s `mov_s` and end with the `j_s [blink]` at `0x00306920`. The previous catalog candidate ends at this entry; the next catalog function begins at `0x00306924`. Bytes `[0x00306922,0x00306924)` are included in the boundary context but remain unassigned. The referenced SDK report was not available for inspection, and the helper’s independent ownership remains a private candidate pending review.

All fixtures are symbolic and constrained to the decoded body. There is no C implementation or canonical admission.
