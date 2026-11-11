/* SPDX-License-Identifier: MIT
 * Stock 0x306050 IRQHandler_ProtocolTimerOutCmp0 (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: the stock handler is the shared interrupt frame
 * (em_irq_frame.h) around this body, written from the lowered ARC asm and harness-checked against the lowered stock extent (60 qemu-arc tests, MMIO randomised, aux lr/sr substituted, callback arguments compared; the frame itself is not covered).
 * protocol timer output-compare 0 interrupt: ack 1<<0 at 0xf00820, then 0x333404(0).
 */
#include "em_irq_frame.h"
extern void opencfw_em9305_stock_333404(uint32_t);

__attribute__((used)) void opencfw_em9305_IRQHandler_ProtocolTimerOutCmp0_body(void)
{
  EM_R32(0xf00820u) = 1u;
  __builtin_arc_sync();
  opencfw_em9305_stock_333404(0u);
}

EM_IRQ_HANDLER(opencfw_em9305_IRQHandler_ProtocolTimerOutCmp0, opencfw_em9305_IRQHandler_ProtocolTimerOutCmp0_body);
