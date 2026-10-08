//*****************************************************************************
//
//! @file am_hal_syspll.c
//!
//! @brief Functions for interfacing with the System PLL.
//!
//! @addtogroup syspll_ap510 SYSPLL - System PLL
//! @ingroup apollo510_hal
//! @{
//!
//! Purpose: This module provides comprehensive functions for interfacing with
//!          the System PLL (Phase-Locked Loop) on Apollo5 devices. It supports
//!          PLL configuration, frequency generation, lock management, and clock
//!          multiplexing for precise clock generation and distribution.
//!
//! @section hal_syspll_features Key Features
//!
//! 1. @b PLL @b Configuration: Flexible PLL parameter configuration.
//! 2. @b Frequency @b Generation: Precise frequency generation and control.
//! 3. @b Lock @b Management: PLL lock detection and wait functionality.
//! 4. @b Clock @b Multiplexing: Support for multiple clock source selection.
//! 5. @b Bypass @b Mode: PLL bypass functionality for direct clock routing.
//!
//! @section hal_syspll_functionality Functionality
//!
//! - Initialize and configure System PLL
//! - Generate precise clock frequencies
//! - Handle PLL lock detection and management
//! - Support clock multiplexing and selection
//! - Enable/disable PLL and bypass modes
//!
//! @section hal_syspll_usage Usage
//!
//! 1. Initialize PLL using am_hal_syspll_initialize()
//! 2. Configure PLL parameters and frequencies
//! 3. Enable PLL and wait for lock
//! 4. Configure clock multiplexing as needed
//! 5. Disable PLL when no longer needed
//!
//! @section hal_syspll_configuration Configuration
//!
//! - @b PLL @b Parameters: Configure reference and feedback dividers
//! - @b Frequency @b Settings: Set up output frequencies and VCO ranges
//! - @b Lock @b Timing: Configure lock detection and wait times
//! - @b Clock @b Sources: Set up clock multiplexing and selection
//
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
#include <float.h>
#include <math.h>
#include "am_mcu_apollo.h"
#include "am_hal_sysctrl_clk_mux_reset.h"

//*****************************************************************************
//
// Local defines
//
//*****************************************************************************
#define AM_HAL_SYSPLL_GCD_CALC_MAX_LOOP (16)
#define AM_HAL_SYSPLL_MODULE_NUM        (0)

//
// Minimum Frequency for System PLL clock source expected. This is used to
// calculate PLL lock wait time. Reduce this value if System PLL is configured
// to take in clock slower than the one defined below
//
#define AM_HAL_SYSPLL_CLOCK_SRC_MIN_MHZ (12)

//
// System PLL Lock time Maximum Cycle Count
//
#define AM_HAL_SYSPLL_MAX_LOCK_CYCLE_VCOSEL0 (1000)
#define AM_HAL_SYSPLL_MAX_LOCK_CYCLE_VCOSEL1 (1875)

//
// Table to convert POSTDIV divider needed to POSTDIV1 and POSTDIV2
//
static const uint8_t am_hal_syspll_postdiv_to_divider_table[50] =
    {
        0x00, 0x11, 0x21, 0x31, 0x41, 0x51, 0x61, 0x71, 0x42, 0x33,
        0x52, 0x62, 0x62, 0x72, 0x72, 0x53, 0x44, 0x63, 0x63, 0x54,
        0x54, 0x73, 0x64, 0x64, 0x64, 0x55, 0x74, 0x74, 0x74, 0x65,
        0x65, 0x75, 0x75, 0x75, 0x75, 0x75, 0x66, 0x76, 0x76, 0x76,
        0x76, 0x76, 0x76, 0x77, 0x77, 0x77, 0x77, 0x77, 0x77, 0x77
    };

//
// Constants used to decide which generated config should be used
//
const uint32_t AM_HAL_SYSPLL_CFG_PTS_A[4] = { 435700, 465700, 131525, 139025 };
const uint32_t AM_HAL_SYSPLL_CFG_PTS_B[4] = { 228000, 396000, 228000, 396000 };

//*****************************************************************************
//
// Macros
//
//*****************************************************************************
#define UI32_HZ_TO_FLT_MHZ(x)  (((float)x) / 1000000)
#define UI32_MHZ_TO_UI32_HZ(x) (x*1000000)

//*****************************************************************************
//
//! @name System PLL magic number macros for handle verification.
//! @{
//
//*****************************************************************************
#define AM_HAL_MAGIC_SYSPLL            0x504C30
#define AM_HAL_SYSPLL_CHK_HANDLE(h)    ((h) && ((am_hal_handle_prefix_t *)(h))->s.bInit && (((am_hal_handle_prefix_t *)(h))->s.magic == AM_HAL_MAGIC_SYSPLL))
//! @}

//*****************************************************************************
//
//! Structure for handling SYSPLL HAL state information.
//
//*****************************************************************************
typedef struct
{
    //
    //! Handle validation prefix.
    //
    am_hal_handle_prefix_t           prefix;

    //
    //! Physical module number.
    //
    uint32_t                    ui32Module;

}am_hal_syspll_state_t;

//*****************************************************************************
//
//! Conversion Table to convert syspll LLMUX selection to LL clock mux
//
//*****************************************************************************
const am_hal_syspll_mux_e ui8SysPllMuxSelToMux[AM_HAL_SYSPLL_LLMUX_SELECT_MAX] =
{
    AM_HAL_SYSPLL_LLMUX_PDM,    // AM_HAL_SYSPLL_LLMUX_PDM_SRC_PLL
    AM_HAL_SYSPLL_LLMUX_PDM,    // AM_HAL_SYSPLL_LLMUX_PDM_SRC_HFRC
    AM_HAL_SYSPLL_LLMUX_PDM,    // AM_HAL_SYSPLL_LLMUX_PDM_SRC_CLKGEN
    AM_HAL_SYSPLL_LLMUX_AUDADC, // AM_HAL_SYSPLL_LLMUX_AUDADC_SRC_PLL
    AM_HAL_SYSPLL_LLMUX_AUDADC, // AM_HAL_SYSPLL_LLMUX_AUDADC_SRC_HFRC
    AM_HAL_SYSPLL_LLMUX_AUDADC, // AM_HAL_SYSPLL_LLMUX_AUDADC_SRC_CLKGEN
    AM_HAL_SYSPLL_LLMUX_USB,    // AM_HAL_SYSPLL_LLMUX_USB_SRC_PLL
    AM_HAL_SYSPLL_LLMUX_USB,    // AM_HAL_SYSPLL_LLMUX_USB_SRC_CLKGEN
    AM_HAL_SYSPLL_LLMUX_I2S0,   // AM_HAL_SYSPLL_LLMUX_I2S0_SRC_PLL_FOUT4
    AM_HAL_SYSPLL_LLMUX_I2S0,   // AM_HAL_SYSPLL_LLMUX_I2S0_SRC_PLL_FOUT3
    AM_HAL_SYSPLL_LLMUX_I2S0,   // AM_HAL_SYSPLL_LLMUX_I2S0_SRC_CLKGEN
    AM_HAL_SYSPLL_LLMUX_I2S1,   // AM_HAL_SYSPLL_LLMUX_I2S1_SRC_PLL_FOUT4
    AM_HAL_SYSPLL_LLMUX_I2S1,   // AM_HAL_SYSPLL_LLMUX_I2S1_SRC_PLL_FOUT3
    AM_HAL_SYSPLL_LLMUX_I2S1,   // AM_HAL_SYSPLL_LLMUX_I2S1_SRC_CLKGEN
};

