#include "case_logger_contract.h"
#include "../semantic_strings_candidate_20261011/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Native CASE 0x08009684 transport state callback. The two sample refresh
 * children remain separate source obligations at 0x9bc0 and 0x9cc8.
 */
#include <stdint.h>
extern void case_boot_transport_sample_refresh(void); /* 0x9bc0 */
extern void case_boot_transport_sample_refresh_mode4(void); /* 0x9cc8 */
extern uint32_t case_policy_service_idle(void); /* 0xd154 */
extern uint32_t case_legacy_logger(const char *,...);
extern int32_t case_boot_sensor_finish_signal(uint32_t,uint32_t); /* 0xa888 */
extern void case_boot_transport_stop_clock(uint32_t); /* 0x6b80 */
extern void case_boot_transport_stop_link(uint32_t); /* 0x6b98 */

void case_boot_transport_cb_9684(void)
{
    volatile uint8_t *device=(volatile uint8_t *)(uintptr_t)0x200000f4u;
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0x2000087cu;
    volatile uint8_t *shared=(volatile uint8_t *)(uintptr_t)0x200000b8u;
    volatile uint8_t *sample=state+0x20u;
    volatile uint8_t *other=state+0x40u;
    if(device[6u]!=1u)return;
    *(volatile uint32_t *)(void *)(device+12u)+=5u;
    if(device[7u]==1u){
        case_boot_transport_sample_refresh();
        uint32_t threshold=0xe42u;
        if(*(volatile uint16_t *)(void *)(state+54u)>threshold &&
           sample[18u]>40u && *(volatile uint16_t *)(void *)(other+18u)>threshold &&
           other[14u]>40u && shared[10u]==0u){
            shared[2u]=0u;
        }else if(shared[2u]<2u){
            shared[2u]++;
            if(shared[7u]==0u){(void)case_policy_log_number(CASE_STRING_ADDR(080098b8),shared[2u]);(void)case_policy_log(CASE_STRING_ADDR(0800992c));}
        }else{
            shared[2u]=0u;device[7u]=2u;state[21u]=1u;
            (void)case_policy_service_idle();state[16u]=0u;state[17u]=0u;
            if(shared[7u]==0u){(void)case_policy_log(CASE_STRING_ADDR(080098f8));(void)case_policy_log(CASE_STRING_ADDR(0800992c));}
        }
        if(shared[7u]==0u)(void)case_policy_log_number(CASE_STRING_ADDR(08009930),*(volatile uint32_t *)(void *)(device+12u));
    }else if(device[7u]==2u){
        case_boot_transport_sample_refresh();
        if((sample[17u]!=0u && other[13u]!=0u) || shared[9u]!=0u){
            device[7u]=1u;shared[2u]=0u;state[21u]=0u;
            (void)case_policy_service_idle();state[16u]=0u;state[17u]=0u;
            if(shared[7u]==0u){(void)case_policy_log(CASE_STRING_ADDR(08009958));(void)case_policy_log(CASE_STRING_ADDR(0800992c));}
        }
        if(shared[7u]==0u){(void)case_policy_log_number(CASE_STRING_ADDR(0800998c),*(volatile uint32_t *)(void *)(device+12u));(void)case_policy_log(CASE_STRING_ADDR(0800992c));}
    }else if(device[7u]==4u){
        case_boot_transport_sample_refresh_mode4();
        if(state[16u]!=0u && state[17u]!=0u){
            if(device[4u]==0u){
                state[21u]=0u;(void)case_policy_service_idle();
                state[16u]=0u;state[17u]=0u;device[4u]=1u;device[5u]=0u;
                if(shared[7u]==0u){(void)case_policy_log(CASE_STRING_ADDR(0800983c));(void)case_policy_log(CASE_STRING_ADDR(0800992c));}
            }
        }else if(shared[7u]==0u){
            (void)case_legacy_logger((const char *)(uintptr_t)CASE_STRING_ADDR(0800987c),state[16u],state[17u]);
            (void)case_policy_log(CASE_STRING_ADDR(0800992c));
        }
    }else return;
    uint32_t elapsed=*(volatile uint32_t *)(void *)(device+12u);
    uint32_t prior=*(volatile uint32_t *)(void *)(device+8u);
    if((uint32_t)(elapsed+prior)>=0x3840u || shared[11u]!=0u){
        if(shared[7u]==0u){(void)case_policy_log(CASE_STRING_ADDR(080099b8));(void)case_policy_log(CASE_STRING_ADDR(0800992c));}
        device[6u]=3u;state[2u]=4u;
        case_boot_transport_stop_clock(0u);case_boot_transport_stop_link(1u);
    }else if(prior>=0x1c20u && elapsed>=60u){
        device[6u]=2u;state[2u]=4u;
        (void)case_boot_sensor_finish_signal(*(volatile uint32_t *)(void *)(shared+56u),4u);
        if(shared[7u]==0u){(void)case_policy_log(CASE_STRING_ADDR(0800d72c));(void)case_policy_log(CASE_STRING_ADDR(0800992c));}
    }
}
