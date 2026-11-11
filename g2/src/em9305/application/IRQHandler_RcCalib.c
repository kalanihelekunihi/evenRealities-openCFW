/* SPDX-License-Identifier: MIT
 * Stock 0x3064fc IRQHandler_RcCalib (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: the stock handler is the shared interrupt frame
 * (em_irq_frame.h) around this body, written from the lowered ARC asm and harness-checked against the lowered stock extent (60 qemu-arc tests, MMIO randomised, aux lr/sr substituted, callback arguments compared; the frame itself is not covered).
 * RC calibration interrupt: status 0xf0095c bit 0; ack 1 at +8; reads the pair 0xf01c14/0xf01c18; if bit 2 of 0xf00404 is set it calls the callback at 0x805c30 (no null check in stock) with the pair, otherwise it latches the pair at 0x8019b8/0x8019bc and calls the callbacks at 0x805cf0 (with the pair) and 0x805c2c (no args), each if set.
 */
#include "em_irq_frame.h"
typedef void (*pair_cb_t)(uint32_t, uint32_t);

__attribute__((used)) void opencfw_em9305_IRQHandler_RcCalib_body(void)
{
  if (!(EM_R32(0xf0095cu) & 1u))
    return;
  EM_R32(0xf00964u) = 1u;
  __builtin_arc_sync();
  uint32_t flags = EM_R32(0xf00404u);
  uint32_t first = EM_R32(0xf01c14u);
  uint32_t second;
  if (flags & 4u) {
    second = EM_R32(0xf01c18u);
    ((pair_cb_t)(uintptr_t)EM_R32(0x805c30u))(first, second);
  } else {
    EM_R32(0x8019b8u) = first;
    second = EM_R32(0xf01c18u);
    EM_R32(0x8019bcu) = second;
    pair_cb_t cb = (pair_cb_t)(uintptr_t)EM_R32(0x805cf0u);
    if (cb)
      cb(first, second);
    EM_IRQ_CALL_SLOT(0x805c2cu);
  }
}

EM_IRQ_HANDLER(opencfw_em9305_IRQHandler_RcCalib, opencfw_em9305_IRQHandler_RcCalib_body);
