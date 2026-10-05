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

/* Unchanged selected upstream bodies; compatibility view uses proven stock offsets.
 * CQ and delay providers must be supplied by integration; simulator providers are
 * explicitly synthetic seams, not actual queue or hardware implementations. */
#include "ambiq_mspi_compat.h"

uint32_t
am_hal_mspi_disable(void *pHandle)
{
    am_hal_mspi_state_t           *pMSPIState = (am_hal_mspi_state_t *)pHandle;
    uint32_t                       ui32Status;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    //
    // Check the handle.
    //
    if (!AM_HAL_MSPI_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    if (!pMSPIState->prefix.s.bEnable)
    {
        return AM_HAL_STATUS_SUCCESS;
    }
    // We should not allow disable if there are pending transactions
    if (pMSPIState->ui32NumHPEntries || pMSPIState->ui32NumCQEntries)
    {
        return AM_HAL_STATUS_IN_USE;
    }

    if (pMSPIState->pTCB)
    {
        //
        // Disable the Command Queue.
        //
        ui32Status = mspi_cq_disable(pHandle);
        if (AM_HAL_STATUS_SUCCESS != ui32Status)
        {
          return ui32Status;
        }

        //
        // Reset the Command Queue.
        //
        mspi_cq_term(pHandle);
    }

    pMSPIState->prefix.s.bEnable = false;

    if (MSPIn(pMSPIState->ui32Module)->DEV0XIP_b.XIPEN0)
    {
        //
        // Need to make sure all pending XIP MM transactions are flushed
        //
        am_hal_delay_us(pMSPIState->ui32XIPOffMinDelay);
    }
    //
    // Return the status.
    //
    return AM_HAL_STATUS_SUCCESS;
}

uint32_t
am_hal_mspi_deinitialize(void *pHandle)
{
    am_hal_mspi_state_t           *pMSPIState = (am_hal_mspi_state_t *)pHandle;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    //
    // Check the handle.
    //
    if (!AM_HAL_MSPI_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    if (pMSPIState->prefix.s.bEnable)
    {
        am_hal_mspi_disable(pHandle);
    }

    //
    // Reset the handle.
    //
    pMSPIState->prefix.s.bInit = false;
    pMSPIState->ui32Module = 0;

    //
    // Return the status.
    //
    return AM_HAL_STATUS_SUCCESS;
}
