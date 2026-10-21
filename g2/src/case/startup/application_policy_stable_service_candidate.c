/* SPDX-License-Identifier: MIT
 * Stock unchanged-service path 0x08007850 through 0x08007884. The tick byte
 * belongs to the live 0x08007200 stack context (SP+16).
 */
#include <stdint.h>
extern void case_policy_service_maintenance(void); /* 0x080018e4 */
uint8_t case_policy_stable_service_7850(volatile uint8_t *state,uint8_t tick)
{
    volatile uint8_t *shared=(volatile uint8_t *)(uintptr_t)0x200000b8u;
    shared[4u]=1u;
    volatile uint32_t *left_ticks=(volatile uint32_t *)(void *)(state+0x3cu);
    volatile uint32_t *right_ticks=(volatile uint32_t *)(void *)(state+0x58u);
    if(((*left_ticks<10u || *right_ticks<10u) && shared[0x3du]==0u) ||
       ((tick=(uint8_t)(tick+1u))>=10u)){
        case_policy_service_maintenance();tick=0u;
    }
    shared[4u]=0u;
    return tick;
}
