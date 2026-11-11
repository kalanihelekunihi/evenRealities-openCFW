/* SPDX-License-Identifier: MIT
 * Stock 0x3195a0 lctrDecodeCtrlPduCasePduPwrChangeInd (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it in the
 * QEMU-ARC harness (.waves/w28). Requires feature byte 0x805a98 bit 2; copies src[1..4] to pdu+0xc..0xf and accepts packet type 5. Field names are not recovered (offsets only).
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
uint32_t opencfw_em9305_lctrDecodeCtrlPduCasePduPwrChangeInd(uint32_t pdu, uint32_t src, uint32_t len)
{
  (void)len;
  if ((B8(0x805a98u) & 4u) == 0u) return 0x19u;
  B8(pdu + 0xcu) = B8(src + 1u);
  B8(pdu + 0xdu) = B8(src + 2u);
  B8(pdu + 0xeu) = B8(src + 3u);
  B8(pdu + 0xfu) = B8(src + 4u);
  return B8(pdu + 5u) == 5u ? 0u : 0x19u;
}
