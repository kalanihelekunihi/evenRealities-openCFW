/* SPDX-License-Identifier: MIT
 * Source-owned idle-state transition from the internal CASE policy loop
 * 0x08007214. The enclosing task starts at 0x08007200, keeps R4 pointing
 * to 0x2000087c and carries R6 as its idle counter. This function is only
 * the all-idle branch through the OTA decision at 0x08007376.
 */
#include <stdint.h>
extern void case_policy_periodic_power_check(void); /* 0x08002cb8 */
extern void case_policy_standby_idle(void); /* native 0x0800726a sequence; not yet reduced */
struct case_policy_idle_context {uint32_t state_address;uint32_t idle_counter;};
uint32_t case_policy_idle_step_7214(struct case_policy_idle_context *context)
{
    volatile uint8_t *s=(volatile uint8_t *)(uintptr_t)context->state_address;
    volatile uint32_t *seconds=(volatile uint32_t *)(uintptr_t)(s+8u);
    volatile uint32_t *iterations=(volatile uint32_t *)(uintptr_t)(s+12u);
    uint32_t old_seconds=*seconds;
    *iterations=*iterations+1u;
    *seconds=old_seconds+1u;
    if(old_seconds%5u==0u && *(volatile uint8_t *)(uintptr_t)0x200000beu!=0u)
        case_policy_periodic_power_check();
    if(s[4u]!=0u || s[3u]!=0u || s[0x10u]!=0u || s[0x11u]!=0u){
        context->idle_counter=0u; /* stock 0x08007250 */
        return 0u;
    }
    uint32_t old_idle=context->idle_counter;
    context->idle_counter=(old_idle+1u)&0xffu;
    if(old_idle==10u)case_policy_standby_idle();
    return 1u;
}
