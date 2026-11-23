/* SPDX-License-Identifier: MIT
 * Stock 0x329464 lctrSlvBisTxData (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered
 * ARC asm. Field names are not recovered (offsets only); G=0x80542c holds the current {row, col, ?, col2}
 * bytes, the 0x805448 table has 0x90-byte rows of 0x18-byte entries. mpywhl = ARCv2 DSP 32x16 multiply (low 32 bits of the
 * product, settled wave 28); {lo,hi} = 64-bit (+0x24:+0x20) * byte +0x18; macdu accumulates {hi,lo} + b1a*G[3] into the 64-bit callback argument.
 */
#include <stdint.h>
#include "em9305_ram.h"
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define LCTR_SLV_BIG_CUR     ((uintptr_t)&em9305_ram_80542c)
#define BIS_TXENT_TAB        0x805448u
#define LCTR_SLV_BIG_TIME_CB 0x8052d0u
extern uint32_t opencfw_em9305_BbBleBisTxData(uint32_t ent, uint32_t kind, uint32_t a, uint32_t b);
extern uint32_t opencfw_em9305_dispatch_child_30e6b0(uint32_t x);

void opencfw_em9305_lctrSlvBisTxData(uint32_t big)
{
  uint32_t row = B8(LCTR_SLV_BIG_CUR), col = B8(LCTR_SLV_BIG_CUR + 1u), col2 = B8(LCTR_SLV_BIG_CUR + 3u);
  uint32_t ent = BIS_TXENT_TAB + (row * 0x90u) + (uint32_t)(uint16_t)(col2 + col) * 0x18u;
  uint32_t kind, strm, cb;

  kind = (W32(ent + 0x0cu) == 0u) ? 1u : (W32(ent + 0x14u) != 0u) + 2u;
  strm = W32(big + (row << 2) + 0x38u);
  if (B8(big + 0x1e4u) != 0u && (cb = W32(LCTR_SLV_BIG_TIME_CB)) != 0u) {
    uint32_t b = B8(big + 0x18u), a = W32(big + 0x20u);
    uint64_t prod = (uint64_t)a * b;
    uint32_t hi = (uint32_t)(W32(big + 0x24u) * b) + (uint32_t)(prod >> 32);
    uint64_t acc = (((uint64_t)hi << 32) | (uint32_t)prod) + col;
    acc += (uint64_t)B8(big + 0x1au) * col2;
    ((void (*)(uint32_t, uint32_t))(uintptr_t)cb)((uint32_t)acc, (uint32_t)(acc >> 32));
  }
  (void)opencfw_em9305_BbBleBisTxData(ent, kind, W32(big + 0x130u) + W32(LCTR_SLV_BIG_CUR + 0x10u), W32(LCTR_SLV_BIG_CUR + 0x14u));
  B8(strm + 177u) = (uint8_t)opencfw_em9305_dispatch_child_30e6b0(strm + 0x78u);
}
