/* SPDX-License-Identifier: MIT
 * Stock 0x319518 lctrDecodeCtrlPduCasePduPeriodicSyncWrInd (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it in the
 * QEMU-ARC harness (.waves/w28). Requires feature byte ((uintptr_t)&em9305_ram_805a6c + 0x2bu) bit 1 and packet type 0x2bu (child validator packet_child_32e068 runs first). Field names are not recovered (offsets only).
 */
#include <stdint.h>
#include "em9305_ram.h"
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_packet_child_32e068(uint32_t body);
uint32_t opencfw_em9305_lctrDecodeCtrlPduCasePduPeriodicSyncWrInd(uint32_t pdu, uint32_t src, uint32_t len)
{
  (void)src; (void)len;
  if ((B8(((uintptr_t)&em9305_ram_805a6c + 0x2bu)) & 2u) == 0u) return 0x19u;
  (void)opencfw_em9305_packet_child_32e068(pdu + 0xcu);
  return B8(pdu + 5u) == 0x2bu ? 0u : 0x19u;
}
