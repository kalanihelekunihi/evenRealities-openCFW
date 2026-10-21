/* SPDX-License-Identifier: BSD-3-Clause
 * Copyright (c) 2025, Ambiq Micro, Inc. All rights reserved.
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 * this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution.
 *
 * 3. Neither the name of the copyright holder nor the names of its
 * contributors may be used to endorse or promote products derived from this
 * software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 * Derived from the pinned Ambiq HAL 5.1.0 interrupt-clear leaf.
 * Bootloader original entry 0x426506 was compared in 37 cases with 48
 * distinct original bytes executed (pre-consolidation:g2/components/bootloader/mspi/verify.py).
 */
#include "ambiq_mspi_compat.h"

uint32_t am_hal_mspi_interrupt_clear(void *handle, uint32_t mask)
{
    am_hal_mspi_state_t *state = (am_hal_mspi_state_t *)handle;
    if (!AM_HAL_MSPI_CHK_HANDLE(handle)) {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
    const uint32_t module = state->ui32Module;
    MSPIn(module)->INTCLR = mask;
    *(volatile uint32_t *)(&MSPIn(module)->INTSTAT);
    return AM_HAL_STATUS_SUCCESS;
}
