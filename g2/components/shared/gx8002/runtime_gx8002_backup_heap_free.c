/* SPDX-License-Identifier: MIT */
/* Recovered stock free semantics, including diagnostic-only header checks. */
#include "runtime_gx8002_backup_heap.h"
extern const char backup_heap_free_range[], backup_heap_free_invalid[], backup_heap_free_details[];
extern int printf(const char *, ...);
extern void backup_heap_merge(HeapBlock *);
void backup_rt_free(void *pointer)
{
    if (!pointer) return;
    uintptr_t address=(uintptr_t)pointer;
    uintptr_t base=(uintptr_t)backup_heap_state.base;
    if (address<base || address>=(uintptr_t)backup_heap_state.end) {
        printf(backup_heap_free_range);
        return;
    }
    HeapBlock *block=(HeapBlock *)(address-12u);
    if (!block->used || block->magic!=0x1ea0) {
        printf(backup_heap_free_invalid);
        uint32_t magic=block->magic;
        uint32_t used=block->used;
        printf(backup_heap_free_details,(void *)block,used,magic);
        base=(uintptr_t)backup_heap_state.base;
    }
    /* Preserve separate stock halfword stores to the ordinary-RAM header. */
    ((volatile HeapBlock *)block)->used=0;
    ((volatile HeapBlock *)block)->magic=0x1ea0;
    if ((uintptr_t)block<(uintptr_t)backup_heap_state.lowest_free)
        backup_heap_state.lowest_free=(HeapBlock *)block;
    uint32_t used=backup_heap_state.used_bytes;
    uint32_t next=block->next;
    backup_heap_state.used_bytes=(uint32_t)((uintptr_t)block-base)+used-next;
    backup_heap_merge((HeapBlock *)block);
}
