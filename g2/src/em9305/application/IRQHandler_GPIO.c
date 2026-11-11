/* SPDX-License-Identifier: MIT
 * Stock 0x305ca4 IRQHandler_GPIO (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: the `enter_s` interrupt frame (em_irq_frame_e.h) around this body,
 * written from the lowered ARC asm and harness-checked against the lowered stock extent (60 qemu-arc tests, MMIO randomised, aux lr/sr substituted, callback arguments compared; the frame itself is not covered). Finds the lowest set bit of the pending word at 0xf008cc (the stock loop never ends
 * when the word is 0), acknowledges that line by writing its bit (low 12 bits) to 0xf008d4, runs controller_irq_action with the same mask, then
 * calls the callback stored at 0x80190c, if any, with the bit index.
 */
#include "em_irq_frame_e.h"

extern void opencfw_em9305_controller_irq_action(uint32_t);

__attribute__((used)) void opencfw_em9305_IRQHandler_GPIO_body(void)
{
  uint32_t pending = EM_R32(0xf008ccu);
  uint32_t index = 0;
  while (!((pending >> (index & 31u)) & 1u)) index++;
  index &= 0xffu;
  uint32_t mask = (1u << (index & 31u)) & 0xfffu;
  EM_R32(0xf008d4u) = mask;
  __builtin_arc_sync();
  opencfw_em9305_controller_irq_action(mask);
  void (*cb)(uint32_t) = (void (*)(uint32_t))(uintptr_t)EM_R32(0x80190cu);
  if (cb) cb(index);
}

EM_IRQ_HANDLER_E(opencfw_em9305_IRQHandler_GPIO, opencfw_em9305_IRQHandler_GPIO_body, "r13");
