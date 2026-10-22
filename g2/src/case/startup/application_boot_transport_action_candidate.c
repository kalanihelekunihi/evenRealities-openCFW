#include "case_logger_contract.h"
#include "../semantic-strings/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Native CASE 0x08001c1c side transport request/reply state update.
 * The eight packet seed bytes at 0x1d04 remain product-data source input.
 */
#include <stdint.h>
extern const uint8_t case_boot_transport_action_template[8]; /* stock 0x1d04 */
extern void case_policy_ota_checksum(uint8_t *packet,uint32_t count); /* 0x9b70 */
extern uint32_t case_policy_send_probe(uint32_t side,const uint8_t *packet,uint32_t count,uint32_t reply); /* 0x258c */
extern uint32_t case_policy_parse_probe(uint32_t side); /* 0x1e94 */

/* Stock 0x08001C1C (glasses_status_force_refresh) */
void case_boot_transport_action(uint32_t left,uint32_t right)
{
    if((left|right)==0u)return;
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0x2000087cu;
    volatile uint8_t *quiet=(volatile uint8_t *)(uintptr_t)0x200000bfu;
    uint8_t packet[8];
    for(uint32_t i=0u;i<8u;++i)packet[i]=case_boot_transport_action_template[i];
    packet[4u]=(uint8_t)((state[3u]<<7u)|state[1u]);
    packet[5u]=state[4u]!=0u?1u:2u;
    if(left!=0u && state[16u]!=0u){
        packet[2u]=0u;
        case_policy_ota_checksum(packet,7u);
        case_policy_send_probe(1u,packet,7u,1u);
        (*(volatile uint32_t *)(void *)(state+0x48u))++;
        if(case_policy_parse_probe(1u)==19u){
            *(volatile uint32_t *)(void *)(state+0x40u)=0u;
            *(volatile uint32_t *)(void *)(state+0x44u)=0u;
            (*(volatile uint32_t *)(void *)(state+0x3cu))++;
        }else{
            *(volatile uint32_t *)(void *)(state+0x3cu)=0u;
            (*(volatile uint32_t *)(void *)(state+0x40u))++;
            if(*quiet==0u){(void)case_policy_log(CASE_STRING_ADDR(08001d14));(void)case_policy_log(CASE_STRING_ADDR(08001d3c));}
        }
    }
    if(right!=0u && state[17u]!=0u){
        packet[2u]=1u;
        case_policy_ota_checksum(packet,7u);
        case_policy_send_probe(0u,packet,7u,1u);
        (*(volatile uint32_t *)(void *)(state+0x64u))++;
        if(case_policy_parse_probe(0u)==19u){
            *(volatile uint32_t *)(void *)(state+0x5cu)=0u;
            *(volatile uint32_t *)(void *)(state+0x60u)=0u;
            (*(volatile uint32_t *)(void *)(state+0x58u))++;
        }else{
            *(volatile uint32_t *)(void *)(state+0x58u)=0u;
            (*(volatile uint32_t *)(void *)(state+0x5cu))++;
            if(*quiet==0u){(void)case_policy_log(CASE_STRING_ADDR(08001d40));(void)case_policy_log(CASE_STRING_ADDR(08001d3c));}
        }
    }
}
