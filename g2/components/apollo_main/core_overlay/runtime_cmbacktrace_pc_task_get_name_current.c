/* SPDX-License-Identifier: MIT */

/*
 * OpenCFW CmBacktrace/FreeRTOS ABI adapter.
 *
 * CmBacktrace's recovered vTaskName integration has no arguments. The stock
 * G2 adapter loads the current TCB word at 0x20074A20 and returns the pointer
 * at offset 0x34 without a null check. Preserve that behavior exactly: a null
 * current TCB returns (const char *)0x34 rather than entering the assertion
 * path used by pcTaskGetName(NULL).
 *
 * The host-only seam is deliberately unavailable unless the focused test
 * defines OPEN_CFW_CMBACKTRACE_HOST_TEST_CURRENT_TCB. Production target
 * builds therefore retain the fixed-address volatile load and no external
 * dependency.
 */

#include "runtime_cmbacktrace_pc_task_get_name_current.h"

#define OPEN_CFW_CMBACKTRACE_CURRENT_TCB_WORD_ADDRESS 0x20074A20U
#define OPEN_CFW_CMBACKTRACE_TASK_NAME_OFFSET 0x34U

#if defined(OPEN_CFW_CMBACKTRACE_HOST_TEST_CURRENT_TCB)
extern __UINTPTR_TYPE__ open_cfw_cmbacktrace_host_test_current_tcb(void);
#else
_Static_assert(
    sizeof(__UINTPTR_TYPE__) == 4U,
    "G2 CmBacktrace current-TCB word width changed"
);
#endif

__attribute__((used, noinline))
const char *open_cfw_cmbacktrace_pc_task_get_name_current(void)
{
    __UINTPTR_TYPE__ current_tcb;

#if defined(OPEN_CFW_CMBACKTRACE_HOST_TEST_CURRENT_TCB)
    current_tcb = open_cfw_cmbacktrace_host_test_current_tcb();
#else
    current_tcb = *(volatile __UINTPTR_TYPE__ *)
        (__UINTPTR_TYPE__)OPEN_CFW_CMBACKTRACE_CURRENT_TCB_WORD_ADDRESS;
#endif

    return (const char *)(current_tcb + OPEN_CFW_CMBACKTRACE_TASK_NAME_OFFSET);
}
