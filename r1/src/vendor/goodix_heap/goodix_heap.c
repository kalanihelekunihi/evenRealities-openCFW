/*
 * Clean-room implementation of the R1 Goodix goodix_mem/GdMem pool manager.
 * The recovered target stores native pointers in a 44-byte control prefix.
 * This implementation uses checked pool-relative offsets, preserving the
 * allocator behavior without host pointer truncation or firmware addresses.
 */

#include "goodix_heap/goodix_heap.h"

#define GOODIX_HEAP_FLAG_PREVIOUS_USED UINT32_C(1)
#define GOODIX_HEAP_FLAG_CURRENT_USED UINT32_C(2)
#define GOODIX_HEAP_FLAG_MASK UINT32_C(3)

static size_t align_up(size_t value, size_t alignment) {
    return (value + alignment - 1u) & ~(alignment - 1u);
}

static uint32_t load_u32(const goodix_heap *heap, size_t offset) {
    return (uint32_t)heap->pool[offset] |
           (uint32_t)heap->pool[offset + 1u] << 8u |
           (uint32_t)heap->pool[offset + 2u] << 16u |
           (uint32_t)heap->pool[offset + 3u] << 24u;
}

static void store_u32(goodix_heap *heap, size_t offset, uint32_t value) {
    heap->pool[offset] = (uint8_t)value;
    heap->pool[offset + 1u] = (uint8_t)(value >> 8u);
    heap->pool[offset + 2u] = (uint8_t)(value >> 16u);
    heap->pool[offset + 3u] = (uint8_t)(value >> 24u);
}

static uint32_t block_encoded(const goodix_heap *heap, size_t block) {
    return load_u32(heap, block + 4u);
}

static size_t block_size(const goodix_heap *heap, size_t block) {
    return (size_t)(block_encoded(heap, block) >> 2u);
}

static void block_set(goodix_heap *heap, size_t block, size_t bytes,
                      uint32_t flags) {
    store_u32(heap, block + 4u,
              (uint32_t)(bytes << 2u) | (flags & GOODIX_HEAP_FLAG_MASK));
}

static size_t free_previous(const goodix_heap *heap, size_t block) {
    const uint32_t encoded = load_u32(heap, block + 8u);
    return encoded == UINT32_MAX ? GOODIX_HEAP_NONE : (size_t)encoded;
}

static size_t free_next(const goodix_heap *heap, size_t block) {
    const uint32_t encoded = load_u32(heap, block + 12u);
    return encoded == UINT32_MAX ? GOODIX_HEAP_NONE : (size_t)encoded;
}

static void free_set_previous(goodix_heap *heap, size_t block, size_t value) {
    store_u32(heap, block + 8u,
              value == GOODIX_HEAP_NONE ? UINT32_MAX : (uint32_t)value);
}

static void free_set_next(goodix_heap *heap, size_t block, size_t value) {
    store_u32(heap, block + 12u,
              value == GOODIX_HEAP_NONE ? UINT32_MAX : (uint32_t)value);
}

static bool block_offset_valid(const goodix_heap *heap, size_t block) {
    return heap != NULL && heap->initialized && block >= heap->first_block &&
           block + GOODIX_HEAP_BLOCK_HEADER_BYTES <= heap->pool_size;
}

static void set_next_boundary(goodix_heap *heap, size_t block,
                              bool previous_used) {
    const size_t next = block + block_size(heap, block);
    if (next + GOODIX_HEAP_BLOCK_HEADER_BYTES > heap->pool_size) {
        return;
    }
    store_u32(heap, next, (uint32_t)block_size(heap, block));
    uint32_t encoded = block_encoded(heap, next);
    if (previous_used) {
        encoded |= GOODIX_HEAP_FLAG_PREVIOUS_USED;
    } else {
        encoded &= ~GOODIX_HEAP_FLAG_PREVIOUS_USED;
    }
    store_u32(heap, next + 4u, encoded);
}

static void report_exhaustion(goodix_heap *heap, size_t bytes) {
    if (heap != NULL && heap->exhausted != NULL) {
        heap->exhausted(heap->exhausted_context, bytes);
    }
}

