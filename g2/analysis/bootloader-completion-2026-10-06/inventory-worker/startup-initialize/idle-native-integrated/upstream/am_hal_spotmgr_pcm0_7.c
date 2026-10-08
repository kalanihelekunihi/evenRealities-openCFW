// ****************************************************************************
//
//! @file am_hal_spotmgr_pcm0_7.c
//!
//! @brief SPOT manager functions that manage power states for PCM0.7 parts.
//!
//! @addtogroup spotmgr_07_ap510 SPOTMGR - SPOT Manager PCM0.7
//! @ingroup apollo510_hal
//! @{
//!
//! Purpose: This module provides SPOT manager functionality for PCM0.7
//! Apollo5 devices, supporting power state management, peripheral
//! control, and system optimization. It enables efficient power
//! management and system reliability for PCM0.7-based designs.
//!
//! @section hal_spotmgr_pcm0_7_features Key Features
//!
//! 1. @b PCM0.7 @b Support: Power management for PCM0.7 hardware.
//! 2. @b TON @b Configuration: Manage TON levels for different power states.
//! 3. @b SIMOBUCK/LDO @b Integration: Control power domain transitions.
//! 4. @b GPU/SDIO @b Handling: Special handling for GPU and SDIO power events.
//! 5. @b Extensible: Support for custom power management strategies.
//!
//! @section hal_spotmgr_pcm0_7_functionality Functionality
//!
//! - Manage power state transitions for PCM0.7 hardware
//! - Configure TON levels for various power states
//! - Integrate with SIMOBUCK, LDO, and other power domains
//! - Handle GPU and SDIO power event handling
//! - Provide hooks for board-specific power management
//!
//! @section hal_spotmgr_pcm0_7_usage Usage
//!
//! 1. Initialize SPOT manager for PCM0.7 hardware
//! 2. Handle power state transitions in response to events
//! 3. Integrate with board and application power management
//! 4. Extend with custom logic as needed
//!
//! @section hal_spotmgr_pcm0_7_configuration Configuration
//!
//! - @b PCM @b Version: Select PCM0.7 for hardware
//! - @b TON @b Levels: Configure TON levels for power states
//! - @b GPU/SDIO: Set up event handling as required
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

#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include "am_mcu_apollo.h"
#include "mcu/am_hal_sysctrl_ton_config.h"

//*****************************************************************************
//
//! Defines
//
//*****************************************************************************

//*****************************************************************************
//
//! Extern Variables
//
//*****************************************************************************
extern uint32_t g_orig_TVRGCVREFTRIM;
extern uint32_t g_orig_TVRGFVREFTRIM;
extern uint32_t g_orig_VDDCLKGTRIM;
extern uint32_t g_orig_CORELDOTEMPCOTRIM;
extern uint32_t g_orig_CORELDOACTIVETRIM;

//*****************************************************************************
//
//! Static Variable
//
//*****************************************************************************
static uint32_t g_ui32CurCORELDOTEMPCOTRIMLDO  = 0;
static uint32_t g_ui32CurMEMLDOACTIVETRIMLDO   = 0;

// Simobuck Ton active trim values
static uint8_t g_ui8VddcActLowTonTrim    = 0x0D;
static uint8_t g_ui8VddcActHighTonTrim   = 0x0D;
static uint8_t g_ui8VddcLvActLowTonTrim  = 0x0B;
static uint8_t g_ui8VddcLvActHighTonTrim = 0x0B;
static uint8_t g_ui8VddfActLowTonTrim    = 0x12;
static uint8_t g_ui8VddfActHighTonTrim   = 0x19;

//
// TON Configuration Tables
//
#if (AM_SIMOBUCK_SCHEME_HIGH_EFFICIENCY == 0)
static const am_hal_sysctrl_ton_levels_t ui8TonActiveConfig[SYSCTRL_GPU_TON_POWER_STATE_MAX][SYSCTRL_CPU_TON_POWER_STATE_MAX] =
{
    {SYSCTRL_TON_LEVEL_LOW, SYSCTRL_TON_LEVEL_LOW,  SYSCTRL_TON_LEVEL_HIGH},
    {SYSCTRL_TON_LEVEL_LOW, SYSCTRL_TON_LEVEL_LOW,  SYSCTRL_TON_LEVEL_HIGH},
    {SYSCTRL_TON_LEVEL_LOW, SYSCTRL_TON_LEVEL_HIGH, SYSCTRL_TON_LEVEL_HIGH},
};
#else
static const am_hal_sysctrl_ton_levels_t ui8TonActiveConfig[SYSCTRL_GPU_TON_POWER_STATE_MAX][SYSCTRL_CPU_TON_POWER_STATE_MAX] =
 {
    {SYSCTRL_TON_LEVEL_LOW, SYSCTRL_TON_LEVEL_LOW,  SYSCTRL_TON_LEVEL_LOW },
    {SYSCTRL_TON_LEVEL_LOW, SYSCTRL_TON_LEVEL_LOW,  SYSCTRL_TON_LEVEL_LOW },
    {SYSCTRL_TON_LEVEL_LOW, SYSCTRL_TON_LEVEL_LOW,  SYSCTRL_TON_LEVEL_HIGH},
};
#endif

