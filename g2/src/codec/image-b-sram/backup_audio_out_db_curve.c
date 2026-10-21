/* SPDX-License-Identifier: MIT
 * Native image-B 0x1000602c/0x1000609c DAC dB mapping.
 * Stock 0x10012ad4..0x10012b68 is 37 signed-dB / 10-bit-level records.
 * Typed values below preserve the original calibrated transfer curve.
 */
#include <stdint.h>

#define LATE_AUDIO __attribute__((section(".image_b_late_audio")))

struct gx8002_audio_db_level { uint16_t level; int16_t db; };
_Static_assert(sizeof(struct gx8002_audio_db_level) == 4u, "native dB stride");
static const struct gx8002_audio_db_level db_curve[37] = {
    {16u, -18},
    {18u, -17},
    {20u, -16},
    {23u, -15},
    {25u, -14},
    {28u, -13},
    {32u, -12},
    {36u, -11},
    {40u, -10},
    {45u, -9},
    {51u, -8},
    {57u, -7},
    {64u, -6},
    {72u, -5},
    {81u, -4},
    {91u, -3},
    {102u, -2},
    {114u, -1},
    {128u, 0},
    {144u, 1},
    {162u, 2},
    {181u, 3},
    {203u, 4},
    {228u, 5},
    {256u, 6},
    {288u, 7},
    {323u, 8},
    {362u, 9},
    {407u, 10},
    {460u, 11},
    {512u, 12},
    {576u, 13},
    {646u, 14},
    {725u, 15},
    {814u, 16},
    {913u, 17},
    {1023u, 18},
};

LATE_AUDIO
int32_t gx8002_image_b_audio_out_set_db_1000602c(
    volatile uint8_t *state, int32_t requested)
{
    int32_t clamped = requested;
    if (clamped > 18) clamped = 18;
    if (clamped < -18) clamped = -18;
    uint32_t level = 0u;
    if (clamped != -18) {
        for (uint32_t i = 1u; i < 37u; ++i) {
            if (db_curve[i].db == clamped) {
                level = db_curve[i].level & 1023u;
                break;
            }
        }
    }
    /* The native LSli-16 / masked writes clear the two nibble fields;
     * the requested signed dB remains at state +0x12. Keep all three
     * ordered volatile writes, including the final bit-zero merge. */
    uint32_t shifted = level << 16;
    uint32_t low = shifted & 0xffffu;
    uint32_t nibble = shifted & 0xf00u;
    volatile uint32_t *const dac = (volatile uint32_t *)(uintptr_t)0xa0b00000u;
    uint32_t old = dac[5];
    dac[5] = (old & ~0xf00u) | nibble;
    uint32_t next = dac[5];
    dac[5] = (next & ~0xf000u) | low;
    next = dac[5];
    dac[5] = (next & ~1u) | (old & 1u);
    *(volatile uint16_t *)(volatile void *)(state + 0x12u) = (uint16_t)requested;
    return 0;
}

LATE_AUDIO
uint32_t gx8002_image_b_audio_out_get_db_1000609c(
    volatile uint8_t *state, volatile int16_t *out_db)
{
    volatile uint32_t *const dac = (volatile uint32_t *)(uintptr_t)0xa0b00000u;
    uint16_t level = (uint16_t)((dac[5] >> 16) & 1023u);
    int16_t db = 0;
    if (level == 16u) {
        db = -18;
    } else {
        for (uint32_t i = 1u; i < 37u; ++i) {
            if (db_curve[i].level == level) {
                db = db_curve[i].db;
                break;
            }
        }
    }
    *out_db = db;
    return *(volatile uint16_t *)(volatile void *)(state + 0x12u);
}
