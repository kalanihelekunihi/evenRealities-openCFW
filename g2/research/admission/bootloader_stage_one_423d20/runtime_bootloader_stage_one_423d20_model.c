/* SPDX-License-Identifier: MIT */
/* Host semantic model for the exact target assembly in the adjacent file. */

#include "runtime_bootloader_stage_one_423d20.h"

static open_cfw_stage_one_model_ports open_cfw_stage_one_ports;

void open_cfw_bootloader_stage_one_model_configure(
    const open_cfw_stage_one_model_ports *ports)
{
    open_cfw_stage_one_ports = *ports;
}

open_cfw_stage_one_u32 open_cfw_bootloader_stage_one_wait_index_model(
    open_cfw_stage_one_u32 index)
{
    volatile open_cfw_stage_one_u32 *address =
        (volatile open_cfw_stage_one_u32 *)(__UINTPTR_TYPE__)(
            0xE0000000U + index * 4U);
    return open_cfw_stage_one_ports.wait(1000U, address, 3U, 1U) == 0U;
}

open_cfw_stage_one_u32 open_cfw_bootloader_stage_one_wait_reg80_model(void)
{
    return open_cfw_stage_one_ports.wait(
        1000U, open_cfw_stage_one_ports.register_80, 0x00800000U, 0U) == 0U;
}

open_cfw_stage_one_u32 open_cfw_bootloader_stage_one_status_model(void)
{
    if (open_cfw_bootloader_stage_one_wait_index_model(0U) == 0U
        || open_cfw_bootloader_stage_one_wait_reg80_model() == 0U)
        return 4U;
    open_cfw_stage_one_ports.delay(500U);
    return 0U;
}

open_cfw_stage_one_u32 open_cfw_bootloader_stage_one_model(void)
{
    open_cfw_stage_one_u32 result = open_cfw_bootloader_stage_one_status_model();
    open_cfw_stage_one_u32 debug;
    *open_cfw_stage_one_ports.register_80 &= ~0x11U;
    result = open_cfw_stage_one_ports.wait(
        1000U, open_cfw_stage_one_ports.register_80, 0U, 0U);
    if (result != 0U)
        return result;
    debug = open_cfw_stage_one_ports.debug_disable();
    return debug == 3U ? 0U : debug;
}