//*****************************************************************************
//
//! Globals
//
//*****************************************************************************

//*****************************************************************************
//
//! Extern Functions
//
//*****************************************************************************
void buck_ldo_update_override(bool bEnable);

// ****************************************************************************
//
//  Internal function for SIMOBUCK on/off
//
// ****************************************************************************
static inline void
simobuck_enable(bool bEnable)
{
    if (bEnable)
    {
        //
        // Enable the simobuck
        //
        PWRCTRL->VRCTRL_b.SIMOBUCKEN = 1;
        am_hal_delay_us(5);
        buck_ldo_update_override(true);
    }
    else
    {
        //
        // Disable the simobuck
        //
        buck_ldo_update_override(false);
        am_hal_delay_us(5);
        PWRCTRL->VRCTRL_b.SIMOBUCKEN = 0;
    }
}

//*****************************************************************************
//
//! @brief Handle GPU On sequence for PCM0.7
//!
//! @param eGpuState - GPU Power State in am_hal_spotmgr_gpu_state_e type
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
static uint32_t am_hal_spotmgr_pcm0_7_gpu_on_sequence(am_hal_spotmgr_gpu_state_e eState)
{
    // If GPU HP mode is not selected, update Ton Config to Low Power
    if (eState != AM_HAL_SPOTMGR_GPUSTATE_ACTIVE_HP)
    {
        am_hal_spotmgr_ton_config_update(true, AM_HAL_PWRCTRL_GPU_MODE_LOW_POWER);
    }

    // Buck mode
    if (PWRCTRL->VRSTATUS_b.SIMOBUCKST == PWRCTRL_VRSTATUS_SIMOBUCKST_ACT)
    {
        if (g_bOrigTrimsStored)
        {
            //
            // Disable the simobuck
            //
            simobuck_enable(false);
            //
            // coreldo boost
            //
            MCUCTRL->LDOREG1_b.CORELDOTEMPCOTRIM = 1;
            //
            // Simobuck VDDC boost
            //
            FINAL_VAL_OVF_CAP_BASE(g_orig_TVRGCVREFTRIM, 9, MCUCTRL, VREFGEN2, TVRGCVREFTRIM);
            //
            // Simobuck VDDC boost
            //
            MCUCTRL->D2ASPARE_b.SIMOVDDCBOOST = 1;
            //
            // Simobuck VDDF and memldo boost
            //
            FINAL_VAL_OVF_CAP_BASE(g_orig_TVRGFVREFTRIM, 15, MCUCTRL, VREFGEN4, TVRGFVREFTRIM);
            //
            // Adjust the simobuck Ton gen clock to compensate for the VDDC boost
            //
            MCUCTRL->SIMOBUCK14_b.VDDCLKGTRIM = 3;
            //
            // Enable the simobuck
            //
            simobuck_enable(true);
            //
            // Delay 20us for VDDC and VDDF to boost
            //
            am_hal_delay_us(15);
        }
    }
    // LDO Mode
    else
    {
        //
        // coreldo boost
        //
        g_ui32CurCORELDOTEMPCOTRIMLDO = MCUCTRL->LDOREG1_b.CORELDOTEMPCOTRIM;
        MCUCTRL->LDOREG1_b.CORELDOTEMPCOTRIM = 2;
        //
        // memldo boost
        //
        g_ui32CurMEMLDOACTIVETRIMLDO = MCUCTRL->LDOREG2_b.MEMLDOACTIVETRIM;
        FINAL_VAL_OVF_CAP(5, MCUCTRL, LDOREG2, MEMLDOACTIVETRIM);
        //
        // Delay 15us for coreldo and memldo to boost
        //
        am_hal_delay_us(15);
    }

    return AM_HAL_STATUS_SUCCESS;
}

