/* SPDX-License-Identifier: MIT
 * Stock 0x3067b8 IRQHandler_SleepTimerOutCmp3 (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: the `enter_s` interrupt frame (em_irq_frame_e.h)
 * around this body, written from the lowered ARC asm and harness-checked against the lowered stock extent (60 qemu-arc tests, MMIO randomised, aux lr/sr substituted, callback arguments compared; the frame itself is not covered). Takes the index (aux 1034 minus 0x1f, low byte),
 * acknowledges bit `index` (low 4 bits) at 0xf00844, runs controller_irq_action with the mask shifted left by 16, then calls the callback stored at
 * 0x801920, if any, with the index. FLAG: aux register 1034 is unnamed here.
 */
#include "em_irq_frame_e.h"
#include "em9305_ram.h"

extern void opencfw_em9305_controller_irq_action(uint32_t);

__attribute__((used)) void opencfw_em9305_IRQHandler_SleepTimerOutCmp3_body(void)
{
  uint32_t index = (__builtin_arc_lr(1034) - 0x1fu) & 0xffu;
  uint32_t mask = (1u << (index & 31u)) & 0xfu;
  EM_R32(0xf00844u) = mask;
  __builtin_arc_sync();
  opencfw_em9305_controller_irq_action(mask << 16);
  void (*cb)(uint32_t) = (void (*)(uint32_t))(uintptr_t)em9305_ram_80190c.u32_801920;
  if (cb) cb(index);
}

EM_IRQ_HANDLER_E(opencfw_em9305_IRQHandler_SleepTimerOutCmp3, opencfw_em9305_IRQHandler_SleepTimerOutCmp3_body, "r13");