int32_t goodix_heap_initialize(goodix_heap *heap, void *pool,
                               size_t pool_size,
                               goodix_heap_exhausted_fn exhausted,
                               void *exhausted_context) {
    if (heap == NULL || pool == NULL) {
        return -1;
    }
    if (pool_size < GOODIX_HEAP_MINIMUM_POOL_BYTES ||
            pool_size > UINT32_MAX / 4u) {
        return -2;
    }
    uint8_t *pool_bytes = pool;
    for (size_t index = 0u; index < pool_size; ++index) {
        pool_bytes[index] = 0u;
    }
    heap->pool = pool;
    heap->pool_size = pool_size;
    heap->first_block = align_up(GOODIX_HEAP_CONTROL_BYTES + 7u, 8u);
    heap->top_block = heap->first_block;
    heap->bin_head[0] = GOODIX_HEAP_NONE;
    heap->bin_head[1] = GOODIX_HEAP_NONE;
    heap->bin_bitmap = 0u;
    heap->exhausted = exhausted;
    heap->exhausted_context = exhausted_context;
    heap->initialized = true;

    if (heap->first_block + 16u >= pool_size) {
        heap->initialized = false;
        return -2;
    }
    const size_t initial_bytes = pool_size - heap->first_block - 16u;
    block_set(heap, heap->top_block, initial_bytes,
              GOODIX_HEAP_FLAG_PREVIOUS_USED);
    return 0;
}

goodix_heap *goodix_heap_control(goodix_heap *heap) {
    return heap != NULL && heap->initialized ? heap : NULL;
}

size_t goodix_heap_size_to_bin(size_t adjusted_block_bytes) {
    return adjusted_block_bytes <= 1032u ? 0u : 1u;
}

bool goodix_heap_insert_free_block(goodix_heap *heap, size_t block) {
    if (!block_offset_valid(heap, block) || block == heap->top_block ||
            block_size(heap, block) < GOODIX_HEAP_MINIMUM_SPLIT_BYTES) {
        return false;
    }
    const size_t bin = goodix_heap_size_to_bin(block_size(heap, block));
    size_t current = heap->bin_head[bin];
    size_t previous = GOODIX_HEAP_NONE;
    while (current != GOODIX_HEAP_NONE &&
           block_size(heap, current) < block_size(heap, block)) {
        previous = current;
        current = free_next(heap, current);
    }
    free_set_previous(heap, block, previous);
    free_set_next(heap, block, current);
    if (previous == GOODIX_HEAP_NONE) {
        heap->bin_head[bin] = block;
    } else {
        free_set_next(heap, previous, block);
    }
    if (current != GOODIX_HEAP_NONE) {
        free_set_previous(heap, current, block);
    }
    heap->bin_bitmap |= UINT32_C(1) << bin;
    return true;
}

bool goodix_heap_unlink_free_block(goodix_heap *heap, size_t block,
                                   size_t bin) {
    if (!block_offset_valid(heap, block) || bin >= GOODIX_HEAP_BIN_COUNT) {
        return false;
    }
    const size_t previous = free_previous(heap, block);
    const size_t next = free_next(heap, block);
    if (previous == GOODIX_HEAP_NONE) {
        if (heap->bin_head[bin] != block) {
            return false;
        }
        heap->bin_head[bin] = next;
    } else {
        free_set_next(heap, previous, next);
    }
    if (next != GOODIX_HEAP_NONE) {
        free_set_previous(heap, next, previous);
    }
    free_set_previous(heap, block, GOODIX_HEAP_NONE);
    free_set_next(heap, block, GOODIX_HEAP_NONE);
    if (heap->bin_head[bin] == GOODIX_HEAP_NONE) {
        heap->bin_bitmap &= ~(UINT32_C(1) << bin);
    }
    return true;
}

static void *allocate_from_block(goodix_heap *heap, size_t block,
                                 size_t adjusted) {
    const uint32_t previous_flag =
        block_encoded(heap, block) & GOODIX_HEAP_FLAG_PREVIOUS_USED;
    const size_t original = block_size(heap, block);
    const size_t remainder = original - adjusted;
    if (remainder >= GOODIX_HEAP_MINIMUM_SPLIT_BYTES) {
        const size_t split = block + adjusted;
        block_set(heap, block, adjusted,
                  previous_flag | GOODIX_HEAP_FLAG_CURRENT_USED);
        block_set(heap, split, remainder, GOODIX_HEAP_FLAG_PREVIOUS_USED);
        set_next_boundary(heap, split, false);
        (void)goodix_heap_insert_free_block(heap, split);
    } else {
        block_set(heap, block, original,
                  previous_flag | GOODIX_HEAP_FLAG_CURRENT_USED);
        set_next_boundary(heap, block, true);
    }
    return &heap->pool[block + GOODIX_HEAP_BLOCK_HEADER_BYTES];
}

