/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 *
 * SPDX-License-Identifier: MIT
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 * Production source adaptation of vPortYield(),
 * vPortEnterCritical(), and vPortExitCritical() from FreeRTOS-Kernel V10.5.1
 * portable/IAR/ARM_CM55_NTZ/non_secure/port.c at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.
 *
 * The official G2 Apollo-main image owns the trio at
 * [0x004420BC, 0x00442114).  Its recovered fixed seams are ICSR at
 * 0xE000ED04, ulCriticalNesting at 0x2000309C, and the authenticated
 * ulSetInterruptMask()/vClearInterruptMask() assembly pair.  The latter pair
 * installs/restores BASEPRI with configMAX_SYSCALL_INTERRUPT_PRIORITY=0x30.
 *
 * The production overlay compiles these three entry points as isolated,
 * relocated source leaves and redirects their complete stock bodies.
 */

#include "freertos_scheduler_port_trio.h"

_Static_assert(
    sizeof(open_cfw_freertos_port_u32) == 4U,
    "G2 FreeRTOS port words must remain 32-bit");

extern open_cfw_freertos_port_u32 ulSetInterruptMask(void);
extern void vClearInterruptMask(open_cfw_freertos_port_u32 mask);

#ifndef OPEN_CFW_FREERTOS_PORT_WRITE_ICSR
#define OPEN_CFW_FREERTOS_PORT_WRITE_ICSR(value)                         \
    (*(volatile open_cfw_freertos_port_u32 *)(__UINTPTR_TYPE__)          \
        OPEN_CFW_FREERTOS_PORT_ICSR_ADDRESS = (value))
#endif

#ifndef OPEN_CFW_FREERTOS_PORT_READ_CRITICAL_NESTING
#define OPEN_CFW_FREERTOS_PORT_READ_CRITICAL_NESTING()                   \
    (*(volatile open_cfw_freertos_port_u32 *)(__UINTPTR_TYPE__)          \
        OPEN_CFW_FREERTOS_PORT_CRITICAL_NESTING_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_PORT_WRITE_CRITICAL_NESTING
#define OPEN_CFW_FREERTOS_PORT_WRITE_CRITICAL_NESTING(value)             \
    (*(volatile open_cfw_freertos_port_u32 *)(__UINTPTR_TYPE__)          \
        OPEN_CFW_FREERTOS_PORT_CRITICAL_NESTING_ADDRESS = (value))
#endif

#ifndef OPEN_CFW_FREERTOS_PORT_SET_INTERRUPT_MASK
#define OPEN_CFW_FREERTOS_PORT_SET_INTERRUPT_MASK() ulSetInterruptMask()
#endif

#ifndef OPEN_CFW_FREERTOS_PORT_CLEAR_INTERRUPT_MASK
#define OPEN_CFW_FREERTOS_PORT_CLEAR_INTERRUPT_MASK(mask)                \
    vClearInterruptMask(mask)
#endif

#ifndef OPEN_CFW_FREERTOS_PORT_DATA_BARRIER
#define OPEN_CFW_FREERTOS_PORT_DATA_BARRIER()                            \
    __asm volatile("dsb sy" ::: "memory")
#endif

#ifndef OPEN_CFW_FREERTOS_PORT_INSTRUCTION_BARRIER
#define OPEN_CFW_FREERTOS_PORT_INSTRUCTION_BARRIER()                     \
    __asm volatile("isb sy")
#endif

#ifndef OPEN_CFW_FREERTOS_PORT_ASSERT_FAILURE
#define OPEN_CFW_FREERTOS_PORT_ASSERT_FAILURE()                          \
    do                                                                  \
    {                                                                   \
        (void)OPEN_CFW_FREERTOS_PORT_SET_INTERRUPT_MASK();              \
        *(volatile open_cfw_freertos_port_u32 *)(__UINTPTR_TYPE__)      \
            0xFFFFFFFFU = 0U;                                           \
        for (;;)                                                        \
        {                                                               \
        }                                                               \
    } while (0)
#endif

__attribute__((used, noinline))
void open_cfw_freertos_port_yield(void)
{
    OPEN_CFW_FREERTOS_PORT_WRITE_ICSR(
        OPEN_CFW_FREERTOS_PORT_PENDSVSET_BIT);
    OPEN_CFW_FREERTOS_PORT_DATA_BARRIER();
    OPEN_CFW_FREERTOS_PORT_INSTRUCTION_BARRIER();
}

__attribute__((used, noinline))
void open_cfw_freertos_port_enter_critical(void)
{
    (void)OPEN_CFW_FREERTOS_PORT_SET_INTERRUPT_MASK();
    OPEN_CFW_FREERTOS_PORT_WRITE_CRITICAL_NESTING(
        OPEN_CFW_FREERTOS_PORT_READ_CRITICAL_NESTING() + 1U);
    OPEN_CFW_FREERTOS_PORT_DATA_BARRIER();
    OPEN_CFW_FREERTOS_PORT_INSTRUCTION_BARRIER();
}

__attribute__((used, noinline))
void open_cfw_freertos_port_exit_critical(void)
{
    if (OPEN_CFW_FREERTOS_PORT_READ_CRITICAL_NESTING() == 0U)
    {
        OPEN_CFW_FREERTOS_PORT_ASSERT_FAILURE();
    }

    OPEN_CFW_FREERTOS_PORT_WRITE_CRITICAL_NESTING(
        OPEN_CFW_FREERTOS_PORT_READ_CRITICAL_NESTING() - 1U);

    if (OPEN_CFW_FREERTOS_PORT_READ_CRITICAL_NESTING() == 0U)
    {
        OPEN_CFW_FREERTOS_PORT_CLEAR_INTERRUPT_MASK(0U);
    }
}
