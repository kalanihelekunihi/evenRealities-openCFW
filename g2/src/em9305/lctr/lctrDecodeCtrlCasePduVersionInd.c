/* SPDX-License-Identifier: MIT
 * Stock 0x3191c4 lctrDecodeCtrlCasePduVersionInd (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it in the
 * QEMU-ARC harness (.waves/w28). Runs the child validator packet_child_32e1f4 on the body and accepts packet type 6. Field names are not recovered (offsets only).
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_packet_child_32e1f4(uint32_t body);
uint32_t opencfw_em9305_lctrDecodeCtrlCasePduVersionInd(uint32_t pdu, uint32_t src, uint32_t len)
{
  (void)src; (void)len;
  (void)opencfw_em9305_packet_child_32e1f4(pdu + 0xcu);
  return B8(pdu + 5u) == 6u ? 0u : 0x19u;
}
