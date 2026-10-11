#include <stdint.h>
void case_policy_scheduler_lock(void){}
uint32_t case_policy_scheduler_unlock(void){return 0;}
void case_policy_task_unlink(uint32_t x){(void)x;}
void case_boot_task_reclaim(uint32_t x){(void)x;}
