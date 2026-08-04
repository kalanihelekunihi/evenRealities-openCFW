/*
 * Genuine 32-bit execution oracle for the source-owned G2 TLSF allocator.
 *
 * This translation unit deliberately uses the same freestanding prefix and
 * byte-preserved upstream source as the Apollo overlay. WebAssembly's ILP32
 * data model exercises the allocator with real 32-bit pointers while keeping
 * the test deterministic and independent of the host process ABI.
 */

#include "../../components/apollo_main/core_overlay/runtime_tlsf.c"
#include "../../third_party/tlsf/tlsf.c"

_Static_assert(__wasm32__ == 1, "fixture must compile for wasm32");
_Static_assert(sizeof(short) == 2, "wasm32 short ABI changed");
_Static_assert(sizeof(int) == 4, "wasm32 int ABI changed");
_Static_assert(sizeof(long) == 4, "wasm32 must use ILP32");
_Static_assert(sizeof(void *) == 4, "wasm32 pointer ABI changed");
_Static_assert(sizeof(size_t) == 4, "wasm32 size_t ABI changed");
_Static_assert(sizeof(ptrdiff_t) == 4, "wasm32 ptrdiff_t ABI changed");

enum {
    OPEN_CFW_TLSF_WASM_ARENA_SIZE = 128U * 1024U,
    OPEN_CFW_TLSF_WASM_COALESCE_SLOTS = 256U,
    OPEN_CFW_TLSF_WASM_EXHAUST_SLOTS = 160U,
    OPEN_CFW_TLSF_WASM_STRESS_SLOTS = 64U,
    OPEN_CFW_TLSF_WASM_STRESS_ITERATIONS = 5000U
};

_Alignas(64)
static unsigned char
open_cfw_tlsf_wasm_arena[OPEN_CFW_TLSF_WASM_ARENA_SIZE];

static void *
open_cfw_tlsf_wasm_coalesce_allocations[
    OPEN_CFW_TLSF_WASM_COALESCE_SLOTS
];
static void *
open_cfw_tlsf_wasm_exhaust_allocations[
    OPEN_CFW_TLSF_WASM_EXHAUST_SLOTS
];
static void *
open_cfw_tlsf_wasm_stress_allocations[
    OPEN_CFW_TLSF_WASM_STRESS_SLOTS
];
static unsigned int
open_cfw_tlsf_wasm_stress_sizes[OPEN_CFW_TLSF_WASM_STRESS_SLOTS];
static unsigned char
open_cfw_tlsf_wasm_stress_patterns[OPEN_CFW_TLSF_WASM_STRESS_SLOTS];

static void open_cfw_tlsf_wasm_zero_arena(void)
{
    unsigned int index;

    for (index = 0U; index < OPEN_CFW_TLSF_WASM_ARENA_SIZE; ++index) {
        open_cfw_tlsf_wasm_arena[index] = 0U;
    }
}

static open_cfw_tlsf_t open_cfw_tlsf_wasm_create(void)
{
    open_cfw_tlsf_wasm_zero_arena();
    return open_cfw_tlsf_create_with_pool(
        open_cfw_tlsf_wasm_arena,
        OPEN_CFW_TLSF_WASM_ARENA_SIZE
    );
}

static int open_cfw_tlsf_wasm_is_aligned(
    const void *pointer,
    unsigned int alignment
)
{
    return (
        ((__UINTPTR_TYPE__)pointer & (__UINTPTR_TYPE__)(alignment - 1U))
        == 0U
    );
}

static unsigned char open_cfw_tlsf_wasm_pattern_byte(
    unsigned char pattern,
    unsigned int index
)
{
    return (unsigned char)(
        (unsigned int)pattern + index * 29U + (index >> 3)
    );
}

static void open_cfw_tlsf_wasm_fill(
    void *allocation,
    unsigned int size,
    unsigned char pattern
)
{
    unsigned char *bytes = (unsigned char *)allocation;
    unsigned int index;

    for (index = 0U; index < size; ++index) {
        bytes[index] = open_cfw_tlsf_wasm_pattern_byte(pattern, index);
    }
}

