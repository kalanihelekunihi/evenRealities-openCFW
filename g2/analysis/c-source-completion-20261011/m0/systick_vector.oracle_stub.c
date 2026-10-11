#include <stdint.h>
uint32_t case_policy_task_lookup(uint32_t x){return x;}
uint32_t case_kernel_irq_save(void){return 0;}
void case_kernel_irq_restore(uint32_t x){(void)x;}
uint32_t case_policy_task_pended(void){return 0;}
