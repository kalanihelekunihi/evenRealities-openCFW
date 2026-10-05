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
#include "ready_compat.h"
static void prvResetNextTaskUnblockTime(void);
BaseType_t xTaskRemoveFromEventList( const List_t * const pxEventList )
{
    TCB_t * pxUnblockedTCB;
    BaseType_t xReturn;

    /* THIS FUNCTION MUST BE CALLED FROM A CRITICAL SECTION.  It can also be
     * called from a critical section within an ISR. */

    /* The event list is sorted in priority order, so the first in the list can
     * be removed as it is known to be the highest priority.  Remove the TCB from
     * the delayed list, and add it to the ready list.
     *
     * If an event is for a queue that is locked then this function will never
     * get called - the lock count on the queue will get modified instead.  This
     * means exclusive access to the event list is guaranteed here.
     *
     * This function assumes that a check has already been made to ensure that
     * pxEventList is not empty. */
    pxUnblockedTCB = listGET_OWNER_OF_HEAD_ENTRY( pxEventList ); /*lint !e9079 void * is used as this macro is used with timers and co-routines too.  Alignment is known to be fine as the type of the pointer stored and retrieved is the same. */
    configASSERT( pxUnblockedTCB );
    listREMOVE_ITEM( &( pxUnblockedTCB->xEventListItem ) );

    if( uxSchedulerSuspended == ( UBaseType_t ) pdFALSE )
    {
        listREMOVE_ITEM( &( pxUnblockedTCB->xStateListItem ) );
        prvAddTaskToReadyList( pxUnblockedTCB );

        #if ( configUSE_TICKLESS_IDLE != 0 )
        {
            /* If a task is blocked on a kernel object then xNextTaskUnblockTime
             * might be set to the blocked task's time out time.  If the task is
             * unblocked for a reason other than a timeout xNextTaskUnblockTime is
             * normally left unchanged, because it is automatically reset to a new
             * value when the tick count equals xNextTaskUnblockTime.  However if
             * tickless idling is used it might be more important to enter sleep mode
             * at the earliest possible time - so reset xNextTaskUnblockTime here to
             * ensure it is updated at the earliest possible time. */
            prvResetNextTaskUnblockTime();
        }
        #endif
    }
    else
    {
        /* The delayed and ready lists cannot be accessed, so hold this task
         * pending until the scheduler is resumed. */
        listINSERT_END( &( xPendingReadyList ), &( pxUnblockedTCB->xEventListItem ) );
    }

    if( pxUnblockedTCB->uxPriority > pxCurrentTCB->uxPriority )
    {
        /* Return true if the task removed from the event list has a higher
         * priority than the calling task.  This allows the calling task to know if
         * it should force a context switch now. */
        xReturn = pdTRUE;

        /* Mark that a yield is pending in case the user is not using the
         * "xHigherPriorityTaskWoken" parameter to an ISR safe FreeRTOS function. */
        xYieldPending = pdTRUE;
    }
    else
    {
        xReturn = pdFALSE;
    }

    return xReturn;
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
UBaseType_t uxTaskGetNumberOfTasks( void )
{
    /* A critical section is not required because the variables are of type
     * BaseType_t. */
    return uxCurrentNumberOfTasks;
}
