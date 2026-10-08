// ****************************************************************************
//
//! @file am_hal_spotmgr_pcm2_2.c
//!
//! @brief SPOT manager functions that manage power states for PCM2.2 parts
//!
//! @addtogroup spotmgr_22_ap510 SPOTMGR - SPOT Manager PCM2.2
//! @ingroup apollo510_hal
//! @{
//!
//! Purpose: This module provides SPOT manager functionality for PCM2.2
//! Apollo5 devices, supporting advanced power state management, peripheral
//! control, and system optimization. It enables efficient power
//! management and system reliability for PCM2.2-based designs.
//!
//! @section hal_spotmgr_pcm2_2_features Key Features
//!
//! 1. @b PCM2.2 @b Support: Power management for PCM2.2 hardware.
//! 2. @b Temperature @b Compensation: Handle temperature-based power adjustments.
//! 3. @b SIMOBUCK/LDO @b Integration: Manage power domain transitions.
//! 4. @b SDIO/GPU @b Handling: Special handling for SDIO and GPU power events.
//! 5. @b Extensible: Support for custom power management strategies.
//!
//! @section hal_spotmgr_pcm2_2_functionality Functionality
//!
//! - Manage power state transitions for PCM2.2 hardware
//! - Integrate with SIMOBUCK, LDO, and other power domains
//! - Handle temperature compensation and event postponement
//! - Support for SDIO and GPU power event handling
//! - Provide hooks for board-specific power management
//!
//! @section hal_spotmgr_pcm2_2_usage Usage
//!
//! 1. Initialize SPOT manager for PCM2.2 hardware
//! 2. Handle power state transitions in response to events
//! 3. Integrate with board and application power management
//! 4. Extend with custom logic as needed
//!
//! @section hal_spotmgr_pcm2_2_configuration Configuration
//!
//! - @b PCM @b Version: Select PCM2.2 for hardware
//! - @b Temperature @b Compensation: Configure compensation parameters
//! - @b SDIO/GPU: Set up event handling as required
//****************************************************************************

// ****************************************************************************
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
// This is part of revision release_5p1p0beta-2927d425bf of the AmbiqSuite Development Package.
//
// ****************************************************************************


