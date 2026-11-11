/* SPDX-License-Identifier: MIT
 * Stock 0x319414 lctrDecodeCtrlPduCasePduFeatureReq (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it in the
 * QEMU-ARC harness (.waves/w28). FLAG: name from the opcode position (0x08 LL_FEATURE_REQ) in the stock dispatch table 0x334d0c, the stock image names this block 'unnamed'. Rejects an empty PDU, else behaves exactly like the FeatureRsp case (the stock code jumps into it): child validator packet_child_32dfe8, packet type 9. Field names are not recovered (offsets only).
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_packet_child_32dfe8(uint32_t body);
uint32_t opencfw_em9305_lctrDecodeCtrlPduCasePduFeatureReq(uint32_t pdu, uint32_t src, uint32_t len)
{
  (void)src;
  if (len == 0u) return 0x19u;
  (void)opencfw_em9305_packet_child_32dfe8(pdu + 0xcu);
  return B8(pdu + 5u) == 9u ? 0u : 0x19u;
}
