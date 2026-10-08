//*****************************************************************************
//
//! @file am_hal_sysctrl.c
//!
//! @brief Functions for interfacing with the M55 system control registers
//!
//! @addtogroup sysctrl4_ap510 SYSCTRL - System Control
//! @ingroup apollo510_hal
//! @{
//!
//! Purpose: This module provides system control functions for Apollo5
//! devices, including power management, sleep mode control, and system
//! bus synchronization. It enables efficient power management and
//! reliable system operation across different power states.
//!
//! @section hal_sysctrl_features Key Features
//!
//! 1. @b Sleep @b Management: Control normal and deep sleep modes.
//! 2. @b Power @b Control: Manage buck converter and power states.
//! 3. @b FPU @b Control: Enable/disable floating-point unit operations.
//! 4. @b System @b Reset: Provide system reset functionality.
//! 5. @b Clock @b Management: Control clock multiplexer and reset operations.
//!
//! @section hal_sysctrl_functionality Functionality
//!
//! - Control system sleep and deep sleep modes
//! - Manage power states and buck converter operation
//! - Enable/disable FPU and configure stacking
//! - Handle system reset operations
//! - Control clock multiplexer and reset functionality
//!
//! @section hal_sysctrl_usage Usage
//!
//! 1. Configure sleep modes using am_hal_sysctrl_sleep()
//! 2. Control FPU operations as needed
//! 3. Manage power states and buck converter
//! 4. Handle system reset when required
//! 5. Configure clock multiplexer operations
//!
//! @section hal_sysctrl_configuration Configuration
//!
//! - @b Sleep @b Modes: Configure normal and deep sleep parameters
//! - @b Power @b States: Set up buck converter and power management
//! - @b FPU @b Settings: Configure floating-point unit operations
//! - @b Clock @b Control: Set up clock multiplexer and reset operations
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
#include "am_hal_sysctrl_ton_config.h"
#include "am_hal_sysctrl_clk_mux_reset.h"

//*****************************************************************************
//
// Defines
//
//*****************************************************************************

//*****************************************************************************
//
//  Globals
//
//*****************************************************************************

extern void buck_ldo_update_override(bool bEnable);

bool g_bFrcBuckAct  = false;
static bool g_bAppFrcBuckAct = false;

//! @cond SYSCTRL_CLK_MUX_RESET
static uint8_t g_ui8ClkmuxrstClkNeeded[SYSCTRL_CLKMUXRST_CLK_MAX] = {0};
//! @endcond SYSCTRL_CLK_MUX_RESET

//*****************************************************************************
//
//! @brief Control the buck state in deepsleep
//!
//! @param bFrcBuckAct - True for forcing buck active in deepsleep
//!                    - False for not forcing buck active in deepsleep
//!
//! If you want to manually force the buck stay active in deepsleep mode,
//! am_hal_sysctrl_force_buck_active_in_deepsleep must
//! be called for setting g_bAppFrcBuckAct to true before
//! calling am_hal_sysctrl_sleep(AM_HAL_SYSCTRL_SLEEP_DEEP).
//! For PCM2.1 and later versions, if anyone of spotmgr and
//! am_hal_sysctrl_force_buck_active_in_deepsleep forced buck stay active, buck
//! will stay active in deepsleep.
//
//*****************************************************************************
void
am_hal_sysctrl_force_buck_active_in_deepsleep(bool bFrcBuckAct)
{
    g_bAppFrcBuckAct = bFrcBuckAct;
}

//
// Instrumentation hook for collecting the Register Settings values such as PWRCTRL, MCUCTRL and CLKGEN
//
__attribute__((weak)) void am_hal_PRE_SLEEP_PROCESSING(void){}

