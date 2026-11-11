/* SPDX-License-Identifier: MIT
 * Stock 0x3066e8 IRQHandler_SleepTimerFullVal (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: the stock handler is the shared interrupt frame
 * (em_irq_frame.h) around this body, written from the lowered ARC asm and harness-checked against the lowered stock extent (60 qemu-arc tests, MMIO randomised, aux lr/sr substituted, callback arguments compared; the frame itself is not covered).
 * sleep timer full-value interrupt: ack 16 at 0xf00844, then the callback at 0x80191c if set.
 */
#include "em_irq_frame.h"

__attribute__((used)) void opencfw_em9305_IRQHandler_SleepTimerFullVal_body(void)
{
  EM_R32(0xf00844u) = 16u;
  __builtin_arc_sync();
  EM_IRQ_CALL_SLOT(0x80191cu);
}

EM_IRQ_HANDLER(opencfw_em9305_IRQHandler_SleepTimerFullVal, opencfw_em9305_IRQHandler_SleepTimerFullVal_body);
