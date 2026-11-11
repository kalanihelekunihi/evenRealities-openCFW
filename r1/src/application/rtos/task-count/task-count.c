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
/* Define native assertions before portmacro.h selects the ISR safety hook. */
#include "native_port_assert.h"
#include "FreeRTOS.h"
#include "task.h"
extern volatile UBaseType_t uxCurrentNumberOfTasks;
UBaseType_t uxTaskGetNumberOfTasks( void )
{
    /* A critical section is not required because the variables are of type
     * BaseType_t. */
    return uxCurrentNumberOfTasks;
}

/* Shared native kernel words already used by selected scheduler units. */
#define xTickCount (*(volatile TickType_t *)(uintptr_t)UINT32_C(0x20007828))
#define xSchedulerRunning (*(volatile BaseType_t *)(uintptr_t)UINT32_C(0x20007830))
#define uxSchedulerSuspended (*(volatile UBaseType_t *)(uintptr_t)UINT32_C(0x20007850))
_Static_assert(sizeof(TickType_t)==4 && portTICK_TYPE_IS_ATOMIC==1 &&
               taskSCHEDULER_SUSPENDED==0 && taskSCHEDULER_NOT_STARTED==1 &&
               taskSCHEDULER_RUNNING==2, "native kernel query configuration");

TickType_t xTaskGetTickCount( void )
{
    TickType_t xTicks;

    /* Critical section required if running on a 16 bit processor. */
    portTICK_TYPE_ENTER_CRITICAL();
    {
        xTicks = xTickCount;
    }
    portTICK_TYPE_EXIT_CRITICAL();

    return xTicks;
}

TickType_t xTaskGetTickCountFromISR( void )
{
    TickType_t xReturn;
    UBaseType_t uxSavedInterruptStatus;

    /* RTOS ports that support interrupt nesting have the concept of a maximum
     * system call (or maximum API call) interrupt priority.  Interrupts that are
     * above the maximum system call priority are kept permanently enabled, even
     * when the RTOS kernel is in a critical section, but cannot make any calls to
     * FreeRTOS API functions.  If configASSERT() is defined in FreeRTOSConfig.h
     * then portASSERT_IF_INTERRUPT_PRIORITY_INVALID() will result in an assertion
     * failure if a FreeRTOS API function is called from an interrupt that has been
     * assigned a priority above the configured maximum system call priority.
     * Only FreeRTOS functions that end in FromISR can be called from interrupts
     * that have been assigned a priority at or (logically) below the maximum
     * system call  interrupt priority.  FreeRTOS maintains a separate interrupt
     * safe API to ensure interrupt entry is as fast and as simple as possible.
     * More information (albeit Cortex-M specific) is provided on the following
     * link: https://www.FreeRTOS.org/RTOS-Cortex-M3-M4.html */
    portASSERT_IF_INTERRUPT_PRIORITY_INVALID();

    uxSavedInterruptStatus = portTICK_TYPE_SET_INTERRUPT_MASK_FROM_ISR();
    {
        xReturn = xTickCount;
    }
    portTICK_TYPE_CLEAR_INTERRUPT_MASK_FROM_ISR( uxSavedInterruptStatus );

    return xReturn;
}

BaseType_t xTaskGetSchedulerState( void )
    {
        BaseType_t xReturn;

        if( xSchedulerRunning == pdFALSE )
        {
            xReturn = taskSCHEDULER_NOT_STARTED;
        }
        else
        {
            if( uxSchedulerSuspended == ( UBaseType_t ) pdFALSE )
            {
                xReturn = taskSCHEDULER_RUNNING;
            }
            else
            {
                xReturn = taskSCHEDULER_SUSPENDED;
            }
        }

        return xReturn;
    }

/* Stock compressed RW initialization sets the word at 0x2000781c to zero.
 * The final firmware linker must place this shared cell at that address. */
__attribute__((section(".r1.rtos.current_tcb"), aligned(4), used))
TaskHandle_t volatile pxCurrentTCB = NULL;
_Static_assert(sizeof(pxCurrentTCB) == 4, "native current-task pointer width");

TaskHandle_t xTaskGetCurrentTaskHandle( void )
{
    TaskHandle_t xReturn;

    xReturn = pxCurrentTCB;
    return xReturn;
}

/* Native CmBacktrace integration: 0x964b0 / 0x964bc. The depth word
 * is a count of StackType_t entries, not a byte size or end pointer. */
#include "../../board/native_task_construction.h"
_Static_assert(offsetof(r1_native_tcb, pxStack) == 48 &&
               offsetof(r1_native_tcb, uxNativeStackDepth) == 84,
               "native crash diagnostic stack fields");

uint32_t *vTaskStackAddr(void)
{
    return pxCurrentTCB->pxStack;
}

uint32_t vTaskStackSize(void)
{
    return pxCurrentTCB->uxNativeStackDepth;
}

/* Stock 0x6a098 prefers the watchdog-expired task, then samples current TCB.
 * Native name leaves add 52 without dereferencing the task/name pointer. */
extern uint32_t r1_native_watchdog_expired_task(void);
_Static_assert(offsetof(r1_native_tcb, pcTaskName) == 52,
               "native crash diagnostic name field");
char *vTaskName(void)
{
    uintptr_t task = r1_native_watchdog_expired_task();
    if (task == 0)
        task = (uintptr_t)pxCurrentTCB;
    return (char *)(task + offsetof(r1_native_tcb, pcTaskName));
}
