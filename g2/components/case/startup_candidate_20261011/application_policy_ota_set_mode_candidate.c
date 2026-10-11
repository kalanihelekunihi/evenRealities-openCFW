/* SPDX-License-Identifier: MIT
 * Native CASE 0x1d68 OTA mode packet and three-attempt response exchange.
 * The native twelve-byte template remains a product data contract.
 */
#include <stdint.h>
extern const uint8_t case_policy_ota_probe_template[12]; /* 0x1e4c */
extern void case_policy_sensor_delay(uint32_t amount); /* 0xa7b0 */
extern uint32_t case_legacy_logger(const char *format,...); /* 0x9170 */
extern uint32_t case_policy_ota_transmit(uint32_t channel,const uint8_t *packet,uint32_t count,uint32_t option); /* 0x2744 */
extern uint32_t case_policy_parse_probe(uint32_t channel); /* 0x1e94 */
void case_policy_ota_checksum(uint8_t *packet,uint32_t count) /* 0x9b70 */
{
    packet[count-1u]=(uint8_t)(count+125u);
    for(uint32_t i=0u;(int32_t)i<(int32_t)(count-1u);++i)
        packet[count-1u]=(uint8_t)(packet[count-1u]+packet[i]);
}
void case_policy_ota_set_mode(uint32_t mode)
{
    volatile uint8_t *busy=(volatile uint8_t *)(uintptr_t)0x200000bcu;
    while(*busy!=0u)case_policy_sensor_delay(100u);
    uint8_t silent=*(volatile uint8_t *)(uintptr_t)0x200000bfu;
    if(silent==0u){
        (void)case_legacy_logger((const char *)(uintptr_t)0x08001e20u,mode);
        (void)case_legacy_logger((const char *)(uintptr_t)0x08001e48u);
    }
    uint8_t packet[12];
    for(uint32_t i=0u;i<12u;++i)packet[i]=case_policy_ota_probe_template[i];
    packet[4]=mode!=0u?1u:0u;
    packet[5]=1u;
    if(mode!=0u){
        packet[6]=*(volatile uint8_t *)(uintptr_t)0x20000898u;
        packet[7]=*(volatile uint8_t *)(uintptr_t)0x20000899u;
    }else{packet[6]=2u;packet[7]=0x39u;}
    packet[8]=0u;
    case_policy_ota_checksum(packet,10u);
    uint32_t success=0u;
    for(uint32_t attempt=0u;attempt<3u;++attempt){
        if(*busy==0u){
            *busy=1u;
            (void)case_policy_ota_transmit(1u,packet,10u,1u);
            *busy=0u;
            if(case_policy_parse_probe(1u)==0x5bu){success=1u;break;}
        }
        case_policy_sensor_delay(200u);
    }
    if(silent==0u){
        (void)case_legacy_logger((const char *)(uintptr_t)(success?0x08001e78u:0x08001e5cu));
        (void)case_legacy_logger((const char *)(uintptr_t)0x08001e48u);
    }
}
