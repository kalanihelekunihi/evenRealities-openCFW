/* SPDX-License-Identifier: MIT
 * Stock 0x319438 lctrDecodeCtrlPduCasePduLengthReqRsp (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it in the
 * QEMU-ARC harness (.waves/w28). FLAG: name from the opcode positions (0x14 LL_LENGTH_REQ and 0x15 LL_LENGTH_RSP both point here in the stock dispatch table 0x334d0c). Runs the child validator packet_child_32deac on the body and accepts packet type 9. Field names are not recovered (offsets only).
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_packet_child_32deac(uint32_t body);
uint32_t opencfw_em9305_lctrDecodeCtrlPduCasePduLengthReqRsp(uint32_t pdu, uint32_t src, uint32_t len)
{
  (void)src; (void)len;
  (void)opencfw_em9305_packet_child_32deac(pdu + 0xcu);
  return B8(pdu + 5u) == 9u ? 0u : 0x19u;
}
