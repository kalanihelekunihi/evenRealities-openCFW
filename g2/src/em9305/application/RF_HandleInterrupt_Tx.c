/* SPDX-License-Identifier: MIT
 * Stock 0x311c14 RF_HandleInterrupt_Tx (g2-2.2.6.10 firmware_ble_em9305.bin; FLAG: name inferred from its sibling RF_HandleInterrupt_Rx at 0x311ab4, which
 * IRQHandler_RadioRx calls the same way IRQHandler_RadioTx calls this; 0x311c14 has no stock symbol). Wave 28: radio channel-2 completion handler,
 * body of IRQHandler_RadioTx. Record at 0x8019d4 is the one `radio_schedule_311ef0` fills: +0 pending, +4 callback, +8 fallback callback, +0xc u16
 * base, +0xe u16 delta. Status 0xf00860: bit 0 -> ack 1 at 0xf00868, radio_control_refresh(1), measure, exit unless bit 7 of 0xf04054, then
 * callback(0, delta); bit 4 -> ack 16, common_radio_restore(status), measure, callback(2, delta). measure: delta = base - byte(0xf0407c) +
 * (field != 0x1fff ? ~field : 0), field = (aux 1686 >> 8) & 0x1fff after `sr 4,[1666]` (aux meanings not checked: FLAG).
 * Harness (.waves/w28/run_txirq.sh, --mmio, orig = lowered 0x311c14..0x311ce6): EQUIVALENT on 60 tests with the aux lr/sr replaced by a RAM word
 * and a no-op on both sides (QEMU has no such aux registers), 8 of 8 mutants killed. Size differs: 240 B vs 220 B lowered (stock 210 B; no xbfu).
 */
#include <stdint.h>
extern uint32_t opencfw_em9305_common_radio_restore_312410(uint32_t);
extern uint32_t opencfw_em9305_radio_control_refresh_31252c(uint32_t);
typedef void (*cb_t)(uint32_t, uint32_t);
struct ch2 { uint32_t pending; cb_t cb; cb_t fallback; uint16_t base; uint16_t delta; };
struct rfreg { uint32_t ctl; uint8_t pad[0x24]; uint8_t last; };
#define CH2 (*(volatile struct ch2 *)(uintptr_t)0x8019d4u)
#define RF (*(volatile struct rfreg *)(uintptr_t)0xf04054u)
#define R32(a) (*(volatile uint32_t *)(uintptr_t)(a))
static inline __attribute__((always_inline)) void measure(void)
{
  uint16_t base = CH2.base;
  __builtin_arc_sr(4u, 1666u);
  __builtin_arc_sync();
  uint32_t v = (__builtin_arc_lr(1686u) >> 8) & 0x1fffu;
  uint32_t d = base - RF.last;
  d += (v != 0x1fffu) ? ~v : 0u;
  CH2.delta = (uint16_t)d;
}
static inline __attribute__((always_inline)) void fire(uint32_t arg)
{
  uint32_t delta = CH2.delta;
  cb_t cb = CH2.cb;
  CH2.pending = 0u;
  CH2.cb = 0;
  if (cb == 0) {
    cb = CH2.fallback;
    if (cb == 0)
      return;
  }
  cb(arg, delta);
}
void opencfw_em9305_RF_HandleInterrupt_Tx(void)
{
  uint32_t status = R32(0xf00860u);
  if (status & 1u) {
    R32(0xf00868u) = 1u;
    __builtin_arc_sync();
    (void)opencfw_em9305_radio_control_refresh_31252c(1u);
    measure();
    if (!(RF.ctl & 0x80u))
      return;
    fire(0u);
  } else if (status & 0x10u) {
    R32(0xf00868u) = 16u;
    __builtin_arc_sync();
    (void)opencfw_em9305_common_radio_restore_312410(status);
    measure();
    fire(2u);
  }
}
