/* SPDX-License-Identifier: MIT
 * Stock 0x30f720 emsys_set_configuration_mode_flag_30f720 (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm; the compiled
 * -Os instructions were compared with the lowered stock code (tiny function, no harness run). Byte-identical second copy of 0x30f710 (sets bit 23 of 0xf00430); called from the system-reset path.
 */
#include <stdint.h>

void opencfw_em9305_emsys_set_configuration_mode_flag_30f720(void)
{
  *(volatile uint32_t *)(uintptr_t)0xf00430u |= 1u << 23;
}
