// ****************************************************************************
//
//! @file am_hal_spotmgr_pcm2_0.c
//!
//! @brief SPOT manager functions that manage power states for PCM2.0, PCM1.1 and PCM1.0 parts.
//!
//! @addtogroup spotmgr_20_ap510 SPOTMGR - SPOT Manager PCM2.0
//! @ingroup apollo510_hal
//! @{
//!
//! Purpose: This module provides SPOT manager functionality for PCM1.0,
//! PCM1.1, and PCM2.0 Apollo5 devices, supporting power state management,
//! peripheral control, and system optimization. It enables efficient
//! power management and system reliability for a range of PCM-based
//! designs.
//!
//! @section hal_spotmgr_pcm2_0_features Key Features
//!
//! 1. @b PCM2.0/1.1/1.0 @b Support: Power management for multiple PCM versions.
//! 2. @b Temperature @b Compensation: Handle temperature-based power adjustments.
//! 3. @b SIMOBUCK/LDO @b Integration: Manage power domain transitions.
//! 4. @b SDIO/GPU @b Handling: Special handling for SDIO and GPU power events.
//! 5. @b Extensible: Support for custom power management strategies.
//!
//! @section hal_spotmgr_pcm2_0_functionality Functionality
//!
//! - Manage power state transitions for PCM2.0, PCM1.1, and PCM1.0
//! - Integrate with SIMOBUCK, LDO, and other power domains
//! - Handle temperature compensation and event postponement
//! - Support for SDIO and GPU power event handling
//! - Provide hooks for board-specific power management
//!
//! @section hal_spotmgr_pcm2_0_usage Usage
//!
//! 1. Initialize SPOT manager for PCM2.0/1.1/1.0 hardware
//! 2. Handle power state transitions in response to events
//! 3. Integrate with board and application power management
//! 4. Extend with custom logic as needed
//!
//! @section hal_spotmgr_pcm2_0_configuration Configuration
//!
//! - @b PCM @b Version: Select appropriate PCM version for hardware
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

#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include "am_mcu_apollo.h"

#if !AM_HAL_SPOTMGR_PCM2_0_DISABLE

//*****************************************************************************
//
//! Defines
//
//*****************************************************************************
#define TVRGFVREFTRIM_BOOST_CODE_FOR_GPU    (15)
#define CORELDOTRIM_BOOST_CODE_FOR_GPU      (12)
#define TVRGCVREFTRIM_BOOST_CODE_FOR_GPU    (9)
#define TVRGFVREFTRIM_BOOST_CODE_FOR_SDIO   (30)
#define DELAY_FOR_SDIO_VDDF_BOOST_IN_10US   (200)
typedef union
{
    uint32_t DATECODE;
    struct
    {
        uint32_t FT1REV : 16;
        uint32_t DATE   : 5;
        uint32_t MONTH  : 4;
        uint32_t YEAR   : 5;
        uint32_t        : 2;
    } DATECODE_b;
} date_code_t;

#define DATE_CODE_STRUCT         ((date_code_t)(g_sINFO1regs.ui32FT1_GDR1))
#define SDIO_SCREEN_PARTS_FOR_B2 ((DATE_CODE_STRUCT.DATECODE_b.YEAR == 24 && DATE_CODE_STRUCT.DATECODE_b.MONTH == 12 && DATE_CODE_STRUCT.DATECODE_b.DATE >= 20 && DATE_CODE_STRUCT.DATECODE_b.FT1REV == 0) || \
                                  (DATE_CODE_STRUCT.DATECODE_b.YEAR >= 25 && DATE_CODE_STRUCT.DATECODE_b.FT1REV == 0))
//
// B0-PCM1.0&PCM1.1, B1-PCM1.1&PCM2.0 are all unscreened parts, distinguish B2-PCM2.0 unscreened parts by date code.
//
#define NOT_SDIO_SCREEN_PARTS (APOLLO5_B0_GE_PCM1P0 || APOLLO5_B1_LE_PCM2P0 || (APOLLO5_B2_PCM2P0 && !SDIO_SCREEN_PARTS_FOR_B2))

//*****************************************************************************
//
//! Extern Variable
//
//*****************************************************************************
extern uint32_t g_orig_TVRGCVREFTRIM;
extern uint32_t g_orig_TVRGFVREFTRIM;
extern uint32_t g_orig_CORELDOACTIVETRIM;

//*****************************************************************************
//
//! Static Variable
//
//*****************************************************************************
static bool g_bIsB0Pcm1p0;
static bool g_bIsPCM1p0Or1p1;
DIAG_SUPPRESS_SETNOTUSED_VAR
static bool g_bIsPCM2p0Unscreened;
DIAG_SUPPRESS_SETNOTUSED_VAR_DEFAULT
static uint32_t g_ui32CurCORELDOTEMPCOTRIMLDO       = 0;
static uint32_t g_ui32CurCORELDOTEMPCOTRIMBuck      = 0;
static uint32_t g_ui32CurMEMLDOACTIVETRIMLDO        = 0;
static bool g_bPostponeTempco                       = false;
static bool g_bTempcoPending                        = false;
static bool bSimoLPAutoSwitch                       = false;
static am_hal_pwrctrl_tempco_range_e g_eTempCoRange = AM_HAL_PWRCTRL_TEMPCO_RANGE_LOW;
#if BOOST_VDDF_FOR_SDIO
static bool g_bVddcBoostedGPU  = false;
static bool g_bVddfBoostedGPU  = false;
static bool g_bVddfBoostedSDIO = false;
static bool g_bDelayForSdio    = false;
static uint32_t g_ui32VddfBoostedStatusSDIO = 0;
#endif

//*****************************************************************************
//
//! Globals
//
//*****************************************************************************

