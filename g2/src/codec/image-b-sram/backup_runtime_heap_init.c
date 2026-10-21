/* SPDX-License-Identifier: Apache-2.0
 * Image-B 0x10009a44 / 0x10009f10 RT-Thread heap initialization.
 * Matched to pinned NationalChip utility/rt_malloc/rt_mem.c and native body.
 */
#include <stdint.h>

typedef int (*gx8002_image_b_heap_log_fn)(const char *, uint32_t, uint32_t);
extern int gx8002_image_b_heap_log_10009934(
    const char *format, uint32_t first, uint32_t second);

static const char heap_init_ok[] =
    "mem init, heap begin address 0x%x, size %d\n";
static const char heap_init_error[] =
    "mem init, error begin address 0x%x, and end address 0x%x\n";

typedef struct {
    volatile uint16_t magic;
    volatile uint16_t used;
    volatile uint32_t next;
    volatile uint32_t previous;
} gx8002_image_b_heap_block;

void gx8002_image_b_heap_init_at_10009a44(
    uintptr_t begin_address, uintptr_t end_address,
    volatile uint32_t *control, gx8002_image_b_heap_log_fn log)
{
    uintptr_t begin = (begin_address + 3u) & ~(uintptr_t)3u;
    uintptr_t end = end_address & ~(uintptr_t)3u;
    if (end <= 24u || end - 24u < begin) {
        log(heap_init_error, (uint32_t)begin_address, (uint32_t)end_address);
        return;
    }

    uint32_t size = (uint32_t)(end - begin - 24u);
    control[3] = size;
    control[0] = (uint32_t)begin;
    log(heap_init_ok, (uint32_t)begin, size);

    volatile gx8002_image_b_heap_block *first =
        (volatile gx8002_image_b_heap_block *)begin;
    uint32_t tail_offset = size + 12u;
    first->magic = UINT16_C(0x1ea0);
    first->next = tail_offset;
    first->previous = 0u;
    first->used = 0u;

    volatile gx8002_image_b_heap_block *last =
        (volatile gx8002_image_b_heap_block *)(begin + tail_offset);
    last->magic = UINT16_C(0x1ea0);
    last->used = 1u;
    last->next = tail_offset;
    last->previous = tail_offset;
    control[1] = (uint32_t)(uintptr_t)last;
    control[2] = (uint32_t)begin;
}

void gx8002_image_b_heap_init_10009a44(
    uintptr_t begin_address, uintptr_t end_address)
{
    gx8002_image_b_heap_init_at_10009a44(
        begin_address, end_address,
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x200176dc),
        gx8002_image_b_heap_log_10009934);
}

uint32_t gx8002_image_b_heap_start_10009f10(void)
{
    gx8002_image_b_heap_init_10009a44(
        (uintptr_t)UINT32_C(0x2001bb80),
        (uintptr_t)UINT32_C(0x2002cb80));
    return 0u;
}
