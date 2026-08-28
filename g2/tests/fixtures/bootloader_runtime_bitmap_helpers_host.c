/* SPDX-License-Identifier: MIT */

typedef __UINT32_TYPE__ open_cfw_bitmap_fixture_u32;

static open_cfw_bitmap_fixture_u32 open_cfw_bitmap_fixture_table[256][2];

#define OPEN_CFW_BOOTLOADER_BITMAP_TABLE open_cfw_bitmap_fixture_table
#include "../../components/bootloader/core_overlay/runtime_popcount_421584.c"
#include "../../components/bootloader/core_overlay/runtime_bitmap_helpers_4215ae.c"

void open_cfw_bitmap_fixture_clear(void)
{
    open_cfw_bitmap_fixture_u32 row;
    for (row = 0U; row < 256U; ++row) {
        open_cfw_bitmap_fixture_table[row][0] = 0U;
        open_cfw_bitmap_fixture_table[row][1] = 0U;
    }
}

void open_cfw_bitmap_fixture_set(
    open_cfw_bitmap_fixture_u32 row,
    open_cfw_bitmap_fixture_u32 word,
    open_cfw_bitmap_fixture_u32 value)
{
    open_cfw_bitmap_fixture_table[row & 0xFFU][word & 1U] = value;
}
