#include "case_logger_contract.h"
#include "../semantic_strings_candidate_20261011/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Native CASE 0x080082ec recurring transport side monitor.
 */
#include <stdint.h>
extern int32_t case_policy_sensor_delay(uint32_t amount); /* 0xa7b0 */
extern void case_boot_transport_action(uint32_t side,uint32_t mode); /* 0x1c1c */

void case_boot_transport_cb_82ec(void)
{
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0x2000087cu;
    volatile uint8_t *shared=(volatile uint8_t *)(uintptr_t)0x200000b8u;
    uint32_t first=1u;
    for(;;){
        if(state[16u]==0u || state[17u]==0u){
            first=1u;shared[1u]=0u;
            (void)case_policy_sensor_delay(100u);
            continue;
        }
        if((int8_t)shared[1u]<=0){
            first=1u;
            (void)case_policy_sensor_delay(100u);
            continue;
        }
        if(first!=0u){(void)case_policy_sensor_delay(200u);first=0u;}
        if(shared[4u]!=0u){
            int8_t next=(int8_t)(shared[1u]-1u);shared[1u]=(uint8_t)next;
            if(next>0)goto pause;
            if(shared[7u]==0u){
                (void)case_policy_log(CASE_STRING_ADDR(080083bc));
                (void)case_policy_log(CASE_STRING_ADDR(080083ec));
            }
        }else{
            shared[4u]=1u;
            uint32_t mode=state[0x4cu]!=0u?0u:1u;
            case_boot_transport_action(state[0x30u]!=0u?0u:1u,mode);
            shared[4u]=0u;
        }
pause:
        if(state[0x30u]!=0u && state[0x4cu]!=0u){
            shared[1u]=0u;
        }else{
            int8_t next=(int8_t)(shared[1u]-1u);shared[1u]=(uint8_t)next;
            if(next<=0 && shared[7u]==0u){
                (void)case_policy_log(CASE_STRING_ADDR(080083f0));
                (void)case_policy_log(CASE_STRING_ADDR(080083ec));
            }
        }
        (void)case_policy_sensor_delay(20u);
    }
}
