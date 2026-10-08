//*****************************************************************************
//
//! @file am_hal_stimer.c
//!
//! @brief Functions for interfacing with the system timer (STIMER).
//!
//! @addtogroup stimer5_ap510 STIMER - System Timer
//! @ingroup apollo510_hal
//! @{
//!
//! Purpose: This module provides system timer functionality for Apollo5
//! devices, supporting precise timing, compare operations, capture
//! functionality, and interrupt generation. It enables accurate system
//! timing and event synchronization for applications requiring
//! deterministic timing behavior.
//!
//! @section hal_stimer_features Key Features
//!
//! 1. @b Flexible @b Clock @b Sources: Support for multiple clock sources and frequencies.
//! 2. @b Compare @b Events: Multiple compare channels for precise timing control.
//! 3. @b Capture @b Functionality: Input capture for measuring external signals.
//! 4. @b Interrupt @b Support: Comprehensive interrupt handling for timer events.
//! 5. @b NVRAM @b Storage: Non-volatile storage for timer configuration persistence.
//!
//! @section hal_stimer_functionality Functionality
//!
//! - Configure timer clock sources and operational modes
//! - Start, stop, and restart timer operations
//! - Read timer counter values and clear counters
//! - Set up compare events and delta timing
//! - Configure input capture for external signal measurement
//! - Handle timer interrupts and status monitoring
//!
//! @section hal_stimer_usage Usage
//!
//! 1. Configure the timer using am_hal_stimer_config()
//! 2. Start the timer with am_hal_stimer_start()
//! 3. Set up compare events or capture functionality as needed
//! 4. Handle timer interrupts and monitor status
//! 5. Stop or restart the timer as required
//!
//! @section hal_stimer_configuration Configuration
//!
//! - @b Clock @b Sources: Select from HFRC, XTAL, or LFRC clock sources
//! - @b Compare @b Channels: Configure up to 8 compare channels
//! - @b Capture @b Channels: Set up input capture for external signals
//! - @b Interrupts: Configure interrupt sources and handlers
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

//
//! Timer Currently Configured
//
static bool g_bStimerConfigured = false;

//
//! Time at which last delta was set
//
static uint32_t g_ui32LastStimer[8] =
{
    0xFFFFFFFE, 0xFFFFFFFE, 0xFFFFFFFE, 0xFFFFFFFE,
    0xFFFFFFFE, 0xFFFFFFFE, 0xFFFFFFFE, 0xFFFFFFFE
};

//*****************************************************************************
//
//! @brief Get clock source for STIMER configuration.
//!
//! @param clk - STIMER clock selection value.
//!
//! @return Returns the corresponding clock manager clock ID.
//
//*****************************************************************************
static am_hal_clkmgr_clock_id_e
am_hal_stimer_clksrc_get(uint32_t clk)
{
    switch(clk)
    {
        case STIMER_STCFG_CLKSEL_HFRC_6MHZ:
        case STIMER_STCFG_CLKSEL_HFRC_375KHZ:
            return AM_HAL_CLKMGR_CLK_ID_HFRC;
#ifdef AM_HAL_CLKMGR_MANAGE_XTAL_LS
        case STIMER_STCFG_CLKSEL_XTAL_32KHZ:
        case STIMER_STCFG_CLKSEL_XTAL_16KHZ:
        case STIMER_STCFG_CLKSEL_XTAL_1KHZ:
            return AM_HAL_CLKMGR_CLK_ID_XTAL_LS;
#endif
        case STIMER_STCFG_CLKSEL_LFRC_NOMINAL:
            return AM_HAL_CLKMGR_CLK_ID_LFRC;
        default:
            return AM_HAL_CLKMGR_CLK_ID_MAX;
    }
}

