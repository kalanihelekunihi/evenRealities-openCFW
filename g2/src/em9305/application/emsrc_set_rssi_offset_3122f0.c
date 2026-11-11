/* SPDX-License-Identifier: MIT
 * Stock 0x3122f0 emsrc_set_rssi_offset_3122f0 (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm; the compiled
 * -Os instructions were compared with the lowered stock code (tiny function, no harness run). Stores the low byte of the argument at 0x80fd5e (the RSSI offset set by EMSG_SetRssiOffset).
 */
#include <stdint.h>

void opencfw_em9305_emsrc_set_rssi_offset_3122f0(uint32_t value)
{
  *(volatile uint8_t *)(uintptr_t)0x80fd5eu = (uint8_t)value;
}
