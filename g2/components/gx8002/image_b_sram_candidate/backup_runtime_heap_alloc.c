/* SPDX-License-Identifier: Apache-2.0
 * Image-B 0x10009ab8 RT-Thread allocator from pinned rt_mem.c, adjusted to
 * native observed logging branches and fixed SRAM control layout.
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

typedef struct {
    uint8_t *base;
    gx8002_image_b_heap_block *end;
    gx8002_image_b_heap_block *lowest_free;
    uint32_t aligned_size;
    uint32_t used_bytes;
    uint32_t maximum_used_bytes;
} gx8002_image_b_heap_state;

typedef int (*gx8002_image_b_heap_alloc_log_fn)(
    const char *format, uint32_t first, uint32_t second);
extern int gx8002_image_b_heap_log_10009934(
    const char *format, uint32_t first, uint32_t second);

static const char heap_align_message[] =
    "malloc size %d, but align to %d\n";
static const char heap_exhausted_message[] = "no memory\n";

void *gx8002_image_b_heap_alloc_at_10009ab8(
    gx8002_image_b_heap_state *state, uint32_t requested,
    gx8002_image_b_heap_alloc_log_fn log)
{
    if (requested == 0u) return 0;
    uint32_t amount = (requested + 3u) & ~UINT32_C(3);
    if (requested != amount)
        log(heap_align_message, requested, amount);
    if (amount > state->aligned_size) {
        log(heap_exhausted_message, 0u, 0u);
        return 0;
    }
    if (amount < 12u) amount = 12u;

    uint32_t offset = (uint32_t)((uint8_t *)state->lowest_free - state->base);
    while (offset < state->aligned_size - amount) {
        gx8002_image_b_heap_block *block =
            (gx8002_image_b_heap_block *)(state->base + offset);
        uint32_t next_offset = block->next;
        if (block->used == 0u && next_offset - (offset + 12u) >= amount) {
            if (next_offset - (offset + 12u) >= amount + 24u) {
                uint32_t second_offset = offset + 12u + amount;
                gx8002_image_b_heap_block *second =
                    (gx8002_image_b_heap_block *)(state->base + second_offset);
                second->next = next_offset;
                second->previous = offset;
                second->magic = UINT16_C(0x1ea0);
                second->used = 0u;
                block->next = second_offset;
                block->used = 1u;
                if (second->next != state->aligned_size + 12u) {
                    gx8002_image_b_heap_block *following =
                        (gx8002_image_b_heap_block *)(state->base + second->next);
                    following->previous = second_offset;
                }
                state->used_bytes += amount + 12u;
            } else {
                block->used = 1u;
                state->used_bytes += next_offset - offset;
            }
            if (state->maximum_used_bytes < state->used_bytes)
                state->maximum_used_bytes = state->used_bytes;
            block->magic = UINT16_C(0x1ea0);

            if (block == state->lowest_free) {
                while (state->lowest_free->used != 0u &&
                       state->lowest_free != state->end) {
                    state->lowest_free =
                        (gx8002_image_b_heap_block *)(state->base +
                            state->lowest_free->next);
                }
            }
            return (uint8_t *)block + 12u;
        }
        offset = next_offset;
    }
    return 0;
}

void *gx8002_image_b_heap_alloc_10009ab8(uint32_t requested)
{
    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x200176dc);
    gx8002_image_b_heap_state state = {
        .base = (uint8_t *)(uintptr_t)control[0],
        .end = (gx8002_image_b_heap_block *)(uintptr_t)control[1],
        .lowest_free = (gx8002_image_b_heap_block *)(uintptr_t)control[2],
        .aligned_size = control[3],
        .used_bytes = control[4],
        .maximum_used_bytes = control[5],
    };
    void *result = gx8002_image_b_heap_alloc_at_10009ab8(
        &state, requested, gx8002_image_b_heap_log_10009934);
    if (control[2] != (uint32_t)(uintptr_t)state.lowest_free)
        control[2] = (uint32_t)(uintptr_t)state.lowest_free;
    if (control[4] != state.used_bytes) control[4] = state.used_bytes;
    if (control[5] != state.maximum_used_bytes)
        control[5] = state.maximum_used_bytes;
    return result;
}
