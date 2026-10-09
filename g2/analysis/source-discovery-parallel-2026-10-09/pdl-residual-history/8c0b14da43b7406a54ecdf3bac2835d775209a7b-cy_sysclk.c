/***************************************************************************//**
* \file cy_sysclk.c
* \version 1.10
*
* Provides an API implementation of the sysclk driver.
*
********************************************************************************
* \copyright
* Copyright 2016-2020 Cypress Semiconductor Corporation
* SPDX-License-Identifier: Apache-2.0
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*******************************************************************************/


#include "cy_sysclk.h"
#include "cy_syslib.h"
#include <stdlib.h>


/* ========================================================================== */
/* =========================    EXTCLK SECTION    =========================== */
/* ========================================================================== */

/** \cond INTERNAL */
static uint32_t extClkFreq = 0UL; /* Internal storage for external clock frequency user setting */

#define CY_SYSCLK_EXTCLK_MIN_FREQ (1000000UL)  /* 1 MHz */
#define CY_SYSCLK_EXTCLK_MAX_FREQ (48000000UL) /* 48 MHz */
/** \endcond */

/**
* \addtogroup group_sysclk_ext_clk_funcs
* \{
*/
/*******************************************************************************
* Function Name: Cy_SysClk_ExtClkSetFrequency
****************************************************************************//**
*
* Sets the signal frequency of the External Clock Source (EXTCLK) into the
* internal storage to be used in \ref Cy_SysClk_ClkHfGetFrequency.
*
* \param freq The frequency of the External Clock Source.
* Valid range is 1000000...48000000 (1...48 MHz).
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_ExtClkSetFrequency
*
*******************************************************************************/
void Cy_SysClk_ExtClkSetFrequency(uint32_t freq)
{
    if ((CY_SYSCLK_EXTCLK_MIN_FREQ <= freq) && (freq <= CY_SYSCLK_EXTCLK_MAX_FREQ))
    {
        extClkFreq = freq;
    }
}


/*******************************************************************************
* Function Name: Cy_SysClk_ExtClkGetFrequency
****************************************************************************//**
*
* Returns the frequency of the External Clock Source (EXTCLK) from the
* internal storage.
*
* \return The frequency of the External Clock Source.
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_ExtClkSetFrequency
*
*******************************************************************************/
uint32_t Cy_SysClk_ExtClkGetFrequency(void)
{
    return (extClkFreq);
}
/** \} group_sysclk_ext_clk_funcs */


/* ========================================================================== */
/* =========================    EXTREF SECTION    =========================== */
/* ========================================================================== */
#if (defined(CY_IP_M0S8EXCO) && (CY_IP_M0S8EXCO == 1u))
#if (CY_IP_M0S8EXCO_VERSION == 2U) || defined(CY_DOXYGEN)
/** \cond INTERNAL */
static uint32_t extRefFreq = 0UL; /* Internal storage for external PLL reference frequency user setting */

#define CY_SYSCLK_EXTREF_MIN_FREQ (1000000UL)  /* 1 MHz */
#define CY_SYSCLK_EXTREF_MAX_FREQ (64000000UL) /* 64 MHz */
/** \endcond */
/**
* \addtogroup group_sysclk_ext_ref_funcs
* \{
*/
/*******************************************************************************
* Function Name: Cy_SysClk_ExtRefSetFrequency
****************************************************************************//**
*
* Sets the signal frequency of the External PLL Reference Clock Source (EXTREF)
* into the internal storage to be used in \ref Cy_SysClk_PllGetFrequency.
*
* \param freq The frequency of the External PLL Reference Source.
* Valid range is 1000000...64000000 (1...64 MHz).
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_ExtRefSetFrequency
*
*******************************************************************************/
void Cy_SysClk_ExtRefSetFrequency(uint32_t freq)
{
    if ((CY_SYSCLK_EXTREF_MIN_FREQ <= freq) && (freq <= CY_SYSCLK_EXTREF_MAX_FREQ))
    {
        extRefFreq = freq;
    }
}


/*******************************************************************************
* Function Name: Cy_SysClk_ExtRefGetFrequency
****************************************************************************//**
*
* Returns the frequency of the External PLL Reference Source (EXT_REF) from the
* internal storage.
*
* \return The frequency of the External PLL Reference Source.
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_ExtRefSetFrequency
*
*******************************************************************************/
uint32_t Cy_SysClk_ExtRefGetFrequency(void)
{
    return (extRefFreq);
}
/** \} group_sysclk_ext_ref_funcs */
#endif /* CY_IP_M0S8EXCO_VERSION == 2U */
#endif /* CY_IP_M0S8EXCO */

/* ========================================================================== */
/* ===========================    IMO SECTION    ============================ */
/* ========================================================================== */



#define CY_SYSCLK_IS_FREQ_VALID(freq)  ((CY_SYSCLK_IMO_24MHZ == (freq)) || \
                                        (CY_SYSCLK_IMO_28MHZ == (freq)) || \
                                        (CY_SYSCLK_IMO_32MHZ == (freq)) || \
                                        (CY_SYSCLK_IMO_36MHZ == (freq)) || \
                                        (CY_SYSCLK_IMO_40MHZ == (freq)) || \
                                        (CY_SYSCLK_IMO_44MHZ == (freq)) || \
                                        (CY_SYSCLK_IMO_48MHZ == (freq)))

#define CY_SYSCLK_FREQ_SCALER           (1000000UL)


/*******************************************************************************
* Function Name: Cy_SysClk_ImoSetFrequency
****************************************************************************//**
*
* Sets the IMO desired frequency.
*
* \note There is a \ref Cy_SysClk_ImoLock feature to improve an IMO precision.
*
* \param freq - the desired IMO frequency, \ref cy_en_sysclk_imo_freq_t.
*
* \note Call \ref SystemCoreClockUpdate after this function calling
* if it affects the ClkSys frequency.
*
* \note Call \ref Cy_SysLib_SetWaitStates before calling this function if
* ClkSys frequency is increasing.
*
* \note Call \ref Cy_SysLib_SetWaitStates after calling this function if
* ClkSys frequency is decreasing.
*
* \return Error / status code \ref cy_en_sysclk_status_t : \n
* CY_SYSCLK_SUCCESS - the frequency is set as requested \n
* CY_SYSCLK_BAD_PARAM - Invalid parameter.
* CY_SYSCLK_INVALID_STATE - IMO is not enabled.
*
*******************************************************************************/
cy_en_sysclk_status_t Cy_SysClk_ImoSetFrequency(cy_en_sysclk_imo_freq_t freq)
{
    cy_en_sysclk_status_t retVal = CY_SYSCLK_BAD_PARAM;

    if (Cy_SysClk_ImoIsEnabled())
    {
        if (CY_SYSCLK_IS_FREQ_VALID(freq))
        {
            if ((uint32_t) freq != Cy_SysClk_ImoGetFrequency())
            {
                /* Convert the frequency value in Hz into the SFLASH.IMO_TRIM register index */
                uint32_t locFreq = ((uint32_t)freq - (uint32_t)CY_SYSCLK_IMO_24MHZ) / CY_SYSCLK_FREQ_SCALER;
                uint32_t intStat = Cy_SysLib_EnterCriticalSection();
            #if defined(CY_IP_M0S8WCO)
                /* Unlock if locked */
                cy_en_sysclk_imo_lock_t lock = Cy_SysClk_ImoGetLockStatus();

                if (CY_SYSCLK_IMO_LOCK_NONE != lock)
                {
                    (void) Cy_SysClk_ImoLock(CY_SYSCLK_IMO_LOCK_NONE);
                }
            #endif /* (CY_IP_M0S8WCO) */

                /* Set IMO to 24 MHz */
                SRSSLT_CLK_IMO_SELECT = 0UL;

                /* Apply coarse trim */
                SRSSLT_CLK_IMO_TRIM1 = SFLASH_IMO_TRIM_LT(locFreq);

                /* Zero out fine trim */
                SRSSLT_CLK_IMO_TRIM2 = 0UL;

                /* Apply TC trim */
                SRSSLT_CLK_IMO_TRIM3 = SFLASH_IMO_TCTRIM_LT(locFreq);

                /* Convert the SFLASH.IMO_TRIM register index into the frequency bitfield value */
                locFreq >>= 2UL;

                Cy_SysLib_DelayCycles(50UL);

                if (0UL != locFreq)
                {
                    /* Select nearby intermediate frequency */
                    CY_REG32_CLR_SET(SRSSLT_CLK_IMO_SELECT, SRSSLT_CLK_IMO_SELECT_FREQ, locFreq - 1UL);

                    Cy_SysLib_DelayCycles(50UL);

                    /* Make small step to final frequency */
                    CY_REG32_CLR_SET(SRSSLT_CLK_IMO_SELECT, SRSSLT_CLK_IMO_SELECT_FREQ, locFreq);
                }

            #if defined(CY_IP_M0S8WCO)
                /* Restore locking */
                if (CY_SYSCLK_IMO_LOCK_NONE != lock)
                {
                    (void) Cy_SysClk_ImoLock(lock);
                }
            #endif /* (CY_IP_M0S8WCO) */

                Cy_SysLib_ExitCriticalSection(intStat);
            }

            retVal = CY_SYSCLK_SUCCESS;
        }
    }
    else
    {
        retVal = CY_SYSCLK_INVALID_STATE;
    }

    return(retVal);
}


/*******************************************************************************
* Function Name: Cy_SysClk_ImoGetFrequency
****************************************************************************//**
*
* Returns the IMO nominal frequency.
*
* \return the frequency value in Hz.
*
*******************************************************************************/
uint32_t Cy_SysClk_ImoGetFrequency(void)
{
    return (Cy_SysClk_ImoIsEnabled() ?
            (((_FLD2VAL(SRSSLT_CLK_IMO_SELECT_FREQ, SRSSLT_CLK_IMO_SELECT) << 2UL) *
              CY_SYSCLK_FREQ_SCALER) + (uint32_t)CY_SYSCLK_IMO_24MHZ) : 0UL);
}


#if defined(CY_IP_M0S8WCO)
/*******************************************************************************
* Function Name: Cy_SysClk_ImoGetLockStatus
****************************************************************************//**
*
* Returns IMO lock status.
*
* \return IMO lock state \ref cy_en_sysclk_imo_lock_t.
*
*******************************************************************************/
cy_en_sysclk_imo_lock_t Cy_SysClk_ImoGetLockStatus(void)
{
    cy_en_sysclk_imo_lock_t retVal = CY_SYSCLK_IMO_LOCK_NONE;

    if (_FLD2BOOL(WCO_CONFIG_DPLL_ENABLE, WCO_CONFIG))
    {
        retVal = CY_SYSCLK_IMO_LOCK_WCO;
    }

    return (retVal);
}


