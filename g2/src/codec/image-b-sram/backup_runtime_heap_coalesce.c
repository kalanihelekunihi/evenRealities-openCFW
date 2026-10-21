/* SPDX-License-Identifier: Apache-2.0
 * Image-B 0x100099d4 RT-Thread plug_holes, matched to pinned rt_mem.c.
 */
#include <stdint.h>
#include <stddef.h>

typedef struct {
    volatile uint16_t magic;
    volatile uint16_t used;
    volatile uint32_t next;
    volatile uint32_t previous;
} gx8002_image_b_heap_block;

_Static_assert(sizeof(gx8002_image_b_heap_block) == 12u,
               "native heap block size");

gx8002_image_b_heap_block *gx8002_image_b_heap_plug_at_100099d4(
    uint8_t *heap_base, gx8002_image_b_heap_block *heap_end,
    gx8002_image_b_heap_block *lowest_free,
    gx8002_image_b_heap_block *block)
{
    gx8002_image_b_heap_block *next =
        (gx8002_image_b_heap_block *)(heap_base + block->next);
    if (block != next && next->used == 0u && next != heap_end) {
        if (lowest_free == next) lowest_free = block;
        block->next = next->next;
        gx8002_image_b_heap_block *after =
            (gx8002_image_b_heap_block *)(heap_base + next->next);
        after->previous = (uint32_t)((uint8_t *)block - heap_base);
    }

    gx8002_image_b_heap_block *previous =
        (gx8002_image_b_heap_block *)(heap_base + block->previous);
    if (previous != block && previous->used == 0u) {
        if (lowest_free == block) lowest_free = previous;
        previous->next = block->next;
        gx8002_image_b_heap_block *after =
            (gx8002_image_b_heap_block *)(heap_base + block->next);
        after->previous = (uint32_t)((uint8_t *)previous - heap_base);
    }
    return lowest_free;
}

void gx8002_image_b_heap_plug_100099d4(void *block)
{
    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x200176dc);
    uint32_t original_lowest = control[2];
    gx8002_image_b_heap_block *lowest =
        gx8002_image_b_heap_plug_at_100099d4(
            (uint8_t *)(uintptr_t)control[0],
            (gx8002_image_b_heap_block *)(uintptr_t)control[1],
            (gx8002_image_b_heap_block *)(uintptr_t)original_lowest,
            (gx8002_image_b_heap_block *)block);
    if ((uint32_t)(uintptr_t)lowest != original_lowest)
        control[2] = (uint32_t)(uintptr_t)lowest;
}
