/* SPDX-License-Identifier: MIT
 * Image-B 0x10007c90: identify the flash and select its descriptor record.
 * Record contents at 0x20016ea4 are a separate initialized-data contract.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_flash_read_10006c30(
    uint32_t command, uint8_t *destination, uint32_t length);

static uint32_t record_word(const volatile uint8_t *record, uint32_t offset)
{
    return *(const volatile uint32_t *)(const void *)(record + offset);
}

static void select_record(uint32_t index)
{
    volatile uint32_t *const descriptor =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20016d60);
    volatile const uint8_t *const record =
        (volatile const uint8_t *)(uintptr_t)(UINT32_C(0x20016ea4) +
                                              index * 24u);
    descriptor[0] = index;
    descriptor[1] = record_word(record, 8u);
    descriptor[2] = 3u;
    descriptor[3] = (uint32_t)(uintptr_t)record;
}

int32_t gx8002_image_b_flash_probe_10007c90(void)
{
    volatile int32_t *const selected =
        (volatile int32_t *)(uintptr_t)UINT32_C(0x20016d60);
    volatile const uint8_t *const records =
        (volatile const uint8_t *)(uintptr_t)UINT32_C(0x20016ea4);
    *selected = -1;
    uint8_t id[3];
    if ((int32_t)gx8002_image_b_flash_read_10006c30(0x9fu, id, 3u) < 0)
        return -1;
    uint32_t detected = ((uint32_t)id[0] << 16) |
                        ((uint32_t)id[1] << 8) | id[2];
    uint32_t first_id = record_word(records, 4u);
    if (first_id == 0u) return *selected < 0 ? -2 : 0;
    if (first_id == detected) {
        select_record(0u);
        return 0;
    }
    for (uint32_t i = 1u;; ++i) {
        uint32_t candidate = record_word(records + i * 24u, 4u);
        if (candidate == detected) {
            select_record(i);
            return 0;
        }
        if (candidate == 0u) break;
    }
    if (*selected >= 0) return 0;
    if (first_id == UINT32_C(0xc22016)) {
        select_record(0u);
        return -2;
    }
    for (uint32_t i = 1u;; ++i) {
        uint32_t candidate = record_word(records + i * 24u, 4u);
        if (candidate == 0u) return -2;
        if (candidate == UINT32_C(0xc22016)) {
            select_record(i);
            return -2;
        }
    }
}