/*******************************************************************************
* Function Name: Cy_SysClk_ImoLock
****************************************************************************//**
*
* Locks/unlocks IMO.
*
* \param lock - the desired IMO lock state, \ref cy_en_sysclk_imo_lock_t
*
* \return Error / status code \ref cy_en_sysclk_status_t : \n
* CY_SYSCLK_SUCCESS - the lock state is set as requested \n
* CY_SYSCLK_BAD_PARAM - Invalid parameter \n
* CY_SYSCLK_INVALID_STATE - Invalid state (IMO or WCO is not enabled, etc.)
*
*******************************************************************************/
cy_en_sysclk_status_t Cy_SysClk_ImoLock(cy_en_sysclk_imo_lock_t lock)
{
    cy_en_sysclk_status_t retVal = CY_SYSCLK_BAD_PARAM;

    if ((CY_SYSCLK_IMO_LOCK_NONE == lock) ||
        (CY_SYSCLK_IMO_LOCK_WCO  == lock))
    {
        if (!Cy_SysClk_ImoIsEnabled())
        {
            retVal = CY_SYSCLK_INVALID_STATE;
        }
        else if (lock == Cy_SysClk_ImoGetLockStatus())
        {
            /* Do nothing, the lock is already as requested */
            retVal = CY_SYSCLK_SUCCESS;
        }
        else if ((CY_SYSCLK_IMO_LOCK_NONE == lock))
        {
            WCO_CONFIG &= ~WCO_CONFIG_DPLL_ENABLE_Msk;

            /* Convert the IMO_SELECT_FREQ value into the SFLASH.IMO_TRIM register index */
            SRSSLT_CLK_IMO_TRIM1 = SFLASH_IMO_TRIM_LT((_FLD2VAL(SRSSLT_CLK_IMO_SELECT_FREQ, SRSSLT_CLK_IMO_SELECT) << 2UL));

            retVal = CY_SYSCLK_SUCCESS;
        }
        else if ((CY_SYSCLK_IMO_LOCK_WCO == lock))
        {
            if(!Cy_SysClk_WcoIsEnabled())
            {
                retVal = CY_SYSCLK_INVALID_STATE;
            }
            else
            {
                uint32_t regTmp = 0uL;
                uint32_t lfLimit = 0uL;
                uint32_t flashCtlReg = 0uL;

                /* Set oscillator interface control port to WCO */
                SRSSLT_CLK_IMO_TRIM1 = 0UL;

                /* For the WCO locking mode, the IMO gain needs to be CY_SYS_CLK_IMO_TRIM4_GAIN */
                regTmp = (_CLR_SET_FLD32U(WCO_DPLL, WCO_DPLL_DPLL_MULT,     0) |
                          _CLR_SET_FLD32U(WCO_DPLL, WCO_DPLL_DPLL_LF_IGAIN, 0) |
                          _CLR_SET_FLD32U(WCO_DPLL, WCO_DPLL_DPLL_LF_PGAIN, 0) |
                          _CLR_SET_FLD32U(WCO_DPLL, WCO_DPLL_DPLL_LF_LIMIT, 0));

                /* Set multiplier to determine IMO frequency in multiples of the WCO frequency */
                regTmp |= CY_SYSLIB_DIV_ROUND(Cy_SysClk_ImoGetFrequency(), CY_SYSCLK_WCO_FREQ) & WCO_DPLL_DPLL_MULT_Msk;

                /* Set DPLL Loop Filter Integral and Proportional Gains Setting */
                regTmp |= (_FLD2VAL(WCO_DPLL_DPLL_LF_IGAIN, WCO_DPLL) | _FLD2VAL(WCO_DPLL_DPLL_LF_PGAIN, WCO_DPLL));

                WCO_DPLL = regTmp;

                flashCtlReg = CPUSS_FLASH_CTL;
                Cy_SysLib_SetWaitStates(48);

                WCO_CONFIG |= _VAL2FLD(WCO_CONFIG_IP_ENABLE, 0x1u);

                regTmp  = (WCO_DPLL & ~WCO_DPLL_DPLL_LF_LIMIT_Msk);

                while (lfLimit < (CY_SYSCLK_WCO_CONFIG_DPLL_LF_LIMIT_MAX - CY_SYSCLK_WCO_CONFIG_DPLL_LF_LIMIT_STEP))
                {
                    Cy_SysLib_Delay(CY_SYSCLK_WCO_DPLL_TIMEOUT_MS);
                    lfLimit += CY_SYSCLK_WCO_CONFIG_DPLL_LF_LIMIT_STEP;
                    WCO_DPLL = (regTmp | (lfLimit << WCO_DPLL_DPLL_LF_LIMIT_Pos));
                }

                Cy_SysLib_Delay(CY_SYSCLK_WCO_DPLL_TIMEOUT_MS);
                WCO_DPLL = (regTmp | (CY_SYSCLK_WCO_CONFIG_DPLL_LF_LIMIT_MAX << WCO_DPLL_DPLL_LF_LIMIT_Pos));

                CPUSS_FLASH_CTL = flashCtlReg;

                retVal = CY_SYSCLK_SUCCESS;
            }
        }
        else
        {
            /* Do nothing, all the cases are addressed */
        }
    }

    return(retVal);
}
#endif /* (CY_IP_M0S8WCO) */


/* ========================================================================== */
/* ===========================    ILO SECTION    ============================ */
/* ========================================================================== */

/** \cond */
#define SRSSLT_CLK_DFT_SELECT_DFT_SEL_NC  (0UL) /* DFT_SEL not connected (output is 0) */
#define SRSSLT_CLK_DFT_SELECT_DFT_SEL_ILO (1UL) /* DFT_SEL ILO output */

#define SRSSLT_CLK_DFT_SELECT_DFT_CHCK_MSK (SRSSLT_CLK_DFT_SELECT_DFT_SEL0_Msk | \
                                            SRSSLT_CLK_DFT_SELECT_DFT_SEL1_Msk)
#define SRSSLT_CLK_DFT_SELECT_DFT_CHCK_VAL (_VAL2FLD(SRSSLT_CLK_DFT_SELECT_DFT_SEL0, \
                                                     SRSSLT_CLK_DFT_SELECT_DFT_SEL_NC) | \
                                            _VAL2FLD(SRSSLT_CLK_DFT_SELECT_DFT_SEL1, \
                                                     SRSSLT_CLK_DFT_SELECT_DFT_SEL_ILO))

#define SRSSLT_TST_DDFT_CTRL_DFT_SEL0_Pos   0UL
#define SRSSLT_TST_DDFT_CTRL_DFT_SEL0_Msk   0xFUL
#define SRSSLT_TST_DDFT_CTRL_DFT_SEL1_Pos   8UL
#define SRSSLT_TST_DDFT_CTRL_DFT_SEL1_Msk   0xF00UL

#define SRSSLT_TST_DDFT_CTRL_DFT_SEL_CLK0   (8UL)
#define SRSSLT_TST_DDFT_CTRL_DFT_SEL_CLK1   (9UL)

#define SRSSLT_TST_DDFT_CTRL_DFT_SEL_Pos    (SRSSLT_TST_DDFT_CTRL_DFT_SEL0_Pos)
#define SRSSLT_TST_DDFT_CTRL_DFT_SEL_Msk    (SRSSLT_TST_DDFT_CTRL_DFT_SEL0_Msk | SRSSLT_TST_DDFT_CTRL_DFT_SEL1_Msk)

/** \endcond */


/******************************************************************************
* Function Name: Cy_SysClk_IloStartMeasurement
***************************************************************************//**
*
* \brief Starts the ILO accuracy measurement.
*
* This function is non-blocking and needs to be called before using the
* \ref Cy_SysClk_IloCompensate() function.
*
* This function configures measurement counters to be sourced by SysClk (Counter 1)
* and ILO (Counter 2).
*
* \note SysClk should be clocked by IMO, otherwise
* Cy_SysClk_IloCompensate() function can give incorrect results.
*
* \funcusage
* \snippet sysclk/sut/sysclk_snippet.c SNIPPET_SYSCLK_ILO_COMPENSATE
* \snippet sysclk/sut/sysclk_snippet.c SNIPPET_SYSCLK_WDT_CFG
*
******************************************************************************/
void Cy_SysClk_IloStartMeasurement(void)
{
    /* Configure measurement counters to source by SysClk (Counter 1) and ILO (Counter 2)*/
    CY_REG32_CLR_SET(SRSSLT_CLK_DFT_SELECT,
                     SRSSLT_CLK_DFT_SELECT_DFT_SEL1,
                     SRSSLT_CLK_DFT_SELECT_DFT_SEL_ILO);

    CY_REG32_CLR_SET(SRSSLT_TST_DDFT_CTRL,
                     SRSSLT_TST_DDFT_CTRL_DFT_SEL,
           (_VAL2FLD(SRSSLT_TST_DDFT_CTRL_DFT_SEL0,
                     SRSSLT_TST_DDFT_CTRL_DFT_SEL_CLK0) |
            _VAL2FLD(SRSSLT_TST_DDFT_CTRL_DFT_SEL1,
                     SRSSLT_TST_DDFT_CTRL_DFT_SEL_CLK1)));
}


/******************************************************************************
* Function Name: Cy_SysClk_IloStopMeasurement
***************************************************************************//**
* \brief
* Stops the ILO accuracy measurement.
*
* Calling this function immediately stops the the ILO frequency measurement.
* Call this function before placing the device to deepsleep, if
* \ref Cy_SysClk_IloStartMeasurement() API was called before.
*
* \funcusage
* \snippet sysclk/sut/sysclk_snippet.c SNIPPET_SYSCLK_ILO_COMPENSATE
* \snippet sysclk/sut/sysclk_snippet.c SNIPPET_SYSCLK_WDT_CFG
*
******************************************************************************/
void Cy_SysClk_IloStopMeasurement(void)
{
    /* Set default configurations in 11...8 DFT register bits to zero */
    SRSSLT_CLK_DFT_SELECT &= ~SRSSLT_CLK_DFT_SELECT_DFT_SEL1_Msk;
    SRSSLT_TST_DDFT_CTRL &= SRSSLT_TST_DDFT_CTRL_DFT_SEL_Msk;
}


#define MAX_DELAY_US                     (0x1E8480UL) /* 2s */
#define MIN_DELAY_US                     (0x64UL)     /* 100 us */
#define COEF_PHUNDRED                    (0x64UL)   /* 100 */
#define ILO_PERIOD_PPH                   (0x09C4UL) /* 2500 */
#define SYS_CLK_DIVIDER                  (0x0AUL) /* 10 */
#define ILO_FREQ_2MSB                    (0x28UL) /* 40 */
#define ILO_FREQ_3LSB                    (0x3E8UL) /* 1000 */
#define ILO_DESIRED_FREQ_HZ              (40000UL) /* 40kHz */

/**********************************************************************************
* Cy_SysClk_IloCompensate() - value to walk over oversamling in calculations with
* srsslite. The oversample can be obtained when ilo frequency in equal 80 KHz and
* desired clocks are 80 000 clocks.
**********************************************************************************/
#define MAX_LITE_NUMBER                  (53600UL)

/******************************************************************************
* Function Name: Cy_SysClk_IloCompensate
***************************************************************************//**
*
* \brief Measures the current ILO accuracy.
*
* Basing on the measured frequency the required number of ILO cycles for a
* given delay (in microseconds) is obtained. The desired delay that needs to
* be compensated is passed through the desiredDelay parameter. The compensated
* cycle count is returned through the compesatedCycles pointer.
* The compensated ILO cycles can then be used to define the WDT period value,
* effectively compensating for the ILO inaccuracy and allowing a more
* accurate WDT interrupt generation.
*
* \ref Cy_SysClk_IloStartMeasurement() function should be called prior to calling this function.
*
* \note SysClk should be clocked by IMO, otherwise the
* Cy_SysClk_IloCompensate() function can give incorrect results.
*
* \note If the System clock frequency is changed in runtime, the
* \ref SystemCoreClockUpdate() should be called before
* calling a next Cy_SysClk_IloCompensate().
*
* \note For a correct WDT or DeepSleep Timers functioning with ILO compensating
* the \ref Cy_SysClk_IloCompensate() should be called before WDT or DeepSleep Timers
* enabling.
*
* \warning Do not enter deep sleep mode until the function returns CY_SYSCLK_SUCCESS.
*
* \param desiredDelay Required delay in microseconds.
*                     Valid range is 100 ... 2 000 000 us.
*
* \note The desiredDelay range 100..2000000 is mathematically possible, but:\n
* Physically, the longest WDT period is 65536 * ILO clock period,\n
* which is nominally 25us, so the real maximum desiredDelay is 1.63s @40kHz ILO.\n
* The 100us is about a four ILO clocks, so such a small desiredDelay may be imprecise (~25% of error or even more).\n
* Therefore, the range 1ms..1s (1000...1000000) is recommended as practically applicable.
*
* \param *compensatedCycles The pointer to the variable in which the required
* number of ILO cycles for the given delay will be returned.
*
* \details The value returned in *compensatedCycles pointer is not valid until the
* function returns CY_SYSCLK_SUCCESS.
*
* \return The status \ref cy_en_sysclk_status_t
* - \ref CY_SYSCLK_SUCCESS - The compensation process is complete and the
* compensated cycles value is returned in the compensatedCycles pointer.
* - \ref CY_SYSCLK_BAD_PARAM - One or more invalid parameters
* - \ref CY_SYSCLK_STARTED - Indicates measurement is in progress. It is
* strongly recommended to do not make pauses between API calling. The
* function should be called repeatedly until the API returns CY_SYSCLK_SUCCESS.
* - \ref CY_SYSCLK_INVALID_STATE - Indicates that measurement not started.
* The user should call \ref Cy_SysClk_IloStartMeasurement() API before calling
* this function.
*
* \funcusage
* \snippet sysclk/sut/sysclk_snippet.c SNIPPET_SYSCLK_ILO_COMPENSATE
* \snippet sysclk/sut/sysclk_snippet.c SNIPPET_SYSCLK_WDT_CFG
*
*******************************************************************************/
cy_en_sysclk_status_t Cy_SysClk_IloCompensate(uint32_t desiredDelay , uint32_t * compensatedCycles)
{
    uint32_t iloCompensatedCycles;
    uint32_t desiredDelayInCounts;
    static bool compRunStat = false; /* compensation running status */
    cy_en_sysclk_status_t retVal = CY_SYSCLK_INVALID_STATE;

    /* Check if CySysStartMeasurement was called before */
    bool ddftClkSel = (SRSSLT_TST_DDFT_CTRL == (_VAL2FLD(SRSSLT_TST_DDFT_CTRL_DFT_SEL0,
                                           SRSSLT_TST_DDFT_CTRL_DFT_SEL_CLK0) |
                                  _VAL2FLD(SRSSLT_TST_DDFT_CTRL_DFT_SEL1,
                                           SRSSLT_TST_DDFT_CTRL_DFT_SEL_CLK1)));
    bool ddftCheck = (SRSSLT_CLK_DFT_SELECT_DFT_CHCK_VAL == (SRSSLT_CLK_DFT_SELECT & SRSSLT_CLK_DFT_SELECT_DFT_CHCK_MSK));

    if ((MIN_DELAY_US > desiredDelay) ||
        (MAX_DELAY_US < desiredDelay) ||
        (NULL == compensatedCycles))
    {
        retVal = CY_SYSCLK_BAD_PARAM;
    }
    /* Check if CySysStartMeasurement was called before */
    else if (ddftClkSel && ddftCheck)
    {
        if(compRunStat)
        {
            /* Wait until counter 1 stopped counting and after it calculate compensated cycles */
            if(0UL != (SRSSLT_TST_TRIM_CNTR1 & SRSSLT_TST_TRIM_CNTR1_COUNTER_DONE_Msk))
            {
                if (0UL != SRSSLT_TST_TRIM_CNTR2)
                {
                    /* Calculate required number of ILO cycles for given delay */
                    desiredDelayInCounts = CY_SYSLIB_DIV_ROUND(desiredDelay * COEF_PHUNDRED, ILO_PERIOD_PPH);

                    if(MAX_LITE_NUMBER < desiredDelayInCounts)
                    {
                        iloCompensatedCycles = (((SRSSLT_TST_TRIM_CNTR2 * SystemCoreClock) /
                            (SystemCoreClock >> SYS_CLK_DIVIDER)) / ILO_FREQ_2MSB) * (desiredDelayInCounts / ILO_FREQ_3LSB);
                    }
                    else
                    {
                        iloCompensatedCycles = (((SRSSLT_TST_TRIM_CNTR2 * SystemCoreClock) /
                            (SystemCoreClock >> SYS_CLK_DIVIDER)) * desiredDelayInCounts) / ILO_DESIRED_FREQ_HZ;
                    }

                    *compensatedCycles = iloCompensatedCycles;
                    compRunStat = false;
                    retVal = CY_SYSCLK_SUCCESS;
                }
            }
            else
            {
                retVal = CY_SYSCLK_STARTED;
            }
        }
        else
        {
            /* Reload CNTR 1 count value for next measurement cycle*/
            SRSSLT_TST_TRIM_CNTR1 = (SystemCoreClock >> SYS_CLK_DIVIDER);
            compRunStat = true;
            retVal = CY_SYSCLK_STARTED;
        }
    }
    else
    {
        /* Do nothing, return CY_SYSCLK_INVALID_STATE */
    }

    return (retVal);
}


