//*****************************************************************************
//
//! @file am_hal_debug.c
//!
//! @brief Functions for general debug operations.
//!
//! @addtogroup debug_ap510 General Debug Functionality
//! @ingroup apollo510_hal
//! @{
//!
//! Purpose: This module provides general debug operation functions for Apollo5
//!          devices. It supports debug enable/disable, power management, trace
//!          configuration, and TPIU clock setup for development and debugging.
//!
//! @section hal_debug_features Key Features
//!
//! 1. @b Debug @b Enable/Disable: Control debug operation state.
//! 2. @b Power @b Management: Manage debug power domain.
//! 3. @b Trace @b Configuration: Enable/disable trace and TPIU clock.
//! 4. @b Counter @b Management: Track debug and trace enable counts.
//! 5. @b MCUCTRL @b Integration: Integrate with MCU control registers.
//!
//! @section hal_debug_functionality Functionality
//!
//! - Enable and disable debug operation
//! - Manage debug power domain and counters
//! - Configure trace and TPIU clock
//! - Integrate with MCU control registers
//! - Track debug and trace enable/disable counts
//!
//! @section hal_debug_usage Usage
//!
//! 1. Enable debug using am_hal_debug_enable()
//! 2. Disable debug using am_hal_debug_disable()
//! 3. Manage debug power and trace configuration
//! 4. Track debug and trace enable/disable counts
//! 5. Integrate with MCU control as needed
//!
//! @section hal_debug_configuration Configuration
//!
//! - @b Debug @b Power: Configure debug power management
//! - @b Trace @b Settings: Set up trace and TPIU clock
//! - @b Counter @b Management: Track enable/disable counts
//! - @b MCUCTRL: Configure MCU control register integration
//
//*****************************************************************************

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

#include "compat.h"

uint32_t
am_hal_debug_disable(void)
{
    uint32_t ui32Ret = AM_HAL_STATUS_SUCCESS;

    AM_CRITICAL_BEGIN

    if ( g_ui8DebugEnableCount != 0 )
    {
        --g_ui8DebugEnableCount;
    }

    if ( g_ui8DebugEnableCount > 0 )
    {
        //
        // Debug to remain enabled for now.
        //
        ui32Ret = AM_HAL_STATUS_IN_USE;
    }
    else
    {
        //
        // Disable the CM55 TPIU clock source in MCU control.
        //
        MCUCTRL->DBGCTRL_b.DBGTPIUTRACEENABLE = MCUCTRL_DBGCTRL_DBGTPIUTRACEENABLE_DIS;
        MCUCTRL->DBGCTRL_b.DBGTPIUCLKSEL      = MCUCTRL_DBGCTRL_DBGTPIUCLKSEL_OFF;
    }

    //
    // Check if TRCENA needs to be disabled.
    //
    am_hal_debug_trace_disable();

    //
    // Check if the debug power domain needs to be powered down.
    //
    ui32Ret = am_hal_debug_power(false);

    AM_CRITICAL_END

    return ui32Ret;

}

uint32_t
am_hal_debug_power(bool bPowerup)
{
    uint32_t ui32Ret = AM_HAL_STATUS_SUCCESS;

    AM_CRITICAL_BEGIN

    if ( bPowerup )
    {
        //
        // Bump the count
        //
        g_ui8PowerCount++;

        //
        // Make sure the debug domain is powered up.
        //
        if ( g_ui8PwrStDbgOnEntry == 0x0 )
        {
            //
            //  0x1 = Debug power was initially off.
            //  0x3 = Debug power was initially on.
            //  All other values are invalid and would generally indicate that
            //  this function was never called.
            //
            g_ui8PwrStDbgOnEntry = 0x1;

            bool bEnabled;
            am_hal_pwrctrl_periph_enabled(AM_HAL_PWRCTRL_PERIPH_DEBUG, &bEnabled);
            if ( bEnabled )
            {
                //
                // Already powered up, set the flag.
                //
                g_ui8PwrStDbgOnEntry |= 0x2;
            }
            else
            {
                //
                // Power up the debug domain.
                //
                am_hal_pwrctrl_periph_enable(AM_HAL_PWRCTRL_PERIPH_DEBUG);
            }

        }
    }
    else
    {
        if ( g_ui8PowerCount != 0 )
        {
            --g_ui8PowerCount;
        }

        if ( g_ui8PowerCount > 0 )
        {
            //
            // Debug to remain enabled for now.
            //
            ui32Ret = AM_HAL_STATUS_IN_USE;
        }
        else
        {
            if ( g_ui8PwrStDbgOnEntry == 0x1 )
            {
                am_hal_pwrctrl_periph_disable(AM_HAL_PWRCTRL_PERIPH_DEBUG);
            }
            g_ui8PwrStDbgOnEntry = 0x0;
        }
    }

    AM_CRITICAL_END

    return ui32Ret;

}

uint32_t
am_hal_debug_trace_disable(void)
{
    uint32_t ui32Ret = AM_HAL_STATUS_SUCCESS;

    AM_CRITICAL_BEGIN

    //
    // Reset the TRCENA bit in the DEMCR register.
    // Note that all operations from DWT, PMU, and ITM should be discontinued
    // and flushed before calling this function.
    //
    if ( g_ui8TRCENAcount != 0 )
    {
        --g_ui8TRCENAcount;
    }

    if ( g_ui8TRCENAcount > 0 )
    {
        ui32Ret = AM_HAL_STATUS_IN_USE;
    }
    else
    {
        DCB->DEMCR &= ~DCB_DEMCR_TRCENA_Msk;

        //
        // Wait for the changes to take effect with a 10us timeout.
        //
        ui32Ret = am_hal_delay_us_status_change(10,
                                                (uint32_t)&DCB->DEMCR,
                                                DCB_DEMCR_TRCENA_Msk,
                                                0 );
    }

    AM_CRITICAL_END

    return ui32Ret;

}
