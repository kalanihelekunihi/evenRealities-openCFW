/* SPDX-License-Identifier: MIT
 * Stock 0x3172ec lctrBigTxCtrlQueuePeek (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified
 * against it in the QEMU-ARC harness (.waves/w28). Field names are not recovered (offsets only).
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
uint32_t opencfw_em9305_lctrBigTxCtrlQueuePeek(uint32_t big, uint32_t out)
{
  uint32_t e;
  B8(out) = 0u;
  e = *(volatile uint32_t *)(uintptr_t)(big + 184u);
  if (e == 0u) return 0u;
  B8(out) = (uint8_t)(B8(e + 4u) >> 7);
  return e + 8u;
}
