/* SPDX-License-Identifier: MIT
 * Stock 0x08007e90-0x08007ed6 policy tail before the recurring 0x08007214
 * loop body. No full-task claim follows from this bounded transition.
 */
#include <stdint.h>
extern void case_policy_task_notify(uint32_t task); /* 0x0800aa24 */
extern void case_policy_flash_write(uint32_t address,uint32_t value,uint32_t count);
extern void case_init_wake_mask(uint32_t mask);
extern void case_init_wake_config(uint32_t mode);
extern void case_policy_wake_arm(uint32_t a,uint32_t b); /* 0x080050e8 */
extern void case_policy_system_reset(void); /* 0x0800b600 */
uint32_t case_policy_tail_7e90(volatile uint8_t *state)
{
    volatile uint8_t *shared=(volatile uint8_t *)(uintptr_t)0x200000b8u;
    if(state[0x17u]<30u)return 0u;
    if(shared[3u]==0u){
        case_policy_task_notify(*(volatile uint32_t *)(void *)(shared+0x2cu));
        case_policy_task_notify(*(volatile uint32_t *)(void *)(shared+0x30u));
        case_policy_task_notify(*(volatile uint32_t *)(void *)(shared+0x28u));
        shared[3u]=1u;
    }
    case_policy_flash_write(0x20000948u,7u,4u);
    case_init_wake_mask(0x2bu);case_init_wake_config(0x2028u);
    case_policy_wake_arm(0u,1u);
    case_policy_system_reset();
    return 1u;
}
