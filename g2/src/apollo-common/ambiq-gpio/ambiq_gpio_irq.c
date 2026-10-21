//*****************************************************************************
//
//! @file am_hal_gpio.c
//!
//! @brief General Purpose Input Output Functionality
//!
//! @addtogroup gpio_ap510 GPIO - General Purpose Input Output
//! @ingroup apollo510_hal
//! @{
//!
//! Purpose: This module provides a comprehensive hardware abstraction layer for
//! General Purpose Input/Output (GPIO) pins on Apollo5 devices. It enables pin
//! configuration, state reading/writing, interrupt handling, and various GPIO
//! modes for flexible digital I/O control.
//!
//! @section hal_gpio_features Key Features
//!
//! 1. @b Pin @b Configuration: Configure pins as input, output, or special functions.
//! 2. @b State @b Control: Read and write pin states with various options.
//! 3. @b Interrupt @b Support: Comprehensive interrupt handling for GPIO events.
//! 4. @b Function @b Selection: Support for multiple pin functions and modes.
//! 5. @b Power @b Management: Efficient pin state management for low-power operation.
//!
//! @section hal_gpio_functionality Functionality
//!
//! - Configure GPIO pins for various modes and functions
//! - Read and write pin states with different options
//! - Set up and handle GPIO interrupts
//! - Manage pin configurations and overrides
//! - Support for multiple GPIO channels and interrupt sources
//!
//! @section hal_gpio_usage Usage
//!
//! 1. Configure pins using am_hal_gpio_pinconfig() or related functions
//! 2. Read/write pin states as needed
//! 3. Set up interrupts if required
//! 4. Handle GPIO events in interrupt service routines
//!
//! @section hal_gpio_configuration Configuration
//!
//! - @b Pin @b Modes: Input, output, tristate, open-drain, disabled
//! - @b Pull-up/Pull-down: Configure internal pull resistors
//! - @b Interrupts: Set up interrupt channels and masks
//! - @b Function @b Selection: Choose pin functions and modes
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

#include "ambiq_gpio_compat.h"
uint32_t
am_hal_gpio_interrupt_irq_status_get(uint32_t ui32GpioIrq,
                                     bool bEnabledOnly,
                                     uint32_t *pui32IntStatus)
{
    uint32_t ui32FuncRet = AM_HAL_STATUS_SUCCESS;
    uint32_t ui32Nx, ui32Idx, ui32EnblAddr, ui32StatAddr;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    if (  (pui32IntStatus == NULL)          ||
          (ui32GpioIrq < GPIO0_001F_IRQn)   ||
          ( (ui32GpioIrq > GPIO0_C0DF_IRQn) && (ui32GpioIrq < GPIO1_001F_IRQn) ) ||
          (ui32GpioIrq > GPIO1_C0DF_IRQn) )
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    //
    // Get the addresses of the required interrupts registers.
    //
    ui32Nx  = (ui32GpioIrq <= GPIO0_C0DF_IRQn) ? 0 : 1;
    ui32Idx = ui32GpioIrq - GPIO0_001F_IRQn - (ui32Nx * (GPIO1_001F_IRQn - GPIO0_C0DF_IRQn - 1)) - (ui32Nx * (GPIO0_C0DF_IRQn - GPIO0_001F_IRQn + 1));

    ui32EnblAddr = (uint32_t)&GPIO->MCUN0INT0EN   + (ui32Nx * GPIO_NXINT_DELTA) + (ui32Idx * GPIO_INTX_DELTA);
    ui32StatAddr = (uint32_t)&GPIO->MCUN0INT0STAT + (ui32Nx * GPIO_NXINT_DELTA) + (ui32Idx * GPIO_INTX_DELTA);

    AM_CRITICAL_BEGIN
    *pui32IntStatus  = bEnabledOnly ? AM_REGVAL(ui32EnblAddr) : 0xFFFFFFFF;

    //
    // Get the GPIO status register we are interested in.
    //
    *pui32IntStatus &= AM_REGVAL(ui32StatAddr);
    AM_CRITICAL_END

    //
    // Return the status.
    //
    return ui32FuncRet;

}

uint32_t
am_hal_gpio_interrupt_irq_clear(uint32_t ui32GpioIrq,
                                uint32_t ui32GpioIntMaskStatus)
{
    uint32_t ui32Nx, ui32Idx, ui32RegAddr;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    if ( (ui32GpioIrq < GPIO0_001F_IRQn)   ||
        ( (ui32GpioIrq > GPIO0_C0DF_IRQn) && (ui32GpioIrq < GPIO1_001F_IRQn) ) ||
         (ui32GpioIrq > GPIO1_C0DF_IRQn) )
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    //
    // Get the addresses of the required interrupts registers.
    //
    ui32Nx  = (ui32GpioIrq <= GPIO0_C0DF_IRQn) ? 0 : 1;
    ui32Idx = ui32GpioIrq - GPIO0_001F_IRQn - (ui32Nx * (GPIO1_001F_IRQn - GPIO0_C0DF_IRQn - 1)) - (ui32Nx * (GPIO0_C0DF_IRQn - GPIO0_001F_IRQn + 1));
    ui32RegAddr = (uint32_t)&GPIO->MCUN0INT0CLR + (ui32Nx * GPIO_NXINT_DELTA) + (ui32Idx * GPIO_INTX_DELTA);

    //
    // Clear the given interrupt.
    //
    AM_REGVAL(ui32RegAddr) = ui32GpioIntMaskStatus;

    //
    // Return the status.
    //
    return AM_HAL_STATUS_SUCCESS;

}