/* Exact extracted public bodies/enums/macros; static/inline linkage removed. */
#include <stdint.h>
typedef enum
{
    AM_HAL_SPOTMGR_TRANS_SEQ_0  , // From "PCM2.1 LP" to "PCM2.0 LP peripheral on and GPU&SDIO off" or "PCM2.0 LP GPU/SDIO on"
    AM_HAL_SPOTMGR_TRANS_SEQ_1  , // From "PCM2.1 LP" to "PCM2.1 HP"
    AM_HAL_SPOTMGR_TRANS_SEQ_2  , // From "PCM2.0 LP peripheral on and GPU&SDIO off" or "PCM2.0 LP GPU/SDIO on" to "PCM2.1 LP"
    AM_HAL_SPOTMGR_TRANS_SEQ_3  , // From "PCM2.0 LP peripheral on and GPU&SDIO off" to "PCM2.0 HP peripheral on" or "PCM2.0 LP GPU/SDIO on"
    AM_HAL_SPOTMGR_TRANS_SEQ_4  , // From "PCM2.1 HP" to "PCM2.1 LP"
    AM_HAL_SPOTMGR_TRANS_SEQ_5  , // From "PCM2.1 HP" to "PCM2.0 HP peripheral on"
    AM_HAL_SPOTMGR_TRANS_SEQ_6  , // From "PCM2.0 HP peripheral on" to "PCM2.0 LP peripheral on and GPU&SDIO off"
    AM_HAL_SPOTMGR_TRANS_SEQ_7  , // From "PCM2.0 HP peripheral on" to "PCM2.1 HP"
    AM_HAL_SPOTMGR_TRANS_SEQ_8  , // From "PCM2.0 HP peripheral on" to "PCM2.0 LP GPU/SDIO on"
    AM_HAL_SPOTMGR_TRANS_SEQ_9  , // From "PCM2.0 LP GPU/SDIO on" to "PCM2.0 LP peripheral on and GPU&SDIO off"
    AM_HAL_SPOTMGR_TRANS_SEQ_10 , // From "PCM2.0 LP GPU/SDIO on" to "PCM2.0 HP peripheral on"
    AM_HAL_SPOTMGR_TRANS_SEQ_11 , // Temperature transitions to > 50C and Power state 9 to 8 transition
    AM_HAL_SPOTMGR_TRANS_SEQ_12 , // Temperature transitions to > 50C and Power state 1 to 0 transition
    AM_HAL_SPOTMGR_TRANS_SEQ_13 , // Temperature transitions to < 50C and Power state 8 to 9 transition
    AM_HAL_SPOTMGR_TRANS_SEQ_14 , // Temperature transitions to < 50C and Power state 0 to 1 transition
    AM_HAL_SPOTMGR_TRANS_SEQ_15 , // Temperature transitions to > 0C and Power state 2 to 1 or 10 to 9 transition
    AM_HAL_SPOTMGR_TRANS_SEQ_16 , // Temperature transitions to > 0C and not Power state 2 to 1 or 10 to 9 transition
    AM_HAL_SPOTMGR_TRANS_SEQ_17 , // Temperature transitions to < 0C and Power state 9 to 10 transition
    AM_HAL_SPOTMGR_TRANS_SEQ_18 , // Temperature transitions to < 0C and Power state 1 to 2 transition
    AM_HAL_SPOTMGR_TRANS_SEQ_19 , // Temperature transitions to < 0C and not Power state 9 to 10 or 1 to 2 transition
    AM_HAL_SPOTMGR_TRANS_SEQ_20 , // Temperature transitions: Power state 11 to 10 or 10 to 11 transition
    AM_HAL_SPOTMGR_TRANS_SEQ_21 , // Power state 0 to 8 transition
    AM_HAL_SPOTMGR_TRANS_SEQ_22 , // Power state 8 to 0 transition
    AM_HAL_SPOTMGR_TRANS_SEQ_23 , // Power state 8 to 12 or 12 to 8 transition
    AM_HAL_SPOTMGR_TRANS_SEQ_24 , // Other temperature transitions besides SEQ_11 to SEQ_20
    AM_HAL_SPOTMGR_TRANS_SEQ_TEMP_TRANS, // The first entry of Temperature transitions
    AM_HAL_SPOTMGR_TRANS_SEQ_INVALID, // Invalid state transitions
} am_hal_spotmgr_transition_sequence_e;
typedef enum
{
    //! -40C ~ -20C
    AM_HAL_SPOTMGR_TEMPCO_RANGE_VERY_LOW,
    //! -20C ~ 0C
    AM_HAL_SPOTMGR_TEMPCO_RANGE_LOW,
    //! 0C ~ 50C
    AM_HAL_SPOTMGR_TEMPCO_RANGE_MID,
    //! > 50C
    AM_HAL_SPOTMGR_TEMPCO_RANGE_HIGH,
    AM_HAL_SPOTMGR_TEMPCO_OUT_OF_RANGE,
    //! Default temperature value.
    AM_HAL_SPOTMGR_TEMPCO_UNKNOWN
} am_hal_spotmgr_tempco_range_e;
#define STATE_TEMP_RANGE_MASK 0x00000003
#define StateGroup(m) ((m) >> 2)
#define IsStateGT50C(m) (((m & STATE_TEMP_RANGE_MASK) == 0) && (StateGroup(m) <= 4))
#define IsStateLE50C(m) (((m & STATE_TEMP_RANGE_MASK) > 0) && (StateGroup(m) <= 4))
#define IsStateGT0C(m) (((m & STATE_TEMP_RANGE_MASK) <= 1) && (StateGroup(m) <= 4))
#define IsStateLE0C(m) (((m & STATE_TEMP_RANGE_MASK) >= 2) && (StateGroup(m) <= 4))
#define LOW_LIMIT                 -273.0f
#define HIGH_LIMIT                1000.0f
#define VDDC_VDDF_TEMPCO_THRESHOLD_LOW  -20.0f
#define VDDC_VDDF_TEMPCO_THRESHOLD_MID    0.0f
#define VDDC_VDDF_TEMPCO_THRESHOLD_HIGH  50.0f
#define AM_HAL_STATUS_SUCCESS 0
#define AM_HAL_STATUS_INVALID_OPERATION 7
am_hal_spotmgr_tempco_range_e spotmgr_temp_to_range(float fTemp)
{
    if ((fTemp < VDDC_VDDF_TEMPCO_THRESHOLD_LOW) && (fTemp >= LOW_LIMIT))
    {
        return AM_HAL_SPOTMGR_TEMPCO_RANGE_VERY_LOW;
    }
    else if ((fTemp >= VDDC_VDDF_TEMPCO_THRESHOLD_LOW) && (fTemp < VDDC_VDDF_TEMPCO_THRESHOLD_MID))
    {
        return AM_HAL_SPOTMGR_TEMPCO_RANGE_LOW;
    }
    else if ((fTemp >= VDDC_VDDF_TEMPCO_THRESHOLD_MID) && (fTemp < VDDC_VDDF_TEMPCO_THRESHOLD_HIGH))
    {
        return AM_HAL_SPOTMGR_TEMPCO_RANGE_MID;
    }
    else if ((fTemp >= VDDC_VDDF_TEMPCO_THRESHOLD_HIGH) && (fTemp < HIGH_LIMIT))
    {
        return AM_HAL_SPOTMGR_TEMPCO_RANGE_HIGH;
    }
    return AM_HAL_SPOTMGR_TEMPCO_OUT_OF_RANGE;
}
uint32_t spotmgr_state_transition_sequence_determine(uint32_t ui32TarPwrState, uint32_t ui32CurPwrState, am_hal_spotmgr_transition_sequence_e * peSeqNum)
{
    am_hal_spotmgr_transition_sequence_e eTransitionSeqTable[5][5] =
    {
        {AM_HAL_SPOTMGR_TRANS_SEQ_TEMP_TRANS, AM_HAL_SPOTMGR_TRANS_SEQ_0,          AM_HAL_SPOTMGR_TRANS_SEQ_1,          AM_HAL_SPOTMGR_TRANS_SEQ_INVALID,    AM_HAL_SPOTMGR_TRANS_SEQ_0         },
        {AM_HAL_SPOTMGR_TRANS_SEQ_2,          AM_HAL_SPOTMGR_TRANS_SEQ_TEMP_TRANS, AM_HAL_SPOTMGR_TRANS_SEQ_INVALID,    AM_HAL_SPOTMGR_TRANS_SEQ_3,          AM_HAL_SPOTMGR_TRANS_SEQ_3         },
        {AM_HAL_SPOTMGR_TRANS_SEQ_4,          AM_HAL_SPOTMGR_TRANS_SEQ_INVALID,    AM_HAL_SPOTMGR_TRANS_SEQ_TEMP_TRANS, AM_HAL_SPOTMGR_TRANS_SEQ_5,          AM_HAL_SPOTMGR_TRANS_SEQ_INVALID   },
        {AM_HAL_SPOTMGR_TRANS_SEQ_INVALID,    AM_HAL_SPOTMGR_TRANS_SEQ_6,          AM_HAL_SPOTMGR_TRANS_SEQ_7,          AM_HAL_SPOTMGR_TRANS_SEQ_TEMP_TRANS, AM_HAL_SPOTMGR_TRANS_SEQ_8         },
        {AM_HAL_SPOTMGR_TRANS_SEQ_2,          AM_HAL_SPOTMGR_TRANS_SEQ_9,          AM_HAL_SPOTMGR_TRANS_SEQ_INVALID,    AM_HAL_SPOTMGR_TRANS_SEQ_10,         AM_HAL_SPOTMGR_TRANS_SEQ_TEMP_TRANS}
    };

    //
    // Get the sequence index from the table
    //
    *peSeqNum = eTransitionSeqTable[StateGroup(ui32CurPwrState)][StateGroup(ui32TarPwrState)];
    if (*peSeqNum == AM_HAL_SPOTMGR_TRANS_SEQ_INVALID)
    {
        return AM_HAL_STATUS_INVALID_OPERATION;
    }
    //
    // Special handling for power state 0<->8 transitions
    //
    if ((ui32CurPwrState == 0) && (ui32TarPwrState == 8))
    {
        *peSeqNum = AM_HAL_SPOTMGR_TRANS_SEQ_21;
    }
    else if ((ui32CurPwrState == 8) && (ui32TarPwrState == 0))
    {
        *peSeqNum = AM_HAL_SPOTMGR_TRANS_SEQ_22;
    }
    //
    // Special handling for power state 12<->8 transitions
    //
    if (((ui32CurPwrState == 8) && (ui32TarPwrState == 12)) ||
        ((ui32CurPwrState == 12) && (ui32TarPwrState == 8)))
    {
        *peSeqNum = AM_HAL_SPOTMGR_TRANS_SEQ_23;
    }
    //
    // If it is tempperature transition, execute the code below.
    //
    if (*peSeqNum == AM_HAL_SPOTMGR_TRANS_SEQ_TEMP_TRANS)
    {
        //
        // Tansitions to > 50C
        //
        if (IsStateLE50C(ui32CurPwrState) && IsStateGT50C(ui32TarPwrState))
        {
            if ((ui32CurPwrState == 9) &&
                (ui32TarPwrState == 8))
            {
                *peSeqNum = AM_HAL_SPOTMGR_TRANS_SEQ_11;
            }
            else if ((ui32CurPwrState == 1) &&
                     (ui32TarPwrState == 0))
            {
                *peSeqNum = AM_HAL_SPOTMGR_TRANS_SEQ_12;
            }
            else
            {
                //
                // The temperature transition does not need any trim update
                //
                *peSeqNum = AM_HAL_SPOTMGR_TRANS_SEQ_24;
            }
        }
        //
        // Tansitions to < 50C
        //
        else if (IsStateGT50C(ui32CurPwrState) && IsStateLE50C(ui32TarPwrState))
        {
            if ((ui32CurPwrState == 8) &&
                (ui32TarPwrState == 9))
            {
                *peSeqNum = AM_HAL_SPOTMGR_TRANS_SEQ_13;
            }
            else if ((ui32CurPwrState == 0) &&
                     (ui32TarPwrState == 1))
            {
                *peSeqNum = AM_HAL_SPOTMGR_TRANS_SEQ_14;
            }
            else
            {
                //
                // The temperature transition does not need any trim update
                //
                *peSeqNum = AM_HAL_SPOTMGR_TRANS_SEQ_24;
            }
        }
        //
        // Tansitions to > 0C
        //
        else if (IsStateLE0C(ui32CurPwrState) && IsStateGT0C(ui32TarPwrState))
        {
            if (((ui32CurPwrState == 2) && (ui32TarPwrState == 1)) ||
                ((ui32CurPwrState == 10) && (ui32TarPwrState == 9)))
            {
                *peSeqNum = AM_HAL_SPOTMGR_TRANS_SEQ_15;
            }
            else
            {
                *peSeqNum = AM_HAL_SPOTMGR_TRANS_SEQ_16;
            }
        }
        //
        // Tansitions to < 0C
        //
        else if (IsStateGT0C(ui32CurPwrState) && IsStateLE0C(ui32TarPwrState))
        {
            if ((ui32CurPwrState == 9) && (ui32TarPwrState == 10))
            {
                *peSeqNum = AM_HAL_SPOTMGR_TRANS_SEQ_17;
            }
            else if ((ui32CurPwrState == 1) && (ui32TarPwrState == 2))
            {
                *peSeqNum = AM_HAL_SPOTMGR_TRANS_SEQ_18;
            }
            else
            {
                *peSeqNum = AM_HAL_SPOTMGR_TRANS_SEQ_19;
            }
        }
        //
        // Special handling for 10<->11.
        //
        else if (((ui32CurPwrState == 10) && (ui32TarPwrState == 11)) ||
                 ((ui32CurPwrState == 11) && (ui32TarPwrState == 10)))
        {
            *peSeqNum = AM_HAL_SPOTMGR_TRANS_SEQ_20;
        }
        else
        {
            //
            // The temperature transition does not need any trim update
            //
            *peSeqNum = AM_HAL_SPOTMGR_TRANS_SEQ_24;
        }
    }

    return AM_HAL_STATUS_SUCCESS;
}
