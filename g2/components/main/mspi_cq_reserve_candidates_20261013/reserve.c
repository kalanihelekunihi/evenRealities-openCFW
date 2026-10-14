/* SPDX-License-Identifier: MIT
 * Main 0x538ece: reserve command-queue descriptor words.
 */
#include <stdint.h>

extern void g2_main_cq_update_indices_538d18(uint32_t *);

uint64_t g2_main_cq_reserve_538ece(uint32_t queue,
                                    uint32_t words,
                                    uint32_t output_address,
                                    uint32_t output_index)
{
    uint32_t result;
    if (queue == 0u ||
        (*(const volatile uint32_t *)(uintptr_t)queue &
         UINT32_C(0x01ffffff)) != UINT32_C(0x01cdcdcd)) {
        result = 2u;
    } else if (output_address == 0u || output_index == 0u) {
        result = 6u;
    } else {
        volatile uint32_t *const state =
            (volatile uint32_t *)(uintptr_t)queue;
        if (state[4] != state[5]) {
            result = 7u;
        } else {
            g2_main_cq_update_indices_538d18((uint32_t *)(uintptr_t)queue);
            if ((int32_t)((state[7] + 0xfeu) - state[8]) < 0) {
                result = 5u;
            } else {
                uint32_t slot;
                if (state[4] < state[3]) {
                    if (state[3] <= state[4] + (words + 1u) * 8u)
                        goto no_capacity;
                    slot = state[4];
                } else if (state[2] < state[4] + (words + 2u) * 8u) {
                    if (state[3] <= state[1] + (words + 1u) * 8u)
                        goto no_capacity;
                    volatile uint32_t *const wrap =
                        (volatile uint32_t *)(uintptr_t)state[4];
                    wrap[0] = *(const volatile uint32_t *)(uintptr_t)
                        (state[9] + 4u);
                    wrap[1] = state[1];
                    slot = state[1];
                } else {
                    slot = state[4];
                }
                *(volatile uint32_t *)(uintptr_t)output_address = slot;
                state[8] += 1u;
                *(volatile uint32_t *)(uintptr_t)output_index = state[8];
                state[5] = slot + words * 8u;
                result = 0u;
                goto done;
no_capacity:
                result = 5u;
            }
        }
    }
done:
    return ((uint64_t)output_index << 32) | result;
}
