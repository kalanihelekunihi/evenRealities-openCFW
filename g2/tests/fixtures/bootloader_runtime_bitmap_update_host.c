/* SPDX-License-Identifier: MIT */

#include <stdint.h>

static uint32_t open_cfw_bitmap_update_fixture_table[256][2];

#define OPEN_CFW_BOOTLOADER_BITMAP_UPDATE_TABLE \
    open_cfw_bitmap_update_fixture_table
#include "../../components/bootloader/core_overlay/runtime_bitmap_update_421632.c"

void open_cfw_bitmap_update_fixture_clear(void)
{
    uint32_t row;
    for (row = 0U; row < 256U; ++row) {
        open_cfw_bitmap_update_fixture_table[row][0] = 0U;
        open_cfw_bitmap_update_fixture_table[row][1] = 0U;
    }
}

uint32_t open_cfw_bitmap_update_fixture_get(uint32_t row, uint32_t word)
{
    return open_cfw_bitmap_update_fixture_table[(uint8_t)row][word & 1U];
}

void open_cfw_bitmap_update_fixture_set(
    uint32_t row, uint32_t word, uint32_t value)
{
    open_cfw_bitmap_update_fixture_table[(uint8_t)row][word & 1U] = value;
}
