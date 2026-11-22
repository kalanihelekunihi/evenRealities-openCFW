/* One-image bounded allocator for DFU ATT attributes and authorized writes.
 * The arena storage belongs to bootloader RAM; these functions and their
 * two boundary pointers are source-built lower Cordio code and RAM. */
#if defined(R1_CORDIO_RTC0)
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "cordio_dfu_arena.h"

typedef struct {
    uint32_t bytes;
    uint32_t used;
} block_t;

static uint8_t *arena_begin;
static uint8_t *arena_end;

bool r1_cordio_dfu_arena_init(void *memory, uint32_t bytes)
{
    uintptr_t start = (uintptr_t)memory;
    if (memory == 0 || (start & 7u) != 0u ||
        (bytes & 7u) != 0u || bytes < 16u)
        return false;
#if !defined(R1_DFU_ARENA_HOST_TEST)
    if (start < 0x200064a8u || start >= 0x20040000u ||
        bytes > 0x20040000u - start)
        return false;
#endif
    arena_begin = memory;
    arena_end = arena_begin + bytes;
    block_t *first = (block_t *)arena_begin;
    first->bytes = bytes - sizeof(*first);
    first->used = 0u;
    return true;
}

void *r1_cordio_dfu_arena_alloc(size_t bytes)
{
    if (arena_begin == 0 || bytes == 0u || bytes > UINT32_MAX - 7u)
        return 0;
    uint32_t needed = ((uint32_t)bytes + 7u) & ~7u;
    for (uint8_t *at = arena_begin; at < arena_end;) {
        block_t *block = (block_t *)at;
        if ((uint32_t)(arena_end - at) < sizeof(*block) ||
            block->bytes < 8u || (block->bytes & 7u) != 0u ||
            block->bytes > (uint32_t)(arena_end - at - sizeof(*block)))
            return 0;
        if (block->used == 0u && block->bytes >= needed) {
            uint32_t remainder = block->bytes - needed;
            if (remainder >= sizeof(*block) + 8u) {
                block_t *next = (block_t *)(at + sizeof(*block) + needed);
                next->bytes = remainder - sizeof(*block);
                next->used = 0u;
                block->bytes = needed;
            }
            block->used = 1u;
            return at + sizeof(*block);
        }
        at += sizeof(*block) + block->bytes;
    }
    return 0;
}

void r1_cordio_dfu_arena_free(void *pointer)
{
    if (pointer == 0 || arena_begin == 0) return;
    block_t *previous = 0;
    for (uint8_t *at = arena_begin; at < arena_end;) {
        block_t *block = (block_t *)at;
        if ((uint32_t)(arena_end - at) < sizeof(*block) ||
            block->bytes < 8u || (block->bytes & 7u) != 0u ||
            block->bytes > (uint32_t)(arena_end - at - sizeof(*block)))
            return;
        uint8_t *next_at = at + sizeof(*block) + block->bytes;
        if (at + sizeof(*block) == pointer && block->used != 0u) {
            block->used = 0u;
            if (next_at < arena_end) {
                block_t *next = (block_t *)next_at;
                if ((uint32_t)(arena_end - next_at) >= sizeof(*next) &&
                    next->bytes >= 8u && (next->bytes & 7u) == 0u &&
                    next->bytes <=
                        (uint32_t)(arena_end - next_at - sizeof(*next)) &&
                    next->used == 0u)
                    block->bytes += sizeof(*next) + next->bytes;
            }
            if (previous != 0 && previous->used == 0u)
                previous->bytes += sizeof(*block) + block->bytes;
            return;
        }
        previous = block;
        at = next_at;
    }
}
#endif
