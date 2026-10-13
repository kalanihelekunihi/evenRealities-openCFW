#include "case_logger_contract.h"
#include "../semantic_strings_candidate_20261011/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Native CASE 0x08009a9c no-reply sensor reset. The five GPIO configuration
 * words at stock 0xd36c alias the event descriptor tail at 0xd26c+0x100.
 */
#include <stdint.h>
#include <stddef.h>
#include "application_boot_transport_registration_data_candidate.h"
extern void case_policy_sensor_prepare(void); /* 0xd250 */
extern uint32_t case_policy_sensor_shutdown(uint32_t descriptor); /* 0x5f00 */
extern void case_bus_gpio_config(uint32_t base,volatile uint32_t *config); /* 0x4d30 */
extern void case_policy_ota_left_prepare(void); /* 0xbe90 */
extern void case_policy_ota_right_prepare(void); /* 0xbede */
extern void case_policy_reset_pulse(void); /* 0xb678 */
extern void case_policy_ota_left_finish(void); /* 0xbeba */
extern void case_policy_ota_right_finish(void); /* 0xbf08 */
extern int32_t case_policy_sensor_delay(uint32_t amount); /* 0xa7b0 */
extern void case_policy_idle_clear(void); /* 0x9a14 */

void case_policy_no_reply_reset(uint32_t left,uint32_t right)
{
    _Static_assert(offsetof(Registry,event)+offsetof(EventSpec,field4)==0x100u,
                   "native reset configuration alias");
    if((left|right)==0u)return;
    volatile uint8_t *shared=(volatile uint8_t *)(uintptr_t)0x200000b8u;
    if(shared[4u]!=0u){
        if(shared[7u]==0u){
            (void)case_policy_log(CASE_STRING_ADDR(08009b38));
            (void)case_policy_log(CASE_STRING_ADDR(08009b60));
        }
        return;
    }
    shared[4u]=1u;
    case_policy_sensor_prepare();
    const uint32_t descriptor=0x20000eb8u;
    volatile const uint32_t *sensor=(volatile const uint32_t *)(uintptr_t)(descriptor+0x80u);
    if(((sensor[2u]|sensor[3u])&0x20u)!=0u)(void)case_policy_sensor_shutdown(descriptor);

    uint32_t config[5];
    volatile const uint32_t *config_source=&case_boot_transport_registration_storage.event.field4;
    for(uint32_t i=0u;i<5u;++i)config[i]=config_source[i];
    case_bus_gpio_config(0x50000400u,config);
    if(left!=0u){
        case_policy_ota_left_prepare();
        case_policy_reset_pulse();
        case_policy_ota_left_finish();
        (void)case_policy_sensor_delay(10u);
    }
    if(right!=0u){
        case_policy_ota_right_prepare();
        case_policy_reset_pulse();
        case_policy_ota_right_finish();
        (void)case_policy_sensor_delay(10u);
    }
    config[1u]=0u;
    case_bus_gpio_config(0x50000400u,config);
    case_policy_idle_clear();
    shared[4u]=0u;
}
