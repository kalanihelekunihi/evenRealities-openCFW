/* SPDX-License-Identifier: MIT
 * Native CASE 0x9df4 PMIC prepare and 0x2c30/0x2c8e power gates.
 */
#include <stdint.h>
extern int32_t case_init_pmic_probe_once(void); /* 0xa046 */
extern void case_init_pmic_reset(uint32_t reg,uint32_t value); /* 0x39e4 */
extern uint32_t case_init_pmic_read(uint32_t reg,uint8_t *out,uint32_t count); /* 0x35d4 */
extern uint32_t case_init_secondary_write(uint32_t reg,uint32_t count,const uint8_t *value); /* 0x9004 */
/* Stock 0x08009DF4 (peripheral_init_retry) */
void case_init_pmic_prepare(void)
{
    for(uint32_t attempt=0u;attempt<4u;++attempt)
        if(case_init_pmic_probe_once()==0)break;
}
/* Stock 0x08002C30 (peripheral_mode_write_retry) */
void case_init_boost_set(uint32_t enabled)
{
    const uint8_t target=enabled?9u:8u;
    uint8_t observed=enabled?8u:9u;
    for(uint8_t attempt=0u;attempt<3u;++attempt){
        case_init_pmic_reset(21u,target);
        (void)case_init_pmic_read(21u,&observed,1u);
        if(observed==target)break;
    }
}
void case_init_power_set(uint32_t enabled)
{
    uint8_t value=enabled?0x3bu:0u;
    if(enabled){
        (void)case_init_secondary_write(5u,1u,&value);
        value=7u;
    }
    (void)case_init_secondary_write(4u,1u,&value);
}
