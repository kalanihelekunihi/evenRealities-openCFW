/* SPDX-License-Identifier: MIT. Stock417d16 dynamic stack/TCB lifetime. */
#include <stdint.h>
extern uintptr_t opencfw_bl_rtos_allocate(uint32_t bytes);
extern void opencfw_bl_rtos_free(uintptr_t memory);
extern void opencfw_boot_thread_initialize(uintptr_t,uintptr_t,uint32_t,
 uintptr_t,uint32_t,uint32_t *,uint32_t *,uint32_t);
extern void opencfw_bl_thread_register(uint32_t *);
uint32_t opencfw_bl_kernel_dynamic_thread(uintptr_t entry,uintptr_t name,
 uint32_t words,uintptr_t arg,uint32_t priority,uint32_t *handle) {
    uint32_t n=(uint16_t)words;
    uintptr_t stack=opencfw_bl_rtos_allocate(n<<2);
    uint32_t *tcb=0;
    if (stack) {
        tcb=(uint32_t *)opencfw_bl_rtos_allocate(112);
        if (tcb) {
            uint8_t *bytes=(uint8_t *)tcb;
            for (uint32_t i=0;i<112;i++)bytes[i]=0;
            tcb[12]=stack;
        } else opencfw_bl_rtos_free(stack);
    }
    if (!tcb)return UINT32_MAX;
    ((uint8_t *)tcb)[0x6d]=0;
    opencfw_boot_thread_initialize(entry,name,n,arg,priority,handle,tcb,0);
    opencfw_bl_thread_register(tcb);return 1;
}
