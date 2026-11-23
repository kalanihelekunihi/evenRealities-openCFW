/* SPDX-License-Identifier: MIT
 * Stock 0x305a20 emsmm_write_memory_305a20 (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified against it
 * in the QEMU-ARC harness (.waves/w28). Writes count bytes to the address kept at [obj+0x70] (advanced by count). Regions 1 and 5 (RAM/peripheral): ROM word copy or memcpy. Regions 2 and 3 (0x300000 / 0x400000 based flash): word-aligned only, via 0x30f014(bank = region == 3, word index, src, words): 0 -> 0, 3 -> 0x12, else 3. Other regions or misalignment -> 0x12. Used by EMSMM_WriteAtAddress and WriteContinue.
 * Helper of the em_system memory commands (not a command handler itself).
 */
#include <stdint.h>
#include "em9305_ram.h"
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_emsmm_region_id_305944(uint32_t addr, uint32_t len);
extern uint32_t opencfw_em9305_stock_30f014(uint32_t bank, uint32_t index, const uint8_t *src, uint32_t nwords);
extern void opencfw_em9305_rom_copy_words_100d20(void *dst, const void *src, uint32_t nwords);
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t bytes);
uint32_t opencfw_em9305_emsmm_write_memory_305a20(const uint8_t *src, uint32_t count)
{
  uint32_t obj = W32(((uintptr_t)&em9305_ram_801090 + 0x8u));
  uint32_t addr = W32(obj + 0x70u);
  uint32_t reg, r;
  W32(obj + 0x70u) = addr + count;
  reg = opencfw_em9305_emsmm_region_id_305944(addr, count);
  if (reg - 2u < 2u) {
    uint32_t base;
    if (((addr | count) & 3u) != 0u) return 0x12u;
    base = (reg == 3u) ? 0x400000u : 0x300000u;
    r = opencfw_em9305_stock_30f014(reg == 3u, (addr - base) >> 2, src, count >> 2);
    if (r == 3u) return 0x12u;
    return (r == 0u) ? 0u : 3u;
  }
  if (reg != 1u && reg != 5u) return 0x12u;
  if (((addr | count) & 3u) == 0u) opencfw_em9305_rom_copy_words_100d20((void *)(uintptr_t)addr, src, count >> 2);
  else (void)opencfw_em9305_memcpy((void *)(uintptr_t)addr, src, count);
  return 0u;
}
