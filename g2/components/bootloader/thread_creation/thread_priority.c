/* SPDX-License-Identifier: MIT. Stock4161c6/4161ce/41806e/418b4e. */
#include <stdint.h>
#include <stddef.h>
extern uint32_t opencfw_bl_context_guard(void);
extern uint32_t opencfw_bl_mask_interrupts(void);
extern void opencfw_bl_kernel_enter(void);
extern void opencfw_bl_kernel_exit(void);
extern void opencfw_bl_kernel_reschedule(void);
#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
uintptr_t opencfw_boot_thread_current(void) {return WORD(0x20027134);}
static void remove_item(uint32_t *item) {
    uint32_t *container=(uint32_t *)(uintptr_t)item[4];
    uint32_t *next=(uint32_t *)(uintptr_t)item[1];
    uint32_t *previous=(uint32_t *)(uintptr_t)item[2];
    next[2]=(uintptr_t)previous;previous[1]=(uintptr_t)next;
    if (container[1]==(uintptr_t)item)container[1]=(uintptr_t)previous;
    item[4]=0;container[0]--;
}
void opencfw_bl_thread_priority_set(uintptr_t handle,uint32_t priority) {
    if (priority>=56) {
        (void)opencfw_bl_mask_interrupts();WORD(UINT32_MAX)=0;
        for (;;)__asm__ volatile("b .":::"memory");
    }
    opencfw_bl_kernel_enter();
    uint32_t *tcb=(uint32_t *)(handle?handle:WORD(0x20027134));
    uint32_t old_base=tcb[24],old_effective=tcb[11],yield=0;
    if (old_base!=priority) {
        uint32_t *current=(uint32_t *)(uintptr_t)WORD(0x20027134);
        if (old_base<priority)yield=tcb!=current && priority>=current[11];
        else yield=tcb==current;
        if (old_effective==old_base)tcb[11]=priority;
        tcb[24]=priority;
        if (!(tcb[6]&0x80000000))tcb[6]=56-priority;
        uint32_t *old_list=(uint32_t *)(uintptr_t)(0x20024870+20*old_effective);
        if (tcb[5]==(uintptr_t)old_list) {
            remove_item(tcb+1);
            uint32_t effective=tcb[11];
            if (WORD(0x2002714c)<effective)WORD(0x2002714c)=effective;
            uint32_t *list=(uint32_t *)(uintptr_t)(0x20024870+20*effective);
            uint32_t *index=(uint32_t *)(uintptr_t)list[1];
            tcb[2]=(uintptr_t)index;tcb[3]=index[2];
            uint32_t *previous=(uint32_t *)(uintptr_t)index[2];
            previous[1]=(uintptr_t)tcb+4;index[2]=(uintptr_t)tcb+4;
            tcb[5]=(uintptr_t)list;list[0]++;
        }
        if (yield)opencfw_bl_kernel_reschedule();
    }
    opencfw_bl_kernel_exit();
}
int32_t opencfw_boot_thread_priority_set(uintptr_t handle,uint32_t priority) {
    if (opencfw_bl_context_guard())return -6;
    if (!handle || (priority-1)>=56)return -4;
    opencfw_bl_thread_priority_set(handle,priority);
    return 0;
}
