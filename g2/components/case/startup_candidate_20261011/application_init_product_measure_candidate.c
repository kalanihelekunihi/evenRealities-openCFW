/* SPDX-License-Identifier: MIT
 * Native CASE 0x08009ebc: product measurement register 4 scaled to 0..100.
 */
#include <stdint.h>
extern int32_t case_policy_timer_query(uint32_t reg,uint32_t *out); /* 0xa074 */
extern uint32_t case_policy_sensor_divide(uint32_t value,uint32_t divisor); /* 0x0160 */
int32_t case_init_read_product_byte(uint32_t *out)
{
    uint32_t raw=0u;
    if(case_policy_timer_query(4u,&raw)!=0)return -1;
    uint32_t scaled=case_policy_sensor_divide(raw*100u,99u<<8);
    if(scaled>=100u)scaled=100u;
    *out=scaled;
    return 0;
}
