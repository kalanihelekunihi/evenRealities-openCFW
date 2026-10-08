// ****************************************************************************
//
//! @file am_hal_spotmgr.c
//!
//! @brief SPOT manager functions that manage power states.
//!
//! @addtogroup spotmgr5b_ap510 SPOTMGR - SPOT Manager
//! @ingroup apollo510_hal
//! @{
///!
//! Purpose: This module provides SPOT manager functionality for Apollo5
//! devices, supporting power state management, peripheral control, and
//! system optimization across multiple PCM versions.
//!
//! @section hal_spotmgr_features Key Features
//!
//! 1. @b Power @b State @b Management: Control and monitor system power states.
//! 2. @b Stimulus @b Handling: Respond to hardware and software power events.
//! 3. @b Hardware @b Integration: Interface with SIMOBUCK, LDO, and other power domains.
//! 4. @b Version @b Support: Handle multiple PCM (Power Control Module) versions.
//!
//! @section hal_spotmgr_functionality Functionality
//!
//! - Initialize and configure SPOT manager state
//! - Handle power state transitions and stimulus events
//! - Integrate with hardware power domains and peripherals
//! - Support for timer-based power management
//! - Provide hooks for custom power management logic
//!
//! @section hal_spotmgr_usage Usage
//!
//! 1. Initialize SPOT manager and configure callbacks
//! 2. Handle power state transitions in response to events
//! 3. Integrate with board and application power management
//! 4. Extend with custom logic as needed
//!
//! @section hal_spotmgr_configuration Configuration
//!
//! - @b PCM @b Version: Select appropriate PCM version for hardware
//! - @b Callbacks: Configure function pointers for custom handling
//! - @b Timer: Set up timer-based power management if required
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

//*****************************************************************************
//
//! Defines
//
//*****************************************************************************

//
//! Function pointer type for SPOT manager functions
//
typedef uint32_t (*am_hal_spotmgr_pcm_init_t)(void);
typedef uint32_t (*am_hal_spotmgr_pcm_power_state_update_t)(am_hal_spotmgr_stimulus_e eStimulus, bool bOn, void *pArgs);
typedef uint32_t (*am_hal_spotmgr_default_reset_t)(void);
typedef uint32_t (*am_hal_spotmgr_tempco_postpone_set_t)(void);
typedef uint32_t (*am_hal_spotmgr_tempco_pending_handle_t)(void);
typedef uint32_t (*am_hal_spotmgr_simobuck_init_bfr_ovr_t)(void);
typedef uint32_t (*am_hal_spotmgr_simobuck_init_bfr_enable_t)(void);
typedef uint32_t (*am_hal_spotmgr_simobuck_init_aft_enable_t)(void);
typedef uint32_t (*am_hal_spotmgr_tempco_suspend_t)(void);
typedef uint32_t (*am_hal_spotmgr_ton_config_init_t)(void);
typedef uint32_t (*am_hal_spotmgr_ton_config_update_t)(bool bGpuOn, am_hal_pwrctrl_gpu_mode_e eGpuSt);
typedef uint32_t (*am_hal_spotmgr_power_setting_aft_lptohp_t)(void);
typedef void     (*am_hal_spotmgr_timer_interrupt_service_t)(void);
typedef uint32_t (*am_hal_spotmgr_simobuck_lp_autosw_init_t)(void);
typedef uint32_t (*am_hal_spotmgr_simobuck_lp_autosw_enable_t)(void);
typedef uint32_t (*am_hal_spotmgr_simobuck_lp_autosw_disable_t)(void);

