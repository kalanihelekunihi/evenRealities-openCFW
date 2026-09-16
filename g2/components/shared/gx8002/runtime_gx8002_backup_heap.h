/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_BACKUP_HEAP_H
#define OPEN_CFW_BACKUP_HEAP_H
#include <stdint.h>
#include <stddef.h>
typedef struct { uint16_t magic, used; uint32_t next, previous; } HeapBlock;
typedef struct { HeapBlock *base, *end, *lowest_free; uint32_t usable, used_bytes, maximum_used_bytes; } HeapState;
extern volatile HeapState backup_heap_state;
extern const char backup_heap_invalid_message[], backup_heap_initialize_message[];
_Static_assert(sizeof(HeapBlock)==12, "heap block ABI");
_Static_assert(sizeof(HeapState)==24, "heap state ABI");
_Static_assert(offsetof(HeapState,usable)==12, "heap state ABI");
_Static_assert(offsetof(HeapState,used_bytes)==16, "heap usage ABI");
_Static_assert(offsetof(HeapState,maximum_used_bytes)==20, "heap high-water ABI");
#endif
