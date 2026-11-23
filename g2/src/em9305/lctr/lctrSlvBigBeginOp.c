/* SPDX-License-Identifier: MIT
 * Stock 0x3288b0 lctrSlvBigBeginOp (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the
 * lowered ARC asm. Field names are not recovered (offsets only). The {lo, hi} pair built at sp+4/sp+8
 * is the 64-bit product (+0x24:+0x20) * byte +0x18: mpydu (lo, hi) on +0x20, with hi += mpywhl(+0x24, byte +0x18)
 * (DSP 32x16 multiply, LOW 32 bits of the product; settled wave 28 from this very 64-bit-multiply use plus the stride/625-us uses).
 */
#include <stdint.h>
#include "em9305_ram.h"
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define LCTR_SLV_BIG_G ((uintptr_t)&em9305_ram_80542c)  /* 28-byte scratch cleared on entry */
#define LCTR_SLV_BIG_RX_CB 0x8051e0u      /* function pointer: 4-arg PDU handler */
#define LCTR_SLV_BIG_BUF 0x802858u        /* 2 + n byte PDU copy buffer */
extern uint32_t opencfw_em9305_memset(uint32_t, uint32_t, uint32_t);
extern uint32_t opencfw_em9305_memcpy(uint32_t, uint32_t, uint32_t);
extern uint32_t opencfw_em9305_lctrBigTxCtrlQueuePeek(uint32_t big, uint32_t out_u8);
extern uint32_t opencfw_em9305_ll_stream_header_3175d0(uint32_t dst, uint32_t src);
extern uint32_t opencfw_em9305_lctrSlvBisSetupTxData(uint32_t big, uint32_t a, uint32_t b);
extern uint32_t opencfw_em9305_lctrSlvBisTxData(uint32_t big);
extern uint32_t opencfw_em9305_wsf_event_at(uint32_t queue, uint32_t index, uint32_t out_u8);
extern uint32_t opencfw_em9305_child_3230e0(uint32_t big, uint32_t a);

void opencfw_em9305_lctrSlvBigBeginOp(uint32_t ctx)
{
  uint32_t big = W32(ctx + 0x24u);
  uint32_t g = LCTR_SLV_BIG_G;
  union { uint32_t w; uint8_t b[4]; } hu;
  uint32_t pair[2];
  uint8_t peek_u8, ev_u8;
  uint32_t t, src, i, j, k, cnt, n;

  (void)opencfw_em9305_memset(g, 0u, 0x1cu);
  if (B8(big + 0x1fu) == 1u) {
    if (B8(big + 0x34u) >= 2u) t = W32(big + 0x3cu) + 0xb0u;
    else if (B8(big + 0x19u) < 2u) t = big + 0x198u;
    else t = W32(big + 0x38u) + 0xb0u;
    src = big + 0x0cu;
  } else {
    if (B8(big + 0x19u) >= 2u) t = W32(big + 0x38u) + 0xb0u;
    else if (B8(big + 0x34u) < 2u) t = big + 0x198u;
    else t = W32(big + 0x3cu) + 0xb0u;
    src = big + 0x30u;
  }
  W32(g + 0x14u) = t;
  t = W32(src);
  W32(g + 0x10u) = t;
  t = opencfw_em9305_lctrBigTxCtrlQueuePeek(big, (uint32_t)(uintptr_t)&peek_u8);
  cnt = B8(big + 0x112u);
  W32(g + 0x18u) = t;
  if (peek_u8 != 0u) { cnt = cnt + 1u; B8(big + 0x112u) = (uint8_t)cnt; }
  hu.b[0] = 1u; hu.b[1] = (uint8_t)cnt; hu.b[2] = (uint8_t)(t != 0u); hu.b[3] = 0u;
  (void)opencfw_em9305_ll_stream_header_3175d0(g + 6u, (uint32_t)(uintptr_t)&hu);
  (void)opencfw_em9305_lctrSlvBisSetupTxData(big, 0u, 0u);
  (void)opencfw_em9305_lctrSlvBisTxData(big);

  for (i = 0u; i < B8(big + 0x34u); i++) {
    n = B8(big + 0x18u);
    for (j = 0u; j < n; j++) {
      if ((i | j) != 0u) {
        (void)opencfw_em9305_lctrSlvBisSetupTxData(big, (uint8_t)i, (uint8_t)j);
        n = B8(big + 0x18u);
      }
    }
    n = (uint16_t)(n * B8(big + 0x1bu));
    if (n < B8(big + 0x19u)) {
      uint32_t rem = B8(big + 0x19u) - n;
      for (k = 0u; k < rem; k++)
        (void)opencfw_em9305_lctrSlvBisSetupTxData(big, (uint8_t)i, (uint8_t)(B8(big + 0x18u) + k));
    }
  }

  if (B8(big + 0x1au) != 0u) {
    uint32_t idx = 0u;
    for (i = 0u; i < B8(big + 0x34u); i++) {
      for (;;) {
        uint32_t p = opencfw_em9305_wsf_event_at(W32(big + 0x38u + (i << 2)) + 8u, (uint8_t)idx, (uint32_t)(uintptr_t)&ev_u8);
        idx++;
        if (p == 0u) break;
        B8(p + 13u) = 0u;
      }
    }
  }

  if (B8(big + 0xc0u) == 0u) {
    B8(big + 0xc0u) = 1u;
    (void)opencfw_em9305_child_3230e0(big, 0u);
  }
  if (W32(g + 0x18u) != 0u) {
    uint32_t item = W32(g + 0x18u);
    uint32_t a = W32(big + 0x20u), b = B8(big + 0x18u);
    uint64_t prod = (uint64_t)a * b;
    uint32_t cbf;
    W32(big + 0x1ccu) = (uint32_t)(uintptr_t)pair;
    pair[0] = (uint32_t)prod;
    /* {lo,hi} = the 64-bit value (+0x24:+0x20) * byte +0x18: mpydu gives lo and hi of the low word's product, mpywhl (low 32 bits of a 32x16 multiply) adds the high word's product */
    pair[1] = (uint32_t)(W32(big + 0x24u) * b) + (uint32_t)(prod >> 32);
    cbf = W32(LCTR_SLV_BIG_RX_CB);
    if (B8(big + 0x1e4u) != 0u && cbf != 0u) {
      uint32_t len = B8(item + 1u);
      (void)opencfw_em9305_memcpy(LCTR_SLV_BIG_BUF, item, len + 2u);
      ((void (*)(uint32_t, uint32_t, uint32_t, uint32_t))(uintptr_t)cbf)(big + 0x1acu, LCTR_SLV_BIG_BUF, LCTR_SLV_BIG_BUF + 2u, LCTR_SLV_BIG_BUF + 2u + len);
    }
    W32(big + 0x1ccu) = 0u;
  }
}
