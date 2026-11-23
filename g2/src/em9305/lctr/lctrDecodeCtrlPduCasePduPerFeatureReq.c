/* SPDX-License-Identifier: MIT
 * Stock 0x3194cc lctrDecodeCtrlPduCasePduPerFeatureReq (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it in the
 * QEMU-ARC harness (.waves/w28). A one-byte-length PDU is rejected; requires feature byte ((uintptr_t)&em9305_ram_805a6c + 0x28u) bit 3; child validator packet_child_32dfe8; packet type 9. Field names are not recovered (offsets only).
 */
#include <stdint.h>
#include "em9305_ram.h"
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_packet_child_32dfe8(uint32_t body);
uint32_t opencfw_em9305_lctrDecodeCtrlPduCasePduPerFeatureReq(uint32_t pdu, uint32_t src, uint32_t len)
{
  (void)src;
  if (len == 1u) return 0x19u;
  if ((B8(((uintptr_t)&em9305_ram_805a6c + 0x28u)) & 8u) == 0u) return 0x19u;
  (void)opencfw_em9305_packet_child_32dfe8(pdu + 0xcu);
  return B8(pdu + 5u) == 9u ? 0u : 0x19u;
}
