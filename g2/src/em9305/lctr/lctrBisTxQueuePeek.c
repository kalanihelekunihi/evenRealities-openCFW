/* SPDX-License-Identifier: MIT
 * Stock 0x317890 lctrBisTxQueuePeek (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm and verified
 * against it in the QEMU-ARC harness (.waves/w28). Field names are not recovered (offsets only).
 */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_wsf_event_at(uint32_t queue, uint32_t index, uint32_t out_u8);
extern uint32_t opencfw_em9305_radio_record_timing_30c40c(uint32_t, uint32_t);

uint32_t opencfw_em9305_lctrBisTxQueuePeek(uint32_t ctx, uint32_t pos, uint32_t out)
{
  uint8_t tmp;
  uint32_t q = ctx + 8u, cfg = W32(ctx + 4u), ev, i = pos, j = 0u, t, tm, step, base, r1, r2, p;
  int32_t evb;

  if (B8(cfg + 0x1au) != 0u) {
    base = pos - pos % B8(cfg + 0x18u);
    for (i = 0u;; i++) {
      ev = opencfw_em9305_wsf_event_at(q, (uint8_t)i, (uint32_t)(uintptr_t)&tmp);
      if (ev == 0u) return 0u;
      cfg = W32(ctx + 4u);
      evb = (int8_t)B8(ev + 12u);
      if ((int32_t)B8(cfg + 0x1au) * (int32_t)(int8_t)base < evb) return 0u;
      if ((uint32_t)(uint8_t)base * B8(cfg + 0x1au) == (uint8_t)evb) break;
      if (B8(ev + 13u) == 0u) {
        step = B8(cfg + 0x18u); B8(ev + 13u) = 1u; B8(ev + 12u) = (uint8_t)((uint32_t)evb - step);
      }
    }
    step = B8(cfg + 0x18u); B8(ev + 13u) = 1u; B8(ev + 12u) = (uint8_t)((uint32_t)evb - step);
  }
  t = (uint8_t)i;
  for (;;) {
    ev = opencfw_em9305_wsf_event_at(q, (uint8_t)j, (uint32_t)(uintptr_t)&tmp);
    if (ev == 0u) return 0u;
    if (H16(ev + 8u) == 0u) {
      uint32_t d = B8(ev + 0x14u);
      W32(out + 12u) = 0u; W32(out + 4u) = ev + 0x16u; H16(out) = (uint16_t)d;
      return 1u;
    }
    tm = opencfw_em9305_radio_record_timing_30c40c(H16(ev + 8u), B8(ev + 0xau));
    j++;
    if (t >= tm) { i -= tm; t = (uint8_t)i; continue; }
    r1 = (uint32_t)B8(ev + 0xau) * t;
    r2 = H16(ev + 8u);
    if (r1 >= r2) continue;
    {
      int32_t rem = (int32_t)(r2 - r1), cap = (int32_t)B8(ev + 0xau);
      uint32_t o13 = t * 13u;
      H16(out + 8u) = (uint16_t)(rem < cap ? rem : cap);
      p = ev + o13;
      W32(out + 4u) = p + 0x16u;
      r2 = B8(p + 0x14u); { uint32_t b15 = B8(p + 0x15u);
      uint32_t w = W32(ev + 4u);
      W32(out + 0x14u) = 0u;
      H16(out) = (uint16_t)r2;
      W32(out + 12u) = w + r1;
      if (b15 == 0u) return 2u;
      H16(out + 0x10u) = (uint16_t)b15;
      W32(out + 0x14u) = ev + o13 + 0x1du;
      return 3u; }
    }
  }
}
