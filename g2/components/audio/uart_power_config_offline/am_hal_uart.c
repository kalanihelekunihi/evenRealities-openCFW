//*****************************************************************************
//
//! @file am_hal_uart.c
//!
//! @brief Hardware abstraction for the UART
//!
//! @addtogroup uart_ap510 UART Functionality
//! @ingroup apollo510_hal
//! @{
//!
//! Purpose: This module provides comprehensive UART (Universal Asynchronous
//!          Receiver/Transmitter) hardware abstraction for Apollo5 devices.
//!          It supports UART configuration, data transfer, interrupt handling,
//!          and DMA operations for serial communication applications.
//!
//! @section hal_uart_features Key Features
//!
//! 1. @b UART @b Configuration: Flexible baud rate and parameter configuration.
//! 2. @b Data @b Transfer: Support for blocking and non-blocking data transfer.
//! 3. @b DMA @b Support: High-speed DMA-based data transfer operations.
//! 4. @b Interrupt @b Handling: Comprehensive interrupt management for UART events.
//! 5. @b FIFO @b Management: Advanced FIFO handling and buffer management.
//!
//! @section hal_uart_functionality Functionality
//!
//! - Initialize and configure UART peripheral
//! - Handle data transfer operations (blocking/non-blocking)
//! - Support DMA-based high-speed transfers
//! - Manage FIFO buffers and data flow
//! - Handle UART interrupts and status monitoring
//!
//! @section hal_uart_usage Usage
//!
//! 1. Initialize UART using am_hal_uart_initialize()
//! 2. Configure UART parameters and baud rate
//! 3. Set up DMA or interrupt handling as needed
//! 4. Perform data transfer operations
//! 5. Handle UART events and status monitoring
//!
//! @section hal_uart_configuration Configuration
//!
//! - @b Baud @b Rate: Configure UART baud rate and timing
//! - @b Data @b Format: Set up data bits, parity, and stop bits
//! - @b DMA @b Settings: Configure DMA transfer parameters
//! - @b Interrupts: Set up interrupt sources and handlers
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

#include "compat.h"

