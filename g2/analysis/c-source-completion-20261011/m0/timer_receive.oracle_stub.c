#include <stdint.h>
uint32_t case_policy_scheduler_mode(void){return 1;}
void case_policy_scheduler_lock(void){}
uint32_t case_policy_scheduler_unlock(void){return 0;}
uint32_t case_policy_task_reschedule(void){return 0;}
uint32_t case_boot_pool_wake_waiter(uint32_t a){(void)a;return 0;}
void case_policy_queue_wait_snapshot(uint32_t *a){(void)a;}
void case_policy_task_sleep_enter(void){}
uint32_t case_policy_queue_wait_elapsed(uint32_t *a,uint32_t *b){(void)a;(void)b;return 0;}
void case_policy_queue_wait_cleanup(uint32_t a){(void)a;}
uint32_t case_policy_task_sleep_exit(void){return 0;}
void case_policy_queue_wait_register(uint32_t a,uint32_t b){(void)a;(void)b;}
