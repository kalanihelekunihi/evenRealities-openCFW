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
#include "compat.h"
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

    void vTaskPriorityDisinheritAfterTimeout( TaskHandle_t const pxMutexHolder,
                                              UBaseType_t uxHighestPriorityWaitingTask )
    {
        TCB_t * const pxTCB = pxMutexHolder;
        UBaseType_t uxPriorityUsedOnEntry, uxPriorityToUse;
        const UBaseType_t uxOnlyOneMutexHeld = ( UBaseType_t ) 1;

        if( pxMutexHolder != NULL )
        {
            /* If pxMutexHolder is not NULL then the holder must hold at least
             * one mutex. */
            configASSERT( pxTCB->uxMutexesHeld );

            /* Determine the priority to which the priority of the task that
             * holds the mutex should be set.  This will be the greater of the
             * holding task's base priority and the priority of the highest
             * priority task that is waiting to obtain the mutex. */
            if( pxTCB->uxBasePriority < uxHighestPriorityWaitingTask )
            {
                uxPriorityToUse = uxHighestPriorityWaitingTask;
            }
            else
            {
                uxPriorityToUse = pxTCB->uxBasePriority;
            }

            /* Does the priority need to change? */
            if( pxTCB->uxPriority != uxPriorityToUse )
            {
                /* Only disinherit if no other mutexes are held.  This is a
                 * simplification in the priority inheritance implementation.  If
                 * the task that holds the mutex is also holding other mutexes then
                 * the other mutexes may have caused the priority inheritance. */
                if( pxTCB->uxMutexesHeld == uxOnlyOneMutexHeld )
                {
                    /* If a task has timed out because it already holds the
                     * mutex it was trying to obtain then it cannot of inherited
                     * its own priority. */
                    configASSERT( pxTCB != pxCurrentTCB );

                    /* Disinherit the priority, remembering the previous
                     * priority to facilitate determining the subject task's
                     * state. */
                    traceTASK_PRIORITY_DISINHERIT( pxTCB, uxPriorityToUse );
                    uxPriorityUsedOnEntry = pxTCB->uxPriority;
                    pxTCB->uxPriority = uxPriorityToUse;

                    /* Only reset the event list item value if the value is not
                     * being used for anything else. */
                    if( ( listGET_LIST_ITEM_VALUE( &( pxTCB->xEventListItem ) ) & taskEVENT_LIST_ITEM_VALUE_IN_USE ) == 0UL )
                    {
                        listSET_LIST_ITEM_VALUE( &( pxTCB->xEventListItem ), ( TickType_t ) configMAX_PRIORITIES - ( TickType_t ) uxPriorityToUse ); /*lint !e961 MISRA exception as the casts are only redundant for some ports. */
                    }
                    else
                    {
                        mtCOVERAGE_TEST_MARKER();
                    }

                    /* If the running task is not the task that holds the mutex
                     * then the task that holds the mutex could be in either the
                     * Ready, Blocked or Suspended states.  Only remove the task
                     * from its current state list if it is in the Ready state as
                     * the task's priority is going to change and there is one
                     * Ready list per priority. */
                    if( listIS_CONTAINED_WITHIN( &( pxReadyTasksLists[ uxPriorityUsedOnEntry ] ), &( pxTCB->xStateListItem ) ) != pdFALSE )
                    {
                        if( uxListRemove( &( pxTCB->xStateListItem ) ) == ( UBaseType_t ) 0 )
                        {
                            /* It is known that the task is in its ready list so
                             * there is no need to check again and the port level
                             * reset macro can be called directly. */
                            portRESET_READY_PRIORITY( pxTCB->uxPriority, uxTopReadyPriority );
                        }
                        else
                        {
                            mtCOVERAGE_TEST_MARKER();
                        }

                        prvAddTaskToReadyList( pxTCB );
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
        }
        else
        {
            mtCOVERAGE_TEST_MARKER();
        }
    }

    BaseType_t xTaskPriorityInherit( TaskHandle_t const pxMutexHolder )
    {
        TCB_t * const pxMutexHolderTCB = pxMutexHolder;
        BaseType_t xReturn = pdFALSE;

        /* If the mutex was given back by an interrupt while the queue was
         * locked then the mutex holder might now be NULL.  _RB_ Is this still
         * needed as interrupts can no longer use mutexes? */
        if( pxMutexHolder != NULL )
        {
            /* If the holder of the mutex has a priority below the priority of
             * the task attempting to obtain the mutex then it will temporarily
             * inherit the priority of the task attempting to obtain the mutex. */
            if( pxMutexHolderTCB->uxPriority < pxCurrentTCB->uxPriority )
            {
                /* Adjust the mutex holder state to account for its new
                 * priority.  Only reset the event list item value if the value is
                 * not being used for anything else. */
                if( ( listGET_LIST_ITEM_VALUE( &( pxMutexHolderTCB->xEventListItem ) ) & taskEVENT_LIST_ITEM_VALUE_IN_USE ) == 0UL )
                {
                    listSET_LIST_ITEM_VALUE( &( pxMutexHolderTCB->xEventListItem ), ( TickType_t ) configMAX_PRIORITIES - ( TickType_t ) pxCurrentTCB->uxPriority ); /*lint !e961 MISRA exception as the casts are only redundant for some ports. */
                }
                else
                {
                    mtCOVERAGE_TEST_MARKER();
                }

                /* If the task being modified is in the ready state it will need
                 * to be moved into a new list. */
                if( listIS_CONTAINED_WITHIN( &( pxReadyTasksLists[ pxMutexHolderTCB->uxPriority ] ), &( pxMutexHolderTCB->xStateListItem ) ) != pdFALSE )
                {
                    if( uxListRemove( &( pxMutexHolderTCB->xStateListItem ) ) == ( UBaseType_t ) 0 )
                    {
                        /* It is known that the task is in its ready list so
                         * there is no need to check again and the port level
                         * reset macro can be called directly. */
                        portRESET_READY_PRIORITY( pxMutexHolderTCB->uxPriority, uxTopReadyPriority );
                    }
                    else
                    {
                        mtCOVERAGE_TEST_MARKER();
                    }

                    /* Inherit the priority before being moved into the new list. */
                    pxMutexHolderTCB->uxPriority = pxCurrentTCB->uxPriority;
                    prvAddTaskToReadyList( pxMutexHolderTCB );
                }
                else
                {
                    /* Just inherit the priority. */
                    pxMutexHolderTCB->uxPriority = pxCurrentTCB->uxPriority;
                }

                traceTASK_PRIORITY_INHERIT( pxMutexHolderTCB, pxCurrentTCB->uxPriority );

                /* Inheritance occurred. */
                xReturn = pdTRUE;
            }
            else
            {
                if( pxMutexHolderTCB->uxBasePriority < pxCurrentTCB->uxPriority )
                {
                    /* The base priority of the mutex holder is lower than the
                     * priority of the task attempting to take the mutex, but the
                     * current priority of the mutex holder is not lower than the
                     * priority of the task attempting to take the mutex.
                     * Therefore the mutex holder must have already inherited a
                     * priority, but inheritance would have occurred if that had
                     * not been the case. */
                    xReturn = pdTRUE;
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

        return xReturn;
    }
