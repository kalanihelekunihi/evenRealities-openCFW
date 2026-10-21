/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x10204b5c..0x10204c3d and case tails
 * 0x10204c3e..0x10204c61. The seven jump-table entries at 0x1020a8f4
 * were read from authenticated image bytes and resolved to these values.
 * Preserve each strobe read/write in source order; they are hardware effects.
 */
#include <stdint.h>

static volatile uint32_t *const aout =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0b00000);

static void strobe_lodac(void)
{
    uint32_t current = aout[0x28u / 4u];
    aout[0x28u / 4u] = current | 2u;
    current = aout[0x28u / 4u];
    aout[0x28u / 4u] = current & ~UINT32_C(2);
}

void gx8002_xip_aout_set_lodac_10204b5c(void)
{
    aout[0x28u / 4u] = aout[0x28u / 4u] | 1u;
    strobe_lodac();
    strobe_lodac();

    uint32_t selector = ((aout[0x04u / 4u] >> 4u) & 7u) - 1u;
    uint32_t setup;
    switch (selector) {
    case 0: setup = 2437u; break;
    case 1: setup = 2181u; break;
    case 2: setup = 2949u; break;
    case 3: setup = 2565u; break;
    case 4: setup = 2309u; break;
    case 5: setup = 2053u; break;
    case 6: setup = 3589u; break;
    default: setup = 2693u; break;
    }
    aout[0x28u / 4u] = setup;
    strobe_lodac();
    aout[0x28u / 4u] = 9u;
    strobe_lodac();

    uint32_t clock_bits = (aout[0x24u / 4u] << 4u) & ~UINT32_C(31);
    aout[0x28u / 4u] = clock_bits | 5u;
    strobe_lodac();
    aout[0x28u / 4u] = 14181u;
    strobe_lodac();
    aout[0x28u / 4u] = clock_bits | 21u;
    strobe_lodac();
    aout[0x28u / 4u] = 14181u;
    strobe_lodac();
    aout[0x28u / 4u] = 9093u;
    strobe_lodac();
}
