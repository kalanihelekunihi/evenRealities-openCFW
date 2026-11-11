/* SPDX-License-Identifier: MIT
 * Stock 0x311ab4 RF_HandleInterrupt_Rx (g2-2.2.6.10 firmware_ble_em9305.bin; the name comes from the stock symbol table). Wave 28: radio completion handler,
 * body of IRQHandler_RadioRx; the sibling of RF_HandleInterrupt_Tx (0x311c14). Record at 0x8019c4: +0 pending, +4 callback, +8 fallback callback,
 * +0xc u16 base, +0xe u16 delta. Status 0xf00860, checked in this order (callback arguments are (code, delta)):
 *   bit 25 -> common_radio_restore first (its argument is unused);
 *   bit 22 -> ack bit 22 at 0xf00868, callback(3, 0); the record is NOT cleared;
 *   bit 16 -> ack, then exit unless bit 6 of 0xf04054; radio_control_refresh(0); code 8 if bit 4, 7 if bit 5, else measure and code 4 if byte 0xf0407d == 0 else 10;
 *             callback(code, delta);
 *   bit 21 -> ack, common_radio_restore, measure, callback(9, delta);
 *   none, but bit 25 -> ack bit 25, radio_control_refresh(0), callback(5, 0).
 * The callback is the pending one, else the fallback; pending and callback are cleared before the call (except for bit 22). measure: delta = base +
 * (field != 0x1fff ? ~field : 0), field = (aux 1689 >> 8) & 0x1fff after `sr 8,[1666]` (aux meanings not checked: FLAG; the Tx handler uses 1686 and `sr 4`).
 * The bit-25 path reads the base and aux 1689 and discards both (kept as volatile reads, as stock). Harness result: see C-RECONSTRUCTION-PROGRESS.md.
 */
#include <stdint.h>
extern uint32_t opencfw_em9305_common_radio_restore_312410(uint32_t);
extern uint32_t opencfw_em9305_radio_control_refresh_31252c(uint32_t);
typedef void (*cb_t)(uint32_t, uint32_t);
struct rec { uint32_t pending; cb_t cb; cb_t fallback; uint16_t base; uint16_t delta; };
#define REC (*(volatile struct rec *)(uintptr_t)0x8019c4u)
#define R32(a) (*(volatile uint32_t *)(uintptr_t)(a))
static inline __attribute__((always_inline)) void measure(void)
{
  uint16_t base = REC.base;
  __builtin_arc_sr(8u, 1666u);
  __builtin_arc_sync();
  uint32_t v = (__builtin_arc_lr(1689u) >> 8) & 0x1fffu;
  uint32_t d = base;
  d += (v != 0x1fffu) ? ~v : 0u;
  REC.delta = (uint16_t)d;
}
/* Takes the pending callback (else the fallback); clears pending and the callback first when CLEAR. */
static inline __attribute__((always_inline)) cb_t take(int clear)
{
  cb_t cb = REC.cb;
  if (clear) {
    REC.pending = 0u;
    REC.cb = 0;
  }
  if (cb == 0)
    cb = REC.fallback;
  return cb;
}
void opencfw_em9305_RF_HandleInterrupt_Rx(void)
{
  uint32_t status = R32(0xf00860u);
  uint32_t bit25 = status & 0x2000000u;
  if (bit25)
    (void)opencfw_em9305_common_radio_restore_312410(0u);
  if (status & 0x400000u) {
    R32(0xf00868u) = 0x400000u;
    __builtin_arc_sync();
    cb_t cb = take(0);
    if (cb)
      cb(3u, 0u);
    return;
  }
  if (status & 0x10000u) {
    R32(0xf00868u) = 0x10000u;
    __builtin_arc_sync();
    uint32_t ctl = R32(0xf04054u);
    if (!(ctl & 0x40u))
      return;
    (void)opencfw_em9305_radio_control_refresh_31252c(0u);
    uint32_t code;
    if (ctl & 0x10u) {
      code = 8u;
    } else if (ctl & 0x20u) {
      code = 7u;
    } else {
      measure();
      code = (*(volatile uint8_t *)(uintptr_t)0xf0407du == 0u) ? 4u : 10u;
    }
    uint32_t delta = REC.delta;
    cb_t cb = take(1);
    if (cb)
      cb(code, delta);
    return;
  }
  if (status & 0x200000u) {
    R32(0xf00868u) = 0x200000u;
    __builtin_arc_sync();
    (void)opencfw_em9305_common_radio_restore_312410(0u);
    measure();
    uint32_t delta = REC.delta;
    cb_t cb = take(1);
    if (cb)
      cb(9u, delta);
    return;
  }
  if (!bit25)
    return;
  R32(0xf00868u) = 0x2000000u;
  __builtin_arc_sync();
  (void)opencfw_em9305_radio_control_refresh_31252c(0u);
  (void)REC.base;
  __builtin_arc_sr(8u, 1666u);
  __builtin_arc_sync();
  (void)__builtin_arc_lr(1689u);
  cb_t cb = take(1);
  if (cb)
    cb(5u, 0u);
}
