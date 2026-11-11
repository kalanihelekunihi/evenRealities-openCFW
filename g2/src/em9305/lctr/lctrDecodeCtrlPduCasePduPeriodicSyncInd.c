/* SPDX-License-Identifier: MIT
 * Stock 0x3194f4 lctrDecodeCtrlPduCasePduPeriodicSyncInd (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it in the
 * QEMU-ARC harness (.waves/w28). Requires feature byte 0x805a97 bit 1 and packet type 0x23u (child validator packet_child_32dffc runs first). Field names are not recovered (offsets only).
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_packet_child_32dffc(uint32_t body);
uint32_t opencfw_em9305_lctrDecodeCtrlPduCasePduPeriodicSyncInd(uint32_t pdu, uint32_t src, uint32_t len)
{
  (void)src; (void)len;
  if ((B8(0x805a97u) & 2u) == 0u) return 0x19u;
  (void)opencfw_em9305_packet_child_32dffc(pdu + 0xcu);
  return B8(pdu + 5u) == 0x23u ? 0u : 0x19u;
}
