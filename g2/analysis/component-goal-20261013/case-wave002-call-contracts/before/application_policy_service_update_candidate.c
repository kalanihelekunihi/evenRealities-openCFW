#include "../semantic_strings_candidate_20261011/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Source reduction of native CASE 0x0800ce34..0x0800d0ea.
 * The ADC/time/IRQ descendants remain typed platform contracts.
 */
#include <stdint.h>
extern void case_policy_sensor_command(uint32_t channel,uint32_t value); /* 0x99e8 */
extern void case_policy_sensor_delay(uint32_t amount); /* 0xa7b0 */
extern uint32_t case_policy_sensor_sample(void); /* 0x2edc */
extern uint32_t case_policy_sensor_divide(uint32_t value,uint32_t divisor); /* 0x0160 */
extern void case_policy_sensor_prepare(void); /* 0xd250 */
extern void case_policy_idle_clear(void); /* 0x9a14, existing source owner */
extern void case_policy_log(uint32_t message); /* 0x9170 */

static uint32_t sense_1000(void)
{
    volatile uint8_t *divisor=(volatile uint8_t *)(uintptr_t)0x20000106u;
    return case_policy_sensor_divide(case_policy_sensor_sample()*1000u,*divisor);
}
static void count_low(volatile uint8_t *counter,volatile uint8_t *state,
                      volatile uint8_t *quiet,uint32_t first_log)
{
    if(*counter<6u){++*counter;return;}
    if(*quiet==0u){case_policy_log(first_log);case_policy_log(CASE_STRING_ADDR(0800d128));}
    state[0]=1u;state[2]=1u;
}
void case_policy_service_update(void)
{
    volatile uint8_t *s=(volatile uint8_t *)(uintptr_t)0x2000087cu;
    volatile uint8_t *guard=(volatile uint8_t *)(uintptr_t)0x20000105u;
    volatile uint8_t *counters=(volatile uint8_t *)(uintptr_t)0x2000007cu;
    volatile uint8_t *quiet=(volatile uint8_t *)(uintptr_t)0x200000bfu;
    uint32_t left_ok=1u,right_ok=1u,left_low=0u,right_low=0u;

    if(s[0x10u]!=0u && s[0x31u]==0u && (*guard==0u || s[0x11u]!=0u)){
        case_policy_sensor_command(5u,3u);
        case_policy_sensor_command(3u,0xafu);
        case_policy_sensor_command(6u,0x8bu);
        case_policy_sensor_delay(3u);
        uint32_t value=sense_1000();
        if(value>120u){s[0x10u]=1u;left_ok=0u;counters[0]=0u;}
        else if(value<80u)left_low=1u;
    }
    if(s[0x11u]!=0u && s[0x4du]==0u && (*guard==0u || s[0x10u]!=0u)){
        case_policy_sensor_command(5u,3u);
        case_policy_sensor_command(4u,0xafu);
        case_policy_sensor_command(6u,0x8du);
        case_policy_sensor_delay(3u);
        uint32_t value=sense_1000();
        if(value>120u){s[0x11u]=1u;right_ok=0u;counters[1]=0u;}
        else if(value<80u)right_low=1u;
    }
    if((left_ok|right_ok)==0u)return;
    case_policy_sensor_prepare();
    if(left_ok!=0u){
        if(s[0x10u]!=0u)case_policy_sensor_command(6u,0xc1u);
        case_policy_sensor_command(3u,0xaeu);case_policy_sensor_delay(3u);
    }
    if(right_ok!=0u){
        if(s[0x11u]!=0u)case_policy_sensor_command(6u,0xc1u);
        case_policy_sensor_command(4u,0xaeu);case_policy_sensor_delay(3u);
    }
    if(left_ok!=0u){
        case_policy_sensor_command(6u,0x85u);case_policy_sensor_delay(2u);
        if(case_policy_sensor_sample()>620u)s[0x10u]=1u;
        else{
            case_policy_sensor_command(5u,11u);case_policy_sensor_delay(3u);
            s[0x10u]=(uint8_t)(case_policy_sensor_sample()<620u);
        }
        if(s[0x10u]!=0u && left_low!=0u)
            count_low(counters,s+0x31u,quiet,CASE_STRING_ADDR(0800d100));
        else counters[0]=0u;
        if(s[0x10u]!=0u && s[0x11u]!=0u && s[0x31u]!=0u && s[0x33u]==0u){
            case_policy_sensor_command(5u,3u);case_policy_sensor_command(6u,0x81u);
            case_policy_sensor_command(7u,0x20u);case_policy_sensor_command(3u,0xafu);
            case_policy_sensor_delay(5u);case_policy_sensor_command(3u,0xaeu);
        }
    }
    if(right_ok!=0u){
        case_policy_sensor_command(6u,0x87u);case_policy_sensor_delay(2u);
        if(case_policy_sensor_sample()>620u)s[0x11u]=1u;
        else{
            case_policy_sensor_command(5u,7u);case_policy_sensor_delay(3u);
            s[0x11u]=(uint8_t)(case_policy_sensor_sample()<620u);
        }
        if(s[0x11u]!=0u && right_low!=0u)
            count_low(counters+1u,s+0x4du,quiet,CASE_STRING_ADDR(0800d12c));
        else counters[1]=0u;
        if(s[0x10u]!=0u && s[0x11u]!=0u && s[0x4du]!=0u && s[0x4fu]==0u){
            case_policy_sensor_command(5u,3u);case_policy_sensor_command(6u,0x81u);
            case_policy_sensor_command(7u,0x20u);case_policy_sensor_command(4u,0xafu);
            case_policy_sensor_delay(5u);case_policy_sensor_command(4u,0xaeu);
        }
    }
    case_policy_idle_clear();
}