//*****************************************************************************
//
//! Conversion Table to convert syspll LLMUX selection to LL clock mux control
//! values
//
//*****************************************************************************
const uint8_t ui8SysPllMuxSelToMuxCtl[AM_HAL_SYSPLL_LLMUX_SELECT_MAX] =
{
    (uint8_t)MCUCTRL_PLLMUXCTL_PDMPLLCLKSEL_PLL,         // AM_HAL_SYSPLL_LLMUX_PDM_SRC_PLL
    (uint8_t)MCUCTRL_PLLMUXCTL_PDMPLLCLKSEL_HFRC,        // AM_HAL_SYSPLL_LLMUX_PDM_SRC_HFRC
    (uint8_t)MCUCTRL_PLLMUXCTL_PDMPLLCLKSEL_CLKGEN,      // AM_HAL_SYSPLL_LLMUX_PDM_SRC_CLKGEN
    (uint8_t)MCUCTRL_PLLMUXCTL_AUDADCPLLCLKSEL_PLL,      // AM_HAL_SYSPLL_LLMUX_AUDADC_SRC_PLL
    (uint8_t)MCUCTRL_PLLMUXCTL_AUDADCPLLCLKSEL_HFRC,     // AM_HAL_SYSPLL_LLMUX_AUDADC_SRC_HFRC
    (uint8_t)MCUCTRL_PLLMUXCTL_AUDADCPLLCLKSEL_CLKGEN,   // AM_HAL_SYSPLL_LLMUX_AUDADC_SRC_CLKGEN
    (uint8_t)MCUCTRL_PLLMUXCTL_USBPLLCLKSEL_PLL,         // AM_HAL_SYSPLL_LLMUX_USB_SRC_PLL
    (uint8_t)MCUCTRL_PLLMUXCTL_USBPLLCLKSEL_CLKGEN,      // AM_HAL_SYSPLL_LLMUX_USB_SRC_CLKGEN
    (uint8_t)MCUCTRL_PLLMUXCTL_I2S0PLLCLKSEL_PLLFOUT4,   // AM_HAL_SYSPLL_LLMUX_I2S0_SRC_PLL_FOUT4
    (uint8_t)MCUCTRL_PLLMUXCTL_I2S0PLLCLKSEL_PLLFOUT3,   // AM_HAL_SYSPLL_LLMUX_I2S0_SRC_PLL_FOUT3
    (uint8_t)MCUCTRL_PLLMUXCTL_I2S0PLLCLKSEL_CLKGEN,     // AM_HAL_SYSPLL_LLMUX_I2S0_SRC_CLKGEN
    (uint8_t)MCUCTRL_PLLMUXCTL_I2S1PLLCLKSEL_PLLFOUT4,   // AM_HAL_SYSPLL_LLMUX_I2S1_SRC_PLL_FOUT4
    (uint8_t)MCUCTRL_PLLMUXCTL_I2S1PLLCLKSEL_PLLFOUT3,   // AM_HAL_SYSPLL_LLMUX_I2S1_SRC_PLL_FOUT3
    (uint8_t)MCUCTRL_PLLMUXCTL_I2S1PLLCLKSEL_CLKGEN,     // AM_HAL_SYSPLL_LLMUX_I2S1_SRC_CLKGEN
};

//! @cond SYSCTRL_CLK_MUX_RESET
//*****************************************************************************
//
//! Conversion Table to convert syspll LLMUX selection to ClkMuxRst mux
//
//*****************************************************************************
const am_hal_sysctrl_clkmuxrst_clk_e ui8SysPllMuxToClkMuxRst[AM_HAL_SYSPLL_LLMUX_MAX] =
{
    SYSCTRL_CLKMUXRST_MUX_LL_PDM,    // AM_HAL_SYSPLL_LLMUX_PDM
    SYSCTRL_CLKMUXRST_MUX_LL_AUDADC, // AM_HAL_SYSPLL_LLMUX_AUDADC
    SYSCTRL_CLKMUXRST_MUX_LL_USB,    // AM_HAL_SYSPLL_LLMUX_USB
    SYSCTRL_CLKMUXRST_MUX_LL_I2S0,   // AM_HAL_SYSPLL_LLMUX_I2S0
    SYSCTRL_CLKMUXRST_MUX_LL_I2S1,   // AM_HAL_SYSPLL_LLMUX_I2S1
};

//*****************************************************************************
//
//! Conversion Table to convert syspll LLMUX selection to CLKMUXRST mux clock
//! source bitmap
//
//*****************************************************************************
const uint8_t ui8SysPllMuxSelToClkMuxRstClkSrcBm[AM_HAL_SYSPLL_LLMUX_SELECT_MAX] =
{
    SYSCTRL_CLKMUXRST_CLK_PLL,       // AM_HAL_SYSPLL_LLMUX_PDM_SRC_PLL
    SYSCTRL_CLKMUXRST_CLK_HFRC_DED,  // AM_HAL_SYSPLL_LLMUX_PDM_SRC_HFRC
    SYSCTRL_CLKMUXRST_CLK_CLKGEN,    // AM_HAL_SYSPLL_LLMUX_PDM_SRC_CLKGEN
    SYSCTRL_CLKMUXRST_CLK_PLL,       // AM_HAL_SYSPLL_LLMUX_AUDADC_SRC_PLL
    SYSCTRL_CLKMUXRST_CLK_HFRC_DED,  // AM_HAL_SYSPLL_LLMUX_AUDADC_SRC_HFRC
    SYSCTRL_CLKMUXRST_CLK_CLKGEN,    // AM_HAL_SYSPLL_LLMUX_AUDADC_SRC_CLKGEN
    SYSCTRL_CLKMUXRST_CLK_PLL,       // AM_HAL_SYSPLL_LLMUX_USB_SRC_PLL
    SYSCTRL_CLKMUXRST_CLK_CLKGEN,    // AM_HAL_SYSPLL_LLMUX_USB_SRC_CLKGEN
    SYSCTRL_CLKMUXRST_CLK_PLL,       // AM_HAL_SYSPLL_LLMUX_I2S0_SRC_PLL_FOUT4
    SYSCTRL_CLKMUXRST_CLK_PLL,       // AM_HAL_SYSPLL_LLMUX_I2S0_SRC_PLL_FOUT3
    SYSCTRL_CLKMUXRST_CLK_CLKGEN,    // AM_HAL_SYSPLL_LLMUX_I2S0_SRC_CLKGEN
    SYSCTRL_CLKMUXRST_CLK_PLL,       // AM_HAL_SYSPLL_LLMUX_I2S1_SRC_PLL_FOUT4
    SYSCTRL_CLKMUXRST_CLK_PLL,       // AM_HAL_SYSPLL_LLMUX_I2S1_SRC_PLL_FOUT3
    SYSCTRL_CLKMUXRST_CLK_CLKGEN,    // AM_HAL_SYSPLL_LLMUX_I2S1_SRC_CLKGEN
};
//! @endcond SYSCTRL_CLK_MUX_RESET

//*****************************************************************************
//
// Global Variables.
//
//*****************************************************************************
am_hal_syspll_state_t             g_SysPLLState[AM_REG_SYSPLL_NUM_MODULES];

