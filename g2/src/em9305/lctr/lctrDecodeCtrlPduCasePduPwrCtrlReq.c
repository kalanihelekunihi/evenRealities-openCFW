/* SPDX-License-Identifier: MIT
 * Stock 0x3195cc lctrDecodeCtrlPduCasePduPwrCtrlReq (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and
 * verified against it in the QEMU-ARC harness (.waves/w28, 300 tests). If bit 1 of the byte at 0x805a98 is set, copies the three
 * LL_POWER_CONTROL_REQ bytes (src+1..3) into the PDU body and accepts packet type 4. Field names are not recovered (offsets only).
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
uint32_t opencfw_em9305_lctrDecodeCtrlPduCasePduPwrCtrlReq(uint32_t pdu, uint32_t src)
{
  uint8_t b1, b2, ty, b3;
  if ((B8(0x805a98u) & 0x2u) == 0u) return 0x19u;
  b1 = B8(src + 1u);
  B8(pdu + 0xcu) = b1;
  b2 = B8(src + 2u);
  ty = B8(pdu + 5u);
  B8(pdu + 0xdu) = b2;
  b3 = B8(src + 3u);
  B8(pdu + 0xeu) = b3;
  return ty == 4u ? 0u : 0x19u;
}
