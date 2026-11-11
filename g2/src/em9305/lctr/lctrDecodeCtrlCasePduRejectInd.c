/* SPDX-License-Identifier: MIT
 * Stock 0x3191ac lctrDecodeCtrlCasePduRejectInd (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it in the
 * QEMU-ARC harness (.waves/w28). Stores 0xff at pdu+0xc and the error code src[1] at pdu+0xd; accepts packet type 2. Field names are not recovered (offsets only).
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
uint32_t opencfw_em9305_lctrDecodeCtrlCasePduRejectInd(uint32_t pdu, uint32_t src, uint32_t len)
{
  (void)len;
  B8(pdu + 0xcu) = 0xffu;
  B8(pdu + 0xdu) = B8(src + 1u);
  return B8(pdu + 5u) == 2u ? 0u : 0x19u;
}
