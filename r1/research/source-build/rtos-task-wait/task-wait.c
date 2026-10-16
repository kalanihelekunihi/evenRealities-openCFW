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
#include "task_wait_contract.h"
const volatile UBaseType_t uxTopUsedPriority = configMAX_PRIORITIES - 1U;

    #define portRESET_READY_PRIORITY( uxPriority, uxTopReadyPriority )

#define prvAddTaskToReadyList( pxTCB )                                                                 \
    traceMOVED_TASK_TO_READY_STATE( pxTCB );                                                           \
    taskRECORD_READY_PRIORITY( ( pxTCB )->uxPriority );                                                \
    listINSERT_END( &( pxReadyTasksLists[ ( pxTCB )->uxPriority ] ), &( ( pxTCB )->xStateListItem ) ); \
    tracePOST_MOVED_TASK_TO_READY_STATE( pxTCB )

    #define taskRECORD_READY_PRIORITY( uxPriority ) \
    {                                               \
        if( ( uxPriority ) > uxTopReadyPriority )   \
        {                                           \
            uxTopReadyPriority = ( uxPriority );    \
        }                                           \
    } /* taskRECORD_READY_PRIORITY */

void vTaskInternalSetTimeOutState( TimeOut_t * const pxTimeOut )
{
    /* For internal use only as it does not use a critical section. */
    pxTimeOut->xOverflowCount = xNumOfOverflows;
    pxTimeOut->xTimeOnEntering = xTickCount;
}

void vTaskMissedYield( void )
{
    xYieldPending = pdTRUE;
}

void vTaskPlaceOnEventList( List_t * const pxEventList,
                            const TickType_t xTicksToWait )
{
    configASSERT( pxEventList );

    /* THIS FUNCTION MUST BE CALLED WITH EITHER INTERRUPTS DISABLED OR THE
     * SCHEDULER SUSPENDED AND THE QUEUE BEING ACCESSED LOCKED. */

    /* Place the event list item of the TCB in the appropriate event list.
     * This is placed in the list in priority order so the highest priority task
     * is the first to be woken by the event.
     *
     * Note: Lists are sorted in ascending order by ListItem_t.xItemValue.
     * Normally, the xItemValue of a TCB's ListItem_t members is:
     *      xItemValue = ( configMAX_PRIORITIES - uxPriority )
     * Therefore, the event list is sorted in descending priority order.
     *
     * The queue that contains the event list is locked, preventing
     * simultaneous access from interrupts. */
    vListInsert( pxEventList, &( pxCurrentTCB->xEventListItem ) );

    prvAddCurrentTaskToDelayedList( xTicksToWait, pdTRUE );
}

