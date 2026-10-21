/* SPDX-License-Identifier: MIT
 * Main 0x538fb4/0x5391d6/0x538f82: commit or roll back a CQ reservation.
 */
#include <stdint.h>

static volatile uint32_t *queue_state(uint32_t queue)
{
    return (volatile uint32_t *)(uintptr_t)queue;
}

static uint32_t valid_queue(uint32_t queue)
{
    if (queue == 0u) return 0u;
    return (queue_state(queue)[0] & UINT32_C(0x01ffffff)) ==
           UINT32_C(0x01cdcdcd);
}

static void publish(volatile uint32_t *state)
{
    if (state[2] >= UINT32_C(0x20080000))
        __asm__ volatile("dmb sy" ::: "memory");
    const uint32_t ops = state[9];
    const uint32_t write_index_register =
        *(const volatile uint32_t *)(uintptr_t)(ops + 0xcu);
    *(volatile uint32_t *)(uintptr_t)write_index_register =
        (uint8_t)state[8];
}

uint32_t g2_main_cq_commit_538fb4(uint32_t queue, uint32_t marker)
{
    if (!valid_queue(queue)) return 2u;
    volatile uint32_t *const state = queue_state(queue);
    if (state[4] == state[5]) return 7u;
    volatile uint32_t *const slot =
        (volatile uint32_t *)(uintptr_t)state[5];
    const uint32_t ops = state[9];
    slot[0] = ((uint8_t)marker != 0u) |
              *(const volatile uint32_t *)(uintptr_t)(ops + 8u);
    slot[1] = state[8];
    state[5] = (uint32_t)(uintptr_t)(slot + 2);
    state[4] = state[5];
    publish(state);
    return 0u;
}

uint32_t g2_main_cq_commit_marker_5391d6(uint32_t queue, uint32_t marker)
{
    if (!valid_queue(queue)) return 2u;
    volatile uint32_t *const state = queue_state(queue);
    if (state[4] == state[5]) return 7u;
    volatile uint32_t *const slot =
        (volatile uint32_t *)(uintptr_t)state[5];
    const uint32_t ops = state[9];
    slot[0] = *(const volatile uint32_t *)(uintptr_t)(ops + 8u);
    slot[1] = 0u;
    slot[2] = ((uint8_t)marker != 0u) |
              *(const volatile uint32_t *)(uintptr_t)(ops + 4u);
    slot[3] = state[1];
    state[5] = (uint32_t)(uintptr_t)(slot + 4);
    state[4] = state[5];
    publish(state);
    return 0u;
}

uint32_t g2_main_cq_rollback_538f82(uint32_t queue)
{
    if (!valid_queue(queue)) return 2u;
    volatile uint32_t *const state = queue_state(queue);
    if (state[4] == state[5]) return 7u;
    state[5] = state[4];
    state[8] -= 1u;
    return 0u;
}
