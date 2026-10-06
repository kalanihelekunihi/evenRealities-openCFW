/* SPDX-License-Identifier: MIT. Reconstruction of 42e224/42e2f8/42e39a. */
#include "manager_task.h"
extern void opencfw_provider_42e254(void);
extern void opencfw_provider_42e278(void);
extern void opencfw_provider_42e2ea(void);
extern uint32_t opencfw_provider_4162c4(uint32_t mask,uint32_t options,uint32_t ticks);
extern uint32_t opencfw_provider_4160e8(void);
extern uint32_t opencfw_provider_42dca2(const void *message);
extern void opencfw_provider_4176ce(uint32_t level,const char *module,const char *file,const char *function,uint32_t line,const char *format,...);
static const char file[]="D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\bootloader\\threads\\thread_manager.c";
static const char module[]="task.manager";
uint32_t opencfw_boot_manager_needs_update(void) {
    uint32_t flag=*(volatile const uint32_t *)(uintptr_t)0x7fe000;
    opencfw_provider_4176ce(3,module,file,"is_need_updata_image",0x40,"otaFlag = 0x%x",flag);
    return flag==0x55555555;
}
__attribute__((noinline))
void opencfw_boot_manager_flags_noop(uint32_t flags) {
    (void)flags;
    /* Original 42e39a is BX LR. Memory clobber preserves this observation point. */
    __asm__ volatile("" :: "r"(flags) : "memory");
}
__attribute__((noinline))
void opencfw_boot_manager_setup_noop(void) {
    __asm__ volatile("" ::: "memory");
}
void opencfw_boot_manager_task(void *argument) {
    (void)argument;
    volatile uint32_t previous_tick=0;
    volatile uint32_t message[10];
    opencfw_provider_42e254();
    opencfw_boot_manager_setup_noop();
    opencfw_provider_42e278();
    opencfw_provider_42e2ea();
    uint32_t needs_update=opencfw_boot_manager_needs_update();
    opencfw_provider_4176ce(3,module,file,"thread_manager",needs_update?0xd1:0xd8,
        needs_update?"need updata firmware":"DO NOT need updata firmware, GO TO APP");
    for (uint32_t i=0;i<10;i++) message[i]=0;
    message[0]=needs_update?1:0;
    (void)opencfw_provider_42dca2((const void *)message);
    for (;;) {
        uint32_t flags=opencfw_provider_4162c4(0xffffff,0,60000);
        uint32_t now=opencfw_provider_4160e8();
        if (flags!=0 && flags<0x80000000) {
            opencfw_boot_manager_flags_noop(flags);
            continue;
        }
        if ((uint32_t)(now-previous_tick)>=60000) previous_tick=now;
        /* Original updates only its local baseline; no periodic action follows. */
    }
}