BaseType_t xTaskCheckForTimeOut( TimeOut_t * const pxTimeOut,
                                 TickType_t * const pxTicksToWait )
{
    BaseType_t xReturn;

    configASSERT( pxTimeOut );
    configASSERT( pxTicksToWait );

    taskENTER_CRITICAL();
    {
        /* Minor optimisation.  The tick count cannot change in this block. */
        const TickType_t xConstTickCount = xTickCount;
        const TickType_t xElapsedTime = xConstTickCount - pxTimeOut->xTimeOnEntering;

        #if ( INCLUDE_xTaskAbortDelay == 1 )
            if( pxCurrentTCB->ucDelayAborted != ( uint8_t ) pdFALSE )
            {
                /* The delay was aborted, which is not the same as a time out,
                 * but has the same result. */
                pxCurrentTCB->ucDelayAborted = pdFALSE;
                xReturn = pdTRUE;
            }
            else
        #endif

        #if ( INCLUDE_vTaskSuspend == 1 )
            if( *pxTicksToWait == portMAX_DELAY )
            {
                /* If INCLUDE_vTaskSuspend is set to 1 and the block time
                 * specified is the maximum block time then the task should block
                 * indefinitely, and therefore never time out. */
                xReturn = pdFALSE;
            }
            else
        #endif

        if( ( xNumOfOverflows != pxTimeOut->xOverflowCount ) && ( xConstTickCount >= pxTimeOut->xTimeOnEntering ) ) /*lint !e525 Indentation preferred as is to make code within pre-processor directives clearer. */
        {
            /* The tick count is greater than the time at which
             * vTaskSetTimeout() was called, but has also overflowed since
             * vTaskSetTimeOut() was called.  It must have wrapped all the way
             * around and gone past again. This passed since vTaskSetTimeout()
             * was called. */
            xReturn = pdTRUE;
            *pxTicksToWait = ( TickType_t ) 0;
        }
        else if( xElapsedTime < *pxTicksToWait ) /*lint !e961 Explicit casting is only redundant with some compilers, whereas others require it to prevent integer conversion errors. */
        {
            /* Not a genuine timeout. Adjust parameters for time remaining. */
            *pxTicksToWait -= xElapsedTime;
            vTaskInternalSetTimeOutState( pxTimeOut );
            xReturn = pdFALSE;
        }
        else
        {
            *pxTicksToWait = ( TickType_t ) 0;
            xReturn = pdTRUE;
        }
    }
    taskEXIT_CRITICAL();

    return xReturn;
}

    BaseType_t xTaskPriorityDisinherit( TaskHandle_t const pxMutexHolder )
    {
        TCB_t * const pxTCB = pxMutexHolder;
        BaseType_t xReturn = pdFALSE;

        if( pxMutexHolder != NULL )
        {
            /* A task can only have an inherited priority if it holds the mutex.
             * If the mutex is held by a task then it cannot be given from an
             * interrupt, and if a mutex is given by the holding task then it must
             * be the running state task. */
            configASSERT( pxTCB == pxCurrentTCB );
            configASSERT( pxTCB->uxMutexesHeld );
            ( pxTCB->uxMutexesHeld )--;

            /* Has the holder of the mutex inherited the priority of another
             * task? */
            if( pxTCB->uxPriority != pxTCB->uxBasePriority )
            {
                /* Only disinherit if no other mutexes are held. */
                if( pxTCB->uxMutexesHeld == ( UBaseType_t ) 0 )
                {
                    /* A task can only have an inherited priority if it holds
                     * the mutex.  If the mutex is held by a task then it cannot be
                     * given from an interrupt, and if a mutex is given by the
                     * holding task then it must be the running state task.  Remove
                     * the holding task from the ready list. */
                    if( uxListRemove( &( pxTCB->xStateListItem ) ) == ( UBaseType_t ) 0 )
                    {
                        portRESET_READY_PRIORITY( pxTCB->uxPriority, uxTopReadyPriority );
                    }
                    else
                    {
                        mtCOVERAGE_TEST_MARKER();
                    }

                    /* Disinherit the priority before adding the task into the
                     * new  ready list. */
                    traceTASK_PRIORITY_DISINHERIT( pxTCB, pxTCB->uxBasePriority );
                    pxTCB->uxPriority = pxTCB->uxBasePriority;

                    /* Reset the event list item value.  It cannot be in use for
                     * any other purpose if this task is running, and it must be
                     * running to give back the mutex. */
                    listSET_LIST_ITEM_VALUE( &( pxTCB->xEventListItem ), ( TickType_t ) configMAX_PRIORITIES - ( TickType_t ) pxTCB->uxPriority ); /*lint !e961 MISRA exception as the casts are only redundant for some ports. */
                    prvAddTaskToReadyList( pxTCB );

                    /* Return true to indicate that a context switch is required.
                     * This is only actually required in the corner case whereby
                     * multiple mutexes were held and the mutexes were given back
                     * in an order different to that in which they were taken.
                     * If a context switch did not occur when the first mutex was
                     * returned, even if a task was waiting on it, then a context
                     * switch should occur when the last mutex is returned whether
                     * a task is waiting on it or not. */
                    xReturn = pdTRUE;
                }
                else
                {
                    mtCOVERAGE_TEST_MARKER();
                }
            }
            else
            {
                mtCOVERAGE_TEST_MARKER();
            }
        }
        else
        {
            mtCOVERAGE_TEST_MARKER();
        }

        return xReturn;
    }

