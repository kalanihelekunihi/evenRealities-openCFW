/* SPDX-License-Identifier: MIT. Boot-only timer service419240/419684.
 * Fresh static queue path419c9c/419d68/419be8 recovered for startup.
 */
#include <stdint.h>
extern void opencfw_bl_kernel_enter(void);
extern void opencfw_bl_kernel_exit(void);
extern void opencfw_boot_list_initialize(uint32_t *);
extern uint32_t opencfw_bl_mask_interrupts(void);
extern uint32_t opencfw_bl_kernel_static_thread(uintptr_t,uintptr_t,uint32_t,
 uintptr_t,uint32_t,uintptr_t,uintptr_t);
#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
__attribute__((section(".boot_timer_name"),used))
const char opencfw_boot_timer_name[]="Tmr Svc";
static void fail(void) {
    (void)opencfw_bl_mask_interrupts();WORD(UINT32_MAX)=0;
    for (;;)__asm__ volatile("b .":::"memory");
}
/* This specializes the proven fresh-queue branch, not the reuse/wakeup path. */
uint32_t opencfw_boot_timer_queue_fresh(uint32_t count,uint32_t item_size,
 uintptr_t storage,uintptr_t control_block,uint32_t type) {
    if (!control_block || !count || ((storage==0)!=(item_size==0)))fail();
    uint32_t *q=(uint32_t *)control_block;uint8_t *bytes=(uint8_t *)q;
    bytes[0x46]=1;q[0]=item_size?storage:control_block;
    q[15]=count;q[16]=item_size;
    if (UINT32_MAX/count<item_size)fail();
    opencfw_bl_kernel_enter();
    q[2]=q[0]+count*item_size;q[14]=0;q[1]=q[0];
    q[3]=q[0]+(count-1)*item_size;bytes[0x44]=255;bytes[0x45]=255;
    opencfw_boot_list_initialize(q+4);opencfw_boot_list_initialize(q+9);
    opencfw_bl_kernel_exit();bytes[0x4c]=(uint8_t)type;
    return control_block;
}
void opencfw_boot_timer_initialize(void) {
    opencfw_bl_kernel_enter();
    if (!WORD(0x20027180)) {
        opencfw_boot_list_initialize((uint32_t *)(uintptr_t)0x20026f98);
        opencfw_boot_list_initialize((uint32_t *)(uintptr_t)0x20026fac);
        WORD(0x20027178)=0x20026f98;WORD(0x2002717c)=0x20026fac;
        WORD(0x20027180)=opencfw_boot_timer_queue_fresh(50,16,0x20025cd0,0x20026da0,0);
    }
    opencfw_bl_kernel_exit();
}
uint32_t opencfw_bl_timer_service_start(void) {
    opencfw_boot_timer_initialize();
    if (!WORD(0x20027180))fail();
    WORD(0x20027184)=opencfw_bl_kernel_static_thread(0x419445,
       (uintptr_t)opencfw_boot_timer_name,256,0,54,0x200254d0,0x200269e0);
    if (!WORD(0x20027184))fail();
    return 1;
}