#if (defined(CY_IP_M0S8EXCO) && (CY_IP_M0S8EXCO == 1u)) || defined(CY_DOXYGEN)
/* ========================================================================== */
/* ===========================    ECO SECTION    ============================ */
/* ========================================================================== */

#define CY_SYSCLK_ECO_CONFIG_CLK_EN_TIMEOUT_US (10U)


/** \cond *********************************************************************
* Function Name: cy_sqrt
* Calculates square root.
* input is 32-bit wide.
* result is 16-bit wide.
*******************************************************************************/
static uint32_t cy_sqrt(uint32_t x);
static uint32_t cy_sqrt(uint32_t x)
{
    uint32_t i;
    uint32_t res = 0UL;
    uint32_t add = 0x8000UL;

    for(i = 0UL; i < 16UL; i++)
    {
        uint32_t tmp = res | add;

        if (x >= (tmp * tmp))
        {
            res = tmp;
        }

        add >>= 1U;
    }

    return (res);
}

static uint32_t ecoFreq = 0UL; /* Internal storage for ECO frequency user setting */

#define CY_SYSCLK_ECO_FREQ_MIN (4000000UL)  /* 4 MHz */
#define CY_SYSCLK_ECO_FREQ_MAX (33333000UL) /* 33.333 MHz */
#define CY_SYSCLK_ECO_CLD_MAX  (100UL)      /* 100 pF */
#define CY_SYSCLK_ECO_ESR_MAX  (1000UL)     /* 1000 Ohm */
#define CY_SYSCLK_ECO_DRV_MAX  (2000UL)     /* 2 mW */

#define CY_SYSCLK_ECO_IS_FREQ_VALID(freq) ((CY_SYSCLK_ECO_FREQ_MIN <= (freq)) && ((freq) <= CY_SYSCLK_ECO_FREQ_MAX))
#define CY_SYSCLK_ECO_IS_CLD_VALID(cld)   ((0UL < (cld)) && ((cld) <= CY_SYSCLK_ECO_CLD_MAX))
#define CY_SYSCLK_ECO_IS_ESR_VALID(esr)   ((0UL < (esr)) && ((esr) <= CY_SYSCLK_ECO_ESR_MAX))
#define CY_SYSCLK_ECO_IS_DRV_VALID(drv)   ((0UL < (drv)) && ((drv) <= CY_SYSCLK_ECO_DRV_MAX))
/** \endcond */


/**
* \addtogroup group_sysclk_eco_funcs
* \{
*/

/*******************************************************************************
* Function Name: Cy_SysClk_EcoConfigure
****************************************************************************//**
*
* Configures the external crystal oscillator (ECO) trim bits based on crystal
* characteristics. This function should be called only when the ECO is disabled.
*
* \param freq Operating frequency of the crystal in Hz.
* Valid range: 4000000...33333000 (4..33.333 MHz).
*
* \param cLoad Crystal load capacitance in pF.
* Valid range: 1...100.
*
* \param esr Effective series resistance of the crystal in ohms.
* Valid range: 1...1000.
*
* \param driveLevel Crystal drive level in uW.
* Valid range: 1...2000.
*
* \return Error / status code \ref cy_en_sysclk_status_t : \n
* CY_SYSCLK_SUCCESS - ECO configuration completed successfully \n
* CY_SYSCLK_BAD_PARAM - One or more invalid parameters \n
* CY_SYSCLK_INVALID_STATE - ECO already enabled
*
* \note
* The following calculations are implemented in integer 32-bitwise math:
*
* \verbatim
*   freqKhz = freq / 1000
*   maxAmpl = sqrt(drivelevel / 2 / esr) / 3.14 / freqKhz / cLoad
*   ampSect = INT(5 * 4 * 3.14^2 * freqKhz^2 * cLoad^2 * 4 * esr / 1000000000 / 1000000 / 4.5)
*
*   As a result of the above calculations, maxAmpl must be >= 0.5, and the
*   number of amplifier sections must be <= 3, otherwise this function returns with
*   a parameter error.
*
*   atrim = maxAmpl < 0.6 ? 0 :
*           maxAmpl < 0.7 ? 1 :
*           maxAmpl < 0.8 ? 2 :
*           maxAmpl < 0.9 ? 3 :
*           maxAmpl < 1.025 ? 4 :
*           maxAmpl < 1.150 ? 5 :
*           maxAmpl < 1.275 ? 6 : 7

*   wdtrim = maxAmpl < 1.2 ? INT(5 * maxAmpl) - 2 : 3

*   gtrim = ampSect > 1 ? ampSect : ampSect == 1 ? 0 : 1

*   rtrim = freqKhz > 30000 ? 0 :
*           freqMHz > 24000 ? 1 :
*           freqMHz > 17000 ? 2 : 3
*
*   ftrim = rtrim
*
* \endverbatim
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_EcoConfigure
*
*******************************************************************************/
cy_en_sysclk_status_t Cy_SysClk_EcoConfigure(uint32_t freq, uint32_t cLoad, uint32_t esr, uint32_t driveLevel)
{
    cy_en_sysclk_status_t retVal = CY_SYSCLK_BAD_PARAM;

    if (Cy_SysClk_EcoIsEnabled())
    {
        retVal = CY_SYSCLK_INVALID_STATE;
    }
    else if ((CY_SYSCLK_ECO_IS_FREQ_VALID(freq)) &&
             (CY_SYSCLK_ECO_IS_CLD_VALID(cLoad)) &&
             (CY_SYSCLK_ECO_IS_ESR_VALID(esr))   &&
             (CY_SYSCLK_ECO_IS_DRV_VALID(driveLevel)))
    {
        uint32_t freqKhz = CY_SYSLIB_DIV_ROUND(freq, 1000UL);

        /* calculate intermediate values */
        uint32_t maxAmpl = CY_SYSLIB_DIV_ROUND((159155UL * /* 5 * 100000 / PI */
                   cy_sqrt(CY_SYSLIB_DIV_ROUND(2000000UL * driveLevel, esr))), /* scaled by 2 */
                                               (freqKhz * cLoad)); /* The result is scaled by 10^3 */

        /* (4.5 * 10^9) / (5 * 4 * 4 * PI^2) = 5699316,5798814996437182198055472.. -> 56993, scaled by 100 */
        uint32_t ampSect = (CY_SYSLIB_DIV_ROUND(cLoad * cLoad *
                            CY_SYSLIB_DIV_ROUND(freqKhz * freqKhz, 56993UL), 1000UL) * esr) / 1000000UL;

        if ((maxAmpl >= 500UL) && (ampSect <= 3UL)) /* Error if input parameters cause erroneous intermediate values */
        {
            uint32_t wdtrim = (maxAmpl < 1200UL) ? (5UL * maxAmpl / 1000UL) - 2UL : 3UL;

            uint32_t atrim = (maxAmpl < 600UL)  ? 0UL :
                            ((maxAmpl < 700UL)  ? 1UL :
                            ((maxAmpl < 800UL)  ? 2UL :
                            ((maxAmpl < 900UL)  ? 3UL :
                            ((maxAmpl < 1025UL) ? 4UL :
                            ((maxAmpl < 1150UL) ? 5UL :
                            ((maxAmpl < 1275UL) ? 6UL : 7UL))))));

            uint32_t ftrim = ((freq > 30000000UL) ? 0UL :
                              ((freq > 24000000UL) ? 1UL :
                               ((freq > 17000000UL) ? 2UL : 3UL)));

            uint32_t gtrim = (ampSect > 1UL) ? ampSect :
                            ((ampSect == 1UL) ? 0UL : 1UL);

            EXCO_ECO_CONFIG = (maxAmpl < 2000UL) ? EXCO_ECO_CONFIG_AGC_EN_Msk : 0x0UL;

            EXCO_ECO_TRIM0 = _VAL2FLD(EXCO_ECO_TRIM0_WDTRIM, wdtrim) |
                             _VAL2FLD(EXCO_ECO_TRIM0_ATRIM, atrim);

            EXCO_ECO_TRIM1 = _VAL2FLD(EXCO_ECO_TRIM1_FTRIM, ftrim) |
                             _VAL2FLD(EXCO_ECO_TRIM1_RTRIM, ftrim) | /* rtrim = ftrim */
                             _VAL2FLD(EXCO_ECO_TRIM1_GTRIM, gtrim);

            ecoFreq = freq; /* Store the ECO frequency */

            retVal = CY_SYSCLK_SUCCESS;
        }
    }
    else
    {
        /* return CY_SYSCLK_BAD_PARAM */
    }

    return (retVal);
}


/*******************************************************************************
* Function Name: Cy_SysClk_EcoEnable
****************************************************************************//**
*
* Enables the external crystal oscillator (ECO). This function should be called
* after \ref Cy_SysClk_EcoConfigure.
*
* \param timeoutUs Amount of time in microseconds to wait for the ECO to stabilize.
* To avoid waiting for stabilization, set this parameter to 0.
*
* \return Error / status code \ref cy_en_sysclk_status_t : \n
* CY_SYSCLK_SUCCESS - ECO is enabled \n
* CY_SYSCLK_TIMEOUT - ECO timed out and did not stabilized \n
* CY_SYSCLK_INVALID_STATE - ECO is not configured using \ref Cy_SysClk_EcoConfigure.
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_EcoConfigure
*
*******************************************************************************/
cy_en_sysclk_status_t Cy_SysClk_EcoEnable(uint32_t timeoutUs)
{
    cy_en_sysclk_status_t retVal = CY_SYSCLK_INVALID_STATE;

    /* Invalid state error if ECO is not configured */
    if (0UL != ecoFreq)
    {
        bool zeroTimeout = (0UL == timeoutUs);

        if (!Cy_SysClk_EcoIsEnabled())
        {
            EXCO_ECO_CONFIG |= EXCO_ECO_CONFIG_ENABLE_Msk;
            Cy_SysLib_DelayUs(CY_SYSCLK_ECO_CONFIG_CLK_EN_TIMEOUT_US);
            EXCO_ECO_CONFIG |= EXCO_ECO_CONFIG_CLK_EN_Msk;
        }

        /* Wait for CY_SYSCLK_ECOSTAT_STABLE */
        while ((CY_SYSCLK_ECO_STABLE != Cy_SysClk_EcoGetStatus()) && (0UL != timeoutUs))
        {
            timeoutUs--;
            Cy_SysLib_DelayUs(1U);
        }

        if (zeroTimeout || (0UL != timeoutUs))
        {
            retVal = CY_SYSCLK_SUCCESS;
        }
        else
        {
            retVal = CY_SYSCLK_TIMEOUT;
            Cy_SysClk_EcoDisable();
        }
    }

    return (retVal);
}


