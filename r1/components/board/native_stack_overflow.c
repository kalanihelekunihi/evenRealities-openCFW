/* Native R1 0x95bfc. Terminal logger drain/loop; no explicit interrupt mask. */
#include "FreeRTOS.h"
#include "task.h"
#include <stdbool.h>
#include <stdint.h>
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern bool nrf_log_frontend_dequeue(void);
const char r1_stack_overflow_ring[]
 __attribute__((section(".r1.stack_overflow.ring")))="[RING]Stack overflow in task: %s\n";
const char r1_stack_overflow_nordic[]
 __attribute__((section(".r1.stack_overflow.nordic")))="Stack overflow in task: %s\n";
_Noreturn void vApplicationStackOverflowHook(TaskHandle_t task,char *name)
{
 (void)task;
 if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(UINT32_C(0x0c400000),r1_stack_overflow_ring,r1_stack_overflow_ring,name);
 if (r1_structured_log_mode_get()&2u)
  nrf_log_frontend_std_1(UINT32_C(0x001c0003),r1_stack_overflow_nordic,(uint32_t)(uintptr_t)name);
 while (nrf_log_frontend_dequeue()) {}
 for (;;) {}
}
