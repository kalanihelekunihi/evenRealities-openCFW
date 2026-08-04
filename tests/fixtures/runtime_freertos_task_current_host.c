#include <stdint.h>

static void *volatile open_cfw_test_freertos_task_current_tcb;

#define OPEN_CFW_FREERTOS_TASK_CURRENT_TCB \
    open_cfw_test_freertos_task_current_tcb
#include "../../components/apollo_main/core_overlay/runtime_freertos_task_current.c"

void open_cfw_test_freertos_task_current_set(uintptr_t value)
{
    open_cfw_test_freertos_task_current_tcb = (void *)value;
}

uintptr_t open_cfw_test_freertos_task_current_get(void)
{
    return (uintptr_t)open_cfw_freertos_task_get_current_task_handle();
}
