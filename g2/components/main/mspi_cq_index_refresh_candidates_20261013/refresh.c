/* SPDX-License-Identifier: MIT
 * Main command queue index refresh at 0x538d18, using the observed ops row.
 */
#include <stdint.h>

extern uint32_t g2_main_critical_save_473940(void);

void g2_main_cq_update_indices_538d18(uint32_t *queue)
{
    const uint32_t saved_mask = g2_main_critical_save_473940();
    const uintptr_t ops = queue[9];
    const uintptr_t index_register =
        *(const volatile uint32_t *)(ops + 8u);
    const uint32_t index_low =
        *(const volatile uint32_t *)index_register & 0xffu;
    uint32_t current = index_low | (queue[8] & UINT32_C(0xffffff00));
    queue[7] = current;
    if ((int32_t)(queue[8] - current) < 0) {
        current -= UINT32_C(0x100);
        queue[7] = current;
    }
    const uintptr_t head_register =
        *(const volatile uint32_t *)(ops + 4u);
    queue[3] = *(const volatile uint32_t *)head_register;
    __asm__ volatile("msr primask, %0" :: "r"(saved_mask) : "memory");
}

uint32_t g2_main_critical_save_473940(void)
{
    uint32_t previous;
    __asm__ volatile("mrs %0, primask\n\tcpsid i" : "=r"(previous) :: "memory");
    return previous;
}
