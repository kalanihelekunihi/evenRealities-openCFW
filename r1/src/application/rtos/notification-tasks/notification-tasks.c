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
#include "notification_task_contract.h"
    #define taskYIELD_IF_USING_PREEMPTION()    portYIELD_WITHIN_API()

#define taskNOTIFICATION_RECEIVED                 ( ( uint8_t ) 2 )

#define taskWAITING_NOTIFICATION                  ( ( uint8_t ) 1 )

#define taskNOT_WAITING_NOTIFICATION              ( ( uint8_t ) 0 ) /* Must be zero as it is the initialised value. */

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

    BaseType_t xTaskGenericNotify( TaskHandle_t xTaskToNotify,
                                   UBaseType_t uxIndexToNotify,
                                   uint32_t ulValue,
                                   eNotifyAction eAction,
                                   uint32_t * pulPreviousNotificationValue )
    {
        TCB_t * pxTCB;
        BaseType_t xReturn = pdPASS;
        uint8_t ucOriginalNotifyState;

        configASSERT( uxIndexToNotify < configTASK_NOTIFICATION_ARRAY_ENTRIES );
        configASSERT( xTaskToNotify );
        pxTCB = xTaskToNotify;

        taskENTER_CRITICAL();
        {
            if( pulPreviousNotificationValue != NULL )
            {
                *pulPreviousNotificationValue = pxTCB->ulNotifiedValue[ uxIndexToNotify ];
            }

            ucOriginalNotifyState = pxTCB->ucNotifyState[ uxIndexToNotify ];

            pxTCB->ucNotifyState[ uxIndexToNotify ] = taskNOTIFICATION_RECEIVED;

            switch( eAction )
            {
                case eSetBits:
                    pxTCB->ulNotifiedValue[ uxIndexToNotify ] |= ulValue;
                    break;

                case eIncrement:
                    ( pxTCB->ulNotifiedValue[ uxIndexToNotify ] )++;
                    break;

                case eSetValueWithOverwrite:
                    pxTCB->ulNotifiedValue[ uxIndexToNotify ] = ulValue;
                    break;

                case eSetValueWithoutOverwrite:

                    if( ucOriginalNotifyState != taskNOTIFICATION_RECEIVED )
                    {
                        pxTCB->ulNotifiedValue[ uxIndexToNotify ] = ulValue;
                    }
                    else
                    {
                        /* The value could not be written to the task. */
                        xReturn = pdFAIL;
                    }

                    break;

                case eNoAction:

                    /* The task is being notified without its notify value being
                     * updated. */
                    break;

                default:

                    /* Should not get here if all enums are handled.
                     * Artificially force an assert by testing a value the
                     * compiler can't assume is const. */
                    configASSERT( xTickCount == ( TickType_t ) 0 );

                    break;
            }

            traceTASK_NOTIFY( uxIndexToNotify );

            /* If the task is in the blocked state specifically to wait for a
             * notification then unblock it now. */
            if( ucOriginalNotifyState == taskWAITING_NOTIFICATION )
            {
                listREMOVE_ITEM( &( pxTCB->xStateListItem ) );
                prvAddTaskToReadyList( pxTCB );

                /* The task should not have been on an event list. */
                configASSERT( listLIST_ITEM_CONTAINER( &( pxTCB->xEventListItem ) ) == NULL );

                #if ( configUSE_TICKLESS_IDLE != 0 )
                {
                    /* If a task is blocked waiting for a notification then
                     * xNextTaskUnblockTime might be set to the blocked task's time
                     * out time.  If the task is unblocked for a reason other than
                     * a timeout xNextTaskUnblockTime is normally left unchanged,
                     * because it will automatically get reset to a new value when
                     * the tick count equals xNextTaskUnblockTime.  However if
                     * tickless idling is used it might be more important to enter
                     * sleep mode at the earliest possible time - so reset
                     * xNextTaskUnblockTime here to ensure it is updated at the
                     * earliest possible time. */
                    prvResetNextTaskUnblockTime();
                }
                #endif

                if( pxTCB->uxPriority > pxCurrentTCB->uxPriority )
                {
                    /* The notified task has a priority above the currently
                     * executing task so a yield is required. */
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

        return xReturn;
    }

    BaseType_t xTaskGenericNotifyFromISR( TaskHandle_t xTaskToNotify,
                                          UBaseType_t uxIndexToNotify,
                                          uint32_t ulValue,
                                          eNotifyAction eAction,
                                          uint32_t * pulPreviousNotificationValue,
                                          BaseType_t * pxHigherPriorityTaskWoken )
    {
        TCB_t * pxTCB;
        uint8_t ucOriginalNotifyState;
        BaseType_t xReturn = pdPASS;
        UBaseType_t uxSavedInterruptStatus;

        configASSERT( xTaskToNotify );
        configASSERT( uxIndexToNotify < configTASK_NOTIFICATION_ARRAY_ENTRIES );

        /* RTOS ports that support interrupt nesting have the concept of a
         * maximum  system call (or maximum API call) interrupt priority.
         * Interrupts that are  above the maximum system call priority are keep
         * permanently enabled, even when the RTOS kernel is in a critical section,
         * but cannot make any calls to FreeRTOS API functions.  If configASSERT()
         * is defined in FreeRTOSConfig.h then
         * portASSERT_IF_INTERRUPT_PRIORITY_INVALID() will result in an assertion
         * failure if a FreeRTOS API function is called from an interrupt that has
         * been assigned a priority above the configured maximum system call
         * priority.  Only FreeRTOS functions that end in FromISR can be called
         * from interrupts  that have been assigned a priority at or (logically)
         * below the maximum system call interrupt priority.  FreeRTOS maintains a
         * separate interrupt safe API to ensure interrupt entry is as fast and as
         * simple as possible.  More information (albeit Cortex-M specific) is
         * provided on the following link:
         * https://www.FreeRTOS.org/RTOS-Cortex-M3-M4.html */
        portASSERT_IF_INTERRUPT_PRIORITY_INVALID();

        pxTCB = xTaskToNotify;

        uxSavedInterruptStatus = portSET_INTERRUPT_MASK_FROM_ISR();
        {
            if( pulPreviousNotificationValue != NULL )
            {
                *pulPreviousNotificationValue = pxTCB->ulNotifiedValue[ uxIndexToNotify ];
            }

            ucOriginalNotifyState = pxTCB->ucNotifyState[ uxIndexToNotify ];
            pxTCB->ucNotifyState[ uxIndexToNotify ] = taskNOTIFICATION_RECEIVED;

            switch( eAction )
            {
                case eSetBits:
                    pxTCB->ulNotifiedValue[ uxIndexToNotify ] |= ulValue;
                    break;

                case eIncrement:
                    ( pxTCB->ulNotifiedValue[ uxIndexToNotify ] )++;
                    break;

                case eSetValueWithOverwrite:
                    pxTCB->ulNotifiedValue[ uxIndexToNotify ] = ulValue;
                    break;

                case eSetValueWithoutOverwrite:

                    if( ucOriginalNotifyState != taskNOTIFICATION_RECEIVED )
                    {
                        pxTCB->ulNotifiedValue[ uxIndexToNotify ] = ulValue;
                    }
                    else
                    {
                        /* The value could not be written to the task. */
                        xReturn = pdFAIL;
                    }

                    break;

                case eNoAction:

                    /* The task is being notified without its notify value being
                     * updated. */
                    break;

                default:

                    /* Should not get here if all enums are handled.
                     * Artificially force an assert by testing a value the
                     * compiler can't assume is const. */
                    configASSERT( xTickCount == ( TickType_t ) 0 );
                    break;
            }

            traceTASK_NOTIFY_FROM_ISR( uxIndexToNotify );

            /* If the task is in the blocked state specifically to wait for a
             * notification then unblock it now. */
            if( ucOriginalNotifyState == taskWAITING_NOTIFICATION )
            {
                /* The task should not have been on an event list. */
                configASSERT( listLIST_ITEM_CONTAINER( &( pxTCB->xEventListItem ) ) == NULL );

                if( uxSchedulerSuspended == ( UBaseType_t ) pdFALSE )
                {
                    listREMOVE_ITEM( &( pxTCB->xStateListItem ) );
                    prvAddTaskToReadyList( pxTCB );
                }
                else
                {
                    /* The delayed and ready lists cannot be accessed, so hold
                     * this task pending until the scheduler is resumed. */
                    listINSERT_END( &( xPendingReadyList ), &( pxTCB->xEventListItem ) );
                }

                if( pxTCB->uxPriority > pxCurrentTCB->uxPriority )
                {
                    /* The notified task has a priority above the currently
                     * executing task so a yield is required. */
                    if( pxHigherPriorityTaskWoken != NULL )
                    {
                        *pxHigherPriorityTaskWoken = pdTRUE;
                    }

                    /* Mark that a yield is pending in case the user is not
                     * using the "xHigherPriorityTaskWoken" parameter to an ISR
                     * safe FreeRTOS function. */
                    xYieldPending = pdTRUE;
                }
                else
                {
                    mtCOVERAGE_TEST_MARKER();
                }
            }
        }
        portCLEAR_INTERRUPT_MASK_FROM_ISR( uxSavedInterruptStatus );

        return xReturn;
    }

    BaseType_t xTaskGenericNotifyWait( UBaseType_t uxIndexToWait,
                                       uint32_t ulBitsToClearOnEntry,
                                       uint32_t ulBitsToClearOnExit,
                                       uint32_t * pulNotificationValue,
                                       TickType_t xTicksToWait )
    {
        BaseType_t xReturn;

        configASSERT( uxIndexToWait < configTASK_NOTIFICATION_ARRAY_ENTRIES );

        taskENTER_CRITICAL();
        {
            /* Only block if a notification is not already pending. */
            if( pxCurrentTCB->ucNotifyState[ uxIndexToWait ] != taskNOTIFICATION_RECEIVED )
            {
                /* Clear bits in the task's notification value as bits may get
                 * set  by the notifying task or interrupt.  This can be used to
                 * clear the value to zero. */
                pxCurrentTCB->ulNotifiedValue[ uxIndexToWait ] &= ~ulBitsToClearOnEntry;

                /* Mark this task as waiting for a notification. */
                pxCurrentTCB->ucNotifyState[ uxIndexToWait ] = taskWAITING_NOTIFICATION;

                if( xTicksToWait > ( TickType_t ) 0 )
                {
                    prvAddCurrentTaskToDelayedList( xTicksToWait, pdTRUE );
                    traceTASK_NOTIFY_WAIT_BLOCK( uxIndexToWait );

                    /* All ports are written to allow a yield in a critical
                     * section (some will yield immediately, others wait until the
                     * critical section exits) - but it is not something that
                     * application code should ever do. */
                    portYIELD_WITHIN_API();
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

        taskENTER_CRITICAL();
        {
            traceTASK_NOTIFY_WAIT( uxIndexToWait );

            if( pulNotificationValue != NULL )
            {
                /* Output the current notification value, which may or may not
                 * have changed. */
                *pulNotificationValue = pxCurrentTCB->ulNotifiedValue[ uxIndexToWait ];
            }

            /* If ucNotifyValue is set then either the task never entered the
             * blocked state (because a notification was already pending) or the
             * task unblocked because of a notification.  Otherwise the task
             * unblocked because of a timeout. */
            if( pxCurrentTCB->ucNotifyState[ uxIndexToWait ] != taskNOTIFICATION_RECEIVED )
            {
                /* A notification was not received. */
                xReturn = pdFALSE;
            }
            else
            {
                /* A notification was already pending or a notification was
                 * received while the task was waiting. */
                pxCurrentTCB->ulNotifiedValue[ uxIndexToWait ] &= ~ulBitsToClearOnExit;
                xReturn = pdTRUE;
            }

            pxCurrentTCB->ucNotifyState[ uxIndexToWait ] = taskNOT_WAITING_NOTIFICATION;
        }
        taskEXIT_CRITICAL();

        return xReturn;
    }

    void vTaskDelay( const TickType_t xTicksToDelay )
    {
        BaseType_t xAlreadyYielded = pdFALSE;

        /* A delay time of zero just forces a reschedule. */
        if( xTicksToDelay > ( TickType_t ) 0U )
        {
            configASSERT( uxSchedulerSuspended == 0 );
            vTaskSuspendAll();
            {
                traceTASK_DELAY();

                /* A task that is removed from the event list while the
                 * scheduler is suspended will not get placed in the ready
                 * list or removed from the blocked list until the scheduler
                 * is resumed.
                 *
                 * This task cannot be in an event list as it is the currently
                 * executing task. */
                prvAddCurrentTaskToDelayedList( xTicksToDelay, pdFALSE );
            }
            xAlreadyYielded = xTaskResumeAll();
        }
        else
        {
            mtCOVERAGE_TEST_MARKER();
        }

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