uint32_t
am_hal_uart_power_control(void *pHandle, uint32_t ePowerState,
                          bool bRetainState)
{

#ifndef AM_HAL_DISABLE_API_VALIDATION
    //
    // Check to make sure this is a valid handle.
    //
    if (!AM_HAL_UART_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
#endif
    am_hal_uart_state_t *pState = (am_hal_uart_state_t *) pHandle;
    uint32_t ui32Module = pState->ui32Module;

    am_hal_pwrctrl_periph_e eUARTPowerModule = ((am_hal_pwrctrl_periph_e)
                                                (AM_HAL_PWRCTRL_PERIPH_UART0 +
                                                 ui32Module));
    // Decode the requested power state and update UART operation accordingly.
    //
    switch (ePowerState)
    {
        //
        // Turn on the UART.
        //
        case AM_HAL_SYSCTRL_WAKE:
            //
            // Make sure we don't try to restore an invalid state.
            //
            if (bRetainState && !pState->sRegState.bValid)
            {
                return AM_HAL_STATUS_INVALID_OPERATION;
            }

            //
            // Enable power control.
            //
            am_hal_pwrctrl_periph_enable(eUARTPowerModule);

            if (bRetainState)
            {
                if ( ( pState->ui32BaudRate > 1500000 ) && ( APOLLO5_GE_B1 ) )
                {
                    // Resume D2ASPARE, force uart_gate.clken to be 1, making uart.pclk to be always-on
                    MCUCTRL->D2ASPARE |= (MCUCTRL_D2ASPARE_UART0PLL_Msk << ui32Module);
                }
                am_hal_clkmgr_clock_request(pState->eClkSrc, (am_hal_clkmgr_user_id_e)(AM_HAL_CLKMGR_USER_ID_UART0 + ui32Module));

                //
                // Restore UART registers
                //
                // AM_CRITICAL_BEGIN
                UARTn(ui32Module)->ILPR = pState->sRegState.regILPR;
                UARTn(ui32Module)->IBRD = pState->sRegState.regIBRD;
                UARTn(ui32Module)->FBRD = pState->sRegState.regFBRD;
                UARTn(ui32Module)->LCRH = pState->sRegState.regLCRH;
                UARTn(ui32Module)->CR   = pState->sRegState.regCR;
                UARTn(ui32Module)->IFLS = pState->sRegState.regIFLS;
                UARTn(ui32Module)->IER  = pState->sRegState.regIER;
                UARTn(ui32Module)->DCR  = pState->sRegState.regDMACFG;
                pState->sRegState.bValid = false;

                // AM_CRITICAL_END
            }
            break;

        //
        // Turn off the UART.
        //
        case AM_HAL_SYSCTRL_NORMALSLEEP:
        case AM_HAL_SYSCTRL_DEEPSLEEP:
            if (bRetainState)
            {
                // AM_CRITICAL_BEGIN

                pState->sRegState.regILPR = UARTn(ui32Module)->ILPR;
                pState->sRegState.regIBRD = UARTn(ui32Module)->IBRD;
                pState->sRegState.regFBRD = UARTn(ui32Module)->FBRD;
                pState->sRegState.regLCRH = UARTn(ui32Module)->LCRH;
                pState->sRegState.regCR   = UARTn(ui32Module)->CR;
                pState->sRegState.regIFLS = UARTn(ui32Module)->IFLS;
                pState->sRegState.regIER  = UARTn(ui32Module)->IER;
                pState->sRegState.regDMACFG = UARTn(ui32Module)->DCR;
                pState->sRegState.bValid = true;

                // AM_CRITICAL_END
            }

            if ( ( pState->ui32BaudRate > 1500000 ) && ( APOLLO5_GE_B1 ) )
            {
                // Clear D2ASPARE to save power
                MCUCTRL->D2ASPARE &= ~(MCUCTRL_D2ASPARE_UART0PLL_Msk << ui32Module);
            }
            am_hal_clkmgr_clock_release(pState->eClkSrc, (am_hal_clkmgr_user_id_e)(AM_HAL_CLKMGR_USER_ID_UART0 + ui32Module));

            //
            // Clear all interrupts before sleeping as having a pending UART
            // interrupt burns power.
            //
            am_hal_uart_interrupt_clear(pState, 0xFFFFFFFF);

            //
            // If the user is going to sleep, certain bits of the CR register
            // need to be 0 to be low power and have the UART shut off.
            // Since the user either wishes to retain state which takes place
            // above or the user does not wish to retain state, it is acceptable
            // to set the entire CR register to 0.
            //
            UARTn(ui32Module)->CR = 0;

            //
            // Disable power control.
            //
            am_hal_pwrctrl_periph_disable(eUARTPowerModule);
            break;

        default:
            return AM_HAL_STATUS_INVALID_ARG;
    }

    //
    // Return the status.
    //
    return AM_HAL_STATUS_SUCCESS;
}

uint32_t
am_hal_uart_interrupt_clear(void *pHandle, uint32_t ui32IntMask)
{
    am_hal_uart_state_t *pState = (am_hal_uart_state_t *) pHandle;
    uint32_t ui32Module = pState->ui32Module;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    if (!AM_HAL_UART_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
#endif
    UARTn(ui32Module)->IEC = ui32IntMask;
    *(volatile uint32_t*)(&UARTn(ui32Module)->MIS);
    return AM_HAL_STATUS_SUCCESS;
}

static uint32_t
config_baudrate(uint32_t ui32Module, uint32_t ui32DesiredBaudrate, uint32_t *pui32ActualBaud)
{
    uint32_t ui32UartClkFreq;

    //
    // Check that the baudrate is in range.
    //
    switch ( UARTn(ui32Module)->CR_b.CLKSEL )
    {
        case UART0_CR_CLKSEL_PLL_CLK:
            ui32UartClkFreq = 49152000;
            break;

        case UART0_CR_CLKSEL_HFRC_48MHZ:
            ui32UartClkFreq = 48000000;
            break;

        case UART0_CR_CLKSEL_HFRC_24MHZ:
            ui32UartClkFreq = 24000000;
            break;

        case UART0_CR_CLKSEL_HFRC_12MHZ:
            ui32UartClkFreq = 12000000;
            break;

        case UART0_CR_CLKSEL_HFRC_6MHZ:
            ui32UartClkFreq = 6000000;
            break;

        case UART0_CR_CLKSEL_HFRC_3MHZ:
            ui32UartClkFreq = 3000000;
            break;

        default:
            *pui32ActualBaud = 0;
            return AM_HAL_UART_STATUS_CLOCK_NOT_CONFIGURED;
    }

    //
    // Calculate register values.
    //
    {
        uint32_t ui32BaudClk             = BAUDCLK * ui32DesiredBaudrate;
        uint32_t ui32IntegerDivisor      = (ui32UartClkFreq / ui32BaudClk);
        uint64_t ui64IntermediateLong    = ((uint64_t) ui32UartClkFreq * 64) / ui32BaudClk; // Q58.6
        uint64_t ui64FractionDivisorLong = ui64IntermediateLong - ((uint64_t) ui32IntegerDivisor * 64); // Q58.6
        uint32_t ui32FractionDivisor     = (uint32_t) ui64FractionDivisorLong;

        //
        // Check the result.
        //
        if (ui32IntegerDivisor == 0)
        {
            *pui32ActualBaud = 0;
            return AM_HAL_UART_STATUS_BAUDRATE_NOT_POSSIBLE;
        }

        //
        // Write the UART regs.
        //
        UARTn(ui32Module)->IBRD = ui32IntegerDivisor;
        UARTn(ui32Module)->FBRD = ui32FractionDivisor;

        //
        // Return the actual baud rate.
        //
        *pui32ActualBaud = (ui32UartClkFreq / ((BAUDCLK * ui32IntegerDivisor) + ui32FractionDivisor / 4));
    }
    return AM_HAL_STATUS_SUCCESS;
}

uint32_t
am_hal_uart_configure(void *pHandle, const am_hal_uart_config_t *psConfig)
{

#ifndef AM_HAL_DISABLE_API_VALIDATION
    //
    // Check to make sure this is a valid handle.
    //
    if (!AM_HAL_UART_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
#endif
    am_hal_uart_state_t *pState = (am_hal_uart_state_t *) pHandle;
    uint32_t ui32Module = pState->ui32Module;

    //
    // Reset the CR register to a known value.
    //
    UARTn(ui32Module)->CR = 0;

    //
    // Start by enabling the clocks, which needs to happen in a critical
    // section.
    //
    UARTn(ui32Module)->CR_b.CLKEN = 1;

    // B0 does not support SYSPLL
    if ( ( psConfig->eClockSrc > AM_HAL_UART_CLOCK_SRC_SYSPLL ) ||
         (( psConfig->eClockSrc == AM_HAL_UART_CLOCK_SRC_SYSPLL ) && ( APOLLO5_B0 )) )
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }
    pState->eClkSrc = (psConfig->eClockSrc == AM_HAL_UART_CLOCK_SRC_HFRC) ? AM_HAL_CLKMGR_CLK_ID_HFRC : AM_HAL_CLKMGR_CLK_ID_SYSPLL;
    if ( psConfig->ui32BaudRate > 1500000 )
    {
        if ( APOLLO5_GE_B1 )
        {
            // Set D2ASPARE, force uart_gate.clken to be 1, making uart.pclk to be always-on
            MCUCTRL->D2ASPARE |= (MCUCTRL_D2ASPARE_UART0PLL_Msk << ui32Module);
        }
        UARTn(ui32Module)->CR_b.CLKSEL = (pState->eClkSrc == AM_HAL_CLKMGR_CLK_ID_SYSPLL) ? UART0_CR_CLKSEL_PLL_CLK : UART0_CR_CLKSEL_HFRC_48MHZ;
    }
    else
    {
        if ( APOLLO5_GE_B1 )
        {
            // Clear D2ASPARE to save power
            MCUCTRL->D2ASPARE &= ~(MCUCTRL_D2ASPARE_UART0PLL_Msk << ui32Module);
        }
        UARTn(ui32Module)->CR_b.CLKSEL = (pState->eClkSrc == AM_HAL_CLKMGR_CLK_ID_SYSPLL) ? UART0_CR_CLKSEL_PLL_CLK : UART0_CR_CLKSEL_HFRC_24MHZ;
    }
    am_hal_clkmgr_clock_request(pState->eClkSrc, (am_hal_clkmgr_user_id_e)(AM_HAL_CLKMGR_USER_ID_UART0 + ui32Module));

    //
    // Disable the UART.
    //
    // AM_CRITICAL_BEGIN
    UARTn(ui32Module)->CR_b.UARTEN = 0;
    UARTn(ui32Module)->CR_b.RXE    = 0;
    UARTn(ui32Module)->CR_b.TXE    = 0;
    // AM_CRITICAL_END

    //
    // Set the baud rate.
    //
    uint32_t ui32ErrorStatus = config_baudrate(ui32Module,
                                      psConfig->ui32BaudRate,
                                      &(pState->ui32BaudRate));

    if (ui32ErrorStatus != AM_HAL_STATUS_SUCCESS)
    {
        return ui32ErrorStatus;
    }

    //
    // Set the flow control options
    //
    // AM_CRITICAL_BEGIN
    UARTn(ui32Module)->CR_b.RTSEN = 0;
    UARTn(ui32Module)->CR_b.CTSEN = 0;
    UARTn(ui32Module)->CR |= psConfig->eFlowControl;
    // AM_CRITICAL_END

    //
    // Calculate the parity options.
    //
    uint32_t ui32ParityEnable = 0;
    uint32_t ui32EvenParity = 0;

    switch (psConfig->eParity)
    {
        case AM_HAL_UART_PARITY_ODD:
            ui32ParityEnable = 1;
            ui32EvenParity = 0;
            break;

        case AM_HAL_UART_PARITY_EVEN:
            ui32ParityEnable = 1;
            ui32EvenParity = 1;
            break;

        case AM_HAL_UART_PARITY_NONE:
            ui32ParityEnable = 0;
            ui32EvenParity = 0;
            break;
    }

    //
    // Set the data format.
    //
    // AM_CRITICAL_BEGIN
    UARTn(ui32Module)->LCRH_b.BRK  = 0;
    UARTn(ui32Module)->LCRH_b.PEN  = ui32ParityEnable;
    UARTn(ui32Module)->LCRH_b.EPS  = ui32EvenParity;
    UARTn(ui32Module)->LCRH_b.STP2 = psConfig->eStopBits;
    UARTn(ui32Module)->LCRH_b.FEN  = 1;
    UARTn(ui32Module)->LCRH_b.WLEN = psConfig->eDataBits;
    UARTn(ui32Module)->LCRH_b.SPS  = 0;
    // AM_CRITICAL_END

    //
    // Set the FIFO levels.
    //
    // AM_CRITICAL_BEGIN
    UARTn(ui32Module)->IFLS_b.TXIFLSEL = psConfig->eTXFifoLevel;
    UARTn(ui32Module)->IFLS_b.RXIFLSEL = psConfig->eRXFifoLevel;
    // AM_CRITICAL_END

    //
    // Enable the UART, RX, and TX.
    //
    // AM_CRITICAL_BEGIN
    UARTn(ui32Module)->CR_b.UARTEN = 1;
    UARTn(ui32Module)->CR_b.RXE = 1;
    UARTn(ui32Module)->CR_b.TXE = 1;
    // AM_CRITICAL_END

    return AM_HAL_STATUS_SUCCESS;
}
