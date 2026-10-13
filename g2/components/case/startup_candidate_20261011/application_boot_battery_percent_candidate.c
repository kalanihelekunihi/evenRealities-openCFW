/* SPDX-License-Identifier: MIT
 * Native CASE 0x08009ebc battery percentage conversion.
 */
#include "case_battery_measurement_contract.h"
extern int32_t case_policy_timer_query(uint32_t,uint32_t *); /* 0xa074 */
extern uint32_t case_policy_sensor_divide(uint32_t,uint32_t); /* 0x0160 */
int32_t case_boot_battery_percent(uint32_t *out)
{
    uint32_t raw=0u;
    if(case_policy_timer_query(4u,&raw)!=0)return -1;
    uint32_t normalized=((raw>>8)<<8)|(uint8_t)raw;
    uint32_t percent=case_policy_sensor_divide(normalized*100u,99u<<8);
    if(percent>=100u)percent=100u;
    *out=percent;
    return 0;
}
