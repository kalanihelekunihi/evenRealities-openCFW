/* SPDX-License-Identifier: MIT
 * Native CASE 0x08009e0c repair, 0x0800a0ea arm,
 * 0x0800a13a write adapter, and 0x9ef8/0x9f80/0xa046/a124 probe chain.
 */
#include <stdint.h>
extern uint32_t case_init_selfcheck_read(uint32_t reg,uint8_t *out,uint32_t count); /* 0x35b8 */
extern uint32_t case_init_pmic_write(uint32_t reg,uint32_t value); /* 0x39c8 */
extern void case_policy_timer_delay(uint32_t count); /* 0xa148 */
__attribute__((noinline)) int32_t case_init_pmic_write_register(uint32_t reg,const uint8_t *value)
{
    (void)case_init_pmic_write(reg,*value);
    return 0;
}
static int32_t case_init_pmic_arm(void)
{
    uint8_t value=0x30u;
    if(case_init_pmic_write_register(8u,&value)!=0)return -1;
    case_policy_timer_delay(21u);
    value=0xf0u;
    if(case_init_pmic_write_register(8u,&value)!=0)return -1;
    case_policy_timer_delay(11u);
    return 0;
}
__attribute__((noinline)) int32_t case_init_pmic_read_register(uint32_t reg,uint8_t *out)
{
    (void)case_init_selfcheck_read(reg,out,1u);
    return 0;
}
__attribute__((noinline)) int32_t case_init_pmic_identify(uint32_t *out)
{
    uint8_t value=0u;
    if(case_init_pmic_read_register(0u,&value)!=0)return -1;
    *out=value;
    return 0;
}
__attribute__((noinline)) int32_t case_init_pmic_status(void)
{
    uint8_t value=0u;
    if(case_init_pmic_read_register(8u,&value)!=0)return -1;
    if(value!=0u)return 1;
    if(case_init_pmic_read_register(11u,&value)!=0)return -1;
    if((value&0x80u)==0u)return 2;
    volatile uint8_t *expected=(volatile uint8_t *)(uintptr_t)0x2000002au;
    for(uint32_t i=0u;i<80u;++i){
        if(case_init_pmic_read_register((uint8_t)(16u+i),&value)!=0)return -1;
        if(value!=expected[i])return 3;
    }
    return 0;
}
__attribute__((noinline)) int32_t case_init_pmic_repair(void)
{
    if(case_init_pmic_arm()<0)return -1;
    volatile uint8_t *expected=(volatile uint8_t *)(uintptr_t)0x2000002au;
    for(uint32_t i=0u;i<80u;++i)
        if(case_init_pmic_write_register((uint8_t)(16u+i),(const uint8_t *)(uintptr_t)(expected+i))!=0)return -1;
    uint8_t value=0x80u;
    if(case_init_pmic_write_register(11u,&value)!=0)return -1;
    value=0u;
    if(case_init_pmic_write_register(10u,&value)!=0)return -1;
    value=0x30u;
    if(case_init_pmic_write_register(8u,&value)!=0)return -1;
    case_policy_timer_delay(21u);
    value=0u;
    if(case_init_pmic_write_register(8u,&value)<0)return -1;
    case_policy_timer_delay(11u);
    for(uint32_t attempt=0u;attempt<50u;++attempt){
        case_policy_timer_delay(101u);
        (void)case_init_pmic_read_register(0xa7u,&value);
        if(((value>>2)&3u)==3u)return 0;
    }
    (void)case_init_pmic_arm();
    return -1;
}
int32_t case_init_pmic_probe_once(void)
{
    uint32_t identity=0u;
    if(case_init_pmic_identify(&identity)!=0)return -1;
    if(identity!=0xa0u)return -2;
    int32_t state=case_init_pmic_status();
    if(state<0)return state;
    if(state>0){
        int32_t result=case_init_pmic_repair();
        if(result<0)return result;
    }
    return 0;
}
