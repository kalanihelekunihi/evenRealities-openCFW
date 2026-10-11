/* SPDX-License-Identifier: MIT
 * Native CASE 0x08009bc0 and 0x08009cc8 aging status refresh paths.
 */
#include <stdint.h>
extern uint32_t case_boot_transport_aging_status(void); /* 0x1408 */
extern uint32_t case_policy_log(uint32_t);
extern uint32_t case_policy_log_number(uint32_t,uint32_t);
extern uint32_t case_legacy_logger(const char *,...);
extern int32_t case_boot_sensor_finish_signal(uint32_t,uint32_t);

static volatile uint8_t *const shared=(volatile uint8_t *)(uintptr_t)0x200000b8u;
static volatile uint8_t *const device=(volatile uint8_t *)(uintptr_t)0x200000f4u;
static volatile uint8_t *const state=(volatile uint8_t *)(uintptr_t)0x2000087cu;

void case_boot_transport_sample_refresh(void)
{
    if(case_boot_transport_aging_status()!=0u){
        shared[0u]=0u;
        if(shared[7u]==0u){
            (void)case_legacy_logger((const char *)(uintptr_t)0x08009c48u,device[2u],device[3u]);
            (void)case_policy_log(0x08009c70u);
        }
        if(device[2u]==0u || device[3u]==0u)shared[0u]=10u;
    }else{
        shared[0u]=(uint8_t)(shared[0u]+1u);
        if(shared[7u]==0u){(void)case_policy_log_number(0x08009c74u,shared[0u]);(void)case_policy_log(0x08009c70u);}
    }
    if(shared[0u]>9u){
        device[6u]=2u;state[2u]=4u;
        (void)case_boot_sensor_finish_signal(*(volatile uint32_t *)(void *)(shared+56u),4u);
        if(shared[7u]==0u){(void)case_policy_log(0x08009ca0u);(void)case_policy_log(0x08009c70u);}
    }
}

void case_boot_transport_sample_refresh_mode4(void)
{
    if(state[16u]!=0u && state[17u]!=0u){shared[0u]=0u;return;}
    shared[0u]=(uint8_t)(shared[0u]+1u);
    if(shared[7u]==0u){(void)case_policy_log_number(0x08009d30u,shared[0u]);(void)case_policy_log(0x08009d4cu);}
    if(shared[0u]>9u){
        device[6u]=2u;state[2u]=4u;
        (void)case_boot_sensor_finish_signal(*(volatile uint32_t *)(void *)(shared+56u),4u);
        if(shared[7u]==0u){(void)case_policy_log(0x08009d50u);(void)case_policy_log(0x08009d4cu);}
    }
}
