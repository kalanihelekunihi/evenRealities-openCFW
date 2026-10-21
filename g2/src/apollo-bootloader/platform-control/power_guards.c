/* SPDX-License-Identifier: MIT
 * Reconstructed 0x41BD92/0x41BDE4. Poll bound is 10,000 iterations, not time.
 */
#include <stdint.h>
extern uint32_t opencfw_boot_power_control(uint32_t,uint32_t,uint32_t *);
#define ENABLED (*(volatile uint8_t *)(uintptr_t)0x200271a7u)
#define STATUS  (*(volatile uint32_t *)(uintptr_t)0x40021018u)
#define REQUEST (*(volatile uint32_t *)(uintptr_t)0x40021014u)

uint32_t opencfw_boot_control_guard_begin(void)
{
    if(ENABLED==1u) {
        uint32_t config=STATUS|0x80u;
        (void)opencfw_boot_power_control(5,1,&config);
        REQUEST|=0x20u;
        uint32_t iterations=0;
        while(iterations<10000u && !(STATUS&0x80u))++iterations;
        if(iterations==10000u)return 4;
    }
    return 0;
}

uint32_t opencfw_boot_control_guard_end(void)
{
    if(ENABLED==1u) {
        REQUEST&=~0x20u;
        uint32_t iterations=0;
        while(iterations<10000u && (STATUS&0x80u))++iterations;
        if(iterations==10000u)return 4;
        uint32_t config=STATUS;
        (void)opencfw_boot_power_control(5,0,&config);
    }
    return 0;
}
