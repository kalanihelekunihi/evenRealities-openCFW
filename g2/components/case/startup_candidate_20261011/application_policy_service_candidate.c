/* SPDX-License-Identifier: MIT
 * Stock task loop service gate, 0x080077b0 through 0x080077e8.
 * The caller at 0x08007200 owns state R4 and the stack context. This is an
 * internal transition, not a callable stock function at 0x080077b0.
 */
#include <stdint.h>

extern void case_policy_wait(uint32_t ticks);       /* 0x0800a7b0 */
extern void case_policy_service_idle(void);         /* 0x0800d154 */
extern void case_policy_service_update(void);       /* 0x0800ce34 */

/* Return 0 at the 0x08007eda loop tail, 1 at the 0x080077e8 continuation.
 * The latter retains the pre-update snapshot for the caller's change test.
 */
uint32_t case_policy_service_gate_77b0(volatile uint8_t *state,
                                       uint8_t *previous_left,
                                       uint8_t *previous_right)
{
    volatile uint8_t *shared=(volatile uint8_t *)(uintptr_t)0x200000b8u;
    if(state[0x15u]==0u){
        state[0x10u]=1u;
        state[0x11u]=1u;
        case_policy_service_idle();
        return 0u;
    }
    *previous_left=state[0x10u];
    *previous_right=state[0x11u];
    while(shared[4u]!=0u)case_policy_wait(50u);
    shared[4u]=1u;
    case_policy_service_update();
    shared[4u]=0u;
    return 1u;
}