//
//! SPOT manager state data structure
//
typedef struct
{
    // SPOT Manager Initialization
    // Applicable PCM version: ALL
    am_hal_spotmgr_pcm_init_t pfnSpotmgrInit;

    // SPOT Manager Power State Update
    // Applicable PCM version: ALL
    am_hal_spotmgr_pcm_power_state_update_t pfnSpotmgrPSUpdate;

    // Restore power state to POR default
    // Applicable PCM version: 2.1
    am_hal_spotmgr_default_reset_t pfnSpotMgrDefaultRst;

    // Postpone Tempco triggered changes when peripheral On/Off Sequence is
    // in progress
    // Applicable PCM version: 2.0, 1.1, 1.0
    am_hal_spotmgr_tempco_postpone_set_t pfnSpotMgrTempcoPostponeSet;
    am_hal_spotmgr_tempco_pending_handle_t pfnSpotMgrTempcoPendingHandle;

    // SIMOBUCK initialization handling just before overriding LDO and SIMOBUCK
    // enable
    // Applicable PCM version: 2.1
    am_hal_spotmgr_simobuck_init_bfr_ovr_t pfnSpotMgrSimobuckInitBfrOvr;

    // SIMOBUCK initialization handlings just before/after enabling SIMOBUCK
    // Applicable PCM version: 2.1, 2.0, 1.1, 1.0, 0.7
    am_hal_spotmgr_simobuck_init_bfr_enable_t pfnSpotMgrSimobuckInitBfrEnable;
    am_hal_spotmgr_simobuck_init_aft_enable_t pfnSpotMgrSimobuckInitAftEnable;

    // Ton Config handlings for earlier PCM versions
    // Applicable PCM version: 0.7
    am_hal_spotmgr_ton_config_init_t pfnTonConfigInit;
    am_hal_spotmgr_ton_config_update_t pfnTonConfigUpdate;

    // Power handling after LP to HP transition
    // Applicable PCM version: 2.1, 2.2
    am_hal_spotmgr_power_setting_aft_lptohp_t pfnSpotMgrPwrSetAftLpToHp;

    // Spotmgr timer interrupt service
    // Applicable PCM version: 2.1, 2.2
    am_hal_spotmgr_timer_interrupt_service_t pfnTimerIntService;

#if NO_TEMPSENSE_IN_DEEPSLEEP
    // Pre-DeepSleep handling to allow temperature sensing activity to be
    // suspended after deep sleep is entered
    // Applicable PCM version: 2.1, 2.0, 1.1, 1.0, 0.7
    am_hal_spotmgr_tempco_suspend_t pfnSpotMgrTempcoSuspend;
#endif

#if AM_HAL_PWRCTRL_SIMOLP_AUTOSWITCH
    // SIMOBUCK LP autoswitch feature control handling
    // Applicable PCM version: 2.0, 1.1, 1.0
    am_hal_spotmgr_simobuck_lp_autosw_init_t pfnSimobuckLpAutoSwInit;
    am_hal_spotmgr_simobuck_lp_autosw_enable_t pfnSimobuckLpAutoSwEnable;
    am_hal_spotmgr_simobuck_lp_autosw_disable_t pfnSimobuckLpAutoSwDisable;
#endif

} am_hal_spotmgr_state_t;

//*****************************************************************************
//
//! Global Variables
//
//*****************************************************************************
//! Trim Version booleans for optimization of trim version eval
bool g_bIsPCM2p1;
bool g_bIsPCM1p0OrPCM1p1;
bool g_bIsB0PCM1p1OrNewer;
bool g_bIsPCM2p0;
bool g_bIsPCM2p2OrNewer;
bool g_bIsPCM2p1WoPatch;
bool g_bCallPcm2p0Spotmgr;

//! Applicable PCM version: 2.1 2.2
//! Flag to override Vddcaor and Vddcpu
bool g_bVddcaorVddcpuOverride = false;

//! Applicable PCM version: 2.1, 2.2
//! Flag for current temperature is less than 50C
bool g_bTempLessThan50C = true;

//! Applicable PCM version: 2.1, 2.2
//! Flag to clear or set PWRSWVDDCAOROVERRIDE and PWRSWVDDCPUOVERRIDE when
//! switching between HP and deepsleep
bool g_bHpToDeepSleep = false;

//! Applicable PCM version: 2.1, 2.2
//! Flag for setting VDDF LP minus offset trim to reduce VDDF when entering
//! deepsleep from LP mode.
bool g_bVddfLpMinusForLp = false;

//! Applicable PCM version: 2.1, 2.2
//! The flag indicates MCU LP to HP switching is ongoing
bool g_bSwitchingToHp = false;

//! Applicable PCM version: 2.1, 2.2
//! This table will be populated with SPOT manager related INFO1 values and
//! will be used for easy lookup after OTP is powered down.
am_hal_spotmgr_info1_regs_t g_sSpotMgrINFO1regs;

//! SPOT manager profile
am_hal_spotmgr_profile_t g_sSpotMgrProfile = {.PROFILE = 0};

//*****************************************************************************
//
//! Static Variables
//
//*****************************************************************************
static am_hal_spotmgr_state_t g_sSpotMgr;

