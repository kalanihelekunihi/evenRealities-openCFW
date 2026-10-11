/* SPDX-License-Identifier: MIT
 * Native CASE 0x08001408 aging status exchange. Native immediate packet
 * fields at 0x1564/0x156c are expressed as typed protocol bytes.
 */
#include <stdint.h>
extern void case_policy_ota_checksum(uint8_t *packet,uint32_t count); /* 0x9b70 */
extern uint32_t case_policy_send_probe(uint32_t side,const uint8_t *packet,uint32_t count,uint32_t reply); /* 0x258c */
extern uint32_t case_policy_parse_probe(uint32_t side); /* 0x1e94 */
extern uint32_t case_policy_log(uint32_t message); /* 0x9170 */

uint32_t case_boot_transport_aging_status(void)
{
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0x2000087cu;
    volatile uint8_t *busy=(volatile uint8_t *)(uintptr_t)0x200000bcu;
    volatile uint8_t *quiet=(volatile uint8_t *)(uintptr_t)0x200000bfu;
    if(state[16u]==0u || state[17u]==0u){
        if(*quiet==0u){(void)case_policy_log(0x08001518u);(void)case_policy_log(0x08001538u);}
        return 0u;
    }
    if(*busy!=0u){
        if(*quiet==0u){(void)case_policy_log(0x0800153cu);(void)case_policy_log(0x08001538u);}
        return 1u;
    }
    *busy=1u;
    uint8_t probe[8]={0x46u,0u,0u,0u,0u,0u,0u,0u};
    case_policy_ota_checksum(probe,5u);
    case_policy_send_probe(1u,probe,5u,1u);
    uint32_t success=case_policy_parse_probe(1u)==70u;
    uint8_t status[8]={0x13u,0u,0u,1u,0u,0u,0u,0u};
    status[4u]=(uint8_t)((state[3u]<<7u)|state[1u]);
    status[5u]=state[4u]!=0u?1u:2u;
    status[2u]=0u;
    case_policy_ota_checksum(status,7u);
    case_policy_send_probe(1u,status,7u,1u);
    (void)case_policy_parse_probe(1u);
    status[2u]=1u;
    case_policy_ota_checksum(status,7u);
    case_policy_send_probe(0u,status,7u,1u);
    (void)case_policy_parse_probe(0u);
    probe[2u]=1u;
    case_policy_ota_checksum(probe,5u);
    case_policy_send_probe(0u,probe,5u,1u);
    if(case_policy_parse_probe(0u)!=70u)success=0u;
    *busy=0u;
    return success;
}
