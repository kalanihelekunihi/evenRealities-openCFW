/* SPDX-License-Identifier: MIT
 * Stock 0x305b1c IRQHandler_ArcTimer0 (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: the stock handler is the shared interrupt frame
 * (em_irq_frame.h) around this body, written from the lowered ARC asm and harness-checked against the lowered stock extent (60 qemu-arc tests, MMIO randomised, aux lr/sr substituted, callback arguments compared; the frame itself is not covered).
 * ARC timer 0 interrupt: calls the callback stored at 0x801904 if set.
 */
#include "em_irq_frame.h"
#include "em9305_ram.h"

__attribute__((used)) void opencfw_em9305_IRQHandler_ArcTimer0_body(void)
{
  {
    em_irq_cb_t cb_ = (em_irq_cb_t)(uintptr_t)em9305_ram_801904.u32_801904;
    if (cb_) cb_();
  }
}

EM_IRQ_HANDLER(opencfw_em9305_IRQHandler_ArcTimer0, opencfw_em9305_IRQHandler_ArcTimer0_body);
