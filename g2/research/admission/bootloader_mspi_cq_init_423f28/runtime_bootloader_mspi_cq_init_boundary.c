/* SPDX-License-Identifier: MIT */
#include "runtime_bootloader_mspi_cq_init_boundary.h"

#include <stddef.h>

enum
{
    OPEN_CFW_BOOT_MSPI_CQ_INIT_START = 0x00423F28U,
    OPEN_CFW_BOOT_MSPI_CQ_INIT_END = 0x00423F54U,
    OPEN_CFW_BOOT_CMDQ_INIT_START = 0x00427794U,
    OPEN_CFW_BOOT_CMDQ_INIT_END = 0x00427878U,
    OPEN_CFW_BOOT_MSPI_STATE_BASE = 0x2001CAA0U,
    OPEN_CFW_BOOT_MSPI_STATE_STRIDE = 0x000008D0U,
    OPEN_CFW_BOOT_MSPI_CMDQ_HANDLE_OFFSET = 0x00000828U,
    OPEN_CFW_BOOT_CMDQ_INTERFACE_MSPI0 = 8U,
    OPEN_CFW_BOOT_CMDQ_INTERFACE_COUNT = 12U,
    OPEN_CFW_BOOT_CMDQ_STATE_BASE = 0x200262F0U,
    OPEN_CFW_BOOT_CMDQ_REGISTER_TABLE = 0x00430880U,
    OPEN_CFW_BOOT_CMDQ_PRIORITY_HIGH = 1U
};

static const open_cfw_bootloader_mspi_cq_init_boundary_t boundary =
{
    OPEN_CFW_BOOT_MSPI_CQ_INIT_START,
    OPEN_CFW_BOOT_MSPI_CQ_INIT_END,
    OPEN_CFW_BOOT_CMDQ_INIT_START,
    OPEN_CFW_BOOT_CMDQ_INIT_END,
    OPEN_CFW_BOOT_MSPI_STATE_BASE,
    OPEN_CFW_BOOT_MSPI_STATE_STRIDE,
    OPEN_CFW_BOOT_MSPI_CMDQ_HANDLE_OFFSET,
    OPEN_CFW_BOOT_CMDQ_INTERFACE_MSPI0,
    OPEN_CFW_BOOT_CMDQ_INTERFACE_COUNT,
    OPEN_CFW_BOOT_CMDQ_STATE_BASE,
    OPEN_CFW_BOOT_CMDQ_REGISTER_TABLE,
    "AmbiqSuite 5.1.0 mspi_cq_init",
    "AmbiqSuite 5.1.0 am_hal_cmdq_init",
    "5efc0228528a8adce5eae0d226fac85d2551eb3b",
    "BSD-3-Clause",
    "stock IAR compiler release, short-enum ABI options, and literal-pool placement are unavailable",
    OPEN_CFW_BOOT_MSPI_CQ_INIT_EXACT_TOOLCHAIN_UNRESOLVED
};

const open_cfw_bootloader_mspi_cq_init_boundary_t *
open_cfw_bootloader_mspi_cq_init_boundary(void)
{
    return &boundary;
}

open_cfw_bootloader_mspi_cq_init_admission_status_t
open_cfw_bootloader_mspi_cq_init_admission_status(void)
{
    return boundary.status;
}

uint32_t
open_cfw_bootloader_mspi_cq_init_model(
    uint32_t module,
    uint32_t length,
    const uint32_t *transfer_control_buffer,
    const open_cfw_bootloader_mspi_cq_init_model_ports_t *ports)
{
    open_cfw_bootloader_cmdq_config_model_t config;
    uint32_t handle_slot;
    uint8_t hardware_interface;

    if ((ports == NULL) || (ports->cmdq_init == NULL))
    {
        return UINT32_MAX;
    }

    config.cmdq_size = length / 2U;
    config.cmdq_buffer = transfer_control_buffer;
    config.priority = OPEN_CFW_BOOT_CMDQ_PRIORITY_HIGH;
    hardware_interface = (uint8_t)(module + OPEN_CFW_BOOT_CMDQ_INTERFACE_MSPI0);
    handle_slot = OPEN_CFW_BOOT_MSPI_STATE_BASE
        + module * OPEN_CFW_BOOT_MSPI_STATE_STRIDE
        + OPEN_CFW_BOOT_MSPI_CMDQ_HANDLE_OFFSET;

    return ports->cmdq_init(
        ports->context, hardware_interface, &config, handle_slot);
}
