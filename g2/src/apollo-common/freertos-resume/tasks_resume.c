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

#include "resume_compat.h"
static void prvResetNextTaskUnblockTime(void);
void vTaskSuspendAll( void )
{
    /* A critical section is not required as the variable is of type
     * BaseType_t.  Please read Richard Barry's reply in the following link to a
     * post in the FreeRTOS support forum before reporting this as a bug! -
     * https://goo.gl/wu4acr */

    /* portSOFTWARE_BARRIER() is only implemented for emulated/simulated ports that
     * do not otherwise exhibit real time behaviour. */
    portSOFTWARE_BARRIER();

    /* The scheduler is suspended if uxSchedulerSuspended is non-zero.  An increment
     * is used to allow calls to vTaskSuspendAll() to nest. */
    ++uxSchedulerSuspended;

    /* Enforces ordering for ports and optimised compilers that may otherwise place
     * the above increment elsewhere. */
    portMEMORY_BARRIER();
}
BaseType_t xTaskResumeAll( void )
{
    TCB_t * pxTCB = NULL;
    BaseType_t xAlreadyYielded = pdFALSE;

    /* If uxSchedulerSuspended is zero then this function does not match a
     * previous call to vTaskSuspendAll(). */
    configASSERT( uxSchedulerSuspended );

    /* It is possible that an ISR caused a task to be removed from an event
     * list while the scheduler was suspended.  If this was the case then the
     * removed task will have been added to the xPendingReadyList.  Once the
     * scheduler has been resumed it is safe to move all the pending ready
     * tasks from this list into their appropriate ready list. */
    taskENTER_CRITICAL();
    {
        --uxSchedulerSuspended;

        if( uxSchedulerSuspended == ( UBaseType_t ) pdFALSE )
        {
            if( uxCurrentNumberOfTasks > ( UBaseType_t ) 0U )
            {
                /* Move any readied tasks from the pending list into the
                 * appropriate ready list. */
                while( listLIST_IS_EMPTY( &xPendingReadyList ) == pdFALSE )
                {
                    pxTCB = listGET_OWNER_OF_HEAD_ENTRY( ( &xPendingReadyList ) ); /*lint !e9079 void * is used as this macro is used with timers and co-routines too.  Alignment is known to be fine as the type of the pointer stored and retrieved is the same. */
                    listREMOVE_ITEM( &( pxTCB->xEventListItem ) );
                    portMEMORY_BARRIER();
                    listREMOVE_ITEM( &( pxTCB->xStateListItem ) );
                    prvAddTaskToReadyList( pxTCB );

                    /* If the moved task has a priority higher than or equal to
                     * the current task then a yield must be performed. */
                    if( pxTCB->uxPriority >= pxCurrentTCB->uxPriority )
                    {
                        xYieldPending = pdTRUE;
                    }
                    else
                    {
                        mtCOVERAGE_TEST_MARKER();
                    }
                }

                if( pxTCB != NULL )
                {
                    /* A task was unblocked while the scheduler was suspended,
                     * which may have prevented the next unblock time from being
                     * re-calculated, in which case re-calculate it now.  Mainly
                     * important for low power tickless implementations, where
                     * this can prevent an unnecessary exit from low power
                     * state. */
                    prvResetNextTaskUnblockTime();
                }

                /* If any ticks occurred while the scheduler was suspended then
                 * they should be processed now.  This ensures the tick count does
                 * not  slip, and that any delayed tasks are resumed at the correct
                 * time. */
                {
                    TickType_t xPendedCounts = xPendedTicks; /* Non-volatile copy. */

                    if( xPendedCounts > ( TickType_t ) 0U )
                    {
                        do
                        {
                            if( xTaskIncrementTick() != pdFALSE )
                            {
                                xYieldPending = pdTRUE;
                            }
                            else
                            {
                                mtCOVERAGE_TEST_MARKER();
                            }

                            --xPendedCounts;
                        } while( xPendedCounts > ( TickType_t ) 0U );

                        xPendedTicks = 0;
                    }
                    else
                    {
                        mtCOVERAGE_TEST_MARKER();
                    }
                }

                if( xYieldPending != pdFALSE )
                {
                    #if ( configUSE_PREEMPTION != 0 )
                    {
                        xAlreadyYielded = pdTRUE;
                    }
                    #endif
                    taskYIELD_IF_USING_PREEMPTION();
                }
                else
                {
                    mtCOVERAGE_TEST_MARKER();
                }
            }
        }
        else
        {
            mtCOVERAGE_TEST_MARKER();
        }
    }
    taskEXIT_CRITICAL();

    return xAlreadyYielded;
}
static void prvResetNextTaskUnblockTime( void )
{
    if( listLIST_IS_EMPTY( pxDelayedTaskList ) != pdFALSE )
    {
        /* The new current delayed list is empty.  Set xNextTaskUnblockTime to
         * the maximum possible value so it is  extremely unlikely that the
         * if( xTickCount >= xNextTaskUnblockTime ) test will pass until
         * there is an item in the delayed list. */
        xNextTaskUnblockTime = portMAX_DELAY;
    }
    else
    {
        /* The new current delayed list is not empty, get the value of
         * the item at the head of the delayed list.  This is the time at
         * which the task at the head of the delayed list should be removed
         * from the Blocked state. */
        xNextTaskUnblockTime = listGET_ITEM_VALUE_OF_HEAD_ENTRY( pxDelayedTaskList );
    }
}
