/* SPDX-License-Identifier: MIT
 * Stock 0x332b70 lhciVsExtDecodeCmdPkt (g2-2.2.6.10 firmware_ble_em9305.bin), the callback controller_init installs at boot. Wave 28: converted
 * from the lowered ARC asm and verified against it in the QEMU-ARC harness (.waves/w28, ROM call mocked through its binding). Hands the
 * command packet header (opcode halfword at +0, length byte at +2), the caller's second argument, a 0xff limit and a 256-byte stack scratch
 * buffer to the resident IROM routine at 0x101e48 and always returns 1. Field names are not recovered (offsets only).
 */
#include <stdint.h>
extern uint32_t opencfw_em9305_rom_lhci_vs_ext_101e48(uint32_t opcode, uint32_t len, uint32_t arg, uint32_t limit, uint8_t *scratch);
uint32_t opencfw_em9305_lhciVsExtDecodeCmdPkt(const uint8_t *pkt, uint32_t arg)
{
  uint8_t scratch[256];
  (void)opencfw_em9305_rom_lhci_vs_ext_101e48(*(const volatile uint16_t *)pkt, pkt[2], arg, 0xffu, scratch);
  return 1u;
}
