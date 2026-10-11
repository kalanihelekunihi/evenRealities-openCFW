#include <stdint.h>
void case_policy_scheduler_lock(void){}
uint32_t case_policy_scheduler_unlock(void){return 0;}
void case_policy_task_list_insert(uint32_t a,uint32_t b){(void)a;(void)b;}
uint32_t case_policy_task_reschedule(void){return 0;}
void case_boot_first_task_prepare(void){}
