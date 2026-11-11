/* SPDX-License-Identifier: MIT
 * Stock 0x319620 lctrDecodeCtrlPduCasePduRejectExtInd (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it in the
 * QEMU-ARC harness (.waves/w28). Requires feature byte 0x805a94 bit 2; copies src[1], src[2] to pdu+0xc/+0xd and accepts packet type 3. Field names are not recovered (offsets only).
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
uint32_t opencfw_em9305_lctrDecodeCtrlPduCasePduRejectExtInd(uint32_t pdu, uint32_t src, uint32_t len)
{
  (void)len;
  if ((B8(0x805a94u) & 4u) == 0u) return 0x19u;
  B8(pdu + 0xcu) = B8(src + 1u);
  B8(pdu + 0xdu) = B8(src + 2u);
  return B8(pdu + 5u) == 3u ? 0u : 0x19u;
}
