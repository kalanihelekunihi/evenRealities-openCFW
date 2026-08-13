/* SPDX-License-Identifier: MIT */
#include <stdint.h>

static uint32_t host_irq, host_suspend, host_resume, host_delayed;
static uint32_t host_yield, host_ticks, host_scheduler_suspended;
static int32_t host_resume_result;

#include "../../components/shared/freertos/runtime_freertos_queue_receive.h"
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_SCHEDULER_SUSPENDED_LOAD
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_SCHEDULER_SUSPENDED_LOAD() (host_scheduler_suspended)
#undef OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT
#define OPEN_CFW_FREERTOS_QUEUE_NEXT_ASSERT(condition) do { if (!(condition)) __builtin_trap(); } while (0)

void open_cfw_freertos_task_suspend_all(void) { ++host_suspend; }
void open_cfw_freertos_task_add_current_to_delayed_list(uint32_t ticks, int can_block)
{ ++host_delayed; host_ticks = ticks; if (can_block != 0) __builtin_trap(); }
int open_cfw_freertos_task_resume_all(void) { ++host_resume; return host_resume_result; }
void open_cfw_freertos_port_yield(void) { ++host_yield; }
#include "../../components/shared/freertos/runtime_freertos_task_delay.c"

uint32_t open_cfw_cmsis_irq_context(void) { return host_irq; }
#include "../../components/apollo_main/core_overlay/runtime_cmsis_delay.c"

void open_cfw_delay_host_reset(uint32_t irq, int32_t resume_result)
{
    host_irq = irq; host_resume_result = resume_result;
    host_suspend = host_resume = host_delayed = host_yield = host_ticks = 0U;
    host_scheduler_suspended = 0U;
}
int32_t open_cfw_delay_host_call(uint32_t ticks) { return open_cfw_cmsis_delay(ticks); }
uintptr_t open_cfw_delay_host_get(uint32_t selector)
{
    switch (selector) {
        case 0: return host_suspend; case 1: return host_resume;
        case 2: return host_delayed; case 3: return host_yield;
        case 4: return host_ticks; default: return 0U;
    }
}
