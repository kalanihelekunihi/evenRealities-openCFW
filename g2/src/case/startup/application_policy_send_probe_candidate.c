#include "case_logger_contract.h"
#include "../semantic-strings/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800258c sensor probe send and optional framed reply read.
 */
#include <stdint.h>
extern void case_policy_sensor_prepare(void); /* 0xd250 */
extern uint32_t case_policy_sensor_shutdown(uint32_t); /* 0x5f00 */
extern void case_boot_sensor_service_start(void); /* 0x6cf8 */
extern void case_control_write(uint32_t,uint32_t,uint32_t); /* 0x4e9e */
extern void case_policy_ota_left_prepare(void); /* 0xbe90 */
extern void case_policy_ota_right_prepare(void); /* 0xbede */
extern int32_t case_policy_sensor_delay(uint32_t); /* 0xa7b0 */
extern uint32_t case_boot_sensor_send_packet(const uint8_t *,uint32_t); /* 0x3bb0 */
extern void case_boot_sensor_post_transmit(void); /* 0x6c80 */
extern uint32_t case_boot_sensor_finish_guard(uint32_t,const uint8_t *,uint32_t,uint32_t); /* 0x63ec */
extern void log_hex_buffer(const uint8_t *,uint32_t); /* 0x67c8 */
extern uint32_t case_policy_sensor_divide(uint32_t,uint32_t); /* 0x0160 */
extern void case_policy_idle_clear(void); /* 0x9a14 */
extern uint32_t case_boot_sensor_flags_5f44(uint32_t descriptor);
static void logline(uint32_t address)
{(void)case_policy_log(address);(void)case_policy_log(CASE_STRING_ADDR(0800271c));}

uint32_t case_policy_send_probe(uint32_t side,const uint8_t *packet,uint32_t count,uint32_t reply)
{
    const uint32_t descriptor=0x20000eb8u;
    volatile uint8_t *rx=(volatile uint8_t *)(uintptr_t)0x20000664u;
    volatile uint8_t *quiet=(volatile uint8_t *)(uintptr_t)0x200000bfu;
    case_policy_sensor_prepare();
    if((case_boot_sensor_flags_5f44(descriptor)&0x20u)==0u)case_boot_sensor_service_start();
    case_control_write(0x50000000u,8u,1u);
    if(side!=0u)case_policy_ota_left_prepare();
    else case_policy_ota_right_prepare();
    (void)case_policy_sensor_delay(1u);
    (void)case_boot_sensor_send_packet(packet,count);
    case_boot_sensor_post_transmit();
    if(reply!=0u){
        if(case_boot_sensor_finish_guard(descriptor,(const uint8_t *)(uintptr_t)rx,5u,80u)==3u){
            if(*quiet==0u)logline(CASE_STRING_ADDR(080026c8));
            goto finish;
        }
        uint32_t index=0u;
        while(index<5u && rx[index]!=0x5au)++index;
        if(index==5u){
            if(*quiet==0u)(void)case_policy_log(CASE_STRING_ADDR(080026e0));
            log_hex_buffer((const uint8_t *)(uintptr_t)rx,5u);
            goto finish;
        }
        uint32_t retained=5u-index;
        if(index!=0u){
            for(uint32_t j=0u;j<retained;++j)rx[j]=rx[index+j];
            if(index>1u){
                if(case_boot_sensor_finish_guard(descriptor,
                    (const uint8_t *)(uintptr_t)(rx+index+1u),index-1u,50u)==3u){
                    if(*quiet==0u)logline(CASE_STRING_ADDR(08002700));
                    log_hex_buffer((const uint8_t *)(uintptr_t)rx,5u);
                    goto finish;
                }
                retained=4u;
            }
        }
        uint32_t data_length=rx[3u];
        uint32_t wait=(case_policy_sensor_divide(data_length,30u)*5u+5u)&0xffffu;
        if(case_boot_sensor_finish_guard(descriptor,
            (const uint8_t *)(uintptr_t)(rx+retained),data_length,wait)==3u){
            if(*quiet==0u){
                (void)case_policy_log_number(CASE_STRING_ADDR(08002720),data_length);
                (void)case_policy_log(CASE_STRING_ADDR(0800271c));
            }
        }
    }
finish:
    (void)case_policy_sensor_shutdown(descriptor);
    case_policy_idle_clear();
    return 1u;
}