// ****************************************************************************
//
//  vddc_vddf_tempco
//
// ****************************************************************************
static inline void
vddc_vddf_tempco(am_hal_pwrctrl_tempco_range_e eTempCoRange)
{
#if AM_HAL_ENABLE_TEMPCO_VDDC
    int32_t i32TVRGCDiff = 0;
    int32_t i32CORELDOReduce = 0;
    int32_t i32TVRGCReduce = 0;
#endif
#if AM_HAL_ENABLE_TEMPCO_VDDF
    int32_t i32TVRGFDiff = 0;
    int32_t i32TVRGFReduce = 0;
#endif
    int32_t i32PosVal = 0;

    if (g_bOrigTrimsStored && (PWRCTRL->VRSTATUS_b.SIMOBUCKST == PWRCTRL_VRSTATUS_SIMOBUCKST_ACT))
    {
#if !BOOST_VDDF_FOR_SDIO
        if ((PWRCTRL->DEVPWREN_b.PWRENGFX) && (g_bIsPCM1p0Or1p1))
        {
#if AM_HAL_ENABLE_TEMPCO_VDDC
            i32TVRGCDiff = TVRGCVREFTRIM_BOOST_CODE_FOR_GPU;
#endif
#if AM_HAL_ENABLE_TEMPCO_VDDF
            i32TVRGFDiff = TVRGFVREFTRIM_BOOST_CODE_FOR_GPU;
#endif
        }
#else
        if ((PWRCTRL->DEVPWREN_b.PWRENGFX) || (PWRCTRL->DEVPWREN_b.PWRENSDIO0) || (PWRCTRL->DEVPWREN_b.PWRENSDIO1))
        {
#if AM_HAL_ENABLE_TEMPCO_VDDC
            if (PWRCTRL->DEVPWREN_b.PWRENGFX)
            {
                if (g_bIsPCM1p0Or1p1)
                {
                    i32TVRGCDiff = TVRGCVREFTRIM_BOOST_CODE_FOR_GPU;
                }
                else
                {
                    i32TVRGCDiff = 0;
                }
            }
#endif

#if AM_HAL_ENABLE_TEMPCO_VDDF
            if ((PWRCTRL->DEVPWREN_b.PWRENSDIO0) || (PWRCTRL->DEVPWREN_b.PWRENSDIO1))
            {
                if ((g_bIsPCM1p0Or1p1) || (g_bIsPCM2p0Unscreened))
                {
                    i32TVRGFDiff = TVRGFVREFTRIM_BOOST_CODE_FOR_SDIO;
                }
                else
                {
                    i32TVRGFDiff = 0;
                }
            }
            else
            {
                // assert(PWRCTRL->DEVPWREN_b.PWRENGFX == 1);
                if (g_bIsPCM1p0Or1p1)
                {
                    i32TVRGFDiff = TVRGFVREFTRIM_BOOST_CODE_FOR_GPU;
                }
                else
                {
                    i32TVRGFDiff = 0;
                }
            }
#endif
        }
#endif

        switch (eTempCoRange)
        {
            case AM_HAL_PWRCTRL_TEMPCO_RANGE_LOW:
#if AM_HAL_ENABLE_TEMPCO_VDDC
                i32CORELDOReduce = 17;
                i32TVRGCReduce = 35;
#endif
#if AM_HAL_ENABLE_TEMPCO_VDDF
                i32TVRGFReduce = 10;
#endif
                break;

            case AM_HAL_PWRCTRL_TEMPCO_RANGE_MID:
#if AM_HAL_ENABLE_TEMPCO_VDDC
                i32CORELDOReduce = 12;
                i32TVRGCReduce = 20;
#endif
#if AM_HAL_ENABLE_TEMPCO_VDDF
                i32TVRGFReduce = 10;
#endif
                break;

            case AM_HAL_PWRCTRL_TEMPCO_RANGE_HIGH:
#if AM_HAL_ENABLE_TEMPCO_VDDC
                if ( APOLLO5_B0_GE_PCM1P1 || APOLLO5_B1_PCM2P0 || APOLLO5_B2_PCM2P0 )
                {
                    i32CORELDOReduce = CORELDOACTIVETRIM_REDUCE_IN_SIMOBUCK_INIT_B0TRIM3_B1TRIM1;
                }
                else
                {
                    i32CORELDOReduce = CORELDOACTIVETRIM_REDUCE_IN_SIMOBUCK_INIT;
                }
                i32TVRGCReduce = 0;
#endif
#if AM_HAL_ENABLE_TEMPCO_VDDF
                i32TVRGFReduce = 0;
#endif
                break;

            default:
#if AM_HAL_ENABLE_TEMPCO_VDDC
                i32CORELDOReduce = 0;
                i32TVRGCReduce = 0;
#endif
#if AM_HAL_ENABLE_TEMPCO_VDDF
                i32TVRGFReduce = 0;
#endif
                break;
        }

#if AM_HAL_ENABLE_TEMPCO_VDDC
        if (i32CORELDOReduce > 0)
        {
            FINAL_VAL_UDF_CAP_BASE(g_orig_CORELDOACTIVETRIM, i32CORELDOReduce, MCUCTRL, LDOREG1, CORELDOACTIVETRIM);
        }
        else
        {
            i32PosVal = -i32CORELDOReduce;
            FINAL_VAL_OVF_CAP_BASE(g_orig_CORELDOACTIVETRIM, i32PosVal, MCUCTRL, LDOREG1, CORELDOACTIVETRIM);
        }
        if (i32TVRGCReduce - i32TVRGCDiff > 0)
        {
            i32PosVal = i32TVRGCReduce - i32TVRGCDiff;
            FINAL_VAL_UDF_CAP_BASE(g_orig_TVRGCVREFTRIM, i32PosVal, MCUCTRL, VREFGEN2, TVRGCVREFTRIM);
        }
        else
        {
            i32PosVal = -(i32TVRGCReduce - i32TVRGCDiff);
            FINAL_VAL_OVF_CAP_BASE(g_orig_TVRGCVREFTRIM, i32PosVal, MCUCTRL, VREFGEN2, TVRGCVREFTRIM);
        }
#endif
#if AM_HAL_ENABLE_TEMPCO_VDDF
        if (i32TVRGFReduce - i32TVRGFDiff > 0)
        {
            i32PosVal = i32TVRGFReduce - i32TVRGFDiff;
            FINAL_VAL_UDF_CAP_BASE(g_orig_TVRGFVREFTRIM, i32PosVal, MCUCTRL, VREFGEN4, TVRGFVREFTRIM);
        }
        else
        {
            i32PosVal = -(i32TVRGFReduce - i32TVRGFDiff);
            FINAL_VAL_OVF_CAP_BASE(g_orig_TVRGFVREFTRIM, i32PosVal, MCUCTRL, VREFGEN4, TVRGFVREFTRIM);
        }
#endif
    }
}

// ****************************************************************************
//
//  vddc_vddf_tempco_top
//
// ****************************************************************************
static inline void
vddc_vddf_tempco_top(am_hal_pwrctrl_tempco_range_e eTempCoRange)
{
    AM_CRITICAL_BEGIN

    g_eTempCoRange = eTempCoRange;

    if (g_bPostponeTempco)
    {
        g_bTempcoPending = true;
    }
    else
    {
        vddc_vddf_tempco(eTempCoRange);
    }

    AM_CRITICAL_END
}