//*****************************************************************************
//
//! @brief  convert syspll LLMUX selection to am_hal_syspll_mux_e
//!
//! @param eMuxSel - am_hal_syspll_mux_select_e value that indicates LL mux and
//!                  its selected clock source
//!
//! @return returns the syspll LL mux being selected by the LLMUX selection
//
//*****************************************************************************
static inline am_hal_syspll_mux_e
am_hal_syspll_muxsel_to_mux(am_hal_syspll_mux_select_e eMuxSel)
{
    return ui8SysPllMuxSelToMux[(uint8_t)eMuxSel];
}

//*****************************************************************************
//
//! @brief  convert syspll LLMUX selection to value to set into LL mux HW
//!         register
//!
//! @param eMuxSel - am_hal_syspll_mux_select_e value that indicates LL mux and
//!                  its selected clock source
//!
//! @return returns the value to be set into the corresponding LL mux register
//
//*****************************************************************************
static inline uint8_t
am_hal_syspll_muxsel_to_muxctl(am_hal_syspll_mux_select_e eMuxSel)
{
    return ui8SysPllMuxSelToMuxCtl[(uint8_t)eMuxSel];
}

//! @cond SYSCTRL_CLK_MUX_RESET
//*****************************************************************************
//
//! @brief convert syspll LLMUX selection to ClkMuxRst mux selection
//!
//! @param eMuxSel - am_hal_syspll_mux_select_e value that indicates LL mux and
//!                  its selected clock source
//!
//! @return returns the corresponding ClkMuxRst mux selection enum
//*****************************************************************************
static inline am_hal_sysctrl_clkmuxrst_clk_e
am_hal_syspll_spllmux_to_clkmuxrstmux(am_hal_syspll_mux_e spll_mux)
{
    if ( spll_mux >= AM_HAL_SYSPLL_LLMUX_MAX )
    {
        return SYSCTRL_CLKMUXRST_CLK_MAX;
    }
    return ui8SysPllMuxToClkMuxRst[(uint8_t)spll_mux];
}

//*****************************************************************************
//
//! @brief convert syspll LLMUX selection to ClkMuxRst clock source bitmap
//!
//! @param eMuxSel - am_hal_syspll_mux_select_e value that indicates LL mux and
//!                  its selected clock source
//!
//! @return returns the corresponding clock source bitmap for ClkMuxRst
//*****************************************************************************
static inline uint8_t
am_hal_syspll_muxsel_to_clkmuxrstclk(am_hal_syspll_mux_select_e eMuxSel)
{
    return ui8SysPllMuxSelToClkMuxRstClkSrcBm[(uint8_t)eMuxSel];
}

//! @endcond SYSCTRL_CLK_MUX_RESET

//*****************************************************************************
//
//! @brief  calculate the Greatest Common Divisor in float for the 2 float
//!         numbers provided.
//!
//! @param fA - first float number
//! @param fB - second float number
//!
//! @return returns positive Common divisor if it is found. Returns false
//!         otherwise.
//
//*****************************************************************************
static float syspll_config_util_gcd(float fA, float fB)
{
    uint8_t gcdLoop = 0;

    //
    // fA is expected to be greater than fB.
    // If fB is greater than fA, swap them
    //
    if (fA < fB)
    {
        float fTmp = fA;
        fA = fB;
        fB = fTmp;
    }

    //
    // GCD calculation loop
    //
    for (gcdLoop = 0; gcdLoop < AM_HAL_SYSPLL_GCD_CALC_MAX_LOOP; gcdLoop++)
    {
        //
        // If fB is zero, fA is the greatest Common Divisor
        //
        if (fB < FLT_EPSILON)
        {
            return fA;
        }
        //
        // Else, continue GCD calculation loop
        //
        else
        {
            float fTmp = fA - floorf(fA / fB) * fB;
            fA = fB;
            fB = fTmp;
        }
    }

    //
    // GCD not found after max loop, return -1.0 to indicate failure
    //
    return -1.0;

} // syspll_config_util_gcd()

//*****************************************************************************
//
//! @brief Check whether the output frequency specified can be generated using
//!        System PLL integer mode, and generate the configuration if it is
//!        feasible.
//!
//! @param fSrcClk        - source clock frequency in MHz
//! @param fDstClk        - targeted System PLL VCO Frequency in MHz
//! @param pui8RefDiv     - pointer to variable for Reference Clock Divide
//!                         output
//! @param pui16FBDivInt  - pointer to variable for Feedback Clock Divide
//!                         (integer part) output.
//! @param pui32FBDivFrac - pointer to variable for Feedback Clock Divide
//!                         (fraction part) output.
//!
//! @return found - returns true if fraction setting for the desired VCO
//!                 is available and written to the pointers. returns false
//!                 otherwise.
//
//*****************************************************************************
static bool syspll_config_util_integer_mode_check(float fSrcClk, float fDstClk, uint8_t* pui8RefDiv, uint16_t* pui16FBDiv)
{
    float fGCD;
    float fMultiplier;
    float fDivider;
    uint32_t ui32Divider;
    uint32_t ui32Multiplier;
    uint32_t normalizeFactor;

    //
    // Find Greatest Common Divisor(GCD) for source and destination clock.
    //
    fGCD = syspll_config_util_gcd(fDstClk, fSrcClk);

    //
    // GCD Not Found, return not integer mode.
    //
    if (fGCD < FLT_EPSILON)
    {
        return false;
    }

    //
    // Calculate multipler and divider needed for integer mode
    //
    fMultiplier = fDstClk / fGCD;
    fDivider = fSrcClk / fGCD;

    //
    // Check both multiplier and divider are integer values and in range.
    // cast it to integer if it is, return not integer mode otherwise.
    //
    if ((fmodf(fMultiplier, 1.0) > FLT_EPSILON) || ( roundf(fMultiplier) > AM_HAL_SYSPLL_MAX_FBDIV_INT_MODE))
    {
        return false;
    }
    ui32Multiplier = (uint32_t)roundf(fMultiplier);

    if ((fmodf(fDivider, 1.0) > FLT_EPSILON) || (roundf(fDivider) > AM_HAL_SYSPLL_MAX_REFDIV))
    {
        return false;
    }
    ui32Divider = (uint32_t)roundf(fDivider);

    //
    // Normalize multiplier and divider to minimum FBDIV value
    //
    if (ui32Multiplier < AM_HAL_SYSPLL_MIN_FBDIV_INT_MODE)
    {
        normalizeFactor = (AM_HAL_SYSPLL_MIN_FBDIV_INT_MODE + ui32Multiplier - 1) / ui32Multiplier;
        ui32Divider *= normalizeFactor;
        ui32Multiplier *= normalizeFactor;
    }

    //
    // Divider Out of range, return not integer mode.
    //
    if ((ui32Divider == 0) || (ui32Divider > AM_HAL_SYSPLL_MAX_REFDIV))
    {
        return false;
    }

    //
    // Multiplier out of range, return not integer mode.
    //
    if ((ui32Multiplier < AM_HAL_SYSPLL_MIN_FBDIV_INT_MODE) || (ui32Multiplier > AM_HAL_SYSPLL_MAX_FBDIV_INT_MODE))
    {
        return false;
    }

    //
    // Set Divider values calculated for Integer mode and return true to indicate that it is integer mode
    //
    *pui8RefDiv = (uint8_t)(ui32Divider & 0x3F);
    *pui16FBDiv = (uint16_t)(ui32Multiplier & 0xFFF);

    //
    // All conditions met. return integer mode.
    //
    return true;

} // syspll_config_util_integer_mode_check()

