/* SPDX-License-Identifier: MIT
 * Stock 0x305e68 IRQHandler_PmlSvld (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: the `enter_s [r13-r15,blink]` interrupt frame (em_irq_frame_e.h)
 * around this body, written from the lowered ARC asm and harness-checked against the lowered stock extent (a dead volatile load under flags bit 6 is unobservable there; 60 qemu-arc tests, MMIO randomised, aux lr/sr substituted, callback arguments compared; the frame itself is not covered). Reads the status word at 0xf009a4, acknowledges its bit 0 by
 * writing it back to 0xf009ac and, when set, runs the same sequence as timer_enable's update path: timer_irq_enable(0), then
 * (timer context at 0x80fde0, selected level byte at 0x8019a0) decrement the selected level if it is not negative, timer_threshold_flags and
 * timer_apply with the signed level, controller_timer_changed(<timer_apply result>), controller_mode_action(), timer_irq_enable(1).
 * FLAG: the load of the timer context when saved flag bit 6 is set is kept as a volatile read because the stock code executes it (its result is
 * overwritten by the next call's argument); the argument of controller_timer_changed is taken from r0 as left by timer_apply (guess).
 */
#include "em_irq_frame_e.h"

extern uint32_t opencfw_em9305_timer_irq_enable(uint32_t);
extern uint32_t opencfw_em9305_timer_threshold_flags(int32_t);
extern uint32_t opencfw_em9305_timer_apply(int32_t);
extern void opencfw_em9305_controller_timer_changed(uint32_t);
extern uint32_t opencfw_em9305_controller_mode_action(void);

__attribute__((used)) void opencfw_em9305_IRQHandler_PmlSvld_body(void)
{
  uint32_t status = EM_R32(0xf009a4u) & 1u;
  EM_R32(0xf009acu) = status;
  __builtin_arc_sync();
  if (status == 0u) return;
  (void)opencfw_em9305_timer_irq_enable(0u);
  uintptr_t context = EM_R32(0x80fde0u);
  uint32_t flags = *(volatile uint8_t *)(context + 14u);
  volatile int8_t *selected = (volatile int8_t *)(uintptr_t)0x8019a0u;
  if (*selected >= 0) *selected = (int8_t)(*selected - 1);
  (void)opencfw_em9305_timer_threshold_flags(*selected);
  if (flags & 64u) (void)EM_R32(0x80fde0u);
  uint32_t applied = opencfw_em9305_timer_apply(*selected);
  opencfw_em9305_controller_timer_changed(applied);
  (void)opencfw_em9305_controller_mode_action();
  (void)opencfw_em9305_timer_irq_enable(1u);
}

EM_IRQ_HANDLER_E(opencfw_em9305_IRQHandler_PmlSvld, opencfw_em9305_IRQHandler_PmlSvld_body, "r13-r15");
