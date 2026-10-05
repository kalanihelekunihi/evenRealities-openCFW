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

#include "gpio_config_compat.h"

static const uint32_t
g_ui32CfgDSExt[7] =
{
    0x00000000,     //  31:0
    0x00003FE0,     //  63:32,  set  45:37
    0x000003FF,     //  95:64,  set  73:64
    0x1FFBFE00,     // 127:96,  set 124:105
    0x0007C000,     // 159:128, set 146:142
    0x00000000,     // 191:160
    0x00000000      // 223:192
};

static const uint32_t
g_ui32DSpintbl[7] =
{
    0x8FC007E6,
    0xE3F3FFFF,
    0x81FFFFFF,
    0xFFFFFFFF,
    0xF00FC07F,
    0x00000001,
    0x00000189
};

uint32_t
am_hal_gpio_pinconfig_get(uint32_t ui32GpioNum, am_hal_gpio_pincfg_t* psGpioCfg)
{
    volatile uint32_t *pui32Config = &GPIO->PINCFG0;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    if ( ui32GpioNum >= AM_HAL_PIN_TOTAL_GPIOS )
    {
        return AM_HAL_STATUS_OUT_OF_RANGE;
    }

    if ( psGpioCfg == (am_hal_gpio_pincfg_t*)0x0 )
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }
#endif /// AM_HAL_DISABLE_API_VALIDATION

    psGpioCfg->GP.cfg = pui32Config[ui32GpioNum];

    return AM_HAL_STATUS_SUCCESS;

}

uint32_t
am_hal_gpio_pinconfig(uint32_t ui32GpioNum, const am_hal_gpio_pincfg_t sGpioCfg)
{
    volatile uint32_t *pui32Config = &GPIO->PINCFG0;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    if ( ui32GpioNum >= AM_HAL_PIN_TOTAL_GPIOS )
    {
        return AM_HAL_STATUS_OUT_OF_RANGE;
    }

    uint32_t udx = ui32GpioNum / 32;
    uint32_t umsk = 1 << (ui32GpioNum % 32);
    if ( (g_ui32CfgDSExt[udx] & umsk) == 0 )
    {
        //
        // This is a "normal" pad. For normal pads, the slew rate is assumed
        //  to have been included as bit2 of the eDriveStrength field, so we
        //  need to ignore it for this check.
        // Make sure the given pin supports this drive strength.
        //
        if ( (sGpioCfg.GP.cfg_b.eDriveStrength & 0x3) > AM_HAL_GPIO_PIN_DRIVESTRENGTH_0P5X )
        {
            //
            // Make sure the given pin supports this drive strength
            //
            if ( (g_ui32DSpintbl[udx] & umsk) == 0 )
            {
                return AM_HAL_STATUS_INVALID_OPERATION;
            }
        }
    }
    else
    {
        //
        // For high-speed pads, there is only 50 kohm pull-up/pull-down options.
        //
        if ((sGpioCfg.GP.cfg_b.ePullup != AM_HAL_GPIO_PIN_PULLUP_NONE) && \
            (sGpioCfg.GP.cfg_b.ePullup != AM_HAL_GPIO_PIN_PULLUP_50K)  && \
            (sGpioCfg.GP.cfg_b.ePullup != AM_HAL_GPIO_PIN_PULLDOWN_50K))
        {
            return AM_HAL_STATUS_INVALID_OPERATION;
        }
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    AM_CRITICAL_BEGIN

    //
    // Set the key to enable GPIO configuration.
    //
    GPIO->PADKEY = GPIO_PADKEY_PADKEY_Key;

    //
    // Write the configuration directly to the register.
    //
    pui32Config[ui32GpioNum] = sGpioCfg.GP.cfg;

    //
    // Lock the GPIO register again.
    //
    GPIO->PADKEY = 0;

    AM_CRITICAL_END


    return AM_HAL_STATUS_SUCCESS;

}
