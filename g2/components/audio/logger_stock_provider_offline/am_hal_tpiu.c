//*****************************************************************************
//
//! @file am_hal_tpiu.c
//!
//! @brief Support functions for the Arm TPIU module
//!
//! @addtogroup tpiu4_ap510 TPIU - Trace Port Interface Unit
//! @ingroup apollo510_hal
//! @{
//!
//! Purpose: This module provides support functions for configuring and managing
//!          the Arm TPIU (Trace Port Interface Unit) module on Apollo5 devices.
//!          It enables debug trace functionality, SWO (Serial Wire Output) support,
//!          and trace data formatting for development and debugging applications.
//!
//! @section hal_tpiu_features Key Features
//!
//! 1. @b Debug @b Trace: Support for Arm debug trace functionality.
//! 2. @b SWO @b Output: Serial Wire Output for debug data transmission.
//! 3. @b Trace @b Formatting: Configurable trace data formatting.
//! 4. @b Clock @b Configuration: Flexible clock source selection.
//! 5. @b Pin @b Protocol: Support for various pin protocols and modes.
//!
//! @section hal_tpiu_functionality Functionality
//!
//! - Configure TPIU module and trace parameters
//! - Enable/disable debug trace functionality
//! - Set up SWO output and data formatting
//! - Configure clock sources and pin protocols
//! - Handle trace data flow and formatting
//!
//! @section hal_tpiu_usage Usage
//!
//! 1. Configure TPIU using am_hal_tpiu_config()
//! 2. Enable TPIU with am_hal_tpiu_enable()
//! 3. Set up trace parameters and formatting
//! 4. Configure SWO output as needed
//! 5. Disable TPIU when no longer needed
//!
//! @section hal_tpiu_configuration Configuration
//!
//! - @b Clock @b Sources: Select TPIU clock sources
//! - @b Trace @b Formatting: Configure trace data format
//! - @b Pin @b Protocols: Set up pin protocols and modes
//! - @b SWO @b Settings: Configure Serial Wire Output parameters
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
am_hal_tpiu_disable(void)
{
    uint32_t ui32Status;

    AM_CRITICAL_BEGIN

    if ( g_ui8TpiuEnCnt != 0 )
    {
        --g_ui8TpiuEnCnt;
    }

    if ( g_ui8TpiuEnCnt > 0 )
    {
        //
        // TPIU needs to remain enabled for now.
        //
        ui32Status = AM_HAL_STATUS_IN_USE;
    }
    else
    {
        //
        // Invalidate any previous TPIU configuration
        //
        g_bTpiu_DebugEnabled = false;

        //
        // Shut down the general debug/tracing configuration.
        //
        ui32Status = am_hal_debug_disable();
        if ( ui32Status == AM_HAL_STATUS_IN_USE )
        {
            ui32Status = AM_HAL_STATUS_SUCCESS;
        }
    }

    AM_CRITICAL_END

    return ui32Status;

}
