/* SPDX-License-Identifier: MIT. Test linkage adapters for serialized stock
 * task entry pointers. Each adapter tail-calls compiled source from its own
 * section; these placements are not the original instruction encoding or a
 * byte-identical layout. */
#include <stdint.h>

#include "../manager-task/event_dispatch.h"
#include "../manager-task/manager_task.h"
#include "resource_creators.h"
#include "timer_wait.h"

extern void opencfw_boot_dfu_thread_init(void);

__attribute__((section(".timer_task_adapter")))
void opencfw_test_timer_entry(void *argument)
{
    opencfw_boot_timer_task(argument);
}

__attribute__((section(".manager_task_adapter")))
void opencfw_test_manager_entry(void *argument)
{
    opencfw_boot_manager_task(argument);
}

__attribute__((section(".event_task_adapter")))
void opencfw_test_event_entry(void *argument)
{
    opencfw_boot_event_thread(argument);
}

__attribute__((section(".dfu_init_adapter")))
void opencfw_test_dfu_init_entry(void)
{
    opencfw_boot_dfu_thread_init();
}

__attribute__((section(".timer_callback_adapter")))
void opencfw_test_timer_callback_entry(uint32_t *timer)
{
    opencfw_boot_timer_callback_dispatcher(timer);
}
