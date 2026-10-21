#include "case_logger_contract.h"
#include "../semantic-strings/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Native 0x08003a00 fake-standby state change and 0x080013b8 clear.
 */
#include "case_side_state_contract.h"
extern void case_policy_task_cancel(uint32_t task); /* 0x0800aa00 */
void case_policy_fake_standby_set(uint32_t side)
{
    case_boot_button_mode_reset(side);
}
void case_policy_fake_standby_clear(void)
{
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0x2000087cu;
    volatile uint8_t *shared=(volatile uint8_t *)(uintptr_t)0x200000b8u;
    state[0x17u]=0u;
    case_policy_task_cancel(*(volatile uint32_t *)(void *)(shared+0x2cu));
    case_policy_task_cancel(*(volatile uint32_t *)(void *)(shared+0x30u));
    case_policy_task_cancel(*(volatile uint32_t *)(void *)(shared+0x28u));
    shared[3u]=0u;
    if(shared[7u]==0u){case_policy_log(CASE_STRING_ADDR(080013f4));case_policy_log(CASE_STRING_ADDR(08001404));}
}
