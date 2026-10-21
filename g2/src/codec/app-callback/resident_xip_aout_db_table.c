/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x10204f90/0x10204ff0 output dB conversion.
 * Exact 37 semantic (register code, signed dB) pairs occupy 0x1020a910
 * through 0x1020a9a3 in stock XIP. The next four bytes are the first
 * channel-selector entry and form the native no-match fallback pair.
 */
#include <stdint.h>

struct db_pair { uint16_t code; int16_t db; };
static const struct db_pair db_pairs[37] = {
    {16u, -18}, {18u, -17}, {20u, -16}, {23u, -15},
    {25u, -14}, {28u, -13}, {32u, -12}, {36u, -11},
    {40u, -10}, {45u, -9}, {51u, -8}, {57u, -7},
    {64u, -6}, {72u, -5}, {81u, -4}, {91u, -3},
    {102u, -2}, {114u, -1}, {128u, 0}, {144u, 1},
    {162u, 2}, {181u, 3}, {203u, 4}, {228u, 5},
    {256u, 6}, {288u, 7}, {323u, 8}, {362u, 9},
    {407u, 10}, {460u, 11}, {512u, 12}, {576u, 13},
    {646u, 14}, {725u, 15}, {814u, 16}, {913u, 17},
    {1023u, 18}
};

static volatile uint32_t *const db_register =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0b00014);

uint32_t gx8002_xip_aout_set_db_10204f90(
    volatile uint8_t *context, int32_t requested)
{
    int32_t clamped = requested;
    if (clamped > 18) clamped = 18;
    if (clamped < -18) clamped = -18;
    uint32_t index = 0u;
    while (index < 37u && db_pairs[index].db != clamped) ++index;
    /* Every integer in the clamped range has an exact stock table row. */
    uint32_t code = db_pairs[index].code & 0x3ffu;
    *db_register = (*db_register & UINT32_C(0xfc00ffff)) | (code << 16u);
    *(volatile uint16_t *)(void *)(context + 0x12u) = (uint16_t)requested;
    return 0u;
}

uint32_t gx8002_xip_aout_get_db_10204ff0(
    const volatile uint8_t *context, uint16_t *result)
{
    uint32_t code = (*db_register >> 16u) & 0x3ffu;
    uint32_t index = 0u;
    while (index < 37u && db_pairs[index].code != code) ++index;
    /* Native loop falls into the adjacent channel table on no match:
     * bytes 00 00 01 00 give a signed dB value of 1. */
    *result = (uint16_t)(index == 37u ? 1 : db_pairs[index].db);
    return *(volatile const uint16_t *)(const void *)(context + 0x12u);
}
