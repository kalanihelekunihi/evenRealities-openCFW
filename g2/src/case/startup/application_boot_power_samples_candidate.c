/* SPDX-License-Identifier: MIT
 * Native CASE 0x08009ff0 temperature and 0x0800a01e battery sample.
 */
#include <stdint.h>
extern int32_t case_init_pmic_read_register(uint32_t,uint8_t *); /* 0xa124 */
extern int32_t case_policy_timer_query(uint32_t,uint32_t *); /* 0xa074 */
int32_t case_boot_temperature_sample(uint32_t *out)
{
    uint8_t raw=0u;
    if(case_init_pmic_read_register(6u,&raw)!=0)return -1;
    *out=((uint32_t)raw*5u)-400u;
    return 0;
}
/* Dedup (0x0800a01e): case_boot_battery_sample is an alias of case_policy_elapsed (startup/application_policy_timer_query_candidate.c). */
extern int32_t case_boot_battery_sample(uint32_t *out);
/* Dedup (0x08009ff0): case_binary_14_read_a (was legacy-default/binary_value_readers_candidate.c). */
uint32_t case_binary_14_read_a(uint32_t *out) __attribute__((alias("case_boot_temperature_sample")));