/*******************************************************************************
* Function Name: Cy_SysClk_EcoGetFrequency
****************************************************************************//**
*
* Returns the frequency of the external crystal oscillator (ECO).
*
* \return The frequency of the ECO.
*
* \note If the ECO is not enabled or stable - a zero is returned.
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_EcoConfigure
*
*******************************************************************************/
uint32_t Cy_SysClk_EcoGetFrequency(void)
{
    return ((Cy_SysClk_EcoIsEnabled() && (CY_SYSCLK_ECO_STABLE == Cy_SysClk_EcoGetStatus())) ? ecoFreq : 0UL);
}
/** \} group_sysclk_eco_funcs */


#if (defined(EXCO_PLL_PRESENT) && (EXCO_PLL_PRESENT == 1u)) || defined(CY_DOXYGEN)
/* ========================================================================== */
/* ===========================    PLL SECTION    ============================ */
/* ========================================================================== */

#if (defined (EXCO_PLL_REF_IN_EN) && (EXCO_PLL_REF_IN_EN == 1u)) || defined(CY_DOXYGEN)

#if (CY_IP_M0S8EXCO_VERSION == 1U)
#define  CY_SYSCLK_PLL_IS_SRC_VALID(src) (((src) == CY_SYSCLK_PLL_SRC_ECO) || \
                                          ((src) == CY_SYSCLK_PLL_SRC_IMO))
#else /* (CY_IP_M0S8EXCO_VERSION == 2U) */
#define  CY_SYSCLK_PLL_IS_SRC_VALID(src) (((src) == CY_SYSCLK_PLL_SRC_ECO)    || \
                                          ((src) == CY_SYSCLK_PLL_SRC_EXTREF) || \
                                          ((src) == CY_SYSCLK_PLL_SRC_IMO))
#endif /* (CY_IP_M0S8EXCO_VERSION == 1U) */

#define CY_SYSCLK_EXCO_PGM_CLK_SEQ_GEN (5UL)


/*******************************************************************************
* Function Name: Cy_SysClk_EcoSeqGen
********************************************************************************
*
* Generates the ECO clock sequence for EXCO.CLK_SELECT programming.
*
*******************************************************************************/
void Cy_SysClk_EcoSeqGen(void)
{
    if (0UL == Cy_SysClk_EcoGetFrequency()) /* If ECO is not working */
    {
        /* Generate clock sequence to change clock source in CY_SYS_ECO_CLK_SELECT_REG */
        EXCO_EXCO_PGM_CLK |= EXCO_EXCO_PGM_CLK_ENABLE_Msk;

        for(uint32_t i = 0UL; i < CY_SYSCLK_EXCO_PGM_CLK_SEQ_GEN; i++)
        {
            EXCO_EXCO_PGM_CLK |= EXCO_EXCO_PGM_CLK_CLK_ECO_Msk;
            EXCO_EXCO_PGM_CLK &= ~EXCO_EXCO_PGM_CLK_CLK_ECO_Msk;
        }

        EXCO_EXCO_PGM_CLK &= ~EXCO_EXCO_PGM_CLK_ENABLE_Msk;
    }
}

/**
* \addtogroup group_sysclk_pll_funcs
* \{
*/

/*******************************************************************************
* Function Name: Cy_SysClk_PllSetSource
****************************************************************************//**
*
* Selects the PLL reference clock of the selected ClkHf.
*
* \param pllNum the number of PLL instance, starting from 0.
* If there is only one PLL in device - the 0 is the only valid number.
*
* \param source \ref cy_en_sysclk_pll_src_t
*
* \return  Error / status code \ref cy_en_sysclk_status_t : \n
* CY_SYSCLK_SUCCESS - the PLL reference clock source is selected \n
* CY_SYSCLK_INVALID_STATE - the PLL reference clock source is not enabled \n
* CY_SYSCLK_BAD_PARAM - some input parameter is invalid
*
* \note Call \ref SystemCoreClockUpdate after this function calling if
* ClkSys frequency is affected.
*
* \note Call \ref Cy_SysLib_SetWaitStates before this function calling if
* ClkSys frequency is increasing.
*
* \note Call \ref Cy_SysLib_SetWaitStates after this function calling if
* ClkSys frequency is decreasing.
*
* \note In case of switching to the \ref CY_SYSCLK_PLL_SRC_EXTREF the
* EXTREF frequency should be specified using \ref Cy_SysClk_ExtRefSetFrequency.
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_PllConfigure
*
*******************************************************************************/
cy_en_sysclk_status_t Cy_SysClk_PllSetSource(uint32_t pllNum, cy_en_sysclk_pll_src_t source)
{
    cy_en_sysclk_status_t retVal = CY_SYSCLK_SUCCESS;

    if ((0UL == pllNum) && CY_SYSCLK_PLL_IS_SRC_VALID(source))
    {
        if (source != Cy_SysClk_PllGetSource(pllNum))
        {
            if (((CY_SYSCLK_PLL_SRC_ECO == source) && (0UL != Cy_SysClk_EcoGetFrequency())) ||
#if (CY_IP_M0S8EXCO_VERSION == 2U)
                ((CY_SYSCLK_PLL_SRC_EXTREF == source) && (0UL != Cy_SysClk_ExtRefGetFrequency())) ||
#endif /* (CY_IP_M0S8EXCO_VERSION == 2U) */
                ((CY_SYSCLK_PLL_SRC_IMO == source) && Cy_SysClk_ImoIsEnabled()))
            {
                CY_REG32_CLR_SET(EXCO_CLK_SELECT, EXCO_CLK_SELECT_REF_SEL, source);
                Cy_SysClk_EcoSeqGen();
            }
            else
            {
                retVal = CY_SYSCLK_INVALID_STATE;
            }
        }
    }
    else
    {
        retVal = CY_SYSCLK_BAD_PARAM;
    }

    return (retVal);
}
/** \} group_sysclk_pll_funcs */
#endif /* (EXCO_PLL_REF_IN_EN == 1u) */


/* PLL REFERENCE_DIV bitfield allowable range */
#define PLL_MIN_REF_DIV      (0x00UL)
#define PLL_MAX_REF_DIV      (0x3FUL)

/* PLL FEEDBACK_DIV bitfield allowable range selection */
#define PLL_MIN_FB_DIV   (8UL)
#define PLL_MAX_FB_DIV   (255UL)

/* PLL OUTPUT_DIV bitfield allowable range */
#define PLL_MIN_OUT_DIV  (0UL)
#define PLL_MAX_OUT_DIV  (3UL)

/* Internal PLL frequencies ranges */
#define PLL_MIN_FVCO     (22500000UL)
#define PLL_THR_FVCO     (67000000UL) /* Threshold for ICP setting */
#define PLL_MAX_FVCO     (104000000UL)
#define PLL_MIN_FPFD     (1000000UL)
#define PLL_MAX_FPFD     (3000000UL)

/* PLL input and output frequency limits */
#define PLL_MIN_IN_FREQ  (1000000UL)
#define PLL_MAX_IN_FREQ  (64000000UL)
#define PLL_MIN_OUT_FREQ (PLL_MIN_FVCO / (1UL << PLL_MAX_OUT_DIV))
#define PLL_MAX_OUT_FREQ ((PLL_MAX_FVCO > CY_SYSCLK_HF_CLK_MAX_FREQ) ? CY_SYSCLK_HF_CLK_MAX_FREQ : PLL_MAX_FVCO)

#define PLL_ICP_SEL_LT67MHZ (2U) /* For FVCO frequency <= 67 MHz */
#define PLL_ICP_SEL_GT67MHZ (3U) /* For FVCO frequency > 67 MHz */

/**
* \addtogroup group_sysclk_pll_funcs
* \{
*/
/*******************************************************************************
* Function Name: Cy_SysClk_PllConfigure
****************************************************************************//**
*
* Configures a given PLL.
* The configuration formula used is:
*   Fout = pll_clk * (P / Q / div_out), where:
*     Fout is the desired output frequency
*     pll_clk is the frequency of the input source
*     P is the feedback divider. Its value is in bitfield FEEDBACK_DIV.
*     Q is the reference divider. Its value is in bitfield REFERENCE_DIV.
*     div_out is the reference divider. Its value is in bitfield OUTPUT_DIV.
*
* \param pllNum the number of PLL instance, starting from 0.
* If there is only one PLL in device - the 0 is the only valid number.
*
* \param config The pointer to a configuration structure \ref cy_stc_sysclk_pll_config_t
*
* \return  Error / status code \ref cy_en_sysclk_status_t : \n
* CY_SYSCLK_SUCCESS - PLL successfully configured \n
* CY_SYSCLK_INVALID_STATE - PLL not configured because it is already enabled \n
* CY_SYSCLK_BAD_PARAM - One or more invalid parameters.
*
* \note
* In case of returning CY_SYSCLK_BAD_PARAM the function does not write anything into
* the configuration register, so either the previous correct configuration or
* the default configuration remains in the register.
*
* \note
* Call this function after changing the PLL input frequency, for example if
* \ref Cy_SysClk_ImoSetFrequency() or \ref Cy_SysClk_PllSetSource() is called.
*
* \note
* Do not call this function when the PLL is enabled. If it is called, then this function
* returns immediately with an error return value and no register updates.
*
* \note
* Call \ref SystemCoreClockUpdate after this function calling
* if it affects the CLK_HF0 frequency.
*
* \note
* Call \ref Cy_SysLib_SetWaitStates before calling this function if
* the PLL is the source of CLK_HF0 and the PLL frequency is increasing.
*
* \note
* Call \ref Cy_SysLib_SetWaitStates after calling this function if
* the PLL is the source of CLK_HF0 and the PLL frequency is decreasing.
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_PllConfigure
*
*******************************************************************************/
cy_en_sysclk_status_t Cy_SysClk_PllConfigure(uint32_t pllNum, const cy_stc_sysclk_pll_config_t *config)
{
    cy_en_sysclk_status_t retVal = CY_SYSCLK_BAD_PARAM;
    uint32_t inputFreq = 0U;

    if (0UL == config->inputFreq)
    {
        if (CY_SYSCLK_PLL_SRC_ECO == Cy_SysClk_PllGetSource(pllNum))
        {
            inputFreq = Cy_SysClk_EcoGetFrequency();
        }
    #if (CY_IP_M0S8EXCO_VERSION == 2U)
        else if (CY_SYSCLK_PLL_SRC_EXTREF == Cy_SysClk_PllGetSource(pllNum))
        {
            inputFreq = Cy_SysClk_ExtRefGetFrequency();
        }
    #endif /* (CY_IP_M0S8EXCO_VERSION == 2U) */
        else /* IMO */
        {
            inputFreq = Cy_SysClk_ImoGetFrequency();
        }

        if (0UL == inputFreq)
        {
            retVal = CY_SYSCLK_INVALID_STATE;
        }
    }
    else
    {
        inputFreq = config->inputFreq;
    }

    CY_MISRA_DEVIATE_BLOCK_START('MISRA C-2012 Rule 14.3', 2, \
    'The CY_SYSCLK_HF_CLK_MAX_FREQ is device-specific, and so PLL_MAX_OUT_FREQ expression may be invariant.');
    if ((PLL_MIN_IN_FREQ <= inputFreq)  && (inputFreq <= PLL_MAX_IN_FREQ) &&
        (PLL_MIN_OUT_FREQ <= config->outputFreq) && (config->outputFreq <= PLL_MAX_OUT_FREQ))
    {
        CY_MISRA_BLOCK_END('MISRA C-2012 Rule 14.3');

        cy_stc_sysclk_pll_manual_config_t manualConfig = {0U, 0U, 0U, 0U};

        /* for each possible value of OUTPUT_DIV and REFERENCE_DIV (Q), try
           to find a value for FEEDBACK_DIV (P) that gives an output frequency
           as close as possible to the desired output frequency. */
        uint32_t q, fpfd;
        uint32_t foutBest = 0UL; /* to ensure at least one pass through the for loops below */

        /* REFERENCE_DIV (Q) selection */
        for (q = PLL_MIN_REF_DIV; q <= PLL_MAX_REF_DIV; q++)
        {
            fpfd = CY_SYSLIB_DIV_ROUND(inputFreq, 1UL + q);

            if ((PLL_MIN_FPFD <= fpfd) && (fpfd <= PLL_MAX_FPFD))
            {
                uint32_t p, fvco;

                /* FEEDBACK_DIV (P) selection */
                for (p = PLL_MIN_FB_DIV; p <= PLL_MAX_FB_DIV; p++)
                {
                    /* Calculate the intermediate Fvco, and make sure that it's in range */
                    fvco = fpfd * p;

                    if ((PLL_MIN_FVCO <= fvco) && (fvco <= PLL_MAX_FVCO))
                    {
                        uint32_t out;

                        /* OUTPUT_DIV selection */
                        for (out = PLL_MIN_OUT_DIV; out <= PLL_MAX_OUT_DIV; out++)
                        {
                            /* Calculate what output frequency will actually be produced.
                               If it's closer to the target than what we have so far, then save it. */
                            uint32_t fout = CY_SYSLIB_DIV_ROUND(fvco, 1UL << out);

                            if ((uint32_t)abs((int32_t)fout - (int32_t)(config->outputFreq)) <
                                (uint32_t)abs((int32_t)foutBest - (int32_t)(config->outputFreq)))
                            {
                                foutBest = fout;
                                manualConfig.feedbackDiv  = (uint8_t)p;
                                manualConfig.referenceDiv = (uint8_t)q;
                                manualConfig.outputDiv    = (uint8_t)out;
                                manualConfig.icp          = (uint8_t)((PLL_THR_FVCO < fvco) ? PLL_ICP_SEL_GT67MHZ : PLL_ICP_SEL_LT67MHZ);
                            }

                            if (foutBest == (config->outputFreq))
                            {
                                break;
                            }
                        }
                    }

                    if (foutBest == (config->outputFreq))
                    {
                        break;
                    }
                }
            }

            if (foutBest == (config->outputFreq))
            {
                break;
            }
        } /* exit loops if foutBest equals outputFreq */

        /* configure PLL based on calculated values */
        retVal = Cy_SysClk_PllManualConfigure(pllNum, &manualConfig);
    } /* if no error */

    return (retVal);
}