//*****************************************************************************
//
//! Function for initializing the timer for SPOT manager.
//
//*****************************************************************************
void
am_hal_spotmgr_timer_init(void)
{
    //
    // Disable the timer.
    //
    TIMERn(AM_HAL_INTERNAL_TIMER_NUM_A)->CTRL0_b.TMR0EN = 0;
    //
    // Apply the settings.
    //
    TIMERn(AM_HAL_INTERNAL_TIMER_NUM_A)->CTRL0 = _VAL2FLD(TIMER_CTRL0_TMR0CLK,     AM_HAL_TIMER_CLOCK_HFRC_DIV16)  |
                                                 _VAL2FLD(TIMER_CTRL0_TMR0FN,      AM_HAL_TIMER_FN_EDGE)           |
                                                 _VAL2FLD(TIMER_CTRL0_TMR0POL1,    false)                          |
                                                 _VAL2FLD(TIMER_CTRL0_TMR0POL0,    false)                          |
                                                 _VAL2FLD(TIMER_CTRL0_TMR0TMODE,   AM_HAL_TIMER_TRIGGER_DIS)       |
                                                 _VAL2FLD(TIMER_CTRL0_TMR0LMT,     0)                              |
                                                 _VAL2FLD(TIMER_CTRL0_TMR0EN,      0);
    TIMERn(AM_HAL_INTERNAL_TIMER_NUM_A)->MODE0 = _VAL2FLD(TIMER_MODE0_TMR0TRIGSEL, AM_HAL_TIMER_TRIGGER_TMR0_OUT1);
    TIMERn(AM_HAL_INTERNAL_TIMER_NUM_A)->TMR0CMP0 = 0xFFFFFFFF;
    TIMERn(AM_HAL_INTERNAL_TIMER_NUM_A)->TMR0CMP1 = 0xFFFFFFFF;
    //
    // Clear the timer Interrupt
    //
    TIMER->INTCLR = (uint32_t) AM_HAL_TIMER_MASK(AM_HAL_INTERNAL_TIMER_NUM_A, AM_HAL_TIMER_COMPARE_BOTH);
    //
    // Enable the timer Interrupt.
    //
    TIMER->INTEN |= (uint32_t) AM_HAL_TIMER_MASK(AM_HAL_INTERNAL_TIMER_NUM_A, AM_HAL_TIMER_COMPARE0);
}

//*****************************************************************************
//
//! Function for starting the timer for SPOT manager.
//
//*****************************************************************************
void
am_hal_spotmgr_timer_start(uint32_t ui32TimerDelayInUs)
{
    //
    // Request clock
    //
    am_hal_clkmgr_clock_request(AM_HAL_CLKMGR_CLK_ID_HFRC, (am_hal_clkmgr_user_id_e)(AM_HAL_CLKMGR_USER_ID_TIMER0 + AM_HAL_INTERNAL_TIMER_NUM_A));
    //
    //  Set timer compare value
    //
    TIMERn(AM_HAL_INTERNAL_TIMER_NUM_A)->TMR0CMP0 = ui32TimerDelayInUs * (AM_HAL_CLKGEN_FREQ_MAX_MHZ / 16);
    //
    // Toggle the clear bit (required by the hardware), and then enable the timer.
    //
    TIMER->GLOBEN |= 1UL <<  AM_HAL_INTERNAL_TIMER_NUM_A;
    TIMERn(AM_HAL_INTERNAL_TIMER_NUM_A)->CTRL0_b.TMR0CLR = 1;
    TIMERn(AM_HAL_INTERNAL_TIMER_NUM_A)->CTRL0_b.TMR0CLR = 0;
    //
    // Set the timer interrupt
    //
    NVIC->ISER[(TIMER0_IRQn + AM_HAL_INTERNAL_TIMER_NUM_A) / 32] = (1 << ((TIMER0_IRQn + AM_HAL_INTERNAL_TIMER_NUM_A) % 32));
    //
    // Enable the timer
    //
    TIMERn(AM_HAL_INTERNAL_TIMER_NUM_A)->CTRL0_b.TMR0EN = 1;
}

