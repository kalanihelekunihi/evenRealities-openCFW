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

/* Public timeout snapshot from the same pinned kernel tasks.c. */
_Static_assert(sizeof(TimeOut_t)==8 && offsetof(TimeOut_t,xTimeOnEntering)==4,"native timeout snapshot layout");
void vTaskSetTimeOutState( TimeOut_t * const pxTimeOut )
{
    configASSERT( pxTimeOut );
    taskENTER_CRITICAL();
    {
        pxTimeOut->xOverflowCount = xNumOfOverflows;
        pxTimeOut->xTimeOnEntering = xTickCount;
    }
    taskEXIT_CRITICAL();
}

/* Event-group unordered wait from the same pinned kernel tasks.c. */
#define taskEVENT_LIST_ITEM_VALUE_IN_USE ((TickType_t)0x80000000u)
#define uxSchedulerSuspended (*(volatile UBaseType_t *)(uintptr_t)UINT32_C(0x20007850))
void vTaskPlaceOnUnorderedEventList( List_t * pxEventList,
                                     const TickType_t xItemValue,
                                     const TickType_t xTicksToWait )
{
    configASSERT( pxEventList );

    /* THIS FUNCTION MUST BE CALLED WITH THE SCHEDULER SUSPENDED.  It is used by
     * the event groups implementation. */
    configASSERT( uxSchedulerSuspended != 0 );

    /* Store the item value in the event list item.  It is safe to access the
     * event list item here as interrupts won't access the event list item of a
     * task that is not in the Blocked state. */
    listSET_LIST_ITEM_VALUE( &( pxCurrentTCB->xEventListItem ), xItemValue | taskEVENT_LIST_ITEM_VALUE_IN_USE );

    /* Place the event list item of the TCB at the end of the appropriate event
     * list.  It is safe to access the event list here because it is part of an
     * event group implementation - and interrupts don't access event groups
     * directly (instead they access them indirectly by pending function calls to
     * the task level). */
    listINSERT_END( pxEventList, &( pxCurrentTCB->xEventListItem ) );

    prvAddCurrentTaskToDelayedList( xTicksToWait, pdTRUE );
}
#undef uxSchedulerSuspended
#undef taskEVENT_LIST_ITEM_VALUE_IN_USE

/* Periodic delay from the same pinned kernel tasks.c. */
#define uxSchedulerSuspended (*(volatile UBaseType_t *)(uintptr_t)UINT32_C(0x20007850))
BaseType_t xTaskDelayUntil( TickType_t * const pxPreviousWakeTime,
                                const TickType_t xTimeIncrement )
    {
        TickType_t xTimeToWake;
        BaseType_t xAlreadyYielded, xShouldDelay = pdFALSE;

        configASSERT( pxPreviousWakeTime );
        configASSERT( ( xTimeIncrement > 0U ) );
        configASSERT( uxSchedulerSuspended == 0 );

        vTaskSuspendAll();
        {
            /* Minor optimisation.  The tick count cannot change in this
             * block. */
            const TickType_t xConstTickCount = xTickCount;

            /* Generate the tick time at which the task wants to wake. */
            xTimeToWake = *pxPreviousWakeTime + xTimeIncrement;

            if( xConstTickCount < *pxPreviousWakeTime )
            {
                /* The tick count has overflowed since this function was
                 * lasted called.  In this case the only time we should ever
                 * actually delay is if the wake time has also  overflowed,
                 * and the wake time is greater than the tick time.  When this
                 * is the case it is as if neither time had overflowed. */
                if( ( xTimeToWake < *pxPreviousWakeTime ) && ( xTimeToWake > xConstTickCount ) )
                {
                    xShouldDelay = pdTRUE;
                }
                else
                {
                    mtCOVERAGE_TEST_MARKER();
                }
            }
            else
            {
                /* The tick time has not overflowed.  In this case we will
                 * delay if either the wake time has overflowed, and/or the
                 * tick time is less than the wake time. */
                if( ( xTimeToWake < *pxPreviousWakeTime ) || ( xTimeToWake > xConstTickCount ) )
                {
                    xShouldDelay = pdTRUE;
                }
                else
                {
                    mtCOVERAGE_TEST_MARKER();
                }
            }

            /* Update the wake time ready for the next call. */
            *pxPreviousWakeTime = xTimeToWake;

            if( xShouldDelay != pdFALSE )
            {
                traceTASK_DELAY_UNTIL( xTimeToWake );

                /* prvAddCurrentTaskToDelayedList() needs the block time, not
                 * the time to wake, so subtract the current tick count. */
                prvAddCurrentTaskToDelayedList( xTimeToWake - xConstTickCount, pdFALSE );
            }
            else
            {
                mtCOVERAGE_TEST_MARKER();
            }
        }
        xAlreadyYielded = xTaskResumeAll();

        /* Force a reschedule if xTaskResumeAll has not already done so, we may
         * have put ourselves to sleep. */
        if( xAlreadyYielded == pdFALSE )
        {
            portYIELD_WITHIN_API();
        }
        else
        {
            mtCOVERAGE_TEST_MARKER();
        }

        return xShouldDelay;
    }
