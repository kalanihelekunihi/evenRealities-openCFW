/* SPDX-License-Identifier: MIT
 * Stock 0x310aa8 (ProtTimer_RestoreConfig) and 0x310c08 (ProtTimer_StoreConfig), g2-2.2.6.10 firmware_ble_em9305.bin.
 * The state record at 0x80fd20 has the saved-configuration pointer at +0xc and the timer index byte at +0x14. The saved block holds
 * (word index): 0 = register 0xf01804, 1 = register 0xf01808, 2 = register 0xf0180c, 3..16 = registers 0xf01810..0xf01844,
 * 17 = the word at 0xf00480 + 4 * timer index, 19 = cleared after a store. FLAG: register meanings (the block at 0xf018xx) and the saved-block
 * words 17/18/19 are named by address only; the bytes at 0xf0047a (bit mask per timer index, low 4 bits) and 0xf0047c.. (one byte per index < 3)
 * and the byte at 0xf0383b (bits 0..1 == 3 together with bit 1 of register 0xf0180c request a wake-up marker) are not understood. The state record
 * is addressed by literal, as in stock, because nothing else in C allocates it.
 */
#include <stdint.h>

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

struct prot_timer_state {
  uint32_t word_0[3];
  struct prot_timer_saved *saved;
  uint32_t word_10;
  uint8_t timer;
};

#define PT_STATE ((struct prot_timer_state *)(uintptr_t)0x80fd20u)

void opencfw_em9305_stock_310aa8(void)
{
  struct prot_timer_state *st = PT_STATE;
  RW32(0xf01804u) = st->saved->reg_f01804;
  for (uint32_t i = 0u; i < 14u; i++) RW32(0xf01810u + 4u * i) = st->saved->regs_f01810[i];
  uint32_t t = st->timer;
  if (t < 3u) RB8(0xf0047cu + t) = 0u;
  RB8(0xf0047au) = (uint8_t)(((1u << (st->timer & 31u)) & 0xfu) | RB8(0xf0047au));
  uint32_t second = st->saved->reg_f01808;
  RW32(0xf01814u) = second;
  RW32(0xf01800u) = 512u;
}

void opencfw_em9305_stock_310c08(void)
{
  struct prot_timer_state *st = PT_STATE;
  st->saved->reg_f0180c = RW32(0xf0180cu);
  st->saved->reg_f01804 = RW32(0xf01804u);
  uint32_t skip = ((st->saved->reg_f0180c & 2u) == 0u) || ((RB8(0xf0383bu) & 3u) != 3u);
  if (!skip) {
    uint32_t t = st->timer;
    if (t < 3u) RB8(0xf0047cu + t) = 1u;
    RB8(0xf0047au) = (uint8_t)(((1u << (st->timer & 31u)) & 0xfu) | RB8(0xf0047au));
    RW32(0xf01804u) = RW32(0xf01804u) | (1u << 17);
    __builtin_arc_nop(); __builtin_arc_nop(); __builtin_arc_nop(); __builtin_arc_nop();
  }
  RW32(0xf01800u) = 2u;
  for (uint32_t i = 0u; i < 14u; i++) st->saved->regs_f01810[i] = RW32(0xf01810u + 4u * i);
  if (skip) return;
  while (RW32(0xf0180cu) & 1u) {}
  st->saved->reg_f01808 = RW32(0xf01808u);
  st->saved->timer_slot = RW32(0xf00480u + 4u * st->timer);
  RB8(0xf0047au) = (uint8_t)(((~(1u << (st->timer & 31u))) | 240u) & RB8(0xf0047au));
  st->saved->cleared = 0u;
}
