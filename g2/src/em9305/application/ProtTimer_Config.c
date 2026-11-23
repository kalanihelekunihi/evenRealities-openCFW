/* SPDX-License-Identifier: MIT
 * Stock 0x310aa8 (ProtTimer_RestoreConfig) and 0x310c08 (ProtTimer_StoreConfig), g2-2.2.6.10 firmware_ble_em9305.bin.
 * The hook record at em9305_ram_80fd20 is followed by em9305_ram_80fd2c (saved-configuration pointer at u32_80fd2c, timer index at u8_80fd34). The saved block holds
 * (word index): 0 = register 0xf01804, 1 = register 0xf01808, 2 = register 0xf0180c, 3..16 = registers 0xf01810..0xf01844,
 * 17 = the word at 0xf00480 + 4 * timer index, 19 = cleared after a store. FLAG: register meanings (the block at 0xf018xx) and the saved-block
 * words 17/18/19 are named by address only; the bytes at 0xf0047a (bit mask per timer index, low 4 bits) and 0xf0047c.. (one byte per index < 3)
 * and the byte at 0xf0383b (bits 0..1 == 3 together with bit 1 of register 0xf0180c request a wake-up marker) are not understood. The state record
 * lives at em9305_ram_8011f8 after ini_record e1 copies that address into u32_80fd2c.
 */
#include <stdint.h>
#include "em9305_ram.h"

#define RW32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define RB8(a)  (*(volatile uint8_t *)(uintptr_t)(a))

struct prot_timer_saved {
  uint32_t reg_f01804;
  uint32_t reg_f01808;
  uint32_t reg_f0180c;
  uint32_t regs_f01810[14];
  uint32_t timer_slot;
  uint32_t word_18;
  uint32_t cleared;
};

void opencfw_em9305_stock_310aa8(void)
{
  /* Hooks at em9305_ram_80fd20 are sleep_lock_update slots, not used here.
   * saved and timer live on the adjacent typo object (do not index 80fd20 past 12 bytes). */
  struct prot_timer_saved *saved = (struct prot_timer_saved *)(uintptr_t)em9305_ram_80fd2c.u32_80fd2c;
  uint8_t timer = em9305_ram_80fd2c.u8_80fd34;
  RW32(0xf01804u) = saved->reg_f01804;
  for (uint32_t i = 0u; i < 14u; i++) RW32(0xf01810u + 4u * i) = saved->regs_f01810[i];
  uint32_t t = timer;
  if (t < 3u) RB8(0xf0047cu + t) = 0u;
  RB8(0xf0047au) = (uint8_t)(((1u << (timer & 31u)) & 0xfu) | RB8(0xf0047au));
  uint32_t second = saved->reg_f01808;
  RW32(0xf01814u) = second;
  RW32(0xf01800u) = 512u;
}

void opencfw_em9305_stock_310c08(void)
{
  struct prot_timer_saved *saved = (struct prot_timer_saved *)(uintptr_t)em9305_ram_80fd2c.u32_80fd2c;
  uint8_t timer = em9305_ram_80fd2c.u8_80fd34;
  saved->reg_f0180c = RW32(0xf0180cu);
  saved->reg_f01804 = RW32(0xf01804u);
  uint32_t skip = ((saved->reg_f0180c & 2u) == 0u) || ((RB8(0xf0383bu) & 3u) != 3u);
  if (!skip) {
    uint32_t t = timer;
    if (t < 3u) RB8(0xf0047cu + t) = 1u;
    RB8(0xf0047au) = (uint8_t)(((1u << (timer & 31u)) & 0xfu) | RB8(0xf0047au));
    RW32(0xf01804u) = RW32(0xf01804u) | (1u << 17);
    __builtin_arc_nop(); __builtin_arc_nop(); __builtin_arc_nop(); __builtin_arc_nop();
  }
  RW32(0xf01800u) = 2u;
  for (uint32_t i = 0u; i < 14u; i++) saved->regs_f01810[i] = RW32(0xf01810u + 4u * i);
  if (skip) return;
  while (RW32(0xf0180cu) & 1u) {}
  saved->reg_f01808 = RW32(0xf01808u);
  saved->timer_slot = RW32(0xf00480u + 4u * timer);
  RB8(0xf0047au) = (uint8_t)(((~(1u << (timer & 31u))) | 240u) & RB8(0xf0047au));
  saved->cleared = 0u;
}
