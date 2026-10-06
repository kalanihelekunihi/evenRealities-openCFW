# Readable cache command contract

The range interface is exactly two accessed words: uint32 address at0 and length at4. Stock compares length as signed32; the reconstruction expresses that test using sign-bit checks and unsigned wrap arithmetic.

```c
if ((read32(0xe000ed14) & (1u << 16)) == 0) {
    DSB(); ISB(); return 0;
}
if (range == NULL) {
    write32(0xe000ed84, 0); // select cache0
    DSB();
    geometry = read32(0xe000ed80);
    sets = (geometry >> 13) & 0x7fff;
    max_way = (geometry >> 3) & 0x3ff;
    do {
        way = max_way;
        do {
            write32(selected_whole_operation,
                    ((sets << 5) & 0x3fe0) | (way << 30));
        } while (way-- != 0);
    } while (sets-- != 0);
    DSB(); ISB(); return 0;
}
remaining = range->length; // load before address, including skipped lengths
address = range->address;
if (remaining == 0 || (remaining & 0x80000000)) return 0;
remaining += address & 31;
DSB();
do {
    write32(selected_range_operation, address);
    address += 32;
    remaining -= 32;
} while (remaining != 0 && !(remaining & 0x80000000));
DSB(); ISB(); return 0;
```

| Operation | Whole-cache command register | Range command register |
| --- | --- | --- |
| Invalidate, flag low byte0 | 0xe000ef60 | 0xe000ef5c |
| Clean+invalidate, flag low byte nonzero | 0xe000ef74 | 0xe000ef70 |
| Clean | 0xe000ef6c | 0xe000ef68 |

Example raw range sequence: address0x2000801f,length2 emits0x2000801f and0x2000803f, separated by32, because length+misalignment=33. The command register's physical line selection is not modeled. All lengths/addresses wrap as32-bit values; enormous positive lengths can yield enormous loops even when initial signed addition crosses a boundary. No range/null validation beyond these branches is inferred.

Static consumer chains:

```c
// Display write59ccdc; providers beyond clean not implemented by this batch.
local_range.address = request->buffer14;
local_range.length  = request->length0c;
clean_47510e(&local_range); // BL59cd10
build_transfer_59cafc(...);
transfer_status = blocking_mspi_4c2098(...);

// Audio DMA accessor57a7e0; query/producers not implemented by this batch.
local_range = flash_template_78d474; // {0,3200}
local_range.address = inactive_buffer_query_590b6c(handle,0);
invalidate_475014(&local_range,0); // BL57a800
*returned_buffer = local_range.address;
*returned_length = local_range.length;
```

The two new source APIs provide the maintenance calls for those interfaces. This is not source completion of either consumer or a runtime route/firmware patch.
