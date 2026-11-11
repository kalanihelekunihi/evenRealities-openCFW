/* SPDX-License-Identifier: MIT
 * Stock 0x3059d8 emsmm_read_memory_3059d8 (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). Copies count bytes from the address kept at [obj+0x6c] (advanced by count) into dst when the region id is 1..5, using the ROM word copy when address and count are 4-byte aligned, else memcpy; returns 0, or 0x12 for an unmapped range. Used by EMSMM_ReadAtAddress.
 * Helper of the em_system memory commands (not a command handler itself).
 */
#include <stdint.h>
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_emsmm_region_id_305944(uint32_t addr, uint32_t len);
extern void opencfw_em9305_rom_copy_words_100ca8(void *dst, const void *src, uint32_t nwords);
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t bytes);
uint32_t opencfw_em9305_emsmm_read_memory_3059d8(uint8_t *dst, uint32_t count)
{
  uint32_t obj = W32(0x801098u);
  uint32_t addr = W32(obj + 0x6cu);
  W32(obj + 0x6cu) = addr + count;
  if (opencfw_em9305_emsmm_region_id_305944(addr, count) - 1u > 4u) return 0x12u;
  if (((addr | count) & 3u) == 0u) opencfw_em9305_rom_copy_words_100ca8(dst, (const void *)(uintptr_t)addr, count >> 2);
  else (void)opencfw_em9305_memcpy(dst, (const void *)(uintptr_t)addr, count);
  return 0u;
}
