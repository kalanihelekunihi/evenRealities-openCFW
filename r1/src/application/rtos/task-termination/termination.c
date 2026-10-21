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
#include "task_termination_contract.h"
#define prvGetTCBFromHandle( pxHandle )    ( ( ( pxHandle ) == NULL ) ? pxCurrentTCB : ( pxHandle ) )

    #define taskRESET_READY_PRIORITY( uxPriority )

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

    static void prvDeleteTCB( TCB_t * pxTCB )
    {
        /* This call is required specifically for the TriCore port.  It must be
         * above the vPortFree() calls.  The call is also used by ports/demos that
         * want to allocate and clean RAM statically. */
        portCLEAN_UP_TCB( pxTCB );

        #if ( ( configUSE_NEWLIB_REENTRANT == 1 ) || ( configUSE_C_RUNTIME_TLS_SUPPORT == 1 ) )
        {
            /* Free up the memory allocated for the task's TLS Block. */
            configDEINIT_TLS_BLOCK( pxCurrentTCB->xTLSBlock );
        }
        #endif

        #if ( ( configSUPPORT_DYNAMIC_ALLOCATION == 1 ) && ( configSUPPORT_STATIC_ALLOCATION == 0 ) && ( portUSING_MPU_WRAPPERS == 0 ) )
        {
            /* The task can only have been allocated dynamically - free both
             * the stack and TCB. */
            vPortFreeStack( pxTCB->pxStack );
            vPortFree( pxTCB );
        }
        #elif ( tskSTATIC_AND_DYNAMIC_ALLOCATION_POSSIBLE != 0 ) /*lint !e731 !e9029 Macro has been consolidated for readability reasons. */
        {
            /* The task could have been allocated statically or dynamically, so
             * check what was statically allocated before trying to free the
             * memory. */
            if( pxTCB->ucStaticallyAllocated == tskDYNAMICALLY_ALLOCATED_STACK_AND_TCB )
            {
                /* Both the stack and TCB were allocated dynamically, so both
                 * must be freed. */
                vPortFreeStack( pxTCB->pxStack );
                vPortFree( pxTCB );
            }
            else if( pxTCB->ucStaticallyAllocated == tskSTATICALLY_ALLOCATED_STACK_ONLY )
            {
                /* Only the stack was statically allocated, so the TCB is the
                 * only memory that must be freed. */
                vPortFree( pxTCB );
            }
            else
            {
                /* Neither the stack nor the TCB were allocated dynamically, so
                 * nothing needs to be freed. */
                configASSERT( pxTCB->ucStaticallyAllocated == tskSTATICALLY_ALLOCATED_STACK_AND_TCB );
                mtCOVERAGE_TEST_MARKER();
            }
        }
        #endif /* configSUPPORT_DYNAMIC_ALLOCATION */
    }

    void vTaskDelete( TaskHandle_t xTaskToDelete )
    {
        TCB_t * pxTCB;

        taskENTER_CRITICAL();
        {
            /* If null is passed in here then it is the calling task that is
             * being deleted. */
            pxTCB = prvGetTCBFromHandle( xTaskToDelete );

            /* Remove task from the ready/delayed list. */
            if( uxListRemove( &( pxTCB->xStateListItem ) ) == ( UBaseType_t ) 0 )
            {
                taskRESET_READY_PRIORITY( pxTCB->uxPriority );
            }
            else
            {
                mtCOVERAGE_TEST_MARKER();
            }

            /* Is the task waiting on an event also? */
            if( listLIST_ITEM_CONTAINER( &( pxTCB->xEventListItem ) ) != NULL )
            {
                ( void ) uxListRemove( &( pxTCB->xEventListItem ) );
            }
            else
            {
                mtCOVERAGE_TEST_MARKER();
            }

            /* Increment the uxTaskNumber also so kernel aware debuggers can
             * detect that the task lists need re-generating.  This is done before
             * portPRE_TASK_DELETE_HOOK() as in the Windows port that macro will
             * not return. */
            uxTaskNumber++;

            if( pxTCB == pxCurrentTCB )
            {
                /* A task is deleting itself.  This cannot complete within the
                 * task itself, as a context switch to another task is required.
                 * Place the task in the termination list.  The idle task will
                 * check the termination list and free up any memory allocated by
                 * the scheduler for the TCB and stack of the deleted task. */
                vListInsertEnd( &xTasksWaitingTermination, &( pxTCB->xStateListItem ) );

                /* Increment the ucTasksDeleted variable so the idle task knows
                 * there is a task that has been deleted and that it should therefore
                 * check the xTasksWaitingTermination list. */
                ++uxDeletedTasksWaitingCleanUp;

                /* Call the delete hook before portPRE_TASK_DELETE_HOOK() as
                 * portPRE_TASK_DELETE_HOOK() does not return in the Win32 port. */
                traceTASK_DELETE( pxTCB );

                /* The pre-delete hook is primarily for the Windows simulator,
                 * in which Windows specific clean up operations are performed,
                 * after which it is not possible to yield away from this task -
                 * hence xYieldPending is used to latch that a context switch is
                 * required. */
                portPRE_TASK_DELETE_HOOK( pxTCB, &xYieldPending );
            }
            else
            {
                --uxCurrentNumberOfTasks;
                traceTASK_DELETE( pxTCB );

                /* Reset the next expected unblock time in case it referred to
                 * the task that has just been deleted. */
                prvResetNextTaskUnblockTime();
            }
        }
        taskEXIT_CRITICAL();

        /* If the task is not deleting itself, call prvDeleteTCB from outside of
         * critical section. If a task deletes itself, prvDeleteTCB is called
         * from prvCheckTasksWaitingTermination which is called from Idle task. */
        if( pxTCB != pxCurrentTCB )
        {
            prvDeleteTCB( pxTCB );
        }

        /* Force a reschedule if it is the currently running task that has just
         * been deleted. */
        if( xSchedulerRunning != pdFALSE )
        {
            if( pxTCB == pxCurrentTCB )
            {
                configASSERT( uxSchedulerSuspended == 0 );
                portYIELD_WITHIN_API();
            }
            else
            {
                mtCOVERAGE_TEST_MARKER();
            }
        }
    }

    eTaskState eTaskGetState( TaskHandle_t xTask )
    {
        eTaskState eReturn;
        List_t const * pxStateList;
        List_t const * pxDelayedList;
        List_t const * pxOverflowedDelayedList;
        const TCB_t * const pxTCB = xTask;

        configASSERT( pxTCB );

        if( pxTCB == pxCurrentTCB )
        {
            /* The task calling this function is querying its own state. */
            eReturn = eRunning;
        }
        else
        {
            taskENTER_CRITICAL();
            {
                pxStateList = listLIST_ITEM_CONTAINER( &( pxTCB->xStateListItem ) );
                pxDelayedList = pxDelayedTaskList;
                pxOverflowedDelayedList = pxOverflowDelayedTaskList;
            }
            taskEXIT_CRITICAL();

            if( ( pxStateList == pxDelayedList ) || ( pxStateList == pxOverflowedDelayedList ) )
            {
                /* The task being queried is referenced from one of the Blocked
                 * lists. */
                eReturn = eBlocked;
            }

            #if ( INCLUDE_vTaskSuspend == 1 )
                else if( pxStateList == &xSuspendedTaskList )
                {
                    /* The task being queried is referenced from the suspended
                     * list.  Is it genuinely suspended or is it blocked
                     * indefinitely? */
                    if( listLIST_ITEM_CONTAINER( &( pxTCB->xEventListItem ) ) == NULL )
                    {
                        #if ( configUSE_TASK_NOTIFICATIONS == 1 )
                        {
                            BaseType_t x;

                            /* The task does not appear on the event list item of
                             * and of the RTOS objects, but could still be in the
                             * blocked state if it is waiting on its notification
                             * rather than waiting on an object.  If not, is
                             * suspended. */
                            eReturn = eSuspended;

                            for( x = 0; x < configTASK_NOTIFICATION_ARRAY_ENTRIES; x++ )
                            {
                                if( pxTCB->ucNotifyState[ x ] == taskWAITING_NOTIFICATION )
                                {
                                    eReturn = eBlocked;
                                    break;
                                }
                            }
                        }
                        #else /* if ( configUSE_TASK_NOTIFICATIONS == 1 ) */
                        {
                            eReturn = eSuspended;
                        }
                        #endif /* if ( configUSE_TASK_NOTIFICATIONS == 1 ) */
                    }
                    else
                    {
                        eReturn = eBlocked;
                    }
                }
            #endif /* if ( INCLUDE_vTaskSuspend == 1 ) */

            #if ( INCLUDE_vTaskDelete == 1 )
                else if( ( pxStateList == &xTasksWaitingTermination ) || ( pxStateList == NULL ) )
                {
                    /* The task being queried is referenced from the deleted
                     * tasks list, or it is not referenced from any lists at
                     * all. */
                    eReturn = eDeleted;
                }
            #endif

            else /*lint !e525 Negative indentation is intended to make use of pre-processor clearer. */
            {
                /* If the task is not in any other state, it must be in the
                 * Ready (including pending ready) state. */
                eReturn = eReady;
            }
        }

        return eReturn;
    }
