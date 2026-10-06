# Audio receive handoff: reconstructed pseudocode

This is readable instruction reconstruction, not recovered vendor C. The compiled implementation is in `g2/components/foundation/audio_cache_handoff/handoff.c`; the original instruction evidence and identities are adjacent.

```c
// Original 0x590b6c..0x590b92, full return observed.
u32 selected_buffer(handle, selector) {
    if ((u8)selector == 0)
        return load32(handle+0x40) == UINT32_MAX
            ? load32(handle+0x3c) : load32(handle+0x4c);
    return load32(handle+0x48) == UINT32_MAX
        ? load32(handle+0x44) : load32(handle+0x50);
}
// Original 0x57a7e0..0x57a80e, full return observed.
u32 audio_rx_buffer_get(u32 *buffer_out, u32 *length_out) {
    Range range = {0, 3200}; // authenticated flash 0x78d474
    handle = load32(0x2007450c);
    range.address = selected_buffer(handle, 0);
    cache_invalidate(&range, 0); // actual original 0x475014, not stub
    *buffer_out = range.address;
    *length_out = range.length;
    return range.address; // stock pop restores local first word into R0
}
```

The raw API assumes mapped valid handle/output words and provides no validation, lock, allocation, refcount, PCM copy or release. It publishes only after cache maintenance returns. Aliased raw output words end with 3,200, while returned R0 remains the selected pointer. The observed return register does not establish the vendor's C signature.

| Handle offset | Observed purpose | Evidence |
| --- | --- | --- |
| +0x04 | peripheral instance index | service/configuration use base + index<<12 |
| +0x3c / +0x40 | first channel's two configured pointers; UINT32_MAX in second selects single buffer | configure + query |
| +0x44 / +0x48 | second channel's two pointers, same sentinel | configure + query |
| +0x4c / +0x50 | mutable selected pointers | configure initializes; service toggles and programs DMA address |
| +0x54 / +0x58 | byte lengths converted from DMA record word counts<<2 | configure; service converts back with >>2 |

Static lifecycle: ISR 0x57a4d8 reads/clears enabled status, calls service 0x5908a0, then notifies through 0x53c6b2 when status bit4 is set. For bit4 service may toggle +0x4c and write that same pointer to peripheral +0x224 before enabling bit0 of +0x21c. This prevents labeling selected_buffer as exclusively inactive/CPU-owned without the real peripheral contract. The current getter tests do not execute this ISR/service schedule.

New policy, explicitly distinct from stock: cache_checked requires nonnull range, nonzero aligned base/capacity, nonwrapping extent and operation 0/1/2. It reads length then address and rejects zero/signed-negative/out-of-bounds ranges before cache activity. Valid bounds cover the assumed 32-byte address-block footprint, not physical geometry or allocation liveness. It snapshots the descriptor before calling the unchanged raw provider. Checked getter also rejects missing/aliased outputs and null handle; on failure it leaves outputs unchanged and returns 6; on success it returns 0 and publishes the borrowed address/3200. Bounds are supplied by the caller, not discovered allocations.
