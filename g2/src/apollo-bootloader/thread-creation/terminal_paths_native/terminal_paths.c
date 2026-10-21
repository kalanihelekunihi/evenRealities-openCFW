/* Reconstructed bootloader terminal paths; not an artificial replacement trap.
 * All hardware/fault effects are stopped or modeled in offline tests. */
#include <stdint.h>
extern void opencfw_boot_manager_start_signal(uint32_t);
extern int32_t opencfw_cmsis_delay(uint32_t);
extern int opencfw_boot_plain_printf(const char *,...);
extern void opencfw_bl_mask_interrupts(void);
extern void opencfw_iar_exit(void);
static const char malloc_text[]="MallocFaile\xef\xbc\x9a" "cannot malloc memory\r\n";
static const char overflow_text[]="task %s stack overflow";
__attribute__((noreturn)) void opencfw_dfu_terminal_native(void){
 opencfw_boot_manager_start_signal(1);
 for(;;)(void)opencfw_cmsis_delay(UINT32_MAX);
}
__attribute__((noreturn)) void opencfw_malloc_failed_native(void){
 (void)opencfw_boot_plain_printf(malloc_text);
 for(;;)__asm__ volatile("b .":::"memory");
}
__attribute__((noreturn)) void opencfw_stack_overflow_native(uint32_t *tcb,const char *name){
 (void)tcb;(void)opencfw_boot_plain_printf(overflow_text,name);
 for(;;)__asm__ volatile("bkpt #0":::"memory");
}
/* Entry4329c4/4329c8 deliberately do not return or preserveR7. Exit ignores
 * its raw status and implements the actual stock semihost protocol. */
__attribute__((naked,noreturn)) void opencfw_platform_terminal_native(void){__asm__ volatile(
 "b.w 1f\n1: mov r7,r0\n2: mov r0,r7\nbl opencfw_iar_exit\nb 2b\n");}
/* Keep the real debugger-release stack slot and raw return behavior. */
__attribute__((naked)) void opencfw_task_return_native(void){__asm__ volatile(
 "push {r7,lr}\nmovs r0,#0\nstr r0,[sp]\nldr r0,=0x200004c4\nldr r0,[r0]\ncmn r0,#1\nbeq 2f\n"
 "bl opencfw_bl_mask_interrupts\nmovs r0,#0\nmovs.w r1,#-1\nstr r0,[r1]\n1: b 1b\n"
 "2: bl opencfw_bl_mask_interrupts\n3: ldr r0,[sp]\ncmp r0,#0\nbeq 3b\npop {r0,pc}\n");}
