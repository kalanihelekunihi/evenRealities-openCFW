/* SPDX-License-Identifier: MIT
 * Stock 0x08009a14 lens charge/idle command selection.
 */
#include <stdint.h>
extern uint32_t case_policy_bus_write(uint32_t bus,uint32_t channel,uint32_t count,const uint8_t *value); /* 0x08000610 */
extern void case_policy_log_four(uint32_t message,uint32_t a,uint32_t b,uint32_t c,uint32_t d); /* 0x08009170 */
extern void case_policy_log(uint32_t message);
/* Stock 0x08009108: nine IRQ-guarded bus attempts, cumulative failure count. */
uint32_t case_policy_sensor_write(uint32_t channel,uint32_t count,const uint8_t *value)
{
    volatile uint32_t *bus_state=(volatile uint32_t *)(uintptr_t)0x2000007cu;
    for(uint32_t attempt=1u;attempt<10u;attempt++){
        __asm__ volatile("cpsid i" ::: "memory");
        uint32_t result=case_policy_bus_write(0x42u,channel,count,value);
        __asm__ volatile("cpsie i" ::: "memory");
        if(result!=0u)return result;
        bus_state[1u]=bus_state[1u]+1u;
    }
    if(*(volatile uint8_t *)(uintptr_t)0x200000bfu==0u){
        case_policy_log_four(0x0800d538u,10u,bus_state[2u],bus_state[3u],bus_state[4u]);
        case_policy_log(0x0800916cu);
    }
    return 0u;
}
/* Stock 0x080099e8 cache check and conditional bus write. */
void case_policy_sensor_command(uint32_t channel,uint32_t value)
{
    volatile uint8_t *cache=(volatile uint8_t *)(uintptr_t)0x20000090u;
    uint8_t byte=(uint8_t)value;
    if(cache[channel]==byte)return;
    if(case_policy_sensor_write(channel,1u,&byte)!=0u)cache[channel]=byte;
}
void case_policy_idle_clear(void)
{
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0x2000087cu;
    volatile uint8_t *left=state+0x20u,*right=state+0x40u;
    uint8_t inhibit=*(volatile uint8_t *)(uintptr_t)0x20000105u;
    case_policy_sensor_command(5u,3u);
    case_policy_sensor_command(6u,0x81u);
    case_policy_sensor_command(7u,0x20u);
    uint32_t left_cmd=(state[0x10u]!=0u && state[0x15u]!=0u && left[0x11u]==0u &&
                       (inhibit==0u || state[0x11u]!=0u))?0xafu:0xaeu;
    case_policy_sensor_command(3u,left_cmd);
    uint32_t right_cmd=(state[0x11u]!=0u && state[0x15u]!=0u && right[0x0du]==0u &&
                        (inhibit==0u || state[0x10u]!=0u))?0xafu:0xaeu;
    case_policy_sensor_command(4u,right_cmd);
}
