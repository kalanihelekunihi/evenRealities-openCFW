/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800ab70 idle transport event callback.
 */
#include <stdint.h>
extern void case_boot_irq_hall_prepare(uint32_t mode); /* 0x3848 */
extern int32_t case_policy_event_signal(uint32_t task,uint32_t value); /* 0xaaf0 */
void case_boot_transport_cb_ab70(void)
{
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0x2000087cu;
    if(state[16u]!=0u || state[17u]!=0u || state[2u]!=0u || state[0u]==3u)return;
    case_boot_irq_hall_prepare(0u);
    state[2u]=1u;
    uint32_t task=*(volatile uint32_t *)(uintptr_t)0x200000c8u;
    (void)case_policy_event_signal(task,3000u);
}
