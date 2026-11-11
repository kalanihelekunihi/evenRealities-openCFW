/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800a01e elapsed conversion and 0xa074 timer query.
 */
#include <stdint.h>
extern uint32_t case_policy_timer_device_read(uint32_t reg,uint8_t *out,uint32_t count); /* 0x28b4 */
/* Dedup (0x080035b8): case_policy_timer_bus_read is an alias of case_binary_guarded_sensor_read (legacy-default/binary_guarded_sensor_candidate.c). */
extern int32_t case_policy_timer_bus_read(uint32_t reg,uint8_t *out,uint32_t count);
/* Stock 0x0800A148 (case_nested_delay): 13000 x "nop; adds; cmp; blt"
 * = 65000 cycles (1.02 ms at 64 MHz) per count. Here each inner pass is
 * "nop; nop; subs; bgt", also 5 cycles; the NOPs take the counter as an
 * operand so the compiler cannot shorten the loop (it emitted a 4-cycle
 * "subs; bne" loop, 20% short, before). */
__attribute__((noinline)) void case_policy_timer_delay(uint32_t count)
{
    for(int32_t outer=0;outer<(int32_t)count;++outer)
        for(int32_t inner=0x32c8;inner>0;--inner)
            __asm__ volatile("nop\n\tnop":"+r"(inner));
}
__attribute__((noinline)) int32_t case_policy_timer_query(uint32_t reg,uint32_t *out)
{
    uint8_t bytes[4]={0u,0u,0u,0u};
    if(case_policy_timer_bus_read(reg,bytes,2u)!=0)return -1;
    uint32_t first=((uint32_t)bytes[0]<<8)|bytes[1];
    case_policy_timer_delay(5u);
    if(case_policy_timer_bus_read(reg,bytes,2u)!=0)return -1;
    uint32_t second=((uint32_t)bytes[0]<<8)|bytes[1];
    if(first!=second){
        case_policy_timer_delay(5u);
        if(case_policy_timer_bus_read(reg,bytes,2u)!=0)return -1;
        first=((uint32_t)bytes[0]<<8)|bytes[1];
    }
    *out=first;
    return 0;
}
int32_t case_policy_elapsed(uint32_t *out)
{
    uint32_t ticks=0u;
    if(case_policy_timer_query(2u,&ticks)!=0)return -1;
    *out=(ticks+(ticks<<2))>>4;
    return 0;
}
/* Dedup (0x0800a01e): case_binary_14_read_c (was legacy-default/binary_value_readers_candidate.c). */
uint32_t case_binary_14_read_c(uint32_t *out) __attribute__((alias("case_policy_elapsed")));
/* Dedup (0x0800a01e): case_boot_battery_sample (was startup/application_boot_power_samples_candidate.c). */
__typeof__(case_policy_elapsed) case_boot_battery_sample __attribute__((alias("case_policy_elapsed")));
/* Dedup (0x0800a074): case_binary_read_word_lower (was legacy-default/binary_sensor_word_lower_candidate.c). */
uint32_t case_binary_read_word_lower(uint32_t selector, uint32_t *out) __attribute__((alias("case_policy_timer_query")));
/* Dedup (0x0800a148): case_binary_sensor_delay_count (was legacy-default/sensor_delay_candidate.c). */
uint32_t case_binary_sensor_delay_count(uint32_t count) __attribute__((alias("case_policy_timer_delay")));
