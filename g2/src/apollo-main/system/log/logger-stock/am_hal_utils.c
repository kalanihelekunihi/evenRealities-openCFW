//*****************************************************************************
//
//! @file am_hal_utils.c
//!
//! @brief HAL Utility Functions
//!
//! @addtogroup utils4_ap510 Utils - HAL Utility Functions
//! @ingroup apollo510_hal
//! @{
//!
//! Purpose: This module provides utility functions for the HAL on Apollo5 devices,
//!          including delay functions, status checking, and memory operations.
//!          It supports precise timing control, status monitoring, and efficient
//!          memory access for system-level operations and debugging.
//!
//! @section hal_utils_features Key Features
//!
//! 1. @b Delay @b Functions: Precise microsecond and cycle-based delay operations.
//! 2. @b Status @b Monitoring: Check register status with timeout capabilities.
//! 3. @b Memory @b Operations: Efficient word-based memory read operations.
//! 4. @b Burst @b Mode: Support for burst mode status checking.
//! 5. @b BootROM @b Integration: Integration with bootrom helper functions.
//!
//! @section hal_utils_functionality Functionality
//!
//! - Provide precise delay functions in microseconds and cycles
//! - Monitor register status with timeout and equality checking
//! - Support efficient memory read operations
//! - Handle burst mode status and configuration
//! - Integrate with bootrom helper functionality
//!
//! @section hal_utils_usage Usage
//!
//! 1. Use delay functions for precise timing control
//! 2. Monitor register status with timeout capabilities
//! 3. Perform efficient memory read operations
//! 4. Check burst mode status as needed
//! 5. Integrate with bootrom helper functions
//!
//! @section hal_utils_configuration Configuration
//!
//! - @b Delay @b Timing: Configure delay parameters and cycle counts
//! - @b Status @b Monitoring: Set up timeout values and status checking
//! - @b Memory @b Access: Configure memory read operations
//! - @b Burst @b Mode: Set up burst mode operations
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
am_hal_delay_us_status_change(uint32_t ui32usMaxDelay, uint32_t ui32Address,
                              uint32_t ui32Mask, uint32_t ui32Value)
{
    while ( 1 )
    {
        //
        // Check the status
        //
        if ( ( AM_REGVAL(ui32Address) & ui32Mask ) == ui32Value )
        {
            return AM_HAL_STATUS_SUCCESS;
        }

        if (ui32usMaxDelay--)
        {
            //
            // Call the ROM helper cycle function to delay for about 1 microsecond.
            //
            am_hal_delay_us(1);
        }
        else
        {
            break;
        }
    }

    return AM_HAL_STATUS_TIMEOUT;

}
