/* SPDX-License-Identifier: MIT
 * Instruction-derived leaves used by HAL control requests 30 and 34.
 * Queue register accesses are volatile and must be bound to real queue state.
 */
#include "control_request_helpers.h"
#include <stddef.h>

#define CMDQ_VALID_MAGIC UINT32_C(0x01cdcdcd)
#define CMDQ_VALID_MASK UINT32_C(0x01ffffff)
#define CMDQ_DEVICE_VISIBLE UINT32_C(0x20080000)

uint32_t opencfw_bl_control_stage_two_flags(uint32_t handle_address,
                                             uint32_t flags)
{
    volatile uint32_t *const handle =
        (volatile uint32_t *)(uintptr_t)handle_address;
    const uint32_t mode = handle[0x20e];

    if (mode == 1u) {
        flags |= 0x40a0u;
        handle[0x20e] = 2u;
    } else if (mode == 2u) {
        flags = 0x4000u;
    } else {
        flags |= 0x4080u;
    }
    return flags;
}

uint32_t opencfw_provider_427c12(uint32_t queue_address,
                                 uint32_t command_kind)
{
    volatile uint32_t *const queue =
        (volatile uint32_t *)(uintptr_t)queue_address;
    volatile uint32_t *write;
    volatile uint32_t *const ops = queue == NULL ? NULL :
        (volatile uint32_t *)(uintptr_t)queue[9];
    uint32_t command;

    if (queue == NULL || (queue[0] & CMDQ_VALID_MASK) != CMDQ_VALID_MAGIC)
        return 2u;
    if (queue[4] == queue[5])
        return 7u;

    write = (volatile uint32_t *)(uintptr_t)queue[5];
    write[0] = ops[2];
    write[1] = 0u;
    command = (uint8_t)command_kind != 0u ? 1u : 0u;
    command |= ops[1];
    write[2] = command;
    write[3] = queue[1];
    queue[5] += 16u;
    queue[4] = queue[5];

    if (queue[2] >= CMDQ_DEVICE_VISIBLE)
        __asm__ volatile("dmb sy" ::: "memory");
    *(volatile uint32_t *)(uintptr_t)ops[3] = (uint8_t)queue[8];
    return 0u;
}

uint32_t opencfw_provider_4279be(uint32_t queue_address)
{
    volatile uint32_t *const queue =
        (volatile uint32_t *)(uintptr_t)queue_address;

    if (queue == NULL || (queue[0] & CMDQ_VALID_MASK) != CMDQ_VALID_MAGIC)
        return 2u;
    if (queue[4] == queue[5])
        return 7u;
    queue[5] = queue[4];
    queue[8] -= 1u;
    return 0u;
}
