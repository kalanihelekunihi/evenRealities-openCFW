/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800bb90 transport inbox/charging confirmation callback.
 */
#include <stdint.h>
extern uint32_t case_policy_log(uint32_t);
extern uint32_t case_policy_log_four(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern void case_boot_irq_hall_prepare(uint32_t); /* 0x3848 */
extern int32_t case_policy_event_signal(uint32_t,uint32_t); /* 0xaaf0 */
extern int32_t case_policy_task_reset(uint32_t); /* 0xab26 */
extern int32_t case_boot_sensor_finish_signal(uint32_t,uint32_t); /* 0xa888 */

static uint32_t rd32(volatile uint8_t *p)
{return *(volatile uint32_t *)(void *)p;}
static void logline(uint32_t message)
{(void)case_policy_log(message);(void)case_policy_log(0x0800bd40u);}

void case_boot_transport_cb_bb90(void)
{
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0x2000087cu;
    volatile uint8_t *shared=(volatile uint8_t *)(uintptr_t)0x200000b8u;
    uint8_t quiet=shared[7u];
    if(state[16u]==0u || state[17u]==0u){
        if(state[16u]!=0u || state[17u]!=0u){
            if(quiet==0u)logline(state[16u]!=0u?0x0800be4cu:0x0800be24u);
            goto error_state;
        }
        if(quiet==0u)logline(0x0800bdf8u);
        state[20u]=0u;
        if(state[2u]>=4u)return;
        if(state[2u]==3u)(void)case_policy_task_reset(rd32(shared+24u));
        case_boot_irq_hall_prepare(1u);
        state[2u]=2u;
        (void)case_policy_event_signal(rd32(shared+16u),0xbb8u);
        return;
    }
    uint8_t left_status=state[52u],left_confirm=state[48u];
    uint8_t right_status=state[80u],right_confirm=state[76u];
    uint32_t left_need=(left_status==0u || left_confirm!=0u)?1u:0u;
    uint32_t right_need=(right_status==0u || right_confirm!=0u)?1u:0u;
    if((left_need&right_need)==0u){
        if(quiet==0u)logline(left_need!=0u?0x0800bdccu:0x0800bda0u);
        goto error_state;
    }
    if((left_status==0u && rd32(state+68u)>=210u) ||
       (right_status==0u && rd32(state+96u)>=210u)){
        if(left_status==0u){
            if(quiet==0u)logline(0x0800bd10u);
            state[49u]=1u;state[51u]=1u;
        }else{
            if(quiet==0u)logline(0x0800bd44u);
            state[77u]=1u;state[79u]=1u;
        }
        goto error_state;
    }
    if(state[0u]==3u){
        state[0u]=0u;
        if(quiet==0u)logline(0x0800bd74u);
        state[20u]=2u;
        return;
    }
    if(quiet==0u){
        (void)case_policy_log_four(0x0800d770u,left_status,left_confirm,right_status,right_confirm);
        (void)case_policy_log(0x0800bd40u);
    }
    shared[1u]=0u;state[20u]=2u;
    if(state[2u]>=4u)return;
    state[2u]=2u;
    case_boot_irq_hall_prepare(1u);
    (void)case_policy_event_signal(rd32(shared+16u),0xbb8u);
    return;
error_state:
    state[20u]=1u;
    if(state[2u]>=4u)return;
    state[2u]=3u;
    (void)case_boot_sensor_finish_signal(rd32(shared+56u),4u);
}
