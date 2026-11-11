/* SPDX-License-Identifier: MIT
 * Stock 0x30f6dc emsys_volt_restore_mode_update_30f6dc (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: converted from the lowered ARC asm; the compiled
 * -Os instructions were compared with the lowered stock code (tiny function, no harness run). PML_VoltMonitorReStoreConfig() then emsys_timer_mode_update_30f6c8(its return value). Name inferred from the callees.
 */
#include <stdint.h>
extern uint32_t opencfw_em9305_PML_VoltMonitorReStoreConfig(void);
extern uint32_t opencfw_em9305_emsys_timer_mode_update_30f6c8(uint32_t);

uint32_t opencfw_em9305_emsys_volt_restore_mode_update_30f6dc(void)
{
  return opencfw_em9305_emsys_timer_mode_update_30f6c8(opencfw_em9305_PML_VoltMonitorReStoreConfig());
}