uint32_t
am_hal_gpio_interrupt_register(am_hal_gpio_int_channel_e eChannel,
                               uint32_t ui32GpioNum,
                               am_hal_gpio_handler_t pfnHandler,
                               void *pArg)
{
    //
    // Determine the correct IRQ offset numbers.
    //
    uint32_t ui32Channel0Irq = GPIO_NUM2IDX(ui32GpioNum);
    uint32_t ui32Channel1Irq = ui32Channel0Irq + 7;

    //
    // Store the handler information in the array associated with this GPIO.
    //
    if ( eChannel == AM_HAL_GPIO_INT_CHANNEL_0 )
    {
        gpio_ppfnHandlers[ui32Channel0Irq][ui32GpioNum % 32] = pfnHandler;
        gpio_pppvIrqArgs[ui32Channel0Irq][ui32GpioNum % 32] = pArg;
    }
    else if ( eChannel == AM_HAL_GPIO_INT_CHANNEL_1)
    {
        gpio_ppfnHandlers[ui32Channel1Irq][ui32GpioNum % 32] = pfnHandler;
        gpio_pppvIrqArgs[ui32Channel1Irq][ui32GpioNum % 32] = pArg;
    }
    else if ( eChannel == AM_HAL_GPIO_INT_CHANNEL_BOTH)
    {
        gpio_ppfnHandlers[ui32Channel0Irq][ui32GpioNum % 32] = pfnHandler;
        gpio_pppvIrqArgs[ui32Channel0Irq][ui32GpioNum % 32] = pArg;
        gpio_ppfnHandlers[ui32Channel1Irq][ui32GpioNum % 32] = pfnHandler;
        gpio_pppvIrqArgs[ui32Channel1Irq][ui32GpioNum % 32] = pArg;
    }
    else
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }

    //
    // Return the status.
    //
    return AM_HAL_STATUS_SUCCESS;

}

uint32_t
am_hal_gpio_interrupt_service(uint32_t ui32GpioIrq,
                              uint32_t ui32GpioIntMaskStatus)
{
    uint32_t ui32RetStatus = AM_HAL_STATUS_SUCCESS;
    uint32_t ui32FFS, ui32HandlerIdx;
    am_hal_gpio_handler_t pfnHandler;
    void *pArg;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    //
    // Check parameters
    //
    if (!(((ui32GpioIrq >= GPIO1_001F_IRQn) && (ui32GpioIrq <= GPIO1_C0DF_IRQn)) || \
          ((ui32GpioIrq >= GPIO0_001F_IRQn) && (ui32GpioIrq <= GPIO0_C0DF_IRQn))))
    {
        return AM_HAL_STATUS_OUT_OF_RANGE;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    //
    // Get Irq service handler index.
    //
    if ( GPIO_IRQ2N(ui32GpioIrq) == 0)
    {
        ui32HandlerIdx = GPIO_IRQ2IDX(ui32GpioIrq);
    }
    else
    {
        ui32HandlerIdx = GPIO_IRQ2IDX(ui32GpioIrq) + 7;
    }

    //
    // Handle interrupts.
    // Get status word from the caller.
    //
    while ( ui32GpioIntMaskStatus )
    {
        //
        // We need to FFS (Find First Set).  We can easily zero-base FFS
        // since we know that at least 1 bit is set in ui32GpioIntMaskStatus.
        // FFS(x) = 31 - clz(x & -x).       // Zero-based version of FFS.
        //
        ui32FFS = ui32GpioIntMaskStatus & (uint32_t)(-(int32_t)ui32GpioIntMaskStatus);
        ui32FFS = 31 - AM_ASM_CLZ(ui32FFS);

        //
        // Turn off the bit we picked in the working copy
        //
        ui32GpioIntMaskStatus &= ~(0x00000001 << ui32FFS);

        //
        // Check the bit handler table to see if there is an interrupt handler
        // registered for this particular bit.
        //
        pfnHandler = gpio_ppfnHandlers[ui32HandlerIdx][ui32FFS];
        pArg = gpio_pppvIrqArgs[ui32HandlerIdx][ui32FFS];
        if ( pfnHandler )
        {
            //
            // If we found an interrupt handler routine, call it now.
            //
            pfnHandler(pArg);
        }
        else
        {
            //
            // No handler was registered for the GPIO that interrupted.
            // Return an error.
            //
            ui32RetStatus = AM_HAL_STATUS_INVALID_OPERATION;
        }
    }

    //
    // Return the status.
    //
    return ui32RetStatus;

}
