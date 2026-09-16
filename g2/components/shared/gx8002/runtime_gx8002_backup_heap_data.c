/* SPDX-License-Identifier: MIT */
#include "runtime_gx8002_backup_heap.h"
volatile HeapState backup_heap_state __attribute__((section(".bss.backup_heap_state")));
const char backup_heap_initialize_message[] __attribute__((section(".heap_message.initialize"))) =
    "mem init, heap begin address 0x%x, size %d\n";
const char backup_heap_invalid_message[] __attribute__((section(".heap_message.invalid"))) =
    "mem init, error begin address 0x%x, and end address 0x%x\n";
const char backup_heap_free_range[] __attribute__((section(".heap_message.free_range"))) =
    "illegal memory\n";
const char backup_heap_free_invalid[] __attribute__((section(".heap_message.free_invalid"))) =
    "to free a bad data block:\n";
const char backup_heap_free_details[] __attribute__((section(".heap_message.free_details"))) =
    "mem: 0x%08x, used flag: %d, magic code: 0x%04x\n";
const char backup_heap_malloc_align[] __attribute__((section(".heap_message.malloc_align"))) =
    "malloc size %d, but align to %d\n";
const char backup_heap_malloc_large[] __attribute__((section(".heap_message.malloc_large"))) =
    "no memory\n";
const char backup_heap_realloc_large[] __attribute__((section(".heap_message.realloc_large"))) =
    "realloc: out of memory\n";
