/* SPDX-License-Identifier: MIT
 * Stock 0x30f014 (g2-2.2.6.10 firmware_ble_em9305.bin; stock_residual_code.c named it application_sleep_gap): write `nwords` 32-bit words from `src`
 * into the NVM, starting at word `index`, as the em_system memory-write command does for the region selected by `bank` (the caller passes reg == 3).
 * Returns 3 for an empty or out-of-range request (the end must not pass 0x20000 words for bank 0 or 0x2000 words otherwise), 1 if the ROM routine
 * at 0x103370 returns 1 for one of the 2K-word pages that the range touches, 0 on success, or the result of ROM 0x1032b4 if the status word at 0xf02804 is non-zero
 * afterwards. The data goes out in chunks of up to 8 words that never cross a 128-word boundary: each is copied to 0xf02814 by ROM 0x100d20 with
 * (count << 8 | (bank != 0) << 16) at 0xf02808 and the index at 0xf0280c, then 1 is written to 0xf02800, the CPU sleeps (`sleep 0x19`) and the code
 * spins until the byte at 0xf02804 is zero. Interrupts are off for the whole operation, ROM 0x103c00(0) brackets it with (1) and NVM_BeforeOperation /
 * NVM_AfterOperation wrap the writes (the same sequence as the sleeping operation at 0x30ee78, including the byte at 0xf0041e set to 15 when bits 2 and 3 of the
 * byte at 0xf0383b are set). FLAG: ROM 0x103370, 0x103c00 and 0x1032b4 are named by address only because their roles are unknown.
 */
#include <stdint.h>

#define RB8(a)  (*(volatile uint8_t *)(uintptr_t)(a))
#define RW32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#ifndef EM_SLEEP
#define EM_SLEEP(n) __builtin_arc_sleep((int)(n))
#endif

extern uint32_t em9305_rom_page_103370(uint32_t bank, uint32_t page);
extern void em9305_rom_gate_103c00(uint32_t);
extern uint32_t em9305_rom_wait_done_1032b4(void);
extern void opencfw_em9305_rom_copy_words_100d20(void *dst, const void *src, uint32_t nwords);
extern uint32_t opencfw_em9305_stock_30ec9c(void *a, void *b);
extern void opencfw_em9305_stock_30eb48(void *a, void *b, uint32_t token);

uint32_t opencfw_em9305_stock_30f014(uint32_t bank, uint32_t index, const uint8_t *src, uint32_t nwords)
{
  uint32_t buf[0x50 / 4];
  if (nwords == 0u) return 3u;
  uint32_t end = index + nwords;
  uint32_t limit = (bank == 0u) ? (1u << 17) : (1u << 13);
  if (index > limit || end > limit) return 3u;

  uint32_t last = ((end + 0x7ffffu) >> 11) & 0xffu;
  uint32_t page = index >> 11;
  if (last >= page) {
    do {
      if (em9305_rom_page_103370(bank, page & 0xffu) == 1u) return 1u;
      page++;
    } while (last >= (page & 0xffu));
  }

  uint32_t irq;
  irq=(uint32_t)__builtin_arc_clri(); __builtin_arc_sync();
  em9305_rom_gate_103c00(0u);
  uint32_t token = opencfw_em9305_stock_30ec9c(&buf[2], &buf[0]);
  uint8_t saved = RB8(0xf0041eu);
  if ((RB8(0xf0383bu) & 0xcu) == 0xcu) RB8(0xf0041eu) = 15u;
  uint32_t bank_bit = (bank != 0u) << 16;
  uint32_t result = 0u;
  for (;;) {
    uint32_t room = (0u - 128u - (index & 0x7fu)) & 0xffu;
    if ((int32_t)room > 8) room = 8u;
    uint32_t n = nwords;
    if (room < nwords) n = room;
    RW32(0xf02808u) = (n << 8) + bank_bit;
    RW32(0xf0280cu) = index;
    opencfw_em9305_rom_copy_words_100d20((void *)(uintptr_t)0xf02814u, src, n & 0xffffu);
    RW32(0xf02800u) = 1u;
    EM_SLEEP(0x19u);
    while (RB8(0xf02804u) != 0u) {}
    (void)__builtin_arc_clri(); __builtin_arc_sync();
    uint32_t status = RW32(0xf02804u);
    nwords -= n;
    src += n * 4u;
    index += n;
    if (status != 0u) {
      opencfw_em9305_stock_30eb48(&buf[2], &buf[0], token);
      result = em9305_rom_wait_done_1032b4();
      em9305_rom_gate_103c00(1u);
      goto restore;
    }
    if (nwords == 0u) break;
  }
  opencfw_em9305_stock_30eb48(&buf[2], &buf[0], token);
  em9305_rom_gate_103c00(1u);
restore:
  if ((RB8(0xf0383bu) & 0xcu) == 0xcu) RB8(0xf0041eu) = saved;
  __builtin_arc_seti((int)irq);
  return result;
}

/* Stock 0x30f170: the handler that fills the unused interrupt vectors (stock_residual_data.c lists it for every vector without a handler of its own):
 * the 88-byte frame of em_irq_frame.h is saved and the system is reset through ROM 0x103f14, which does not return, so the restore half of the frame is
 * unreachable. FLAG: the stock code saves aux 1409 in the delay slot of the call, here it is saved before the call; the role of the vector is a guess from its use. */
#include "em_irq_frame.h"
extern void em9305_rom_system_reset_103f14(void);
EM_IRQ_HANDLER(opencfw_em9305_stock_30f170, em9305_rom_system_reset_103f14);