void *goodix_heap_allocate_core(goodix_heap *heap,
                                size_t adjusted_block_bytes) {
    if (heap == NULL || !heap->initialized ||
            adjusted_block_bytes < 16u || adjusted_block_bytes > UINT32_MAX / 4u) {
        return NULL;
    }
    const size_t first_bin = goodix_heap_size_to_bin(adjusted_block_bytes);
    for (size_t bin = first_bin; bin < GOODIX_HEAP_BIN_COUNT; ++bin) {
        size_t block = heap->bin_head[bin];
        while (block != GOODIX_HEAP_NONE &&
               block_size(heap, block) < adjusted_block_bytes) {
            block = free_next(heap, block);
        }
        if (block != GOODIX_HEAP_NONE) {
            if (!goodix_heap_unlink_free_block(heap, block, bin)) {
                return NULL;
            }
            return allocate_from_block(heap, block, adjusted_block_bytes);
        }
    }

    const size_t top = heap->top_block;
    const size_t available = block_size(heap, top);
    if (available < adjusted_block_bytes) {
        return NULL;
    }
    const uint32_t previous_flag =
        block_encoded(heap, top) & GOODIX_HEAP_FLAG_PREVIOUS_USED;
    block_set(heap, top, adjusted_block_bytes,
              previous_flag | GOODIX_HEAP_FLAG_CURRENT_USED);
    heap->top_block = top + adjusted_block_bytes;
    block_set(heap, heap->top_block, available - adjusted_block_bytes,
              GOODIX_HEAP_FLAG_PREVIOUS_USED);
    store_u32(heap, heap->top_block, (uint32_t)adjusted_block_bytes);
    return &heap->pool[top + GOODIX_HEAP_BLOCK_HEADER_BYTES];
}

void *goodix_heap_allocate(goodix_heap *heap, size_t bytes) {
    if (heap == NULL || !heap->initialized) {
        report_exhaustion(heap, bytes);
        return NULL;
    }
    const size_t request = bytes < GOODIX_HEAP_MINIMUM_REQUEST_BYTES ?
        GOODIX_HEAP_MINIMUM_REQUEST_BYTES : bytes;
    if (request > SIZE_MAX - 11u) {
        report_exhaustion(heap, bytes);
        return NULL;
    }
    const size_t adjusted = align_up(request, 4u) +
        GOODIX_HEAP_BLOCK_HEADER_BYTES;
    if (adjusted > heap->pool_size) {
        report_exhaustion(heap, bytes);
        return NULL;
    }
    void *allocation = goodix_heap_allocate_core(heap, adjusted);
    if (allocation == NULL) {
        report_exhaustion(heap, bytes);
    }
    return allocation;
}

void *goodix_heap_zero_allocate(goodix_heap *heap, size_t bytes) {
    void *allocation = goodix_heap_allocate(heap, bytes);
    if (allocation != NULL) {
        uint8_t *output = allocation;
        for (size_t index = 0u; index < bytes; ++index) {
            output[index] = 0u;
        }
    }
    return allocation;
}

