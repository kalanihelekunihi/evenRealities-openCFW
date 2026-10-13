#include "case_logger_contract.h"
#include "../semantic_strings_candidate_20261011/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Stock 0x08007494 through 0x08007548 box idle qualification. This internal
 * path uses 0x08007200's left/right stack pointers and state R4.
 */
#include <stdint.h>
extern void case_policy_idle_clear(void);       /* 0x08009a14 */

/* 0: 0x7376; 1: 0x75e2; 2: 0x77ae; 3: 0x754a log continuation. */
uint32_t case_policy_box_idle_7494(volatile uint8_t *state,
                                   volatile uint8_t *right,
                                   volatile uint8_t *left)
{
    volatile uint8_t *shared=(volatile uint8_t *)(uintptr_t)0x200000b8u;
    if(state[4u]==0u)goto clear;
    if(state[0x10u]==0u){
        if(state[0x11u]!=0u || shared[1u]!=0u || shared[0u]!=0u)goto clear;
        if(state[0x17u]>30u)return 0u;
        uint8_t next=(uint8_t)(state[0x17u]+1u);
        state[0x17u]=next;
        if(next==30u && shared[7u]==0u){
            case_policy_log(CASE_STRING_ADDR(080076ec));
            case_policy_log(CASE_STRING_ADDR(08007608));
        }
        return 0u;
    }
    if(state[0x11u]==0u || shared[1u]!=0u || shared[0u]!=0u)goto clear;
    if(right[0x11u]==0u || left[0x0du]==0u ||
       right[0x13u]!=0u || left[0x0fu]!=0u || state[0x19u]!=0u){
        goto clear;
    }
    if(state[0x17u]<=30u){
        uint8_t next=(uint8_t)(state[0x17u]+1u);
        state[0x17u]=next;
        if(next==30u && shared[7u]==0u){
            case_policy_log(CASE_STRING_ADDR(0800770c));
            case_policy_log(CASE_STRING_ADDR(08007608));
            return 0u;
        }
    }
    if(state[0x1au]!=0u){
        state[0x10u]=0u;state[0x11u]=0u;state[0x1au]=0u;
        case_policy_idle_clear();
    }
    if(shared[0x3du]!=0u){
        state[0x10u]=1u;state[0x11u]=1u;
        return 2u;
    }
    return 1u;
clear:
    state[0x17u]=0u;
    return 0u;
}
