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
am_hal_uart_fifo_read(void *pHandle, uint8_t *pui8Data, uint32_t ui32NumBytes,
                      uint32_t *pui32NumBytesRead)
{
    uint32_t i = 0;
    uint32_t ui32ReadData;
    uint32_t ui32ErrorStatus = AM_HAL_STATUS_SUCCESS;

    am_hal_uart_state_t *pState = (am_hal_uart_state_t *) pHandle;
    uint32_t ui32Module = pState->ui32Module;

    //
    // Start a loop where we attempt to read everything requested.
    //
    while (i < ui32NumBytes)
    {
        //
        // If the fifo is empty, return with the number of bytes we read.
        // Otherwise, read the data into the provided buffer.
        //
        if ( UARTn(ui32Module)->FR_b.RXFE )
        {
            break;
        }
        else
        {
            ui32ReadData = UARTn(ui32Module)->DR;

            //
            // If error bits are set, we need to alert the caller.
            //
            if (ui32ReadData & (_VAL2FLD(UART0_DR_OEDATA, UART0_DR_OEDATA_ERR) |
                                _VAL2FLD(UART0_DR_BEDATA, UART0_DR_BEDATA_ERR) |
                                _VAL2FLD(UART0_DR_PEDATA, UART0_DR_PEDATA_ERR) |
                                _VAL2FLD(UART0_DR_FEDATA, UART0_DR_FEDATA_ERR)) )
            {
                ui32ErrorStatus =  AM_HAL_UART_STATUS_BUS_ERROR;
                break;
            }
            else if (pui8Data)
            {
                pui8Data[i++] = ui32ReadData & 0xFF;
            }
        }
    }

    if (pui32NumBytesRead)
    {
        *pui32NumBytesRead = i;
    }

    return ui32ErrorStatus;
}
