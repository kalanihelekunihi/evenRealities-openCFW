/* SPDX-License-Identifier: MIT
 * Stock 0x3293e0 lctrSlvBisTxControl (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the
 * lowered ARC asm. Field names are not recovered (offsets only). mpywhl is the ARCv2 DSP 32x16 multiply (low 32 bits of the
 * product; settled wave 28, see docs/em9305-arc-harness.md), so {lo,hi} is the 64-bit value (+0x24:+0x20) * byte +0x18; the 64-bit value handed to the 0x8052d0 callback is {lo, hi} as in lctrSlvBigBeginOp.
 */
#include <stdint.h>
#include "em9305_ram.h"
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define LCTR_SLV_BIG_RX_CB  0x8051e0u
#define LCTR_SLV_BIG_BUF    0x802858u
#define LCTR_SLV_BIG_TXCTL_HDR ((uintptr_t)&em9305_ram_80542c.u32_805444)
#define LCTR_SLV_BIG_TIME_CB 0x8052d0u
extern uint32_t opencfw_em9305_BbBleBisTxData(uint32_t hdr, uint32_t a, uint32_t b, uint32_t c);

void opencfw_em9305_lctrSlvBisTxControl(uint32_t big)
{
  struct { uint16_t len; uint16_t pad; uint32_t p; } hdr;
  uint32_t p, cb, mode;

  if (B8(big + 0x1e4u) != 0u && W32(LCTR_SLV_BIG_RX_CB) != 0u) p = LCTR_SLV_BIG_BUF;
  else p = W32(LCTR_SLV_BIG_TXCTL_HDR);
  hdr.p = p;
  hdr.len = (uint16_t)(B8(p + 1u) + 2u);
  mode = B8(big + 0x112u);
  B8(p) = (uint8_t)((B8(p) & ~0x1cu) | ((mode << 2) & 0x1cu));
  B8(p) = (uint8_t)(B8(p) & ~0x20u);
  if (B8(big + 0x1e4u) != 0u && (cb = W32(LCTR_SLV_BIG_TIME_CB)) != 0u) {
    uint32_t b = B8(big + 0x18u), a = W32(big + 0x20u);
    uint64_t prod = (uint64_t)a * b;
    uint32_t hi = (uint32_t)(W32(big + 0x24u) * b) + (uint32_t)(prod >> 32);
    ((void (*)(uint32_t, uint32_t))(uintptr_t)cb)((uint32_t)prod, hi);
  }
  (void)opencfw_em9305_BbBleBisTxData((uint32_t)(uintptr_t)&hdr, 1u, 0u, 0u);
}
