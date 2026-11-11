/* SPDX-License-Identifier: MIT
 * Stock 0x30660c IRQHandler_SWI7 (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: the stock handler is the shared interrupt frame
 * (em_irq_frame.h) around this body, written from the lowered ARC asm and harness-checked against the lowered stock extent (60 qemu-arc tests, MMIO randomised, aux lr/sr substituted, callback arguments compared; the frame itself is not covered).
 * software interrupt 2..7 handler (one handler for six vectors): acks bit (irq cause - 0x38) in 0xf00a84, then calls the callback at 0x801918 if set, passing the index (found by the harness).
 */
#include "em_irq_frame.h"

__attribute__((used)) void opencfw_em9305_IRQHandler_SWI7_body(void)
{
  uint32_t cause = __builtin_arc_lr(1034u);
  uint32_t index = cause - 0x38u;
  EM_R32(0xf00a84u) = 1u << (index & 31u);
  __builtin_arc_sync();
  void (*cb)(uint32_t) = (void (*)(uint32_t))(uintptr_t)EM_R32(0x801918u);
  if (cb) cb(index);
}

EM_IRQ_HANDLER(opencfw_em9305_IRQHandler_SWI7, opencfw_em9305_IRQHandler_SWI7_body);
