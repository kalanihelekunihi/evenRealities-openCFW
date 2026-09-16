/* SPDX-License-Identifier: MIT */
/* Recovered backup first-fit allocator; preserve unsigned stock arithmetic. */
#include "runtime_gx8002_backup_heap.h"
extern const char backup_heap_malloc_align[], backup_heap_malloc_large[];
extern int printf(const char *, ...);
void *backup_rt_malloc(uint32_t requested)
{
    if (!requested) return NULL;
    uint32_t size = (requested + 3u) & ~3u;
    if (size != requested) printf(backup_heap_malloc_align, requested, size);
    uint32_t usable = backup_heap_state.usable;
    if (size > usable) { printf(backup_heap_malloc_large); return NULL; }
    if (size < 12u) size = 12u;
    HeapBlock *lowest = backup_heap_state.lowest_free;
    uintptr_t base = (uintptr_t)backup_heap_state.base;
    uint32_t offset = (uint32_t)((uintptr_t)lowest - base);
    uint32_t limit = usable - size;
    while (offset < limit) {
        volatile HeapBlock *block = (HeapBlock *)(base + offset);
        if (!block->used) {
            uint32_t next = block->next;
            uint32_t span = next - offset;
            uint32_t available = span - 12u;
            if (available >= size) {
                uint32_t charge;
                if (available >= size + 24u) {
                    uint32_t split_offset = offset + size + 12u;
                    volatile HeapBlock *split = (HeapBlock *)(base + split_offset);
                    split->next = next;
                    split->previous = offset;
                    split->magic = 0x1ea0;
                    split->used = 0;
                    block->next = split_offset;
                    block->used = 1;
                    uint32_t following = split->next;
                    if (following != usable + 12u)
                        ((volatile HeapBlock *)(base + following))->previous = split_offset;
                    charge = size + 12u;
                } else {
                    block->used = 1;
                    charge = span;
                }
                uint32_t used = backup_heap_state.used_bytes + charge;
                uint32_t maximum = backup_heap_state.maximum_used_bytes;
                backup_heap_state.used_bytes = used;
                if (used > maximum) backup_heap_state.maximum_used_bytes = used;
                block->magic = 0x1ea0;
                if (block == lowest && block->used) {
                    HeapBlock *end = backup_heap_state.end;
                    if (block != end) {
                        uintptr_t current_base = (uintptr_t)backup_heap_state.base;
                        volatile HeapBlock *cursor = block;
                        do {
                            cursor = (HeapBlock *)(current_base + cursor->next);
                        } while (cursor->used && cursor != end);
                        backup_heap_state.lowest_free = (HeapBlock *)cursor;
                    }
                }
                return (void *)((uintptr_t)block + 12u);
            }
            offset = next;
        } else offset = block->next;
    }
    return NULL;
}