static int open_cfw_tlsf_wasm_verify(
    const void *allocation,
    unsigned int size,
    unsigned char pattern
)
{
    const unsigned char *bytes = (const unsigned char *)allocation;
    unsigned int index;

    for (index = 0U; index < size; ++index) {
        if (
            bytes[index]
            != open_cfw_tlsf_wasm_pattern_byte(pattern, index)
        ) {
            return 0;
        }
    }
    return 1;
}

static unsigned int open_cfw_tlsf_wasm_next(unsigned int *state)
{
    unsigned int value = *state;

    value ^= value << 13;
    value ^= value >> 17;
    value ^= value << 5;
    *state = value;
    return value;
}

static unsigned int open_cfw_tlsf_wasm_check_constants(void)
{
    if (open_cfw_tlsf_size() != 0xC74U) {
        return 1U;
    }
    if (open_cfw_tlsf_align_size() != 4U) {
        return 2U;
    }
    if (open_cfw_tlsf_block_size_min() != 12U) {
        return 3U;
    }
    if (open_cfw_tlsf_block_size_max() != 0x40000000U) {
        return 4U;
    }
    if (open_cfw_tlsf_pool_overhead() != 8U) {
        return 5U;
    }
    if (open_cfw_tlsf_alloc_overhead() != 4U) {
        return 6U;
    }
    return 0U;
}

static unsigned int open_cfw_tlsf_wasm_check_basic(void)
{
    open_cfw_tlsf_t tlsf = open_cfw_tlsf_wasm_create();
    open_cfw_tlsf_pool_t pool;
    void *small;
    void *resized;
    void *aligned;
    unsigned int size;

    if (tlsf == (open_cfw_tlsf_t)0) {
        return 20U;
    }
    pool = open_cfw_tlsf_get_pool(tlsf);
    if (
        pool
        != (open_cfw_tlsf_pool_t)(
            open_cfw_tlsf_wasm_arena + open_cfw_tlsf_size()
        )
    ) {
        return 21U;
    }
    if (open_cfw_tlsf_check(tlsf) != 0) {
        return 22U;
    }
    if (open_cfw_tlsf_check_pool(pool) != 0) {
        return 23U;
    }

    small = open_cfw_tlsf_malloc(tlsf, 33U);
    if (small == (void *)0) {
        return 24U;
    }
    if (!open_cfw_tlsf_wasm_is_aligned(small, 4U)) {
        return 25U;
    }
    size = (unsigned int)open_cfw_tlsf_block_size(small);
    if (size < 33U || (size & 3U) != 0U) {
        return 26U;
    }
    open_cfw_tlsf_wasm_fill(small, 33U, 0x39U);

    aligned = open_cfw_tlsf_memalign(tlsf, 64U, 257U);
    if (aligned == (void *)0) {
        return 27U;
    }
    if (!open_cfw_tlsf_wasm_is_aligned(aligned, 64U)) {
        return 28U;
    }
    if (open_cfw_tlsf_block_size(aligned) < 257U) {
        return 29U;
    }
    open_cfw_tlsf_wasm_fill(aligned, 257U, 0xA7U);

    resized = open_cfw_tlsf_realloc(tlsf, small, 1024U);
    if (resized == (void *)0) {
        return 30U;
    }
    if (!open_cfw_tlsf_wasm_verify(resized, 33U, 0x39U)) {
        return 31U;
    }
    if (open_cfw_tlsf_block_size(resized) < 1024U) {
        return 32U;
    }
    open_cfw_tlsf_wasm_fill(resized, 1024U, 0x5CU);

    small = open_cfw_tlsf_realloc(tlsf, resized, 19U);
    if (small == (void *)0) {
        return 33U;
    }
    if (!open_cfw_tlsf_wasm_verify(small, 19U, 0x5CU)) {
        return 34U;
    }
    if (!open_cfw_tlsf_wasm_verify(aligned, 257U, 0xA7U)) {
        return 35U;
    }

    open_cfw_tlsf_free(tlsf, small);
    open_cfw_tlsf_free(tlsf, aligned);
    if (open_cfw_tlsf_check(tlsf) != 0) {
        return 36U;
    }
    if (open_cfw_tlsf_check_pool(pool) != 0) {
        return 37U;
    }
    return 0U;
}

