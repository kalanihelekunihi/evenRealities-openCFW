#include <stdint.h>
void case_policy_task_sleep_enter(void){}
void case_policy_task_sleep_enqueue(uint32_t x,uint32_t y){(void)x;(void)y;}
uint32_t case_policy_task_sleep_exit(uint32_t x){(void)x;return 0;}
uint32_t case_policy_task_reschedule(uint32_t x){(void)x;return 0;}
void case_policy_scheduler_lock(void){}
uint32_t case_policy_task_valid(uint32_t x){(void)x;return 0;}
void case_policy_task_unlink(uint32_t x){(void)x;}
void case_policy_task_list_insert(uint32_t x,uint32_t y){(void)x;(void)y;}
uint32_t case_policy_scheduler_unlock(uint32_t x){(void)x;return 0;}
