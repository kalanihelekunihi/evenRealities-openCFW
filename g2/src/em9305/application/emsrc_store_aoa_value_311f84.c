/* SPDX-License-Identifier: MIT
 * Stock 0x311f84 emsrc_store_aoa_value_311f84 (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm; the compiled
 * -Os instructions were compared with the lowered stock code (tiny function, no harness run). Stores the low 16 bits of the argument at 0x805fdc (second value of EMSRC_setAOADCteConfig).
 */
#include <stdint.h>

void opencfw_em9305_emsrc_store_aoa_value_311f84(uint32_t value)
{
  *(volatile uint16_t *)(uintptr_t)0x805fdcu = (uint16_t)value;
}