static unsigned int open_cfw_tlsf_wasm_check_coalescing(void)
{
    open_cfw_tlsf_t tlsf = open_cfw_tlsf_wasm_create();
    open_cfw_tlsf_pool_t pool;
    unsigned int count;
    unsigned int index;
    unsigned int first;
    void *combined;

    if (tlsf == (open_cfw_tlsf_t)0) {
        return 40U;
    }
    pool = open_cfw_tlsf_get_pool(tlsf);
    for (count = 0U; count < OPEN_CFW_TLSF_WASM_COALESCE_SLOTS; ++count) {
        void *allocation = open_cfw_tlsf_malloc(tlsf, 512U);

        open_cfw_tlsf_wasm_coalesce_allocations[count] = allocation;
        if (allocation == (void *)0) {
            break;
        }
    }
    if (count == OPEN_CFW_TLSF_WASM_COALESCE_SLOTS) {
        return 41U;
    }
    if (count < 8U) {
        return 42U;
    }
    if (open_cfw_tlsf_malloc(tlsf, 512U) != (void *)0) {
        return 43U;
    }

    first = count / 2U;
    if (first + 1U >= count) {
        return 44U;
    }
    open_cfw_tlsf_free(
        tlsf,
        open_cfw_tlsf_wasm_coalesce_allocations[first]
    );
    open_cfw_tlsf_free(
        tlsf,
        open_cfw_tlsf_wasm_coalesce_allocations[first + 1U]
    );
    open_cfw_tlsf_wasm_coalesce_allocations[first] = (void *)0;
    open_cfw_tlsf_wasm_coalesce_allocations[first + 1U] = (void *)0;

    combined = open_cfw_tlsf_malloc(tlsf, 900U);
    if (combined == (void *)0) {
        return 45U;
    }
    if (open_cfw_tlsf_block_size(combined) < 900U) {
        return 46U;
    }
    if (open_cfw_tlsf_check(tlsf) != 0) {
        return 47U;
    }
    if (open_cfw_tlsf_check_pool(pool) != 0) {
        return 48U;
    }

    open_cfw_tlsf_free(tlsf, combined);
    for (index = 0U; index < count; ++index) {
        if (
            open_cfw_tlsf_wasm_coalesce_allocations[index]
            != (void *)0
        ) {
            open_cfw_tlsf_free(
                tlsf,
                open_cfw_tlsf_wasm_coalesce_allocations[index]
            );
        }
    }
    if (open_cfw_tlsf_check(tlsf) != 0) {
        return 49U;
    }
    if (open_cfw_tlsf_check_pool(pool) != 0) {
        return 50U;
    }
    return 0U;
}

