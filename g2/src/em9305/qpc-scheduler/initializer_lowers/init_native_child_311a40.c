#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x311a40..0x311ab4: measured radio level (RSSI) in signed
 * 16-bit units. The raw reading 0xf04428 gives an 11-bit magnitude and a
 * 3-bit gain step (bits 11..13, at most 5) that selects a calibration
 * halfword from the table at *((uintptr_t)&em9305_ram_80fd2c + 0x20u) (entries 80.. for the normal
 * receiver, 86.. when 0xf04004 bits 8..10 equal 1). Level =
 * trunc(ln(magnitude) * 86.858887) - calibration + trunc(offset * 0.2 *
 * 10), where offset is the signed byte ((uintptr_t)&em9305_ram_80fd2c + 0x32u). FPU code (profile
 * g2-em9305-2); conversions are the C casts that emit the stock fcvt32
 * modes (2: int to float, 0xb: float to int, truncating). */
extern float opencfw_em9305_child_311e04(uint32_t value);

uint32_t opencfw_em9305_radio_measured_level_311a40(void)
{
    uint32_t raw = *(volatile uint16_t *)(uintptr_t)0xf04428u;
    uintptr_t table = em9305_ram_80fd2c.u32_80fd4c;
    uint32_t mode = *(volatile uint32_t *)(uintptr_t)0xf04004u & 0x700u;
    uint32_t step = (raw >> 11) & 7u;
    if (step > 5u)
        step = 5u;
    uint32_t entry = (mode == 0x100u ? 86u : 80u) + step;
    int32_t calibration = *(volatile uint16_t *)(table + 2u * entry);
    float level = opencfw_em9305_child_311e04(raw & 0x7ffu);
    int32_t offset = em9305_ram_80fd2c.s8_80fd5e;
    float scaled = level * 0x1.5b6f8p+6f;                /* 0x42adb7c0 */
    float trim = (float)offset * 0x1.99999ap-3f;         /* 0x3e4ccccd */
    int32_t result = (int32_t)scaled - calibration + (int32_t)(trim * 10.0f);
    return (uint32_t)(int32_t)(int16_t)result;
}
