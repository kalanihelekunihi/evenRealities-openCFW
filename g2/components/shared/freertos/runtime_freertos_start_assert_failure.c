/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 * SPDX-License-Identifier: MIT
 *
 * Production fail-stop used by vTaskStartScheduler() when the timer task
 * cannot be allocated.  This preserves the released G2 configASSERT path:
 * mask interrupts, fault an invalid address, and never return.
 */

#include "runtime_freertos_start_assert_failure.h"

typedef unsigned int open_cfw_freertos_assert_u32;
typedef __UINTPTR_TYPE__ open_cfw_freertos_assert_uintptr;

extern open_cfw_freertos_assert_u32 ulSetInterruptMask(void);

__attribute__((used, noinline, noreturn))
void open_cfw_freertos_start_assert_failure(void)
{
    (void)ulSetInterruptMask();
    *(volatile open_cfw_freertos_assert_u32 *)
        (open_cfw_freertos_assert_uintptr)-1 = 0U;
    for (;;) {
    }
}
