/* SPDX-License-Identifier: MIT
 * Native CASE 0x6bb0 bus and 0x6c00 sensor descriptor initialization.
 * Device descriptors are RAM objects populated from immediate native values.
 */
#include <stdint.h>
extern uint32_t case_boot_bus_open(uint32_t descriptor); /* 0x5a74 */
extern uint32_t case_boot_bus_set_frequency(uint32_t descriptor,uint32_t frequency,uint32_t width); /* 0x598c */
extern uint32_t case_boot_bus_start(uint32_t descriptor); /* 0x5910 */
extern void case_boot_init_failure(void); /* 0x3e90 */
extern uint32_t case_boot_sensor_open(uint32_t descriptor); /* 0x6240 */
extern uint32_t case_boot_sensor_set_mode(uint32_t descriptor,uint32_t mode); /* 0x5eb6 */
extern uint32_t case_boot_sensor_set_clock(uint32_t descriptor,uint32_t clock); /* 0x5e6e */
extern uint32_t case_boot_sensor_start(uint32_t descriptor); /* 0x5e2e */
extern uint32_t case_boot_sensor_bind(uint32_t descriptor,uint32_t channel,uint32_t enabled); /* 0x64ec */
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
void case_boot_bus_initialize(void)
{
    const uint32_t d=0x20000948u;
    wr(d,0x40002800u);wr(d+12u,127u);wr(d+8u,0u);wr(d+20u,0u);
    wr(d+24u,0u);wr(d+16u,31u);wr(d+28u,0u);wr(d+32u,0x40000000u);wr(d+36u,0u);
    if(case_boot_bus_open(d)!=0u)case_boot_init_failure();
    if(case_boot_bus_set_frequency(d,0xf0u,4u)!=0u)case_boot_init_failure();
    (void)case_boot_bus_start(d);
}
void case_boot_sensor_initialize(void)
{
    const uint32_t d=0x20000e24u;
    wr(d,0x40013800u);wr(d+4u,0x000f4240u);
    wr(d+8u,0u);wr(d+12u,0u);wr(d+16u,0u);wr(d+24u,0u);
    wr(d+28u,0u);wr(d+32u,0u);wr(d+20u,12u);wr(d+36u,0u);
    wr(d+40u,16u);wr(d+60u,0x1000u);
    if(case_boot_sensor_open(d)!=0u)case_boot_init_failure();
    if(case_boot_sensor_set_mode(d,0u)!=0u)case_boot_init_failure();
    if(case_boot_sensor_set_clock(d,0u)!=0u)case_boot_init_failure();
    if(case_boot_sensor_start(d)!=0u)case_boot_init_failure();
    (void)case_boot_sensor_bind(d,0x20000108u,1u);
}