//*****************************************************************************
//
// Set up the stimer.
//
// This function should be used to perform the initial set-up of the
// stimer.
//
//*****************************************************************************
uint32_t
am_hal_stimer_config(uint32_t ui32STimerConfig)
{
    uint32_t ui32CurrVal;
    uint32_t ui32CfgClkSel, ui32PreClkSel;
    uint32_t ui32CfgClkSrc, ui32PreClkSrc;
    bool bCfgClkRequest;
    bool bPreClkRelease;

    //
    // Read the current config
    //
    ui32CurrVal = STIMER->STCFG;

    ui32CfgClkSel = ui32STimerConfig & STIMER_STCFG_CLKSEL_Msk;
    ui32PreClkSel = ui32CurrVal & STIMER_STCFG_CLKSEL_Msk;
    ui32CfgClkSrc = (uint32_t)am_hal_stimer_clksrc_get(ui32CfgClkSel);
    ui32PreClkSrc = (uint32_t)am_hal_stimer_clksrc_get(ui32PreClkSel);

    if ( ((ui32STimerConfig & STIMER_STCFG_CLEAR_Msk) == STIMER_STCFG_CLEAR_RUN) && ((ui32STimerConfig & STIMER_STCFG_FREEZE_Msk) == STIMER_STCFG_FREEZE_THAW) )
    {
        if ( ((ui32CurrVal & STIMER_STCFG_CLEAR_Msk) == STIMER_STCFG_CLEAR_RUN) && ((ui32CurrVal & STIMER_STCFG_FREEZE_Msk) == STIMER_STCFG_FREEZE_THAW) )
        {
            if ( ui32CfgClkSrc != ui32PreClkSrc )
            {
                bCfgClkRequest = true;
                bPreClkRelease = true;
            }
            else
            {
                bCfgClkRequest = false;
                bPreClkRelease = false;
            }
        }
        else
        {
            bCfgClkRequest = true;
            bPreClkRelease = false;
        }
    }
    else
    {
        bCfgClkRequest = false;
        bPreClkRelease = true;
    }

    if ( bCfgClkRequest )
    {
        //
        // Request a clock
        //
        if ( STIMER_STCFG_CLKSEL_HFRC_6MHZ <= ui32CfgClkSel && ui32CfgClkSel <= STIMER_STCFG_CLKSEL_LFRC_NOMINAL )
        {
            am_hal_clkmgr_clock_request((am_hal_clkmgr_clock_id_e)ui32CfgClkSrc, AM_HAL_CLKMGR_USER_ID_STIMER);
        }
    }

    //
    // Write our configuration value.
    //
    STIMER->STCFG = ui32STimerConfig;

    if ( bPreClkRelease )
    {
        //
        // Release the previous clock source
        //
        if ( STIMER_STCFG_CLKSEL_HFRC_6MHZ <= ui32PreClkSel && ui32PreClkSel <= STIMER_STCFG_CLKSEL_LFRC_NOMINAL )
        {
            am_hal_clkmgr_clock_release((am_hal_clkmgr_clock_id_e)ui32PreClkSrc, AM_HAL_CLKMGR_USER_ID_STIMER);
        }
    }

    //
    // Indication that the STIMER has been configured.
    //
    g_bStimerConfigured = true;

    return ui32CurrVal;
}

//*****************************************************************************
//
// Check if the STIMER is running.
//
// This function should be used to perform the initial set-up of the
// stimer.
//
//*****************************************************************************
bool
am_hal_stimer_is_running(void)
{
    bool bRetVal;

    AM_CRITICAL_BEGIN

    //
    // Check the STIMER has been configured and is currently counting
    //
    bRetVal = g_bStimerConfigured &&
      ((STIMER->STCFG &
       (STIMER_STCFG_CLKSEL_NOCLK | STIMER_STCFG_FREEZE_THAW | STIMER_STCFG_CLEAR_RUN)) ==
       (STIMER_STCFG_FREEZE_THAW | STIMER_STCFG_CLEAR_RUN));

    AM_CRITICAL_END

    return bRetVal;
}