//*****************************************************************************
//
//! @brief Handle GPU Off sequence for PCM0.7
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
static uint32_t am_hal_spotmgr_pcm0_7_gpu_off_sequence()
{
    if (PWRCTRL->VRSTATUS_b.SIMOBUCKST == PWRCTRL_VRSTATUS_SIMOBUCKST_ACT) // Buck mode
    {
        if (g_bOrigTrimsStored)
        {
            //
            // Disable the simobuck
            //
            simobuck_enable(false);
            //
            // Set back to original value
            //
            MCUCTRL->SIMOBUCK14_b.VDDCLKGTRIM = g_orig_VDDCLKGTRIM;
            //
            // Set back to original value
            //
            MCUCTRL->VREFGEN4_b.TVRGFVREFTRIM = g_orig_TVRGFVREFTRIM;
            //
            // Set back to original value
            //
            MCUCTRL->D2ASPARE_b.SIMOVDDCBOOST = 0;
            //
            // Set back to original value
            //
            MCUCTRL->VREFGEN2_b.TVRGCVREFTRIM = g_orig_TVRGCVREFTRIM;
            //
            // Set back to original value
            //
            MCUCTRL->LDOREG1_b.CORELDOTEMPCOTRIM = g_orig_CORELDOTEMPCOTRIM;
            //
            // Enable the simobuck
            //
            simobuck_enable(true);
        }
    }
    else
    {
        //
        // Set back to original value
        //
        MCUCTRL->LDOREG2_b.MEMLDOACTIVETRIM = g_ui32CurMEMLDOACTIVETRIMLDO;
        //
        // Set back to original value
        //
        MCUCTRL->LDOREG1_b.CORELDOTEMPCOTRIM = g_ui32CurCORELDOTEMPCOTRIMLDO;
    }

    //
    // Update TON configuration after GPU is done turned off
    //
    am_hal_spotmgr_ton_config_update(false, AM_HAL_PWRCTRL_GPU_MODE_LOW_POWER);
    return AM_HAL_STATUS_SUCCESS;
}

//*****************************************************************************
//
//! @brief Power states update for PCM0.7
//!
//! @param eStimulus - Stimilus for power states transition. For GPU state/power
//!                    changes, please use AM_HAL_SPOTMGR_STIM_GPU_STATE but not
//!                    AM_HAL_SPOTMGR_STIM_DEVPWR.
//! @param bOn       - Only needs to be set to true/false when turning on/off
//!                    peripherals or memories included in DEVPWRSTATUS,
//!                    AUDSSPWRSTATUS, MEMPWRSTATUS and SSRAMPWRST. It is
//!                    ignored when updating temperature, CPU state and GPU state.
//! @param pArgs     - Pointer to arguments for power states update, assign it
//!                    to NULL if not needed.
//!
//! When eStimulus is AM_HAL_SPOTMGR_STIM_CPU_STATE,
//! bOn is ignored, and pArgs must point to a am_hal_spotmgr_cpu_state_e enum.
//!
//! When eStimulus is AM_HAL_SPOTMGR_STIM_GPU_STATE,
//! bOn is ignored, and pArgs must point to a am_hal_spotmgr_gpu_state_e enum.
//!
//! When eStimulus is AM_HAL_SPOTMGR_STIM_TEMP,
//! bOn is ignored, and pArgs must point to a am_hal_spotmgr_tempco_param_t struct.
//!
//! When eStimulus is AM_HAL_SPOTMGR_STIM_DEVPWR,
//! bOn must be set to true when turning on a peripheral,
//! bOn must be set to false when turning off a peripheral,
//! and pArgs must point to the DEVPWRSTATUS_MASK of the peripheral to be opened
//! when turning on a peripheral, pArgs is ignored when turning off a peripheral.
//!
//! When eStimulus is AM_HAL_SPOTMGR_STIM_AUDSSPWR,
//! bOn must be set to true when turning on a peripheral,
//! bOn must be set to false when turning off a peripheral,
//! and pArgs must point to the AUDSSPWRSTATUS_MASK of the peripheral to be opened
//! when turning on a peripheral, pArgs is ignored when turning off a peripheral.
//!
//! When eStimulus is AM_HAL_SPOTMGR_STIM_MEMPWR,
//! bOn is ignored, and pArgs must point to the entire MEMPWRSTATUS.
//!
//! When eStimulus is AM_HAL_SPOTMGR_STIM_SSRAMPWR,
//! bOn must be set to true when turning on partial or entire SSRAM,
//! bOn must be set to false when turning off partial or entire SSRAM,
//! and pArgs must point to the expected SSRAMPWRST when turning on,
//! pArgs is ignored when turning off.
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t
am_hal_spotmgr_pcm0_7_power_state_update(am_hal_spotmgr_stimulus_e eStimulus, bool bOn, void *pArgs)
{
    uint32_t ui32Status = AM_HAL_STATUS_SUCCESS;

    switch (eStimulus)
    {
        case AM_HAL_SPOTMGR_STIM_INIT_STATE:
            break;
        case AM_HAL_SPOTMGR_STIM_CPU_STATE:
            // Nothing to be done for PCM0.7
            break;
        case AM_HAL_SPOTMGR_STIM_GPU_STATE:
        {
            am_hal_spotmgr_gpu_state_e eState = *((am_hal_spotmgr_gpu_state_e*)pArgs);
            if (eState == AM_HAL_SPOTMGR_GPUSTATE_OFF)
            {
                am_hal_spotmgr_pcm0_7_gpu_off_sequence();
            }
            else
            {
                am_hal_spotmgr_pcm0_7_gpu_on_sequence(eState);
            }
            break;
        }
        case AM_HAL_SPOTMGR_STIM_TEMP:
        {
            am_hal_spotmgr_tempco_param_t *psTempCo = (am_hal_spotmgr_tempco_param_t *)pArgs;
            psTempCo->fRangeLower = LOW_LIMIT;
            psTempCo->fRangeHigher = HIGH_LIMIT;
            break;
        }
        case AM_HAL_SPOTMGR_STIM_DEVPWR:
            // Nothing to be done for PCM0.7
            break;
        case AM_HAL_SPOTMGR_STIM_AUDSSPWR:
            // Nothing to be done for PCM0.7
            break;
        case AM_HAL_SPOTMGR_STIM_MEMPWR:
            // Nothing to be done for PCM0.7
            break;
        case AM_HAL_SPOTMGR_STIM_SSRAMPWR:
            // Nothing to be done for PCM0.7
            break;
        case AM_HAL_SPOTMGR_STIM_BACK_TO_DEFAULT_STATE:
            break;
    }

    return ui32Status;
}