//*****************************************************************************
//
// Place the core into sleep or deepsleep.
//
// This function puts the MCU to sleep or deepsleep depending on bSleepDeep.
//
// Valid values for bSleepDeep are:
//     AM_HAL_SYSCTRL_SLEEP_NORMAL
//     AM_HAL_SYSCTRL_SLEEP_DEEP
//
//*****************************************************************************
void
am_hal_sysctrl_sleep(bool bSleepDeep)
{
    bool bBuckIntoLPinDS = false, bSimobuckAct = false, bPeriphOff = false;
    am_hal_pwrctrl_pwrmodctl_cpdlp_t sActCpdlpConfig;
    bool bReportedDeepSleep = false, bVDDCACTLOWTONTRIMChanged = false;
    uint32_t ui32CurVDDCACTLOWTONTRIM = 0, ui32CpdlpConfig = 0;
    uint32_t ui32InternalTimerAIRQNum = TIMER0_IRQn + AM_HAL_INTERNAL_TIMER_NUM_A + NVIC_USER_IRQ_OFFSET;
    am_hal_spotmgr_cpu_state_e eCpuSt;
    bool bSetPwrSwOverrideAtWake = false, bOtherIsrPending = false;

    //
    // Disable interrupts and save the previous interrupt state.
    //
    AM_CRITICAL_BEGIN

    //
    // Get the current CPDLPSTATE configuration in active mode
    //
    am_hal_pwrctrl_pwrmodctl_cpdlp_get(&sActCpdlpConfig);
    //
    // Prepare the data for restoring CPDLPSTATE configuration after waking up
    //
    ui32CpdlpConfig |= (sActCpdlpConfig.eRlpConfig << PWRMODCTL_CPDLPSTATE_RLPSTATE_Pos);
    ui32CpdlpConfig |= (sActCpdlpConfig.eElpConfig << PWRMODCTL_CPDLPSTATE_ELPSTATE_Pos);
    ui32CpdlpConfig |= (sActCpdlpConfig.eClpConfig << PWRMODCTL_CPDLPSTATE_CLPSTATE_Pos);

    //
    // Get current mode.
    //
    bSimobuckAct = ( PWRCTRL->VRSTATUS_b.SIMOBUCKST == PWRCTRL_VRSTATUS_SIMOBUCKST_ACT );

    //
    // If the user selected DEEPSLEEP and OTP is off, setup the system to enter DEEP SLEEP.
    // CPU cannot go to deepsleep if OTP is still powered on
    //
    if ((bSleepDeep == AM_HAL_SYSCTRL_SLEEP_DEEP)
        && (!PWRCTRL->DEVPWRSTATUS_b.PWRSTOTP))
    {
        //
        // Set the CPDLPSTATE configuration in deepsleep mode
        //
        am_hal_pwrctrl_pwrmodctl_cpdlp_t sDSCpdlpConfig =
        {
            .eRlpConfig = sActCpdlpConfig.eRlpConfig,
            .eElpConfig = AM_HAL_PWRCTRL_ELP_RET,
            .eClpConfig = AM_HAL_PWRCTRL_CLP_RET
        };
        //
        // If ELP is OFF in active state, keep it OFF.
        //
        if (sActCpdlpConfig.eElpConfig == AM_HAL_PWRCTRL_ELP_OFF)
        {
            sDSCpdlpConfig.eElpConfig = AM_HAL_PWRCTRL_ELP_OFF;
        }
        am_hal_pwrctrl_pwrmodctl_cpdlp_config(sDSCpdlpConfig);

#if NO_TEMPSENSE_IN_DEEPSLEEP
        am_hal_spotmgr_tempco_suspend();
#endif
        //
        // Report CPU state change
        //
        eCpuSt = AM_HAL_SPOTMGR_CPUSTATE_SLEEP_DEEP;
        am_hal_spotmgr_power_state_update(AM_HAL_SPOTMGR_STIM_CPU_STATE, false, (void *) &eCpuSt);
        //
        // Prepare the data for reporting CPU status after waking up.
        //
        if (PWRCTRL->MCUPERFREQ_b.MCUPERFREQ == AM_HAL_PWRCTRL_MCU_MODE_HIGH_PERFORMANCE)
        {
            eCpuSt = AM_HAL_SPOTMGR_CPUSTATE_ACTIVE_HP;
        }
        else
        {
            eCpuSt = AM_HAL_SPOTMGR_CPUSTATE_ACTIVE_LP;
        }
        bReportedDeepSleep = true;

        //
        // Check if SIMOBUCK needs to stay in Active mode in DeepSleep
        //
        if ( bSimobuckAct )
        {
            //
            // Check if SIMOBUCK would go into LP mode in DeepSleep
            //
            if (
                //
                // For PCM2.1 and later versions, check peripheral status in spotmgr.
                //
                APOLLO5_B1_GE_PCM2P1                                                  ||
                APOLLO5_B2_GE_PCM2P1                                                  ||
                (!(PWRCTRL->AUDSSPWRSTATUS &
                    (PWRCTRL_AUDSSPWRSTATUS_PWRSTAUDADC_Msk |
                    PWRCTRL_AUDSSPWRSTATUS_PWRSTI2S1_Msk   |
                    PWRCTRL_AUDSSPWRSTATUS_PWRSTI2S0_Msk   |
                    PWRCTRL_AUDSSPWRSTATUS_PWRSTPDM0_Msk)) &&
                !(PWRCTRL->DEVPWRSTATUS &
                    (PWRCTRL_DEVPWRSTATUS_PWRSTDBG_Msk      |
                    PWRCTRL_DEVPWRSTATUS_PWRSTUSBPHY_Msk   |
                    PWRCTRL_DEVPWRSTATUS_PWRSTUSB_Msk      |
                    PWRCTRL_DEVPWRSTATUS_PWRSTSDIO1_Msk    |
                    PWRCTRL_DEVPWRSTATUS_PWRSTSDIO0_Msk    |
                    PWRCTRL_DEVPWRSTATUS_PWRSTCRYPTO_Msk   |
                    PWRCTRL_DEVPWRSTATUS_PWRSTDISPPHY_Msk  |
                    PWRCTRL_DEVPWRSTATUS_PWRSTDISP_Msk     |
                    PWRCTRL_DEVPWRSTATUS_PWRSTGFX_Msk      |
                    PWRCTRL_DEVPWRSTATUS_PWRSTMSPI3_Msk    |
                    PWRCTRL_DEVPWRSTATUS_PWRSTMSPI2_Msk    |
                    PWRCTRL_DEVPWRSTATUS_PWRSTMSPI1_Msk    |
                    PWRCTRL_DEVPWRSTATUS_PWRSTMSPI0_Msk    |
                    PWRCTRL_DEVPWRSTATUS_PWRSTADC_Msk      |
                    PWRCTRL_DEVPWRSTATUS_PWRSTUART3_Msk    |
                    PWRCTRL_DEVPWRSTATUS_PWRSTUART2_Msk    |
                    PWRCTRL_DEVPWRSTATUS_PWRSTUART1_Msk    |
                    PWRCTRL_DEVPWRSTATUS_PWRSTUART0_Msk    |
                    PWRCTRL_DEVPWRSTATUS_PWRSTIOM7_Msk     |
                    PWRCTRL_DEVPWRSTATUS_PWRSTIOM6_Msk     |
                    PWRCTRL_DEVPWRSTATUS_PWRSTIOM5_Msk     |
                    PWRCTRL_DEVPWRSTATUS_PWRSTIOM4_Msk     |
                    PWRCTRL_DEVPWRSTATUS_PWRSTIOM3_Msk     |
                    PWRCTRL_DEVPWRSTATUS_PWRSTIOM2_Msk     |
                    PWRCTRL_DEVPWRSTATUS_PWRSTIOM1_Msk     |
                    PWRCTRL_DEVPWRSTATUS_PWRSTIOM0_Msk     |
                    PWRCTRL_DEVPWRSTATUS_PWRSTIOSFD0_Msk   |
                    PWRCTRL_DEVPWRSTATUS_PWRSTIOSFD1_Msk   |
                    PWRCTRL_DEVPWRSTATUS_PWRSTIOS0_Msk     |
                    PWRCTRL_DEVPWRSTATUS_PWRSTOTP_Msk ))      &&
                //
                // Check and confirm Simobuck/LDO is forced active if PLL is enabled
                //
                ( MCUCTRL->PLLCTL0_b.SYSPLLPDB != MCUCTRL_PLLCTL0_SYSPLLPDB_ENABLE )))
            {
                bPeriphOff = true;
                if (!g_bAppFrcBuckAct && !g_bFrcBuckAct)
                {
                    //
                    // This implies upon deepsleep, buck can transition into LP mode
                    //
                    bBuckIntoLPinDS = true;
                    //
                    // Remove overrides to allow buck to go in LP mode
                    //
                    buck_ldo_update_override(false);

#if AM_HAL_PWRCTRL_SIMOLP_AUTOSWITCH
                    am_hal_spotmgr_simobuck_lp_autosw_enable();
#endif
                }
            }
        }
        //
        // Prepare the core for deepsleep (write 1 to the DEEPSLEEP bit).
        //
        SCB->SCR |= _VAL2FLD(SCB_SCR_SLEEPDEEP, 1);
#if !AM_HAL_STALL_CPU_HPWAKE
        //
        // If in HP mode, we need to wait till HFRC2 is ready and CPU is fully back in HP mode, before attempting deepsleep
        //
        if (PWRCTRL->MCUPERFREQ_b.MCUPERFREQ == AM_HAL_PWRCTRL_MCU_MODE_HIGH_PERFORMANCE)
        {
            while ( PWRCTRL->MCUPERFREQ_b.MCUPERFSTATUS != AM_HAL_PWRCTRL_MCU_MODE_HIGH_PERFORMANCE )
            {
                am_hal_delay_us(1);
            }
        }
#endif // !AM_HAL_STALL_CPU_HPWAKE
        //
        // Clear PWRSWVDDCAOROVERRIDE and PWRSWVDDCPUOVERRIDE
        //
        if (g_bHpToDeepSleep)
        {
            MCUCTRL->SIMOBUCK14_b.VDDFCOMPTRIMMINUS = g_sSpotMgrINFO1regs.sMemldoCfg.MEMLDOCONFIG_b.VDDFCOMPTRIMMINUS;
            if (g_bVddcaorVddcpuOverride)
            {
                MCUCTRL->PWRSW0_b.PWRSWVDDCPUOVERRIDE = 0;
                MCUCTRL->PWRSW0_b.PWRSWVDDCAOROVERRIDE = 0;
            }

            // Check for condition to recover PwrSwOverrides on wakeup
            bSetPwrSwOverrideAtWake = (g_bIsPCM2p2OrNewer && g_bVddcaorVddcpuOverride) ||
                                      (g_bIsPCM2p1 && g_bVddcaorVddcpuOverride && (!g_bSwitchingToHp));
        }
        //
        // If entering deepsleep in CPU LP mode, and STM state was collapsed to STM+periph state,
        // the simobuck VDDF LP minus offset trim must be set to reduce VDDF to reduce the power consumption.
        //
        if (g_bVddfLpMinusForLp)
        {
            MCUCTRL->SIMOBUCK14_b.VDDFCOMPTRIMMINUS = 11;
        }
        //
        // If current VDDCACTLOWTONTRIM is > GPULPCPUHPVDDCTON in INFO1, set it to GPULPCPUHPVDDCTON in INFO1.
        //
        if ((g_sSpotMgrINFO1regs.ui32SpotMgrINFO1GlobalValid == INFO1GLOBALVALID) && g_bIsPCM2p1)
        {
            if (MCUCTRL->SIMOBUCK2_b.VDDCACTLOWTONTRIM > g_sSpotMgrINFO1regs.sGpuVddcTon.GPUVDDCTON_b.GPULPCPUHPVDDCTON)
            {
                ui32CurVDDCACTLOWTONTRIM = MCUCTRL->SIMOBUCK2_b.VDDCACTLOWTONTRIM;
                MCUCTRL->SIMOBUCK2_b.VDDCACTLOWTONTRIM = g_sSpotMgrINFO1regs.sGpuVddcTon.GPUVDDCTON_b.GPULPCPUHPVDDCTON;
                bVDDCACTLOWTONTRIMChanged = true;
            }
        }
    }
    else
    {
        //
        // Set the CPDLPSTATE configuration in normal sleep mode
        //
        am_hal_pwrctrl_pwrmodctl_cpdlp_t sNSCpdlpConfig;
        if (PWRCTRL->CPUPWRCTRL_b.SLEEPMODE) // ARM sleep
        {
            sNSCpdlpConfig.eRlpConfig = sActCpdlpConfig.eRlpConfig;
            sNSCpdlpConfig.eElpConfig = AM_HAL_PWRCTRL_ELP_RET;
            sNSCpdlpConfig.eClpConfig = AM_HAL_PWRCTRL_CLP_ON_CLK_OFF;
        }
        else // Ambiq sleep
        {
            sNSCpdlpConfig.eRlpConfig = sActCpdlpConfig.eRlpConfig;
            sNSCpdlpConfig.eElpConfig = AM_HAL_PWRCTRL_ELP_RET; // or can leave at 0x0 as we will turn the clocks off at the source
            sNSCpdlpConfig.eClpConfig = AM_HAL_PWRCTRL_CLP_ON_CLK_OFF; // or can leave at 0x0 as we will turn the clocks off at the source
        }
        //
        // If ELP is OFF or RET in active state, keep it OFF or RET.
        //
        if ((sActCpdlpConfig.eElpConfig == AM_HAL_PWRCTRL_ELP_OFF) || (sActCpdlpConfig.eElpConfig == AM_HAL_PWRCTRL_ELP_RET))
        {
            sNSCpdlpConfig.eElpConfig = sActCpdlpConfig.eElpConfig;
        }
        am_hal_pwrctrl_pwrmodctl_cpdlp_config(sNSCpdlpConfig);

        //
        // Prepare the core for normal sleep (write 0 to the DEEPSLEEP bit).
        //
        SCB->SCR &= ~_VAL2FLD(SCB_SCR_SLEEPDEEP, 1);
    }

    //
    // Before executing WFI, flush APB writes.
    //
    am_hal_sysctrl_sysbus_write_flush();

    //
    // Weak am_hal_PRE_SLEEP_PROCESSING function to be overwritten in the application. Used by pwrctrl_state_transition_trim_regdump_test_cases
    // to collect the Register Settings for PWRCTRL, MCUCTRL and CLKGEN before going into deepsleep
    //
    am_hal_PRE_SLEEP_PROCESSING();

    //
    // Execute the sleep instruction.
    //
    __WFI();

    //
    // Upon wake, execute the Instruction Sync Barrier instruction.
    //
    __ISB();
    //
    // If VDDCACTLOWTONTRIM was changed before deepsleep, restore it.
    //
    if (bVDDCACTLOWTONTRIMChanged)
    {
        MCUCTRL->SIMOBUCK2_b.VDDCACTLOWTONTRIM = ui32CurVDDCACTLOWTONTRIM;
    }
    //
    // Set PWRSWVDDCAOROVERRIDE and PWRSWVDDCPUOVERRIDE
    //
    if (g_bHpToDeepSleep)
    {
        if (bSetPwrSwOverrideAtWake)
        {
            MCUCTRL->PWRSW0_b.PWRSWVDDCPUOVERRIDE = 1;
            MCUCTRL->PWRSW0_b.PWRSWVDDCAOROVERRIDE = 1;
        }
        MCUCTRL->SIMOBUCK14_b.VDDFCOMPTRIMMINUS = 0;
    }
    //
    // After exiting deepsleep in CPU LP mode, the simobuck VDDF LP minus offset trim must be set back to 0.
    //
    if (g_bVddfLpMinusForLp)
    {
        MCUCTRL->SIMOBUCK14_b.VDDFCOMPTRIMMINUS = 0;
    }
    //
    // Check if the wake-up was caused by AM_HAL_INTERNAL_TIMER_NUM_A interrupt; if so, attempt to re-enter deep sleep.
    //
    if ((g_bIsPCM2p1 || g_bIsPCM2p2OrNewer) &&
        (_FLD2VAL(SCB_ICSR_VECTPENDING, SCB->ICSR) == ui32InternalTimerAIRQNum))
    {
        //
        // Call am_hal_spotmgr_boost_timer_interrupt_service manually, we stopped the timer and cleared the timer interrupt status in this fucntion.
        //
        am_hal_spotmgr_boost_timer_interrupt_service();
        if (!(_FLD2VAL(SCB_ICSR_VECTPENDING, SCB->ICSR)))
        {
            if (bSleepDeep == AM_HAL_SYSCTRL_SLEEP_DEEP)
            {
                //
                // If in HP mode, we need to wait till HFRC2 is ready and CPU is fully back in HP mode, before attempting deepsleep
                //
                if (PWRCTRL->MCUPERFREQ_b.MCUPERFREQ == AM_HAL_PWRCTRL_MCU_MODE_HIGH_PERFORMANCE)
                {
                    while ( PWRCTRL->MCUPERFREQ_b.MCUPERFSTATUS != AM_HAL_PWRCTRL_MCU_MODE_HIGH_PERFORMANCE )
                    {
                        //
                        // Check if any other interrupts are pending.
                        //
                        if (_FLD2VAL(SCB_ICSR_VECTPENDING, SCB->ICSR))
                        {
                            bOtherIsrPending = true;
                            break;
                        }
                        else
                        {
                            am_hal_delay_us(1);
                        }
                    }
                }
            }

            //
            // Enter sleep mode again only if no other interrupts are pending.
            //
            if (!bOtherIsrPending)
            {
                if (bReportedDeepSleep)
                {
                    am_hal_spotmgr_power_state_update(AM_HAL_SPOTMGR_STIM_CPU_STATE, false, (void *) &eCpuSt);
                    //
                    // Report deepsleep state again to update global variables (g_bVddcaorVddcpuOverride, g_bHpToDeepSleep...)
                    //
                    am_hal_spotmgr_cpu_state_e eCpuSleepDeep = AM_HAL_SPOTMGR_CPUSTATE_SLEEP_DEEP;
                    am_hal_spotmgr_power_state_update(AM_HAL_SPOTMGR_STIM_CPU_STATE, false, (void *) &eCpuSleepDeep);
                }
                //
                // Remove overrides to allow buck to go in LP mode
                //
                if (bPeriphOff)
                {
                    if (!g_bAppFrcBuckAct && !g_bFrcBuckAct)
                    {
                        //
                        // This implies upon deepsleep, buck can transition into LP mode
                        //
                        bBuckIntoLPinDS = true;
                        //
                        // Remove overrides to allow buck to go in LP mode
                        //
                        buck_ldo_update_override(false);
#if AM_HAL_PWRCTRL_SIMOLP_AUTOSWITCH
                        am_hal_spotmgr_simobuck_lp_autosw_enable();
#endif
                    }
                }
                //
                // Clear PWRSWVDDCAOROVERRIDE and PWRSWVDDCPUOVERRIDE
                //
                if (g_bHpToDeepSleep)
                {
                    MCUCTRL->SIMOBUCK14_b.VDDFCOMPTRIMMINUS = g_sSpotMgrINFO1regs.sMemldoCfg.MEMLDOCONFIG_b.VDDFCOMPTRIMMINUS;
                    if (g_bVddcaorVddcpuOverride)
                    {
                        MCUCTRL->PWRSW0_b.PWRSWVDDCPUOVERRIDE = 0;
                        MCUCTRL->PWRSW0_b.PWRSWVDDCAOROVERRIDE = 0;
                    }
                }
                //
                // If entering deepsleep in CPU LP mode, and STM state was collapsed to STM+periph state,
                // the simobuck VDDF LP minus offset trim must be set to reduce VDDF to reduce the power consumption.
                //
                if (g_bVddfLpMinusForLp)
                {
                    MCUCTRL->SIMOBUCK14_b.VDDFCOMPTRIMMINUS = 11;
                }
                //
                // If current VDDCACTLOWTONTRIM is > GPULPCPUHPVDDCTON in INFO1, set it to GPULPCPUHPVDDCTON in INFO1.
                //
                if (bVDDCACTLOWTONTRIMChanged)
                {
                    MCUCTRL->SIMOBUCK2_b.VDDCACTLOWTONTRIM = g_sSpotMgrINFO1regs.sGpuVddcTon.GPUVDDCTON_b.GPULPCPUHPVDDCTON;
                }

                //
                // Before executing WFI, flush APB writes.
                //
                am_hal_sysctrl_sysbus_write_flush();

                //
                // Execute the sleep instruction.
                //
                __WFI();

                //
                // Upon wake, execute the Instruction Sync Barrier instruction.
                //
                __ISB();

                //
                // If VDDCACTLOWTONTRIM was changed before deepsleep, restore it.
                //
                if (bVDDCACTLOWTONTRIMChanged)
                {
                    MCUCTRL->SIMOBUCK2_b.VDDCACTLOWTONTRIM = ui32CurVDDCACTLOWTONTRIM;
                }
                //
                // Set PWRSWVDDCAOROVERRIDE and PWRSWVDDCPUOVERRIDE
                //
                if (g_bHpToDeepSleep)
                {
                    if (bSetPwrSwOverrideAtWake)
                    {
                        MCUCTRL->PWRSW0_b.PWRSWVDDCPUOVERRIDE = 1;
                        MCUCTRL->PWRSW0_b.PWRSWVDDCAOROVERRIDE = 1;
                    }
                    MCUCTRL->SIMOBUCK14_b.VDDFCOMPTRIMMINUS = 0;
                }
                //
                // After exiting deepsleep in CPU LP mode, the simobuck VDDF LP minus offset trim must be set back to 0.
                //
                if (g_bVddfLpMinusForLp)
                {
                    MCUCTRL->SIMOBUCK14_b.VDDFCOMPTRIMMINUS = 0;
                }
            }
        }
    }
    if (g_bHpToDeepSleep)
    {
        //
        // Clear this bit after setting the Vddcaor Vddcpu Override back and CPU exits deepsleep then enters HP mode.
        //
        g_bHpToDeepSleep = false;
        g_bVddcaorVddcpuOverride = false;
    }
    //
    // Clear flag g_bVddfLpMinusForLp.
    //
    if (g_bVddfLpMinusForLp)
    {
        g_bVddfLpMinusForLp = false;
    }

    //
    // Report CPU state change
    //
    if (bReportedDeepSleep)
    {
        am_hal_spotmgr_power_state_update(AM_HAL_SPOTMGR_STIM_CPU_STATE, false, (void *) &eCpuSt);
    }
#if AM_HAL_STALL_CPU_HPWAKE
    //
    // If in HP mode, we need to wait till HFRC2 is ready and CPU is fully back in HP mode
    //
    if ((bSleepDeep == AM_HAL_SYSCTRL_SLEEP_DEEP) && (PWRCTRL->MCUPERFREQ_b.MCUPERFREQ == AM_HAL_PWRCTRL_MCU_MODE_HIGH_PERFORMANCE))
    {
        while ( PWRCTRL->MCUPERFREQ_b.MCUPERFSTATUS != AM_HAL_PWRCTRL_MCU_MODE_HIGH_PERFORMANCE )
        {
            am_hal_delay_us(1);
        }
    }
#endif // AM_HAL_STALL_CPU_HPWAKE

    if ( bBuckIntoLPinDS )
    {
        //
        // Re-enable overrides
        //
        MCUCTRL->VRCTRL_b.SIMOBUCKOVER   = true;
#if AM_HAL_PWRCTL_SET_CORELDO_MEMLDO_IN_PARALLEL
        MCUCTRL->VRCTRL_b.CORELDOOVER    = true;
        MCUCTRL->VRCTRL_b.MEMLDOOVER     = true;
#endif // AM_HAL_PWRCTL_SET_CORELDO_MEMLDO_IN_PARALLEL
    }

#if AM_HAL_PWRCTRL_SIMOLP_AUTOSWITCH
    am_hal_spotmgr_simobuck_lp_autosw_disable();
#endif

    //
    // Restore the CPDLPSTATE
    // am_hal_pwrctrl_pwrmodctl_cpdlp_config(sActCpdlpConfig);
    //
    PWRMODCTL->CPDLPSTATE = ui32CpdlpConfig;

    //
    // Restore the interrupt state.
    //
    AM_CRITICAL_END
}

