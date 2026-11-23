/* SPDX-License-Identifier: MIT
 * Stock 0x319574 lctrDecodeCtrlPduCasePduPhyUpdateInd (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it in the
 * QEMU-ARC harness (.waves/w28). Rejects an empty PDU; requires feature byte ((uintptr_t)&em9305_ram_805a6c + 0x29u) & 9 nonzero and packet type 5 (child validator packet_child_32e128 runs first). Field names are not recovered (offsets only).
 */
#include <stdint.h>
#include "em9305_ram.h"
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_packet_child_32e128(uint32_t body);
uint32_t opencfw_em9305_lctrDecodeCtrlPduCasePduPhyUpdateInd(uint32_t pdu, uint32_t src, uint32_t len)
{
  (void)src;
  if (len == 0u) return 0x19u;
  if ((B8(((uintptr_t)&em9305_ram_805a6c + 0x29u)) & 9u) == 0u) return 0x19u;
  (void)opencfw_em9305_packet_child_32e128(pdu + 0xcu);
  return B8(pdu + 5u) == 5u ? 0u : 0x19u;
}
