/* SPDX-License-Identifier: MIT
 * Native 0x08003a3c and 0x08003a60 state clearers used by the policy loop.
 * Their caller reads R3/R2 before the call and those registers survive;
 * returning prior models the later stock byte store without inventing data.
 */
#include <stdint.h>
/* Stock 0x08003A3C (left_glasses_state_reset) */
uint8_t case_policy_sensor_left_refresh(volatile uint8_t *left,uint8_t prior,uint8_t active)
{
    (void)active;
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0x2000087cu;
    left[0x10u]=0u;left[0x11u]=0u;
    *(volatile uint16_t *)(void *)(state+0x38u)=0u;
    left[0x12u]=0u;left[0x13u]=0u;
    *(volatile uint16_t *)(void *)(state+0x36u)=0u;
    left[0x14u]=0u;
    *(volatile uint32_t *)(void *)(state+0x40u)=0u;
    *(volatile uint32_t *)(void *)(state+0x3cu)=0u;
    *(volatile uint32_t *)(void *)(state+0x44u)=0u;
    *(volatile uint32_t *)(void *)(state+0x48u)=0u;
    return prior;
}
/* Stock 0x08003A60 (right_glasses_state_reset) */
uint8_t case_policy_sensor_right_refresh(volatile uint8_t *right,uint8_t prior,uint8_t active)
{
    (void)active;
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0x2000087cu;
    right[0x0cu]=0u;right[0x0du]=0u;
    *(volatile uint16_t *)(void *)(right+0x14u)=0u;
    right[0x0eu]=0u;right[0x0fu]=0u;
    *(volatile uint16_t *)(void *)(right+0x12u)=0u;
    right[0x10u]=0u;
    *(volatile uint32_t *)(void *)(state+0x5cu)=0u;
    *(volatile uint32_t *)(void *)(state+0x58u)=0u;
    *(volatile uint32_t *)(void *)(state+0x60u)=0u;
    *(volatile uint32_t *)(void *)(state+0x64u)=0u;
    return prior;
}