//*****************************************************************************
//
//! @brief Check whether the output frequency specified can be generated using
//!        System PLL fraction mode, and generate the configuration if it is
//!        feasible.
//!
//! @param fSrcClk        - source clock frequency in MHz
//! @param fDstClk        - targeted System PLL VCO Frequency in MHz
//! @param pui8RefDiv     - pointer to variable for Reference Clock Divide
//!                         output
//! @param pui16FBDivInt  - pointer to variable for Feedback Clock Divide
//!                         (integer part) output.
//! @param pui32FBDivFrac - pointer to variable for Feedback Clock Divide
//!                         (fraction part) output.
//!
//! @return found - returns true if fraction setting for the desired VCO
//!                 is available and written to the pointers. returns false
//!                 otherwise.
//
//*****************************************************************************
static bool syspll_config_util_fraction_mode_check(float fSrcClk, float fDstClk, uint8_t* pui8RefDiv, uint16_t* pui16FBDivInt, uint32_t* pui32FBDivFrac)
{
    float fClkRatio = 0.0;
    float fRefDiv = 0.0;
    float fFBDiv = 0.0;
    uint32_t ui32RefDivTmp = 0;
    uint32_t ui32FBDivIntTmp = 0;
    uint32_t ui32FBDivFracTmp = 0;

    //
    // Calculate VCO clock to reference clock ratio
    //
    fClkRatio = fDstClk / fSrcClk;

    //
    // Calculate RefDiv
    //
    fRefDiv = ceilf((float)AM_HAL_SYSPLL_MIN_FBDIV_FRAC_MODE / fClkRatio);
    if ((fRefDiv < FLT_EPSILON) || (fRefDiv > AM_HAL_SYSPLL_MAX_REFDIV))
    {
        return false;
    }
    ui32RefDivTmp = (uint32_t)fRefDiv;

    //
    // Calculate FBDiv
    //
    fFBDiv = fClkRatio * ui32RefDivTmp;
    ui32FBDivFracTmp = (uint32_t)roundf(fmodf(fFBDiv, 1.0) * (1 << 24));
    fFBDiv = floorf(fFBDiv);
    if ( fFBDiv < AM_HAL_SYSPLL_MIN_FBDIV_FRAC_MODE || fFBDiv > AM_HAL_SYSPLL_MAX_FBDIV_FRAC_MODE )
    {
        return false;
    }
    ui32FBDivIntTmp = (uint32_t)floorf(fFBDiv);

    //
    // All conditions met. copy value to output and return success.
    //
    *pui8RefDiv = (uint8_t)ui32RefDivTmp;
    *pui16FBDivInt = (uint16_t)ui32FBDivIntTmp;
    *pui32FBDivFrac = (uint32_t)ui32FBDivFracTmp;
    return true;

} // syspll_config_util_fraction_mode_check()

//*****************************************************************************
//
//  Generate system PLL configuration to achieve desired VCO Frequency
//
//*****************************************************************************
uint32_t
am_hal_syspll_config_generate(am_hal_syspll_config_t* pConfig, float fRefClkMHz, float fVCOClkMHz)
{
    bool bRet = false;
    bool bIntMode = false;
    uint8_t ui8RefDiv = 0;
    uint16_t ui16FBDivInt = 0;
    uint32_t ui32FBDivFrac = 0;

    //
    // Check pConfig pointer.
    //
    if (pConfig == NULL)
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }

    //
    // Check fVCOClkMHz is in valid range.
    //
    if ((fVCOClkMHz < 60.0f) || (fVCOClkMHz > 960.0f))
    {
        return AM_HAL_STATUS_OUT_OF_RANGE;
    }

    //
    // Check whether the VCO clock rate can be generated in integer mode.
    //
    bRet = syspll_config_util_integer_mode_check(fRefClkMHz, fVCOClkMHz, &ui8RefDiv, &ui16FBDivInt);
    bIntMode = bRet;

    //
    // If the requested VCO clock rate cannot be generated in integer mode,
    // generate the configuration using fraction mode.
    //
    if (!bIntMode)
    {
        bRet = syspll_config_util_fraction_mode_check(fRefClkMHz, fVCOClkMHz, &ui8RefDiv, &ui16FBDivInt, &ui32FBDivFrac);
    }

    //
    // If conifguration found, update pConfig and return success.
    //
    if (bRet)
    {
        pConfig->eVCOSel = (fVCOClkMHz >= AM_HAL_SYSPLL_VCO_HI_MODE_FREQ_MIN) ? AM_HAL_SYSPLL_VCOSEL_VCOHI :
                                                                                AM_HAL_SYSPLL_VCOSEL_VCOLO;

        pConfig->eFractionMode = bIntMode ? AM_HAL_SYSPLL_FMODE_INTEGER :
                                            AM_HAL_SYSPLL_FMODE_FRACTION;
        pConfig->ui8RefDiv = ui8RefDiv;
        pConfig->ui16FBDivInt = ui16FBDivInt;
        pConfig->ui32FBDivFrac = ui32FBDivFrac;

        return AM_HAL_STATUS_SUCCESS;
    }
    //
    // Else, return failure
    //
    else
    {
        return AM_HAL_STATUS_FAIL;
    }
} // am_hal_syspll_config_generate()

//*****************************************************************************
//
//! @brief Generate syspll config by targeting minimum frequency that can be
//!        achieved above ui32MinFVco_Hz specified
//!
//! @param pConfig              - pointer to the system PLL Config structure.
//! @param ui32RefClk_Hz        - system PLL reference clock frequency in Hz
//! @param ui32FoutPostDiv_Hz   - system PLL FOUTPOSTDIV clock frequency
//!                               desired in Hz
//! @param ui32MinFVco_Hz       - FVCO for the generated config must be greater
//!                               than this frequency
//!
//! @return status      - status whether valid configuration is generated
//
//*****************************************************************************
static uint32_t
am_hal_syspll_config_generate_minFVCO(am_hal_syspll_config_t* pConfig, uint32_t ui32RefClk_Hz, uint32_t ui32FoutPostDiv_Hz, uint32_t ui32MinFVco_Hz)
{
    uint32_t ui32Status;
    uint32_t ui32Div;
    uint32_t ui32FVco_Hz;
    uint8_t  ui8PostDiv1;
    uint8_t  ui8PostDiv2;
    bool     bIsFrac;

    //
    // If there is no gcd between source and dest clock, it should be fractional.
    //
    bIsFrac = (syspll_config_util_gcd((float)ui32FoutPostDiv_Hz / 1000000, (float)ui32RefClk_Hz / 1000000) < 1.0);
    if ( bIsFrac )
    {
        uint32_t ui32PFDLimitFVco = ui32RefClk_Hz / (ui32RefClk_Hz / UI32_MHZ_TO_UI32_HZ(10));
        ui32PFDLimitFVco *= 10;
        if ( ui32PFDLimitFVco > ui32MinFVco_Hz )
        {
            ui32MinFVco_Hz = ui32PFDLimitFVco;
        }
    }

    //
    // Calculate Post Divider values
    //
    if (ui32FoutPostDiv_Hz >= ui32MinFVco_Hz)
    {
        ui32Div     = 1;
        ui8PostDiv1 = 1;
        ui8PostDiv2 = 1;
    }
    else
    {
        // Calculate divider from FVCO
        ui32Div = ui32MinFVco_Hz / ui32FoutPostDiv_Hz;
        if ((ui32MinFVco_Hz % ui32FoutPostDiv_Hz) != 0)
        {
            ui32Div += 1;
        }

        // Check whether divider achievable
        if (ui32Div > AM_HAL_SYSPLL_POST_DIV_TOTAL_MAX)
        {
            return AM_HAL_STATUS_OUT_OF_RANGE;
        }

        // Find smallest possible divider from possible divider combination
        ui8PostDiv1 = am_hal_syspll_postdiv_to_divider_table[ui32Div];
        ui8PostDiv2 = (ui8PostDiv1 & 0x0F);
        ui8PostDiv1 = (ui8PostDiv1 >> 4) & 0x0F;
        ui32Div = ui8PostDiv1 * ui8PostDiv2;
    }

    //
    // Calculate Final FVco
    //
    ui32FVco_Hz = ui32FoutPostDiv_Hz * ui32Div;

    //
    // Generate PLL Configuration
    //
    ui32Status = am_hal_syspll_config_generate(pConfig, UI32_HZ_TO_FLT_MHZ(ui32RefClk_Hz), UI32_HZ_TO_FLT_MHZ(ui32FVco_Hz));
    if (ui32Status == AM_HAL_STATUS_SUCCESS)
    {
        // Check for PFD frequency range
        uint32_t ui32PFDMinFreq = (pConfig->eFractionMode == AM_HAL_SYSPLL_FMODE_FRACTION)? UI32_MHZ_TO_UI32_HZ(10) : UI32_MHZ_TO_UI32_HZ(1);
        uint32_t ui32PFDFreq = ui32RefClk_Hz / pConfig->ui8RefDiv;
        if (ui32RefClk_Hz % pConfig->ui8RefDiv != 0)
        {
            ui32PFDFreq += 1;
        }

        if (ui32PFDFreq < ui32PFDMinFreq)
        {
            ui32Status = AM_HAL_STATUS_OUT_OF_RANGE;
        }
        else
        {
            pConfig->ui8PostDiv1 = ui8PostDiv1;
            pConfig->ui8PostDiv2 = ui8PostDiv2;
        }
    }

    return ui32Status;
}