//*****************************************************************************
//
// Reset the current stimer block to power-up state.
//
//*****************************************************************************
void
am_hal_stimer_reset_config(void)
{
    bool bClkRelease = false;
    uint32_t ui32ClkSel = 0;

    if ( am_hal_stimer_is_running() )
    {
        ui32ClkSel = STIMER->STCFG_b.CLKSEL;
        if ( ui32ClkSel <= STIMER_STCFG_CLKSEL_LFRC_NOMINAL )
        {
            bClkRelease = true;
        }
    }

    STIMER->STCFG       = _VAL2FLD(STIMER_STCFG_FREEZE, 1);
    STIMER->SCAPCTRL0   = _VAL2FLD(STIMER_SCAPCTRL0_STSEL0, 0xFF);
    STIMER->SCAPCTRL1   = _VAL2FLD(STIMER_SCAPCTRL1_STSEL1, 0xFF);
    STIMER->SCAPCTRL2   = _VAL2FLD(STIMER_SCAPCTRL2_STSEL2, 0xFF);
    STIMER->SCAPCTRL3   = _VAL2FLD(STIMER_SCAPCTRL3_STSEL3, 0xFF);
    STIMER->SCMPR0      = 0;
    STIMER->SCMPR1      = 0;
    STIMER->SCMPR2      = 0;
    STIMER->SCMPR3      = 0;
    STIMER->SCMPR4      = 0;
    STIMER->SCMPR5      = 0;
    STIMER->SCMPR6      = 0;
    STIMER->SCMPR7      = 0;
    STIMER->SCAPT0      = 0;
    STIMER->SCAPT1      = 0;
    STIMER->SCAPT2      = 0;
    STIMER->SCAPT3      = 0;
    STIMER->SNVR0       = 0;
    STIMER->SNVR1       = 0;
    STIMER->STMINTEN    = 0;
    STIMER->STMINTSTAT   = 0;
    STIMER->STMINTCLR    = 0xFFF;

    if ( bClkRelease )
    {
        am_hal_clkmgr_clock_release(am_hal_stimer_clksrc_get(ui32ClkSel), AM_HAL_CLKMGR_USER_ID_STIMER);
    }
}

//*****************************************************************************
//
// Get the current stimer value.
//
// This function can be used to read, uninvasively, the value in the stimer.
//
//*****************************************************************************
uint32_t
am_hal_stimer_counter_get(void)
{
    uint32_t      ui32TimerAddr = (uint32_t)&STIMER->STTMR;
    uint32_t      ui32TimerVals[3];

    //
    // Read the register into ui32TimerVals[].
    //
    am_hal_triple_read(ui32TimerAddr, ui32TimerVals);

    //
    // Now determine which of the three values is the correct value.
    // If the first 2 match, then the values are both correct and we're done.
    // Otherwise, the third value is taken to be the correct value.
    //
    if ( ui32TimerVals[0] == ui32TimerVals[1] )
    {
        //
        // If the first two values match, then neither one was a bad read.
        // We'll take this as the current time.
        //
        return ui32TimerVals[1];
    }
    else
    {
        return ui32TimerVals[2];
    }
}

//*****************************************************************************
//
// Clear the stimer counter.
//
// This function clears the STimer Counter and leaves the stimer running.
//
//*****************************************************************************
void
am_hal_stimer_counter_clear(void)
{
    //
    // Start a critical section to ensure atomic operation
    //
    AM_CRITICAL_BEGIN

    //
    // Set the clear bit
    //
    STIMER->STCFG |= STIMER_STCFG_CLEAR_Msk;

    //
    // Reset the clear bit
    //
    STIMER->STCFG &= ~STIMER_STCFG_CLEAR_Msk;

    //
    // End the critical section
    //
    AM_CRITICAL_END
}

//*****************************************************************************
//
// Check if the compare value can be set without blocking.
//
//*****************************************************************************
bool
am_hal_stimer_check_compare_delta_set(uint32_t ui32CmprInstance)
{
#ifndef AM_HAL_DISABLE_API_VALIDATION
    if ( ui32CmprInstance > 7 )
    {
        return AM_HAL_STATUS_OUT_OF_RANGE;
    }
#endif
    uint32_t curTimer;

    //
    // Take a snapshot of STIMER
    //
    curTimer = am_hal_stimer_counter_get();

    //
    // We cannot set COMPARE back to back
    // Need to wait for previous write to complete, which takes 2 cycles
    //
    if ((curTimer != g_ui32LastStimer[ui32CmprInstance]) &&
        (curTimer != (g_ui32LastStimer[ui32CmprInstance] + 1)))
    {
        return true;
    }
    else
    {
        return false;
    }
}

