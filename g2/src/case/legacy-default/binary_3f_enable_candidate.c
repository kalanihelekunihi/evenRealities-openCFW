/* SPDX-License-Identifier: MIT
 * Isolated stock 0x0800d154 output-enable wrapper. The setter is a lower contract.
 */
#include <stdint.h>

extern uint32_t case_binary_3f_set(uint32_t index, uint32_t value);

/* Stock 0x0800D154 (aging_indicator_apply) */
uint32_t case_binary_3f_enable(void)
{
    case_binary_3f_set(3u, 0xaeu);
    case_binary_3f_set(4u, 0xaeu);
    case_binary_3f_set(5u, 3u);
    return case_binary_3f_set(6u, 0x81u);
}
/* Dedup (0x0800d154): case_policy_service_idle (was startup/application_policy_shared_aliases_candidate.c). */
__typeof__(case_binary_3f_enable) case_policy_service_idle __attribute__((alias("case_binary_3f_enable")));