static void prvCheckTasksWaitingTermination( void )
{
    /** THIS FUNCTION IS CALLED FROM THE RTOS IDLE TASK **/

    #if ( INCLUDE_vTaskDelete == 1 )
    {
        TCB_t * pxTCB;

        /* uxDeletedTasksWaitingCleanUp is used to prevent taskENTER_CRITICAL()
         * being called too often in the idle task. */
        while( uxDeletedTasksWaitingCleanUp > ( UBaseType_t ) 0U )
        {
            taskENTER_CRITICAL();
            {
                pxTCB = listGET_OWNER_OF_HEAD_ENTRY( ( &xTasksWaitingTermination ) ); /*lint !e9079 void * is used as this macro is used with timers and co-routines too.  Alignment is known to be fine as the type of the pointer stored and retrieved is the same. */
                ( void ) uxListRemove( &( pxTCB->xStateListItem ) );
                --uxCurrentNumberOfTasks;
                --uxDeletedTasksWaitingCleanUp;
            }
            taskEXIT_CRITICAL();

            prvDeleteTCB( pxTCB );
        }
    }
    #endif /* INCLUDE_vTaskDelete */
}

    static TickType_t prvGetExpectedIdleTime( void )
    {
        TickType_t xReturn;
        UBaseType_t uxHigherPriorityReadyTasks = pdFALSE;

        /* uxHigherPriorityReadyTasks takes care of the case where
         * configUSE_PREEMPTION is 0, so there may be tasks above the idle priority
         * task that are in the Ready state, even though the idle task is
         * running. */
        #if ( configUSE_PORT_OPTIMISED_TASK_SELECTION == 0 )
        {
            if( uxTopReadyPriority > tskIDLE_PRIORITY )
            {
                uxHigherPriorityReadyTasks = pdTRUE;
            }
        }
        #else
        {
            const UBaseType_t uxLeastSignificantBit = ( UBaseType_t ) 0x01;

            /* When port optimised task selection is used the uxTopReadyPriority
             * variable is used as a bit map.  If bits other than the least
             * significant bit are set then there are tasks that have a priority
             * above the idle priority that are in the Ready state.  This takes
             * care of the case where the co-operative scheduler is in use. */
            if( uxTopReadyPriority > uxLeastSignificantBit )
            {
                uxHigherPriorityReadyTasks = pdTRUE;
            }
        }
        #endif /* if ( configUSE_PORT_OPTIMISED_TASK_SELECTION == 0 ) */

        if( pxCurrentTCB->uxPriority > tskIDLE_PRIORITY )
        {
            xReturn = 0;
        }
        else if( listCURRENT_LIST_LENGTH( &( pxReadyTasksLists[ tskIDLE_PRIORITY ] ) ) > 1 )
        {
            /* There are other idle priority tasks in the ready state.  If
             * time slicing is used then the very next tick interrupt must be
             * processed. */
            xReturn = 0;
        }
        else if( uxHigherPriorityReadyTasks != pdFALSE )
        {
            /* There are tasks in the Ready state that have a priority above the
             * idle priority.  This path can only be reached if
             * configUSE_PREEMPTION is 0. */
            xReturn = 0;
        }
        else
        {
            xReturn = xNextTaskUnblockTime - xTickCount;
        }

        return xReturn;
    }

void r1_native_task_reclaim(TCB_t *) __attribute__((alias("prvDeleteTCB")));
void r1_native_task_idle_cleanup(void) __attribute__((alias("prvCheckTasksWaitingTermination")));
TickType_t r1_native_expected_idle_time(void) __attribute__((alias("prvGetExpectedIdleTime")));