//*****************************************************************************
//
// Set the compare value.
//
//*****************************************************************************
uint32_t
am_hal_stimer_compare_delta_set(uint32_t ui32CmprInstance, uint32_t ui32Delta)
{
#ifndef AM_HAL_DISABLE_API_VALIDATION
    if ( ui32CmprInstance > 7 )
    {
        return AM_HAL_STATUS_OUT_OF_RANGE;
    }
#endif
    uint32_t curTimer, curTimer0;
    uint32_t ui32Ret = AM_HAL_STATUS_SUCCESS;

    //
    // Take a snapshot of STIMER at the beginning of the function
    //
    curTimer = curTimer0 = am_hal_stimer_counter_get();

    //
    //! @note Due to latency in write to COMPARE register to take effect, it is
    //!  possible that the application could get a stale interrupt even after
    //!  this API returns (a result of previous value of COMPARE).
    //!
    //! The application needs to handle these cases gracefully.
    //

    do
    {
        // We cannot set COMPARE back to back
        // Need to wait for previous write to complete, which takes 2 cycles
        if ((curTimer != g_ui32LastStimer[ui32CmprInstance]) &&
            (curTimer != (g_ui32LastStimer[ui32CmprInstance] + 1)))
        {
            //
            // Start a critical section.
            //
            AM_CRITICAL_BEGIN

            curTimer = am_hal_stimer_counter_get();

            // Adjust Delta
            // It takes 2 STIMER clock cycles for writes to COMPARE to be effective
            // Also the interrupt itself is delayed by a cycle
            // This effectively means we need to adjust the delta by 3
            // Also adjust for the delay since we entered the function
            if (ui32Delta > (3 + (curTimer - curTimer0)))
            {
                ui32Delta -= 3 + (curTimer - curTimer0);
            }
            else
            {
                //
                // Need to floor delta to 1
                //
                ui32Delta = 1;
                ui32Ret = AM_HAL_STIMER_DELTA_TOO_SMALL;
            }

            //
            // Set the delta
            //
            AM_REGVAL(AM_REG_STIMER_COMPARE(0, ui32CmprInstance)) = ui32Delta;

            //
            // Get a snapshot when we set COMPARE
            //
            g_ui32LastStimer[ui32CmprInstance] = am_hal_stimer_counter_get();

            //
            // End the critical section.
            //
            AM_CRITICAL_END
            break;
        }
        curTimer = am_hal_stimer_counter_get();
    } while (1);

    return ui32Ret;
}

//*****************************************************************************
//
// Get the current stimer compare register value.
//
// This function can be used to read the value in an stimer compare register.
//
//*****************************************************************************
uint32_t
am_hal_stimer_compare_get(uint32_t ui32CmprInstance)
{
#ifndef AM_HAL_DISABLE_API_VALIDATION
    if ( ui32CmprInstance > 7 )
    {
        return AM_HAL_STATUS_OUT_OF_RANGE;
    }
#endif
    uint32_t curTimer;

    //
    // Need to wait at least 3 cycle after setting the compare to read it
    // reliably
    //
    do
    {
        curTimer = am_hal_stimer_counter_get();
        if ((curTimer != g_ui32LastStimer[ui32CmprInstance]) &&
            (curTimer != (g_ui32LastStimer[ui32CmprInstance] + 1)) &&
            (curTimer != (g_ui32LastStimer[ui32CmprInstance] + 2)))
        {
            return AM_REGVAL(AM_REG_STIMER_COMPARE(0, ui32CmprInstance));
        }
    } while (1);
}

