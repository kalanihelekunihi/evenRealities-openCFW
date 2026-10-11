/* SPDX-License-Identifier: MIT
 * Stock 0x0800738a-0x08007482 dual fake-standby counters. The left and right
 * structures are the two live stack pointers initialized at 0x08007200.
 */
#include <stdint.h>
extern void case_policy_log(uint32_t message);
extern void case_policy_fake_standby_set(uint32_t side); /* 0x08003a00 */
extern void case_policy_fake_standby_clear(void);       /* 0x080013b8 */
static uint16_t read16(volatile uint8_t *p)
{return *(volatile uint16_t *)(void *)p;}
static void write16(volatile uint8_t *p,uint16_t v)
{*(volatile uint16_t *)(void *)p=v;}

void case_policy_fake_standby_counters_738a(volatile uint8_t *state,
                                             volatile uint8_t *left,
                                             volatile uint8_t *right)
{
    volatile uint8_t *shared=(volatile uint8_t *)(uintptr_t)0x200000b8u;
    uint8_t right_ready=right[0x0du]!=0u;
    uint8_t left_ready=left[0x11u]!=0u;
    uint8_t left_primary=(state[0x10u]!=0u && left_ready);
    if(!left_primary && (state[0x11u]==0u || !right_ready)){
        write16(state+0x38u,0u);write16(right+0x14u,0u);return;
    }
    if(left_primary || (state[0x10u]==0u && left_ready)){
        if(left_primary && state[0x11u]!=0u && right_ready){
            uint16_t a=read16(state+0x38u),b=read16(right+0x14u);
            if(a<b)write16(right+0x14u,a);else write16(state+0x38u,b);
        }
        uint16_t old=read16(state+0x38u);
        write16(state+0x38u,(uint16_t)(old+1u));
        if(old>300u){
            if(left[0x13u]!=0u){
                if(shared[7u]==0u){case_policy_log(0x0800763cu);case_policy_log(0x08007608u);}
                write16(state+0x38u,0u);
            }else{
                if(shared[7u]==0u){case_policy_log(0x08007664u);case_policy_log(0x08007608u);}
                case_policy_fake_standby_set(1u);
                if(shared[3u]!=0u)case_policy_fake_standby_clear();
            }
        }
    }
    if(right_ready){
        uint16_t old=read16(right+0x14u);
        write16(right+0x14u,(uint16_t)(old+1u));
        if(old>300u){
            if(right[0x0fu]!=0u){
                if(shared[7u]==0u){case_policy_log(0x08007694u);case_policy_log(0x08007608u);}
                write16(right+0x14u,0u);
            }else{
                if(shared[7u]==0u){case_policy_log(0x080076bcu);case_policy_log(0x08007608u);}
                case_policy_fake_standby_set(0u);
            }
        }
    }
}
