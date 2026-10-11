/* SPDX-License-Identifier: MIT
 * Stock static queue constructor, with the selected queue-reset provider lower.
 */
#include <stdint.h>

extern uint32_t opencfw_bl_mask_interrupts(void);
extern uint32_t opencfw_boot_kernel_queue_reset(uint32_t *queue, uint32_t is_new);

static _Noreturn void queue_assert(void)
{
    (void)opencfw_bl_mask_interrupts();
    *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
    for (;;) __asm volatile("b ." ::: "memory");
}

uint32_t opencfw_bl_kernel_queue_create_static(uint32_t count,
                                               uint32_t item_size,
                                               uint32_t storage,
                                               uint32_t control_block,
                                               uint32_t type)
{
    if (!control_block) queue_assert();
    if (!count || ((storage == 0u) != (item_size == 0u))) queue_assert();

    uint32_t *queue = (uint32_t *)(uintptr_t)control_block;
    volatile uint8_t *bytes = (volatile uint8_t *)queue;
    bytes[0x46] = 1u;
    queue[0] = item_size ? storage : control_block;
    queue[15] = count;
    queue[16] = item_size;
    (void)opencfw_boot_kernel_queue_reset(queue, 1u);
    bytes[0x4c] = (uint8_t)type;
    return control_block;
}
