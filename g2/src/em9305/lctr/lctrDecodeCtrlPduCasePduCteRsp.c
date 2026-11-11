/* SPDX-License-Identifier: MIT
 * Stock 0x319400 lctrDecodeCtrlPduCasePduCteRsp (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it in the
 * QEMU-ARC harness (.waves/w28). Accepts the PDU (returns 0) only when feature flag bit 1 (byte 0x805a96) is set, else 0x19. Field names are not recovered (offsets only).
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
uint32_t opencfw_em9305_lctrDecodeCtrlPduCasePduCteRsp(uint32_t pdu, uint32_t src, uint32_t len)
{
  (void)pdu; (void)src; (void)len;
  return (B8(0x805a96u) & 2u) ? 0u : 0x19u;
}
