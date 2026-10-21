/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800b678 reset pin pulse and busy-wait waveform.
 */
#include <stdint.h>
extern void case_control_write(uint32_t base,uint32_t mask,uint32_t enable); /* 0x4e9e */
extern int32_t case_policy_sensor_delay(uint32_t amount); /* 0xa7b0 */

static void spin(uint32_t count) /* stock 0xa7a2 */
{
    for(volatile uint32_t i=0u;i<count;++i)__asm__ volatile("nop");
}
static void pin(uint32_t value)
{
    case_control_write(0x50000400u,0x200u,value);
}
static void clock_pulses(uint32_t count,uint32_t pause)
{
    for(uint32_t i=0u;i<count;++i){pin(0u);spin(pause);pin(1u);spin(pause);}
}
void case_policy_reset_pulse(void)
{
    case_control_write(0x50000000u,8u,1u);
    (void)case_policy_sensor_delay(10u);
    pin(1u);
    (void)case_policy_sensor_delay(10u);
    pin(0u);
    spin(620u);
    pin(1u);
    spin(0x1428u);
    clock_pulses(5u,0x50000400u>>19u);
    pin(1u);
    spin(0x1428u);
    pin(0u);
    (void)case_policy_sensor_delay(40u);
    pin(1u);
    (void)case_policy_sensor_delay(1u);
    pin(0u);
    spin(620u);
    pin(1u);
    spin(0x1428u);
    clock_pulses(7u,0x50000400u>>19u);
    pin(1u);
    spin(0x1428u);
    (void)case_policy_sensor_delay(1u);
    pin(0u);
    spin(620u);
    pin(1u);
    spin(0x1428u);
    clock_pulses(7u,0x50000400u>>19u);
    pin(1u);
    spin(0x1428u);
}
