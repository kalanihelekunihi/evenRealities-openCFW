/* SPDX-License-Identifier: MIT
 * Source reconstruction of the locked Apollo510 CMDQ block helpers.
 * Queue/MMIO state transitions are instruction-derived; actual peripheral
 * progress is intentionally outside these allocation/post/reset routines.
 */
#include "queue_descriptors.h"
#include <stddef.h>

#define CMDQ_MAGIC UINT32_C(0x01cdcdcd)
#define CMDQ_ID_MASK UINT32_C(0xfe000000)
#define CMDQ_VALID_MASK UINT32_C(0x01ffffff)
#define CMDQ_ENABLED UINT32_C(0x02000000)
#define CMDQ_ACTIVE UINT32_C(0x01000000)
#define CMDQ_DEVICE_VISIBLE UINT32_C(0x20080000)

extern uint32_t opencfw_bl_critical_save(void);

static uint32_t valid(const volatile uint32_t *q)
{
    return q != NULL && (q[0] & CMDQ_VALID_MASK) == CMDQ_MAGIC;
}

static void refresh_indices(volatile uint32_t *q)
{
    const uint32_t mask = opencfw_bl_critical_save();
    const uintptr_t ops = q[9];
    const uintptr_t index_reg = *(const volatile uint32_t *)(ops + 8u);
    const uint32_t low = *(const volatile uint32_t *)index_reg & 0xffu;
    uint32_t current = low | (q[8] & UINT32_C(0xffffff00));

    q[7] = current;
    if ((int32_t)(q[8] - current) < 0)
        q[7] = current - 0x100u;
    q[3] = *(const volatile uint32_t *)(uintptr_t)
        *(const volatile uint32_t *)(ops + 4u);
    __asm__ volatile("msr primask, %0" :: "r"(mask) : "memory");
}

uint32_t opencfw_provider_42790a(uint32_t *queue_address,
                                uint32_t block_count,
                                uint32_t *block_address_out,
                                uint32_t *sequence_out)
{
    volatile uint32_t *const q = (volatile uint32_t *)queue_address;
    uint32_t *const block_out = block_address_out;
    uint32_t *const sequence = sequence_out;
    uint32_t available;
    uint32_t block;

    if (!valid(q))
        return 2u;
    if (block_out == NULL || sequence == NULL)
        return 6u;
    if (q[4] != q[5])
        return 7u;

    refresh_indices(q);
    available = q[7] + UINT32_C(0xfe) - q[8];
    if ((int32_t)available < 0)
        return 5u;

    if (q[4] < q[3]) {
        const uint32_t reserve_end = q[4] + (block_count + 1u) * 8u;
        if (reserve_end >= q[3])
            return 5u;
        block = q[4];
    } else {
        const uint32_t reserve_end = q[4] + (block_count + 2u) * 8u;
        if (q[2] >= reserve_end) {
            block = q[4];
        } else {
            const uint32_t wrapped_end = q[1] + (block_count + 1u) * 8u;
            if (wrapped_end >= q[3])
                return 5u;
            *(volatile uint32_t *)(uintptr_t)q[4] =
                *(const volatile uint32_t *)(uintptr_t)(q[9] + 4u);
            *(volatile uint32_t *)(uintptr_t)(q[4] + 4u) = q[1];
            block = q[1];
        }
    }

    *block_out = block;
    q[8] += 1u;
    *sequence = q[8];
    q[5] = block + block_count * 8u;
    return 0u;
}

uint32_t opencfw_provider_4279f0(uint32_t *queue_address,
                                uint32_t command_kind)
{
    volatile uint32_t *const q = (volatile uint32_t *)queue_address;
    volatile uint32_t *write;
    uint32_t command_word;

    if (!valid(q))
        return 2u;
    if (q[4] == q[5])
        return 7u;

    write = (volatile uint32_t *)(uintptr_t)q[5];
    command_word = (uint8_t)command_kind != 0u ? 1u : 0u;
    command_word |= *(const volatile uint32_t *)(uintptr_t)(q[9] + 8u);
    write[0] = command_word;
    write[1] = q[8];
    q[5] += 8u;
    q[4] = q[5];

    if (q[2] >= CMDQ_DEVICE_VISIBLE)
        __asm__ volatile("dmb sy" ::: "memory");
    *(volatile uint32_t *)(uintptr_t)
        *(const volatile uint32_t *)(uintptr_t)(q[9] + 12u) =
        (uint8_t)q[8];
    return 0u;
}

uint32_t opencfw_provider_427baa(uint32_t *queue_address)
{
    volatile uint32_t *const q = (volatile uint32_t *)queue_address;
    volatile uint32_t *ops;
    uint32_t value;

    if (!valid(q))
        return 2u;
    if ((q[0] & CMDQ_ENABLED) != 0u)
        return 7u;

    ops = (volatile uint32_t *)(uintptr_t)q[9];
    value = *(volatile uint32_t *)(uintptr_t)ops[0] & ~1u;
    *(volatile uint32_t *)(uintptr_t)ops[0] = value;
    q[3] = q[1];
    q[5] = q[1];
    q[4] = q[1];
    q[7] = 0u;
    q[8] = 0u;
    *(volatile uint32_t *)(uintptr_t)ops[2] = 0u;
    *(volatile uint32_t *)(uintptr_t)ops[3] = 0u;
    *(volatile uint32_t *)(uintptr_t)ops[1] = q[1];
    q[0] &= ~CMDQ_ENABLED;
    return 0u;
}
