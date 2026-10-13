#include "../semantic_strings_candidate_20261011/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Stock 0x08007376 side-OTA-ready transitions through loop tail 0x08007eda.
 * Box OTA file success and failure transitions are also represented with
 * typed file, mode, delay and flash children.
 */
#include <stdint.h>
extern void case_policy_log(uint32_t message);
extern void case_policy_ota_left_prepare(void);  /* 0x0800be90 */
extern void case_policy_ota_right_prepare(void); /* 0x0800bede */
extern void case_ack(uint32_t opcode);           /* 0x080068d0 */
extern uint32_t case_policy_box_file_open(void); /* 0x08001574 */
extern void case_policy_ota_set_mode(uint32_t mode); /* 0x08001d68 */
extern void case_policy_box_failure_reset(void); /* 0x080012e4 */
extern void case_policy_wait(uint32_t ticks); /* 0x0800a7b0 */
extern void case_policy_box_begin(void); /* 0x080038e0 */
uint32_t case_policy_ota_side_step_7376(volatile uint8_t *state)
{
    uint32_t side=state[0x19u];
    if(side==0u)return 0u;
    state[0x10u]=1u;state[0x11u]=1u;
    if(state[0x1au]==0u){
        if(*(volatile uint8_t *)(uintptr_t)0x200000bfu==0u){
            case_policy_log(side==1u?CASE_STRING_ADDR(08007730):(side==2u?CASE_STRING_ADDR(08007740):CASE_STRING_ADDR(08007750)));
            case_policy_log(CASE_STRING_ADDR(08007608));
        }
        if(side==1u)case_policy_ota_left_prepare();
        else if(side==2u)case_policy_ota_right_prepare();
        else case_policy_ota_left_prepare();
        state[0x1au]=1u;
        if(side>2u){
            if(case_policy_box_file_open()==0u){
                if(*(volatile uint8_t *)(uintptr_t)0x200000bfu==0u){
                    case_policy_log(CASE_STRING_ADDR(08007b50));case_policy_log(CASE_STRING_ADDR(08007b84));
                }
                case_policy_ota_set_mode(0u);
                state[0x1cu]=0u;state[0x1du]=0u;
                for(uint32_t i=0x20u;i<0x2cu;i++)state[i]=0u;
                state[0x2cu]=0u;state[0x19u]=0u;state[0x18u]=0u;
                case_policy_box_failure_reset();
            }else{
                if(*(volatile uint8_t *)(uintptr_t)0x200000bfu==0u){
                    case_policy_log(CASE_STRING_ADDR(08007760));case_policy_log(CASE_STRING_ADDR(08007608));
                }
                case_policy_ota_set_mode(1u);case_policy_wait(100u);case_policy_box_begin();
            }
        }else case_ack(0x56u);
    }
    return 1u;
}
