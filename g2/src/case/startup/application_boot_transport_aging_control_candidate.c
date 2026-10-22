#include "case_logger_contract.h"
#include "../semantic-strings/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Native CASE 0x080023f4/0x080024c0 left/right aging controls.
 * The native immediate six-byte request has command 0x3e, side and enable.
 */
#include <stdint.h>
extern void case_policy_ota_checksum(uint8_t *,uint32_t); /* 0x9b70 */
extern uint32_t case_policy_send_probe(uint32_t,const uint8_t *,uint32_t,uint32_t); /* 0x258c */
extern uint32_t case_policy_parse_probe(uint32_t); /* 0x1e94 */

static void control(uint32_t side,uint32_t enabled)
{
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0x2000087cu;
    volatile uint8_t *quiet=(volatile uint8_t *)(uintptr_t)0x200000bfu;
    volatile uint8_t *busy=(volatile uint8_t *)(uintptr_t)0x200000bcu;
    volatile uint8_t *device=(volatile uint8_t *)(uintptr_t)0x200000f4u;
    uint32_t offset=side==1u?16u:17u;
    if(state[offset]==0u){
        if(*quiet==0u){
            (void)case_policy_log(side==1u?CASE_STRING_ADDR(08002494):CASE_STRING_ADDR(08002560));
            (void)case_policy_log(side==1u?CASE_STRING_ADDR(08002490):CASE_STRING_ADDR(0800255c));
        }
        return;
    }
    if(*busy!=0u){
        if(*quiet==0u){
            (void)case_policy_log(side==1u?CASE_STRING_ADDR(08002468):CASE_STRING_ADDR(08002534));
            (void)case_policy_log(side==1u?CASE_STRING_ADDR(08002490):CASE_STRING_ADDR(0800255c));
        }
        return;
    }
    *busy=1u;
    uint8_t packet[8]={0x3eu,0u,(uint8_t)(side==1u?0u:1u),1u,0u,0u,0u,0u};
    packet[4u]=(uint8_t)enabled;
    case_policy_ota_checksum(packet,6u);
    case_policy_send_probe(side,packet,6u,1u);
    if(case_policy_parse_probe(side)==62u)device[side==1u?2u:3u]=(uint8_t)enabled;
    *busy=0u;
}
/* Stock 0x080023F4 (aging_status_set_left) */
void case_boot_transport_left_aging(uint32_t enabled){control(1u,enabled);}
/* Stock 0x080024C0 (aging_status_set_right) */
void case_boot_transport_right_aging(uint32_t enabled){control(0u,enabled);}
