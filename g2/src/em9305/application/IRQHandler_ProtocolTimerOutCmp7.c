/* SPDX-License-Identifier: MIT
 * Stock 0x305f74 IRQHandler_ProtocolTimerOutCmp7 (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: the stock handler is the shared interrupt frame
 * (em_irq_frame.h) around this body, written from the lowered ARC asm and harness-checked against the lowered stock extent (60 qemu-arc tests, MMIO randomised, aux lr/sr substituted, callback arguments compared; the frame itself is not covered).
 * protocol timer output-compare 4..7 interrupt (one handler for four vectors): acks bit (irq cause - 0x15) in 0xf00820, then calls the callback at 0x801910 if set, passing the index (cause - 0x15, low byte; stock leaves it in r0 at the call; harness-found, see step 19).
 */
#include "em_irq_frame.h"

__attribute__((used)) void opencfw_em9305_IRQHandler_ProtocolTimerOutCmp7_body(void)
{
  uint32_t cause = __builtin_arc_lr(1034u);
  uint32_t index = (uint8_t)(cause - 0x15u);
  EM_R32(0xf00820u) = (uint8_t)(1u << (index & 31u));
  __builtin_arc_sync();
  void (*cb)(uint32_t) = (void (*)(uint32_t))(uintptr_t)EM_R32(0x801910u);
  if (cb) cb(index);
}

EM_IRQ_HANDLER(opencfw_em9305_IRQHandler_ProtocolTimerOutCmp7, opencfw_em9305_IRQHandler_ProtocolTimerOutCmp7_body);
