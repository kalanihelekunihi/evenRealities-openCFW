/* SPDX-License-Identifier: MIT
 * Stock 0x30f1f8 PML_ClearConfigurationModeFlag (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm; the compiled
 * -Os instructions were compared with the lowered stock code (tiny function, no harness run). Clears bit 23 (configuration mode) of 0xf00430.
 */
#include <stdint.h>

void opencfw_em9305_PML_ClearConfigurationModeFlag(void)
{
  *(volatile uint32_t *)(uintptr_t)0xf00430u &= ~(1u << 23);
}
