#include <stdint.h>
void case_policy_scheduler_lock(void){}
uint32_t case_policy_scheduler_unlock(void){return 0;}
uint32_t case_boot_scheduler_pool(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e){(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}
void case_boot_scheduler_register(uint32_t a,const char*b){(void)a;(void)b;}
const char case_boot_scheduler_name[]="SYSTEM";
void case_boot_service_task_entry(void*x){(void)x;}
const char case_boot_service_task_name[]="Tm r Svc";
uint32_t case_boot_task_create(void(*f)(void*),const char*n,uint32_t a,void*b,uint32_t c,uint32_t d,uint32_t e){(void)f;(void)n;(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}