//*****************************************************************************
//
// Enable the floating point module.
//
//*****************************************************************************
void
am_hal_sysctrl_fpu_enable(void)
{
    //
    //! Enable the EPU. See section 6.3 of the CM55 TRM.

    //
    SCB->CPACR |= (0xF << 20);
    __DSB();
    __ISB();
}

//*****************************************************************************
//
// Disable the floating point module.
//
//*****************************************************************************
void
am_hal_sysctrl_fpu_disable(void)
{
    //
    // Disable access to the FPU in both privileged and user modes.
    // NOTE: Write 0s to all reserved fields in this register.
    //
    SCB->CPACR |= ~(0xF << 20);
    __DSB();
    __ISB();
}

//*****************************************************************************
//
// Enable stacking of FPU registers on exception entry.
//
//*****************************************************************************
void
am_hal_sysctrl_fpu_stacking_enable(bool bLazy)
{
    uint32_t ui32fpccr;

    //
    // Set the requested FPU stacking mode in ISRs.
    //
    AM_CRITICAL_BEGIN
#define SYSCTRL_FPCCR_LAZY  (FPU_FPCCR_ASPEN_Msk | FPU_FPCCR_LSPEN_Msk)
    ui32fpccr  = FPU->FPCCR;
    ui32fpccr &= ~SYSCTRL_FPCCR_LAZY;
    ui32fpccr |= (bLazy ? SYSCTRL_FPCCR_LAZY : FPU_FPCCR_ASPEN_Msk);
    FPU->FPCCR = ui32fpccr;
    AM_CRITICAL_END
}

