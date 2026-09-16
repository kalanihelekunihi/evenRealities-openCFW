/* SPDX-License-Identifier: MIT */
/* Recovered from backup image 0x100099d4; offsets are relative to heap base. */
#include "runtime_gx8002_backup_heap.h"
void backup_heap_merge(HeapBlock *pointer)
{
    volatile HeapBlock *block = pointer;
    uint32_t next_offset = block->next;
    uintptr_t base = (uintptr_t)backup_heap_state.base;
    volatile HeapBlock *next = (HeapBlock *)(base + next_offset);
    if (next != block && !next->used && next != backup_heap_state.end) {
        if (next == backup_heap_state.lowest_free)
            backup_heap_state.lowest_free = pointer;
        block->next = next->next;
        /* Reload matches stock even when headers alias. */
        volatile HeapBlock *following = (HeapBlock *)(base + next->next);
        following->previous = (uint32_t)((uintptr_t)block - base);
    }
    uint32_t previous_offset = block->previous;
    volatile HeapBlock *previous = (HeapBlock *)(base + previous_offset);
    if (previous != block && !previous->used) {
        if (block == backup_heap_state.lowest_free)
            backup_heap_state.lowest_free = (HeapBlock *)previous;
        previous->next = block->next;
        volatile HeapBlock *following = (HeapBlock *)(base + block->next);
        following->previous = previous_offset;
    }
}
