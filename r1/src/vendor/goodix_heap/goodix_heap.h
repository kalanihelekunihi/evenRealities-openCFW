#ifndef OPENR1_RECONSTRUCTED_GOODIX_HEAP_H
#define OPENR1_RECONSTRUCTED_GOODIX_HEAP_H

/*
 * Owner-authorized clean-room reconstruction of the Goodix goodix_mem/GdMem
 * pool manager recovered from the R1 application image. This is not Goodix
 * source. Exact extents and behavioral correlation are documented in
 * docs/correlation/GOODIX-HEAP-REDUCTION-CORRELATION.md.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define GOODIX_HEAP_CONTROL_BYTES 44u
#define GOODIX_HEAP_MINIMUM_POOL_BYTES 1025u
#define GOODIX_HEAP_BLOCK_HEADER_BYTES 8u
#define GOODIX_HEAP_MINIMUM_REQUEST_BYTES 8u
#define GOODIX_HEAP_MINIMUM_SPLIT_BYTES 16u
#define GOODIX_HEAP_BIN_COUNT 2u
#define GOODIX_HEAP_NONE SIZE_MAX

typedef void (*goodix_heap_exhausted_fn)(void *context,
                                         size_t requested_bytes);

typedef struct {
    uint8_t *pool;
    size_t pool_size;
    size_t first_block;
    size_t top_block;
    size_t bin_head[GOODIX_HEAP_BIN_COUNT];
    uint32_t bin_bitmap;
    goodix_heap_exhausted_fn exhausted;
    void *exhausted_context;
    bool initialized;
} goodix_heap;

/* Recovered goodix_mem_init contract: -1 null pool, -2 invalid size. */
int32_t goodix_heap_initialize(goodix_heap *heap, void *pool,
                               size_t pool_size,
                               goodix_heap_exhausted_fn exhausted,
                               void *exhausted_context);
goodix_heap *goodix_heap_control(goodix_heap *heap);

void *goodix_heap_zero_allocate(goodix_heap *heap, size_t bytes);
void *goodix_heap_allocate(goodix_heap *heap, size_t bytes);
void goodix_heap_free(goodix_heap *heap, void *allocation);
void *goodix_heap_reallocate(goodix_heap *heap, void *allocation,
                             size_t bytes);
size_t goodix_heap_available_bytes(const goodix_heap *heap);

/* Explicit counterparts of the recovered allocator-internal leaves. */
size_t goodix_heap_size_to_bin(size_t adjusted_block_bytes);
bool goodix_heap_insert_free_block(goodix_heap *heap, size_t block_offset);
bool goodix_heap_unlink_free_block(goodix_heap *heap, size_t block_offset,
                                   size_t bin);
void *goodix_heap_allocate_core(goodix_heap *heap,
                                size_t adjusted_block_bytes);

#endif