//*****************************************************************************
//
// Disable FPU register stacking on exception entry.
//
//*****************************************************************************
void
am_hal_sysctrl_fpu_stacking_disable(void)
{
    //
    // Completely disable FPU context save on entry to ISRs.
    //
    AM_CRITICAL_BEGIN
    FPU->FPCCR &= ~SYSCTRL_FPCCR_LAZY;
    AM_CRITICAL_END
}

//*****************************************************************************
//
// Issue a system wide reset using the AIRCR bit in the M4 system ctrl.
//
//*****************************************************************************
void
am_hal_sysctrl_aircr_reset(void)
{
    //
    // Set the system reset bit in the AIRCR register
    //
    __NVIC_SystemReset();
}

//! @cond SYSCTRL_CLK_MUX_RESET
//*****************************************************************************
//
// Update clocks needed for clock muxes reset operation
//
//*****************************************************************************
void
am_hal_sysctrl_clkmuxrst_audadc_clkgen_off_update(bool bClkgenOff)
{
    AM_CRITICAL_BEGIN
    HALSTATE_b.AUDADC_CLKGEN_OFF = bClkgenOff;
    AM_CRITICAL_END
}

//*****************************************************************************
//
// Update clocks needed for clock muxes reset operation
//
//*****************************************************************************
void
am_hal_sysctrl_clkmuxrst_pll_fref_update(MCUCTRL_PLLCTL0_FREFSEL_Enum eFref)
{
    AM_CRITICAL_BEGIN
    HALSTATE_b.PLL_FREFSEL = (uint8_t)eFref;
    AM_CRITICAL_END
}

