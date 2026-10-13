#include "case_logger_contract.h"
#include "../semantic_strings_candidate_20261011/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Stock 0x08007abc-0x08007b2e OTA probe gate and send. The native program
 * copies 12 product bytes at 0x08007e04 to task stack, then overrides byte 8
 * with 0x1e before sending nine bytes. The bytes require product source.
 */
#include <stdint.h>
extern const uint8_t case_policy_ota_probe_template[12]; /* product data contract */
extern void case_policy_wait(uint32_t ticks);
extern uint32_t case_policy_send_probe(uint32_t channel,const uint8_t *packet,uint32_t count,uint32_t reply); /* 0x0800258c */
extern uint32_t case_policy_parse_probe(uint32_t channel); /* 0x08001e94 */
uint32_t case_policy_ota_probe_7abc(volatile uint8_t *state,volatile uint8_t *left)
{
    volatile uint8_t *shared=(volatile uint8_t *)(uintptr_t)0x200000b8u;
    if(state[0x10u]==0u || state[0x11u]==0u ||
       *(volatile uint32_t *)(void *)(state+0x0cu)<=20u ||
       left[0x12u]<=50u || state[1u]<=20u || state[0x1bu]!=0u ||
       shared[4u]!=0u)return 0u;
    shared[4u]=1u;
    if(shared[7u]==0u){case_policy_log(CASE_STRING_ADDR(08007de0));case_policy_log(CASE_STRING_ADDR(08007b84));}
    case_policy_wait(100u);
    uint8_t packet[12];
    for(uint32_t i=0u;i<12u;i++)packet[i]=case_policy_ota_probe_template[i];
    packet[8u]=0x1eu;
    case_policy_send_probe(1u,packet,9u,1u);
    state[0x1bu]=1u;
    shared[4u]=0u;
    case_policy_parse_probe(1u);
    return 1u;
}
