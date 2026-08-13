#include <stdint.h>
static uint32_t irq_value, active_value, active_calls;
uint32_t open_cfw_cmsis_irq_context(void) { return irq_value; }
uint32_t open_cfw_rtos_timer_is_active(const void *timer)
{ (void)timer; active_calls++; return active_value; }
void open_cfw_test_timer_running_reset(uint32_t irq, uint32_t active)
{ irq_value=irq; active_value=active; active_calls=0; }
uint32_t open_cfw_test_timer_running_calls(void) { return active_calls; }
#include "../../components/apollo_main/core_overlay/runtime_cmsis_timer_is_running.c"
