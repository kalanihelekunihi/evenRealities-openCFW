/* SPDX-License-Identifier: MIT */
/* Recovered backup realloc, including stock shrink threshold and range behavior. */
#include "runtime_gx8002_backup_heap.h"
extern void *rt_malloc(uint32_t);
extern void rt_free(void *);
extern void backup_heap_merge(HeapBlock *);
extern void *memcpy(void *, const void *, size_t);
extern int printf(const char *, ...);
extern const char backup_heap_realloc_large[];
void *backup_rt_realloc(void *pointer, uint32_t requested)
{
    uint32_t size = (requested + 3u) & ~3u;
    uint32_t usable = backup_heap_state.usable;
    if (size > usable) { printf(backup_heap_realloc_large); return NULL; }
    if (!size) { rt_free(pointer); return NULL; }
    if (!pointer) return rt_malloc(size);
    uintptr_t base = (uintptr_t)backup_heap_state.base;
    if ((uintptr_t)pointer < base || (uintptr_t)pointer >= (uintptr_t)backup_heap_state.end)
        return pointer;
    volatile HeapBlock *block = (HeapBlock *)((uintptr_t)pointer - 12u);
    uint32_t offset = (uint32_t)((uintptr_t)block - base);
    uint32_t next = block->next;
    uint32_t old_size = next - 12u - offset;
    if (size == old_size) return pointer;
    if (old_size > size + 24u) {
        uint32_t used = backup_heap_state.used_bytes + size - old_size;
        uint32_t split_offset = offset + size + 12u;
        volatile HeapBlock *split = (HeapBlock *)(base + split_offset);
        split->magic = 0x1ea0;
        split->used = 0;
        split->next = next;
        split->previous = offset;
        block->next = split_offset;
        uint32_t following = split->next;
        backup_heap_state.used_bytes = used;
        if (following != usable + 12u)
            ((volatile HeapBlock *)(base + following))->previous = split_offset;
        if ((uintptr_t)split < (uintptr_t)backup_heap_state.lowest_free)
            backup_heap_state.lowest_free = (HeapBlock *)split;
        backup_heap_merge((HeapBlock *)split);
        return pointer;
    }
    void *replacement = rt_malloc(size);
    if (!replacement) return NULL;
    memcpy(replacement, pointer, size < old_size ? size : old_size);
    rt_free(pointer);
    return replacement;
}
