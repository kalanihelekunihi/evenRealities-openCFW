// SPDX-License-Identifier: BSD-3-Clause
// Copyright (c) 2025, Ambiq Micro, Inc.
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
//
// 1. Redistributions of source code must retain the above copyright notice,
// this list of conditions and the following disclaimer.
//
// 2. Redistributions in binary form must reproduce the above copyright
// notice, this list of conditions and the following disclaimer in the
// documentation and/or other materials provided with the distribution.
//
// 3. Neither the name of the copyright holder nor the names of its
// contributors may be used to endorse or promote products derived from this
// software without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
// SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
// CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
// ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
// POSSIBILITY OF SUCH DAMAGE.
//

/* Exact selected function text from pinned public Ambiq 5.1.0 replay.
 * Full SDK state is intentionally not instantiated by this subset. */
#include "ambiq_mspi_compat.h"

uint32_t
am_hal_mspi_interrupt_enable(void *pHandle,
                             uint32_t ui32IntMask)
{
    am_hal_mspi_state_t           *pMSPIState = (am_hal_mspi_state_t *)pHandle;
    uint32_t                      ui32Module;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    //
    // Check the handle.
    //
    if (!AM_HAL_MSPI_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    ui32Module = pMSPIState->ui32Module;

    //
    // Set the interrupt enables according to the mask.
    //
    MSPIn(ui32Module)->INTEN |= ui32IntMask;

    //
    // Return the status.
    //
    return AM_HAL_STATUS_SUCCESS;
}

uint32_t
am_hal_mspi_interrupt_disable(void *pHandle,
                              uint32_t ui32IntMask)
{
    am_hal_mspi_state_t           *pMSPIState = (am_hal_mspi_state_t *)pHandle;
    uint32_t                      ui32Module;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    //
    // Check the handle.
    //
    if (!AM_HAL_MSPI_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    ui32Module = pMSPIState->ui32Module;
    //
    // Clear the interrupt enables according to the mask.
    //
    MSPIn(ui32Module)->INTEN &= ~ui32IntMask;

    //
    // Return the status.
    //
    return AM_HAL_STATUS_SUCCESS;
}

uint32_t
am_hal_mspi_interrupt_status_get(void *pHandle,
                                 uint32_t  *pui32Status,
                                 bool bEnabledOnly)
{
    am_hal_mspi_state_t           *pMSPIState = (am_hal_mspi_state_t *)pHandle;
    uint32_t                      ui32Module;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    //
    // Check the handle.
    //
    if (!AM_HAL_MSPI_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    ui32Module = pMSPIState->ui32Module;
    //
    // if requested, only return the interrupts that are enabled.
    //
    if ( bEnabledOnly )
    {
        uint32_t ui32RetVal = MSPIn(ui32Module)->INTSTAT;
        *pui32Status = ui32RetVal & MSPIn(ui32Module)->INTEN;
    }
    else
    {
        *pui32Status = MSPIn(ui32Module)->INTSTAT;
    }

    return AM_HAL_STATUS_SUCCESS;
}

uint32_t
am_hal_mspi_interrupt_clear(void *pHandle,
                            uint32_t ui32IntMask)
{
    am_hal_mspi_state_t           *pMSPIState = (am_hal_mspi_state_t *)pHandle;
    uint32_t                      ui32Module;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    //
    // Check the handle.
    //
    if ( !AM_HAL_MSPI_CHK_HANDLE(pHandle) )
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    ui32Module = pMSPIState->ui32Module;
    //
    // clear the requested interrupts.
    //
    MSPIn(ui32Module)->INTCLR = ui32IntMask;
    *(volatile uint32_t*)(&MSPIn(ui32Module)->INTSTAT);
    //
    // Return the status.
    //
    return AM_HAL_STATUS_SUCCESS;
}
