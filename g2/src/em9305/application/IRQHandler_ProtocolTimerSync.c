/* SPDX-License-Identifier: MIT
 * Stock 0x3062ac IRQHandler_ProtocolTimerSync (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: the stock handler is the shared interrupt frame
 * (em_irq_frame.h) around this body, written from the lowered ARC asm and harness-checked against the lowered stock extent (60 qemu-arc tests, MMIO randomised, aux lr/sr substituted, callback arguments compared; the frame itself is not covered).
 * protocol timer sync interrupt: ack 0x200 at 0xf00820, emsys_noop_302d80(), then the callback at 0x801914 if set.
 */
#include "em_irq_frame.h"
extern void opencfw_em9305_emsys_noop_302d80(void);

__attribute__((used)) void opencfw_em9305_IRQHandler_ProtocolTimerSync_body(void)
{
  EM_R32(0xf00820u) = 512u;
  __builtin_arc_sync();
  opencfw_em9305_emsys_noop_302d80();
  EM_IRQ_CALL_SLOT(0x801914u);
}

EM_IRQ_HANDLER(opencfw_em9305_IRQHandler_ProtocolTimerSync, opencfw_em9305_IRQHandler_ProtocolTimerSync_body);
