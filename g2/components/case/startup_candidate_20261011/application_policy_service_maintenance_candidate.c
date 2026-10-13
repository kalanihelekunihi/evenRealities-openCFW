#include "case_logger_contract.h"
#include "../semantic_strings_candidate_20261011/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Native CASE 0x080018e4 periodic left/right charging and status service.
 */
#include <stdint.h>
extern void case_policy_ota_checksum(uint8_t *,uint32_t); /* 0x9b70 */
extern uint32_t case_policy_send_probe(uint32_t,const uint8_t *,uint32_t,uint32_t); /* 0x258c */
extern uint32_t case_policy_parse_probe(uint32_t); /* 0x1e94 */
extern uint32_t case_policy_sensor_divide(uint32_t,uint32_t); /* 0x0160 */
static uint32_t rd32(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr32(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static uint16_t rd16(uint32_t a){return *(volatile uint16_t *)(uintptr_t)a;}
static uint32_t rem(uint32_t value,uint32_t divisor){return value-case_policy_sensor_divide(value,divisor)*divisor;}
static void logline(uint32_t a){(void)case_policy_log(a);(void)case_policy_log(CASE_STRING_ADDR(08001b08));}
void case_policy_service_maintenance(void)
{
    const uint32_t base=0x2000087cu;
    volatile uint8_t *s=(volatile uint8_t *)(uintptr_t)base;
    volatile const uint8_t *quiet=(volatile const uint8_t *)(uintptr_t)0x200000bfu;
    uint32_t left_present=s[0x10u],right_present=s[0x11u];
    if(left_present==0u && right_present==0u)return;
    uint32_t left_allowed=1u,right_allowed=1u;
    if(*(volatile const uint8_t *)(uintptr_t)0x20000105u!=0u &&
       (left_present==0u || right_present==0u)){
        left_allowed=0u;right_allowed=0u;
        uint32_t n=rd32(base+0x0cu);
        if((n<5u || rem(n,20u)==0u) && *quiet==0u)
            {(void)case_policy_log(CASE_STRING_ADDR(08001adc),left_present,right_present);(void)case_policy_log(CASE_STRING_ADDR(08001b08));}
    }
    if(left_present!=0u && s[0x31u]!=0u){
        uint32_t ticks=rd16(base+0x38u);
        if(ticks!=0u){
            left_allowed=0u;
            if(rem(ticks,30u)==0u && *quiet==0u){
                (void)case_policy_log(s[0x33u]==0u?CASE_STRING_ADDR(08001b38):CASE_STRING_ADDR(08001b0c),ticks);
                (void)case_policy_log(CASE_STRING_ADDR(08001b08));
            }
        }
    }
    if(right_present!=0u && s[0x4du]!=0u){
        uint32_t ticks=rd16(base+0x54u);
        if(ticks!=0u){
            right_allowed=0u;
            if(rem(ticks,30u)==0u && *quiet==0u){
                (void)case_policy_log(s[0x4fu]==0u?CASE_STRING_ADDR(08001b98):CASE_STRING_ADDR(08001b6c),ticks);
                (void)case_policy_log(CASE_STRING_ADDR(08001b08));
            }
        }
    }
    uint8_t packet[8]={0x13u,0u,0u,1u,0u,0u,0u,0u};
    packet[4]=(uint8_t)((s[3u]<<7)|s[1u]);
    packet[5]=s[4u]!=0u?1u:2u;
    if(left_present!=0u && left_allowed!=0u && rem(rd32(base+0x44u),15u)==0u){
        packet[2]=0u;
        case_policy_ota_checksum(packet,7u);
        (void)case_policy_send_probe(1u,packet,7u,1u);
        wr32(base+0x48u,rd32(base+0x48u)+1u);
        if(case_policy_parse_probe(1u)==0x13u){
            wr32(base+0x40u,0u);wr32(base+0x44u,0u);
            wr32(base+0x3cu,rd32(base+0x3cu)+1u);
        }else{
            wr32(base+0x3cu,0u);wr32(base+0x40u,rd32(base+0x40u)+1u);
            if(*quiet==0u)logline(CASE_STRING_ADDR(08001bd4));
        }
    }
    if(right_present!=0u && right_allowed!=0u && rem(rd32(base+0x60u),15u)==0u){
        packet[2]=1u;
        case_policy_ota_checksum(packet,7u);
        (void)case_policy_send_probe(0u,packet,7u,1u);
        wr32(base+0x64u,rd32(base+0x64u)+1u);
        if(case_policy_parse_probe(0u)==0x13u){
            wr32(base+0x5cu,0u);wr32(base+0x60u,0u);
            wr32(base+0x58u,rd32(base+0x58u)+1u);
        }else{
            wr32(base+0x5cu,rd32(base+0x5cu)+1u);wr32(base+0x58u,0u);
            if(*quiet==0u)logline(CASE_STRING_ADDR(08001bf8));
        }
    }
}