//*****************************************************************************
//
//! Function for restarting the timer for SPOT manager.
//
//*****************************************************************************
void
am_hal_spotmgr_timer_restart(uint32_t ui32TimerDelayInUs)
{
    //
    // Disable the timer, then toggle the clear bit
    //
    TIMERn(AM_HAL_INTERNAL_TIMER_NUM_A)->CTRL0_b.TMR0EN  = 0;
    TIMERn(AM_HAL_INTERNAL_TIMER_NUM_A)->CTRL0_b.TMR0CLR = 1;
    TIMERn(AM_HAL_INTERNAL_TIMER_NUM_A)->CTRL0_b.TMR0CLR = 0;
    //
    //  Set timer compare value
    //
    TIMERn(AM_HAL_INTERNAL_TIMER_NUM_A)->TMR0CMP0 = ui32TimerDelayInUs * (AM_HAL_CLKGEN_FREQ_MAX_MHZ / 16);
    //
    // clear the timer interrupt status
    //
    TIMER->INTCLR = (uint32_t) AM_HAL_TIMER_MASK(AM_HAL_INTERNAL_TIMER_NUM_A, AM_HAL_TIMER_COMPARE_BOTH);
    //
    // Clear pending NVIC interrupt for the timer-specific IRQ.
    //
    NVIC->ICPR[(((uint32_t)TIMER0_IRQn + AM_HAL_INTERNAL_TIMER_NUM_A) >> 5UL)] = (uint32_t)(1UL << (((uint32_t)TIMER0_IRQn + AM_HAL_INTERNAL_TIMER_NUM_A) & 0x1FUL));
    //
    // Enable the timer
    //
    TIMERn(AM_HAL_INTERNAL_TIMER_NUM_A)->CTRL0_b.TMR0EN  = 1;
}

//*****************************************************************************
//
//! Function for stopping the timer for SPOT manager.
//
//*****************************************************************************
void
am_hal_spotmgr_timer_stop(void)
{
    //
    // Deinit the timer
    //
    TIMERn(AM_HAL_INTERNAL_TIMER_NUM_A)->CTRL0_b.TMR0EN  = 0;
    TIMER->GLOBEN &= ~(1UL <<  AM_HAL_INTERNAL_TIMER_NUM_A);
    //
    // Release clock
    //
    am_hal_clkmgr_clock_release(AM_HAL_CLKMGR_CLK_ID_HFRC, (am_hal_clkmgr_user_id_e)(AM_HAL_CLKMGR_USER_ID_TIMER0 + AM_HAL_INTERNAL_TIMER_NUM_A));
    //
    // Disable the timer interrupt
    //
    NVIC->ICER[(TIMER0_IRQn + AM_HAL_INTERNAL_TIMER_NUM_A) / 32] = (1 << ((TIMER0_IRQn + AM_HAL_INTERNAL_TIMER_NUM_A) % 32));
    //
    // clear the timer interrupt status
    //
    TIMER->INTCLR = (uint32_t) AM_HAL_TIMER_MASK(AM_HAL_INTERNAL_TIMER_NUM_A, AM_HAL_TIMER_COMPARE_BOTH);
    //
    // Flush APB writes.
    //
    am_hal_sysctrl_sysbus_write_flush();
    //
    // Clear pending NVIC interrupt for the timer-specific IRQ.
    //
    NVIC->ICPR[(((uint32_t)TIMER0_IRQn + AM_HAL_INTERNAL_TIMER_NUM_A) >> 5UL)] = (uint32_t)(1UL << (((uint32_t)TIMER0_IRQn + AM_HAL_INTERNAL_TIMER_NUM_A) & 0x1FUL));
}

//*****************************************************************************
//
//! @brief Power states update
//!        This API should be called before turning things on and after turning
//!        things off, or before switching to high performance mode and after
//!        switching to low power mode, or when temperature range is changed.
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
am_hal_spotmgr_power_state_update(am_hal_spotmgr_stimulus_e eStimulus, bool bOn, void *pArgs)
{
    if (g_sSpotMgr.pfnSpotmgrPSUpdate)
    {
        return g_sSpotMgr.pfnSpotmgrPSUpdate(eStimulus, bOn, pArgs);
    }
    return AM_HAL_STATUS_SUCCESS;
}

