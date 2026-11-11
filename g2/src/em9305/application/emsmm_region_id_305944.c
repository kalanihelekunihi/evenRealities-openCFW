/* SPDX-License-Identifier: MIT
 * Stock 0x305944 emsmm_region_id_305944 (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). Classifies the byte range [addr, addr + len) by memory map: 1 at or above 0xf00000, 2 inside 0x300000..0x380000, 3 inside 0x400000..0x408000, 4 inside 0x100000..0x110000, 5 inside 0x800000..0x810000, 0x180000..0x188000 or 0x1ff000..0x200000, else 0. Region meanings are not documented; the numbering is the original return value. Name inferred from its callers (the EMSMM read and write helpers).
 * Helper of the em_system memory commands (not a command handler itself).
 */
#include <stdint.h>
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
uint32_t opencfw_em9305_emsmm_region_id_305944(uint32_t addr, uint32_t len)
{
  uint32_t end;
  if (addr >= 0xf00000u) return 1u;
  end = addr + len;
  if (addr >= 0x300000u && 0x380000u >= end) return 2u;
  if (addr >= 0x400000u && 0x408000u >= end) return 3u;
  if (addr >= 0x100000u && 0x110000u >= end) return 4u;
  if (addr >= 0x800000u && 0x810000u >= end) return 5u;
  if (addr >= 0x180000u && 0x188000u >= end) return 5u;
  if (addr >= 0x1ff000u && 0x200000u >= end) return 5u;
  return 0u;
}