//*****************************************************************************
//
//  Generate system PLL configuration to achieve desired FOUTPOSTDIV
//
//*****************************************************************************
uint32_t
am_hal_syspll_config_generate_with_postdiv(am_hal_syspll_config_t* pConfig, uint32_t ui32RefClk_Hz, uint32_t ui32FoutPostDiv_Hz)
{
    am_hal_syspll_config_t sPLLConfig_LVCO;
    am_hal_syspll_config_t sPLLConfig_HVCO;
    am_hal_syspll_config_t *psSelectedConfig = NULL;
    uint32_t ui32Status;
    bool sPLLConfig_LVCO_Valid = false;
    bool sPLLConfig_HVCO_Valid = false;

    //
    // Generate config for both LOW_SPEED and HIGH_SPEED VCO
    //
    ui32Status = am_hal_syspll_config_generate_minFVCO(&sPLLConfig_LVCO, ui32RefClk_Hz, ui32FoutPostDiv_Hz, UI32_MHZ_TO_UI32_HZ(AM_HAL_SYSPLL_VCO_LO_MODE_FREQ_MIN));
    sPLLConfig_LVCO_Valid = (ui32Status == AM_HAL_STATUS_SUCCESS);
    ui32Status = am_hal_syspll_config_generate_minFVCO(&sPLLConfig_HVCO, ui32RefClk_Hz, ui32FoutPostDiv_Hz, UI32_MHZ_TO_UI32_HZ(AM_HAL_SYSPLL_VCO_HI_MODE_FREQ_MIN));
    sPLLConfig_HVCO_Valid = (ui32Status == AM_HAL_STATUS_SUCCESS);

    //
    // Check result and decide which config to use
    //
    if ( sPLLConfig_LVCO_Valid && sPLLConfig_HVCO_Valid )
    {
        uint32_t LVCO_PTS;
        uint32_t HVCO_PTS;
        uint8_t idx;
        idx  = (sPLLConfig_LVCO.eFractionMode == AM_HAL_SYSPLL_FMODE_FRACTION) ? 1 : 0;
        idx += (sPLLConfig_LVCO.eVCOSel == AM_HAL_SYSPLL_VCOSEL_VCOHI) ? 2 : 0;
        LVCO_PTS  = (ui32RefClk_Hz / 1000000) * AM_HAL_SYSPLL_CFG_PTS_B[idx] / sPLLConfig_LVCO.ui8RefDiv;
        LVCO_PTS += (ui32FoutPostDiv_Hz * sPLLConfig_LVCO.ui8PostDiv1 * sPLLConfig_LVCO.ui8PostDiv2 / 1000000) * AM_HAL_SYSPLL_CFG_PTS_A[idx];

        idx  = (sPLLConfig_HVCO.eFractionMode == AM_HAL_SYSPLL_FMODE_FRACTION) ? 1 : 0;
        idx += (sPLLConfig_HVCO.eVCOSel == AM_HAL_SYSPLL_VCOSEL_VCOHI) ? 2 : 0;
        HVCO_PTS  = (ui32RefClk_Hz / 1000000) * AM_HAL_SYSPLL_CFG_PTS_B[idx] / sPLLConfig_HVCO.ui8RefDiv;
        HVCO_PTS += (ui32FoutPostDiv_Hz * sPLLConfig_HVCO.ui8PostDiv1 * sPLLConfig_HVCO.ui8PostDiv2 / 1000000) * AM_HAL_SYSPLL_CFG_PTS_A[idx];

        if ( HVCO_PTS > LVCO_PTS )
        {
            psSelectedConfig = &sPLLConfig_LVCO;
        }
        else
        {
            psSelectedConfig = &sPLLConfig_HVCO;
        }
    }
    else if ( sPLLConfig_HVCO_Valid )
    {
        psSelectedConfig = &sPLLConfig_HVCO;
    }
    else if ( sPLLConfig_LVCO_Valid )
    {
        psSelectedConfig = &sPLLConfig_LVCO;
    }

    //
    // Copy Config and return result
    //
    if ( psSelectedConfig == NULL )
    {
        return AM_HAL_STATUS_OUT_OF_RANGE;
    }
    else
    {
        pConfig->eVCOSel        =  psSelectedConfig->eVCOSel;
        pConfig->eFractionMode  =  psSelectedConfig->eFractionMode;
        pConfig->ui8RefDiv      =  psSelectedConfig->ui8RefDiv;
        pConfig->ui8PostDiv1    =  psSelectedConfig->ui8PostDiv1;
        pConfig->ui8PostDiv2    =  psSelectedConfig->ui8PostDiv2;
        pConfig->ui16FBDivInt   =  psSelectedConfig->ui16FBDivInt;
        pConfig->ui32FBDivFrac  =  psSelectedConfig->ui32FBDivFrac;
    }

    return AM_HAL_STATUS_SUCCESS;
}

//*****************************************************************************
//
// System PLL initialization function
//
//*****************************************************************************
uint32_t
am_hal_syspll_initialize(uint32_t ui32Module, void **ppHandle)
{
#ifndef AM_HAL_DISABLE_API_VALIDATION
    //
    // Validate module number.
    //
    if (ui32Module >= AM_REG_SYSPLL_NUM_MODULES)
    {
        return AM_HAL_STATUS_OUT_OF_RANGE;
    }

    //
    // Check for valid arguements.
    //
    if (!ppHandle)
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }

    //
    // Make sure module not yet allocated.
    //
    if (g_SysPLLState[ui32Module].prefix.s.bInit)
    {
        return AM_HAL_STATUS_INVALID_OPERATION;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    //
    // Initialize handle.
    //
    g_SysPLLState[ui32Module].prefix.s.bInit = true;
    g_SysPLLState[ui32Module].prefix.s.magic = AM_HAL_MAGIC_SYSPLL;
    g_SysPLLState[ui32Module].ui32Module = ui32Module;

    //
    // Enable sysPLL power
    //
    am_hal_pwrctrl_syspll_enable();

    //
    // Return the handle.
    //
    *ppHandle = (void *)&g_SysPLLState[ui32Module];

    //
    // Return the status.
    //
    return AM_HAL_STATUS_SUCCESS;
} // am_hal_syspll_initialize()

