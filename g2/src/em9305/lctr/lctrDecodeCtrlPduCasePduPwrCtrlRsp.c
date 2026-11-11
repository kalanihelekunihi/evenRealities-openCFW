/* SPDX-License-Identifier: MIT
 * Stock 0x3195f4 lctrDecodeCtrlPduCasePduPwrCtrlRsp (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and
 * verified against it in the QEMU-ARC harness (.waves/w28, 300 tests). If bit 1 of the byte at 0x805a98 is set, copies four
 * response bytes (src+1..4) into the PDU body and accepts packet type 5. Field names are not recovered (offsets only).
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
uint32_t opencfw_em9305_lctrDecodeCtrlPduCasePduPwrCtrlRsp(uint32_t pdu, uint32_t src)
{
  uint8_t b1, b2, b3, ty, b4;
  if ((B8(0x805a98u) & 0x2u) == 0u) return 0x19u;
  b1 = B8(src + 1u);
  B8(pdu + 0xcu) = b1;
  b2 = B8(src + 2u);
  B8(pdu + 0xdu) = b2;
  b3 = B8(src + 3u);
  ty = B8(pdu + 5u);
  B8(pdu + 0xeu) = b3;
  b4 = B8(src + 4u);
  B8(pdu + 0xfu) = b4;
  return ty == 5u ? 0u : 0x19u;
}
