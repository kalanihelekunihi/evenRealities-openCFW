#include "../semantic_strings_candidate_20261011/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Native CASE 0x12e4 failed activation cleanup.
 */
#include <stdint.h>
extern int32_t case_policy_task_reset(uint32_t task); /* 0xab26 */
extern void case_policy_led_left_clear(uint32_t value); /* 0x6b80 */
extern void case_policy_led_right_clear(uint32_t value); /* 0x6b98 */
extern uint32_t case_legacy_logger(const char *format,...); /* 0x9170 */
void case_policy_box_failure_reset(void)
{
    uint32_t task=*(volatile uint32_t *)(uintptr_t)0x200000d0u;
    (void)case_policy_task_reset(task);
    case_policy_led_left_clear(0u);
    case_policy_led_right_clear(0u);
    *(volatile uint8_t *)(uintptr_t)0x2000087eu=0u;
    if(*(volatile uint8_t *)(uintptr_t)0x200000bfu==0u){
        (void)case_legacy_logger((const char *)(uintptr_t)CASE_STRING_ADDR(0800131c));
        (void)case_legacy_logger((const char *)(uintptr_t)CASE_STRING_ADDR(08001330));
    }
}
