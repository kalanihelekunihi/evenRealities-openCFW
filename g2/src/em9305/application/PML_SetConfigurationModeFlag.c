/* SPDX-License-Identifier: MIT
 * Stock 0x30f710 PML_SetConfigurationModeFlag (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm; the compiled
 * -Os instructions were compared with the lowered stock code (tiny function, no harness run). Sets bit 23 (configuration mode) of 0xf00430. Name inferred from PML_ClearConfigurationModeFlag (0x30f1f8), which clears the same bit.
 */
#include <stdint.h>

void opencfw_em9305_PML_SetConfigurationModeFlag(void)
{
  *(volatile uint32_t *)(uintptr_t)0xf00430u |= 1u << 23;
}
