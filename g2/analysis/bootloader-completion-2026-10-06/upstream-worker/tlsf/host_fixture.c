#include <assert.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

#include "tlsf.h"

enum { TARGET_ARENA_BYTES = 0x70800 };

typedef union {
    max_align_t align;
    unsigned char bytes[TARGET_ARENA_BYTES];
} arena_t;

typedef union {
    max_align_t align;
    unsigned char bytes[8192];
} control_t;

typedef union {
    max_align_t align;
    unsigned char bytes[512];
} small_pool_t;

typedef struct {
    size_t free_count;
    size_t max_free;
} pool_stats_t;

static void collect_free(void *ptr, size_t size, int used, void *ctx) {
    pool_stats_t *stats = (pool_stats_t *)ctx;
    (void)ptr;
    if (!used) {
        ++stats->free_count;
        if (size > stats->max_free) {
            stats->max_free = size;
        }
    }
}

static void basic_sizes_and_failures(void) {
    arena_t arena;
    tlsf_t tlsf = tlsf_create(arena.bytes);
    assert(tlsf != NULL);

    size_t control_bytes = tlsf_size();
    assert(control_bytes < sizeof(arena.bytes));
    pool_t pool = tlsf_add_pool(
            tlsf,
            arena.bytes + control_bytes,
            sizeof(arena.bytes) - control_bytes);
    assert(pool != NULL);

    void *p96 = tlsf_malloc(tlsf, 96);
    void *p256 = tlsf_malloc(tlsf, 256);
    void *p4096 = tlsf_malloc(tlsf, 4096);
    assert(p96 && p256 && p4096);
    assert(((uintptr_t)p96 % tlsf_align_size()) == 0);
    assert(((uintptr_t)p256 % tlsf_align_size()) == 0);
    assert(((uintptr_t)p4096 % tlsf_align_size()) == 0);
    assert(tlsf_block_size(p96) >= 96);
    assert(tlsf_block_size(p256) >= 256);
    assert(tlsf_block_size(p4096) >= 4096);

    memset(p96, 0x96, 96);
    memset(p256, 0x56, 256);
    memset(p4096, 0x41, 4096);
    assert(((unsigned char *)p96)[95] == 0x96);
    assert(((unsigned char *)p256)[255] == 0x56);
    assert(((unsigned char *)p4096)[4095] == 0x41);
    assert(tlsf_malloc(tlsf, 0) == NULL);
    assert(tlsf_malloc(tlsf, 0x80000) == NULL);
    assert(tlsf_malloc(tlsf, TARGET_ARENA_BYTES) == NULL);
    assert(tlsf_check(tlsf) == 0);
    assert(tlsf_check_pool(pool) == 0);

    tlsf_free(tlsf, p4096);
    tlsf_free(tlsf, p256);
    tlsf_free(tlsf, p96);
    assert(tlsf_check(tlsf) == 0);
    assert(tlsf_check_pool(pool) == 0);
    tlsf_destroy(tlsf);
}

static void adjacent_free_blocks_coalesce(void) {
    control_t control;
    small_pool_t pool_mem;
    tlsf_t tlsf = tlsf_create(control.bytes);
    assert(tlsf != NULL);
    pool_t pool = tlsf_add_pool(tlsf, pool_mem.bytes, sizeof(pool_mem.bytes));
    assert(pool != NULL);

    void *a = tlsf_malloc(tlsf, 96);
    void *b = tlsf_malloc(tlsf, 256);
    assert(a && b);

    pool_stats_t stats = {0, 0};
    tlsf_walk_pool(pool, collect_free, &stats);
    assert(stats.free_count == 1);
    assert(stats.max_free < 320);
    assert(tlsf_malloc(tlsf, 320) == NULL);

    tlsf_free(tlsf, a);
    tlsf_free(tlsf, b);
    assert(tlsf_check(tlsf) == 0);
    assert(tlsf_check_pool(pool) == 0);
    void *joined = tlsf_malloc(tlsf, 320);
    assert(joined != NULL);
    assert(tlsf_block_size(joined) >= 320);
    assert(tlsf_check(tlsf) == 0);
    assert(tlsf_check_pool(pool) == 0);

    tlsf_free(tlsf, joined);
    tlsf_destroy(tlsf);
}

static void huge_size_overflow_characterization(void) {
    arena_t arena;
    tlsf_t tlsf = tlsf_create(arena.bytes);
    assert(tlsf != NULL);
    size_t control_bytes = tlsf_size();
    pool_t pool = tlsf_add_pool(
            tlsf,
            arena.bytes + control_bytes,
            sizeof(arena.bytes) - control_bytes);
    assert(pool != NULL);

    /* Characterize this upstream revision; do not treat this as valid usage. */
    void *p = tlsf_malloc(tlsf, SIZE_MAX);
    if (p != NULL) {
        printf("TLSF v3.1 characterization: SIZE_MAX returned block of %zu bytes\n",
                tlsf_block_size(p));
        tlsf_free(tlsf, p);
    } else {
        puts("TLSF v3.1 characterization: SIZE_MAX returned NULL");
    }
    assert(tlsf_check(tlsf) == 0);
    assert(tlsf_check_pool(pool) == 0);
    tlsf_destroy(tlsf);
}

int main(void) {
    basic_sizes_and_failures();
    adjacent_free_blocks_coalesce();
    huge_size_overflow_characterization();
    puts("TLSF host fixtures passed: 96/256/4096, failure, adjacent coalescing");
    return 0;
}
