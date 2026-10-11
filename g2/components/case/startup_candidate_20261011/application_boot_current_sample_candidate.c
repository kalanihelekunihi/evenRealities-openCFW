/* SPDX-License-Identifier: MIT
 * Native CASE 0x08009f18 current sample and 0x0800a3ba sign conversion.
 */
#include <stdint.h>
extern int32_t case_init_pmic_read_register(uint32_t,uint8_t *); /* 0xa124 */
extern int32_t case_policy_timer_query(uint32_t,uint32_t *); /* 0xa074 */
extern uint32_t case_policy_sensor_divide(uint32_t,uint32_t); /* 0x0160 */
int32_t case_boot_current_sample(uint32_t *out)
{
    uint8_t config=0u;
    uint32_t raw=0u;
    if(case_init_pmic_read_register(0xabu,&config)!=0)return -1;
    if(case_policy_timer_query(14u,&raw)!=0)return -1;
    uint32_t value=(uint16_t)raw;
    if((value&0x8000u)!=0u)value=0u-(uint16_t)(0x10000u-value);
    uint32_t scale;
    if((config>>6)!=0u)scale=1600u;
    else if(config!=0u)scale=3815u;
    else { *out=0x1e240u;return 0; }
    uint32_t product=value*scale;
    uint32_t negative=(product>>31)!=0u;
    uint32_t magnitude=negative?(0u-product):product;
    uint32_t quotient=case_policy_sensor_divide(magnitude,10000u);
    *out=negative?(0u-quotient):quotient;
    return 0;
}
