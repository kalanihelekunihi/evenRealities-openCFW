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
write_transaction_save(am_hal_uart_state_t *psState,
                       const am_hal_uart_transfer_t *psTransfer)
{
    uint32_t ui32Error = AM_HAL_STATUS_SUCCESS;

    AM_CRITICAL_BEGIN

    if (psState->bCurrentlyWriting == false)
    {
        psState->bCurrentlyWriting = true;
        psState->sActiveWrite.eType = psTransfer->eType;
        psState->sActiveWrite.pui8Data = psTransfer->pui8Data;
        psState->sActiveWrite.ui32NumBytes = psTransfer->ui32NumBytes;
        psState->sActiveWrite.pui32BytesTransferred = psTransfer->pui32BytesTransferred;
        psState->sActiveWrite.ui32TimeoutMs = psTransfer->ui32TimeoutMs;
        psState->sActiveWrite.pfnCallback = psTransfer->pfnCallback;
        psState->sActiveWrite.pvContext = psTransfer->pvContext;
        psState->sActiveWrite.ui32ErrorStatus = psTransfer->ui32ErrorStatus;
        psState->ui32BytesWritten = 0;
        psState->bLastTxComplete = false;
    }
    else
    {
        ui32Error = AM_HAL_UART_STATUS_TX_CHANNEL_BUSY;
    }

    AM_CRITICAL_END

    return ui32Error;
}

uint32_t
am_hal_uart_fifo_write(void *pHandle, uint8_t *pui8Data, uint32_t ui32NumBytes,
                       uint32_t *pui32NumBytesWritten)
{
    uint32_t i = 0;

    am_hal_uart_state_t *pState = (am_hal_uart_state_t *) pHandle;
    uint32_t ui32Module = pState->ui32Module;

    //
    // Start a loop where we attempt to write everything requested.
    //
    while (i < ui32NumBytes)
    {
        //
        // If the TX FIFO is full, break out of the loop. We've sent everything
        // we can.
        //
        if ( UARTn(ui32Module)->FR_b.TXFF )
        {
            break;
        }
        else
        {
            UARTn(ui32Module)->DR = pui8Data[i++];
        }
    }

    //
    // Let the caller know how much we sent.
    //
    if (pui32NumBytesWritten)
    {
        *pui32NumBytesWritten = i;
    }

    return AM_HAL_STATUS_SUCCESS;
}

static uint32_t
tx_queue_update(void *pHandle)
{
    am_hal_uart_state_t *pState = (am_hal_uart_state_t *) pHandle;
    uint32_t ui32Module = pState->ui32Module;

    uint8_t pui8Data;
    uint32_t ui32BytesTransferred;
    uint32_t ui32ErrorStatus = AM_HAL_STATUS_SUCCESS;

    AM_CRITICAL_BEGIN;

    //
    // Loop as long as the TX fifo isn't full yet.
    //
    while ( !UARTn(ui32Module)->FR_b.TXFF )
    {
        //
        // Attempt to grab an item from the queue, and add it to the fifo.
        //
        if (am_hal_queue_item_get(&pState->sTxQueue, &pui8Data, 1))
        {
            ui32ErrorStatus = am_hal_uart_fifo_write(pHandle, &pui8Data, 1,
                                                     &ui32BytesTransferred);

            if (ui32ErrorStatus != AM_HAL_STATUS_SUCCESS)
            {
                break;
            }
        }
        else
        {
            //
            // If we didn't get anything from the FIFO, we can just return.
            //
            break;
        }
    }

    AM_CRITICAL_END;

    return ui32ErrorStatus;
}

