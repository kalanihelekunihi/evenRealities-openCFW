//*****************************************************************************
//
//! @file am_hal_itm.c
//!
//! @brief Functions for operating the instrumentation trace macrocell
//!
//! @addtogroup itm4_ap510 ITM - Instrumentation Trace Macrocell
//! @ingroup apollo510_hal
//! @{
//!
//! Purpose: This module provides functions for operating the Instrumentation
//!          Trace Macrocell (ITM) on Apollo5 devices. It supports trace
//!          port configuration, stimulus register operations, print functions,
//!          and trace synchronization for debugging and development tools.
//!
//! @section hal_itm_features Key Features
//!
//! 1. @b Debug @b Tracing: Comprehensive debug trace functionality.
//! 2. @b Stimulus @b Ports: Multiple stimulus port operations.
//! 3. @b Trace @b Transmission: Real-time trace data transmission.
//! 4. @b TPIU @b Integration: Integration with Trace Port Interface Unit.
//! 5. @b Baud @b Rate: Configurable trace transmission baud rates.
//!
//! @section hal_itm_functionality Functionality
//!
//! - Enable and disable ITM functionality
//! - Configure trace parameters and baud rates
//! - Handle stimulus port operations
//! - Manage trace data transmission
//! - Integrate with TPIU for trace output
//!
//! @section hal_itm_usage Usage
//!
//! 1. Set ITM parameters using am_hal_itm_parameters_set()
//! 2. Enable ITM with am_hal_itm_enable()
//! 3. Configure stimulus ports and trace operations
//! 4. Handle trace data transmission
//! 5. Disable ITM when no longer needed
//!
//! @section hal_itm_configuration Configuration
//!
//! - @b Baud @b Rates: Configure trace transmission baud rates
//! - @b Stimulus @b Ports: Set up stimulus port operations
//! - @b TPIU @b Integration: Configure TPIU interface parameters
//! - @b Trace @b Parameters: Set up trace data format and timing
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
am_hal_itm_disable(void)
{
    uint32_t ui32Status = AM_HAL_STATUS_SUCCESS;

    //
    // Before disabling, make sure all printing has completed and the
    // ITM/TPIU pipelines are completely flushed.
    //
    am_hal_itm_tpiu_pipeline_flush();

    //
    // Disable SWO and the ITM.
    //
    ITM->TCR &= ~ITM_TCR_SWOENA_Msk;
    ITM->TCR &= ~ITM_TCR_ITMENA_Msk;

    //
    // Wait for the changes to take effect with a 1ms timeout.
    //
    ui32Status = am_hal_delay_us_status_change(1000,
                                               (uint32_t)&ITM->TCR,
                                               (ITM_TCR_ITMENA_Msk & ITM_TCR_BUSY_Msk),
                                               0 );
    if ( ui32Status != AM_HAL_STATUS_SUCCESS )
    {
        return ui32Status;
    }

    //
    // Shut down the general debug/tracing configuration.
    //
    ui32Status = am_hal_debug_disable();
    if ( ui32Status == AM_HAL_STATUS_IN_USE )
    {
        ui32Status = AM_HAL_STATUS_SUCCESS;
    }

    return ui32Status;

}

uint32_t
am_hal_itm_tpiu_pipeline_flush(void)
{
    //
    // ARMv8-M Software must ensure that all trace is output and flushed
    // before clearing TRCENA.
    //
    if ( !(am_hal_itm_print_not_busy() && am_hal_itm_not_busy()) )
    {
        return AM_HAL_STATUS_TIMEOUT;
    }

    //
    // At this point, ITM activity has completed. There could still be activity
    // in the ITM or TPIU pipeline, but this cannot be determined by Apollo510.
    //
    // The only thing that can be done is to allow some extra time for the
    // pipeline to be cleared.
    //
    // Note that future Ambiq devices may provide a status bit for this purpose.
    //
    am_hal_delay_us(500);

    return AM_HAL_STATUS_SUCCESS;

}

bool
am_hal_itm_not_busy(void)
{
    //
    // Make sure the ITM is not busy.
    //
    uint32_t ui32Ret;
    ui32Ret = am_hal_delay_us_status_change(1000,
                                            (uint32_t)&ITM->TCR,
                                            ITM_TCR_BUSY_Msk,
                                            0 );

    return (ui32Ret == AM_HAL_STATUS_SUCCESS) ? true : false;

}

bool
am_hal_itm_stimulus_not_busy(uint32_t ui32StimReg)
{
    uint32_t ui32StimAddr = (uint32_t)&ITM->PORT[0] + (4 * ui32StimReg);

    //
    // Waiting until port is available for writing, non-zero means ready to
    // accept additional characters.
    // Note that this doesn't necessarily mean the the port has emptied, and
    // there doesn't seem to be a way to determine that, so unfortunately this
    // function is a bit of a misnomer.
    //
    // M55 ITM stimulus registers on read:
    //  Bit1 DISABLED:  0=Stimulus port and ITM are enabled.
    //                  1=Stimulus port or ITM are disabled.
    //  Bit0 FIFOREADY: 0=Stimulus port cannot accept data,
    //                  1=Stimulus port can accept at least one word.
    //
    // Since this could likely occur while characters are still being output,
    // a hefty timeout period needs to be applied.
    //
    uint32_t ui32Ret;

    ui32Ret = am_hal_delay_us_status_change(1000,
                                            ui32StimAddr,
                                            ITM_STIM_DISABLED_Msk | ITM_STIM_FIFOREADY_Msk,
                                            ITM_STIM_FIFOREADY_Msk );

    return (ui32Ret == AM_HAL_STATUS_SUCCESS) ? true : false;
}

bool
am_hal_itm_print_not_busy(void)
{
    //
    // Poll stimulus register allocated for printing.
    //
    return am_hal_itm_stimulus_not_busy(0);

}
