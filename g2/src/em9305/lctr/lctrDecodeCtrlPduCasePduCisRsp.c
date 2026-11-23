/* SPDX-License-Identifier: MIT
 * Stock 0x3192e8 lctrDecodeCtrlPduCasePduCisRsp (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it in the
 * QEMU-ARC harness (.waves/w28). Requires feature word ((uintptr_t)&em9305_ram_805a6c + 0x28u) bit 28 and packet type 9u (child validator at packet_child_32dd20 runs first). Field names are not recovered (offsets only).
 */
#include <stdint.h>
#include "em9305_ram.h"
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_packet_child_32dd20(uint32_t body);
uint32_t opencfw_em9305_lctrDecodeCtrlPduCasePduCisRsp(uint32_t pdu, uint32_t src, uint32_t len)
{
  (void)src;
  if (len == 1u) return 0x19u;
  if ((W32(((uintptr_t)&em9305_ram_805a6c + 0x28u)) & (1u << 28)) == 0u) return 0x19u;
  (void)opencfw_em9305_packet_child_32dd20(pdu + 0xcu);
  return B8(pdu + 5u) == 9u ? 0u : 0x19u;
}