//*****************************************************************************
//
//! @brief Handle Temperature change request
//!
//! @param psTempCo - pointer to tempco parameter structure with type
//!                   am_hal_spotmgr_tempco_param_t
//!
//! @return SUCCESS or other Failures.
//!
//! @note Setting g_bFrcBuckAct in this function only applies to PCM 1.0/1.1,
//!       for PCM 2.0 it is handled in spotmgr_buck_deepsleep_state_determine().
//
//*****************************************************************************
static uint32_t am_hal_spotmgr_pcm2_0_tempco_update(am_hal_spotmgr_tempco_param_t *psTempCo)
{
    am_hal_pwrctrl_tempco_range_e eTempRange;

    if ((psTempCo->fTemperature < VDDC_VDDF_TEMPCO_THRESHOLD) && (psTempCo->fTemperature >= LOW_LIMIT))
    {
        eTempRange = AM_HAL_PWRCTRL_TEMPCO_RANGE_LOW;
    }
    else if ((psTempCo->fTemperature >= VDDC_VDDF_TEMPCO_THRESHOLD) && (psTempCo->fTemperature < BUCK_LP_TEMP_THRESHOLD))
    {
        eTempRange = AM_HAL_PWRCTRL_TEMPCO_RANGE_MID;
    }
    else if ((psTempCo->fTemperature >= BUCK_LP_TEMP_THRESHOLD) && (psTempCo->fTemperature < HIGH_LIMIT))
    {
        eTempRange = AM_HAL_PWRCTRL_TEMPCO_RANGE_HIGH;
    }
    else
    {
        eTempRange = AM_HAL_PWRCTRL_TEMPCO_OUT_OF_RANGE;
    }

    switch (eTempRange)
    {
        case AM_HAL_PWRCTRL_TEMPCO_RANGE_LOW:
            if (g_bIsPCM2p0 == false)
            {
                g_bFrcBuckAct = false;
            }
            vddc_vddf_tempco_top(AM_HAL_PWRCTRL_TEMPCO_RANGE_LOW);
            psTempCo->fRangeLower = LOW_LIMIT;
            psTempCo->fRangeHigher = VDDC_VDDF_TEMPCO_THRESHOLD;
            break;
        case AM_HAL_PWRCTRL_TEMPCO_RANGE_MID:
            if (g_bIsPCM2p0 == false)
            {
                g_bFrcBuckAct = false;
            }
            vddc_vddf_tempco_top(AM_HAL_PWRCTRL_TEMPCO_RANGE_MID);
            psTempCo->fRangeLower = VDDC_VDDF_TEMPCO_THRESHOLD - TEMP_HYSTERESIS;
            psTempCo->fRangeHigher = BUCK_LP_TEMP_THRESHOLD;
            break;
        case AM_HAL_PWRCTRL_TEMPCO_RANGE_HIGH:
            if (g_bIsPCM2p0 == false)
            {
                g_bFrcBuckAct = true;
            }
            vddc_vddf_tempco_top(AM_HAL_PWRCTRL_TEMPCO_RANGE_HIGH);
            psTempCo->fRangeLower = BUCK_LP_TEMP_THRESHOLD - TEMP_HYSTERESIS;
            psTempCo->fRangeHigher = HIGH_LIMIT;
            break;
        default:
            psTempCo->fRangeLower = 0.0f;
            psTempCo->fRangeHigher = 0.0f;
            return AM_HAL_STATUS_FAIL;
    }

    return AM_HAL_STATUS_SUCCESS;
}

//*****************************************************************************
//
//! @brief Determine the buck state in deepsleep by setting g_bFrcBuckAct
//!
//! @return None.
//!
//! @note This function is only for PCM2.0, not for PCM 1.0/1.1.
//
//*****************************************************************************
static void
spotmgr_buck_deepsleep_state_determine(void)
{
    //
    // This function is only for PCM2.0, not for PCM 1.0/1.1.
    //
    if (g_bIsPCM2p0 == false)
    {
        return;
    }

    //
    // Check temperature range and peripherals power status, if there is any
    // peripheral enabled in deepsleep or temperature range is HIGH, the
    // simobuck must be forced to stay in active mode in deepsleep.
    //
    if (g_eTempCoRange == AM_HAL_PWRCTRL_TEMPCO_RANGE_HIGH)
    {
        g_bFrcBuckAct = true;
        return;
    }
    else
    {
        //
        // Check stimer status and clock source, if it is using either the HFRC,
        // HFRC2 or a GPIO external clock input as the clock source in
        // deepsleep, the simobuck must be forced to stay in active mode in
        // deepsleep.
        //
        if (am_hal_stimer_is_running()                                &&
            (STIMER->STCFG_b.CLKSEL >= STIMER_STCFG_CLKSEL_HFRC_6MHZ) &&
            (STIMER->STCFG_b.CLKSEL <= STIMER_STCFG_CLKSEL_HFRC_375KHZ))
        {
            g_bFrcBuckAct = true;
            return;
        }
        else
        {
            //
            // Check timer status and clock source, if any timer instance is using
            // either the HFRC, HFRC2 or a GPIO external clock input as the clock
            // source in deepsleep, the simobuck must be forced to stay in active
            // mode in deepsleep.
            //
            for (uint32_t ui32TimerNumber = 0; ui32TimerNumber < AM_REG_NUM_TIMERS; ui32TimerNumber++)
            {
                if ((TIMERn(ui32TimerNumber)->CTRL0_b.TMR0EN == TIMER_CTRL0_TMR0EN_EN) &&
                    (TIMER->GLOBEN & (TIMER_GLOBEN_ENB0_EN << ui32TimerNumber))        &&
                    (((TIMERn(ui32TimerNumber)->CTRL0_b.TMR0CLK >= AM_HAL_TIMER_CLOCK_HFRC_DIV4)            &&
                      (TIMERn(ui32TimerNumber)->CTRL0_b.TMR0CLK <= AM_HAL_TIMER_CLOCK_HFRC_DIV4K))          ||
                     ((TIMERn(ui32TimerNumber)->CTRL0_b.TMR0CLK >= AM_HAL_TIMER_CLOCK_HFRC2_125MHz_DIV8)    &&
                      (TIMERn(ui32TimerNumber)->CTRL0_b.TMR0CLK <= AM_HAL_TIMER_CLOCK_HFRC2_125MHz_DIV256)) ||
                     ((TIMERn(ui32TimerNumber)->CTRL0_b.TMR0CLK >= AM_HAL_TIMER_CLOCK_GPIO0)                &&
                      (TIMERn(ui32TimerNumber)->CTRL0_b.TMR0CLK <= AM_HAL_TIMER_CLOCK_GPIO223))))
                {
                    g_bFrcBuckAct = true;
                    return;
                }
            }
            //
            // Set g_bFrcBuckAct to false if all the conditions above are not met.
            //
            g_bFrcBuckAct = false;
        }
    }
}

