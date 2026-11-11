/* Reconstructed bootloader terminal paths; not an artificial replacement trap.
 * All hardware/fault effects are stopped or modeled in offline tests. */
#include <stdint.h>
extern void opencfw_boot_manager_start_signal(uint32_t);
extern int32_t opencfw_cmsis_delay(uint32_t);
extern int opencfw_boot_plain_printf(const char *,...);
extern void opencfw_bl_mask_interrupts(void);
extern __attribute__((noreturn)) void opencfw_iar_exit(void);
static const char malloc_text[]="MallocFaile\xef\xbc\x9a" "cannot malloc memory\r\n";
static const char overflow_text[]="task %s stack overflow";
__attribute__((noreturn)) void opencfw_dfu_terminal_native(void){
 opencfw_boot_manager_start_signal(1);
 for(;;)(void)opencfw_cmsis_delay(UINT32_MAX);
}
__attribute__((noreturn)) void opencfw_malloc_failed_native(void){
 (void)opencfw_boot_plain_printf(malloc_text);
 for(;;){ }
}
__attribute__((noreturn)) void opencfw_stack_overflow_native(uint32_t *tcb,const char *name){
 (void)tcb;(void)opencfw_boot_plain_printf(overflow_text,name);
 for(;;)__asm__ volatile("bkpt #0":::"memory");
}
/* Stock 0x4329c4/0x4329c8: the platform terminal path is the semihosting
 * exit, which never returns. */
__attribute__((noreturn)) void opencfw_platform_terminal_native(void){
 for(;;)opencfw_iar_exit();
}
/* Stock task-return trap (FreeRTOS prvTaskExitError shape): fault if the
 * critical nesting count at 0x200004c4 is live, otherwise mask interrupts and
 * wait for a debugger to set the release word. */
void opencfw_task_return_native(void){
 volatile uint32_t release=0u;
 if(*(volatile uint32_t *)(uintptr_t)0x200004c4u!=UINT32_MAX){
  opencfw_bl_mask_interrupts();
  *(volatile uint32_t *)UINT32_C(0xffffffff)=0u;
  for(;;){}
 }
 opencfw_bl_mask_interrupts();
 while(release==0u){}
}

/* Stock entry names that branch straight to the provider above. */
__typeof__(opencfw_task_return_native) opencfw_bl_task_return __attribute__((alias("opencfw_task_return_native")));

/* Stock entry names that reach the provider above directly. */
__typeof__(opencfw_dfu_terminal_native) opencfw_boot_dfu_terminal __attribute__((alias("opencfw_dfu_terminal_native")));
__typeof__(opencfw_malloc_failed_native) opencfw_bl_malloc_failed __attribute__((alias("opencfw_malloc_failed_native")));
__typeof__(opencfw_platform_terminal_native) opencfw_boot_platform_terminal __attribute__((alias("opencfw_platform_terminal_native")));
__typeof__(opencfw_stack_overflow_native) opencfw_bl_stack_overflow __attribute__((alias("opencfw_stack_overflow_native")));
