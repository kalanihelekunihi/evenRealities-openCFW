/* SPDX-License-Identifier: MIT
 * Native CASE 0x08006c80/0x08006cf8 sensor reconfiguration after/before
 * probe transfer. The two entrypoints differ only in descriptor field +20.
 */
#include <stdint.h>
extern uint32_t case_policy_sensor_shutdown(uint32_t); /* 0x5f00 */
extern uint32_t case_boot_sensor_open(uint32_t); /* 0x6240 */
extern uint32_t case_boot_sensor_set_mode(uint32_t,uint32_t); /* 0x5eb6 */
extern uint32_t case_boot_sensor_set_clock(uint32_t,uint32_t); /* 0x5e6e */
extern uint32_t case_boot_sensor_start(uint32_t); /* 0x5e2e */
extern __attribute__((noreturn)) void case_boot_init_failure(void); /* 0x3e90 */

static void reconfigure(uint32_t mode)
{
    volatile uint32_t *d=(volatile uint32_t *)(uintptr_t)0x20000eb8u;
    (void)case_policy_sensor_shutdown((uint32_t)(uintptr_t)d);
    d[0u]=0x40004800u;
    d[1u]=1000000u;
    d[2u]=0u;d[3u]=0u;d[4u]=0u;
    d[6u]=0u;d[7u]=0u;d[8u]=0u;
    d[5u]=mode;
    d[9u]=0u;d[10u]=16u;d[15u]=4096u;
    if(case_boot_sensor_open((uint32_t)(uintptr_t)d)!=0u)case_boot_init_failure();
    if(case_boot_sensor_set_mode((uint32_t)(uintptr_t)d,0u)!=0u)case_boot_init_failure();
    if(case_boot_sensor_set_clock((uint32_t)(uintptr_t)d,0u)!=0u)case_boot_init_failure();
    if(case_boot_sensor_start((uint32_t)(uintptr_t)d)!=0u)case_boot_init_failure();
}
void case_boot_sensor_post_transmit(void){reconfigure(4u);}
void case_boot_sensor_service_start(void){reconfigure(8u);}
