/* Independent semantic reconstruction: osDelay416378..41639a,
 * vTaskDelay417fa8..417fe4. Tick units; no milliseconds inference. */
#include <stdint.h>
extern uint32_t opencfw_bl_context_guard(void);
extern uint32_t opencfw_bl_mask_interrupts(void);
extern void opencfw_bl_scheduler_suspend(void);
extern void opencfw_boot_task_block(uint32_t,uint32_t);
extern uint32_t opencfw_bl_scheduler_resume(void);
extern void opencfw_bl_kernel_reschedule(void);
#define W(p) (*(volatile uint32_t *)(uintptr_t)(p))
void opencfw_kernel_delay(uint32_t ticks){
 uint32_t resumed=0;
 if(ticks){
  if(W(0x2002716c)){
   (void)opencfw_bl_mask_interrupts();W(UINT32_MAX)=0;
   for(;;)__asm__ volatile("b .":::"memory");
  }
  opencfw_bl_scheduler_suspend();opencfw_boot_task_block(ticks,0);
  resumed=opencfw_bl_scheduler_resume();
 }
 if(!resumed)opencfw_bl_kernel_reschedule();
}
int32_t opencfw_cmsis_delay(uint32_t ticks){
 if(opencfw_bl_context_guard())return -6;
 if(ticks)opencfw_kernel_delay(ticks);
 return 0;
}
