/* SPDX-License-Identifier: MIT
 * Stock 0x329230 lctrSlvBisSetupTxData (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the
 * lowered ARC asm. Field names are not recovered (offsets only); the 0x805448 table has 0x90-byte rows of
 * 0x18-byte entries, the per-stream counters live at em9305_ram_80542c.u8_805434 / u8_805438 (+index), fields of the 28-byte 0x80542c scratch.
 */
#include <stdint.h>
#include "em9305_ram.h"
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define BIS_TXENT_TAB 0x805448u
#define BIS_CNT_A ((uintptr_t)&em9305_ram_80542c.u8_805434[0])
#define BIS_CNT_B ((uintptr_t)&em9305_ram_80542c.u8_805438[0])
extern uint32_t opencfw_em9305_lctrBisFlushStaleSdus(uint32_t queue, uint32_t a, uint32_t b);
extern uint32_t opencfw_em9305_lctrBisTxQueuePeek(uint32_t queue, uint32_t b, uint32_t entry);
extern uint32_t opencfw_em9305_wsf_event_at(uint32_t queue, uint32_t index, uint32_t out_u8);

void opencfw_em9305_lctrSlvBisSetupTxData(uint32_t big, uint32_t a, uint32_t b)
{
  uint32_t slot = big + (a << 2);
  uint32_t ent_off = (uint32_t)(uint16_t)b * 0x18u;
  uint32_t ent, r, hdr, cnt;
  uint8_t ev;

  (void)opencfw_em9305_lctrBisFlushStaleSdus(W32(slot + 0x38u), a, b);
  ent = (uint32_t)(uint16_t)a * 0x90u + ent_off + BIS_TXENT_TAB;
  r = opencfw_em9305_lctrBisTxQueuePeek(W32(slot + 0x38u), b, ent);
  if (r == 0u) {
    *(volatile uint16_t *)(uintptr_t)ent = 2u;
    W32(ent + 0x0cu) = 0u;
    W32(ent + 0x04u) = BIS_CNT_B - 6u;
    return;
  }
  if (b < B8(big + 0x18u)) {
    int bump = 1;
    if (B8(big + 0x1au) != 0u) {
      uint32_t n = opencfw_em9305_wsf_event_at(W32(slot + 0x38u) + 8u, (uint8_t)(b + 1u), (uint32_t)(uintptr_t)&ev);
      if (n == 0u || (int8_t)B8(n + 12u) >= 0) bump = 0;
    }
    if (bump) B8(BIS_CNT_B + a) = (uint8_t)(B8(BIS_CNT_B + a) + 1u);
    B8(BIS_CNT_A + a) = (uint8_t)(B8(BIS_CNT_A + a) + 1u);
  }
  ent = (uint32_t)(uint16_t)a * 0x90u + ent_off + BIS_TXENT_TAB;
  cnt = B8(big + 0x112u);
  hdr = W32(ent + 4u);
  B8(hdr) = (uint8_t)((B8(hdr) & ~0x1cu) | ((cnt << 2) & 0x1cu));
  hdr = W32(ent + 4u);
  if (W32(BIS_CNT_B + 0x0cu) != 0u) B8(hdr) = (uint8_t)(B8(hdr) | 0x20u);
  else B8(hdr) = (uint8_t)(B8(hdr) & ~0x20u);
}