static unsigned int open_cfw_tlsf_wasm_check_exhaustion(void)
{
    open_cfw_tlsf_t tlsf = open_cfw_tlsf_wasm_create();
    open_cfw_tlsf_pool_t pool;
    unsigned int count;
    unsigned int index;

    if (tlsf == (open_cfw_tlsf_t)0) {
        return 60U;
    }
    pool = open_cfw_tlsf_get_pool(tlsf);
    for (count = 0U; count < OPEN_CFW_TLSF_WASM_EXHAUST_SLOTS; ++count) {
        void *allocation = open_cfw_tlsf_malloc(tlsf, 1024U);

        open_cfw_tlsf_wasm_exhaust_allocations[count] = allocation;
        if (allocation == (void *)0) {
            break;
        }
    }
    if (count == OPEN_CFW_TLSF_WASM_EXHAUST_SLOTS) {
        return 61U;
    }
    if (count < 16U) {
        return 62U;
    }
    if (open_cfw_tlsf_malloc(tlsf, 1024U) != (void *)0) {
        return 63U;
    }
    if (open_cfw_tlsf_check(tlsf) != 0) {
        return 64U;
    }
    if (open_cfw_tlsf_check_pool(pool) != 0) {
        return 65U;
    }

    for (index = 0U; index < count; ++index) {
        open_cfw_tlsf_free(
            tlsf,
            open_cfw_tlsf_wasm_exhaust_allocations[index]
        );
    }
    if (open_cfw_tlsf_check(tlsf) != 0) {
        return 66U;
    }
    if (open_cfw_tlsf_check_pool(pool) != 0) {
        return 67U;
    }
    return 0U;
}

static unsigned int open_cfw_tlsf_wasm_stress_failure(
    unsigned int iteration,
    unsigned int reason
)
{
    return 10000U + iteration * 10U + reason;
}