//*****************************************************************************
//
//! @brief SIMOBUCK initialziation handling at stage just before enabling
//!        SIMOBUCK for PCM0.7
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t am_hal_spotmgr_pcm0_7_simobuck_init_bfr_enable(void)
{
    if (g_bOrigTrimsStored)
    {
        FINAL_VAL_UDF_CAP_BASE(g_orig_CORELDOACTIVETRIM, CORELDOACTIVETRIM_REDUCE_IN_SIMOBUCK_INIT, MCUCTRL, LDOREG1, CORELDOACTIVETRIM);
    }
    return AM_HAL_STATUS_SUCCESS;
}

//*****************************************************************************
//
//! @brief SIMOBUCK initialziation handling at stage just after enabling
//!        SIMOBUCK for PCM0.7
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t am_hal_spotmgr_pcm0_7_simobuck_init_aft_enable(void)
{
    am_hal_delay_us(100);
    MCUCTRL->LDOREG2_b.MEMLDOACTIVETRIM = 0;
    MCUCTRL->D2ASPARE_b.MEMLDOREF = 0x1;
    am_hal_delay_us(100);
    return AM_HAL_STATUS_SUCCESS;
}

//*****************************************************************************
//
//! @brief Intitialize TON Config hanlding for PCM0.7 and earlier
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t am_hal_spotmgr_pcm0_7_ton_config_init(void)
{
    //
    // Read Ton-Active-Trim values from registers during initialization
    //
    if (APOLLO5_B0_GE_PCM0P7 || APOLLO5_GE_B1)
    {
        g_ui8VddcActLowTonTrim    = MCUCTRL->SIMOBUCK2_b.VDDCACTLOWTONTRIM;
        g_ui8VddcActHighTonTrim   = MCUCTRL->SIMOBUCK2_b.VDDCACTHIGHTONTRIM;
        g_ui8VddfActLowTonTrim    = MCUCTRL->SIMOBUCK7_b.VDDFACTLOWTONTRIM;
        g_ui8VddfActHighTonTrim   = MCUCTRL->SIMOBUCK6_b.VDDFACTHIGHTONTRIM;
        g_ui8VddcLvActLowTonTrim  = MCUCTRL->SIMOBUCK4_b.VDDCLVACTLOWTONTRIM;
        g_ui8VddcLvActHighTonTrim = MCUCTRL->SIMOBUCK4_b.VDDCLVACTHIGHTONTRIM;
    }
    else
    {
        g_ui8VddcActLowTonTrim    = SPOTMGR_FT_VDDCACTLOWTONTRIM;
        g_ui8VddcActHighTonTrim   = SPOTMGR_FT_VDDCACTHIGHTONTRIM;
        g_ui8VddfActLowTonTrim    = SPOTMGR_FT_VDDFACTLOWTONTRIM;
        g_ui8VddfActHighTonTrim   = SPOTMGR_FT_VDDFACTHIGHTONTRIM;
        g_ui8VddcLvActLowTonTrim  = SPOTMGR_FT_VDDCLVACTLOWTONTRIM;
        g_ui8VddcLvActHighTonTrim = SPOTMGR_FT_VDDCLVACTHIGHTONTRIM;
    }
    return AM_HAL_STATUS_SUCCESS;
}