#undef uxSchedulerSuspended

/* Task resume from the same pinned kernel tasks.c. */
extern List_t xPendingReadyList;
#define taskYIELD_IF_USING_PREEMPTION() portYIELD_WITHIN_API()
static BaseType_t prvTaskIsTaskSuspended( const TaskHandle_t xTask )
    {
        BaseType_t xReturn = pdFALSE;
        const TCB_t * const pxTCB = xTask;

        /* Accesses xPendingReadyList so must be called from a critical
         * section. */

        /* It does not make sense to check if the calling task is suspended. */
        configASSERT( xTask );

        /* Is the task being resumed actually in the suspended list? */
        if( listIS_CONTAINED_WITHIN( &xSuspendedTaskList, &( pxTCB->xStateListItem ) ) != pdFALSE )
        {
            /* Has the task already been resumed from within an ISR? */
            if( listIS_CONTAINED_WITHIN( &xPendingReadyList, &( pxTCB->xEventListItem ) ) == pdFALSE )
            {
                /* Is it in the suspended list because it is in the Suspended
                 * state, or because is is blocked with no timeout? */
                if( listIS_CONTAINED_WITHIN( NULL, &( pxTCB->xEventListItem ) ) != pdFALSE ) /*lint !e961.  The cast is only redundant when NULL is used. */
                {
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
void vTaskResume( TaskHandle_t xTaskToResume )
    {
        TCB_t * const pxTCB = xTaskToResume;

        /* It does not make sense to resume the calling task. */
        configASSERT( xTaskToResume );

        /* The parameter cannot be NULL as it is impossible to resume the
         * currently executing task. */
        if( ( pxTCB != pxCurrentTCB ) && ( pxTCB != NULL ) )
        {
            taskENTER_CRITICAL();
            {
                if( prvTaskIsTaskSuspended( pxTCB ) != pdFALSE )
                {
                    traceTASK_RESUME( pxTCB );

                    /* The ready list can be accessed even if the scheduler is
                     * suspended because this is inside a critical section. */
                    ( void ) uxListRemove( &( pxTCB->xStateListItem ) );
                    prvAddTaskToReadyList( pxTCB );

                    /* A higher priority task may have just been resumed. */
                    if( pxTCB->uxPriority >= pxCurrentTCB->uxPriority )
                    {
                        /* This yield may not cause the task just resumed to run,
                         * but will leave the lists in the correct state for the
                         * next yield. */
                        taskYIELD_IF_USING_PREEMPTION();
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
            taskEXIT_CRITICAL();
        }
        else
        {
            mtCOVERAGE_TEST_MARKER();
        }
    }
#undef taskYIELD_IF_USING_PREEMPTION
