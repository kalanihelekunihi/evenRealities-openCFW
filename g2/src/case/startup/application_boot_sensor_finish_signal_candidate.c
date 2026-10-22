/* SPDX-License-Identifier: MIT
 * CASE 0x0800a888 task/ISR notification dispatcher.
 */
#include <stdint.h>
extern int32_t case_boot_sensor_finish_signal_isr(uint32_t task,uint32_t bits,uint32_t *woken); /* 0xc568 */
extern int32_t case_boot_sensor_finish_signal_task(uint32_t task,uint32_t bits); /* 0xc4de */
/* Stock 0x0800A888 (osEventFlagsSet) */
int32_t case_boot_sensor_finish_signal(uint32_t task,uint32_t bits)
{
    if(task==0u||(bits>>24)!=0u)return -4;
    uint32_t ipsr;__asm volatile("mrs %0, ipsr":"=r"(ipsr));
    if(ipsr==0u)return case_boot_sensor_finish_signal_task(task,bits);
    uint32_t woken=0u;
    if(case_boot_sensor_finish_signal_isr(task,bits,&woken)==0)return -3;
    if(woken!=0u)
        *(volatile uint32_t *)(uintptr_t)0xe000ed04u=1u<<28;
    return (int32_t)bits;
}
