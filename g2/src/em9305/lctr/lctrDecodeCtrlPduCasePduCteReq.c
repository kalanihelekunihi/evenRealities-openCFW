/* SPDX-License-Identifier: MIT
 * Stock 0x3193d8 lctrDecodeCtrlPduCasePduCteReq (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it in the
 * QEMU-ARC harness (.waves/w28). Requires feature flag bit 2 (byte 0x805a96) and packet type 2; copies the request byte src[1] split into low 5 bits (pdu+0xc) and bits 7:6 (pdu+0xd). Field names are not recovered (offsets only).
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
uint32_t opencfw_em9305_lctrDecodeCtrlPduCasePduCteReq(uint32_t pdu, uint32_t src, uint32_t len)
{
  uint32_t b;
  (void)len;
  if ((B8(0x805a96u) & 4u) == 0u) return 0x19u;
  b = B8(src + 1u);
  B8(pdu + 0xdu) = (uint8_t)(b >> 6);
  B8(pdu + 0xcu) = (uint8_t)(b & 0x1fu);
  return B8(pdu + 5u) == 2u ? 0u : 0x19u;
}