/** \cond INTERNAL */
#define EXCO_PLL_CFG_Pos (EXCO_PLL_CONFIG_FEEDBACK_DIV_Pos)
#define EXCO_PLL_CFG_Msk (EXCO_PLL_CONFIG_FEEDBACK_DIV_Msk  | \
                          EXCO_PLL_CONFIG_REFERENCE_DIV_Msk | \
                          EXCO_PLL_CONFIG_OUTPUT_DIV_Msk    | \
                          EXCO_PLL_CONFIG_ICP_SEL_Msk)

#define CY_SYSCLK_IS_ICP_VALID(icp)  ((CY_SYSCLK_IS_PLL_ICP_LT67MHZ == (icp)) || \
                                      (CY_SYSCLK_IS_PLL_ICP_GT67MHZ == (icp)))
/** \endcond */

/*******************************************************************************
* Function Name: Cy_SysClk_PllManualConfigure
****************************************************************************//**
*
* Manually configures a PLL based on user inputs.
*
* \param pllNum the number of PLL instance, starting from 0.
* If there is only one PLL in device - the 0 is the only valid number.
*
* \param config \ref cy_stc_sysclk_pll_manual_config_t
*
* \return  Error / status code \ref cy_en_sysclk_status_t : \n
* CY_SYSCLK_SUCCESS - PLL successfully configured \n
* CY_SYSCLK_INVALID_STATE - PLL not configured because it is already enabled \n
* CY_SYSCLK_BAD_PARAM - One or more invalid parameters.
*
* \note
* In case of returning CY_SYSCLK_BAD_PARAM the function does not write anything into
* the configuration register, so either the previous correct configuration or
* the default configuration remains in the register.
*
* \note
* Call this function after changing the PLL input frequency, for example if
* \ref Cy_SysClk_ImoSetFrequency() or \ref Cy_SysClk_PllSetSource() is called.
*
* \note
* Do not call this function when the PLL is enabled. If it is called, then this function
* returns immediately with an error return value and no register updates.
*
* \note
* Call \ref SystemCoreClockUpdate after this function calling
* if it affects the CLK_HF0 frequency.
*
* \note
* Call \ref Cy_SysLib_SetWaitStates before calling this function if
* the PLL is the source of CLK_HF0 and the PLL frequency is increasing.
*
* \note
* Call \ref Cy_SysLib_SetWaitStates after calling this function if
* the PLL is the source of CLK_HF0 and the PLL frequency is decreasing.
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_PllManualConfigure
*
*******************************************************************************/
cy_en_sysclk_status_t Cy_SysClk_PllManualConfigure(uint32_t pllNum, const cy_stc_sysclk_pll_manual_config_t *config)
{
    cy_en_sysclk_status_t retVal = CY_SYSCLK_BAD_PARAM;

    /* check for errors */
    if ((0UL == pllNum) &&
        (CY_SYSCLK_IS_ICP_VALID(config->icp)) &&
        (PLL_MAX_OUT_DIV >= (uint32_t)config->outputDiv) &&
        (PLL_MAX_REF_DIV >= (uint32_t)config->referenceDiv) &&
        (PLL_MIN_FB_DIV  <= (uint32_t)config->feedbackDiv))
    {
        if (Cy_SysClk_PllIsEnabled(pllNum))
        {
            retVal = CY_SYSCLK_INVALID_STATE;
        }
        else /* no errors */
        {
            uint32_t locPllCfg = _VAL2FLD(EXCO_PLL_CONFIG_FEEDBACK_DIV,  config->feedbackDiv)  |
                                 _VAL2FLD(EXCO_PLL_CONFIG_REFERENCE_DIV, config->referenceDiv) |
                                 _VAL2FLD(EXCO_PLL_CONFIG_OUTPUT_DIV,    config->outputDiv)    |
                                 _VAL2FLD(EXCO_PLL_CONFIG_ICP_SEL,       config->icp);

            CY_REG32_CLR_SET(EXCO_PLL_CONFIG, EXCO_PLL_CFG, locPllCfg); /* To preserve BYPASS_SEL bits */

            retVal = CY_SYSCLK_SUCCESS;
        }
    }

    return (retVal);
}

/*******************************************************************************
* Function Name: Cy_SysClk_PllGetConfiguration
****************************************************************************//**
*
* Reports configuration settings for a PLL.
*
* \param pllNum the number of PLL instance, starting from 0.
* If there is only one PLL in device - the 0 is the only valid number.
*
* \param config \ref cy_stc_sysclk_pll_manual_config_t
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_PllManualConfigure
*
*******************************************************************************/
void Cy_SysClk_PllGetConfiguration(uint32_t pllNum, cy_stc_sysclk_pll_manual_config_t * config)
{
    CY_ASSERT_L1(0UL == pllNum);
    CY_ASSERT_L1(NULL != config);

    if ((0UL == pllNum) && (NULL != config))
    {
        uint32_t locReg = EXCO_PLL_CONFIG;
        config->feedbackDiv  = (uint8_t)_FLD2VAL(EXCO_PLL_CONFIG_FEEDBACK_DIV,  locReg);
        config->referenceDiv = (uint8_t)_FLD2VAL(EXCO_PLL_CONFIG_REFERENCE_DIV, locReg);
        config->outputDiv    = (uint8_t)_FLD2VAL(EXCO_PLL_CONFIG_OUTPUT_DIV,    locReg);
        config->icp          = (uint8_t)_FLD2VAL(EXCO_PLL_CONFIG_ICP_SEL,       locReg);
    }
}

/*******************************************************************************
* Function Name: Cy_SysClk_PllEnable
****************************************************************************//**
*
* Enables the PLL. The PLL should be configured before calling this function.
*
* \param pllNum the number of PLL instance, starting from 0.
* If there is only one PLL in device - the 0 is the only valid number.
*
* \param timeoutUs amount of time in microseconds to wait for the PLL to lock.
* If the lock doesn't occur, PLL is stopped. To avoid waiting for lock, set this to 0
* and manually check for lock using \ref Cy_SysClk_PllIsLocked.
*
* \return Error / status code \ref cy_en_sysclk_status_t : \n
* CY_SYSCLK_SUCCESS - PLL successfully enabled \n
* CY_SYSCLK_TIMEOUT - Timeout waiting for PLL lock \n
* CY_SYSCLK_BAD_PARAM - invalid clock path number
*
* \note
* Call \ref SystemCoreClockUpdate after this function calling
* if it affects the CLK_HF0 frequency.
*
* \note
* Call \ref Cy_SysLib_SetWaitStates before calling this function if
* the PLL is the source of CLK_HF0 and the CLK_HF0 frequency is increasing.
*
* \note
* Call \ref Cy_SysLib_SetWaitStates after calling this function if
* the PLL is the source of CLK_HF0 and the CLK_HF0 frequency is decreasing.
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_PllConfigure
*
*******************************************************************************/
cy_en_sysclk_status_t Cy_SysClk_PllEnable(uint32_t pllNum, uint32_t timeoutUs)
{
    cy_en_sysclk_status_t retVal = CY_SYSCLK_BAD_PARAM;

    if (0UL == pllNum)
    {
        bool zeroTimeout = (0UL == timeoutUs);

        /* Isolate PLL outputs */
        EXCO_PLL_CONFIG &= ~EXCO_PLL_CONFIG_ISOLATE_N_Msk;

        /* first set the PLL enable bit */
        EXCO_PLL_CONFIG |= EXCO_PLL_CONFIG_ENABLE_Msk;

        Cy_SysLib_DelayUs(5U);

        /* De-isolate PLL after PLL enabled */
        EXCO_PLL_CONFIG |= EXCO_PLL_CONFIG_ISOLATE_N_Msk;

        /* now do the timeout wait for PLL_STATUS, bit LOCKED */
        while ((!Cy_SysClk_PllIsLocked(pllNum)) && (0UL != timeoutUs))
        {
            timeoutUs--;
            Cy_SysLib_DelayUs(1U);
        }

        if (zeroTimeout || (0UL != timeoutUs))
        {
            retVal = CY_SYSCLK_SUCCESS;
        }
        else
        {
            retVal = CY_SYSCLK_TIMEOUT;
            Cy_SysClk_PllDisable(pllNum);
        }
    }
    return (retVal);
}


/*******************************************************************************
* Function Name: Cy_SysClk_PllGetFrequency
****************************************************************************//**
*
* Reports the output frequency of the specified PLL.
*
* \param pllNum the number of PLL instance, starting from 0.
* If there is only one PLL in device - the 0 is the only valid number.
*
* \return The frequency, in Hz.
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_PllManualConfigure
*
*******************************************************************************/
uint32_t Cy_SysClk_PllGetFrequency(uint32_t pllNum)
{
    uint32_t freq;
#if (defined (EXCO_PLL_REF_IN_EN) && (EXCO_PLL_REF_IN_EN == 1u))
    if (CY_SYSCLK_PLL_SRC_IMO == Cy_SysClk_PllGetSource(pllNum))
    {
        freq = Cy_SysClk_ImoGetFrequency();
    }
#if (CY_IP_M0S8EXCO_VERSION == 2U)
    else if (CY_SYSCLK_PLL_SRC_EXTREF == Cy_SysClk_PllGetSource(pllNum))
    {
        freq = Cy_SysClk_ExtRefGetFrequency();
    }
#endif /* (CY_IP_M0S8EXCO_VERSION == 2U) */
    else /* CY_SYSCLK_PLL_SRC_ECO */
    {
        freq = Cy_SysClk_EcoGetFrequency();
    }
#else
        freq = Cy_SysClk_EcoGetFrequency();
#endif /* (defined (EXCO_PLL_REF_IN_EN) && (EXCO_PLL_REF_IN_EN == 1u)) */

    if (!Cy_SysClk_PllIsEnabled(pllNum))
    {
        freq = 0UL; /* The frequency is unknown */
    }
    else
    {
        /* Get the Pll parameters */
        cy_stc_sysclk_pll_manual_config_t config;
        Cy_SysClk_PllGetConfiguration(pllNum, &config);

        /* Calculate Pll output frequency */
        freq = CY_SYSLIB_DIV_ROUND(freq, 1UL + config.referenceDiv) * config.feedbackDiv;
        freq = CY_SYSLIB_DIV_ROUND(freq, 1UL << config.outputDiv);
    }

    return (freq);
}