//*****************************************************************************
//
// Update clocks needed for clock muxes reset operation
//
//*****************************************************************************
void
am_hal_sysctrl_clkmuxrst_clkneeded_update(am_hal_sysctrl_clkmuxrst_clk_e eClk, uint8_t ui8ClkSrcBm)
{
    uint8_t ui8Idx;
    uint8_t ui8ClockNeeded = 0;

    AM_CRITICAL_BEGIN

    //
    // Update clock needed array
    //
    g_ui8ClkmuxrstClkNeeded[(uint8_t)eClk] = ui8ClkSrcBm;

    //
    // Compute and save clock needed
    //
    for (ui8Idx = 0; ui8Idx < SYSCTRL_CLKMUXRST_CLK_MAX; ui8Idx++)
    {
        ui8ClockNeeded |= g_ui8ClkmuxrstClkNeeded[ui8Idx];
    }
    HALSTATE_b.HFRC_DED_NEEDED = (ui8ClockNeeded & SYSCTRL_CLKMUXRST_CLK_HFRC_DED) ? 1 : 0;
    HALSTATE_b.HFRC2_NEEDED = (ui8ClockNeeded & SYSCTRL_CLKMUXRST_CLK_HFRC2) ? 1 : 0;
    HALSTATE_b.XTAL_NEEDED = (ui8ClockNeeded & SYSCTRL_CLKMUXRST_CLK_XTAL) ? 1 : 0;
    HALSTATE_b.EXTCLK_NEEDED = (ui8ClockNeeded & SYSCTRL_CLKMUXRST_CLK_EXTCLK) ? 1 : 0;
    HALSTATE_b.PLL_NEEDED = (ui8ClockNeeded & SYSCTRL_CLKMUXRST_CLK_PLL) ? 1 : 0;

    AM_CRITICAL_END
}

