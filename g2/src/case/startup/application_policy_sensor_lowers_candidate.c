/* SPDX-License-Identifier: MIT
 * Native CASE 0x0160, 0x2edc, 0xa7b0 and 0xaa00 source reductions.
 */
#include <stdint.h>
extern void case_policy_adc_open(uint32_t adc); /* 0x47d4 */
extern void case_policy_adc_settle(uint32_t adc,uint32_t count); /* 0x4710 */
extern uint32_t case_policy_adc_read(uint32_t adc); /* 0x4328 */
extern void case_policy_adc_close(uint32_t adc); /* 0x483c */
extern void case_policy_task_sleep(uint32_t ticks); /* 0xc128 */
extern void case_policy_task_cancel_core(uint32_t task); /* 0xc228 */

/* Stock 0x08000160 (__aeabi_uidiv) */
uint32_t case_policy_sensor_divide(uint32_t value,uint32_t divisor)
{
    uint32_t quotient=0u;
    for(uint32_t bit=32u;;--bit){
        uint32_t shifted=bit==32u?0u:value>>bit;
        if(shifted>=divisor){
            uint32_t sub=bit==32u?0u:divisor<<bit;
            value-=sub;
            quotient+=bit==32u?0u:1u<<bit;
        }
        if(bit==0u)break;
    }
    return quotient;
}
/* Stock 0x08002EDC (case_trimmed_average8) */
uint32_t case_policy_sensor_sample(void)
{
    uint32_t adc=0x200008e4u;
    case_policy_adc_open(adc);
    case_policy_adc_settle(adc,10u);
    uint32_t total=0u,high=0u,low=0xffffffffu;
    for(uint32_t i=0u;i<8u;++i){
        uint32_t value=case_policy_adc_read(adc);
        if(value>high)high=value;
        if(value<low)low=value;
        total+=value;
    }
    case_policy_adc_close(adc);
    return (uint16_t)case_policy_sensor_divide(total-high-low,6u);
}
/* Stock 0x0800A7B0 (osDelay) */
int32_t case_policy_sensor_delay(uint32_t amount)
{
    uint32_t ipsr;
    __asm__ volatile("mrs %0, ipsr":"=r"(ipsr));
    if(ipsr!=0u)return -6;
    if(amount!=0u)case_policy_task_sleep(amount);
    return 0;
}
/* Both call sites name native entry 0x0800a7b0. The delay ABI returns status
 * in R0; the policy callers discard it. */
int32_t case_policy_wait(uint32_t amount)
{
    return case_policy_sensor_delay(amount);
}
/* Stock 0x0800AA00 (case_start_scheduler) */
int32_t case_policy_task_cancel(uint32_t task)
{
    uint32_t ipsr;
    __asm__ volatile("mrs %0, ipsr":"=r"(ipsr));
    if(ipsr!=0u)return -6;
    if(task==0u)return -4;
    case_policy_task_cancel_core(task);
    return 0;
}
