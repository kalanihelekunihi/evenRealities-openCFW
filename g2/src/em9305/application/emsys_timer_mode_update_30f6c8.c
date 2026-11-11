/* SPDX-License-Identifier: MIT
 * Stock 0x30f6c8 emsys_timer_mode_update_30f6c8 (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm; the compiled
 * -Os instructions were compared with the lowered stock code (tiny function, no harness run). controller_timer_changed(arg) then returns controller_mode_action(). Name inferred from the two callees.
 */
#include <stdint.h>
extern void opencfw_em9305_controller_timer_changed(uint32_t);
extern uint32_t opencfw_em9305_controller_mode_action(void);

uint32_t opencfw_em9305_emsys_timer_mode_update_30f6c8(uint32_t value)
{
  opencfw_em9305_controller_timer_changed(value);
  return opencfw_em9305_controller_mode_action();
}