#if BOOST_VDDF_FOR_SDIO
//*****************************************************************************
//
//! @brief Handle SDIO On sequence for PCM2.0 unscreened parts
//!
//! @param ePeriph - SDIO instance
//!
//! @return NULL
//
//*****************************************************************************
static void
am_hal_spotmgr_pcm2_0_sdio_on_sequence(am_hal_pwrctrl_periph_e ePeriph)
{
    static uint32_t i = 0;
    AM_CRITICAL_BEGIN
    if (!g_bVddfBoostedSDIO)
    {
        //
        // VDDF boost
        //
        if (g_bVddfBoostedGPU)
        {
            FINAL_VAL_OVF_CAP(TVRGFVREFTRIM_BOOST_CODE_FOR_SDIO - TVRGFVREFTRIM_BOOST_CODE_FOR_GPU, MCUCTRL, VREFGEN4, TVRGFVREFTRIM);
        }
        else
        {
            FINAL_VAL_OVF_CAP(TVRGFVREFTRIM_BOOST_CODE_FOR_SDIO, MCUCTRL, VREFGEN4, TVRGFVREFTRIM);
        }
        g_bVddfBoostedSDIO = true;
        g_bDelayForSdio = true;
    }
    //
    // Track boost status for multiple SDIO instances.
    // Just in case one SDIO is doing sdio_on_sequence() while another has performed a full power cycle.
    //
    g_ui32VddfBoostedStatusSDIO |= (1 << ePeriph);
    AM_CRITICAL_END
    //
    // Perform a delay after boosting VDDF for SDIO.
    // Handled the case that 2 threads call sdio_on_sequence at the same time.
    //
    for ( ; i < DELAY_FOR_SDIO_VDDF_BOOST_IN_10US; i++ )
    {
        if ( g_bDelayForSdio )
        {
            am_hal_delay_us(10);
        }
        else
        {
            break;
        }
    }
    g_bDelayForSdio = false;
    i = 0;
}

//*****************************************************************************
//
//! @brief Handle SDIO Off sequence for PCM2.0 unscreened parts
//!
//! @param ePeriph - SDIO instance
//!
//! @return NULL
//
//*****************************************************************************
static void
am_hal_spotmgr_pcm2_0_sdio_off_sequence(am_hal_pwrctrl_periph_e ePeriph)
{
    //
    // Restore power trims
    //
    AM_CRITICAL_BEGIN
    g_ui32VddfBoostedStatusSDIO &= ~(1 << ePeriph);
    if ((g_bVddfBoostedSDIO) &&
        (!PWRCTRL->DEVPWREN_b.PWRENSDIO0) &&
        (!PWRCTRL->DEVPWREN_b.PWRENSDIO1) &&
        (g_ui32VddfBoostedStatusSDIO == 0))
    {
        if (g_bVddfBoostedGPU)
        {
            FINAL_VAL_UDF_CAP(TVRGFVREFTRIM_BOOST_CODE_FOR_SDIO - TVRGFVREFTRIM_BOOST_CODE_FOR_GPU, MCUCTRL, VREFGEN4, TVRGFVREFTRIM);
        }
        else
        {
            FINAL_VAL_UDF_CAP(TVRGFVREFTRIM_BOOST_CODE_FOR_SDIO, MCUCTRL, VREFGEN4, TVRGFVREFTRIM);
        }
        g_bVddfBoostedSDIO = false;
    }
    AM_CRITICAL_END
}
#endif // BOOST_VDDF_FOR_SDIO