static unsigned int open_cfw_tlsf_wasm_check_stress(void)
{
    open_cfw_tlsf_t tlsf = open_cfw_tlsf_wasm_create();
    open_cfw_tlsf_pool_t pool;
    unsigned int state = 0x6D2B79F5U;
    unsigned int iteration;
    unsigned int index;

    if (tlsf == (open_cfw_tlsf_t)0) {
        return 80U;
    }
    pool = open_cfw_tlsf_get_pool(tlsf);
    for (index = 0U; index < OPEN_CFW_TLSF_WASM_STRESS_SLOTS; ++index) {
        open_cfw_tlsf_wasm_stress_allocations[index] = (void *)0;
        open_cfw_tlsf_wasm_stress_sizes[index] = 0U;
        open_cfw_tlsf_wasm_stress_patterns[index] = 0U;
    }

    for (
        iteration = 0U;
        iteration < OPEN_CFW_TLSF_WASM_STRESS_ITERATIONS;
        ++iteration
    ) {
        unsigned int random = open_cfw_tlsf_wasm_next(&state);
        unsigned int slot = random % OPEN_CFW_TLSF_WASM_STRESS_SLOTS;
        void *allocation =
            open_cfw_tlsf_wasm_stress_allocations[slot];

        if (allocation == (void *)0) {
            unsigned int requested =
                open_cfw_tlsf_wasm_next(&state) % 2048U + 1U;
            unsigned int aligned =
                open_cfw_tlsf_wasm_next(&state) & 3U;
            unsigned int alignment = 4U;

            if (aligned == 0U) {
                alignment =
                    1U << (2U + (open_cfw_tlsf_wasm_next(&state) % 5U));
                allocation = open_cfw_tlsf_memalign(
                    tlsf,
                    alignment,
                    requested
                );
            } else {
                allocation = open_cfw_tlsf_malloc(tlsf, requested);
            }
            if (allocation != (void *)0) {
                unsigned char pattern = (unsigned char)(
                    open_cfw_tlsf_wasm_next(&state) & 0xFFU
                );

                if (!open_cfw_tlsf_wasm_is_aligned(allocation, alignment)) {
                    return open_cfw_tlsf_wasm_stress_failure(iteration, 1U);
                }
                if (open_cfw_tlsf_block_size(allocation) < requested) {
                    return open_cfw_tlsf_wasm_stress_failure(iteration, 2U);
                }
                open_cfw_tlsf_wasm_fill(allocation, requested, pattern);
                open_cfw_tlsf_wasm_stress_allocations[slot] = allocation;
                open_cfw_tlsf_wasm_stress_sizes[slot] = requested;
                open_cfw_tlsf_wasm_stress_patterns[slot] = pattern;
            }
        } else {
            unsigned int old_size =
                open_cfw_tlsf_wasm_stress_sizes[slot];
            unsigned char old_pattern =
                open_cfw_tlsf_wasm_stress_patterns[slot];

            if (
                !open_cfw_tlsf_wasm_verify(
                    allocation,
                    old_size,
                    old_pattern
                )
            ) {
                return open_cfw_tlsf_wasm_stress_failure(iteration, 3U);
            }

            if ((open_cfw_tlsf_wasm_next(&state) & 3U) == 0U) {
                open_cfw_tlsf_free(tlsf, allocation);
                open_cfw_tlsf_wasm_stress_allocations[slot] = (void *)0;
                open_cfw_tlsf_wasm_stress_sizes[slot] = 0U;
            } else {
                unsigned int requested =
                    open_cfw_tlsf_wasm_next(&state) % 3072U + 1U;
                void *resized = open_cfw_tlsf_realloc(
                    tlsf,
                    allocation,
                    requested
                );

                if (resized == (void *)0) {
                    if (
                        !open_cfw_tlsf_wasm_verify(
                            allocation,
                            old_size,
                            old_pattern
                        )
                    ) {
                        return open_cfw_tlsf_wasm_stress_failure(
                            iteration,
                            4U
                        );
                    }
                } else {
                    unsigned int preserved =
                        old_size < requested ? old_size : requested;
                    unsigned char pattern = (unsigned char)(
                        open_cfw_tlsf_wasm_next(&state) & 0xFFU
                    );

                    if (
                        !open_cfw_tlsf_wasm_verify(
                            resized,
                            preserved,
                            old_pattern
                        )
                    ) {
                        return open_cfw_tlsf_wasm_stress_failure(
                            iteration,
                            5U
                        );
                    }
                    if (open_cfw_tlsf_block_size(resized) < requested) {
                        return open_cfw_tlsf_wasm_stress_failure(
                            iteration,
                            6U
                        );
                    }
                    open_cfw_tlsf_wasm_fill(resized, requested, pattern);
                    open_cfw_tlsf_wasm_stress_allocations[slot] = resized;
                    open_cfw_tlsf_wasm_stress_sizes[slot] = requested;
                    open_cfw_tlsf_wasm_stress_patterns[slot] = pattern;
                }
            }
        }

        if ((iteration % 37U) == 0U) {
            if (open_cfw_tlsf_check(tlsf) != 0) {
                return open_cfw_tlsf_wasm_stress_failure(iteration, 7U);
            }
            if (open_cfw_tlsf_check_pool(pool) != 0) {
                return open_cfw_tlsf_wasm_stress_failure(iteration, 8U);
            }
        }
    }

    for (index = 0U; index < OPEN_CFW_TLSF_WASM_STRESS_SLOTS; ++index) {
        void *allocation =
            open_cfw_tlsf_wasm_stress_allocations[index];

        if (allocation != (void *)0) {
            if (
                !open_cfw_tlsf_wasm_verify(
                    allocation,
                    open_cfw_tlsf_wasm_stress_sizes[index],
                    open_cfw_tlsf_wasm_stress_patterns[index]
                )
            ) {
                return 81U;
            }
            open_cfw_tlsf_free(tlsf, allocation);
        }
    }
    if (open_cfw_tlsf_check(tlsf) != 0) {
        return 82U;
    }
    if (open_cfw_tlsf_check_pool(pool) != 0) {
        return 83U;
    }
    return 0U;
}

__attribute__((visibility("default")))
unsigned int open_cfw_tlsf_wasm_run(void)
{
    unsigned int status;

    status = open_cfw_tlsf_wasm_check_constants();
    if (status != 0U) {
        return status;
    }
    status = open_cfw_tlsf_wasm_check_basic();
    if (status != 0U) {
        return status;
    }
    status = open_cfw_tlsf_wasm_check_coalescing();
    if (status != 0U) {
        return status;
    }
    status = open_cfw_tlsf_wasm_check_exhaustion();
    if (status != 0U) {
        return status;
    }
    return open_cfw_tlsf_wasm_check_stress();
}