/** \} group_sysclk_pll_funcs */
#endif /* EXCO_PLL_PRESENT */
#endif  /* CY_IP_M0S8EXCO */


/* ========================================================================== */
/* =========================    ClkHf SECTION    ========================= */
/* ========================================================================== */

/** \cond */
#define  PLL_FLAG (0x4UL)

#if (defined(CY_IP_M0S8EXCO) && (CY_IP_M0S8EXCO == 1u))
#if (defined(EXCO_PLL_PRESENT) && (EXCO_PLL_PRESENT == 1u))
    #define  CY_SYSCLK_IS_SOURCE_VALID(src) (((src) == CY_SYSCLK_CLKHF_IN_IMO)    || \
                                             ((src) == CY_SYSCLK_CLKHF_IN_EXTCLK) || \
                                             ((src) == CY_SYSCLK_CLKHF_IN_ECO)    || \
                                             ((src) == CY_SYSCLK_CLKHF_IN_PLL))
#else
    #define  CY_SYSCLK_IS_SOURCE_VALID(src) (((src) == CY_SYSCLK_CLKHF_IN_IMO)    || \
                                             ((src) == CY_SYSCLK_CLKHF_IN_EXTCLK) || \
                                             ((src) == CY_SYSCLK_CLKHF_IN_ECO))
#endif /* EXCO_PLL_PRESENT */
#else
    #define  CY_SYSCLK_IS_SOURCE_VALID(src) (((src) == CY_SYSCLK_CLKHF_IN_IMO)    || \
                                             ((src) == CY_SYSCLK_CLKHF_IN_EXTCLK))
#endif /* CY_IP_M0S8EXCO */

/* SRSSLT_CLK_SELECT_HFCLK_SEL values. Used by Cy_SysClk_ClkHfGetSource(). */
#define CY_SYSCLK_HFCLK_SEL_IMO     (0UL)
#define CY_SYSCLK_HFCLK_SEL_EXTCLK  (1UL)
#define CY_SYSCLK_HFCLK_SEL_ECO     (2UL)

/** \endcond */

/**
* \addtogroup group_sysclk_clk_hf_funcs
* \{
*/
/*******************************************************************************
* Function Name: Cy_SysClk_ClkHfSetSource
****************************************************************************//**
*
* Selects the source of the selected ClkHf.
*
* \param source \ref cy_en_sysclk_clkhf_src_t
*
* \note The direct transitions from PLL to ECO and vice-versa are not supported
* due to HW limitations.
* In case of such need, first switch the ClkHf clock source to IMO,
* then disable/enable/bypass PLL using PLL \ref group_sysclk_pll_funcs,
* and then the ClkHf clock source can be switched back to ECO/PLL as desired.\n
* For example:
* \snippet sysclk/sut/sysclk_snippet.c snippet_Cy_SysClk_BypassPllEco
*
* \return  Error / status code \ref cy_en_sysclk_status_t : \n
* CY_SYSCLK_SUCCESS - the source is successfully set \n
* CY_SYSCLK_INVALID_STATE - the selected clock source is not enabled,
* or in case of ECO->PLL or PLL->ECO transitions \n
* CY_SYSCLK_BAD_PARAM - the source parameter is invalid.
*
* \note Call \ref SystemCoreClockUpdate after this function calling if
* ClkSys frequency is affected.
*
* \note Call \ref Cy_SysLib_SetWaitStates before this function calling if
* ClkSys frequency is increasing.
*
* \note Call \ref Cy_SysLib_SetWaitStates after this function calling if
* ClkSys frequency is decreasing.
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_EcoDisable
*
*******************************************************************************/
cy_en_sysclk_status_t Cy_SysClk_ClkHfSetSource(cy_en_sysclk_clkhf_src_t source)
{
    cy_en_sysclk_status_t retVal = CY_SYSCLK_SUCCESS;

    if (CY_SYSCLK_IS_SOURCE_VALID(source))
    {
        cy_en_sysclk_clkhf_src_t prevSrc = Cy_SysClk_ClkHfGetSource();

        if (source != prevSrc)
        {
            if (((CY_SYSCLK_CLKHF_IN_IMO == source) && (Cy_SysClk_ImoIsEnabled()))
            #if (defined(CY_IP_M0S8EXCO) && (CY_IP_M0S8EXCO == 1u))
            #if (defined(EXCO_PLL_PRESENT) && (EXCO_PLL_PRESENT == 1u))
                ||  ((CY_SYSCLK_CLKHF_IN_PLL == source) &&   Cy_SysClk_PllIsEnabled(0UL)) /* Currently only one PLL is supported */
                ||  ((CY_SYSCLK_CLKHF_IN_ECO == source) && (0UL != Cy_SysClk_EcoGetFrequency())
                                                        && (!Cy_SysClk_PllIsEnabled(0UL) || (CY_SYSCLK_PLL_OUTPUT_INPUT == Cy_SysClk_PllGetBypassState(0UL))))
            #else /* PLL is not present */
                ||  ((CY_SYSCLK_CLKHF_IN_ECO == source) && (0UL != Cy_SysClk_EcoGetFrequency()))
            #endif /* EXCO_PLL_PRESENT */
            #endif /* CY_IP_M0S8EXCO */
                ||  ((CY_SYSCLK_CLKHF_IN_EXTCLK == source) && (0UL != Cy_SysClk_ExtClkGetFrequency())))
            {
            #if (defined(CY_IP_M0S8EXCO) && (CY_IP_M0S8EXCO == 1u))
            #if (defined(EXCO_PLL_PRESENT) && (EXCO_PLL_PRESENT == 1u))
                if ((CY_SYSCLK_CLKHF_IN_ECO == source) || (CY_SYSCLK_CLKHF_IN_PLL == source))
                {
                    CY_REG32_CLR_SET(EXCO_CLK_SELECT, EXCO_CLK_SELECT_CLK_SELECT, (0UL != (PLL_FLAG & (uint32_t) source)) ? 1UL : 0UL);
                    Cy_SysClk_EcoSeqGen();
                }
            #endif /* EXCO_PLL_PRESENT */
            #endif /* CY_IP_M0S8EXCO */

                CY_REG32_CLR_SET(SRSSLT_CLK_SELECT, SRSSLT_CLK_SELECT_HFCLK_SEL, source);
            }
            else
            {
                retVal = CY_SYSCLK_INVALID_STATE;
            }
        }
    }
    else
    {
        retVal = CY_SYSCLK_BAD_PARAM;
    }

    return (retVal);
}


/*******************************************************************************
* Function Name: Cy_SysClk_ClkHfGetSource
****************************************************************************//**
*
* Reports the source of the ClkHf.
*
* \return \ref cy_en_sysclk_clkhf_src_t
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_EcoDisable
*
*******************************************************************************/
cy_en_sysclk_clkhf_src_t Cy_SysClk_ClkHfGetSource(void)
{
    cy_en_sysclk_clkhf_src_t retVal;
    uint32_t regVal = _FLD2VAL(SRSSLT_CLK_SELECT_HFCLK_SEL, SRSSLT_CLK_SELECT);

    switch(regVal)
    {
        case CY_SYSCLK_HFCLK_SEL_IMO:
             retVal = CY_SYSCLK_CLKHF_IN_IMO;
             break;
        case CY_SYSCLK_HFCLK_SEL_EXTCLK:
             retVal = CY_SYSCLK_CLKHF_IN_EXTCLK;
             break;
    #if defined (CY_IP_M0S8EXCO)
        case CY_SYSCLK_HFCLK_SEL_ECO:
            retVal = CY_SYSCLK_CLKHF_IN_ECO;
        #if (defined(EXCO_PLL_PRESENT) && (EXCO_PLL_PRESENT == 1UL))
            if (0UL != (EXCO_CLK_SELECT & EXCO_CLK_SELECT_CLK_SELECT_Msk))
            {
                retVal = CY_SYSCLK_CLKHF_IN_PLL;
            }
        #endif /* (defined(EXCO_PLL_PRESENT) && (EXCO_PLL_PRESENT == 1UL)) */
            break;
    #endif /* CY_IP_M0S8EXCO */
        default:
            /* Should never get here */
            retVal = CY_SYSCLK_CLKHF_IN_IMO;
            break;
    }

    return (retVal);
}


/*******************************************************************************
* Function Name: Cy_SysClk_ClkHfGetFrequency
****************************************************************************//**
*
* Reports the frequency of the ClkHf
*
* \return The frequency, in Hz.
*
* \note
* The reported value may be zero, which indicates the frequency is unknown.
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_ClkHfSetDivider
*
*******************************************************************************/
uint32_t Cy_SysClk_ClkHfGetFrequency(void)
{
    uint32_t freq = 0UL;    /* ClkHf source clock frequency, in Hz, 0 = unknown frequency */
    /* Convert the cy_en_clkhf_dividers_t value into the natural number of divider */
    uint32_t div = (uint32_t) (1UL << (uint32_t)Cy_SysClk_ClkHfGetDivider());
    cy_en_sysclk_clkhf_src_t source = Cy_SysClk_ClkHfGetSource(); /* source input for ClkHf */

    /* get the frequency of the source, i.e., the path mux input */
    switch(source)
    {
        case CY_SYSCLK_CLKHF_IN_IMO:
            freq = Cy_SysClk_ImoGetFrequency();
            break;

        case CY_SYSCLK_CLKHF_IN_EXTCLK:
            freq = Cy_SysClk_ExtClkGetFrequency();
            break;

    #if (defined(CY_IP_M0S8EXCO) && (CY_IP_M0S8EXCO == 1u))
        case CY_SYSCLK_CLKHF_IN_ECO:
        {
            bool pllEnabled = Cy_SysClk_PllIsEnabled(0U);
            bool pllLocked = Cy_SysClk_PllIsLocked(0U);
            cy_en_sysclk_pll_bypass_t mode = Cy_SysClk_PllGetBypassState(0U);
            bool pllBypassAutos = (mode == CY_SYSCLK_PLL_OUTPUT_AUTO) || (mode == CY_SYSCLK_PLL_OUTPUT_AUTO1);
            bool pllBypassOutput = (mode == CY_SYSCLK_PLL_OUTPUT_OUTPUT);

            if (pllEnabled && ((pllLocked && pllBypassAutos) || pllBypassOutput))
            {
                freq = Cy_SysClk_PllGetFrequency(0UL);
            }
            else /* Pll is disabled, unlocked or bypassed */
            {
                freq = Cy_SysClk_EcoGetFrequency();
            }
        }
            break;

    #if (defined(EXCO_PLL_PRESENT) && (EXCO_PLL_PRESENT == 1u))
        case CY_SYSCLK_CLKHF_IN_PLL:
            freq = Cy_SysClk_PllGetFrequency(0UL);
            break;

    #endif /* EXCO_PLL_PRESENT */
    #endif /* CY_IP_M0S8EXCO */
        default:
            /* Unsupported clock source, return 0 */
            break;
    }

    /* Divide the path input frequency down and return the result */
    return (CY_SYSLIB_DIV_ROUND(freq, div));
}

/** \} group_sysclk_clk_hf_funcs */


/* ========================================================================== */
/* =====================    clk_peripherals SECTION    ====================== */
/* ========================================================================== */

/** \cond */
#if (0U != PERI_PCLK_DIV_8_NR)
#define IS_DIV_8_TYPE_NUM_VALID(typ, num)    (((typ) == CY_SYSCLK_DIV_8_BIT)    && ((num) < PERI_PCLK_DIV_8_NR))
#else
#define IS_DIV_8_TYPE_NUM_VALID(typ, num)    (0U != 0U)
#endif

#if (0U != PERI_PCLK_DIV_16_NR)
#define IS_DIV_16_TYPE_NUM_VALID(typ, num)   (((typ) == CY_SYSCLK_DIV_16_BIT)   && ((num) < PERI_PCLK_DIV_16_NR))
#else
#define IS_DIV_16_TYPE_NUM_VALID(typ, num)   (0U != 0U)
#endif

#if (0U != PERI_PCLK_DIV_16_5_NR)
#define IS_DIV_16_5_TYPE_NUM_VALID(typ, num) (((typ) == CY_SYSCLK_DIV_16_5_BIT) && ((num) < PERI_PCLK_DIV_16_5_NR))
#else
#define IS_DIV_16_5_TYPE_NUM_VALID(typ, num) (0U != 0U)
#endif

