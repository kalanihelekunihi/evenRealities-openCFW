/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800b360 FreeRTOS timer-service task loop.
 * Its three timer operations are genuine descendant bodies.
 */
#include <stdint.h>
extern uint32_t case_boot_timer_wait_next(uint32_t *deadline); /* 0xade8 */
extern void case_boot_timer_process(uint32_t result,uint32_t deadline); /* 0xb1fc */
extern void case_boot_timer_expired(void); /* 0xb0fc */
void case_boot_service_task_entry(void *argument)
{
    (void)argument;
    for(;;){
        uint32_t deadline;
        uint32_t result=case_boot_timer_wait_next(&deadline);
        case_boot_timer_process(result,deadline);
        case_boot_timer_expired();
    }
}