static void
nonblocking_write_sm(void *pHandle)
{
    am_hal_uart_state_t *pState = (am_hal_uart_state_t *) pHandle;

    //
    // Then, check to see if we currently have an active "write" transaction. If
    // we do, we need to pull data out of the user's buffer and either push them
    // into our internal buffer (if TX buffers were enabled) or push them to the
    // hardware fifo.
    //
    if (pState->bCurrentlyWriting)
    {
        //
        // Start a critical section to avoid problems associated with this
        // function being called from multiple places concurrently.
        //
        //
        // When the callback is called, the function must return immediately after
        // calling the callback. It can't return until the function exits the
        // critical section.
        // This flag tracks the callback usage
        //
        bool bReturnAfterCritical = false;

        AM_CRITICAL_BEGIN

        uint32_t i = pState->ui32BytesWritten;
        uint32_t ui32BytesLeft = pState->sActiveWrite.ui32NumBytes - i;

        uint8_t *pui8Src = &(pState->sActiveWrite.pui8Data[i]);

        uint32_t ui32WriteSize;

        if (pState->bEnableTxQueue)
        {
            //
            // If we are using an internal queue, we'll push as much data as we
            // can to the queue.
            //
            uint32_t ui32QueueSpace =
                am_hal_queue_space_left(&pState->sTxQueue);

            ui32WriteSize = (ui32BytesLeft < ui32QueueSpace ?
                             ui32BytesLeft : ui32QueueSpace);

            bool bSuccess = am_hal_queue_item_add(&pState->sTxQueue,
                                                  pui8Src,
                                                  ui32WriteSize);

            //
            // If something goes wrong with this queue write, even though we've
            // checked the size of the queue, then something isn't right, and we
            // should return with an error. This might indicate thread
            // mis-management.
            //
            if (bSuccess == false)
            {
                pState->bCurrentlyWriting = false;
                if (pState->sActiveWrite.pfnCallback)
                {
                    pState->sActiveWrite.pfnCallback(1, pState->sActiveWrite.pvContext);
                    // After the callback,
                    // this function needs to return once the critical section exits with
                    // no other variables modified.
                    // Set this flag to keep track of that (early return) state.
                    bReturnAfterCritical = true;
                }
            }
        }
        else // if ( !pState->bEnableTxQueue )
        {
            //
            // If we're not using a queue, we'll just write straight to the
            // FIFO. This function will attempt to write everything we have
            // left and return the actual number of bytes written to
            // ui32WriteSize.
            //
            am_hal_uart_fifo_write(pHandle, pui8Src, ui32BytesLeft,
                                   &ui32WriteSize);
        }

        if ( !bReturnAfterCritical)
        {
            //
            // Before returning, we also need to update the saved transaction,
            // closing it if we've consumed all the bytes in the user's
            // original buffer.
            // This variable is not updated after a callback has been called above.
            //
            pState->ui32BytesWritten += ui32WriteSize;
        } // else/if ( !pState->bEnableTxQueue )

        AM_CRITICAL_END

        if (bReturnAfterCritical)
        {
            //
            // the callback was executed in the critical section above,
            // and now this function needs to exit
            //
            return;
        }

        if ( pState->sActiveWrite.pui32BytesTransferred )
        {
            *pState->sActiveWrite.pui32BytesTransferred = pState->ui32BytesWritten;
        }

        if ( (pState->ui32BytesWritten == pState->sActiveWrite.ui32NumBytes) &&
             pState->bCurrentlyWriting )
        {
            //
            // all data has been written and completion notification hasn't been sent yet
            //
            pState->bCurrentlyWriting = false;

            if (pState->sActiveWrite.pfnCallback)
            {
                pState->sActiveWrite.pfnCallback(0, pState->sActiveWrite.pvContext);
            }
        }
    }

    //
    // If we're using a TX queue, send all of the data in the TX buffer to the
    // hardware fifo.
    //
    if (pState->bEnableTxQueue)
    {
        tx_queue_update(pHandle);
    }
}

static uint32_t
nonblocking_write(void *pHandle, const am_hal_uart_transfer_t *psTransfer)
{
    uint32_t ui32ErrorStatus;
    uint32_t *pui32NumBytesWritten = psTransfer->pui32BytesTransferred;

    //
    // Initialize the variable tracking how many bytes we've written.
    //
    if (pui32NumBytesWritten)
    {
        *pui32NumBytesWritten = 0;
    }

    //
    // Save the transaction, and run the state machine to transfer the data.
    //
    ui32ErrorStatus = write_transaction_save(pHandle, psTransfer);
    if (ui32ErrorStatus != AM_HAL_STATUS_SUCCESS)
    {
        return ui32ErrorStatus;
    }
    else
    {
        nonblocking_write_sm(pHandle);
    }

    return AM_HAL_STATUS_SUCCESS;
}

