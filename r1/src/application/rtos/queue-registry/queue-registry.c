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
#include "FreeRTOS.h"
#include "queue.h"

/* Queue registry from the same pinned kernel queue.c. */
    typedef struct QUEUE_REGISTRY_ITEM
    {
        const char * pcQueueName; /*lint !e971 Unqualified char types are allowed for strings and single characters only. */
        QueueHandle_t xHandle;
    } xQueueRegistryItem;

/* The old xQueueRegistryItem name is maintained above then typedefed to the
 * new xQueueRegistryItem name below to enable the use of older kernel aware
 * debuggers. */
    typedef xQueueRegistryItem QueueRegistryItem_t;

/* The queue registry is simply an array of QueueRegistryItem_t structures.
 * The pcQueueName member of a structure being NULL is indicative of the
 * array position being vacant. */
    PRIVILEGED_DATA QueueRegistryItem_t xQueueRegistry[ configQUEUE_REGISTRY_SIZE ];


_Static_assert(configQUEUE_REGISTRY_SIZE==2 && sizeof(QueueRegistryItem_t)==8,"configured registry extent");
void vQueueAddToRegistry( QueueHandle_t xQueue,
                              const char * pcQueueName ) /*lint !e971 Unqualified char types are allowed for strings and single characters only. */
    {
        UBaseType_t ux;
        QueueRegistryItem_t * pxEntryToWrite = NULL;

        configASSERT( xQueue );

        if( pcQueueName != NULL )
        {
            /* See if there is an empty space in the registry.  A NULL name denotes
             * a free slot. */
            for( ux = ( UBaseType_t ) 0U; ux < ( UBaseType_t ) configQUEUE_REGISTRY_SIZE; ux++ )
            {
                /* Replace an existing entry if the queue is already in the registry. */
                if( xQueue == xQueueRegistry[ ux ].xHandle )
                {
                    pxEntryToWrite = &( xQueueRegistry[ ux ] );
                    break;
                }
                /* Otherwise, store in the next empty location */
                else if( ( pxEntryToWrite == NULL ) && ( xQueueRegistry[ ux ].pcQueueName == NULL ) )
                {
                    pxEntryToWrite = &( xQueueRegistry[ ux ] );
                }
                else
                {
                    mtCOVERAGE_TEST_MARKER();
                }
            }
        }

        if( pxEntryToWrite != NULL )
        {
            /* Store the information on this queue. */
            pxEntryToWrite->pcQueueName = pcQueueName;
            pxEntryToWrite->xHandle = xQueue;

            traceQUEUE_REGISTRY_ADD( xQueue, pcQueueName );
        }
    }
const char * pcQueueGetName( QueueHandle_t xQueue ) /*lint !e971 Unqualified char types are allowed for strings and single characters only. */
    {
        UBaseType_t ux;
        const char * pcReturn = NULL; /*lint !e971 Unqualified char types are allowed for strings and single characters only. */

        configASSERT( xQueue );

        /* Note there is nothing here to protect against another task adding or
         * removing entries from the registry while it is being searched. */

        for( ux = ( UBaseType_t ) 0U; ux < ( UBaseType_t ) configQUEUE_REGISTRY_SIZE; ux++ )
        {
            if( xQueueRegistry[ ux ].xHandle == xQueue )
            {
                pcReturn = xQueueRegistry[ ux ].pcQueueName;
                break;
            }
            else
            {
                mtCOVERAGE_TEST_MARKER();
            }
        }

        return pcReturn;
    }
void vQueueUnregisterQueue( QueueHandle_t xQueue )
    {
        UBaseType_t ux;

        configASSERT( xQueue );

        /* See if the handle of the queue being unregistered in actually in the
         * registry. */
        for( ux = ( UBaseType_t ) 0U; ux < ( UBaseType_t ) configQUEUE_REGISTRY_SIZE; ux++ )
        {
            if( xQueueRegistry[ ux ].xHandle == xQueue )
            {
                /* Set the name to NULL to show that this slot if free again. */
                xQueueRegistry[ ux ].pcQueueName = NULL;

                /* Set the handle to NULL to ensure the same queue handle cannot
                 * appear in the registry twice if it is added, removed, then
                 * added again. */
                xQueueRegistry[ ux ].xHandle = ( QueueHandle_t ) 0;
                break;
            }
            else
            {
                mtCOVERAGE_TEST_MARKER();
            }
        }
    }