//*****************************************************************************
//
//! @brief Update Ton Config for PCM0.7 and earlier
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t am_hal_spotmgr_pcm0_7_ton_config_update(bool bGpuOn, am_hal_pwrctrl_gpu_mode_e eGpuSt)
{
    am_hal_sysctrl_gpu_ton_power_state eGpuTonSt = SYSCTRL_GPU_TON_POWER_STATE_OFF;

    //
    // Turn off SIMOBUCK before configuring TON
    //
    bool bSIMOBUCKInitialized = PWRCTRL->VRCTRL_b.SIMOBUCKEN;
    if ( bSIMOBUCKInitialized )
    {
        buck_ldo_update_override(false);
        am_hal_delay_us(5);
        PWRCTRL->VRCTRL_b.SIMOBUCKEN = 0;
    }

    //
    // Convert GPU state to corresponding GPU Ton state
    //
    if (bGpuOn)
    {
        eGpuTonSt = (eGpuSt == AM_HAL_PWRCTRL_GPU_MODE_LOW_POWER) ? SYSCTRL_GPU_TON_POWER_STATE_LP:
                                                                    SYSCTRL_GPU_TON_POWER_STATE_HP;
    }
    //
    // Check whether the Ton settings should be at higher/lower values for CPU
    // LP and HP mode, for the GPU state specified, from the power table.
    //
    bool bTonLPisLow = (ui8TonActiveConfig[eGpuTonSt][SYSCTRL_CPU_TON_POWER_STATE_LP] == SYSCTRL_TON_LEVEL_LOW);
    bool bTonHPisLow = (ui8TonActiveConfig[eGpuTonSt][SYSCTRL_CPU_TON_POWER_STATE_HP] == SYSCTRL_TON_LEVEL_LOW);

    //
    // Enable SIMOBUCK HP trims
    //
    MCUCTRL->SIMOBUCK1_b.SIMOBUCKHPTRIMEN = MCUCTRL_SIMOBUCK1_SIMOBUCKHPTRIMEN_SIMOBUCK_HP_ON;

    //
    // Update VDDC and VDDF TON trim values for CPU LP and HP mode when
    // SIMOBUCK is active
    //
    MCUCTRL->SIMOBUCK2_b.VDDCACTLOWTONTRIM    = bTonLPisLow ? g_ui8VddcActLowTonTrim :
                                                              g_ui8VddcActHighTonTrim;
    MCUCTRL->SIMOBUCK2_b.VDDCACTHIGHTONTRIM   = bTonHPisLow ? g_ui8VddcActLowTonTrim :
                                                              g_ui8VddcActHighTonTrim;
    MCUCTRL->SIMOBUCK7_b.VDDFACTLOWTONTRIM    = bTonLPisLow ? g_ui8VddfActLowTonTrim :
                                                              g_ui8VddfActHighTonTrim;
    MCUCTRL->SIMOBUCK6_b.VDDFACTHIGHTONTRIM   = bTonHPisLow ? g_ui8VddfActLowTonTrim :
                                                              g_ui8VddfActHighTonTrim;
    MCUCTRL->SIMOBUCK4_b.VDDCLVACTLOWTONTRIM  = bTonLPisLow ? g_ui8VddcLvActLowTonTrim :
                                                              g_ui8VddcLvActHighTonTrim;
    MCUCTRL->SIMOBUCK4_b.VDDCLVACTHIGHTONTRIM = bTonHPisLow ? g_ui8VddcLvActLowTonTrim :
                                                              g_ui8VddcLvActHighTonTrim;

    //
    // Turn on SIMOBUCK aftger configuring TON
    //
    if ( bSIMOBUCKInitialized )
    {
        PWRCTRL->VRCTRL_b.SIMOBUCKEN = 1;
        am_hal_delay_us(5);
        buck_ldo_update_override(true);
    }
    return AM_HAL_STATUS_SUCCESS;
}

//*****************************************************************************
//
//! @brief SPOT manager init for PCM0.7
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t
am_hal_spotmgr_pcm0_7_init(void)
{
    // Nothing to be done for PCM0.7 for now
    return AM_HAL_STATUS_SUCCESS;
}


//*****************************************************************************
//
// End Doxygen group.
//! @}
//
//*****************************************************************************
