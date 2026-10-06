# Lookup and actual consumer call chain

```c
// Stock47ef18..47ef38, full function; literal47f944 -> table6becb0.
uint32_t lookup(void *destination, uint32_t domain) {
    if (destination == NULL || domain >= 34) return 6;
    stock_copy_439c04(destination, table6becb0 + domain*16, 16);
    return 0;
}

// Stock consumer55ca72: handle already validated/prepared earlier.
domain = (uint8_t)(handle->module4 + 3);
// Call47f7ae: allocates a local descriptor and invokes real lookup.
status = lookup(&local_descriptor, (uint8_t)domain);
// Comparison cut47f7be, before any enable-register access.
// Subsequent physical provider returns or mutates hardware based on descriptor.
// Its result is discarded by the original IOM caller.
(void)physical_provider_47f7ae(domain);
status = provider_4c4530(4, (uint8_t)(handle->module4 + 3));
```

The source IOM lookup helper implements only the byte-truncated domain selection and descriptor copy. It has a supplied output pointer instead of a live physical-provider stack local. Its ABI/return boundary is distinct and explicit. No full power consumer is substituted by this helper.

| Word offset | Observed role in47f7ae |
| --- | --- |
| 0 | Address read to test/clear enable mask |
| 4 | Enable mask used to test then clear bits |
| 8 | Address used by status polling |
| 12 | Mask and expected value for general status poll |

Fields remain uint32_t addresses/masks, avoiding host-sized pointers. Invalid direct input leaves all16 output bytes unchanged; valid input performs four ordered word stores. Test domain direct34/255/256/257 is invalid while IOM module253 wraps selected domain to0 and UINT32_MAX wraps selected domain to2. Alignment coverage is mapped, word-aligned destinations; arbitrary invalid/unmapped or unaligned destinations are outside the accepted contract.
