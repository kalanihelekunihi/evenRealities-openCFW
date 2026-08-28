/* SPDX-License-Identifier: MIT */
/* Typed clean-room ABI for the G2 bootloader 0x423DD0 frontier. */

#ifndef OPEN_CFW_BOOTLOADER_STAGE_TWO_423DD0_H
#define OPEN_CFW_BOOTLOADER_STAGE_TWO_423DD0_H

typedef __UINT8_TYPE__ open_cfw_stage_two_u8;
typedef __UINT32_TYPE__ open_cfw_stage_two_u32;

open_cfw_stage_two_u32 open_cfw_bootloader_stage_two_status_423dd0(void);
open_cfw_stage_two_u32 open_cfw_bootloader_stage_two_mode_flags_423e14(
    void *context,
    open_cfw_stage_two_u32 flags);

/* Authenticated external provider ABIs retained by the exact target body. */
open_cfw_stage_two_u32 open_cfw_bootloader_critical_save_41b8ec(void);
open_cfw_stage_two_u32 open_cfw_bootloader_debug_disable_422468(void);

typedef struct open_cfw_stage_two_model_ports {
    open_cfw_stage_two_u32 (*critical_save)(void);
    void (*critical_restore)(open_cfw_stage_two_u32);
    open_cfw_stage_two_u32 (*debug_disable)(void);
    volatile open_cfw_stage_two_u8 *guard;
    volatile open_cfw_stage_two_u8 *counter;
} open_cfw_stage_two_model_ports;

void open_cfw_bootloader_stage_two_model_configure(
    const open_cfw_stage_two_model_ports *ports);
open_cfw_stage_two_u32 open_cfw_bootloader_stage_two_status_model(void);
open_cfw_stage_two_u32 open_cfw_bootloader_stage_two_mode_flags_model(
    open_cfw_stage_two_u32 *mode,
    open_cfw_stage_two_u32 flags);

#endif