//*****************************************************************************
//
//! @brief Set flag to postpone tempco handling till the function
//!        am_hal_spotmgr_pcm2_0_tempco_pending_handler() is invoked
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t am_hal_spotmgr_tempco_postpone(void)
{
    if (g_sSpotMgr.pfnSpotMgrTempcoPostponeSet)
    {
        return g_sSpotMgr.pfnSpotMgrTempcoPostponeSet();
    }
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
uint32_t am_hal_spotmgr_tempco_pending_handle(void)
{
    if (g_sSpotMgr.pfnSpotMgrTempcoPendingHandle)
    {
        return g_sSpotMgr.pfnSpotMgrTempcoPendingHandle();
    }
    return AM_HAL_STATUS_SUCCESS;
}

//*****************************************************************************
//
//! @brief Restore power state to POR default
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t am_hal_spotmgr_default_reset(void)
{
    if (g_sSpotMgr.pfnSpotMgrDefaultRst)
    {
        return g_sSpotMgr.pfnSpotMgrDefaultRst();
    }
    return AM_HAL_STATUS_SUCCESS;
}

//*****************************************************************************
//
//! @brief SIMOBUCK initialziation handling at stage just before overriding LDO
//!        and SIMOBUCK enable.
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t am_hal_spotmgr_simobuck_init_bfr_ovr(void)
{
    if (g_sSpotMgr.pfnSpotMgrSimobuckInitBfrOvr)
    {
        return g_sSpotMgr.pfnSpotMgrSimobuckInitBfrOvr();
    }
    return AM_HAL_STATUS_SUCCESS;
}

//*****************************************************************************
//
//! @brief SIMOBUCK initialziation handling at stage just before enabling
//!        SIMOBUCK
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t am_hal_spotmgr_simobuck_init_bfr_enable(void)
{
    if (g_sSpotMgr.pfnSpotMgrSimobuckInitBfrEnable)
    {
        return g_sSpotMgr.pfnSpotMgrSimobuckInitBfrEnable();
    }
    return AM_HAL_STATUS_SUCCESS;
}

//*****************************************************************************
//
//! @brief SIMOBUCK initialziation handling at stage just after enabling
//!        SIMOBUCK
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t am_hal_spotmgr_simobuck_init_aft_enable(void)
{
    if (g_sSpotMgr.pfnSpotMgrSimobuckInitAftEnable)
    {
        return g_sSpotMgr.pfnSpotMgrSimobuckInitAftEnable();
    }
    return AM_HAL_STATUS_SUCCESS;
}

//*****************************************************************************
//
//! Timer interrupt service for spotmgr
//
//*****************************************************************************
void
am_hal_spotmgr_boost_timer_interrupt_service(void)
{
    if (g_sSpotMgr.pfnTimerIntService)
    {
        g_sSpotMgr.pfnTimerIntService();
    }
}

#if NO_TEMPSENSE_IN_DEEPSLEEP
//*****************************************************************************
//
//! @brief Prepare SPOT manager for suspended tempco during deep sleep
//!
//! @return SUCCESS or other Failures.
//!
//! This API is to be called before entering deepsleep if there is no handling
//! to execute temperature sensing periodically after the deepsleep is entered.
//
//*****************************************************************************
uint32_t am_hal_spotmgr_tempco_suspend(void)
{
    if (g_sSpotMgr.pfnSpotMgrTempcoSuspend)
    {
        return g_sSpotMgr.pfnSpotMgrTempcoSuspend();
    }
    return AM_HAL_STATUS_SUCCESS;
}
#endif

//*****************************************************************************
//
//! @brief Intitialize TON Config hanlding
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t am_hal_spotmgr_ton_config_init(void)
{
    if (g_sSpotMgr.pfnTonConfigInit)
    {
        return g_sSpotMgr.pfnTonConfigInit();
    }
    return AM_HAL_STATUS_SUCCESS;
}

//*****************************************************************************
//
//! @brief Update Ton Config
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t am_hal_spotmgr_ton_config_update(bool bGpuOn, am_hal_pwrctrl_gpu_mode_e eGpuSt)
{
    if (g_sSpotMgr.pfnTonConfigUpdate)
    {
        return g_sSpotMgr.pfnTonConfigUpdate(bGpuOn, eGpuSt);
    }
    return AM_HAL_STATUS_SUCCESS;
}

//*****************************************************************************
//
//! @brief Update Ton Config
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t am_hal_spotmgr_post_lptohp_handle()
{
    if (g_sSpotMgr.pfnSpotMgrPwrSetAftLpToHp)
    {
        return g_sSpotMgr.pfnSpotMgrPwrSetAftLpToHp();
    }
    return AM_HAL_STATUS_SUCCESS;
}

#if AM_HAL_PWRCTRL_SIMOLP_AUTOSWITCH
//*****************************************************************************
//
//! @brief Initialize registers for SIMOBUCK LP auto switch
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t am_hal_spotmgr_simobuck_lp_autosw_init(void)
{
    if (g_sSpotMgr.pfnSimobuckLpAutoSwInit)
    {
        return g_sSpotMgr.pfnSimobuckLpAutoSwInit();
    }
    return AM_HAL_STATUS_SUCCESS;
}

//*****************************************************************************
//
//! @brief Enable SIMOBUCK LP auto switch
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t am_hal_spotmgr_simobuck_lp_autosw_enable(void)
{
    if (g_sSpotMgr.pfnSimobuckLpAutoSwEnable)
    {
        return g_sSpotMgr.pfnSimobuckLpAutoSwEnable();
    }
    return AM_HAL_STATUS_SUCCESS;
}

//*****************************************************************************
//
//! @brief Disable SIMOBUCK LP auto switch
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t am_hal_spotmgr_simobuck_lp_autosw_disable(void)
{
    if (g_sSpotMgr.pfnSimobuckLpAutoSwDisable)
    {
        return g_sSpotMgr.pfnSimobuckLpAutoSwDisable();
    }
    return AM_HAL_STATUS_SUCCESS;
}
#endif

//*****************************************************************************
//
//! @brief SPOT manager init
//!        This API should be called from am_hal_pwrctrl_low_power_init, to
//!        initialise SPOT manager.
//!
//! @return SUCCESS or other Failures.
//
//*****************************************************************************
uint32_t
am_hal_spotmgr_init(void)
{
    uint32_t ui32Status = AM_HAL_STATUS_SUCCESS;

    //
    // Clear spotmgr storage before initialization
    //
    memset(&g_sSpotMgr, 0, sizeof(am_hal_spotmgr_state_t));

    //
    // Populate cached booleans for trim version eval optimization
    //
    // B2 PCM2.2 and newer trim, and silicon newer than B2
    g_bIsPCM2p2OrNewer = APOLLO5_B2_GE_PCM2P2 || APOLLO5_GT_B2;
    // B1 PCM2.1 and B2 PCM2.1
    g_bIsPCM2p1 = APOLLO5_B1_PCM2P1 || APOLLO5_B2_PCM2P1;
    // B0 PCM1.0/1.1 and B1 PCM1.1
    g_bIsPCM1p0OrPCM1p1 = APOLLO5_B0_PCM1P0 || APOLLO5_B0_PCM1P1 || APOLLO5_B1_PCM1P1;
    // B0 PCM1.1 and newer trim
    g_bIsB0PCM1p1OrNewer = APOLLO5_B0_GE_PCM1P1;
    // B1 PCM2.0, B2 PCM2.0
    g_bIsPCM2p0 = APOLLO5_B1_PCM2P0 || APOLLO5_B2_PCM2P0;
    // B1 PCM2.1 without UCRG patch, B2 PCM2.1 without UCRG patch
    g_bIsPCM2p1WoPatch = (APOLLO5_B1_PCM2P1 || APOLLO5_B2_PCM2P1) && ((g_sINFO1regs.ui32PATCH_TRACKER0 & 0x1) == 0);
    // Silicon versions and trim versions which should call am_hal_spotmgr_pcm2_0
    g_bCallPcm2p0Spotmgr = (APOLLO5_B0_GE_PCM1P0 || APOLLO5_B1_LE_PCM2P0 || APOLLO5_B2_PCM2P0);

    //
    // Populate SPOTmanager function pointer according to PCM version
    //
    if (g_bIsPCM2p2OrNewer)
    {
#if !AM_HAL_SPOTMGR_PCM2_2_DISABLE
        g_sSpotMgr.pfnSpotmgrInit = am_hal_spotmgr_pcm2_2_init;
        g_sSpotMgr.pfnSpotmgrPSUpdate = am_hal_spotmgr_pcm2_2_power_state_update;
        g_sSpotMgr.pfnSpotMgrDefaultRst = am_hal_spotmgr_pcm2_2_default_reset;
        g_sSpotMgr.pfnSpotMgrSimobuckInitBfrOvr = am_hal_spotmgr_pcm2_2_simobuck_init_bfr_ovr;
        g_sSpotMgr.pfnSpotMgrSimobuckInitAftEnable = am_hal_spotmgr_pcm2_2_simobuck_init_aft_enable;
        g_sSpotMgr.pfnSpotMgrPwrSetAftLpToHp = am_hal_spotmgr_pcm2_2_post_lptohp_handle;
#if AM_HAL_SPOTMGR_TIMER_DELAY_PCM2_2
        g_sSpotMgr.pfnTimerIntService = am_hal_spotmgr_pcm2_2_boost_timer_interrupt_service;
#endif
#if NO_TEMPSENSE_IN_DEEPSLEEP
        g_sSpotMgr.pfnSpotMgrTempcoSuspend = am_hal_spotmgr_pcm2_2_tempco_suspend;
#endif
#endif
    }
    else if (g_bIsPCM2p1)
    {
#if !AM_HAL_SPOTMGR_PCM2_1_DISABLE
        g_sSpotMgr.pfnSpotmgrInit = am_hal_spotmgr_pcm2_1_init;
        g_sSpotMgr.pfnSpotmgrPSUpdate = am_hal_spotmgr_pcm2_1_power_state_update;
        g_sSpotMgr.pfnSpotMgrDefaultRst = am_hal_spotmgr_pcm2_1_default_reset;
        g_sSpotMgr.pfnSpotMgrSimobuckInitBfrOvr = am_hal_spotmgr_pcm2_1_simobuck_init_bfr_ovr;
        g_sSpotMgr.pfnSpotMgrSimobuckInitBfrEnable = am_hal_spotmgr_pcm2_1_simobuck_init_bfr_enable;
        g_sSpotMgr.pfnSpotMgrSimobuckInitAftEnable = am_hal_spotmgr_pcm2_1_simobuck_init_aft_enable;
        g_sSpotMgr.pfnSpotMgrPwrSetAftLpToHp = am_hal_spotmgr_pcm2_1_post_lptohp_handle;
#if AM_HAL_SPOTMGR_TIMER_DELAY_PCM2_1
        g_sSpotMgr.pfnTimerIntService = am_hal_spotmgr_pcm2_1_boost_timer_interrupt_service;
#endif
#if NO_TEMPSENSE_IN_DEEPSLEEP
        g_sSpotMgr.pfnSpotMgrTempcoSuspend = am_hal_spotmgr_pcm2_1_tempco_suspend;
#endif // NO_TEMPSENSE_IN_DEEPSLEEP
#endif
    }
    else if (g_bCallPcm2p0Spotmgr)
    {
#if !AM_HAL_SPOTMGR_PCM2_0_DISABLE
        g_sSpotMgr.pfnSpotmgrInit = am_hal_spotmgr_pcm2_0_init;
        g_sSpotMgr.pfnSpotmgrPSUpdate = am_hal_spotmgr_pcm2_0_power_state_update;
        g_sSpotMgr.pfnSpotMgrDefaultRst = am_hal_spotmgr_pcm2_0_default_reset;
        g_sSpotMgr.pfnSpotMgrTempcoPostponeSet = am_hal_spotmgr_pcm2_0_tempco_postpone;
        g_sSpotMgr.pfnSpotMgrTempcoPendingHandle = am_hal_spotmgr_pcm2_0_tempco_pending_handle;
#if NO_TEMPSENSE_IN_DEEPSLEEP
        g_sSpotMgr.pfnSpotMgrTempcoSuspend = am_hal_spotmgr_pcm2_0_tempco_suspend;
#endif // NO_TEMPSENSE_IN_DEEPSLEEP
#if AM_HAL_PWRCTRL_SIMOLP_AUTOSWITCH
        g_sSpotMgr.pfnSimobuckLpAutoSwInit = am_hal_spotmgr_pcm2_0_simobuck_lp_autosw_init;
        g_sSpotMgr.pfnSimobuckLpAutoSwEnable = am_hal_spotmgr_pcm2_0_simobuck_lp_autosw_enable;
        g_sSpotMgr.pfnSimobuckLpAutoSwDisable = am_hal_spotmgr_pcm2_0_simobuck_lp_autosw_disable;
#endif // AM_HAL_PWRCTRL_SIMOLP_AUTOSWITCH
#endif // !AM_HAL_SPOTMGR_PCM2_0_DISABLE
        if ( APOLLO5_B0_PCM1P0 )
        {
#if !AM_HAL_SPOTMGR_PCM1_0_DISABLE
            g_sSpotMgr.pfnSpotMgrSimobuckInitBfrEnable = am_hal_spotmgr_pcm0_7_simobuck_init_bfr_enable;
            g_sSpotMgr.pfnSpotMgrSimobuckInitAftEnable = am_hal_spotmgr_pcm0_7_simobuck_init_aft_enable;
#endif // !AM_HAL_SPOTMGR_PCM1_0_DISABLE
        }
        else
        {
#if !AM_HAL_SPOTMGR_PCM2_0_DISABLE
            g_sSpotMgr.pfnSpotMgrSimobuckInitBfrEnable = am_hal_spotmgr_pcm2_0_simobuck_init_bfr_enable;
            g_sSpotMgr.pfnSpotMgrSimobuckInitAftEnable = am_hal_spotmgr_pcm2_0_simobuck_init_aft_enable;
#endif // !AM_HAL_SPOTMGR_PCM2_0_DISABLE
        }
    }
    else if (APOLLO5_B0_PCM0P7)
    {
#if !AM_HAL_SPOTMGR_PCM0_7_DISABLE
        g_sSpotMgr.pfnSpotmgrInit = am_hal_spotmgr_pcm0_7_init;
        g_sSpotMgr.pfnSpotmgrPSUpdate = am_hal_spotmgr_pcm0_7_power_state_update;
        g_sSpotMgr.pfnSpotMgrSimobuckInitBfrEnable = am_hal_spotmgr_pcm0_7_simobuck_init_bfr_enable;
        g_sSpotMgr.pfnSpotMgrSimobuckInitAftEnable = am_hal_spotmgr_pcm0_7_simobuck_init_aft_enable;
#if NO_TEMPSENSE_IN_DEEPSLEEP
        g_sSpotMgr.pfnSpotMgrTempcoSuspend = am_hal_spotmgr_pcm2_0_tempco_suspend;
#endif // NO_TEMPSENSE_IN_DEEPSLEEP
#endif // !AM_HAL_SPOTMGR_PCM0_7_DISABLE
    }

#if !AM_HAL_SPOTMGR_PCM0_7_DISABLE
    if ( APOLLO5_B0_LE_PCM0P7 )
    {
        g_sSpotMgr.pfnTonConfigInit = am_hal_spotmgr_pcm0_7_ton_config_init;
        g_sSpotMgr.pfnTonConfigUpdate = am_hal_spotmgr_pcm0_7_ton_config_update;
    }
#endif // !AM_HAL_SPOTMGR_PCM0_7_DISABLE

    //
    // Execute SPOTmanager init
    //
    if (g_sSpotMgr.pfnSpotmgrInit)
    {
        ui32Status = g_sSpotMgr.pfnSpotmgrInit();
    }

    return ui32Status;
}

//*****************************************************************************
//
//! @brief Set profile of SPOT manager
//!        This API is used to set SPOT manager profile to change the logic of
//!        power state determination. We implemented 2 profiles as below.
//!
//!        When psProfile->PROFILE_b.COLLAPSESTMANDSTMP ==
//!        AM_HAL_SPOTMGR_COLLAPSE_STM_STMP_DIS (the default profile), keep the
//!        original power state.
//!
//!        When psProfile->PROFILE_b.COLLAPSESTMANDSTMP ==
//!        AM_HAL_SPOTMGR_COLLAPSE_STM_STMP_EN, collapse the STM and STM+periph
//!        power states(0&4, 1&5, 2&6, 3&7, 8&12, 9&13, 10&14, 11&15). We suggest
//!        falling back to this profile for scenarios with frequent peripheral
//!        bursts and the overall time of all peripherals off state is short,
//!        which result in a lower overall average power compared to the default.
//!
//! Important:
//!        After setting the profile, the new profile
//!        takes effect in the next calling to am_hal_spotmgr_power_state_update,
//!        except the calling to am_hal_spotmgr_power_state_update when waking up MCU
//!        from normal sleep or deep sleep, entering normal sleep from CPU HP or LP
//!        mode, entering deepsleep from HP mode.
//!
//! @param psProfile - Pointer of am_hal_spotmgr_profile_t struct.
//!
//! @return None.
//
//*****************************************************************************
void
am_hal_spotmgr_profile_set(am_hal_spotmgr_profile_t * psProfile)
{
    g_sSpotMgrProfile = *psProfile;
}

//*****************************************************************************
//
//! @brief Get current profile which is saved to g_sSpotMgrProfile
//!
//! @param psProfile - Pointer of am_hal_spotmgr_profile_t struct.
//!
//! @return None.
//
//*****************************************************************************
void
am_hal_spotmgr_profile_get(am_hal_spotmgr_profile_t * psProfile)
{
    *psProfile = g_sSpotMgrProfile;
}


//*****************************************************************************
//
//! @brief Dummy Weak function for spotmgr log change event handler
//!
//! @param pChangeLog - Pointer of am_hal_spotmgr_changelog_t struct.
//!
//! @return None.
//
//*****************************************************************************
#ifdef AM_HAL_SPOTMGR_PROFILING
#if defined (__IAR_SYSTEMS_ICC__)
__weak void
#else
void __attribute__((weak))
#endif
am_hal_spotmgr_log_change(am_hal_spotmgr_changelog_t *pChangeLog)
{
    // Dummy weak function - Do nothing
}
#endif

//*****************************************************************************
//
// End Doxygen group.
//! @}
//
//*****************************************************************************
