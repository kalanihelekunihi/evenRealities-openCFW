/* SPDX-License-Identifier: MIT
 * Stock 0x08007884-0x080079b4 lens-status and charging-result decision.
 * Prior left/right status are the 0x08007200 stack snapshots at SP+12/+20.
 */
#include <stdint.h>
extern void case_policy_log(uint32_t message);
extern void case_policy_led_left_clear(uint32_t value);  /* 0x08006b80 */
extern void case_policy_led_right_clear(uint32_t value); /* 0x08006b98 */
/* Return 1 for 0x79b0 refresh, 0 for 0x79b4 no-reply continuation. */
uint32_t case_policy_status_7884(volatile uint8_t *state,
                                 volatile uint8_t *left,
                                 volatile uint8_t *right,
                                 uint8_t old_left,uint8_t old_right)
{
    volatile uint8_t *shared=(volatile uint8_t *)(uintptr_t)0x200000b8u;
    uint8_t l=state[0x10u],r=state[0x11u];
    if(l!=old_left || r!=old_right){
        *(volatile uint32_t *)(void *)(state+0x0cu)=0u;
        if(state[2u]<3u){
            case_policy_led_left_clear(0u);case_policy_led_right_clear(0u);state[2u]=2u;
            if(shared[7u]==0u){case_policy_log(0x08007b8cu);case_policy_log(0x08007b84u);}
        }
        if(r==0u){
            uint32_t message=(l==0u)?0x08007c2cu:0x08007c74u;
            if(shared[7u]==0u){case_policy_log(message);case_policy_log(0x08007b84u);}
        }else if(l==0u){
            if(shared[7u]==0u){case_policy_log(0x08007c50u);case_policy_log(0x08007b84u);}
        }else if(left[0x10u]==0u || right[0x0cu]==0u){
            if(shared[7u]==0u){case_policy_log(0x08007bf0u);case_policy_log(0x08007b84u);}
            shared[1u]=8u;
        }else if(shared[7u]==0u){
            case_policy_log(0x08007bb0u);case_policy_log(0x08007b84u);
        }
        return 1u;
    }
    if(*(volatile uint32_t *)(void *)(state+0x0cu)<=10u)return 0u;
    if(state[0x14u]==1u){
        if(left[0x10u]!=0u && right[0x0cu]!=0u && left[0x13u]==0u && right[0x0fu]==0u){
            if(shared[7u]==0u){case_policy_log(0x08007c98u);case_policy_log(0x08007b84u);}
            return 1u;
        }
    }else if(state[0x14u]==2u){
        uint8_t left_bad=(left[0x14u]==0u || left[0x10u]!=0u);
        uint8_t right_bad=(right[0x10u]==0u || right[0x0cu]!=0u);
        if(!(left_bad && right_bad)){
            if(shared[7u]==0u){case_policy_log(0x08007cc0u);case_policy_log(0x08007b84u);}
            return 1u;
        }
    }
    return 0u;
}
