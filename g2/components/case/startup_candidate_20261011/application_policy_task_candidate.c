/* SPDX-License-Identifier: MIT
 * Experimental whole policy-task control composition from stock 0x08007200.
 * Scoped source bodies own known branches; sensor refresh is a typed lower
 * contract because its live R2/R3 side effects are not yet source-qualified.
 */
#include <stdint.h>
struct case_policy_idle_context {uint32_t state_address;uint32_t idle_counter;};
struct case_policy_task_context {
    struct case_policy_idle_context idle;
    uint8_t full_battery_counter; /* native R5 */
    uint8_t service_tick;         /* native SP+16 */
};
extern uint32_t case_policy_idle_step_7214(struct case_policy_idle_context *context);
extern uint8_t case_policy_full_battery_step_72bc(volatile uint8_t *,volatile uint8_t *,volatile uint8_t *,uint8_t);
extern void case_policy_fake_standby_counters_738a(volatile uint8_t *,volatile uint8_t *,volatile uint8_t *);
extern uint32_t case_policy_box_idle_7494(volatile uint8_t *,volatile uint8_t *,volatile uint8_t *);
extern uint32_t case_policy_ota_side_step_7376(volatile uint8_t *);
extern void case_policy_idle_clear(void);
extern uint32_t case_policy_service_gate_77b0(volatile uint8_t *,uint8_t *,uint8_t *);
extern uint8_t case_policy_stable_service_7850(volatile uint8_t *,uint8_t);
extern uint32_t case_policy_postservice_7884(volatile uint8_t *,volatile uint8_t *,volatile uint8_t *,uint8_t,uint8_t);
extern void case_policy_fake_standby_clear(void);
extern void case_policy_wait(uint32_t ticks);
/* 0x08003a3c/0x08003a60 effect and caller-register side output contracts. */
extern uint8_t case_policy_sensor_left_refresh(volatile uint8_t *left,uint8_t prior,uint8_t active);
extern uint8_t case_policy_sensor_right_refresh(volatile uint8_t *right,uint8_t prior,uint8_t active);

/* Return 1 at the native 0x7ed6 immediate reentry, else after the 1000-tick
 * wait immediately preceding that edge. Neither return is task termination.
 */
uint32_t case_policy_task_iteration_7214(struct case_policy_task_context *ctx)
{
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)ctx->idle.state_address;
    volatile uint8_t *left=state+0x20u;  /* native SP+4 */
    volatile uint8_t *right=state+0x40u; /* native SP+0 */
    volatile uint8_t *shared=(volatile uint8_t *)(uintptr_t)0x200000b8u;
    uint8_t old_left=0u,old_right=0u;
    uint32_t idle=case_policy_idle_step_7214(&ctx->idle);
    if(idle!=0u || (state[4u]==0u && state[3u]==0u)){
        ctx->full_battery_counter=case_policy_full_battery_step_72bc(state,left,right,ctx->full_battery_counter);
    }else if(shared[0x3du]==0u){
        case_policy_fake_standby_counters_738a(state,left,right);
        ctx->full_battery_counter=0u; /* stock 0x08007484 */
        if(state[3u]!=0u){state[0x17u]=0u;goto ota;}
        uint32_t box=case_policy_box_idle_7494(state,left,right);
        if(box==2u)goto wait;
        if(box==1u)goto service;
    }
ota:
    if(case_policy_ota_side_step_7376(state)!=0u)goto wait;
    if(state[0x1au]!=0u){
        state[0x10u]=0u;state[0x11u]=0u;state[0x1au]=0u;
        case_policy_idle_clear();
    }
    if(shared[0x3du]!=0u){state[0x10u]=1u;state[0x11u]=1u;goto wait;}
service:
    if(case_policy_service_gate_77b0(state,&old_left,&old_right)==0u)goto wait;
    if(state[0x10u]==0u && state[0x1bu]!=0u)state[0x1bu]=0u;
    if(state[0x10u]!=old_left || state[0x11u]!=old_right){
        if(shared[3u]!=0u)case_policy_fake_standby_clear();
        if(state[0x10u]==0u){
            left[0x12u]=case_policy_sensor_left_refresh(left,left[0x12u],0u);
            state[0x12u]=0u;
        }else (void)case_policy_sensor_left_refresh(left,left[0x12u],1u);
        if(state[0x11u]==0u){
            right[0x0eu]=case_policy_sensor_right_refresh(right,right[0x0eu],0u);
            state[0x13u]=0u;
        }else (void)case_policy_sensor_right_refresh(right,right[0x0eu],1u);
    }
    if(shared[4u]==0u || (state[0x10u]==old_left && state[0x11u]==old_right))
        ctx->service_tick=case_policy_stable_service_7850(state,ctx->service_tick);
    return case_policy_postservice_7884(state,left,right,old_left,old_right);
wait:
    case_policy_wait(1000u);
    return 0u;
}

void case_policy_task_7200(void)
{
    struct case_policy_task_context ctx={{0x2000087cu,0u},0u,0u};
    for(;;)(void)case_policy_task_iteration_7214(&ctx);
}
