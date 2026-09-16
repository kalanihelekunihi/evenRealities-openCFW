/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern uint32_t open_cfw_gx8002_backup_status(void);
extern void open_cfw_gx8002_analog_config_update_enable(void);
/* Backup board initialization at package 0x3be14. The status read is retained
 * even though this configuration performs no conditional XIP initialization. */
void open_cfw_gx8002_backup_board_initialize(void)
{
    (void)open_cfw_gx8002_backup_status();
    open_cfw_gx8002_analog_config_update_enable();
}