static uint32_t
blocking_write(void *pHandle, const am_hal_uart_transfer_t *psTransfer)
{
    uint32_t ui32Status;
    uint32_t ui32TimeSpent = 0;
    am_hal_uart_state_t *psState = pHandle;

    //
    // Blocking write has all of the same requirements as non-blocking write,
    // but we can't guarantee that the interrupt handlers will be called, so we
    // have to call them in a loop instead.
    //
    ui32Status = nonblocking_write(pHandle, psTransfer);
    if (ui32Status != AM_HAL_STATUS_SUCCESS)
    {
        return ui32Status;
    }

    while (psState->bCurrentlyWriting)
    {
        nonblocking_write_sm(pHandle);
        am_hal_delay_us(1000);

        if ( psTransfer->ui32TimeoutMs != AM_HAL_UART_WAIT_FOREVER )
        {
            ++ui32TimeSpent;
            if ( ui32TimeSpent == psTransfer->ui32TimeoutMs )
            {
                psState->bCurrentlyWriting = false;
                return AM_HAL_STATUS_TIMEOUT;
            }
        }
    }

    return AM_HAL_STATUS_SUCCESS;
}

uint32_t
am_hal_uart_buffer_configure(void *pHandle, uint8_t *pui8TxBuffer,
                             uint32_t ui32TxBufferSize,
                             uint8_t *pui8RxBuffer, uint32_t ui32RxBufferSize)
{
    am_hal_uart_state_t *pState = (am_hal_uart_state_t *) pHandle;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    //
    // Check to make sure this is a valid handle.
    //
    if (!AM_HAL_UART_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
#endif
    pState->bEnableTxQueue = false;
    pState->bEnableRxQueue = false;
    //
    // Check to see if we have a TX buffer.
    //
    if (pui8TxBuffer && ui32TxBufferSize)
    {
        //
        // If so, initialize the transmit queue, and enable the TX FIFO
        // interrupt.
        //
        pState->bEnableTxQueue = true;
        am_hal_queue_init(&pState->sTxQueue, pui8TxBuffer, 1, ui32TxBufferSize);
    }

    //
    // Check to see if we have an RX buffer.
    //
    if (pui8RxBuffer && ui32RxBufferSize)
    {
        //
        // If so, initialize the receive queue and the associated interrupts.
        //
        pState->bEnableRxQueue = true;
        am_hal_queue_init(&pState->sRxQueue, pui8RxBuffer, 1, ui32RxBufferSize);
    }

    return AM_HAL_STATUS_SUCCESS;
}

uint32_t
am_hal_uart_initialize(uint32_t ui32Module, void **ppHandle)
{
#ifndef AM_HAL_DISABLE_API_VALIDATION
    //
    // Check that the request module is in range.
    //
    if (ui32Module >= AM_REG_UART_NUM_MODULES )
    {
        return AM_HAL_STATUS_OUT_OF_RANGE;
    }

    //
    // Check for valid arguments.
    //
    if (!ppHandle)
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }

    //
    // Make sure we're not re-activating an active handle.
    //
    if (AM_HAL_UART_CHK_HANDLE(*ppHandle))
    {
        return AM_HAL_STATUS_INVALID_OPERATION;
    }
#endif
    //
    // Initialize the handle.
    //
    g_am_hal_uart_states[ui32Module].prefix.s.bInit = true;
    g_am_hal_uart_states[ui32Module].prefix.s.magic = AM_HAL_MAGIC_UART;
    g_am_hal_uart_states[ui32Module].ui32Module = ui32Module;
    g_am_hal_uart_states[ui32Module].sRegState.bValid = false;
    g_am_hal_uart_states[ui32Module].ui32BaudRate = 0;
    g_am_hal_uart_states[ui32Module].bCurrentlyReading = 0;
    g_am_hal_uart_states[ui32Module].bCurrentlyWriting = 0;
    g_am_hal_uart_states[ui32Module].bEnableTxQueue = 0;
    g_am_hal_uart_states[ui32Module].bEnableRxQueue = 0;
    g_am_hal_uart_states[ui32Module].ui32BytesWritten = 0;
    g_am_hal_uart_states[ui32Module].ui32BytesRead = 0;
    g_am_hal_uart_states[ui32Module].bLastTxComplete = true;

    //
    // Return the handle.
    //
    *ppHandle = (void *)&g_am_hal_uart_states[ui32Module];

    //
    // Return the status.
    //
    return AM_HAL_STATUS_SUCCESS;
}
