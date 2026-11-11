/* SPDX-License-Identifier: MIT
 * Stock 0x319204 lctrDecodeCtrlPduCaseDefault (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it in the
 * QEMU-ARC harness (.waves/w28). Fallback for opcodes with no PDU decoder (referenced 8 times by the stock dispatch table): always returns 0x19. Field names are not recovered (offsets only).
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
uint32_t opencfw_em9305_lctrDecodeCtrlPduCaseDefault(uint32_t pdu, uint32_t src, uint32_t len)
{
  (void)pdu; (void)src; (void)len;
  return 0x19u;
}
