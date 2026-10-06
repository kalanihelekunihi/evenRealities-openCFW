/* SPDX-License-Identifier: MIT. Stock418148/41b5d0 boot scheduler setup.
 * Timer startup and port timer/SVC transfer remain explicit providers.
 */
#include <stdint.h>
extern uint32_t opencfw_bl_kernel_static_thread(uintptr_t,uintptr_t,uint32_t,
 uintptr_t,uint32_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_bl_timer_service_start(void);
extern uint32_t opencfw_bl_mask_interrupts(void);
extern void opencfw_bl_port_start(void);
#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
__attribute__((section(".boot_idle_name"),used))
const char opencfw_boot_idle_name[]="IDLE";
void opencfw_boot_idle_memory(uint32_t *cb,uint32_t *stack,uint32_t *words) {
    *cb=0x20026970;*stack=0x200250d0;*words=256;
}
uint32_t opencfw_bl_kernel_start(void) {
    uint32_t cb=0,stack=0,words;
    opencfw_boot_idle_memory(&cb,&stack,&words);
    WORD(0x20027168)=opencfw_bl_kernel_static_thread(0x4189ad,
         (uintptr_t)opencfw_boot_idle_name,words,0,0,stack,cb);
    uint32_t success=WORD(0x20027168)!=0;
    if (success)success=opencfw_bl_timer_service_start();
    if (success==1) {
        (void)opencfw_bl_mask_interrupts();
        WORD(0x20027164)=UINT32_MAX;
        WORD(0x20027150)=1;WORD(0x20027148)=0;
        opencfw_bl_port_start();
    } else if (success==UINT32_MAX) {
        (void)opencfw_bl_mask_interrupts();WORD(UINT32_MAX)=0;
        for (;;)__asm__ volatile("b .":::"memory");
    }
    /* Stock return loads word200004c8; caller4160b0 ignores it. */
    return WORD(0x200004c8);
}