#if (0U != PERI_PCLK_DIV_24_5_NR)
#define IS_DIV_24_5_TYPE_NUM_VALID(typ, num) (((typ) == CY_SYSCLK_DIV_24_5_BIT) && ((num) < PERI_PCLK_DIV_24_5_NR))
#else
#define IS_DIV_24_5_TYPE_NUM_VALID(typ, num) (0U != 0U)
#endif

#define IS_DIV_INT_TYPE_NUM_VALID(typ, num)  (IS_DIV_8_TYPE_NUM_VALID((typ), (num)) || \
                                              IS_DIV_16_TYPE_NUM_VALID((typ), (num)))

#define IS_DIV_FRC_TYPE_NUM_VALID(typ, num)  (IS_DIV_16_5_TYPE_NUM_VALID((typ), (num)) || \
                                              IS_DIV_24_5_TYPE_NUM_VALID((typ), (num)))

#define IS_DIV_TYPE_NUM_VALID(typ, num)      (IS_DIV_INT_TYPE_NUM_VALID((typ), (num)) || \
                                              IS_DIV_FRC_TYPE_NUM_VALID((typ), (num)))

#define IS_DIV_PA_TYPE_NUM_VALID(typ, num)   (IS_DIV_TYPE_NUM_VALID((typ), (num)) || \
                                              (((typ) == CY_SYSCLK_DIV_24_5_BIT) && ((num) == 63UL)))
/** \endcond */

/**
* \addtogroup group_sysclk_clk_peripheral_funcs
* \{
*/


/*******************************************************************************
* Function Name: Cy_SysClk_PeriphSetDivider
****************************************************************************//**
*
* Sets one of the programmable clock dividers. This is only used for integer
* dividers. Use \ref Cy_SysClk_PeriphSetFracDivider for setting factional dividers.
*
* \pre If the specified clock divider is already enabled - it should be disabled
* prior to use this function by \ref Cy_SysClk_PeriphDisableDivider.
*
* \param dividerType specifies which type of divider to use; \ref cy_en_sysclk_divider_types_t
*
* \param dividerNum the divider number.
*
* \param dividerValue divider value
* Causes integer division of (divider value + 1), or division by 1 to 256
* (8-bit divider) or 1 to 65536 (16-bit divider).
*
* \return \ref cy_en_sysclk_status_t
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_PeriphSetDivider
*
*******************************************************************************/
cy_en_sysclk_status_t Cy_SysClk_PeriphSetDivider(cy_en_sysclk_divider_types_t dividerType,
                                                                     uint32_t dividerNum,
                                                                     uint32_t dividerValue)
{
    cy_en_sysclk_status_t retVal = CY_SYSCLK_BAD_PARAM;
#if (0UL != PERI_PCLK_DIV_8_NR)
    if (IS_DIV_8_TYPE_NUM_VALID(dividerType, dividerNum) &&
        (dividerValue <= (PERI_DIV_8_CTL_INT8_DIV_Msk >> PERI_DIV_8_CTL_INT8_DIV_Pos)))
    {
        CY_REG32_CLR_SET(PERI_DIV_8_CTL[dividerNum], PERI_DIV_8_CTL_INT8_DIV, dividerValue);
        retVal = CY_SYSCLK_SUCCESS;
    }
    else
#endif /* PERI_PCLK_DIV_8_NR */
#if (0UL != PERI_PCLK_DIV_16_NR)
    if (IS_DIV_16_TYPE_NUM_VALID(dividerType, dividerNum) &&
        (dividerValue <= (PERI_DIV_16_CTL_INT16_DIV_Msk >> PERI_DIV_16_CTL_INT16_DIV_Pos)))
    {
        CY_REG32_CLR_SET(PERI_DIV_16_CTL[dividerNum], PERI_DIV_16_CTL_INT16_DIV, dividerValue);
        retVal = CY_SYSCLK_SUCCESS;
    }
    else
#endif /* PERI_PCLK_DIV_16_NR */
    {
        /* return bad parameter */
    }
    return (retVal);
}

/*******************************************************************************
* Function Name: Cy_SysClk_PeriphGetDivider
****************************************************************************//**
*
* Returns the integer divider value for the specified divider. One works for
* integer dividers. Use \ref Cy_SysClk_PeriphGetFracDivider to get the fractional
* divider value
*
* \param dividerType specifies which type of divider to use; \ref cy_en_sysclk_divider_types_t
*
* \param dividerNum specifies which divider of the selected type to configure
*
* \return The divider value.
* The integer division done is by (divider value + 1), or division by 1 to 256
* (8-bit divider) or 1 to 65536 (16-bit divider).
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_PeriphSetDivider
*
*******************************************************************************/
uint32_t Cy_SysClk_PeriphGetDivider(cy_en_sysclk_divider_types_t dividerType, uint32_t dividerNum)
{
    uint32_t retVal = 0UL;

    CY_ASSERT_L1(IS_DIV_INT_TYPE_NUM_VALID(dividerType, dividerNum));

#if (0UL != PERI_PCLK_DIV_8_NR)
    if (IS_DIV_8_TYPE_NUM_VALID(dividerType, dividerNum))
    {
        retVal = _FLD2VAL(PERI_DIV_8_CTL_INT8_DIV, PERI_DIV_8_CTL[dividerNum]);
    }
    else
#endif /* PERI_PCLK_DIV_8_NR */
#if (0UL != PERI_PCLK_DIV_16_NR)
    if (IS_DIV_16_TYPE_NUM_VALID(dividerType, dividerNum))
    {
        retVal = _FLD2VAL(PERI_DIV_16_CTL_INT16_DIV, PERI_DIV_16_CTL[dividerNum]);
    }
    else
#endif /* PERI_PCLK_DIV_16_NR */
    {
        /* return zero divider */
    }
    return (retVal);
}


/*******************************************************************************
* Function Name: Cy_SysClk_PeriphSetFracDivider
****************************************************************************//**
*
* Sets one of the programmable clock dividers. This function should only be used
* for fractional clock dividers.
*
* \pre If the specified clock divider is already enabled - it should be disabled
* prior to use this function by \ref Cy_SysClk_PeriphDisableDivider.
*
* \param dividerType specifies which type of divider to use; \ref cy_en_sysclk_divider_types_t
*
* \param dividerNum specifies which divider of the selected type to configure
*
* \param dividerIntValue the integer divider value
* The source of the divider is peri_clk, which is a divided version of hf_clk[0].
* The divider value causes integer division of (divider value + 1), or division
* by 1 to 65536 (16-bit divider) or 1 to 16777216 (24-bit divider).
*
* \param dividerFracValue the fraction part of the divider
* The fractional divider can be 1-32, thus it divides the clock by 1/32 for each
* count. To divide the clock by 11/32nds set this value to 11.
*
* \return \ref cy_en_sysclk_status_t
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_PeriphSetFracDivider
*
*******************************************************************************/
cy_en_sysclk_status_t Cy_SysClk_PeriphSetFracDivider(cy_en_sysclk_divider_types_t dividerType,
                                                                         uint32_t dividerNum,
                                                                         uint32_t dividerIntValue,
                                                                         uint32_t dividerFracValue)
{
    cy_en_sysclk_status_t retVal = CY_SYSCLK_BAD_PARAM;

#if (0UL != PERI_PCLK_DIV_16_5_NR)
    if (IS_DIV_16_5_TYPE_NUM_VALID(dividerType, dividerNum) &&
        (dividerIntValue <= (PERI_DIV_16_5_CTL_INT16_DIV_Msk >> PERI_DIV_16_5_CTL_INT16_DIV_Pos)) &&
        (dividerFracValue <= (PERI_DIV_16_5_CTL_FRAC5_DIV_Msk >> PERI_DIV_16_5_CTL_FRAC5_DIV_Pos)))
    {
        CY_REG32_CLR_SET(PERI_DIV_16_5_CTL[dividerNum], PERI_DIV_16_5_CTL_INT16_DIV, dividerIntValue);
        CY_REG32_CLR_SET(PERI_DIV_16_5_CTL[dividerNum], PERI_DIV_16_5_CTL_FRAC5_DIV, dividerFracValue);
        retVal = CY_SYSCLK_SUCCESS;
    }
    else
#endif /* PERI_PCLK_DIV_16_5_NR */
#if (0UL != PERI_PCLK_DIV_24_5_NR)
    if (IS_DIV_24_5_TYPE_NUM_VALID(dividerType, dividerNum) &&
        (dividerIntValue <= (PERI_DIV_24_5_CTL_INT24_DIV_Msk >> PERI_DIV_24_5_CTL_INT24_DIV_Pos)) &&
        (dividerFracValue <= (PERI_DIV_24_5_CTL_FRAC5_DIV_Msk >> PERI_DIV_24_5_CTL_FRAC5_DIV_Pos)))
    {
        CY_REG32_CLR_SET(PERI_DIV_24_5_CTL[dividerNum], PERI_DIV_24_5_CTL_INT24_DIV, dividerIntValue);
        CY_REG32_CLR_SET(PERI_DIV_24_5_CTL[dividerNum], PERI_DIV_24_5_CTL_FRAC5_DIV, dividerFracValue);
        retVal = CY_SYSCLK_SUCCESS;
    }
    else
#endif /* PERI_PCLK_DIV_24_5_NR */
    {
        /* return bad parameter */
    }
    return (retVal);
}


/*******************************************************************************
* Function Name: Cy_SysClk_PeriphGetFracDivider
****************************************************************************//**
*
* Reports the integer and fractional parts of the divider
*
* \param dividerType specifies which type of divider to use; \ref cy_en_sysclk_divider_types_t
*
* \param dividerNum specifies which divider of the selected type to configure
*
* \param *dividerIntValue pointer to return integer divider value
*
* \param *dividerFracValue pointer to return fractional divider value
*
* \return None. Loads pointed-to variables.
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_PeriphSetFracDivider
*
*******************************************************************************/
void Cy_SysClk_PeriphGetFracDivider(cy_en_sysclk_divider_types_t   dividerType,
                                                        uint32_t   dividerNum,
                                                        uint32_t * dividerIntValue,
                                                        uint32_t * dividerFracValue)
{
    CY_ASSERT_L1(IS_DIV_FRC_TYPE_NUM_VALID(dividerType, dividerNum));
    CY_ASSERT_L1(NULL != dividerIntValue);
    CY_ASSERT_L1(NULL != dividerFracValue);

#if (0UL != PERI_PCLK_DIV_16_5_NR)
    if (IS_DIV_16_5_TYPE_NUM_VALID(dividerType, dividerNum))
    {
        *dividerIntValue  = _FLD2VAL(PERI_DIV_16_5_CTL_INT16_DIV, PERI_DIV_16_5_CTL[dividerNum]);
        *dividerFracValue = _FLD2VAL(PERI_DIV_16_5_CTL_FRAC5_DIV, PERI_DIV_16_5_CTL[dividerNum]);
    }
    else
#endif /* PERI_PCLK_DIV_16_5_NR */
#if (0UL != PERI_PCLK_DIV_24_5_NR)
    if (IS_DIV_24_5_TYPE_NUM_VALID(dividerType, dividerNum))
    {
        *dividerIntValue  = _FLD2VAL(PERI_DIV_24_5_CTL_INT24_DIV, PERI_DIV_24_5_CTL[dividerNum]);
        *dividerFracValue = _FLD2VAL(PERI_DIV_24_5_CTL_FRAC5_DIV, PERI_DIV_24_5_CTL[dividerNum]);
    }
    else
#endif /* PERI_PCLK_DIV_24_5_NR */
    {
        *dividerIntValue  = 0UL;
        *dividerFracValue = 0UL;
    }
}


