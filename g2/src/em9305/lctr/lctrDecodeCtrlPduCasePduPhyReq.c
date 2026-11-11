/* SPDX-License-Identifier: MIT
 * Stock 0x31953c lctrDecodeCtrlPduCasePduPhyReq (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it in the
 * QEMU-ARC harness (.waves/w28). Requires feature byte 0x805a95 & 9 nonzero and packet type 3 (child validator packet_child_32e114 runs first). Field names are not recovered (offsets only).
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_packet_child_32e114(uint32_t body);
uint32_t opencfw_em9305_lctrDecodeCtrlPduCasePduPhyReq(uint32_t pdu, uint32_t src, uint32_t len)
{
  (void)src; (void)len;
  if ((B8(0x805a95u) & 9u) == 0u) return 0x19u;
  (void)opencfw_em9305_packet_child_32e114(pdu + 0xcu);
  return B8(pdu + 5u) == 3u ? 0u : 0x19u;
}
