# Recovered layout and preparation flow

New source is a reconstruction of a fixed stock-operation prefix; all addresses below refer to the hash-pinned Apollo OTA after stripping its32-byte header, loaded at0x438000.

| Handle offset | Meaning used by this path |
| --- | --- |
| 0 | Validation prefix; bit25 indicates enabled |
| 4 | IOM module number; register base `0x40050000 + (module << 12)` |
| 0x24 | Pending word, checked only when enabled and status ready |
| 0x828 | Local command-queue pointer |
| 0x868 | Retention flag byte; nonzero request stores1 |

Ordered retention snapshots:

| Register offset | Saved handle offset |
| --- | --- |
| 0x104 | 0x86c |
| 0x118 | 0x874 |
| 0x11c | 0x878 |
| 0x228 | 0x87c |
| 0x22c | 0x880 |
| 0x234 | 0x884 |
| 0x23c | 0x888 |
| 0x240 | 0x88c |
| 0x244 | 0x890 |
| 0x280 | 0x894 |
| 0x2c0 | 0x898 |
| 0x200 | 0x89c |
| 0x210 | 0x870 |

```c
// 55c7e8, stock operation=2; readable fixed-operation reconstruction
if (!handle || (handle->prefix & 0x01ffffff) != 0x01123456) return 2;
if (handle->prefix & (1u << 25)) {
    if ((read(register_base(handle) + 0x248) & 6) != 4) return 3;
    if (handle->pending24 != 0) return 3;
}
if ((uint8_t)retention != 0) {
    save_each_register_in_the_order_above();
    if (read(register_base(handle) + 0x228) & 1)
        (void)local_cq_pause(handle); // 55c168 -> CMDQ disable538e8c
    handle->retained868 = 1;
}
write(reg11c, read(reg11c) & ~1u);
write(reg11c, read(reg11c) & ~16u);
// Stop original at55ca72, with its stack frame still live.
// The new C API returns0 here as "prepared".
```

Stock continuation, not part of preparation:

```c
(void)physical_power_provider_47f7ae((uint8_t)(handle->module + 3));
status = provider_4c4530(4, (uint8_t)(handle->module + 3));
return status; // its actual branch/epilogue determines final return
```

Call-chain boundaries are separately observable: disable55c430 -> local CQ term55c11a -> CMDQ term53909a; prepare's local pause55c168 -> CMDQ disable538e8c. Real PRIMASK consumer473940 executes. Raw RAM/MMIO ordering is observed with serialized synthetic registers. No scheduling, hardware side effects, interrupt interleaving or buffer ownership beyond that state is supplied.
