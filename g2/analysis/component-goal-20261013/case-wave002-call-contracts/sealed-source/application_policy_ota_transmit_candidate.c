#include "case_logger_contract.h"
#include "../semantic_strings_candidate_20261011/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Native CASE 0x08002744 OTA packet send and optional framed response.
 */
#include <stdint.h>
extern void case_boot_sensor_service_start(void); /* 0x6cf8 */
extern void case_control_write(uint32_t,uint32_t,uint32_t); /* 0x4e9e */
extern uint32_t case_boot_sensor_send_packet(const uint8_t *,uint32_t); /* 0x3bb0 */
extern void case_boot_sensor_post_transmit(void); /* 0x6c80 */
extern uint32_t case_boot_sensor_finish_guard(uint32_t,const uint8_t *,uint32_t,uint32_t); /* 0x63ec */
extern uint32_t case_policy_sensor_shutdown(uint32_t); /* 0x5f00 */
extern uint32_t case_policy_sensor_divide(uint32_t,uint32_t); /* 0x0160 */
extern void log_hex_buffer(const uint8_t *,uint32_t); /* 0x67c8 */
static uint32_t sensor_flags(uint32_t d){volatile const uint32_t *s=(volatile const uint32_t *)(uintptr_t)(d+0x88u);return s[0u]|s[1u];}
uint32_t case_policy_ota_transmit(uint32_t channel,const uint8_t *packet,uint32_t count,uint32_t option)
{
    (void)channel;
    const uint32_t descriptor=0x20000eb8u;
    volatile uint8_t *rx=(volatile uint8_t *)(uintptr_t)0x20000664u;
    volatile uint8_t *quiet=(volatile uint8_t *)(uintptr_t)0x200000bfu;
    if((sensor_flags(descriptor)&0x20u)==0u)case_boot_sensor_service_start();
    case_control_write(0x50000000u,8u,1u);
    (void)case_boot_sensor_send_packet(packet,count);
    case_boot_sensor_post_transmit();
    if(option!=0u){
        if(case_boot_sensor_finish_guard(descriptor,(const uint8_t *)(uintptr_t)rx,5u,100u)==3u)goto finish;
        uint32_t index=0u;
        while(index<5u && rx[index]!=0x5au)++index;
        if(index==5u){
            if(*quiet==0u)(void)case_policy_log(CASE_STRING_ADDR(08002838));
            log_hex_buffer((const uint8_t *)(uintptr_t)rx,5u);
            goto finish;
        }
        uint32_t retained=5u-index;
        if(index!=0u){
            for(uint32_t j=0u;j<retained;++j)rx[j]=rx[index+j];
            if(index>1u){
                if(case_boot_sensor_finish_guard(descriptor,(const uint8_t *)(uintptr_t)(rx+index+1u),index-1u,50u)==3u){
                    if(*quiet==0u){(void)case_policy_log(CASE_STRING_ADDR(08002860));(void)case_policy_log(CASE_STRING_ADDR(08002884));}
                    log_hex_buffer((const uint8_t *)(uintptr_t)rx,5u);
                    goto finish;
                }
                retained=4u;
            }
        }
        uint32_t data_length=rx[3u];
        uint32_t capped=data_length<275u?data_length:275u;
        uint32_t wait=(case_policy_sensor_divide(capped,30u)*5u+5u)&0xffffu;
        (void)case_boot_sensor_finish_guard(descriptor,(const uint8_t *)(uintptr_t)(rx+retained),capped,wait);
    }
finish:
    (void)case_policy_sensor_shutdown(descriptor);
    return 1u;
}
