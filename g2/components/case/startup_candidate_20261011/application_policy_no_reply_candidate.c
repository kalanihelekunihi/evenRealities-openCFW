/* SPDX-License-Identifier: MIT
 * Stock 0x080079b0-0x08007abc no-reply policy. Counts and modulo boundaries
 * are state at R4+0x40/+0x44 and +0x5c/+0x60, not independent timers.
 */
#include <stdint.h>
extern void case_policy_log(uint32_t message);
extern void case_policy_log_number(uint32_t message,uint32_t value); /* 0x08009170 */
extern void case_policy_refresh(void); /* 0x0800bb74 */
extern void case_policy_no_reply_reset(uint32_t left,uint32_t right); /* 0x08009a9c */
static uint32_t read32(volatile uint8_t *p)
{return *(volatile uint32_t *)(void *)p;}
static void write32(volatile uint8_t *p,uint32_t value)
{*(volatile uint32_t *)(void *)p=value;}

void case_policy_no_reply_after_79b4(volatile uint8_t *state)
{
    volatile uint8_t *shared=(volatile uint8_t *)(uintptr_t)0x200000b8u;
    if(read32(state+0x40u)>7u){
        uint32_t seconds=read32(state+0x44u);
        if(seconds%15u==0u && shared[7u]==0u){
            case_policy_log_number(0x08007ce8u,15u);case_policy_log(0x08007b84u);
        }
        write32(state+0x44u,seconds+1u);
    }
    if(read32(state+0x5cu)>7u){
        uint32_t seconds=read32(state+0x60u);
        if(seconds%15u==0u && shared[7u]==0u){
            case_policy_log_number(0x08007d0cu,15u);case_policy_log(0x08007b84u);
        }
        write32(state+0x60u,seconds+1u);
    }
    if(read32(state+0x40u)>7u){
        uint32_t seconds=read32(state+0x44u);
        if(seconds%180u==0u){
            if(shared[8u]==0u){
                case_policy_no_reply_reset(1u,0u);
                if(shared[7u]==0u){case_policy_log_number(0x08007d5cu,seconds);case_policy_log(0x08007b84u);}
            }else if(shared[7u]==0u){case_policy_log_number(0x08007d30u,seconds);case_policy_log(0x08007b84u);}
        }
    }
    if(read32(state+0x5cu)>7u){
        uint32_t seconds=read32(state+0x60u);
        if(seconds%180u==0u){
            if(shared[8u]==0u){
                case_policy_no_reply_reset(0u,1u);
                if(shared[7u]==0u){case_policy_log_number(0x08007db4u,seconds);case_policy_log(0x08007b84u);}
            }else if(shared[7u]==0u){
                /* The retained code passes left seconds in this right-side log. */
                case_policy_log_number(0x08007d88u,read32(state+0x44u));case_policy_log(0x08007b84u);
            }
        }
    }
    if((read32(state+0x40u)>7u && read32(state+0x44u)==210u) ||
       (read32(state+0x5cu)>7u && read32(state+0x60u)==210u))case_policy_refresh();
}

void case_policy_no_reply_79b0(volatile uint8_t *state)
{
    case_policy_refresh();
    case_policy_no_reply_after_79b4(state);
}