//*****************************************************************************
//
// System PLL deinitialization function
//
//*****************************************************************************
uint32_t
am_hal_syspll_deinitialize(void *pHandle)
{
#ifndef AM_HAL_DISABLE_API_VALIDATION
    //
    // Check the handle.
    //
    if (!AM_HAL_SYSPLL_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    uint32_t               status = AM_HAL_STATUS_SUCCESS;
    am_hal_syspll_state_t  *pSysPLLState = (am_hal_syspll_state_t *)pHandle;
    bool                    bPowerEnabled = false;

    // Disable PLL if it is still enabled
    if (pSysPLLState->prefix.s.bEnable)
    {
        status = am_hal_syspll_disable(pHandle);
    }

    //
    // Turn off power gates for system PLL if it is not yet powered off
    //
    am_hal_pwrctrl_syspll_enabled(&bPowerEnabled);
    if (bPowerEnabled)
    {
        am_hal_pwrctrl_syspll_disable();
    }

    //
    // Clear inititalized flag
    //
    pSysPLLState->prefix.s.bInit = false;

    //
    // Return the status.
    //
    return status;

} // am_hal_syspll_deinitialize()

//*****************************************************************************
//
// System PLL enable function
//
//*****************************************************************************
uint32_t
am_hal_syspll_enable(void *pHandle)
{
#ifndef AM_HAL_DISABLE_API_VALIDATION
    //
    // Check the handle.
    //
    if (!AM_HAL_SYSPLL_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    am_hal_syspll_state_t  *pSysPLLState = (am_hal_syspll_state_t *)pHandle;
    uint32_t                ui32Module   = pSysPLLState->ui32Module;

    //
    // System PLL is already enabled, return success.
    //
    if (pSysPLLState->prefix.s.bEnable)
    {
        return AM_HAL_STATUS_SUCCESS;
    }

    //
    // Check and make sure SIMOBUCK is active.It is expected that SIMOBUCK
    // init is triggered before syspll is enabled, hence SIMOBUCK should always
    // be active other than in deep sleep state.
    //
    if ((MCUCTRL->VRCTRL_b.SIMOBUCKACTIVE != 1) ||
        (MCUCTRL->VRCTRL_b.SIMOBUCKRSTB != 1) ||
        (MCUCTRL->VRCTRL_b.SIMOBUCKPDNB != 1) ||
        (MCUCTRL->VRCTRL_b.SIMOBUCKOVER != 1))
    {
        return AM_HAL_STATUS_INVALID_OPERATION;
    }

    //
    // Enable the SystemPLL.
    //
    SYSPLLn(ui32Module)->PLLCTL0_b.SYSPLLPDB = MCUCTRL_PLLCTL0_SYSPLLPDB_ENABLE;

    //
    // Set flag to indicate module is enabled.
    //
    pSysPLLState->prefix.s.bEnable = true;

    //
    // Return the status.
    //
    return AM_HAL_STATUS_SUCCESS;

} // am_hal_syspll_enable()

//*****************************************************************************
//
// System PLL disable function
//
//*****************************************************************************
uint32_t
am_hal_syspll_disable(void *pHandle)
{
#ifndef AM_HAL_DISABLE_API_VALIDATION
    //
    // Check the handle.
    //
    if (!AM_HAL_SYSPLL_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    am_hal_syspll_state_t  *pSysPLLState = (am_hal_syspll_state_t *)pHandle;
    uint32_t                ui32Module   = pSysPLLState->ui32Module;

    //
    // Disable the system PLL.
    //
    SYSPLLn(ui32Module)->PLLCTL0_b.SYSPLLPDB = MCUCTRL_PLLCTL0_SYSPLLPDB_DISABLE;

    //
    // Set flag to indicate module is disabled.
    //
    pSysPLLState->prefix.s.bEnable = false;

    //
    // Return the status.
    //
    return AM_HAL_STATUS_SUCCESS;

} // am_hal_syspll_disable()

//*****************************************************************************
//
// System PLL configuration function
//
//*****************************************************************************
uint32_t
am_hal_syspll_configure(void *pHandle, am_hal_syspll_config_t *psConfig)
{
#ifndef AM_HAL_DISABLE_API_VALIDATION
    //
    // Check the handle.
    //
    if (!AM_HAL_SYSPLL_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    am_hal_syspll_state_t  *pSysPLLState = (am_hal_syspll_state_t *)pHandle;
    uint32_t                ui32Module   = pSysPLLState->ui32Module;

    //
    // Configuration can only be changed when system PLL not enabled
    //
    if (pSysPLLState->prefix.s.bEnable)
    {
        return AM_HAL_STATUS_INVALID_OPERATION;
    }

    //
    // Make sure PLL reference clock divider config is in range
    //
    if (psConfig->ui8RefDiv > AM_HAL_SYSPLL_MAX_REFDIV)
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }

    //
    // Make sure PLL Feedback clock divider config is in range
    //
    if (psConfig->eFractionMode == AM_HAL_SYSPLL_FMODE_INTEGER)
    {
        if ((psConfig->ui16FBDivInt < AM_HAL_SYSPLL_MIN_FBDIV_INT_MODE) ||
            (psConfig->ui16FBDivInt > AM_HAL_SYSPLL_MAX_FBDIV_INT_MODE))
        {
            return AM_HAL_STATUS_INVALID_ARG;
        }
    }
    else
    {
        if ((psConfig->ui16FBDivInt < AM_HAL_SYSPLL_MIN_FBDIV_FRAC_MODE) ||
            (psConfig->ui16FBDivInt > AM_HAL_SYSPLL_MAX_FBDIV_FRAC_MODE))
        {
            return AM_HAL_STATUS_INVALID_ARG;
        }
    }

    //
    // Make sure Post Divide is in range and Post Divide 2 not greater than
    // Post Divide 1.
    //
    if ((psConfig->ui8PostDiv1 > AM_HAL_SYSPLL_POST_DIV_MAX) ||
        (psConfig->ui8PostDiv2 > AM_HAL_SYSPLL_POST_DIV_MAX) ||
        (psConfig->ui8PostDiv2 > psConfig->ui8PostDiv1))
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }

    //
    // Write configuration into register
    //
    SYSPLLn(ui32Module)->PLLCTL0_b.VCOSELECT = psConfig->eVCOSel;
    SYSPLLn(ui32Module)->PLLCTL0_b.FREFSEL   = psConfig->eFref;
    SYSPLLn(ui32Module)->PLLCTL0_b.DSMPD     = psConfig->eFractionMode;
    SYSPLLn(ui32Module)->PLLDIV0_b.FRAC      = psConfig->ui32FBDivFrac;
    SYSPLLn(ui32Module)->PLLDIV1_b.FBDIV     = psConfig->ui16FBDivInt;
    SYSPLLn(ui32Module)->PLLDIV1_b.REFDIV    = psConfig->ui8RefDiv;
    SYSPLLn(ui32Module)->PLLDIV1_b.POSTDIV1  = psConfig->ui8PostDiv1;
    SYSPLLn(ui32Module)->PLLDIV1_b.POSTDIV2  = psConfig->ui8PostDiv2;

    //
    // Save PLL FREF selection
    //
    am_hal_sysctrl_clkmuxrst_pll_fref_update((MCUCTRL_PLLCTL0_FREFSEL_Enum)psConfig->eFref);

    //
    // Make sure noise cancelling ADC is powered ON
    //
    SYSPLLn(ui32Module)->PLLCTL0_b.DACPD = MCUCTRL_PLLCTL0_DACPD_ACTIVE;

    //
    // Power Down FOUT_VCO out of system PLL since we will not be needing it
    //
    SYSPLLn(ui32Module)->PLLCTL0_b.FOUTVCOPD     = MCUCTRL_PLLCTL0_FOUTVCOPD_POWERDOWN;
    SYSPLLn(ui32Module)->PLLCTL0_b.FOUTPOSTDIVPD = MCUCTRL_PLLCTL0_FOUTPOSTDIVPD_ACTIVE;
    SYSPLLn(ui32Module)->PLLCTL0_b.FOUT4PHASEPD  = MCUCTRL_PLLCTL0_FOUT4PHASEPD_ACTIVE;

    //
    // Return status.
    //
    return AM_HAL_STATUS_SUCCESS;

} // am_hal_syspll_configure()

//*****************************************************************************
//
// System PLL Get PLL Lock function
//
//*****************************************************************************
uint32_t
am_hal_syspll_lock_read(void *pHandle, bool *pll_ready)
{
#ifndef AM_HAL_DISABLE_API_VALIDATION
    //
    // Check the handle.
    //
    if (!AM_HAL_SYSPLL_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    am_hal_syspll_state_t  *pSysPLLState = (am_hal_syspll_state_t *)pHandle;
    uint32_t                ui32Module   = pSysPLLState->ui32Module;

    //
    // Read system PLL lock status into bool pointed by pll_ready
    //
    *pll_ready = (SYSPLLn(ui32Module)->PLLSTAT_b.LOCK == 1);

    //
    // Return status.
    //
    return AM_HAL_STATUS_SUCCESS;

} // am_hal_syspll_lock_read()

//*****************************************************************************
//
// System PLL Lock Wait according to VCO input clock and operation mode
//
//*****************************************************************************
uint32_t
am_hal_syspll_lock_wait(void *pHandle)
{
#ifndef AM_HAL_DISABLE_API_VALIDATION
    //
    // Check the handle.
    //
    if (!AM_HAL_SYSPLL_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    am_hal_syspll_state_t  *pSysPLLState = (am_hal_syspll_state_t *)pHandle;
    uint32_t ui32Module = pSysPLLState->ui32Module;
    am_hal_syspll_vcosel_e eVCOSel = (am_hal_syspll_vcosel_e)SYSPLLn(ui32Module)->PLLCTL0_b.VCOSELECT;
    uint8_t ui8RefDiv   = SYSPLLn(ui32Module)->PLLDIV1_b.REFDIV;

    //
    // Check System PLL enabled
    //
    if (SYSPLLn(ui32Module)->PLLCTL0_b.SYSPLLPDB != MCUCTRL_PLLCTL0_SYSPLLPDB_ENABLE)
    {
        return AM_HAL_STATUS_INVALID_OPERATION;
    }

    //
    // Calculate Maximum time to wait for PLL Lock
    //
    uint32_t ui32LockTimeoutUs = ( eVCOSel == AM_HAL_SYSPLL_VCOSEL_VCOHI) ? AM_HAL_SYSPLL_MAX_LOCK_CYCLE_VCOSEL1 :
                                                                            AM_HAL_SYSPLL_MAX_LOCK_CYCLE_VCOSEL0;
    ui32LockTimeoutUs = ui32LockTimeoutUs * ui8RefDiv;
    ui32LockTimeoutUs = (ui32LockTimeoutUs + (AM_HAL_SYSPLL_CLOCK_SRC_MIN_MHZ - 1)) / AM_HAL_SYSPLL_CLOCK_SRC_MIN_MHZ;

    //
    // PLL lock wait with timeout
    //
    return am_hal_delay_us_status_check(ui32LockTimeoutUs,
                                        (uint32_t)&SYSPLLn(ui32Module)->PLLSTAT,
                                        MCUCTRL_PLLSTAT_LOCK_Msk,
                                        MCUCTRL_PLLSTAT_LOCK_Msk,
                                        true);
} // am_hal_syspll_lock_wait()

//*****************************************************************************
//
// System PLL refClk bypass function
//
//*****************************************************************************
uint32_t
am_hal_syspll_bypass_set(void *pHandle, bool bBypass)
{
#ifndef AM_HAL_DISABLE_API_VALIDATION
    //
    // Check the handle.
    //
    if (!AM_HAL_SYSPLL_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    am_hal_syspll_state_t  *pSysPLLState = (am_hal_syspll_state_t *)pHandle;
    uint32_t                ui32Module = pSysPLLState->ui32Module;

    //
    // Set Bypass Setting into system PLL register
    //
    SYSPLLn(ui32Module)->PLLCTL0_b.BYPASS = bBypass? 1 : 0;

    //
    // Return status.
    //
    return AM_HAL_STATUS_SUCCESS;

} // am_hal_syspll_bypass_set()

//*****************************************************************************
//
// System PLL Mux select
// Note: Do not call this function directly. Use respective module's HAL to
//       select the clock. Calling this directly might cause clock malfunction.
//
//*****************************************************************************
uint32_t
am_hal_syspll_mux_select(am_hal_syspll_mux_select_e eMuxSel, uint32_t ui32MuxSwitchDelay)
{
    uint8_t eLLMuxCtlVal;
    uint8_t ui8OldSrcClkMuxRstBm;
    uint8_t ui8NewSrcClkMuxRstBm;
    am_hal_syspll_mux_e eLLMux;
    am_hal_syspll_mux_select_e eOldMuxSel = AM_HAL_SYSPLL_LLMUX_PDM_SRC_CLKGEN;
    am_hal_sysctrl_clkmuxrst_clk_e eClkMuxRstClk;

    //
    // Convert mux_select into Mux and register value to set
    //
    eLLMux = am_hal_syspll_muxsel_to_mux(eMuxSel);
    eLLMuxCtlVal = am_hal_syspll_muxsel_to_muxctl(eMuxSel);

    //
    // Recall current Mux Setting and compute variables needed by ClkMuxReset
    //
    am_hal_syspll_mux_get(eLLMux, &eOldMuxSel);
    ui8OldSrcClkMuxRstBm = am_hal_syspll_muxsel_to_clkmuxrstclk(eOldMuxSel);
    ui8NewSrcClkMuxRstBm = am_hal_syspll_muxsel_to_clkmuxrstclk(eMuxSel);
    eClkMuxRstClk = am_hal_syspll_spllmux_to_clkmuxrstmux(eLLMux);

    //
    // Update both old and new clock source to clock mux reset
    //
    am_hal_sysctrl_clkmuxrst_clkneeded_update(eClkMuxRstClk, ui8NewSrcClkMuxRstBm | ui8OldSrcClkMuxRstBm);

    //
    // Set Mux Select Setting into each of the Mux Select
    //
    switch(eLLMux)
    {
        case AM_HAL_SYSPLL_LLMUX_PDM:
            SYSPLLn(AM_HAL_SYSPLL_MODULE_NUM)->PLLMUXCTL_b.PDMPLLCLKSEL = eLLMuxCtlVal;
            break;
        case AM_HAL_SYSPLL_LLMUX_AUDADC:
            SYSPLLn(AM_HAL_SYSPLL_MODULE_NUM)->PLLMUXCTL_b.AUDADCPLLCLKSEL = eLLMuxCtlVal;
            break;
        case AM_HAL_SYSPLL_LLMUX_USB:
            SYSPLLn(AM_HAL_SYSPLL_MODULE_NUM)->PLLMUXCTL_b.USBPLLCLKSEL = eLLMuxCtlVal;
            break;
        case AM_HAL_SYSPLL_LLMUX_I2S0:
            SYSPLLn(AM_HAL_SYSPLL_MODULE_NUM)->PLLMUXCTL_b.I2S0PLLCLKSEL = eLLMuxCtlVal;
            break;
        case AM_HAL_SYSPLL_LLMUX_I2S1:
            SYSPLLn(AM_HAL_SYSPLL_MODULE_NUM)->PLLMUXCTL_b.I2S1PLLCLKSEL = eLLMuxCtlVal;
            break;
        case AM_HAL_SYSPLL_LLMUX_MAX:
            // Do nothing. This case will never be entered.
            break;
    }

    //
    // Wait for MUX switch complete
    //
    am_hal_sysctrl_sysbus_write_flush();
    am_hal_delay_us(ui32MuxSwitchDelay);

    //
    // Update new clock source to clock mux reset
    //
    am_hal_sysctrl_clkmuxrst_clkneeded_update(eClkMuxRstClk, ui8NewSrcClkMuxRstBm);

    //
    // Return status.
    //
    return AM_HAL_STATUS_SUCCESS;

} // am_hal_syspll_mux_select()

//*****************************************************************************
//
// System PLL Mux Get
//
//*****************************************************************************
uint32_t
am_hal_syspll_mux_get(am_hal_syspll_mux_e eMux, am_hal_syspll_mux_select_e *pEMuxSel)
{
    switch(eMux)
    {
        case AM_HAL_SYSPLL_LLMUX_PDM:
            switch ((MCUCTRL_PLLMUXCTL_PDMPLLCLKSEL_Enum)SYSPLLn(AM_HAL_SYSPLL_MODULE_NUM)->PLLMUXCTL_b.PDMPLLCLKSEL)
            {
                case MCUCTRL_PLLMUXCTL_PDMPLLCLKSEL_PLL:
                    *pEMuxSel = AM_HAL_SYSPLL_LLMUX_PDM_SRC_PLL;
                    break;
                case MCUCTRL_PLLMUXCTL_PDMPLLCLKSEL_HFRC:
                    *pEMuxSel = AM_HAL_SYSPLL_LLMUX_PDM_SRC_HFRC;
                    break;
                case MCUCTRL_PLLMUXCTL_PDMPLLCLKSEL_CLKGEN:
                    *pEMuxSel = AM_HAL_SYSPLL_LLMUX_PDM_SRC_CLKGEN;
                    break;
            }
            break;
        case AM_HAL_SYSPLL_LLMUX_AUDADC:
            switch ((MCUCTRL_PLLMUXCTL_AUDADCPLLCLKSEL_Enum)SYSPLLn(AM_HAL_SYSPLL_MODULE_NUM)->PLLMUXCTL_b.AUDADCPLLCLKSEL)
            {
                case MCUCTRL_PLLMUXCTL_AUDADCPLLCLKSEL_PLL:
                    *pEMuxSel = AM_HAL_SYSPLL_LLMUX_AUDADC_SRC_PLL;
                    break;
                case MCUCTRL_PLLMUXCTL_AUDADCPLLCLKSEL_HFRC:
                    *pEMuxSel = AM_HAL_SYSPLL_LLMUX_AUDADC_SRC_HFRC;
                    break;
                case MCUCTRL_PLLMUXCTL_AUDADCPLLCLKSEL_CLKGEN:
                    *pEMuxSel = AM_HAL_SYSPLL_LLMUX_AUDADC_SRC_CLKGEN;
                    break;
            }
            break;
        case AM_HAL_SYSPLL_LLMUX_USB:
            switch ((MCUCTRL_PLLMUXCTL_USBPLLCLKSEL_Enum)SYSPLLn(AM_HAL_SYSPLL_MODULE_NUM)->PLLMUXCTL_b.USBPLLCLKSEL)
            {
                case MCUCTRL_PLLMUXCTL_USBPLLCLKSEL_PLL:
                    *pEMuxSel = AM_HAL_SYSPLL_LLMUX_USB_SRC_PLL;
                    break;
                case MCUCTRL_PLLMUXCTL_USBPLLCLKSEL_CLKGEN:
                    *pEMuxSel = AM_HAL_SYSPLL_LLMUX_USB_SRC_CLKGEN;
                    break;
            }
            break;
        case AM_HAL_SYSPLL_LLMUX_I2S0:
            switch ((MCUCTRL_PLLMUXCTL_I2S0PLLCLKSEL_Enum)SYSPLLn(AM_HAL_SYSPLL_MODULE_NUM)->PLLMUXCTL_b.I2S0PLLCLKSEL)
            {
                case MCUCTRL_PLLMUXCTL_I2S0PLLCLKSEL_PLLFOUT4:
                    *pEMuxSel = AM_HAL_SYSPLL_LLMUX_I2S0_SRC_PLL_FOUT4;
                    break;
                case MCUCTRL_PLLMUXCTL_I2S0PLLCLKSEL_PLLFOUT3:
                    *pEMuxSel = AM_HAL_SYSPLL_LLMUX_I2S0_SRC_PLL_FOUT3;
                    break;
                case MCUCTRL_PLLMUXCTL_I2S0PLLCLKSEL_CLKGEN:
                    *pEMuxSel = AM_HAL_SYSPLL_LLMUX_I2S0_SRC_CLKGEN;
                    break;
            }
            break;
        case AM_HAL_SYSPLL_LLMUX_I2S1:
            switch ((MCUCTRL_PLLMUXCTL_I2S1PLLCLKSEL_Enum)SYSPLLn(AM_HAL_SYSPLL_MODULE_NUM)->PLLMUXCTL_b.I2S1PLLCLKSEL)
            {
                case MCUCTRL_PLLMUXCTL_I2S1PLLCLKSEL_PLLFOUT4:
                    *pEMuxSel = AM_HAL_SYSPLL_LLMUX_I2S1_SRC_PLL_FOUT4;
                    break;
                case MCUCTRL_PLLMUXCTL_I2S1PLLCLKSEL_PLLFOUT3:
                    *pEMuxSel = AM_HAL_SYSPLL_LLMUX_I2S1_SRC_PLL_FOUT3;
                    break;
                case MCUCTRL_PLLMUXCTL_I2S1PLLCLKSEL_CLKGEN:
                    *pEMuxSel = AM_HAL_SYSPLL_LLMUX_I2S1_SRC_CLKGEN;
                    break;
            }
            break;

        case AM_HAL_SYSPLL_LLMUX_MAX:
            return AM_HAL_STATUS_INVALID_ARG;
    }

    //
    // Return status.
    //
    return AM_HAL_STATUS_SUCCESS;

} // am_hal_syspll_mux_get()

//*****************************************************************************
//
// End Doxygen group.
//! @}
//
//*****************************************************************************
