/* SPDX-License-Identifier: MIT
 * Stock 0x305be0 IRQHandler_ArcTimer1 (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: the stock handler is the shared interrupt frame
 * (em_irq_frame.h) around this body, written from the lowered ARC asm and harness-checked against the lowered stock extent (60 qemu-arc tests, MMIO randomised, aux lr/sr substituted, callback arguments compared; the frame itself is not covered).
 * ARC timer 1 interrupt: calls the callback stored at 0x801908 if set.
 */
#include "em_irq_frame.h"
#include "em9305_ram.h"

__attribute__((used)) void opencfw_em9305_IRQHandler_ArcTimer1_body(void)
{
  {
    em_irq_cb_t cb_ = (em_irq_cb_t)(uintptr_t)em9305_ram_801908.u32_801908;
    if (cb_) cb_();
  }
}

EM_IRQ_HANDLER(opencfw_em9305_IRQHandler_ArcTimer1, opencfw_em9305_IRQHandler_ArcTimer1_body);
