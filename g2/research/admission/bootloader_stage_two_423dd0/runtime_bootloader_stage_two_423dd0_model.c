/* SPDX-License-Identifier: MIT */
/* Host semantic model for the exact target assembly in the adjacent file. */

#include "runtime_bootloader_stage_two_423dd0.h"

static open_cfw_stage_two_model_ports open_cfw_stage_two_ports;

void open_cfw_bootloader_stage_two_model_configure(
    const open_cfw_stage_two_model_ports *ports)
{
    open_cfw_stage_two_ports = *ports;
}

open_cfw_stage_two_u32 open_cfw_bootloader_stage_two_status_model(void)
{
    open_cfw_stage_two_u32 mask = open_cfw_stage_two_ports.critical_save();
    open_cfw_stage_two_u32 result;

    if (*open_cfw_stage_two_ports.counter != 0U)
        --*open_cfw_stage_two_ports.counter;
    if (*open_cfw_stage_two_ports.counter != 0U) {
        result = 3U;
    } else {
        *open_cfw_stage_two_ports.guard = 0U;
        result = open_cfw_stage_two_ports.debug_disable();
        if (result == 3U)
            result = 0U;
    }
    open_cfw_stage_two_ports.critical_restore(mask);
    return result;
}

open_cfw_stage_two_u32 open_cfw_bootloader_stage_two_mode_flags_model(
    open_cfw_stage_two_u32 *mode,
    open_cfw_stage_two_u32 flags)
{
    if (*mode == 1U) {
        flags |= 0x40A0U;
        *mode = 2U;
    } else if (*mode == 2U) {
        flags = 0x4000U;
    } else {
        flags |= 0x4080U;
    }
    return flags;
}
