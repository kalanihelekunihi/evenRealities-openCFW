/* SPDX-License-Identifier: MIT
 * Image-B resource accounting and audio MMIO control leaves.
 */
#include <stdint.h>

extern int32_t gx8002_image_b_audio_update_mask_10005cbc(
    uint32_t mask, int32_t enable);

uint32_t gx8002_image_b_audio_budget_advance_1000a3fc(uint32_t amount)
{
    volatile uint32_t *const budget =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002d75c);
    uint32_t next = budget[0] + amount;
    if (budget[1] < next) return UINT32_MAX;
    budget[0] = next;
    return 0u;
}

void gx8002_image_b_audio_mask_clear_1000a714(void)
{
    (void)gx8002_image_b_audio_update_mask_10005cbc(0x20007u, 0);
    (void)gx8002_image_b_audio_update_mask_10005cbc(0u, 1);
}

void gx8002_image_b_audio_mask_set_1000a730(void)
{
    (void)gx8002_image_b_audio_update_mask_10005cbc(0x30007u, 1);
}

uint32_t gx8002_image_b_audio_resource_take_1000a85c(uint32_t *resource)
{
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002cb88);
    uint32_t occupied = state[1];
    for (uint32_t index = 0u; index < 32u; ++index) {
        uint32_t bit = UINT32_C(1) << index;
        if ((occupied & bit) == 0u) {
            *resource = index + 1u;
            state[1] |= bit;
            return *resource;
        }
    }
    return UINT32_MAX;
}

/* The native C-SKY shifts also define the out-of-range signed inputs here. */
uint32_t gx8002_image_b_audio_resource_mark_1000a898(int32_t resource)
{
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002cb88);
    uint32_t bit = 1u;
    uint32_t shift = (uint32_t)resource - 1u;
    __asm__ volatile ("lsl %0, %1" : "+r"(bit) : "r"(shift));
    if ((state[1] & bit) == 0u || resource >= 33) return UINT32_MAX;
    state[0] |= bit;
    return 0u;
}

uint32_t gx8002_image_b_audio_resource_unmark_1000a8c4(int32_t resource)
{
    if (resource >= 33) return UINT32_MAX;
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002cb88);
    uint32_t mask = UINT32_C(0xfffffffe);
    uint32_t shift = (uint32_t)resource - 1u;
    __asm__ volatile ("rotl %0, %1, %2" : "=r"(mask) : "r"(mask), "r"(shift));
    state[0] &= mask;
    return 0u;
}