static void prvAddCurrentTaskToDelayedList( TickType_t xTicksToWait,
                                            const BaseType_t xCanBlockIndefinitely )
{
    TickType_t xTimeToWake;
    const TickType_t xConstTickCount = xTickCount;

    #if ( INCLUDE_xTaskAbortDelay == 1 )
    {
        /* About to enter a delayed list, so ensure the ucDelayAborted flag is
         * reset to pdFALSE so it can be detected as having been set to pdTRUE
         * when the task leaves the Blocked state. */
        pxCurrentTCB->ucDelayAborted = pdFALSE;
    }
    #endif

    /* Remove the task from the ready list before adding it to the blocked list
     * as the same list item is used for both lists. */
    if( uxListRemove( &( pxCurrentTCB->xStateListItem ) ) == ( UBaseType_t ) 0 )
    {
        /* The current task must be in a ready list, so there is no need to
         * check, and the port reset macro can be called directly. */
        portRESET_READY_PRIORITY( pxCurrentTCB->uxPriority, uxTopReadyPriority ); /*lint !e931 pxCurrentTCB cannot change as it is the calling task.  pxCurrentTCB->uxPriority and uxTopReadyPriority cannot change as called with scheduler suspended or in a critical section. */
    }
    else
    {
        mtCOVERAGE_TEST_MARKER();
    }

    #if ( INCLUDE_vTaskSuspend == 1 )
    {
        if( ( xTicksToWait == portMAX_DELAY ) && ( xCanBlockIndefinitely != pdFALSE ) )
        {
            /* Add the task to the suspended task list instead of a delayed task
             * list to ensure it is not woken by a timing event.  It will block
             * indefinitely. */
            listINSERT_END( &xSuspendedTaskList, &( pxCurrentTCB->xStateListItem ) );
        }
        else
        {
            /* Calculate the time at which the task should be woken if the event
             * does not occur.  This may overflow but this doesn't matter, the
             * kernel will manage it correctly. */
            xTimeToWake = xConstTickCount + xTicksToWait;

            /* The list item will be inserted in wake time order. */
            listSET_LIST_ITEM_VALUE( &( pxCurrentTCB->xStateListItem ), xTimeToWake );

            if( xTimeToWake < xConstTickCount )
            {
                /* Wake time has overflowed.  Place this item in the overflow
                 * list. */
                vListInsert( pxOverflowDelayedTaskList, &( pxCurrentTCB->xStateListItem ) );
            }
            else
            {
                /* The wake time has not overflowed, so the current block list
                 * is used. */
                vListInsert( pxDelayedTaskList, &( pxCurrentTCB->xStateListItem ) );

                /* If the task entering the blocked state was placed at the
                 * head of the list of blocked tasks then xNextTaskUnblockTime
                 * needs to be updated too. */
                if( xTimeToWake < xNextTaskUnblockTime )
                {
                    xNextTaskUnblockTime = xTimeToWake;
                }
                else
                {
                    mtCOVERAGE_TEST_MARKER();
                }
            }
        }
    }
    #else /* INCLUDE_vTaskSuspend */
    {
        /* Calculate the time at which the task should be woken if the event
         * does not occur.  This may overflow but this doesn't matter, the kernel
         * will manage it correctly. */
        xTimeToWake = xConstTickCount + xTicksToWait;

        /* The list item will be inserted in wake time order. */
        listSET_LIST_ITEM_VALUE( &( pxCurrentTCB->xStateListItem ), xTimeToWake );

        if( xTimeToWake < xConstTickCount )
        {
            /* Wake time has overflowed.  Place this item in the overflow list. */
            vListInsert( pxOverflowDelayedTaskList, &( pxCurrentTCB->xStateListItem ) );
        }
        else
        {
            /* The wake time has not overflowed, so the current block list is used. */
            vListInsert( pxDelayedTaskList, &( pxCurrentTCB->xStateListItem ) );

            /* If the task entering the blocked state was placed at the head of the
             * list of blocked tasks then xNextTaskUnblockTime needs to be updated
             * too. */
            if( xTimeToWake < xNextTaskUnblockTime )
            {
                xNextTaskUnblockTime = xTimeToWake;
            }
            else
            {
                mtCOVERAGE_TEST_MARKER();
            }
        }

        /* Avoid compiler warning when INCLUDE_vTaskSuspend is not 1. */
        ( void ) xCanBlockIndefinitely;
    }
    #endif /* INCLUDE_vTaskSuspend */
}
