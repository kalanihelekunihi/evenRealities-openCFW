/* SPDX-License-Identifier: Apache-2.0
 * Image-B 0x10009c2c RT-Thread free from pinned rt_mem.c and native branches.
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
extern gx8002_image_b_heap_block *gx8002_image_b_heap_plug_at_100099d4(
    uint8_t *heap_base, gx8002_image_b_heap_block *heap_end,
    gx8002_image_b_heap_block *lowest_free,
    gx8002_image_b_heap_block *block);

void gx8002_image_b_heap_free_at_10009c2c(
    gx8002_image_b_heap_state *state, void *memory,
    int (*log)(const char *format, ...))
{
    if (memory == 0) return;
    uintptr_t address = (uintptr_t)memory;
    if (address < (uintptr_t)state->base ||
        address >= (uintptr_t)state->end) {
        log("illegal memory\n");
        return;
    }

    gx8002_image_b_heap_block *block =
        (gx8002_image_b_heap_block *)(address - 12u);
    if (block->used == 0u || block->magic != UINT16_C(0x1ea0)) {
        log("to free a bad data block:\n");
        log("mem: 0x%08x, used flag: %d, magic code: 0x%04x\n",
            (uint32_t)(uintptr_t)block, (uint32_t)block->used,
            (uint32_t)block->magic);
    }

    block->used = 0u;
    block->magic = UINT16_C(0x1ea0);
    if ((uintptr_t)block < (uintptr_t)state->lowest_free)
        state->lowest_free = block;
    uint32_t offset = (uint32_t)((uint8_t *)block - state->base);
    state->used_bytes -= block->next - offset;
    state->lowest_free = gx8002_image_b_heap_plug_at_100099d4(
        state->base, state->end, state->lowest_free, block);
}

void gx8002_image_b_heap_free_10009c2c(void *memory)
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
    gx8002_image_b_heap_free_at_10009c2c(
        &state, memory, gx8002_image_b_heap_log_10009934);
    if (control[2] != (uint32_t)(uintptr_t)state.lowest_free)
        control[2] = (uint32_t)(uintptr_t)state.lowest_free;
    if (control[4] != state.used_bytes) control[4] = state.used_bytes;
}
