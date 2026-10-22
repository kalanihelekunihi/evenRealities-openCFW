#include "../semantic-strings/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800d178 service command startup sequence.
 * Log format at 0x0800d1ac remains linker-owned product data.
 */
#include <stdint.h>
extern void case_policy_sensor_command(uint32_t channel,uint32_t value); /* 0x99e8 */
extern uint32_t case_legacy_logger(const char *format,...); /* 0x9170 */
/* Stock 0x0800D178 (case_init_service_start) */
void case_init_service_start(void)
{
    case_policy_sensor_command(5u,3u);
    case_policy_sensor_command(6u,0x81u);
    case_policy_sensor_command(3u,0xaeu);
    case_policy_sensor_command(4u,0xaeu);
    case_policy_sensor_command(7u,0x20u);
    (void)case_legacy_logger((const char *)(uintptr_t)CASE_STRING_ADDR(0800d1ac));
}
