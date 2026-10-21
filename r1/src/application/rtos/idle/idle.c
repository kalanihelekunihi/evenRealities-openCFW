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
#include "idle_contract.h"
static portTASK_FUNCTION( prvIdleTask, pvParameters )
{
    /* Stop warnings. */
    ( void ) pvParameters;

    /** THIS IS THE RTOS IDLE TASK - WHICH IS CREATED AUTOMATICALLY WHEN THE
     * SCHEDULER IS STARTED. **/

    /* In case a task that has a secure context deletes itself, in which case
     * the idle task is responsible for deleting the task's secure context, if
     * any. */
    portALLOCATE_SECURE_CONTEXT( configMINIMAL_SECURE_STACK_SIZE );

    for( ; ; )
    {
        /* See if any tasks have deleted themselves - if so then the idle task
         * is responsible for freeing the deleted task's TCB and stack. */
        prvCheckTasksWaitingTermination();

        #if ( configUSE_PREEMPTION == 0 )
        {
            /* If we are not using preemption we keep forcing a task switch to
             * see if any other task has become available.  If we are using
             * preemption we don't need to do this as any task becoming available
             * will automatically get the processor anyway. */
            taskYIELD();
        }
        #endif /* configUSE_PREEMPTION */

        #if ( ( configUSE_PREEMPTION == 1 ) && ( configIDLE_SHOULD_YIELD == 1 ) )
        {
            /* When using preemption tasks of equal priority will be
             * timesliced.  If a task that is sharing the idle priority is ready
             * to run then the idle task should yield before the end of the
             * timeslice.
             *
             * A critical region is not required here as we are just reading from
             * the list, and an occasional incorrect value will not matter.  If
             * the ready list at the idle priority contains more than one task
             * then a task other than the idle task is ready to execute. */
            if( listCURRENT_LIST_LENGTH( &( pxReadyTasksLists[ tskIDLE_PRIORITY ] ) ) > ( UBaseType_t ) 1 )
            {
                taskYIELD();
            }
            else
            {
                mtCOVERAGE_TEST_MARKER();
            }
        }
        #endif /* ( ( configUSE_PREEMPTION == 1 ) && ( configIDLE_SHOULD_YIELD == 1 ) ) */

        #if ( configUSE_IDLE_HOOK == 1 )
        {
            extern void vApplicationIdleHook( void );

            /* Call the user defined function from within the idle task.  This
             * allows the application designer to add background functionality
             * without the overhead of a separate task.
             * NOTE: vApplicationIdleHook() MUST NOT, UNDER ANY CIRCUMSTANCES,
             * CALL A FUNCTION THAT MIGHT BLOCK. */
            vApplicationIdleHook();
        }
        #endif /* configUSE_IDLE_HOOK */

        /* This conditional compilation should use inequality to 0, not equality
         * to 1.  This is to ensure portSUPPRESS_TICKS_AND_SLEEP() is called when
         * user defined low power mode  implementations require
         * configUSE_TICKLESS_IDLE to be set to a value other than 1. */
        #if ( configUSE_TICKLESS_IDLE != 0 )
        {
            TickType_t xExpectedIdleTime;

            /* It is not desirable to suspend then resume the scheduler on
             * each iteration of the idle task.  Therefore, a preliminary
             * test of the expected idle time is performed without the
             * scheduler suspended.  The result here is not necessarily
             * valid. */
            xExpectedIdleTime = prvGetExpectedIdleTime();

            if( xExpectedIdleTime >= configEXPECTED_IDLE_TIME_BEFORE_SLEEP )
            {
                vTaskSuspendAll();
                {
                    /* Now the scheduler is suspended, the expected idle
                     * time can be sampled again, and this time its value can
                     * be used. */
                    configASSERT( xNextTaskUnblockTime >= xTickCount );
                    xExpectedIdleTime = prvGetExpectedIdleTime();

                    /* Define the following macro to set xExpectedIdleTime to 0
                     * if the application does not want
                     * portSUPPRESS_TICKS_AND_SLEEP() to be called. */
                    configPRE_SUPPRESS_TICKS_AND_SLEEP_PROCESSING( xExpectedIdleTime );

                    if( xExpectedIdleTime >= configEXPECTED_IDLE_TIME_BEFORE_SLEEP )
                    {
                        traceLOW_POWER_IDLE_BEGIN();
                        portSUPPRESS_TICKS_AND_SLEEP( xExpectedIdleTime );
                        traceLOW_POWER_IDLE_END();
                    }
                    else
                    {
                        mtCOVERAGE_TEST_MARKER();
                    }
                }
                ( void ) xTaskResumeAll();
            }
            else
            {
                mtCOVERAGE_TEST_MARKER();
            }
        }
        #endif /* configUSE_TICKLESS_IDLE */
    }
}

void r1_native_idle_watchdog_hook(void) { (void)r1_native_watchdog_hw_feed_thunk(); }
void r1_native_idle_task(void *) __attribute__((alias("prvIdleTask")));