void goodix_heap_free(goodix_heap *heap, void *allocation) {
    if (heap == NULL || !heap->initialized || allocation == NULL) {
        return;
    }
    const uintptr_t payload_address = (uintptr_t)allocation;
    const uintptr_t pool_address = (uintptr_t)heap->pool;
    if (payload_address < pool_address + heap->first_block +
                              GOODIX_HEAP_BLOCK_HEADER_BYTES ||
            payload_address >= pool_address + heap->pool_size) {
        return;
    }
    size_t block = (size_t)(payload_address - pool_address) -
        GOODIX_HEAP_BLOCK_HEADER_BYTES;
    uint32_t encoded = block_encoded(heap, block);
    if ((encoded & GOODIX_HEAP_FLAG_CURRENT_USED) == 0u) {
        return;
    }
    size_t bytes = (size_t)(encoded >> 2u);
    uint32_t previous_flag = encoded & GOODIX_HEAP_FLAG_PREVIOUS_USED;
    size_t next = block + bytes;

    if (next == heap->top_block) {
        bytes += block_size(heap, next);
        if (previous_flag == 0u) {
            const size_t previous_bytes = (size_t)load_u32(heap, block);
            if (previous_bytes <= block - heap->first_block) {
                const size_t previous = block - previous_bytes;
                const size_t bin = goodix_heap_size_to_bin(
                    block_size(heap, previous));
                if (goodix_heap_unlink_free_block(heap, previous, bin)) {
                    block = previous;
                    bytes += previous_bytes;
                    previous_flag = block_encoded(heap, block) &
                        GOODIX_HEAP_FLAG_PREVIOUS_USED;
                }
            }
        }
        heap->top_block = block;
        block_set(heap, block, bytes, previous_flag);
        return;
    }

    if (next + GOODIX_HEAP_BLOCK_HEADER_BYTES <= heap->pool_size &&
            (block_encoded(heap, next) &
             GOODIX_HEAP_FLAG_CURRENT_USED) == 0u) {
        const size_t next_bin = goodix_heap_size_to_bin(block_size(heap, next));
        if (goodix_heap_unlink_free_block(heap, next, next_bin)) {
            bytes += block_size(heap, next);
        }
    }
    if (previous_flag == 0u) {
        const size_t previous_bytes = (size_t)load_u32(heap, block);
        if (previous_bytes <= block - heap->first_block) {
            const size_t previous = block - previous_bytes;
            const size_t previous_bin = goodix_heap_size_to_bin(
                block_size(heap, previous));
            if (goodix_heap_unlink_free_block(heap, previous, previous_bin)) {
                block = previous;
                bytes += previous_bytes;
                previous_flag = block_encoded(heap, block) &
                    GOODIX_HEAP_FLAG_PREVIOUS_USED;
            }
        }
    }
    block_set(heap, block, bytes, previous_flag);
    set_next_boundary(heap, block, false);
    (void)goodix_heap_insert_free_block(heap, block);
}

void *goodix_heap_reallocate(goodix_heap *heap, void *allocation,
                             size_t bytes) {
    if (allocation == NULL) {
        return goodix_heap_zero_allocate(heap, bytes);
    }
    if (heap == NULL || !heap->initialized) {
        return NULL;
    }
    const uintptr_t payload_address = (uintptr_t)allocation;
    const uintptr_t pool_address = (uintptr_t)heap->pool;
    if (payload_address < pool_address + heap->first_block + 8u ||
            payload_address >= pool_address + heap->pool_size) {
        return NULL;
    }
    const size_t block = (size_t)(payload_address - pool_address) - 8u;
    const size_t old_total = block_size(heap, block);
    const size_t request = bytes < 8u ? 8u : bytes;
    if (request > SIZE_MAX - 11u) {
        return NULL;
    }
    const size_t new_total = align_up(request, 4u) + 8u;
    if (new_total <= old_total) {
        const size_t remainder = old_total - new_total;
        if (remainder >= GOODIX_HEAP_MINIMUM_SPLIT_BYTES) {
            const uint32_t flags = block_encoded(heap, block) &
                GOODIX_HEAP_FLAG_MASK;
            block_set(heap, block, new_total, flags);
            const size_t split = block + new_total;
            block_set(heap, split, remainder,
                      GOODIX_HEAP_FLAG_PREVIOUS_USED |
                      GOODIX_HEAP_FLAG_CURRENT_USED);
            goodix_heap_free(heap, &heap->pool[split + 8u]);
        }
        return allocation;
    }

    void *replacement = goodix_heap_zero_allocate(heap, bytes);
    if (replacement == NULL) {
        return NULL;
    }
    const size_t old_payload = old_total - 8u;
    const size_t copy = old_payload < bytes ? old_payload : bytes;
    uint8_t *destination = replacement;
    const uint8_t *source = allocation;
    for (size_t index = 0u; index < copy; ++index) {
        destination[index] = source[index];
    }
    goodix_heap_free(heap, allocation);
    return replacement;
}

size_t goodix_heap_available_bytes(const goodix_heap *heap) {
    if (heap == NULL || !heap->initialized ||
            heap->top_block + 16u >= heap->pool_size) {
        return 0u;
    }
    return heap->pool_size - heap->top_block - 16u;
}