//*****************************************************************************
//
// Handle clock muxes reset during low_power_init
//
//*****************************************************************************
void
am_hal_sysctrl_clkmuxrst_low_power_init()
{
    am_hal_clkmgr_board_info_t sClkmgrBoardInfo;
    //
    // Execute clock mux reset if this is not a POA reset and SNVR2 signature
    // matches
    //
    if ( !RSTGEN->STAT_b.POASTAT && HALSTATE_b.SIGNATURE == SYSCTRL_CLKMUXRST_SIGNATURE )
    {
        // If Clock Recovery is needed
        if (HALSTATE_b.AUDADC_CLKGEN_OFF || HALSTATE_b.HFRC_DED_NEEDED ||
            HALSTATE_b.HFRC2_NEEDED || HALSTATE_b.XTAL_NEEDED ||
            HALSTATE_b.EXTCLK_NEEDED || HALSTATE_b.PLL_NEEDED)
        {
            am_hal_gpio_pincfg_t sGpio15Cfg;

            // ----------------------------------------------------------------
            // Stage 1: Enable Clocks Needed
            // ----------------------------------------------------------------
            // Enable HFRC_DED if AUDADC clock gen mux was OFF or if HFRC_DED is
            // marked needed
            if (HALSTATE_b.AUDADC_CLKGEN_OFF || HALSTATE_b.HFRC_DED_NEEDED)
            {
                *(volatile uint32_t*)0x400200C0 |= 0x00000001;
            }

            // Switch to HFRC LL MUX to HFRC if AUDADC clock gen mux was OFF,
            if (HALSTATE_b.AUDADC_CLKGEN_OFF)
            {
                MCUCTRL->PLLMUXCTL_b.AUDADCPLLCLKSEL = MCUCTRL_PLLMUXCTL_AUDADCPLLCLKSEL_HFRC;
                am_hal_sysctrl_sysbus_write_flush();
                am_hal_delay_us(1);
            }

            // If HFRC2 is marked needed, switch to HFRC LL Mux
            if (HALSTATE_b.HFRC2_NEEDED)
            {
                CLKGEN->MISC_b.FRCHFRC2 = CLKGEN_MISC_FRCHFRC2_FRC;
                // Wait for HFRC2 Clock to be ready
                am_hal_delay_us_status_check(200,
                                             (uint32_t)&CLKGEN->CLOCKENSTAT,
                                             CLKGEN_CLOCKENSTAT_HFRC2READY_Msk,
                                             CLKGEN_CLOCKENSTAT_HFRC2READY_Msk,
                                             true);
                am_hal_delay_us(5);
            }

            // If XTAL is marked needed, kick start XTAL
            if (HALSTATE_b.XTAL_NEEDED ||
                (HALSTATE_b.PLL_NEEDED && HALSTATE_b.PLL_FREFSEL == MCUCTRL_PLLCTL0_FREFSEL_XTAL32MHz))
            {
                bool bFalse = false;
                am_hal_mcuctrl_control(AM_HAL_MCUCTRL_CONTROL_EXTCLK32M_KICK_START, &bFalse);
                am_hal_delay_us(1500);
            }

            // if EXTCLK is marked needed, backup GPIO 15 config and switch
            // function to ExtRefClk
            if (HALSTATE_b.EXTCLK_NEEDED ||
                (HALSTATE_b.PLL_NEEDED && HALSTATE_b.PLL_FREFSEL == MCUCTRL_PLLCTL0_FREFSEL_EXTREFCLK))
            {
                //
                // Check if this is a SIP device(Apollo510B) and is it enabled
                //
                am_hal_clkmgr_board_info_get(&sClkmgrBoardInfo);
                if (sClkmgrBoardInfo.bIsSipEnabled)
                {
                    //
                    // Request clock from SIP and wait 1ms for the clock to propagate through
                    //
                    am_hal_gpio_output_set(136);
                    am_hal_delay_us(1000);
                }
                am_hal_gpio_pincfg_t sExtRefClkCfg;
                sExtRefClkCfg.GP.cfg_b.uFuncSel = AM_HAL_PIN_15_REFCLK_EXT;
                am_hal_gpio_pinconfig_get(15, &sGpio15Cfg);
                am_hal_gpio_pinconfig(15, sExtRefClkCfg);
            }

            // if PLL is marked needed, start PLL in bypass mode
            if (HALSTATE_b.PLL_NEEDED)
            {
                am_hal_pwrctrl_syspll_enable();
                SYSPLLn(0)->PLLCTL0_b.FOUTPOSTDIVPD  = MCUCTRL_PLLCTL0_FOUTPOSTDIVPD_ACTIVE;
                SYSPLLn(0)->PLLCTL0_b.FOUT4PHASEPD   = MCUCTRL_PLLCTL0_FOUT4PHASEPD_ACTIVE;
                SYSPLLn(0)->PLLCTL0_b.FREFSEL        = HALSTATE_b.PLL_FREFSEL;
                SYSPLLn(0)->PLLCTL0_b.BYPASS         = 1;
                SYSPLLn(0)->PLLCTL0_b.SYSPLLPDB      = MCUCTRL_PLLCTL0_SYSPLLPDB_ENABLE;
            }

            // ----------------------------------------------------------------
            // Stage 2: Clock muxes reset
            // ----------------------------------------------------------------
            // Power on PDM, I2S, AUDADC, and USB
            am_hal_pwrctrl_periph_enable(AM_HAL_PWRCTRL_PERIPH_PDM0);
            am_hal_pwrctrl_periph_enable(AM_HAL_PWRCTRL_PERIPH_I2S0);
            am_hal_pwrctrl_periph_enable(AM_HAL_PWRCTRL_PERIPH_I2S1);
            am_hal_pwrctrl_periph_enable(AM_HAL_PWRCTRL_PERIPH_AUDADC);
            am_hal_pwrctrl_periph_enable(AM_HAL_PWRCTRL_PERIPH_USB);
            am_hal_pwrctrl_periph_enable(AM_HAL_PWRCTRL_PERIPH_USBPHY);
            am_hal_sysctrl_sysbus_write_flush();
            am_hal_delay_us(5);

            // Make sure the clock path form CLKGEN out to LL mux input is not
            // gated.
            PDMn(0)->CTRL_b.CLKEN = 1;
            I2Sn(0)->CLKCFG_b.MCLKEN = 1;
            I2Sn(1)->CLKCFG_b.MCLKEN = 1;
            USBn(0)->CLKCTRL_b.PHYREFCLKDIS = 0;

            // Generate APB Write Pulse to trigger AUDADC clock gen switching
            AUDADCn(0)->CFG_b.CLKSEL = AUDADC_CFG_CLKSEL_HFRC_48MHz;
            am_hal_sysctrl_bus_write_flush();
            am_hal_delay_us(1);

            // Switch HFRC LL MUX back to CLK_GEN if AUDADC clock gen mux was
            // OFF
            if ( HALSTATE_b.AUDADC_CLKGEN_OFF )
            {
                MCUCTRL->PLLMUXCTL_b.AUDADCPLLCLKSEL = MCUCTRL_PLLMUXCTL_AUDADCPLLCLKSEL_CLKGEN;
                am_hal_sysctrl_sysbus_write_flush();
            }

            // Wait for LL Mux to be completed
            am_hal_delay_us(20);

            //Disable clock we have previously enabled
            PDMn(0)->CTRL_b.CLKEN = 1;
            I2Sn(0)->CLKCFG_b.MCLKEN = 1;
            I2Sn(1)->CLKCFG_b.MCLKEN = 1;
            USBn(0)->CLKCTRL_b.PHYREFCLKDIS = 0;

            // Power off PDM, I2S, AUDADC, and USB
            am_hal_pwrctrl_periph_disable(AM_HAL_PWRCTRL_PERIPH_PDM0);
            am_hal_pwrctrl_periph_disable(AM_HAL_PWRCTRL_PERIPH_I2S0);
            am_hal_pwrctrl_periph_disable(AM_HAL_PWRCTRL_PERIPH_I2S1);
            am_hal_pwrctrl_periph_disable(AM_HAL_PWRCTRL_PERIPH_AUDADC);
            am_hal_pwrctrl_periph_disable(AM_HAL_PWRCTRL_PERIPH_USB);
            am_hal_pwrctrl_periph_disable(AM_HAL_PWRCTRL_PERIPH_USBPHY);

            // ----------------------------------------------------------------
            // Stage 3: Revert Clock Settings
            // ----------------------------------------------------------------
            // if PLL was enabled, power it off
            if (HALSTATE_b.PLL_NEEDED)
            {
                SYSPLLn(0)->PLLCTL0_b.SYSPLLPDB      = MCUCTRL_PLLCTL0_SYSPLLPDB_DISABLE;
                SYSPLLn(0)->PLLCTL0_b.BYPASS         = 0;
                SYSPLLn(0)->PLLCTL0_b.FREFSEL        = MCUCTRL_PLLCTL0_FREFSEL_XTAL32MHz;
                SYSPLLn(0)->PLLCTL0_b.FOUT4PHASEPD   = MCUCTRL_PLLCTL0_FOUT4PHASEPD_POWERDOWN;
                SYSPLLn(0)->PLLCTL0_b.FOUTPOSTDIVPD  = MCUCTRL_PLLCTL0_FOUTPOSTDIVPD_POWERDOWN;
                am_hal_pwrctrl_syspll_disable();
            }

            // if EXTCLK was enabled, revert pin config
            if (HALSTATE_b.EXTCLK_NEEDED ||
                (HALSTATE_b.PLL_NEEDED && HALSTATE_b.PLL_FREFSEL == MCUCTRL_PLLCTL0_FREFSEL_EXTREFCLK))
            {
                if (sClkmgrBoardInfo.bIsSipEnabled)
                {
                    //
                    // Stop clock from SIP
                    //
                    am_hal_gpio_output_clear(136);
                }
                am_hal_gpio_pinconfig(15, sGpio15Cfg);
            }

            // If XTAL was started, power XTAL off
            if (HALSTATE_b.XTAL_NEEDED ||
                (HALSTATE_b.PLL_NEEDED && HALSTATE_b.PLL_FREFSEL == MCUCTRL_PLLCTL0_FREFSEL_XTAL32MHz))
            {
                bool bFalse = false;
                am_hal_mcuctrl_control(AM_HAL_MCUCTRL_CONTROL_EXTCLK32M_DISABLE, &bFalse);
            }

            // If HFRC2 was forced enabled, release the force
            if (HALSTATE_b.HFRC2_NEEDED)
            {
                CLKGEN->MISC_b.FRCHFRC2 = CLKGEN_MISC_FRCHFRC2_NOFRC;
            }

            // If HFRC_DED was forced enabled, release the force
            if (HALSTATE_b.AUDADC_CLKGEN_OFF || HALSTATE_b.HFRC_DED_NEEDED)
            {
                *(volatile uint32_t*)0x400200C0 &= ~((uint32_t)0x00000001);
            }
        }
    }

    // Reinitialize clock mux memory
    HALSTATE = 0;
    HALSTATE_b.SIGNATURE = SYSCTRL_CLKMUXRST_SIGNATURE;
}
//! @endcond SYSCTRL_CLK_MUX_RESET

//*****************************************************************************
//
// End Doxygen group.
//! @}
//
//*****************************************************************************
