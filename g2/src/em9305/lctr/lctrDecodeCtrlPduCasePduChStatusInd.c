/* SPDX-License-Identifier: MIT
 * Stock 0x319234 lctrDecodeCtrlPduCasePduChStatusInd (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it in the
 * QEMU-ARC harness (.waves/w28). A one-byte-length PDU is rejected; requires feature byte 0x805a98 bit 7; copies src[1..10] to pdu+0xc..0x15 (the stock code uses a hardware loop) and accepts packet type 0xb. Field names are not recovered (offsets only).
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
uint32_t opencfw_em9305_lctrDecodeCtrlPduCasePduChStatusInd(uint32_t pdu, uint32_t src, uint32_t len)
{
  uint32_t i;
  if (len == 1u) return 0x19u;
  if ((B8(0x805a98u) & 0x80u) == 0u) return 0x19u;
  for (i = 0u; i < 10u; i++) B8(pdu + 0xcu + i) = B8(src + 1u + i);
  return B8(pdu + 5u) == 0xbu ? 0u : 0x19u;
}
