/* SPDX-License-Identifier: MIT */
/* Software-only evidence boundary; this file performs no MMIO access. */

#include "runtime_bootloader_mspi_fifo_write_boundary.h"

static const open_cfw_mspi_fifo_boundary open_cfw_mspi_fifo_descriptor = {
    0x00423E40U,
    0x00423E8AU,
    0x0041D246U,
    0x0041D1C0U,
    0x00000040U,
    0x40060000U,
    0x00001000U,
    0x10U,
    0x18U,
    0x3FU,
    0x10U,
    4U,
    "AmbiqSuite 5.1.0 mspi_fifo_write",
    "AmbiqSuite 5.1.0 am_hal_delay_us_status_check",
    "5efc0228528a8adce5eae0d226fac85d2551eb3b",
    "BSD-3-Clause",
    "stock IAR compiler release/options and exact emitted-body identity unresolved",
    OPEN_CFW_BOOT_MSPI_FIFO_WRITE_EXACT_TOOLCHAIN_UNRESOLVED,
};

const open_cfw_mspi_fifo_boundary *
open_cfw_bootloader_mspi_fifo_write_boundary(void)
{
    return &open_cfw_mspi_fifo_descriptor;
}

enum open_cfw_mspi_fifo_admission_status
open_cfw_bootloader_mspi_fifo_write_admission_status(void)
{
    return OPEN_CFW_BOOT_MSPI_FIFO_WRITE_EXACT_TOOLCHAIN_UNRESOLVED;
}

open_cfw_mspi_fifo_u32 open_cfw_bootloader_mspi_fifo_write_model(
    open_cfw_mspi_fifo_u32 module,
    const open_cfw_mspi_fifo_u32 *data,
    open_cfw_mspi_fifo_u32 byte_count,
    open_cfw_mspi_fifo_u32 timeout,
    const open_cfw_mspi_fifo_model_ports *ports)
{
    open_cfw_mspi_fifo_u32 index;
    open_cfw_mspi_fifo_u32 status = 0U;
    open_cfw_mspi_fifo_u32 base;

    if (module >= 4U)
        return 5U;

    base = 0x40060000U + module * 0x1000U;
    for (index = 0U; 4U * index < byte_count; ++index) {
        ports->write_word(ports->context, base + 0x10U, data[index]);
        status = ports->status_check(
            ports->context, timeout, base + 0x18U, 0x3FU, 0x10U, 0U);
    }
    return status;
}
