#include <stdint.h>
void case_policy_scheduler_lock(void){}
uint32_t case_policy_scheduler_unlock(void){return 0;}
void case_policy_task_unlink(uint32_t x){(void)x;}
void case_policy_task_list_insert(uint32_t x,uint32_t y){(void)x;(void)y;}
void case_policy_task_wake_cleanup(void){}
uint32_t case_policy_task_reschedule(void){return 0;}
void case_policy_task_wake_dispatch(void){}
void case_boot_idle_task_entry(void*x){(void)x;}
const char case_boot_idle_task_name[5]="IDLE";
uint32_t case_boot_task_create(void(*f)(void*),const char*n,uint32_t a,void*b,uint32_t c,uint32_t d,uint32_t e){(void)f;(void)n;(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}
uint32_t case_boot_scheduler_ready(void){return 0;}
void case_boot_scheduler_run(void){}
