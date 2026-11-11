/* SPDX-License-Identifier: MIT
 * Stock 0x3192c0 lctrDecodeCtrlPduCasePduCisReq (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it in the
 * QEMU-ARC harness (.waves/w28). Requires feature word 0x805a94 bit 29 and packet type 0x24u (child validator at packet_child_32dc40 runs first). Field names are not recovered (offsets only).
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_packet_child_32dc40(uint32_t body);
uint32_t opencfw_em9305_lctrDecodeCtrlPduCasePduCisReq(uint32_t pdu, uint32_t src, uint32_t len)
{
  (void)src;
  if (len == 0u) return 0x19u;
  if ((W32(0x805a94u) & (1u << 29)) == 0u) return 0x19u;
  (void)opencfw_em9305_packet_child_32dc40(pdu + 0xcu);
  return B8(pdu + 5u) == 0x24u ? 0u : 0x19u;
}
