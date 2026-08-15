#include <assert.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "goodix_heap/goodix_heap.h"

typedef union {
    max_align_t alignment;
    uint8_t bytes[4096];
} heap_storage;

typedef struct {
    size_t calls;
    size_t requested;
} exhaustion_trace;

static void record_exhaustion(void *context, size_t requested_bytes) {
    exhaustion_trace *trace = context;
    ++trace->calls;
    trace->requested = requested_bytes;
}

void test_reconstructed_goodix_heap(void) {
    goodix_heap heap;
    heap_storage storage;
    exhaustion_trace exhaustion = {0};

    assert(goodix_heap_initialize(&heap, NULL, sizeof(storage.bytes),
                                  record_exhaustion, &exhaustion) == -1);
    assert(goodix_heap_initialize(&heap, storage.bytes, 1024u,
                                  record_exhaustion, &exhaustion) == -2);
    assert(goodix_heap_initialize(&heap, storage.bytes, sizeof(storage.bytes),
                                  record_exhaustion, &exhaustion) == 0);
    assert(goodix_heap_control(&heap) == &heap);
    assert(heap.first_block == 56u);
    assert(goodix_heap_size_to_bin(1032u) == 0u);
    assert(goodix_heap_size_to_bin(1033u) == 1u);
    const size_t initial_available = goodix_heap_available_bytes(&heap);
    assert(initial_available == sizeof(storage.bytes) - 72u);

    uint8_t *first = goodix_heap_zero_allocate(&heap, 1u);
    uint8_t *second = goodix_heap_zero_allocate(&heap, 24u);
    uint8_t *third = goodix_heap_zero_allocate(&heap, 32u);
    assert(first != NULL && second != NULL && third != NULL);
    for (size_t index = 0u; index < 24u; ++index) {
        assert(second[index] == 0u);
        second[index] = (uint8_t)(index + 1u);
    }

    goodix_heap_free(&heap, second);
    assert((heap.bin_bitmap & 1u) != 0u);
    uint8_t *reused = goodix_heap_allocate(&heap, 24u);
    assert(reused == second);
    goodix_heap_free(&heap, third);
    goodix_heap_free(&heap, reused);
    goodix_heap_free(&heap, first);
    assert(heap.top_block == heap.first_block);
    assert(heap.bin_bitmap == 0u);
    assert(goodix_heap_available_bytes(&heap) == initial_available);

    uint8_t *shrink = goodix_heap_allocate(&heap, 80u);
    uint8_t *guard = goodix_heap_allocate(&heap, 16u);
    assert(shrink != NULL && guard != NULL);
    memset(shrink, 0x5Au, 80u);
    assert(goodix_heap_reallocate(&heap, shrink, 16u) == shrink);
    for (size_t index = 0u; index < 16u; ++index) {
        assert(shrink[index] == UINT8_C(0x5A));
    }
    uint8_t *grown = goodix_heap_reallocate(&heap, shrink, 160u);
    assert(grown != NULL);
    for (size_t index = 0u; index < 16u; ++index) {
        assert(grown[index] == UINT8_C(0x5A));
    }
    goodix_heap_free(&heap, guard);
    goodix_heap_free(&heap, grown);

    void *large = goodix_heap_allocate(&heap, sizeof(storage.bytes));
    assert(large == NULL);
    assert(exhaustion.calls == 1u);
    assert(exhaustion.requested == sizeof(storage.bytes));
    assert(goodix_heap_reallocate(&heap, NULL, 12u) != NULL);

    /* Deterministic churn exercises both bins, split reuse, and two-way
     * coalescing under the sanitizer build. */
    heap_storage stress_storage;
    goodix_heap stress_heap;
    assert(goodix_heap_initialize(&stress_heap, stress_storage.bytes,
                                  sizeof(stress_storage.bytes), NULL,
                                  NULL) == 0);
    uint8_t *slots[16] = {0};
    size_t slot_sizes[16] = {0};
    uint8_t slot_patterns[16] = {0};
    uint32_t random = UINT32_C(0x13579BDF);
    for (size_t iteration = 0u; iteration < 1000u; ++iteration) {
        random = random * UINT32_C(1664525) + UINT32_C(1013904223);
        const size_t slot = (size_t)(random & 15u);
        if (slots[slot] != NULL) {
            for (size_t index = 0u; index < slot_sizes[slot]; ++index) {
                assert(slots[slot][index] == slot_patterns[slot]);
            }
        }
        if ((random & 3u) == 0u) {
            goodix_heap_free(&stress_heap, slots[slot]);
            slots[slot] = NULL;
            slot_sizes[slot] = 0u;
        } else {
            const size_t requested = (size_t)((random >> 8u) % 160u) + 1u;
            uint8_t *replacement = goodix_heap_reallocate(
                &stress_heap, slots[slot], requested);
            if (replacement != NULL) {
                const size_t preserved = slot_sizes[slot] < requested ?
                    slot_sizes[slot] : requested;
                for (size_t index = 0u; index < preserved; ++index) {
                    assert(replacement[index] == slot_patterns[slot]);
                }
                slot_patterns[slot] = (uint8_t)(iteration + 1u);
                memset(replacement, slot_patterns[slot], requested);
                slots[slot] = replacement;
                slot_sizes[slot] = requested;
            }
        }
    }
    for (size_t slot = 0u; slot < 16u; ++slot) {
        goodix_heap_free(&stress_heap, slots[slot]);
    }
    assert(stress_heap.top_block == stress_heap.first_block);
    assert(stress_heap.bin_bitmap == 0u);
}
