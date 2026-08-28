/* SPDX-License-Identifier: MIT */
/* Typed clean-room ABI for the G2 bootloader stage-one status subgraph. */

#ifndef OPEN_CFW_BOOTLOADER_STAGE_ONE_423D20_H
#define OPEN_CFW_BOOTLOADER_STAGE_ONE_423D20_H

typedef __UINT32_TYPE__ open_cfw_stage_one_u32;

open_cfw_stage_one_u32 open_cfw_bootloader_stage_one_423d20(void);
open_cfw_stage_one_u32 open_cfw_bootloader_stage_one_status_423d58(void);
open_cfw_stage_one_u32 open_cfw_bootloader_stage_one_wait_reg80_423d7a(void);
open_cfw_stage_one_u32 open_cfw_bootloader_stage_one_wait_index_423da0(
    open_cfw_stage_one_u32 index);
open_cfw_stage_one_u32 open_cfw_bootloader_stage_one_wait_zero_423dc4(void);

open_cfw_stage_one_u32 open_cfw_bootloader_delay_status_change_41d21c(
    open_cfw_stage_one_u32 timeout,
    volatile open_cfw_stage_one_u32 *address,
    open_cfw_stage_one_u32 mask,
    open_cfw_stage_one_u32 expected);
open_cfw_stage_one_u32 open_cfw_bootloader_debug_disable_422468(void);
void open_cfw_bootloader_retained_delay_41d1c0(open_cfw_stage_one_u32 duration);

typedef struct open_cfw_stage_one_model_ports {
    open_cfw_stage_one_u32 (*wait)(
        open_cfw_stage_one_u32, volatile open_cfw_stage_one_u32 *,
        open_cfw_stage_one_u32, open_cfw_stage_one_u32);
    open_cfw_stage_one_u32 (*debug_disable)(void);
    void (*delay)(open_cfw_stage_one_u32);
    volatile open_cfw_stage_one_u32 *register_80;
} open_cfw_stage_one_model_ports;

void open_cfw_bootloader_stage_one_model_configure(
    const open_cfw_stage_one_model_ports *ports);
open_cfw_stage_one_u32 open_cfw_bootloader_stage_one_wait_index_model(
    open_cfw_stage_one_u32 index);
open_cfw_stage_one_u32 open_cfw_bootloader_stage_one_wait_reg80_model(void);
open_cfw_stage_one_u32 open_cfw_bootloader_stage_one_status_model(void);
open_cfw_stage_one_u32 open_cfw_bootloader_stage_one_model(void);

#endif
