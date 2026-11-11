/* SPDX-License-Identifier: MIT
 * Stock 0x30fa9c PML_VoltMonitorReStoreConfig (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm; the compiled
 * -Os instructions were compared with the lowered stock code (tiny function, no harness run). timer_enable(1), then returns timer_irq_enable(1).
 */
#include <stdint.h>
extern uint32_t opencfw_em9305_timer_enable(uint32_t);
extern uint32_t opencfw_em9305_timer_irq_enable(uint32_t);

uint32_t opencfw_em9305_PML_VoltMonitorReStoreConfig(void)
{
  (void)opencfw_em9305_timer_enable(1u);
  return opencfw_em9305_timer_irq_enable(1u);
}
