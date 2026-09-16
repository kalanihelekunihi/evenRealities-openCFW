/* SPDX-License-Identifier: MIT */
/* Recovered RT-style small-block heap initialization; 32-bit target ABI. */
#include "runtime_gx8002_backup_heap.h"
extern int printf(const char *, ...);
void backup_rt_heap_initialize(void *begin, void *end)
{
    uint32_t aligned_end=(uint32_t)(uintptr_t)end & ~3u;
    uint32_t aligned_begin=((uint32_t)(uintptr_t)begin+3u)&~3u;
    if (aligned_end<=24u || aligned_end-24u<aligned_begin) {
        printf(backup_heap_invalid_message,begin,end);
        return;
    }
    backup_heap_state.usable=aligned_end-24u-aligned_begin;
    backup_heap_state.base=(HeapBlock *)(uintptr_t)aligned_begin;
    printf(backup_heap_initialize_message,aligned_begin,backup_heap_state.usable);
    volatile HeapBlock *first=backup_heap_state.base;
    first->magic=0x1ea0;
    uint32_t next=backup_heap_state.usable+12u;
    first->previous=0;
    first->used=0;
    volatile HeapBlock *last=(HeapBlock *)((uintptr_t)first+next);
    first->next=next;
    last->magic=0x1ea0;
    backup_heap_state.end=(HeapBlock *)last;
    last->used=1;
    last->next=next;
    last->previous=next;
    backup_heap_state.lowest_free=(HeapBlock *)first;
}
