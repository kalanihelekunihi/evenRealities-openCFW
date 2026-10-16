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
#include "startup_timer_contract.h"
    typedef struct tmrTimerParameters
    {
        TickType_t xMessageValue; /*<< An optional value used by a subset of commands, for example, when changing the period of a timer. */
        Timer_t * pxTimer;        /*<< The timer to which the command will be applied. */
    } TimerParameter_t;


    typedef struct tmrCallbackParameters
    {
        PendedFunction_t pxCallbackFunction; /* << The callback function to execute. */
        void * pvParameter1;                 /* << The value that will be used as the callback functions first parameter. */
        uint32_t ulParameter2;               /* << The value that will be used as the callback functions second parameter. */
    } CallbackParameters_t;

/* The structure that contains the two message types, along with an identifier
 * that is used to determine which message type is valid. */
    typedef struct tmrTimerQueueMessage
    {
        BaseType_t xMessageID; /*<< The command being sent to the timer service task. */
        union
        {
            TimerParameter_t xTimerParameters;

            /* Don't include xCallbackParameters if it is not going to be used as
             * it makes the structure (and therefore the timer queue) larger. */
            #if ( INCLUDE_xTimerPendFunctionCall == 1 )
                CallbackParameters_t xCallbackParameters;
            #endif /* INCLUDE_xTimerPendFunctionCall */
        } u;
    } DaemonTaskMessage_t;
    static void prvCheckForValidListAndQueue( void )
    {
        /* Check that the list from which active timers are referenced, and the
         * queue used to communicate with the timer service, have been
         * initialised. */
        taskENTER_CRITICAL();
        {
            if( xTimerQueue == NULL )
            {
                vListInitialise( &xActiveTimerList1 );
                vListInitialise( &xActiveTimerList2 );
                pxCurrentTimerList = &xActiveTimerList1;
                pxOverflowTimerList = &xActiveTimerList2;

                #if ( configSUPPORT_STATIC_ALLOCATION == 1 )
                {
                    /* The timer queue is allocated statically in case
                     * configSUPPORT_DYNAMIC_ALLOCATION is 0. */
                    PRIVILEGED_DATA static StaticQueue_t xStaticTimerQueue;                                                                          /*lint !e956 Ok to declare in this manner to prevent additional conditional compilation guards in other locations. */
                    PRIVILEGED_DATA static uint8_t ucStaticTimerQueueStorage[ ( size_t ) configTIMER_QUEUE_LENGTH * sizeof( DaemonTaskMessage_t ) ]; /*lint !e956 Ok to declare in this manner to prevent additional conditional compilation guards in other locations. */

                    xTimerQueue = xQueueCreateStatic( ( UBaseType_t ) configTIMER_QUEUE_LENGTH, ( UBaseType_t ) sizeof( DaemonTaskMessage_t ), &( ucStaticTimerQueueStorage[ 0 ] ), &xStaticTimerQueue );
                }
                #else
                {
                    xTimerQueue = xQueueCreate( ( UBaseType_t ) configTIMER_QUEUE_LENGTH, sizeof( DaemonTaskMessage_t ) );
                }
                #endif /* if ( configSUPPORT_STATIC_ALLOCATION == 1 ) */

                #if ( configQUEUE_REGISTRY_SIZE > 0 )
                {
                    if( xTimerQueue != NULL )
                    {
                        vQueueAddToRegistry( xTimerQueue, "TmrQ" );
                    }
                    else
                    {
                        mtCOVERAGE_TEST_MARKER();
                    }
                }
                #endif /* configQUEUE_REGISTRY_SIZE */
            }
            else
            {
                mtCOVERAGE_TEST_MARKER();
            }
        }
        taskEXIT_CRITICAL();
    }
    BaseType_t xTimerCreateTimerTask( void )
    {
        BaseType_t xReturn = pdFAIL;

        /* This function is called when the scheduler is started if
         * configUSE_TIMERS is set to 1.  Check that the infrastructure used by the
         * timer service task has been created/initialised.  If timers have already
         * been created then the initialisation will already have been performed. */
        prvCheckForValidListAndQueue();

        if( xTimerQueue != NULL )
        {
            #if ( configSUPPORT_STATIC_ALLOCATION == 1 )
            {
                StaticTask_t * pxTimerTaskTCBBuffer = NULL;
                StackType_t * pxTimerTaskStackBuffer = NULL;
                uint32_t ulTimerTaskStackSize;

                vApplicationGetTimerTaskMemory( &pxTimerTaskTCBBuffer, &pxTimerTaskStackBuffer, &ulTimerTaskStackSize );
                xTimerTaskHandle = xTaskCreateStatic( prvTimerTask,
                                                      configTIMER_SERVICE_TASK_NAME,
                                                      ulTimerTaskStackSize,
                                                      NULL,
                                                      ( ( UBaseType_t ) configTIMER_TASK_PRIORITY ) | portPRIVILEGE_BIT,
                                                      pxTimerTaskStackBuffer,
                                                      pxTimerTaskTCBBuffer );

                if( xTimerTaskHandle != NULL )
                {
                    xReturn = pdPASS;
                }
            }
            #else /* if ( configSUPPORT_STATIC_ALLOCATION == 1 ) */
            {
                xReturn = xTaskCreate( prvTimerTask,
                                       configTIMER_SERVICE_TASK_NAME,
                                       configTIMER_TASK_STACK_DEPTH,
                                       NULL,
                                       ( ( UBaseType_t ) configTIMER_TASK_PRIORITY ) | portPRIVILEGE_BIT,
                                       &xTimerTaskHandle );
            }
            #endif /* configSUPPORT_STATIC_ALLOCATION */
        }
        else
        {
            mtCOVERAGE_TEST_MARKER();
        }

        configASSERT( xReturn );
        return xReturn;
    }
void r1_native_timer_infrastructure(void) __attribute__((alias("prvCheckForValidListAndQueue")));
_Static_assert(sizeof(DaemonTaskMessage_t)==16,"native timer queue message");
