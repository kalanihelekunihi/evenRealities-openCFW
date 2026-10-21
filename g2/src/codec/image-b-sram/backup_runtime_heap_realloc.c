/* SPDX-License-Identifier: Apache-2.0
 * Image-B 0x10009ca4 RT-Thread realloc from pinned rt_mem.c and native ISA.
 */
#include <stdint.h>
#include <stddef.h>

typedef struct {
    volatile uint16_t magic;
    volatile uint16_t used;
    volatile uint32_t next;
    volatile uint32_t previous;
} gx8002_image_b_heap_block;

typedef struct {
    uint8_t *base;
    gx8002_image_b_heap_block *end;
    gx8002_image_b_heap_block *lowest_free;
    uint32_t aligned_size;
    uint32_t used_bytes;
    uint32_t maximum_used_bytes;
} gx8002_image_b_heap_state;

_Static_assert(sizeof(gx8002_image_b_heap_block) == 12u,
               "native heap block size");

extern int gx8002_image_b_heap_log_10009934(const char *format, ...);
extern void *gx8002_image_b_heap_alloc_at_10009ab8(
    gx8002_image_b_heap_state *state, uint32_t requested,
    int (*log)(const char *format, uint32_t first, uint32_t second));
extern void gx8002_image_b_heap_free_at_10009c2c(
    gx8002_image_b_heap_state *state, void *memory,
    int (*log)(const char *format, ...));
extern gx8002_image_b_heap_block *gx8002_image_b_heap_plug_at_100099d4(
    uint8_t *heap_base, gx8002_image_b_heap_block *heap_end,
    gx8002_image_b_heap_block *lowest_free,
    gx8002_image_b_heap_block *block);
extern void gx8002_image_b_copy_10011344(
    void *destination, const void *source, uint32_t count);

void *gx8002_image_b_heap_realloc_at_10009ca4(
    gx8002_image_b_heap_state *state, void *memory, uint32_t requested,
    int (*log)(const char *format, ...),
    int (*alloc_log)(const char *format, uint32_t first, uint32_t second))
{
    uint32_t amount = (requested + 3u) & ~UINT32_C(3);
    if (amount > state->aligned_size) {
        log("realloc: out of memory\n");
        return 0;
    }
    if (amount == 0u) {
        gx8002_image_b_heap_free_at_10009c2c(state, memory, log);
        return 0;
    }
    if (memory == 0)
        return gx8002_image_b_heap_alloc_at_10009ab8(
            state, amount, alloc_log);

    uintptr_t address = (uintptr_t)memory;
    if (address < (uintptr_t)state->base ||
        address >= (uintptr_t)state->end)
        return memory;

    gx8002_image_b_heap_block *block =
        (gx8002_image_b_heap_block *)(address - 12u);
    uint32_t offset = (uint32_t)((uint8_t *)block - state->base);
    uint32_t old_size = block->next - offset - 12u;
    if (amount == old_size) return memory;

    if (amount + 24u < old_size) {
        uint32_t second_offset = offset + 12u + amount;
        gx8002_image_b_heap_block *second =
            (gx8002_image_b_heap_block *)(state->base + second_offset);
        second->magic = UINT16_C(0x1ea0);
        second->used = 0u;
        second->next = block->next;
        second->previous = offset;
        block->next = second_offset;
        state->used_bytes -= old_size - amount;
        if (second->next != state->aligned_size + 12u) {
            gx8002_image_b_heap_block *following =
                (gx8002_image_b_heap_block *)(state->base + second->next);
            following->previous = second_offset;
        }
        if ((uintptr_t)second < (uintptr_t)state->lowest_free)
            state->lowest_free = second;
        state->lowest_free = gx8002_image_b_heap_plug_at_100099d4(
            state->base, state->end, state->lowest_free, second);
        return memory;
    }

    void *replacement = gx8002_image_b_heap_alloc_at_10009ab8(
        state, amount, alloc_log);
    if (replacement != 0) {
        gx8002_image_b_copy_10011344(
            replacement, memory, amount < old_size ? amount : old_size);
        gx8002_image_b_heap_free_at_10009c2c(state, memory, log);
    }
    return replacement;
}

static int realloc_alloc_log(const char *format, uint32_t first,
                             uint32_t second)
{
    return gx8002_image_b_heap_log_10009934(format, first, second);
}

void *gx8002_image_b_heap_realloc_10009ca4(void *memory, uint32_t requested)
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
    void *result = gx8002_image_b_heap_realloc_at_10009ca4(
        &state, memory, requested, gx8002_image_b_heap_log_10009934,
        realloc_alloc_log);
    if (control[2] != (uint32_t)(uintptr_t)state.lowest_free)
        control[2] = (uint32_t)(uintptr_t)state.lowest_free;
    if (control[4] != state.used_bytes) control[4] = state.used_bytes;
    if (control[5] != state.maximum_used_bytes)
        control[5] = state.maximum_used_bytes;
    return result;
}
