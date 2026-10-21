/* SPDX-License-Identifier: MIT
 * Stock ready-list registration417e58..417f0a. Intrusive ARM32 layout.
 * Critical-section, list initialization, and reschedule remain providers.
 */
#include <stdint.h>
extern void opencfw_bl_kernel_enter(void);
extern void opencfw_bl_kernel_exit(void);
extern void opencfw_bl_ready_lists_initialize(void);
extern void opencfw_bl_kernel_reschedule(void);
#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
void opencfw_bl_thread_register(uint32_t *tcb) {
    opencfw_bl_kernel_enter();
    WORD(0x20027144)++;
    if (!WORD(0x20027134)) {
        WORD(0x20027134)=(uintptr_t)tcb;
        if (WORD(0x20027144)==1)opencfw_bl_ready_lists_initialize();
    } else if (!WORD(0x20027150)) {
        uint32_t *current=(uint32_t *)(uintptr_t)WORD(0x20027134);
        if (tcb[11]>=current[11])WORD(0x20027134)=(uintptr_t)tcb;
    }
    WORD(0x20027160)++;
    tcb[22]=WORD(0x20027160);
    if (WORD(0x2002714c)<tcb[11])WORD(0x2002714c)=tcb[11];
    uint32_t *list=(uint32_t *)(uintptr_t)(0x20024870u+20u*tcb[11]);
    uint32_t *index=(uint32_t *)(uintptr_t)list[1];
    tcb[2]=(uintptr_t)index;tcb[3]=index[2];
    uint32_t *previous=(uint32_t *)(uintptr_t)index[2];
    previous[1]=(uintptr_t)tcb+4u;
    index[2]=(uintptr_t)tcb+4u;
    tcb[5]=(uintptr_t)list;list[0]++;
    opencfw_bl_kernel_exit();
    if (WORD(0x20027150)) {
        uint32_t *current=(uint32_t *)(uintptr_t)WORD(0x20027134);
        if (current[11]<tcb[11])opencfw_bl_kernel_reschedule();
    }
}
