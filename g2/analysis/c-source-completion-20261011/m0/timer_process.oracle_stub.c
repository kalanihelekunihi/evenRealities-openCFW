#include <stdint.h>
void case_policy_task_sleep_enter(void){}
uint32_t case_policy_task_sleep_exit(void){return 0;}
uint32_t case_boot_timer_now(uint32_t *x){*x=0;return 0;}
void case_boot_timer_process_due(uint32_t a,uint32_t b){(void)a;(void)b;}
void case_boot_timer_queue_wait(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
uint32_t case_policy_task_reschedule(void){return 0;}
