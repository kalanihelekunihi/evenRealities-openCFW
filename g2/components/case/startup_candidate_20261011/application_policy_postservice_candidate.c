/* SPDX-License-Identifier: MIT
 * Composed stock post-service path 0x08007884 through the 0x08007ed6 loop
 * edge. The enclosing task owns state R4, prior status stack slots and the
 * recurring 0x08007214 body; this composition returns at that edge.
 */
#include <stdint.h>
extern uint32_t case_policy_status_7884(volatile uint8_t *state,
                                        volatile uint8_t *left,volatile uint8_t *right,
                                        uint8_t old_left,uint8_t old_right);
extern void case_policy_no_reply_79b0(volatile uint8_t *state);
extern void case_policy_no_reply_after_79b4(volatile uint8_t *state);
extern uint32_t case_policy_ota_probe_7abc(volatile uint8_t *state,volatile uint8_t *left);
extern void case_policy_event_idle_7b2e(volatile uint8_t *state);
extern uint32_t case_policy_tail_7e90(volatile uint8_t *state);
extern void case_policy_wait(uint32_t ticks);

uint32_t case_policy_postservice_7884(volatile uint8_t *state,
                                      volatile uint8_t *left,
                                      volatile uint8_t *right,
                                      uint8_t old_left,uint8_t old_right)
{
    uint32_t refresh=case_policy_status_7884(state,left,right,old_left,old_right);
    if(refresh!=0u)case_policy_no_reply_79b0(state);
    else case_policy_no_reply_after_79b4(state);
    (void)case_policy_ota_probe_7abc(state,left);
    case_policy_event_idle_7b2e(state);
    if(case_policy_tail_7e90(state)!=0u)return 1u;
    case_policy_wait(1000u);
    return 0u;
}