//*****************************************************************************
//
//! @brief Handle GPU On sequence for PCM 1.0, PCM 1.1, and PCM2.0
//!
//! @param eGpuState - GPU Power State in am_hal_spotmgr_gpu_state_e type
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
static uint32_t am_hal_spotmgr_pcm2_0_gpu_on_sequence(am_hal_spotmgr_gpu_state_e eState)
{
    // Buck mode
    if (PWRCTRL->VRSTATUS_b.SIMOBUCKST == PWRCTRL_VRSTATUS_SIMOBUCKST_ACT)
    {
        int32_t i32CORELDODiff;
        //
        // coreldo boost
        //
        if (g_bIsPCM1p0Or1p1)
        {
            g_ui32CurCORELDOTEMPCOTRIMBuck = MCUCTRL->LDOREG1_b.CORELDOTEMPCOTRIM;
            MCUCTRL->LDOREG1_b.CORELDOTEMPCOTRIM = 1;
        }
        DIFF_OVF_CAP(i32CORELDODiff, CORELDOTRIM_BOOST_CODE_FOR_GPU, MCUCTRL, LDOREG1, CORELDOACTIVETRIM);
        MCUCTRL->LDOREG1_b.CORELDOACTIVETRIM += i32CORELDODiff;
        //
        // memldo boost
        //
        MCUCTRL->LDOREG2_b.MEMLDOACTIVETRIM = 5;
        //
        // Delay 5us
        //
        am_hal_delay_us(5);
        //
        // VDDF boost
        //
#if !BOOST_VDDF_FOR_SDIO
        if (g_bIsPCM1p0Or1p1)
        {
            FINAL_VAL_OVF_CAP(TVRGFVREFTRIM_BOOST_CODE_FOR_GPU, MCUCTRL, VREFGEN4, TVRGFVREFTRIM);
        }
#else
        if (g_bIsPCM1p0Or1p1)
        {
            AM_CRITICAL_BEGIN
            if (!g_bVddfBoostedGPU)
            {
                if (!g_bVddfBoostedSDIO)
                {
                    FINAL_VAL_OVF_CAP(TVRGFVREFTRIM_BOOST_CODE_FOR_GPU, MCUCTRL, VREFGEN4, TVRGFVREFTRIM);
                }
                g_bVddfBoostedGPU = true;
            }
            AM_CRITICAL_END
        }
#endif
        //
        // Short VDDC to VDDC_LV and VDDS to VDDF
        //
        vddc_to_vddclv_and_vdds_to_vddf_short(true);
        //
        // Delay 10us
        //
        am_hal_delay_us(10);
        //
        // VDDC boost
        //
#if !BOOST_VDDF_FOR_SDIO
        if (g_bIsPCM1p0Or1p1)
        {
            FINAL_VAL_OVF_CAP(TVRGCVREFTRIM_BOOST_CODE_FOR_GPU, MCUCTRL, VREFGEN2, TVRGCVREFTRIM );
            MCUCTRL->D2ASPARE_b.SIMOVDDCBOOST = 1;
        }
#else
        if (g_bIsPCM1p0Or1p1)
        {
            AM_CRITICAL_BEGIN
            if (!g_bVddcBoostedGPU)
            {
                FINAL_VAL_OVF_CAP(TVRGCVREFTRIM_BOOST_CODE_FOR_GPU, MCUCTRL, VREFGEN2, TVRGCVREFTRIM);
                g_bVddcBoostedGPU = true;
            }
            AM_CRITICAL_END
            MCUCTRL->D2ASPARE_b.SIMOVDDCBOOST = 1;
        }
#endif
        if (g_bIsPCM1p0Or1p1)
        {
            //
            // VDDC and VDDCLV Ton updates
            //
            MCUCTRL->SIMOBUCK2_b.VDDCACTLOWTONTRIM = 10;
            MCUCTRL->SIMOBUCK2_b.VDDCACTHIGHTONTRIM = 10;
            MCUCTRL->SIMOBUCK4_b.VDDCLVACTLOWTONTRIM = 8;
            MCUCTRL->SIMOBUCK4_b.VDDCLVACTHIGHTONTRIM = 8;
            //
            // VDDF Ton updates
            //
            if (eState == AM_HAL_SPOTMGR_GPUSTATE_ACTIVE_LP)
            {
                MCUCTRL->SIMOBUCK7_b.VDDFACTLOWTONTRIM = 16;
                MCUCTRL->SIMOBUCK6_b.VDDFACTHIGHTONTRIM = 20;
            }
            else
            {
                MCUCTRL->SIMOBUCK7_b.VDDFACTLOWTONTRIM = 20;
                MCUCTRL->SIMOBUCK6_b.VDDFACTHIGHTONTRIM = 22;
            }
        }
        else
        {
            //
            // VDDC and VDDCLV Ton updates
            //
            MCUCTRL->SIMOBUCK2_b.VDDCACTLOWTONTRIM = 6;
            MCUCTRL->SIMOBUCK2_b.VDDCACTHIGHTONTRIM = 6;
            MCUCTRL->SIMOBUCK4_b.VDDCLVACTLOWTONTRIM = 5;
            MCUCTRL->SIMOBUCK4_b.VDDCLVACTHIGHTONTRIM = 5;
            //
            // VDDF Ton updates
            //
            if (eState == AM_HAL_SPOTMGR_GPUSTATE_ACTIVE_LP)
            {
                MCUCTRL->SIMOBUCK7_b.VDDFACTLOWTONTRIM = 9;
                MCUCTRL->SIMOBUCK6_b.VDDFACTHIGHTONTRIM = 13;
            }
            else
            {
                MCUCTRL->SIMOBUCK7_b.VDDFACTLOWTONTRIM = 13;
                MCUCTRL->SIMOBUCK6_b.VDDFACTHIGHTONTRIM = 19;
            }
        }
        //
        // Remove VDDC and VDDC_LV short and VDDS to VDDF
        //
        vddc_to_vddclv_and_vdds_to_vddf_short(false);
        //
        // Reduce coreldo
        //
        MCUCTRL->LDOREG1_b.CORELDOACTIVETRIM -= i32CORELDODiff;
        //
        // Reduce memldo
        //
        if (!g_bIsB0Pcm1p0)
        {
            MCUCTRL->LDOREG2_b.MEMLDOACTIVETRIM = 1;
        }
        else
        {
            MCUCTRL->LDOREG2_b.MEMLDOACTIVETRIM = 0;
        }
    }
    // LDO mode
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
//! @brief Handle GPU Off sequence for PCM 1.0, PCM 1.1, and PCM2.0
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
static uint32_t am_hal_spotmgr_pcm2_0_gpu_off_sequence()
{
    // Buck mode
    if (PWRCTRL->VRSTATUS_b.SIMOBUCKST == PWRCTRL_VRSTATUS_SIMOBUCKST_ACT)
    {
        int32_t i32CORELDODiff;
        //
        // coreldo boost
        //
        DIFF_OVF_CAP(i32CORELDODiff, CORELDOTRIM_BOOST_CODE_FOR_GPU, MCUCTRL, LDOREG1, CORELDOACTIVETRIM);
        MCUCTRL->LDOREG1_b.CORELDOACTIVETRIM += i32CORELDODiff;
        //
        // memldo boost
        //
        MCUCTRL->LDOREG2_b.MEMLDOACTIVETRIM = 5;
        //
        // Delay 5us
        //
        am_hal_delay_us(5);
        //
        // Short VDDC to VDDC_LV and VDDS to VDDF
        //
        vddc_to_vddclv_and_vdds_to_vddf_short(true);
        //
        // Delay 10us
        //
        am_hal_delay_us(10);
        //
        // Ton updates
        //
        MCUCTRL->SIMOBUCK2_b.VDDCACTLOWTONTRIM = 6;
        MCUCTRL->SIMOBUCK2_b.VDDCACTHIGHTONTRIM = 6;
        MCUCTRL->SIMOBUCK4_b.VDDCLVACTLOWTONTRIM = 5;
        MCUCTRL->SIMOBUCK4_b.VDDCLVACTHIGHTONTRIM = 5;
        MCUCTRL->SIMOBUCK7_b.VDDFACTLOWTONTRIM = 7;
        MCUCTRL->SIMOBUCK6_b.VDDFACTHIGHTONTRIM = 10;
        //
        // Restore power trims
        //
#if !BOOST_VDDF_FOR_SDIO
        if (g_bIsPCM1p0Or1p1)
        {
            FINAL_VAL_UDF_CAP(TVRGFVREFTRIM_BOOST_CODE_FOR_GPU, MCUCTRL, VREFGEN4, TVRGFVREFTRIM);
            FINAL_VAL_UDF_CAP(TVRGCVREFTRIM_BOOST_CODE_FOR_GPU, MCUCTRL, VREFGEN2, TVRGCVREFTRIM);
            MCUCTRL->LDOREG1_b.CORELDOTEMPCOTRIM = g_ui32CurCORELDOTEMPCOTRIMBuck;
            MCUCTRL->D2ASPARE_b.SIMOVDDCBOOST = 0;
        }
#else
        if (g_bIsPCM1p0Or1p1)
        {
            AM_CRITICAL_BEGIN
            if (g_bVddfBoostedGPU)
            {
                if (!g_bVddfBoostedSDIO)
                {
                    FINAL_VAL_UDF_CAP(TVRGFVREFTRIM_BOOST_CODE_FOR_GPU, MCUCTRL, VREFGEN4, TVRGFVREFTRIM);
                }
                g_bVddfBoostedGPU = false;
            }
            if (g_bVddcBoostedGPU)
            {
                FINAL_VAL_UDF_CAP(TVRGCVREFTRIM_BOOST_CODE_FOR_GPU, MCUCTRL, VREFGEN2, TVRGCVREFTRIM);
                g_bVddcBoostedGPU = false;
            }
            AM_CRITICAL_END
            MCUCTRL->LDOREG1_b.CORELDOTEMPCOTRIM = g_ui32CurCORELDOTEMPCOTRIMBuck;
            MCUCTRL->D2ASPARE_b.SIMOVDDCBOOST = 0;
        }
#endif
        MCUCTRL->LDOREG1_b.CORELDOACTIVETRIM -= i32CORELDODiff;
        if (!g_bIsB0Pcm1p0)
        {
            MCUCTRL->LDOREG2_b.MEMLDOACTIVETRIM = 1;
        }
        else
        {
            MCUCTRL->LDOREG2_b.MEMLDOACTIVETRIM = 0;
        }
        //
        // Remove VDDC and VDDC_LV short and VDDS to VDDF
        //
        vddc_to_vddclv_and_vdds_to_vddf_short(false);
    }
    // LDO mode
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

    return AM_HAL_STATUS_SUCCESS;
}



//*****************************************************************************
//
//! @brief Power states update for PCM 1.0, PCM 1.1, and PCM2.0
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
am_hal_spotmgr_pcm2_0_power_state_update(am_hal_spotmgr_stimulus_e eStimulus, bool bOn, void *pArgs)
{
    uint32_t ui32Status = AM_HAL_STATUS_SUCCESS;
    static float fTempStatic = BUCK_LP_TEMP_THRESHOLD + 5.0f; // Default power trims correspond to the temperature range AM_HAL_PWRCTRL_TEMPCO_RANGE_HIGH

    switch (eStimulus)
    {
        case AM_HAL_SPOTMGR_STIM_INIT_STATE:
        {
            //
            // For PCM2.0, need to update the tempco related power trims after enabling SIMOBUCK.
            //
            am_hal_spotmgr_tempco_param_t sTemp;
            sTemp.fTemperature = fTempStatic;
            ui32Status = am_hal_spotmgr_pcm2_0_tempco_update(&sTemp);
            break;
        }
        case AM_HAL_SPOTMGR_STIM_CPU_STATE:
        {
            if (pArgs != NULL)
            {
                am_hal_spotmgr_cpu_state_e eCpuState = *((am_hal_spotmgr_cpu_state_e *)pArgs);
                if (eCpuState == AM_HAL_SPOTMGR_CPUSTATE_SLEEP_DEEP)
                {
                    spotmgr_buck_deepsleep_state_determine();
                }
            }
            break;
        }
        case AM_HAL_SPOTMGR_STIM_GPU_STATE:
        {
            am_hal_spotmgr_gpu_state_e eState = *((am_hal_spotmgr_gpu_state_e*)pArgs);
            if (eState == AM_HAL_SPOTMGR_GPUSTATE_OFF)
            {
                ui32Status = am_hal_spotmgr_pcm2_0_gpu_off_sequence();
            }
            else
            {
                ui32Status = am_hal_spotmgr_pcm2_0_gpu_on_sequence(eState);
            }
            break;
        }
        case AM_HAL_SPOTMGR_STIM_TEMP:
        {
            am_hal_spotmgr_tempco_param_t *psTempCo = (am_hal_spotmgr_tempco_param_t *)pArgs;
            //
            // Invoke am_hal_spotmgr_pcm2_0_tempco_update regardless of SIMOBUCK on or off.
            // When simobuck is off, it only calculates temperature range, fRangeHigher and fRangeLower,
            // but not adjust power trims.
            //
            ui32Status = am_hal_spotmgr_pcm2_0_tempco_update(psTempCo);
            //
            // Save the temperature
            //
            fTempStatic = psTempCo->fTemperature;
            break;
        }
        case AM_HAL_SPOTMGR_STIM_DEVPWR:
#if BOOST_VDDF_FOR_SDIO
            if (g_bIsPCM1p0Or1p1 || g_bIsPCM2p0Unscreened)
            {
                uint32_t ui32PeriphStatus = *(uint32_t*)pArgs;
                if ((ui32PeriphStatus & PWRCTRL_DEVPWRSTATUS_PWRSTSDIO0_Msk) ||
                    (ui32PeriphStatus & PWRCTRL_DEVPWRSTATUS_PWRSTSDIO1_Msk))
                {
                    am_hal_pwrctrl_periph_e ePeriph = (ui32PeriphStatus & PWRCTRL_DEVPWRSTATUS_PWRSTSDIO0_Msk) ?
                                                    AM_HAL_PWRCTRL_PERIPH_SDIO0 : AM_HAL_PWRCTRL_PERIPH_SDIO1;
                    if (bOn)
                    {
                        am_hal_spotmgr_pcm2_0_sdio_on_sequence(ePeriph);
                    }
                    else
                    {
                        am_hal_spotmgr_pcm2_0_sdio_off_sequence(ePeriph);
                    }
                }
            }
#endif
            break;
        case AM_HAL_SPOTMGR_STIM_AUDSSPWR:
            // Nothing to be done for PCM2.0
            break;
        case AM_HAL_SPOTMGR_STIM_MEMPWR:
            // Nothing to be done for PCM2.0
            break;
        case AM_HAL_SPOTMGR_STIM_SSRAMPWR:
            // Nothing to be done for PCM2.0
            break;
        case AM_HAL_SPOTMGR_STIM_BACK_TO_DEFAULT_STATE:
            break;
    }

    return ui32Status;
}

//*****************************************************************************
//
//! @brief Set flag to postpone tempco handling till the function
//!        am_hal_spotmgr_pcm2_0_tempco_pending_handle() is invoked
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t am_hal_spotmgr_pcm2_0_tempco_postpone(void)
{
    g_bPostponeTempco = true;
    return AM_HAL_STATUS_SUCCESS;
}

//*****************************************************************************
//
//! @brief Check for pending tempco operation, execute it if pending, and clear
//!        the blocking flag.
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t am_hal_spotmgr_pcm2_0_tempco_pending_handle(void)
{
    AM_CRITICAL_BEGIN
    if (g_bTempcoPending)
    {
        vddc_vddf_tempco(g_eTempCoRange);
        g_bTempcoPending  = false;
    }
    g_bPostponeTempco = false;
    AM_CRITICAL_END
    return AM_HAL_STATUS_SUCCESS;
}

//*****************************************************************************
//
//! @brief SIMOBUCK initialziation handling at stage just before enabling
//!        SIMOBUCK for PCM 1.0, PCM 1.1, and PCM2.0
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t am_hal_spotmgr_pcm2_0_simobuck_init_bfr_enable(void)
{
    if (g_bOrigTrimsStored)
    {
        FINAL_VAL_UDF_CAP_BASE(g_orig_CORELDOACTIVETRIM, CORELDOACTIVETRIM_REDUCE_IN_SIMOBUCK_INIT_B0TRIM3_B1TRIM1, MCUCTRL, LDOREG1, CORELDOACTIVETRIM);
    }
    return AM_HAL_STATUS_SUCCESS;
}

//*****************************************************************************
//
//! @brief SIMOBUCK initialziation handling at stage just after enabling
//!        SIMOBUCK for PCM 1.0, PCM 1.1, and PCM2.0
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t am_hal_spotmgr_pcm2_0_simobuck_init_aft_enable(void)
{
    am_hal_delay_us(100);
    MCUCTRL->LDOREG2_b.MEMLDOACTIVETRIM = 1;
    MCUCTRL->D2ASPARE_b.MEMLDOREF = 0x2;
    am_hal_delay_us(100);
    //
    // Waiting for SIMOBUCK active
    //
    uint32_t ui32Status;
    ui32Status = am_hal_delay_us_status_check(AM_HAL_PWRCTRL_MAX_WAIT_SIMOBUCK_ACT_US,
                                              (uint32_t) &(PWRCTRL->VRSTATUS),
                                              PWRCTRL_VRSTATUS_SIMOBUCKST_Msk,
                                              (PWRCTRL_VRSTATUS_SIMOBUCKST_ACT << PWRCTRL_VRSTATUS_SIMOBUCKST_Pos),
                                              true);
    //
    // Check for success.
    //
    if (AM_HAL_STATUS_SUCCESS != ui32Status)
    {
        return ui32Status;
    }
    else
    {
        //
        // Initialise MCU power state after enabling SIMOBUCK
        //
        return am_hal_spotmgr_pcm2_0_power_state_update(AM_HAL_SPOTMGR_STIM_INIT_STATE, false, NULL);
    }
}

#if NO_TEMPSENSE_IN_DEEPSLEEP
//*****************************************************************************
//
//! @brief Prepare SPOT manager for suspended tempco during deep sleep for
//!        PCM 1.0, PCM 1.1, and PCM2.0
//!
//! @return SUCCESS or other Failures.
//!
//! Note: This handling also handle tempco suspend for versions before PCM2.0
//
//*****************************************************************************
#if !BOOST_VDDF_FOR_SDIO
uint32_t am_hal_spotmgr_pcm2_0_tempco_suspend(void)
{
    //
    // Set g_eTempCoRange to AM_HAL_PWRCTRL_TEMPCO_RANGE_HIGH to align with VDDC and VDDF values.
    //
    g_eTempCoRange = AM_HAL_PWRCTRL_TEMPCO_RANGE_HIGH;

    // Restore VDDC and VDDF settings before deepsleep to allow application to
    // suspend tempsensing during deeplseep.
    if (g_bOrigTrimsStored && (PWRCTRL->VRSTATUS_b.SIMOBUCKST == PWRCTRL_VRSTATUS_SIMOBUCKST_ACT))
    {
        if ((PWRCTRL->DEVPWREN_b.PWRENGFX) && (g_bIsPCM1p0Or1p1))
        {
            //
            // Restore VDDF, and boost 15 codes for GPU
            //
            FINAL_VAL_OVF_CAP_BASE(g_orig_TVRGFVREFTRIM, TVRGFVREFTRIM_BOOST_CODE_FOR_GPU, MCUCTRL, VREFGEN4, TVRGFVREFTRIM);
            //
            // Restore VDDC, and boost 9 codes for GPU
            //
            FINAL_VAL_OVF_CAP_BASE(g_orig_TVRGCVREFTRIM, TVRGCVREFTRIM_BOOST_CODE_FOR_GPU, MCUCTRL, VREFGEN2, TVRGCVREFTRIM);
            //
            // Delay 15 us
            //
            am_hal_delay_us(15);
        }
        else
        {
            //
            // Restore VDDF
            //
            MCUCTRL->VREFGEN4_b.TVRGFVREFTRIM = g_orig_TVRGFVREFTRIM;
            //
            // Restore VDDC
            //
            MCUCTRL->VREFGEN2_b.TVRGCVREFTRIM = g_orig_TVRGCVREFTRIM;
            //
            // Set coreldo below simobuck VDDC
            //
            if ( g_bIsB0PCM1p1OrNewer || g_bIsPCM2p0 )
            {
                FINAL_VAL_UDF_CAP_BASE(g_orig_CORELDOACTIVETRIM, CORELDOACTIVETRIM_REDUCE_IN_SIMOBUCK_INIT_B0TRIM3_B1TRIM1, MCUCTRL, LDOREG1, CORELDOACTIVETRIM);
            }
            else
            {
                FINAL_VAL_UDF_CAP_BASE(g_orig_CORELDOACTIVETRIM, CORELDOACTIVETRIM_REDUCE_IN_SIMOBUCK_INIT, MCUCTRL, LDOREG1, CORELDOACTIVETRIM);
            }
            //
            // Delay 15 us
            //
            am_hal_delay_us(15);
        }
    }
    return AM_HAL_STATUS_SUCCESS;
}
#else
uint32_t am_hal_spotmgr_pcm2_0_tempco_suspend(void)
{
    //
    // Set g_eTempCoRange to AM_HAL_PWRCTRL_TEMPCO_RANGE_HIGH to align with VDDC and VDDF values.
    //
    g_eTempCoRange = AM_HAL_PWRCTRL_TEMPCO_RANGE_HIGH;

    // Restore VDDC and VDDF settings before deepsleep to allow application to
    // suspend tempsensing during deeplseep.
    if (g_bOrigTrimsStored && (PWRCTRL->VRSTATUS_b.SIMOBUCKST == PWRCTRL_VRSTATUS_SIMOBUCKST_ACT))
    {
        //
        // Restore VDDF
        //
        if (g_bVddfBoostedSDIO || g_bVddfBoostedGPU)
        {
            if (g_bVddfBoostedSDIO)
            {
                if (g_bIsPCM1p0Or1p1 || g_bIsPCM2p0Unscreened)
                {
                    FINAL_VAL_OVF_CAP_BASE(g_orig_TVRGFVREFTRIM, TVRGFVREFTRIM_BOOST_CODE_FOR_SDIO, MCUCTRL, VREFGEN4, TVRGFVREFTRIM);
                }
                else
                {
                    MCUCTRL->VREFGEN4_b.TVRGFVREFTRIM = g_orig_TVRGFVREFTRIM;
                }
            }
            else
            {
                // assert(PWRCTRL->DEVPWREN_b.PWRENGFX == 1);
                if (g_bIsPCM1p0Or1p1)
                {
                    FINAL_VAL_OVF_CAP_BASE(g_orig_TVRGFVREFTRIM, TVRGFVREFTRIM_BOOST_CODE_FOR_GPU, MCUCTRL, VREFGEN4, TVRGFVREFTRIM);
                }
                else
                {
                    MCUCTRL->VREFGEN4_b.TVRGFVREFTRIM = g_orig_TVRGFVREFTRIM;
                }
            }
        }
        else
        {
            MCUCTRL->VREFGEN4_b.TVRGFVREFTRIM = g_orig_TVRGFVREFTRIM;
        }

        //
        // Restore VDDC
        //
        if (g_bVddcBoostedGPU)
        {
            if (g_bIsPCM1p0Or1p1)
            {
                FINAL_VAL_OVF_CAP_BASE(g_orig_TVRGCVREFTRIM, TVRGCVREFTRIM_BOOST_CODE_FOR_GPU, MCUCTRL, VREFGEN2, TVRGCVREFTRIM);
            }
            else
            {
                MCUCTRL->VREFGEN2_b.TVRGCVREFTRIM = g_orig_TVRGCVREFTRIM;
            }
        }
        else
        {
            MCUCTRL->VREFGEN2_b.TVRGCVREFTRIM = g_orig_TVRGCVREFTRIM;
        }

        //
        // Set coreldo below simobuck VDDC
        //
        if (g_bIsB0PCM1p1OrNewer || g_bIsPCM2p0)
        {
            FINAL_VAL_UDF_CAP_BASE(g_orig_CORELDOACTIVETRIM, CORELDOACTIVETRIM_REDUCE_IN_SIMOBUCK_INIT_B0TRIM3_B1TRIM1, MCUCTRL, LDOREG1, CORELDOACTIVETRIM);
        }
        else
        {
            FINAL_VAL_UDF_CAP_BASE(g_orig_CORELDOACTIVETRIM, CORELDOACTIVETRIM_REDUCE_IN_SIMOBUCK_INIT, MCUCTRL, LDOREG1, CORELDOACTIVETRIM);
        }

        //
        // Delay 15 us
        //
        am_hal_delay_us(15);
    }
    return AM_HAL_STATUS_SUCCESS;
}
#endif
#endif

#if AM_HAL_PWRCTRL_SIMOLP_AUTOSWITCH
//*****************************************************************************
//
//! @brief Initialize registers for SIMOBUCK LP auto switch  for PCM 1.0, PCM1.1,
//! and PCM2.0
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t am_hal_spotmgr_pcm2_0_simobuck_lp_autosw_init(void)
{
    // These settings decide at what loadcurrent Buck transitions from LP to active automatically.
    PWRCTRL->TONCNTRCTRL_b.CLKDIV = 0;
    PWRCTRL->TONCNTRCTRL_b.FCNT = 1000;
    PWRCTRL->LPOVRHYSTCNT_b.LPOVRHYSTCNT = 0;
    PWRCTRL->LPOVRTHRESHVDDS_b.LPOVRTHRESHVDDS = 800;
    PWRCTRL->LPOVRTHRESHVDDF_b.LPOVRTHRESHVDDF = 450;
    PWRCTRL->LPOVRTHRESHVDDC_b.LPOVRTHRESHVDDC = 600;
    PWRCTRL->LPOVRTHRESHVDDCLV_b.LPOVRTHRESHVDDCLV = 250;
    // This setting ensures that if buck is in LP mode upon entry to deepsleep, it will transition to active
    // if the load increases slowly and stay in active for the rest of the time
    PWRCTRL->TONCNTRCTRL_b.LPMODESWOVR = 0;
    PWRCTRL->TONCNTRCTRL_b.ENABLELPOVR = 0;

    return AM_HAL_STATUS_SUCCESS;
}

//*****************************************************************************
//
//! @brief Enable SIMOBUCK LP auto switch for PCM 1.0, PCM 1.1, and PCM2.0
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t am_hal_spotmgr_pcm2_0_simobuck_lp_autosw_enable(void)
{
    //
    // Toggle overrides to make sure buck goes to LP regardless of the state from last time
    //
    PWRCTRL->TONCNTRCTRL |= (PWRCTRL_TONCNTRCTRL_LPMODESWOVR_Msk | PWRCTRL_TONCNTRCTRL_ENABLELPOVR_Msk);
    bSimoLPAutoSwitch = true;
    return  AM_HAL_STATUS_SUCCESS;
}

//*****************************************************************************
//
//! @brief Disable SIMOBUCK LP auto switch for PCM 1.0, PCM 1.1, and PCM2.0
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t am_hal_spotmgr_pcm2_0_simobuck_lp_autosw_disable(void)
{
    if (bSimoLPAutoSwitch)
    {
        PWRCTRL->TONCNTRCTRL &= ~(PWRCTRL_TONCNTRCTRL_LPMODESWOVR_Msk | PWRCTRL_TONCNTRCTRL_ENABLELPOVR_Msk);
        bSimoLPAutoSwitch = false;
    }
    return  AM_HAL_STATUS_SUCCESS;
}
#endif


//*****************************************************************************
//
//! @brief SPOT manager init for PCM 1.0, PCM 1.1, and PCM2.0
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t
am_hal_spotmgr_pcm2_0_init(void)
{
    uint32_t ui32Status = AM_HAL_STATUS_SUCCESS;

    //
    // Populate boolean for specific trim versions
    //
    g_bIsB0Pcm1p0 = APOLLO5_B0_PCM1P0;
    g_bIsPCM1p0Or1p1 = APOLLO5_B0_PCM1P0 || APOLLO5_B0_PCM1P1 || APOLLO5_B1_PCM1P1;
    //
    // All B1-PCM2.0 parts are unscreened. For B2-PCM2.0, determine if it is an unscreened part through datecode.
    //
    g_bIsPCM2p0Unscreened = APOLLO5_B1_PCM2P0 || (APOLLO5_B2_PCM2P0 && (!SDIO_SCREEN_PARTS_FOR_B2));

    //
    // Powers up ACRG bias current (required when forcing ANALDO into active mode when entering Sleep mode).
    //
    MCUCTRL->ACRG_b.ACRGPWD = 0;
    MCUCTRL->ACRG_b.ACRGSWE = 1;
    //
    // Forces ANALDO into active mode when entering Sleep mode.
    //
    MCUCTRL->VRCTRL_b.ANALDOACTIVE = 1;
    MCUCTRL->VRCTRL_b.ANALDOPDNB = 1;
    MCUCTRL->VRCTRL_b.ANALDOOVER = 1;

    return ui32Status;
}

//*****************************************************************************
//
//! @brief Reset power state to POR default for PCM 1.0, PCM 1.1, and PCM2.0
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t am_hal_spotmgr_pcm2_0_default_reset(void)
{
#if BOOST_VDDF_FOR_SDIO
    if (g_bIsPCM1p0Or1p1 || g_bIsPCM2p0Unscreened)
    {
        bool bEnabled = false;
        //
        // Check SDIO0 status, if it is ON, return failure.
        //
        if (am_hal_pwrctrl_periph_enabled(AM_HAL_PWRCTRL_PERIPH_SDIO0, &bEnabled) == AM_HAL_STATUS_SUCCESS)
        {
            if (bEnabled)
            {
                return AM_HAL_STATUS_FAIL;
            }
        }
        else
        {
            return AM_HAL_STATUS_FAIL;
        }
        //
        // Check SDIO1 status, if it is ON, return failure.
        //
        if (am_hal_pwrctrl_periph_enabled(AM_HAL_PWRCTRL_PERIPH_SDIO1, &bEnabled) == AM_HAL_STATUS_SUCCESS)
        {
            if (bEnabled)
            {
                return AM_HAL_STATUS_FAIL;
            }
        }
        else
        {
            return AM_HAL_STATUS_FAIL;
        }
    }
#endif

    return AM_HAL_STATUS_SUCCESS;
}

#endif

//*****************************************************************************
//
// End Doxygen group.
//! @}
//
//*****************************************************************************
