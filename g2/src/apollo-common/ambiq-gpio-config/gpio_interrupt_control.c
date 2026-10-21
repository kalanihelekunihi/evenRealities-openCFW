//*****************************************************************************
//
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
// This is part of revision release_sdk5p1p0-366b80e084 of the AmbiqSuite Development Package.
//
//*****************************************************************************

#include "gpio_control_compat.h"

static uint32_t
gpionum_intreg_index_get(uint32_t ui32Gpionum,
                         uint32_t *pui32RegIdx,
                         uint32_t *pui32Msk)
{

    *pui32RegIdx = ui32Gpionum / 32;
    *pui32Msk = 1 << (ui32Gpionum & 0x1F);
    return AM_HAL_STATUS_SUCCESS;
} // gpionum_intreg_index_get()

uint32_t
am_hal_gpio_interrupt_control(am_hal_gpio_int_channel_e eChannel,
                              am_hal_gpio_int_ctrl_e eControl,
                              void *pGpioIntMaskOrNumber)
{
    uint32_t ui32Gpionum, ui32RegAddr, ui32Idx, ui32Msk;
    uint32_t ui32FuncRet = AM_HAL_STATUS_SUCCESS;
    am_hal_gpio_mask_t *pGpioIntMask = (am_hal_gpio_mask_t*)pGpioIntMaskOrNumber;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    //
    // In all cases, the pointer must be non-NULL.
    //
    if ( pGpioIntMaskOrNumber == NULL )
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }

    if ( eControl > AM_HAL_GPIO_INT_CTRL_LAST )
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    if ( eControl <= AM_HAL_GPIO_INT_CTRL_INDV_ENABLE )
    {
        ui32Gpionum = *(uint32_t *)pGpioIntMaskOrNumber;
#ifndef AM_HAL_DISABLE_API_VALIDATION
        if ( ui32Gpionum >= AM_HAL_GPIO_MAX_PADS )
        {
            return AM_HAL_STATUS_OUT_OF_RANGE;
        }
#endif // AM_HAL_DISABLE_API_VALIDATION

        //
        // Convert the GPIO number into an index and bitmask.
        // Then use that to obtain the needed register address.
        // These will be used later.
        //
        if ( gpionum_intreg_index_get(ui32Gpionum, &ui32Idx, &ui32Msk) )
        {
            return AM_HAL_STATUS_INVALID_ARG;
        }

        ui32RegAddr = (uint32_t)&GPIO->MCUN0INT0EN + (ui32Idx * GPIO_INTX_DELTA);
        if ( eChannel == AM_HAL_GPIO_INT_CHANNEL_1 )
        {
            ui32RegAddr += GPIO_NXINT_DELTA;
        }
    }

    DIAG_SUPPRESS_VOLATILE_ORDER()
    AM_CRITICAL_BEGIN

    switch ( eControl )
    {
        case AM_HAL_GPIO_INT_CTRL_INDV_DISABLE:
            AM_REGVAL(ui32RegAddr) &= ~ui32Msk;         // Write MCUNxINTxEN
            if ( eChannel == AM_HAL_GPIO_INT_CHANNEL_BOTH )
            {
                ui32RegAddr += GPIO_NXINT_DELTA;        // Get MCUN1INTxEN addr
                AM_REGVAL(ui32RegAddr) &= ~ui32Msk;     // Write MCUN1INTxEN
            }
            break;

        case AM_HAL_GPIO_INT_CTRL_INDV_ENABLE:
            AM_REGVAL(ui32RegAddr) |= ui32Msk;          // Write MCUNnINTxEN
            if ( eChannel == AM_HAL_GPIO_INT_CHANNEL_BOTH )
            {
                ui32RegAddr += GPIO_NXINT_DELTA;        // Get MCUN1INTxEN addr
                AM_REGVAL(ui32RegAddr) |= ui32Msk;      // Write MCUN1INTxEN
            }
            break;

        case AM_HAL_GPIO_INT_CTRL_MASK_DISABLE:
            if ( eChannel != AM_HAL_GPIO_INT_CHANNEL_1)
            {
                GPIO->MCUN0INT0EN &= ~pGpioIntMask->U.Msk[0];
                GPIO->MCUN0INT1EN &= ~pGpioIntMask->U.Msk[1];
                GPIO->MCUN0INT2EN &= ~pGpioIntMask->U.Msk[2];
                GPIO->MCUN0INT3EN &= ~pGpioIntMask->U.Msk[3];
                GPIO->MCUN0INT4EN &= ~pGpioIntMask->U.Msk[4];
                GPIO->MCUN0INT5EN &= ~pGpioIntMask->U.Msk[5];
                GPIO->MCUN0INT6EN &= ~pGpioIntMask->U.Msk[6];
            }
            if ( eChannel != AM_HAL_GPIO_INT_CHANNEL_0)
            {
                GPIO->MCUN1INT0EN &= ~pGpioIntMask->U.Msk[0];
                GPIO->MCUN1INT1EN &= ~pGpioIntMask->U.Msk[1];
                GPIO->MCUN1INT2EN &= ~pGpioIntMask->U.Msk[2];
                GPIO->MCUN1INT3EN &= ~pGpioIntMask->U.Msk[3];
                GPIO->MCUN1INT4EN &= ~pGpioIntMask->U.Msk[4];
                GPIO->MCUN1INT5EN &= ~pGpioIntMask->U.Msk[5];
                GPIO->MCUN1INT6EN &= ~pGpioIntMask->U.Msk[6];
            }
            break;

        case AM_HAL_GPIO_INT_CTRL_MASK_ENABLE:
            if ( eChannel != AM_HAL_GPIO_INT_CHANNEL_1)
            {
                GPIO->MCUN0INT0EN |= pGpioIntMask->U.Msk[0];
                GPIO->MCUN0INT1EN |= pGpioIntMask->U.Msk[1];
                GPIO->MCUN0INT2EN |= pGpioIntMask->U.Msk[2];
                GPIO->MCUN0INT3EN |= pGpioIntMask->U.Msk[3];
                GPIO->MCUN0INT4EN |= pGpioIntMask->U.Msk[4];
                GPIO->MCUN0INT5EN |= pGpioIntMask->U.Msk[5];
                GPIO->MCUN0INT6EN |= pGpioIntMask->U.Msk[6];
            }
            if ( eChannel != AM_HAL_GPIO_INT_CHANNEL_0)
            {
                GPIO->MCUN1INT0EN |= pGpioIntMask->U.Msk[0];
                GPIO->MCUN1INT1EN |= pGpioIntMask->U.Msk[1];
                GPIO->MCUN1INT2EN |= pGpioIntMask->U.Msk[2];
                GPIO->MCUN1INT3EN |= pGpioIntMask->U.Msk[3];
                GPIO->MCUN1INT4EN |= pGpioIntMask->U.Msk[4];
                GPIO->MCUN1INT5EN |= pGpioIntMask->U.Msk[5];
                GPIO->MCUN1INT6EN |= pGpioIntMask->U.Msk[6];
            }
            break;

        default:
            break;
    }

    AM_CRITICAL_END
    DIAG_DEFAULT_VOLATILE_ORDER()

    //
    // Return the status.
    //
    return ui32FuncRet;

} // am_hal_gpio_interrupt_control()

/* Model arbitrary raw ARM entry bits explicitly; stock uses UXTB for both enums. */
uint32_t opencfw_gpio_interrupt_control_raw(uint32_t channel, uint32_t control, void *input)
{
    return am_hal_gpio_interrupt_control((am_hal_gpio_int_channel_e)(uint8_t)channel,
                                        (am_hal_gpio_int_ctrl_e)(uint8_t)control,input);
}
