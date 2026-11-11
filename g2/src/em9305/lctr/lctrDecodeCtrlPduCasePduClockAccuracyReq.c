/* SPDX-License-Identifier: MIT
 * Stock 0x31948c lctrDecodeCtrlPduCasePduClockAccuracyReq (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it in the
 * QEMU-ARC harness (.waves/w28). LL_CLOCK_ACCURACY_REQ (FLAG: opcode 0x1d/0x1e from the position in the stock opcode dispatch table 0x334d0c; the stock image names this block 'unnamed'): requires feature byte 0x805a97 bit 2 and packet type 2; copies the SCA byte src[1] to pdu+0xc. Field names are not recovered (offsets only).
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
uint32_t opencfw_em9305_lctrDecodeCtrlPduCasePduClockAccuracyReq(uint32_t pdu, uint32_t src, uint32_t len)
{
  (void)len;
  if ((B8(0x805a97u) & 4u) == 0u) return 0x19u;
  B8(pdu + 0xcu) = B8(src + 1u);
  return B8(pdu + 5u) == 2u ? 0u : 0x19u;
}