//*****************************************************************************
//
// Start capturing data with the specified capture register.
//
// Use this function to start capturing.
//
//*****************************************************************************
void
am_hal_stimer_capture_start(uint32_t ui32CaptureNum,
                            uint32_t ui32GPIONumber,
                            bool bPolarity)
{
#ifndef AM_HAL_DISABLE_API_VALIDATION
    if ( ui32CaptureNum > 3 )
    {
        return;
    }

    if (ui32GPIONumber > (AM_HAL_GPIO_MAX_PADS-1))
    {
        return;
    }
#endif

    //
    // Set the polarity and pin selection in the GPIO block.
    //
    switch (ui32CaptureNum)
    {
         case 0:
            STIMER->SCAPCTRL0_b.STPOL0 = bPolarity;
            STIMER->SCAPCTRL0_b.STSEL0 = ui32GPIONumber;
            STIMER->SCAPCTRL0_b.CAPTURE0 = STIMER_SCAPCTRL0_CAPTURE0_ENABLE;
            break;
         case 1:
            STIMER->SCAPCTRL1_b.STPOL1 = bPolarity;
            STIMER->SCAPCTRL1_b.STSEL1 = ui32GPIONumber;
            STIMER->SCAPCTRL1_b.CAPTURE1 = STIMER_SCAPCTRL1_CAPTURE1_ENABLE;
            break;
         case 2:
            STIMER->SCAPCTRL2_b.STPOL2 = bPolarity;
            STIMER->SCAPCTRL2_b.STSEL2 = ui32GPIONumber;
            STIMER->SCAPCTRL2_b.CAPTURE2 = STIMER_SCAPCTRL2_CAPTURE2_ENABLE;
            break;
         case 3:
            STIMER->SCAPCTRL3_b.STPOL3 = bPolarity;
            STIMER->SCAPCTRL3_b.STSEL3 = ui32GPIONumber;
            STIMER->SCAPCTRL3_b.CAPTURE3 = STIMER_SCAPCTRL3_CAPTURE3_ENABLE;
            break;
         default:
            return;
    }

    //
    // Start a critical section.
    //
    AM_CRITICAL_BEGIN

    //
    // Set TIMER Global Enable for GPIO inputs.
    //
    TIMER->GLOBEN_b.ENABLEALLINPUTS = 1;

    //
    // End the critical section.
    //
    AM_CRITICAL_END
}

//*****************************************************************************
//
// Stop capturing data with the specified capture register.
//
// Use this function to stop capturing.
//
//*****************************************************************************
void
am_hal_stimer_capture_stop(uint32_t ui32CaptureNum)
{
#ifndef AM_HAL_DISABLE_API_VALIDATION
    if ( ui32CaptureNum > 3 )
    {
        return;
    }
#endif
    switch (ui32CaptureNum)
    {
        case 0:
            STIMER->SCAPCTRL0_b.CAPTURE0 = STIMER_SCAPCTRL0_CAPTURE0_DISABLE;
            break;
        case 1:
            STIMER->SCAPCTRL1_b.CAPTURE1 = STIMER_SCAPCTRL1_CAPTURE1_DISABLE;
            break;
        case 2:
            STIMER->SCAPCTRL2_b.CAPTURE2 = STIMER_SCAPCTRL2_CAPTURE2_DISABLE;
            break;
        case 3:
            STIMER->SCAPCTRL3_b.CAPTURE3 = STIMER_SCAPCTRL3_CAPTURE3_DISABLE;
            break;
        default:
            return;
    }

    //
    // Start a critical section.
    //
    AM_CRITICAL_BEGIN

    //
    // Set TIMER Global Disable for GPIO inputs if all are DISABLED.
    //
    if ((STIMER->SCAPCTRL0_b.CAPTURE0 == STIMER_SCAPCTRL0_CAPTURE0_DISABLE) &&
            (STIMER->SCAPCTRL1_b.CAPTURE1 == STIMER_SCAPCTRL1_CAPTURE1_DISABLE) &&
            (STIMER->SCAPCTRL2_b.CAPTURE2 == STIMER_SCAPCTRL2_CAPTURE2_DISABLE) &&
            (STIMER->SCAPCTRL3_b.CAPTURE3 == STIMER_SCAPCTRL3_CAPTURE3_DISABLE))
    {
        TIMER->GLOBEN_b.ENABLEALLINPUTS = 0;
    }

    //
    // End the critical section.
    //
    AM_CRITICAL_END
}

//*****************************************************************************
//
// Set the current stimer nvram register value.
//
// This function can be used to read the value in an stimer NVRAM register.
//
//*****************************************************************************
void
am_hal_stimer_nvram_set(uint32_t ui32NvramNum, uint32_t ui32NvramVal)
{
#ifndef AM_HAL_DISABLE_API_VALIDATION
    if ( ui32NvramNum > 3 )
    {
        return;
    }
#endif

    AM_REGVAL(AM_REG_STIMER_NVRAM(0, ui32NvramNum)) = ui32NvramVal;
}

//*****************************************************************************
//
// Get the current stimer nvram register value.
//
// This function can be used to read the value in an stimer NVRAM register.
//
//*****************************************************************************
uint32_t am_hal_stimer_nvram_get(uint32_t ui32NvramNum)
{
#ifndef AM_HAL_DISABLE_API_VALIDATION
    if ( ui32NvramNum > 3 )
    {
        return 0;
    }
#endif

    return AM_REGVAL(AM_REG_STIMER_NVRAM(0, ui32NvramNum));
}

