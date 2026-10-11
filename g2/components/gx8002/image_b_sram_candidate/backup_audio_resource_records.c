/* SPDX-License-Identifier: MIT
 * Native image-B resource record copies at 0x1000a784 and 0x1000a7f0.
 */
#include <stdint.h>

extern void gx8002_image_b_copy_10011344(void *destination,
                                           const void *source, uint32_t count);

static uint32_t store_record(const uint32_t *record, uintptr_t table,
                             uintptr_t control, unsigned count_offset,
                             unsigned append_offset)
{
    const uint32_t key = record[0];
    for (unsigned index = 0; index < 8u; ++index) {
        uint32_t *entry = (uint32_t *)(table + index * 8u);
        if (entry[0] == key) {
            gx8002_image_b_copy_10011344(entry, record, 8u);
            return 0u;
        }
    }
    volatile uint32_t *const count =
        (volatile uint32_t *)(control + count_offset);
    uint32_t index = *count;
    if (index >= 8u || key == 0u) return UINT32_MAX;
    uint32_t *entry = (uint32_t *)(control + (index + append_offset) * 8u);
    gx8002_image_b_copy_10011344(entry, record, 8u);
    *count = *count + 1u;
    return 0u;
}

uint32_t gx8002_image_b_audio_record_one_1000a784(const uint32_t *record)
{
    return store_record(record, UINT32_C(0x2002cb98), UINT32_C(0x2002cb88),
                        8u, 2u);
}

uint32_t gx8002_image_b_audio_record_two_1000a7f0(const uint32_t *record)
{
    return store_record(record, UINT32_C(0x2002cbd8), UINT32_C(0x2002cb88),
                        12u, 10u);
}
