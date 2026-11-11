/* SPDX-License-Identifier: MIT
 * Stock 0x312430 (RF_TestModeStart), g2-2.2.6.10 firmware_ble_em9305.bin. Programs the radio test pattern registers for a test mode (0..7) and starts
 * the transmit trigger (0x312390). Returns 1 when a mode was started and 0 for a mode of 8 or more. Mode 0/1 write 0xf04040 = 0x110/0x6000,
 * 0xf04044 = 0xffffffff, 0xf04050 = 16, 0xf040bc = 0x10000; modes 2..7 write 0xf040bc = 0, 0xffff, 0x5555, 0x3333, 0x0f0f, 0xff respectively, then
 * 0xf04050 = 0 and set bit 16 of 0xf040bc. Register meanings are not recovered (named by address only).
 * FLAG: stock keeps its return address in r3 across the trigger call (`mov_s r3,blink ... j_s [r3]`), i.e. it relies on 0x312390 not touching r3;
 * the C version has no such dependence.
 */
#include <stdint.h>

#define RW32(a) (*(volatile uint32_t *)(uintptr_t)(a))

extern uint32_t opencfw_em9305_radio_transmit_trigger_312390(void);

uint32_t opencfw_em9305_stock_312430(uint32_t mode)
{
  if (mode >= 8u) return 0u;
  if (mode <= 1u) {
    RW32(0xf04040u) = mode == 0u ? 272u : 0x6000u;
    RW32(0xf04044u) = 0xffffffffu;
    RW32(0xf04050u) = 16u;
    RW32(0xf040bcu) = 0x10000u;
  } else {
    uint32_t pattern;
    switch (mode) {
    case 2: pattern = 0u; break;
    case 3: pattern = 0xffffu; break;
    case 4: pattern = 0x5555u; break;
    case 5: pattern = 0x3333u; break;
    case 6: pattern = 0x0f0fu; break;
    default: pattern = 0xffu; break;
    }
    RW32(0xf040bcu) = pattern;
    RW32(0xf04050u) = 0u;
    RW32(0xf040bcu) = RW32(0xf040bcu) | 0x10000u;
  }
  (void)opencfw_em9305_radio_transmit_trigger_312390();
  return 1u;
}
