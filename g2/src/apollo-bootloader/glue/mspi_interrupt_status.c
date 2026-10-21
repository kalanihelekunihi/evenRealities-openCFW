/* SPDX-License-Identifier: BSD-3-Clause
 * Pinned Ambiq HAL 5.1.0 am_hal_mspi_interrupt_status_get, checked against
 * locked Boot 0x4264ba. This reads MMIO; physical IRQ timing is untested.
 */
#include <stdint.h>
#include <stdbool.h>
#include "ambiq_mspi_compat.h"

uint32_t am_hal_mspi_interrupt_status_get(void *handle, uint32_t *status,
                                          bool enabled_only)
{
    am_hal_mspi_state_t *state = (am_hal_mspi_state_t *)handle;
    if (!AM_HAL_MSPI_CHK_HANDLE(handle))
        return AM_HAL_STATUS_INVALID_HANDLE;
    const uint32_t module = state->ui32Module;
    const uint32_t pending = MSPIn(module)->INTSTAT;
    *status = enabled_only ? pending & MSPIn(module)->INTEN : pending;
    return AM_HAL_STATUS_SUCCESS;
}
