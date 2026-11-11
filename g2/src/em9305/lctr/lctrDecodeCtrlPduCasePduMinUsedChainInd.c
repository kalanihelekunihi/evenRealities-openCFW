/* SPDX-License-Identifier: MIT
 * Stock 0x319450 lctrDecodeCtrlPduCasePduMinUsedChainInd (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it in the
 * QEMU-ARC harness (.waves/w28). LL_MIN_USED_CHANNELS_IND (opcode 0x19, its slot in the stock opcode dispatch table 0x334d0c, BT Core Vol 6 Part B 2.4.2; the 2..37 range matches the spec): len!=1, feature bit 0, packet type 3; copies PHY mask src[1]&7 (must be nonzero) and the min-channel count src[2] (must be 2..37) to pdu+0xc/+0xd. Field names are not recovered (offsets only).
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
uint32_t opencfw_em9305_lctrDecodeCtrlPduCasePduMinUsedChainInd(uint32_t pdu, uint32_t src, uint32_t len)
{
  uint32_t phys, cnt;
  if (len == 1u) return 0x19u;
  if ((B8(0x805a96u) & 1u) == 0u) return 0x19u;
  phys = B8(src + 1u) & 7u;
  cnt = B8(src + 2u);
  B8(pdu + 0xcu) = (uint8_t)phys;
  B8(pdu + 0xdu) = (uint8_t)cnt;
  if (B8(pdu + 5u) != 3u) return 0x19u;
  if (phys == 0u) return 0x1eu;
  return (uint8_t)(cnt - 0x26u) > 219u ? 0u : 0x1eu;
}
