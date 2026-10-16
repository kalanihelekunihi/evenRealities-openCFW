/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.  All Rights Reserved.
 *
 * SPDX-License-Identifier: MIT
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of
 * this software and associated documentation files (the "Software"), to deal in
 * the Software without restriction, including without limitation the rights to
 * use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
 * the Software, and to permit persons to whom the Software is furnished to do so,
 * subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 * FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
 * COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
 * IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 * https://www.FreeRTOS.org
 * https://github.com/FreeRTOS
 *
 */
#include "sleep_kernel_contract.h"
    eSleepModeStatus eTaskConfirmSleepModeStatus( void )
    {
        #if ( INCLUDE_vTaskSuspend == 1 )
            /* The idle task exists in addition to the application tasks. */
            const UBaseType_t uxNonApplicationTasks = 1;
        #endif /* INCLUDE_vTaskSuspend */

        eSleepModeStatus eReturn = eStandardSleep;

        /* This function must be called from a critical section. */

        if( listCURRENT_LIST_LENGTH( &xPendingReadyList ) != 0 )
        {
            /* A task was made ready while the scheduler was suspended. */
            eReturn = eAbortSleep;
        }
        else if( xYieldPending != pdFALSE )
        {
            /* A yield was pended while the scheduler was suspended. */
            eReturn = eAbortSleep;
        }
        else if( xPendedTicks != 0 )
        {
            /* A tick interrupt has already occurred but was held pending
             * because the scheduler is suspended. */
            eReturn = eAbortSleep;
        }

        #if ( INCLUDE_vTaskSuspend == 1 )
            else if( listCURRENT_LIST_LENGTH( &xSuspendedTaskList ) == ( uxCurrentNumberOfTasks - uxNonApplicationTasks ) )
            {
                /* If all the tasks are in the suspended list (which might mean they
                 * have an infinite block time rather than actually being suspended)
                 * then it is safe to turn all clocks off and just wait for external
                 * interrupts. */
                eReturn = eNoTasksWaitingTimeout;
            }
        #endif /* INCLUDE_vTaskSuspend */
        else
        {
            mtCOVERAGE_TEST_MARKER();
        }

        return eReturn;
    }
    void vTaskStepTick( TickType_t xTicksToJump )
    {
        /* Correct the tick count value after a period during which the tick
         * was suppressed.  Note this does *not* call the tick hook function for
         * each stepped tick. */
        configASSERT( ( xTickCount + xTicksToJump ) <= xNextTaskUnblockTime );

        if( ( xTickCount + xTicksToJump ) == xNextTaskUnblockTime )
        {
            /* Arrange for xTickCount to reach xNextTaskUnblockTime in
             * xTaskIncrementTick() when the scheduler resumes.  This ensures
             * that any delayed tasks are resumed at the correct time. */
            configASSERT( uxSchedulerSuspended );
            configASSERT( xTicksToJump != ( TickType_t ) 0 );

            /* Prevent the tick interrupt modifying xPendedTicks simultaneously. */
            taskENTER_CRITICAL();
            {
                xPendedTicks++;
            }
            taskEXIT_CRITICAL();
            xTicksToJump--;
        }
        else
        {
            mtCOVERAGE_TEST_MARKER();
        }

        xTickCount += xTicksToJump;
        traceINCREASE_TICK_COUNT( xTicksToJump );
    }