/*
 * SPDX-License-Identifier: MIT
 *
 * Verification adapter for the source-owned TLSF integration.
 *
 * OPEN_CFW_TEST_TLSF_TARGET builds the exact firmware translation unit:
 * runtime_tlsf.c immediately followed by the byte-preserved vendored tlsf.c.
 * The default host build renames the same upstream API but intentionally does
 * not include runtime_tlsf.c because the native process has a 64-bit ABI.
 * Consequently, the native lane provides allocator semantic coverage only;
 * it is not evidence for, or proof of, the firmware's 32-bit ABI.
 */

#if defined(OPEN_CFW_TEST_TLSF_TARGET)

#include "../../components/apollo_main/core_overlay/runtime_tlsf.c"
#include "../../third_party/tlsf/tlsf.c"

/*
 * These assertions are evaluated by the ARM target compiler in the combined
 * translation unit. They complement runtime_tlsf.c's pointer, size_t, and
 * ptrdiff_t assertions with the recovered internal G2 configuration.
 */
_Static_assert(ALIGN_SIZE == 4, "G2 TLSF alignment changed");
_Static_assert(SL_INDEX_COUNT == 32, "G2 TLSF SL count changed");
_Static_assert(FL_INDEX_COUNT == 24, "G2 TLSF FL count changed");
_Static_assert(FL_INDEX_SHIFT == 7, "G2 TLSF FL shift changed");
_Static_assert(SMALL_BLOCK_SIZE == 128, "G2 small-block threshold changed");
_Static_assert(sizeof(block_header_t) == 16, "G2 block header changed");
_Static_assert(
    sizeof(block_header_t) - sizeof(block_header_t *) == 12,
    "G2 minimum block changed"
);
_Static_assert(
    (1U << FL_INDEX_MAX) == 0x40000000U,
    "G2 maximum block changed"
);
_Static_assert(sizeof(size_t) == 4, "G2 allocation overhead changed");
_Static_assert(sizeof(control_t) == 0xC74, "G2 TLSF control size changed");

/*
 * Type compatibility is checked in the same target translation unit as the
 * definitions, so a renamed symbol with a silently changed signature fails
 * compilation before it can enter an overlay.
 */
#define OPEN_CFW_TEST_TLSF_ASSERT_SIGNATURE(function, signature) \
    _Static_assert( \
        __builtin_types_compatible_p(__typeof__(&(function)), signature), \
        "public TLSF signature changed: " #function \
    )

typedef open_cfw_tlsf_t (*open_cfw_test_tlsf_create_fn)(void *);
typedef open_cfw_tlsf_t (*open_cfw_test_tlsf_create_with_pool_fn)(
    void *,
    size_t
);
typedef void (*open_cfw_test_tlsf_destroy_fn)(open_cfw_tlsf_t);
typedef open_cfw_tlsf_pool_t (*open_cfw_test_tlsf_get_pool_fn)(
    open_cfw_tlsf_t
);
typedef open_cfw_tlsf_pool_t (*open_cfw_test_tlsf_add_pool_fn)(
    open_cfw_tlsf_t,
    void *,
    size_t
);
typedef void (*open_cfw_test_tlsf_remove_pool_fn)(
    open_cfw_tlsf_t,
    open_cfw_tlsf_pool_t
);
typedef void *(*open_cfw_test_tlsf_malloc_fn)(open_cfw_tlsf_t, size_t);
typedef void *(*open_cfw_test_tlsf_memalign_fn)(
    open_cfw_tlsf_t,
    size_t,
    size_t
);
typedef void *(*open_cfw_test_tlsf_realloc_fn)(
    open_cfw_tlsf_t,
    void *,
    size_t
);
typedef void (*open_cfw_test_tlsf_free_fn)(open_cfw_tlsf_t, void *);
typedef size_t (*open_cfw_test_tlsf_block_size_fn)(void *);
typedef size_t (*open_cfw_test_tlsf_constant_fn)(void);
typedef void (*open_cfw_test_tlsf_walk_pool_fn)(
    open_cfw_tlsf_pool_t,
    open_cfw_tlsf_walker,
    void *
);
typedef int (*open_cfw_test_tlsf_check_fn)(open_cfw_tlsf_t);
typedef int (*open_cfw_test_tlsf_check_pool_fn)(open_cfw_tlsf_pool_t);

