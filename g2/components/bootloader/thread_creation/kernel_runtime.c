/* SPDX-License-Identifier: MIT. Stock guard41602a/lists418a44/critical helpers. */
#include <stdint.h>
extern uint32_t opencfw_bl_queue_runtime_mode(void);
#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
uint32_t opencfw_bl_context_guard(void) {
    uint32_t ipsr,mask,basepri;
    __asm__ volatile("mrs %0, ipsr":"=r"(ipsr));
    if (ipsr) return 1;
    if (opencfw_bl_queue_runtime_mode()==1) return 0;
    __asm__ volatile("mrs %0, primask":"=r"(mask));
    if (mask) return 1;
    __asm__ volatile("mrs %0, basepri":"=r"(basepri));
    return basepri!=0;
}
uint32_t opencfw_bl_mask_interrupts(void) {
    uint32_t old;
    __asm__ volatile("mrs %0, basepri\nmov r1, #48\nmsr basepri, r1\ndsb sy\nisb sy":"=r"(old)::"r1","memory");
    return old;
}
void opencfw_bl_restore_interrupts(uint32_t value) {
    __asm__ volatile("msr basepri, %0\ndsb sy\nisb sy"::"r"(value):"memory");
}
void opencfw_bl_kernel_enter(void) {
    (void)opencfw_bl_mask_interrupts();WORD(0x200004c4)++;
    __asm__ volatile("dsb sy\nisb sy":::"memory");
}
void opencfw_bl_kernel_exit(void) {
    if (!WORD(0x200004c4)) {
        (void)opencfw_bl_mask_interrupts();WORD(UINT32_MAX)=0;
        for (;;)__asm__ volatile("b .":::"memory");
    }
    WORD(0x200004c4)--;
    if (!WORD(0x200004c4))opencfw_bl_restore_interrupts(0);
}
void opencfw_bl_kernel_reschedule(void) {
    WORD(0xe000ed04)=0x10000000;
    __asm__ volatile("dsb sy\nisb sy":::"memory");
}
void opencfw_boot_list_initialize(uint32_t *list) {
    uint32_t end=(uintptr_t)list+8;
    list[1]=end;list[2]=UINT32_MAX;list[3]=end;list[4]=end;list[0]=0;
}
void opencfw_bl_ready_lists_initialize(void) {
    for (uint32_t i=0;i<56;i++)opencfw_boot_list_initialize((uint32_t *)(uintptr_t)(0x20024870+20*i));
    for (uint32_t i=0;i<5;i++)opencfw_boot_list_initialize((uint32_t *)(uintptr_t)(0x20026f34+20*i));
    WORD(0x20027138)=0x20026f34;WORD(0x2002713c)=0x20026f48;
}
