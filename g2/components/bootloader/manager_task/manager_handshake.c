/* SPDX-License-Identifier: MIT. Source for42e3e0/42e412/42e444 and direct
 * DFU control adapters42dd9a/42dda4. Timeouts remain raw ticks. */
#include <stdint.h>
#include <stddef.h>
#include "../flags_runtime/flags_runtime.h"
extern uint32_t opencfw_provider_41652e(uint32_t *,uint32_t);
extern void opencfw_provider_4176ce(uint32_t,const char *,const char *,const char *,uint32_t,const char *,...);
static const char file[]="D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\bootloader\\threads\\thread_manager.c";
static uint32_t task_bit(uint32_t task) {uint32_t shift=task&255;return shift<32?1u<<shift:0;}
void opencfw_boot_manager_start_wait(uint32_t task) {
    while (!((uint32_t)opencfw_provider_4162c4(0x800000,1,UINT32_MAX,0)&0x800000)){}
    opencfw_provider_4176ce(3,"task.manager",file,"thread_manager_sysstart_sync",0x12b,"thread %d sync start:",(uint8_t)task);
}
void opencfw_boot_manager_start_done(uint32_t task) {
    opencfw_provider_4176ce(3,"task.manager",file,"thread_manager_sysstart_sync_end",0x139,"thread %d sync end",(uint8_t)task);
    (void)opencfw_provider_41652e(*(uint32_t *volatile *)(uintptr_t)0x20000510,task_bit(task));
}
void opencfw_boot_manager_start_signal(uint32_t task) {
    (void)opencfw_provider_41652e(*(uint32_t *volatile *)(uintptr_t)0x20000510,task_bit(task));
}
void opencfw_boot_dfu_control_one(void) {opencfw_boot_manager_start_wait(1);}
void opencfw_boot_dfu_control_two(void) {opencfw_boot_manager_start_done(1);}