OPEN_CFW_TEST_TLSF_ASSERT_SIGNATURE(
    open_cfw_tlsf_create,
    open_cfw_test_tlsf_create_fn
);
OPEN_CFW_TEST_TLSF_ASSERT_SIGNATURE(
    open_cfw_tlsf_create_with_pool,
    open_cfw_test_tlsf_create_with_pool_fn
);
OPEN_CFW_TEST_TLSF_ASSERT_SIGNATURE(
    open_cfw_tlsf_destroy,
    open_cfw_test_tlsf_destroy_fn
);
OPEN_CFW_TEST_TLSF_ASSERT_SIGNATURE(
    open_cfw_tlsf_get_pool,
    open_cfw_test_tlsf_get_pool_fn
);
OPEN_CFW_TEST_TLSF_ASSERT_SIGNATURE(
    open_cfw_tlsf_add_pool,
    open_cfw_test_tlsf_add_pool_fn
);
OPEN_CFW_TEST_TLSF_ASSERT_SIGNATURE(
    open_cfw_tlsf_remove_pool,
    open_cfw_test_tlsf_remove_pool_fn
);
OPEN_CFW_TEST_TLSF_ASSERT_SIGNATURE(
    open_cfw_tlsf_malloc,
    open_cfw_test_tlsf_malloc_fn
);
OPEN_CFW_TEST_TLSF_ASSERT_SIGNATURE(
    open_cfw_tlsf_memalign,
    open_cfw_test_tlsf_memalign_fn
);
OPEN_CFW_TEST_TLSF_ASSERT_SIGNATURE(
    open_cfw_tlsf_realloc,
    open_cfw_test_tlsf_realloc_fn
);
OPEN_CFW_TEST_TLSF_ASSERT_SIGNATURE(
    open_cfw_tlsf_free,
    open_cfw_test_tlsf_free_fn
);
OPEN_CFW_TEST_TLSF_ASSERT_SIGNATURE(
    open_cfw_tlsf_block_size,
    open_cfw_test_tlsf_block_size_fn
);
OPEN_CFW_TEST_TLSF_ASSERT_SIGNATURE(
    open_cfw_tlsf_size,
    open_cfw_test_tlsf_constant_fn
);
OPEN_CFW_TEST_TLSF_ASSERT_SIGNATURE(
    open_cfw_tlsf_align_size,
    open_cfw_test_tlsf_constant_fn
);
OPEN_CFW_TEST_TLSF_ASSERT_SIGNATURE(
    open_cfw_tlsf_block_size_min,
    open_cfw_test_tlsf_constant_fn
);
OPEN_CFW_TEST_TLSF_ASSERT_SIGNATURE(
    open_cfw_tlsf_block_size_max,
    open_cfw_test_tlsf_constant_fn
);
OPEN_CFW_TEST_TLSF_ASSERT_SIGNATURE(
    open_cfw_tlsf_pool_overhead,
    open_cfw_test_tlsf_constant_fn
);
OPEN_CFW_TEST_TLSF_ASSERT_SIGNATURE(
    open_cfw_tlsf_alloc_overhead,
    open_cfw_test_tlsf_constant_fn
);
OPEN_CFW_TEST_TLSF_ASSERT_SIGNATURE(
    open_cfw_tlsf_walk_pool,
    open_cfw_test_tlsf_walk_pool_fn
);
OPEN_CFW_TEST_TLSF_ASSERT_SIGNATURE(
    open_cfw_tlsf_check,
    open_cfw_test_tlsf_check_fn
);
OPEN_CFW_TEST_TLSF_ASSERT_SIGNATURE(
    open_cfw_tlsf_check_pool,
    open_cfw_test_tlsf_check_pool_fn
);

#undef OPEN_CFW_TEST_TLSF_ASSERT_SIGNATURE

#else

/*
 * Apply the production public prefix without importing runtime_tlsf.c's
 * deliberately strict ILP32 assertions into this LP64 host-only lane.
 */
#define tlsf_t open_cfw_tlsf_t
#define pool_t open_cfw_tlsf_pool_t
#define tlsf_walker open_cfw_tlsf_walker
#define tlsf_create open_cfw_tlsf_create
#define tlsf_create_with_pool open_cfw_tlsf_create_with_pool
#define tlsf_destroy open_cfw_tlsf_destroy
#define tlsf_get_pool open_cfw_tlsf_get_pool
#define tlsf_add_pool open_cfw_tlsf_add_pool
#define tlsf_remove_pool open_cfw_tlsf_remove_pool
#define tlsf_malloc open_cfw_tlsf_malloc
#define tlsf_memalign open_cfw_tlsf_memalign
#define tlsf_realloc open_cfw_tlsf_realloc
#define tlsf_free open_cfw_tlsf_free
#define tlsf_block_size open_cfw_tlsf_block_size
#define tlsf_size open_cfw_tlsf_size
#define tlsf_align_size open_cfw_tlsf_align_size
#define tlsf_block_size_min open_cfw_tlsf_block_size_min
#define tlsf_block_size_max open_cfw_tlsf_block_size_max
#define tlsf_pool_overhead open_cfw_tlsf_pool_overhead
#define tlsf_alloc_overhead open_cfw_tlsf_alloc_overhead
#define tlsf_walk_pool open_cfw_tlsf_walk_pool
#define tlsf_check open_cfw_tlsf_check
#define tlsf_check_pool open_cfw_tlsf_check_pool

#include "../../third_party/tlsf/tlsf.c"

const char *open_cfw_test_tlsf_host_lane_label(void)
{
    return "semantic coverage only; not 32-bit ABI proof";
}

size_t open_cfw_test_tlsf_host_pointer_size(void)
{
    return sizeof(void *);
}

size_t open_cfw_test_tlsf_host_size_t_size(void)
{
    return sizeof(size_t);
}

size_t open_cfw_test_tlsf_host_ptrdiff_t_size(void)
{
    return sizeof(ptrdiff_t);
}

#endif
