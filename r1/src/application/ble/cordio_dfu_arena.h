#ifndef R1_CORDIO_DFU_ARENA_H
#define R1_CORDIO_DFU_ARENA_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

bool r1_cordio_dfu_arena_init(void *memory, uint32_t bytes);
void *r1_cordio_dfu_arena_alloc(size_t bytes);
void r1_cordio_dfu_arena_free(void *pointer);

#endif