//*****************************************************************************
//
// Get the current stimer capture register value.
//
// This function can be used to read the value in an stimer capture register.
//
//*****************************************************************************
uint32_t am_hal_stimer_capture_get(uint32_t ui32CaptureNum)
{
#ifndef AM_HAL_DISABLE_API_VALIDATION
    if ( ui32CaptureNum > 3 )
    {
        return AM_HAL_STATUS_OUT_OF_RANGE;
    }
#endif


    return AM_REGVAL(AM_REG_STIMER_CAPTURE(0, ui32CaptureNum));
}

//*****************************************************************************
//
// Enables the selected system timer interrupt.
//
// This function will enable the selected interrupts in the STIMER interrupt
// enable register. In order to receive an interrupt from an stimer component,
// you will need to enable the interrupt for that component in this main
// register, as well as in the stimer configuration register (accessible though
// am_hal_stimer_config()), and in the NVIC.
//
//*****************************************************************************
void
am_hal_stimer_int_enable(uint32_t ui32Interrupt)
{
    //
    // Start a critical section to ensure atomic operation
    //
    AM_CRITICAL_BEGIN

    //
    // Enable the interrupt at the module level.
    //
    STIMER->STMINTEN |= ui32Interrupt;

    //
    // End the critical section
    //
    AM_CRITICAL_END
}

//*****************************************************************************
//
// Return the enabled stimer interrupts.
//
// This function will return all enabled interrupts in the STIMER
// interrupt enable register.
//
//*****************************************************************************
uint32_t
am_hal_stimer_int_enable_get(void)
{
    //
    // Return enabled interrupts.
    //
    return STIMER->STMINTEN;
}

//*****************************************************************************
//
// Disables the selected stimer interrupt.
//
// This function will disable the selected interrupts in the STIMER
// interrupt register.
//
//*****************************************************************************
void
am_hal_stimer_int_disable(uint32_t ui32Interrupt)
{
    //
    // Start a critical section
    //
    AM_CRITICAL_BEGIN

    //
    // Disable the interrupt at the module level.
    //
    STIMER->STMINTEN &= ~ui32Interrupt;

    //
    // End the critical section
    //
    AM_CRITICAL_END
}

//*****************************************************************************
//
// Sets the selected stimer interrupt.
//
// This function will set the selected interrupts in the STIMER
// interrupt register.
//
//*****************************************************************************
void
am_hal_stimer_int_set(uint32_t ui32Interrupt)
{
    //
    // Start a critical section
    //
    AM_CRITICAL_BEGIN

    //
    // Set the interrupts.
    //
    STIMER->STMINTSET = ui32Interrupt;

    //
    // End the critical section
    //
    AM_CRITICAL_END
}

//*****************************************************************************
//
// Clears the selected stimer interrupt.
//
// This function will clear the selected interrupts in the STIMER
// interrupt register.
//
//*****************************************************************************
void
am_hal_stimer_int_clear(uint32_t ui32Interrupt)
{
    //
    // Start a critical section
    //
    AM_CRITICAL_BEGIN

    //
    // Clear the interrupts.
    //
    STIMER->STMINTCLR = ui32Interrupt;

    //
    // Memory barrier to ensure the clear operation completes
    //
    AM_REGVAL(&STIMER->STMINTSTAT);

    //
    // End the critical section
    //
    AM_CRITICAL_END
}

//*****************************************************************************
//
// Returns either the enabled or raw stimer interrupt status.
//
// This function will return the stimer interrupt status.
//
//*****************************************************************************
uint32_t
am_hal_stimer_int_status_get(bool bEnabledOnly)
{
    if ( bEnabledOnly )
    {
        uint32_t ui32RetVal;

        //
        // Start a critical section
        //
        AM_CRITICAL_BEGIN


        ui32RetVal = STIMER->STMINTSTAT;
        ui32RetVal &= STIMER->STMINTEN;

        //
        // End the critical section
        //
        AM_CRITICAL_END

        return ui32RetVal;
    }
    else
    {
        return STIMER->STMINTSTAT;
    }
}

//*****************************************************************************
//
// End Doxygen group.
//! @}
//
//*****************************************************************************
