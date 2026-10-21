//*****************************************************************************
//
//! @file am_hal_mram.c
//!
//! @brief BootROM Helper Function Table
//!
//! @addtogroup mram4_ap510 MRAM Functionality
//! @ingroup apollo510_hal
//! @{
//!
//! Purpose: This module provides helper functions for accessing and programming
//!          MRAM (Magnetic Random Access Memory) on Apollo5 devices. It supports
//!          memory programming, filling operations, address validation, and
//!          non-volatile memory management for persistent data storage.
//!
//! @section hal_mram_features Key Features
//!
//! 1. @b MRAM @b Programming: Secure programming of MRAM memory regions.
//! 2. @b ROM @b Access: Helper functions for ROM-based operations.
//! 3. @b Memory @b Filling: Efficient memory fill operations with patterns.
//! 4. @b Security: Secure memory programming with key validation.
//! 5. @b Alignment: Proper memory alignment and boundary checking.
//!
//! @section hal_mram_functionality Functionality
//!
//! - Program MRAM memory regions with data
//! - Fill memory regions with specific patterns
//! - Handle memory alignment and boundary validation
//! - Support secure memory programming operations
//! - Provide ROM-based helper functions
//!
//! @section hal_mram_usage Usage
//!
//! 1. Program MRAM using am_hal_mram_main_words_program()
//! 2. Fill memory regions with am_hal_mram_main_fill()
//! 3. Initialize memory regions as needed
//! 4. Handle memory programming errors
//! 5. Validate memory addresses and alignment
//!
//! @section hal_mram_configuration Configuration
//!
//! - @b Programming @b Keys: Configure secure programming keys
//! - @b Memory @b Alignment: Ensure proper word alignment
//! - @b Address @b Validation: Validate memory addresses and boundaries
//! - @b Security: Set up secure memory programming parameters
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

#include <stdint.h>
#include <stdbool.h>
#include "am_mcu_apollo.h"
#include "am_hal_bootrom_helper.h"

#define AM_HAL_MRAM_WIPE                   0
#define AM_HAL_MRAM_PROGRAM                1

//*****************************************************************************
//
// This programs up to N words of the Main MRAM
//
//*****************************************************************************
uint32_t
am_hal_mram_main_words_program(uint32_t ui32ProgramKey, uint32_t *pui32Src,
                               uint32_t *pui32Dst, uint32_t ui32NumWords)
{
    uint32_t    ui32Status;

    //
    // Check that the pui32Dst is word aligned
    //
    if ( (uint32_t)pui32Dst & 0x3 )
    {
        return AM_HAL_MRAM_INVLD_ADDR_ALIGNMENT;
    }

    //
    // This helper function requires a word offset rather than an actual address.
    //
    pui32Dst = (uint32_t*)(((uint32_t)pui32Dst - AM_HAL_MRAM_ADDR) >> 2);

    AM_CRITICAL_BEGIN

    //
    // Enable the ROM for helper function.
    //
    am_hal_pwrctrl_rom_enable();

    ui32Status = nv_program_main2(ui32ProgramKey, AM_HAL_MRAM_PROGRAM, (uint32_t)pui32Src, (uint32_t)pui32Dst, ui32NumWords);

    //
    // Disable the ROM.
    //
    am_hal_pwrctrl_rom_disable();

    AM_CRITICAL_END

    //
    // Return the status.
    //
    if ( ui32Status == AM_HAL_MRAM_SUCCESS )
    {
        ui32Status = AM_HAL_STATUS_SUCCESS;
    }
    else
    {
        ui32Status |= AM_HAL_MRAM_ERROR;
    }

    return ui32Status;

} // am_hal_mram_main_words_program()

//*****************************************************************************
//
// This programs up to N words of the Main MRAM
//
//*****************************************************************************
uint32_t
am_hal_mram_main_program(uint32_t ui32ProgramKey, uint32_t *pui32Src,
                         uint32_t *pui32Dst, uint32_t ui32NumWords)
{
    //
    // Check for 16 byte aligned pui32Dst & ui32NumWords
    //
    if ( ((uint32_t)pui32Dst & 0xf) || (ui32NumWords & 0x3) )
    {
        return AM_HAL_MRAM_INVLD_ADDR_ALIGNMENT;
    }

    return am_hal_mram_main_words_program(ui32ProgramKey, pui32Src,
                                          pui32Dst, ui32NumWords);
} // am_hal_mram_main_program()

//*****************************************************************************
//
// This Fills up to N words of the Main MRAM
//
//*****************************************************************************
uint32_t
am_hal_mram_main_fill(uint32_t ui32ProgramKey, uint32_t ui32Value,
                      uint32_t *pui32Dst, uint32_t ui32NumWords)
{
    uint32_t    ui32Status;

    //
    // Check for 16 byte aligned pui32Dst & ui32NumWords
    //
    if ( ((uint32_t)pui32Dst & 0xf) || (ui32NumWords & 0x3) )
    {
        return AM_HAL_MRAM_INVLD_ADDR_ALIGNMENT;
    }

    //
    // This helper function requires a word offset rather than an actual address.
    //
    pui32Dst = (uint32_t*)(((uint32_t)pui32Dst - AM_HAL_MRAM_ADDR) >> 2);

    AM_CRITICAL_BEGIN

    //
    // Enable the ROM for helper functions.
    //
    am_hal_pwrctrl_rom_enable();

    ui32Status = nv_program_main2(ui32ProgramKey, AM_HAL_MRAM_WIPE, (uint32_t)ui32Value, (uint32_t)pui32Dst, ui32NumWords);

    //
    // Disable the ROM.
    //
    am_hal_pwrctrl_rom_disable();

    AM_CRITICAL_END

    //
    // Return the status.
    //
    if ( ui32Status == AM_HAL_MRAM_SUCCESS )
    {
        ui32Status = AM_HAL_STATUS_SUCCESS;
    }
    else
    {
        ui32Status |= AM_HAL_MRAM_ERROR;
    }

    return ui32Status;

} // am_hal_mram_main_fill()

//*****************************************************************************
//
// Initialize MRAM for DeepSleep.
//
//*****************************************************************************
uint32_t
am_hal_mram_ds_init(void)
{

    return AM_HAL_STATUS_SUCCESS;

} // am_hal_mram_ds_init()

//*****************************************************************************
//
// End Doxygen group.
//! @}
//
//*****************************************************************************
