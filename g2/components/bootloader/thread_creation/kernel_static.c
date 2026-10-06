/* SPDX-License-Identifier: MIT
 * Stock static creation 417c7c, initializer417d94, initial frame41b46e.
 * Scheduler registration remains an explicit provider.
 */
#include <stdint.h>
extern void opencfw_bl_thread_register(uint32_t *tcb);
extern uint32_t opencfw_bl_mask_interrupts(void);
static void fail(void) {
    (void)opencfw_bl_mask_interrupts();
    *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0;
    for (;;) __asm__ volatile("b ." ::: "memory");
}
uintptr_t opencfw_boot_thread_frame(uintptr_t top,uintptr_t base,
                                  uintptr_t entry,uintptr_t arg) {
    uint32_t *p=(uint32_t *)top;
    *--p=0x01000000;*--p=entry;*--p=0x41b391;
    *--p=0x12121212;*--p=0x03030303;*--p=0x02020202;*--p=0x01010101;
    *--p=arg;*--p=0x11111111;*--p=0x10101010;*--p=0x09090909;
    *--p=0x08080808;*--p=0x07070707;*--p=0x06060606;*--p=0x05050505;
    *--p=0x04040404;*--p=0xfffffffd;*--p=base;
    return (uintptr_t)p;
}
void opencfw_boot_thread_initialize(uintptr_t entry,uintptr_t name,
 uint32_t words,uintptr_t arg,uint32_t priority,uint32_t *out,
 uint32_t *tcb,uint32_t unused) {
    (void)unused;
    uint8_t *stack=(uint8_t *)(uintptr_t)tcb[12];
    uint32_t count=words<<2;
    for (uint32_t i=0;i<count;i++)stack[i]=0xa5;
    uintptr_t top=((uint32_t)(tcb[12]+count-4u))&~7u;
    tcb[21]=words;
    if (name) {
        const uint8_t *n=(const uint8_t *)name;
        uint8_t *dest=(uint8_t *)tcb+0x34;
        for (uint32_t i=0;i<32;i++) {dest[i]=n[i];if (!n[i])break;}
        dest[31]=0;
    }
    if (priority>=56)fail();
    tcb[11]=priority;tcb[24]=priority;
    tcb[5]=0;tcb[10]=0;tcb[4]=(uintptr_t)tcb;
    tcb[6]=56-priority;tcb[9]=(uintptr_t)tcb;
    tcb[0]=opencfw_boot_thread_frame(top,tcb[12],entry,arg);
    if (out)*out=(uintptr_t)tcb;
}
uint32_t opencfw_bl_kernel_static_thread(uintptr_t entry,uintptr_t name,
 uint32_t words,uintptr_t arg,uint32_t priority,uintptr_t stack,
 uintptr_t control_block) {
    if (!stack || !control_block)fail();
    uint8_t *bytes=(uint8_t *)control_block;
    for (uint32_t i=0;i<112;i++)bytes[i]=0;
    uint32_t *tcb=(uint32_t *)control_block;
    tcb[12]=stack;bytes[0x6d]=2;
    uint32_t handle;
    opencfw_boot_thread_initialize(entry,name,words,arg,priority,&handle,tcb,0);
    opencfw_bl_thread_register(tcb);
    return handle;
}
