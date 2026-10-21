/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800af70 initial lists and 0x0800c0b8 registry.
 */
#include <stdint.h>
extern void case_policy_task_list_initialize(uint32_t list);
void case_boot_first_task_prepare(void)
{
    for(uint32_t i=0u;i<56u;++i)
        case_policy_task_list_initialize(0x20000ff4u+i*20u);
    case_policy_task_list_initialize(0x20001454u);
    case_policy_task_list_initialize(0x20001468u);
    case_policy_task_list_initialize(0x2000147cu);
    case_policy_task_list_initialize(0x20001490u);
    case_policy_task_list_initialize(0x200014a4u);
    volatile uint32_t *scheduler=(volatile uint32_t *)(uintptr_t)0x20000128u;
    scheduler[13]=0x20001454u;
    scheduler[14]=0x20001468u;
}
void case_boot_scheduler_register(uint32_t scheduler,const char *name)
{
    volatile uint32_t *registry=(volatile uint32_t *)(uintptr_t)0x20000fb4u;
    for(uint32_t i=0u;i<8u;++i){
        if(registry[i*2u]==0u){
            registry[i*2u]=(uint32_t)(uintptr_t)name;
            registry[i*2u+1u]=scheduler;
            return;
        }
    }
}
