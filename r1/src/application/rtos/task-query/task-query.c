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
#include "mutex_tasks_contract.h"
#define prvGetTCBFromHandle(handle) ((handle)==NULL ? pxCurrentTCB : (TCB_t *)(handle))
_Static_assert(offsetof(TCB_t,pcTaskName)==52,"native task name offset");
char * pcTaskGetName( TaskHandle_t xTaskToQuery ) /*lint !e971 Unqualified char types are allowed for strings and single characters only. */
{
    TCB_t * pxTCB;

    /* If null is passed in here then the name of the calling task is being
     * queried. */
    pxTCB = prvGetTCBFromHandle( xTaskToQuery );
    configASSERT( pxTCB );
    return &( pxTCB->pcTaskName[ 0 ] );
}
    UBaseType_t uxTaskPriorityGet( const TaskHandle_t xTask )
    {
        TCB_t const * pxTCB;
        UBaseType_t uxReturn;

        taskENTER_CRITICAL();
        {
            /* If null is passed in here then it is the priority of the task
             * that called uxTaskPriorityGet() that is being queried. */
            pxTCB = prvGetTCBFromHandle( xTask );
            uxReturn = pxTCB->uxPriority;
        }
        taskEXIT_CRITICAL();

        return uxReturn;
    }

/* Stack watermark from the same pinned kernel tasks.c. */
#define tskSTACK_FILL_BYTE 0xa5U
_Static_assert(portSTACK_GROWTH==-1 && sizeof(StackType_t)==4 && offsetof(TCB_t,pxStack)==48,"native downward stack scan");
static configSTACK_DEPTH_TYPE prvTaskCheckFreeStackSpace( const uint8_t * pucStackByte )
    {
        uint32_t ulCount = 0U;

        while( *pucStackByte == ( uint8_t ) tskSTACK_FILL_BYTE )
        {
            pucStackByte -= portSTACK_GROWTH;
            ulCount++;
        }

        ulCount /= ( uint32_t ) sizeof( StackType_t ); /*lint !e961 Casting is not redundant on smaller architectures. */

        return ( configSTACK_DEPTH_TYPE ) ulCount;
    }
UBaseType_t uxTaskGetStackHighWaterMark( TaskHandle_t xTask )
    {
        TCB_t * pxTCB;
        uint8_t * pucEndOfStack;
        UBaseType_t uxReturn;

        pxTCB = prvGetTCBFromHandle( xTask );

        #if portSTACK_GROWTH < 0
        {
            pucEndOfStack = ( uint8_t * ) pxTCB->pxStack;
        }
        #else
        {
            pucEndOfStack = ( uint8_t * ) pxTCB->pxEndOfStack;
        }
        #endif

        uxReturn = ( UBaseType_t ) prvTaskCheckFreeStackSpace( pucEndOfStack );

        return uxReturn;
    }
#undef tskSTACK_FILL_BYTE
