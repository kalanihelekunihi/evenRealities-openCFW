/* SPDX-License-Identifier: MIT
 * Stock 0x305d84 IRQHandler_PmlClock (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: the stock handler is the shared interrupt frame
 * (em_irq_frame.h) around this body, written from the lowered ARC asm and harness-checked against the lowered stock extent (60 qemu-arc tests, MMIO randomised, aux lr/sr substituted, callback arguments compared; the frame itself is not covered).
 * PML clock interrupt: status 0xf009a4; bits 1|2 (mask 6): ack 6 at +8 and controller_cold_irq(); else bit 3 (mask 8): ack 8 and 0x30fa08(1).
 */
#include "em_irq_frame.h"
extern void opencfw_em9305_controller_cold_irq(void);
extern void opencfw_em9305_stock_30fa08(uint32_t);

__attribute__((used)) void opencfw_em9305_IRQHandler_PmlClock_body(void)
{
  uint32_t status = EM_R32(0xf009a4u);
  if (status & 0x6u) {
    EM_R32(0xf009acu) = 6u;
    __builtin_arc_sync();
    opencfw_em9305_controller_cold_irq();
  } else if (status & 0x8u) {
    EM_R32(0xf009acu) = 8u;
    __builtin_arc_sync();
    opencfw_em9305_stock_30fa08(1u);
  }
}

EM_IRQ_HANDLER(opencfw_em9305_IRQHandler_PmlClock, opencfw_em9305_IRQHandler_PmlClock_body);
