/* SPDX-License-Identifier: MIT */
/* Software-only evidence boundary; this file performs no MMIO access. */

#include "runtime_bootloader_mspi_fifo_read_boundary.h"

static const open_cfw_mspi_read_boundary open_cfw_mspi_read_descriptor = {
    0x00423E8AU,
    0x00423F28U,
    0x0041D246U,
    0x0041D1C0U,
    0x00000040U,
    0x40060000U,
    0x00001000U,
    0x14U,
    0x1CU,
    0x3FU,
    4U,
    "AmbiqSuite 5.1.0 mspi_fifo_read",
    "AmbiqSuite 5.1.0 am_hal_delay_us_status_check",
    "5efc0228528a8adce5eae0d226fac85d2551eb3b",
    "BSD-3-Clause",
    "stock IAR compiler release/options and exact emitted-body identity unresolved",
    OPEN_CFW_BOOT_MSPI_FIFO_READ_EXACT_TOOLCHAIN_UNRESOLVED,
};

const open_cfw_mspi_read_boundary *
open_cfw_bootloader_mspi_fifo_read_boundary(void)
{
    return &open_cfw_mspi_read_descriptor;
}

enum open_cfw_mspi_read_admission_status
open_cfw_bootloader_mspi_fifo_read_admission_status(void)
{
    return OPEN_CFW_BOOT_MSPI_FIFO_READ_EXACT_TOOLCHAIN_UNRESOLVED;
}

static void open_cfw_mspi_read_store_word(
    open_cfw_mspi_read_u8 *destination,
    open_cfw_mspi_read_u32 word,
    open_cfw_mspi_read_u32 count)
{
    open_cfw_mspi_read_u32 index;
    for (index = 0U; index < count; ++index)
        destination[index] = (open_cfw_mspi_read_u8)(word >> (8U * index));
}

open_cfw_mspi_read_u32 open_cfw_bootloader_mspi_fifo_read_model(
    open_cfw_mspi_read_u32 module,
    open_cfw_mspi_read_u8 *data,
    open_cfw_mspi_read_u32 byte_count,
    open_cfw_mspi_read_u32 timeout,
    const open_cfw_mspi_read_model_ports *ports)
{
    open_cfw_mspi_read_u32 index;
    open_cfw_mspi_read_u32 words;
    open_cfw_mspi_read_u32 leftovers;
    open_cfw_mspi_read_u32 status;
    open_cfw_mspi_read_u32 base;

    if (module >= 4U)
        return 5U;

    words = byte_count / 4U;
    leftovers = byte_count - words * 4U;
    base = 0x40060000U + module * 0x1000U;
    for (index = 0U; index < words; ++index) {
        status = ports->status_check(
            ports->context, timeout, base + 0x1CU, 0x3FU, 0U, 0U);
        if (status != 0U)
            return status;
        open_cfw_mspi_read_store_word(
            data + index * 4U,
            ports->read_word(ports->context, base + 0x14U), 4U);
    }
    if (leftovers != 0U) {
        status = ports->status_check(
            ports->context, timeout, base + 0x1CU, 0x3FU, 0U, 0U);
        if (status != 0U)
            return status;
        open_cfw_mspi_read_store_word(
            data + index * 4U,
            ports->read_word(ports->context, base + 0x14U), leftovers);
    }
    return 0U;
}