/*******************************************************************************
* Function Name: Cy_SysClk_PeriphGetFrequency
****************************************************************************//**
*
* Reports the frequency of the output of a given peripheral divider.
*
* \param dividerType specifies which type of divider to use; \ref cy_en_sysclk_divider_types_t
*
* \param dividerNum specifies which divider of the selected type to configure
*
* \return The frequency, in Hz.
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_PeriphGetFrequency
*
*******************************************************************************/
uint32_t Cy_SysClk_PeriphGetFrequency(cy_en_sysclk_divider_types_t dividerType, uint32_t dividerNum)
{
    uint32_t integer = 0UL;        /* Integer part of peripheral divider */
    uint32_t freq = Cy_SysClk_ClkHfGetFrequency(); /* Get ClkHf frequency */

    CY_ASSERT_L1(IS_DIV_TYPE_NUM_VALID(dividerType, dividerNum));

    /* get the divider value for clk_peri to the selected peripheral clock */
    switch(dividerType)
    {
    #if (0UL != PERI_PCLK_DIV_8_NR)
        case CY_SYSCLK_DIV_8_BIT:
    #endif /* PERI_PCLK_DIV_8_NR */
    #if (0UL != PERI_PCLK_DIV_16_NR)
        case CY_SYSCLK_DIV_16_BIT:
    #endif /* PERI_PCLK_DIV_16_NR */
    #if ((0UL != PERI_PCLK_DIV_8_NR) || (0UL != PERI_PCLK_DIV_16_NR))
            integer = 1UL + Cy_SysClk_PeriphGetDivider(dividerType, dividerNum);
            freq = CY_SYSLIB_DIV_ROUND(freq, integer);
            break;
    #endif /* PERI_PCLK_DIV_8_NR or PERI_PCLK_DIV_16_NR */
    #if (0UL != PERI_PCLK_DIV_16_5_NR)
        case CY_SYSCLK_DIV_16_5_BIT:
    #endif /* PERI_PCLK_DIV_16_5_NR */
    #if (0UL != PERI_PCLK_DIV_24_5_NR)
        case CY_SYSCLK_DIV_24_5_BIT:
    #endif /* PERI_PCLK_DIV_24_5_NR */
    #if ((0UL != PERI_PCLK_DIV_16_5_NR) || (0UL != PERI_PCLK_DIV_24_5_NR))
            {
                uint32_t locFrac;
                uint32_t locDiv;
                uint32_t locFreq = freq * 32UL;
                Cy_SysClk_PeriphGetFracDivider(dividerType, dividerNum, &integer, &locFrac);
                /* For fractional dividers, the divider is (int + 1) + frac/32 */
                locDiv = ((1UL + integer) * 32UL) + locFrac;
                freq = CY_SYSLIB_DIV_ROUND(locFreq, locDiv);
            }
            break;
    #endif /* CY_SYSCLK_DIV_16_5_BIT or CY_SYSCLK_DIV_24_5_BIT */

        default:
            /* Invalid divider type */
            break;
    }

    return (freq);
}


/*******************************************************************************
* Function Name: Cy_SysClk_PeriphAssignDivider
****************************************************************************//**
*
* Assigns a programmable divider to a selected IP block, such as a TCPWM or SCB.
*
* \param periphNum specifies the peripheral block \ref en_clk_dst_t.
*
* \param dividerType specifies which type of divider to use; \ref cy_en_sysclk_divider_types_t
*
* \param dividerNum specifies which divider of the selected type to configure
*
* \return \ref cy_en_sysclk_status_t
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_PeriphAssignDivider
*
*******************************************************************************/
cy_en_sysclk_status_t Cy_SysClk_PeriphAssignDivider(en_clk_dst_t periphNum, cy_en_sysclk_divider_types_t dividerType, uint32_t dividerNum)
{
    cy_en_sysclk_status_t retVal = CY_SYSCLK_BAD_PARAM;
    if ((PERI_PCLK_CLOCK_NR > (uint32_t)periphNum) && IS_DIV_TYPE_NUM_VALID(dividerType, dividerNum))
    {
        PERI_PCLK_CTL[periphNum] = _VAL2FLD(PERI_PCLK_CTL_SEL_TYPE, dividerType) |
                                   _VAL2FLD(PERI_PCLK_CTL_SEL_DIV,  dividerNum);
        retVal = CY_SYSCLK_SUCCESS;
    }
    return (retVal);
}


/*******************************************************************************
* Function Name: Cy_SysClk_PeriphEnableDivider
****************************************************************************//**
*
* Enables the selected divider.
*
* \param dividerType specifies which type of divider to use; \ref cy_en_sysclk_divider_types_t
*
* \param dividerNum specifies which divider of the selected type to configure
*
* \note This function also sets the phase alignment bits such that the enabled
* divider is aligned to clk_peri. See \ref Cy_SysClk_PeriphDisableDivider()
* for information on how to phase-align a divider after it is enabled.
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_PeriphEnableDivider
*
*******************************************************************************/
cy_en_sysclk_status_t Cy_SysClk_PeriphEnableDivider(cy_en_sysclk_divider_types_t dividerType, uint32_t dividerNum)
{
    cy_en_sysclk_status_t retVal = CY_SYSCLK_BAD_PARAM;

    if (IS_DIV_TYPE_NUM_VALID(dividerType, dividerNum))
    {
        /* specify the divider, make the reference = clk_peri, and enable the divider */
        PERI_DIV_CMD = PERI_DIV_CMD_ENABLE_Msk             |
                       PERI_DIV_CMD_PA_SEL_TYPE_Msk        |
                       PERI_DIV_CMD_PA_SEL_DIV_Msk         |
              _VAL2FLD(PERI_DIV_CMD_SEL_TYPE, dividerType) |
              _VAL2FLD(PERI_DIV_CMD_SEL_DIV,  dividerNum);
        (void)PERI_DIV_CMD; /* dummy read to handle buffered writes */
        retVal = CY_SYSCLK_SUCCESS;
    }

    return (retVal);
}


/*******************************************************************************
* Function Name: Cy_SysClk_PeriphDisableDivider
****************************************************************************//**
*
* Disables a selected divider.
*
* \param dividerType specifies which type of divider to use; \ref cy_en_sysclk_divider_types_t.
*
* \param dividerNum specifies which divider of the selected type to configure.
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_PeriphDisableDivider
*
*******************************************************************************/
cy_en_sysclk_status_t Cy_SysClk_PeriphDisableDivider(cy_en_sysclk_divider_types_t dividerType, uint32_t dividerNum)
{
    cy_en_sysclk_status_t retVal = CY_SYSCLK_BAD_PARAM;

    if (IS_DIV_TYPE_NUM_VALID(dividerType, dividerNum))
    {
        /* specify the divider and disable it */
        PERI_DIV_CMD = PERI_DIV_CMD_DISABLE_Msk            |
              _VAL2FLD(PERI_DIV_CMD_SEL_TYPE, dividerType) |
              _VAL2FLD(PERI_DIV_CMD_SEL_DIV,  dividerNum);
        retVal = CY_SYSCLK_SUCCESS;
    }

    return (retVal);
}


/*******************************************************************************
* Function Name: Cy_SysClk_PeriphDividerIsEnabled
****************************************************************************//**
*
* Reports the enabled/disabled state of the selected divider.
*
* \param dividerType specifies which type of divider to use; \ref cy_en_sysclk_divider_types_t.
*
* \param dividerNum specifies which divider of the selected type to configure.
*
* \return The enabled/disabled state; \n
* false = disabled \n
* true = enabled
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_PeriphGetDividerEnabled
*
*******************************************************************************/
bool Cy_SysClk_PeriphDividerIsEnabled(cy_en_sysclk_divider_types_t dividerType, uint32_t dividerNum)
{
    bool retVal = false;

    CY_ASSERT_L1(IS_DIV_TYPE_NUM_VALID(dividerType, dividerNum));

    switch(dividerType)
    {
        #if (0UL != PERI_PCLK_DIV_8_NR)
            case CY_SYSCLK_DIV_8_BIT:
                retVal = _FLD2BOOL(PERI_DIV_8_CTL_EN, PERI_DIV_8_CTL[dividerNum]);
                break;
        #endif /* PERI_PCLK_DIV_8_NR */
        #if (0UL != PERI_PCLK_DIV_16_NR)
            case CY_SYSCLK_DIV_16_BIT:
                retVal = _FLD2BOOL(PERI_DIV_16_CTL_EN, PERI_DIV_16_CTL[dividerNum]);
                break;
        #endif /* PERI_PCLK_DIV_16_NR */
        #if (0UL != PERI_PCLK_DIV_16_5_NR)
            case CY_SYSCLK_DIV_16_5_BIT:
                retVal = _FLD2BOOL(PERI_DIV_16_5_CTL_EN, PERI_DIV_16_5_CTL[dividerNum]);
                break;
        #endif /* PERI_PCLK_DIV_16_5_NR */
        #if (0UL != PERI_PCLK_DIV_24_5_NR)
            case CY_SYSCLK_DIV_24_5_BIT:
                retVal = _FLD2BOOL(PERI_DIV_24_5_CTL_EN, PERI_DIV_24_5_CTL[dividerNum]);
                break;
        #endif /* PERI_PCLK_DIV_24_5_NR */
            default:
                /* Invalid divider type */
                break;
    }
    return (retVal);
}


/*******************************************************************************
* Function Name: Cy_SysClk_PeriphEnablePhaseAlignDivider
****************************************************************************//**
*
* First disables a selected divider (\ref Cy_SysClk_PeriphDisableDivider),
* then aligns that divider to another programmable divider, and enables the
* selected divider. The divider to align to must already be enabled in order
* to align a divider to it.
*
* \param dividerType specifies which type of divider to use; \ref cy_en_sysclk_divider_types_t.
*
* \param dividerNum specifies which divider of the selected type to configure.
*
* \param dividerTypePA type of divider to phase-align to; \ref cy_en_sysclk_divider_types_t.
*
* \param dividerNumPA divider number of type specified to phase align to.
*
* \note
* To phase-align a divider to clk_peri, set dividerTypePA to 3 and dividerNumPA
* to 63.
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_PeriphEnablePhaseAlignDivider
*
*******************************************************************************/
cy_en_sysclk_status_t Cy_SysClk_PeriphEnablePhaseAlignDivider(cy_en_sysclk_divider_types_t dividerType,
                                                                                  uint32_t dividerNum,
                                                              cy_en_sysclk_divider_types_t dividerTypePA,
                                                                                  uint32_t dividerNumPA)
{
    cy_en_sysclk_status_t retVal = CY_SYSCLK_BAD_PARAM;

    if (IS_DIV_PA_TYPE_NUM_VALID(dividerTypePA, dividerNumPA))
    {
        /* First, disable the divider that is to be phase-aligned.
           The other two parameters are checked in that function;
           if they're not valid, the divider is not disabled. */
        retVal = Cy_SysClk_PeriphDisableDivider(dividerType, dividerNum);
        if (retVal == CY_SYSCLK_SUCCESS)
        {
            /* Then, specify the reference divider, and the divider, and enable the divider */
            PERI_DIV_CMD = PERI_DIV_CMD_ENABLE_Msk             |
                  _VAL2FLD(PERI_DIV_CMD_PA_SEL_TYPE, dividerTypePA) |
                  _VAL2FLD(PERI_DIV_CMD_PA_SEL_DIV,  dividerNumPA)  |
                  _VAL2FLD(PERI_DIV_CMD_SEL_TYPE, dividerType)      |
                  _VAL2FLD(PERI_DIV_CMD_SEL_DIV,  dividerNum);
        }
    }
    return (retVal);
}

/** \} group_sysclk_clk_peripheral_funcs */


/* ========================================================================== */
/* =========================    clk_pump SECTION    ========================= */
/* ========================================================================== */


/*******************************************************************************
* Function Name: Cy_SysClk_ClkPumpSetSource
****************************************************************************//**
*
* Sets the source for the pump clock (clk_pump). The pump clock can be used for
* the analog pumps in the CTBm block.
*
* \param source \ref cy_en_sysclk_clkpump_src_t
*
* \return  Error / status code \ref cy_en_sysclk_status_t : \n
* CY_SYSCLK_SUCCESS - the source is successfully set \n
* CY_SYSCLK_INVALID_STATE - the selected clock source is not enabled \n
* CY_SYSCLK_BAD_PARAM - the source parameter is invalid.
*
* \funcusage
* \snippet sysclk/snippet/main.c snippet_Cy_SysClk_ClkPumpSetSource
*
*******************************************************************************/
cy_en_sysclk_status_t Cy_SysClk_ClkPumpSetSource(cy_en_sysclk_clkpump_src_t source)
{
    cy_en_sysclk_status_t retVal = CY_SYSCLK_SUCCESS;

    if (CY_SYSCLK_IS_PUMP_SRC_VALID(source))
    {
        if (source != Cy_SysClk_ClkPumpGetSource())
        {
            if ((CY_SYSCLK_PUMP_IN_IMO == source) && (!Cy_SysClk_ImoIsEnabled()))
            {
                retVal = CY_SYSCLK_INVALID_STATE;
            }
            else
            {
                CY_REG32_CLR_SET(SRSSLT_CLK_SELECT, SRSSLT_CLK_SELECT_PUMP_SEL, source);
            }
        }
    }
    else
    {
        retVal = CY_SYSCLK_BAD_PARAM;
    }

    return (retVal);
}


/* [] END OF FILE */
