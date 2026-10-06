/* SPDX-License-Identifier: MIT. Stock42e254/42e278/42e284/42e2a2/42e2ea. */
#include "manager_task.h"
#include <stddef.h>
extern uint32_t opencfw_provider_4164da(uintptr_t attributes);
extern void opencfw_provider_42e53c(void);
extern uintptr_t opencfw_boot_thread_current(void);
extern int32_t opencfw_boot_thread_priority_set(uintptr_t handle,uint32_t priority);
extern uint32_t opencfw_provider_41623a(uintptr_t thread,uint32_t flags);
extern uint32_t opencfw_provider_416590(uintptr_t event,uint32_t flags,uint32_t options,uint32_t ticks);
extern uint32_t opencfw_bl_mask_interrupts(void);
extern void opencfw_provider_4176ce(uint32_t,const char *,const char *,const char *,uint32_t,const char *,...);
#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))
void opencfw_provider_42e254(void) {
    WORD(0x20000510)=opencfw_provider_4164da(0);
    if (!WORD(0x20000510)) {
        (void)opencfw_bl_mask_interrupts();WORD(UINT32_MAX)=0;
        for (;;)__asm__ volatile("b .":::"memory");
    }
}
void opencfw_boot_manager_callback_dispatch(void) {
    (void)opencfw_boot_thread_priority_set(opencfw_boot_thread_current(),8);
    void (*callback)(void)=(void (*)(void))(uintptr_t)WORD(0x200004cc);
    callback();
    (void)opencfw_boot_thread_priority_set(opencfw_boot_thread_current(),48);
}
void opencfw_provider_42e278(void) {
    opencfw_provider_42e53c();
    opencfw_boot_manager_callback_dispatch();
}
void opencfw_boot_manager_signal_wait(uintptr_t thread,uint32_t bit) {
    /* ARM register LSL uses the low byte; shifts>=32 produce zero. */
    uint32_t shift=bit&255,mask=shift<32?1u<<shift:0;
    (void)opencfw_provider_41623a(thread,0x800000);
    uint32_t result=opencfw_provider_416590(WORD(0x20000510),mask,1,20000);
    if ((result&mask)!=mask)
        opencfw_provider_4176ce(1,"task.manager",
            "D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\bootloader\\threads\\thread_manager.c",
            "_thread_sync",0x87,"thread sync failed:0x%x, task:%d",result,(uint8_t)bit);
}
void opencfw_provider_42e2ea(void) {
    opencfw_boot_manager_signal_wait(WORD(0x200004d4),1);
}
