/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_nema_buffer_helpers.h"

#include <stddef.h>
#include <stdint.h>

#include "am_hal_cachectrl.h"

/*
 * The three descriptor addresses and prefix offsets are authenticated from
 * the official G2 2.2.6.10 Nema HAL.  A host test may replace only the
 * addresses by defining the macros below; the target defaults are fixed.
 */
#ifndef OPEN_CFW_G2_NEMA_RENDER_HEAP_ADDRESS
#define OPEN_CFW_G2_NEMA_RENDER_HEAP_ADDRESS UINT32_C(0x20000354)
#endif
#ifndef OPEN_CFW_G2_NEMA_ASSETS_HEAP_ADDRESS
#define OPEN_CFW_G2_NEMA_ASSETS_HEAP_ADDRESS UINT32_C(0x20000370)
#endif
#ifndef OPEN_CFW_G2_NEMA_CPU_HEAP_ADDRESS
#define OPEN_CFW_G2_NEMA_CPU_HEAP_ADDRESS UINT32_C(0x20000338)
#endif

enum {
    OPEN_CFW_NEMA_MEM_POOL_CL = 0,
    OPEN_CFW_NEMA_MEM_POOL_FB = 1,
    OPEN_CFW_NEMA_MEM_POOL_ASSETS = 2,
    OPEN_CFW_NEMA_MEM_POOL_CLIPPED_PATH = 3,
};

struct open_cfw_g2_nema_heap_prefix {
    uint32_t private_words[4];
    uint32_t arena_size;
    uint32_t arena_start;
    uint8_t cacheable;
};

_Static_assert(offsetof(struct open_cfw_g2_nema_heap_prefix, arena_size) == 0x10U,
               "G2 Nema heap size offset changed");
_Static_assert(offsetof(struct open_cfw_g2_nema_heap_prefix, arena_start) == 0x14U,
               "G2 Nema heap arena offset changed");
_Static_assert(offsetof(struct open_cfw_g2_nema_heap_prefix, cacheable) == 0x18U,
               "G2 Nema heap cache-policy offset changed");
#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(nema_buffer_t) == 16U, "Nema buffer ABI changed");
_Static_assert(offsetof(nema_buffer_t, size) == 0U, "Nema buffer size offset changed");
_Static_assert(offsetof(nema_buffer_t, fd) == 4U, "Nema buffer pool offset changed");
_Static_assert(offsetof(nema_buffer_t, base_virt) == 8U, "Nema buffer virtual offset changed");
_Static_assert(offsetof(nema_buffer_t, base_phys) == 12U, "Nema buffer physical offset changed");
#endif

static const volatile struct open_cfw_g2_nema_heap_prefix *select_heap(int pool)
{
    uintptr_t address;

    if(pool == OPEN_CFW_NEMA_MEM_POOL_ASSETS) {
        address = (uintptr_t)OPEN_CFW_G2_NEMA_ASSETS_HEAP_ADDRESS;
    }
    else if(pool == OPEN_CFW_NEMA_MEM_POOL_CLIPPED_PATH) {
        address = (uintptr_t)OPEN_CFW_G2_NEMA_CPU_HEAP_ADDRESS;
    }
    else {
        /* Stock maps CL, FB, and every other value to the render heap. */
        address = (uintptr_t)OPEN_CFW_G2_NEMA_RENDER_HEAP_ADDRESS;
    }

    return (const volatile struct open_cfw_g2_nema_heap_prefix *)address;
}

bool nema_buffer_is_within_pool(int pool, uint32_t start, uint32_t length)
{
    const volatile struct open_cfw_g2_nema_heap_prefix *heap = select_heap(pool);
    const uint32_t arena_start = heap->arena_start;
    const uint32_t arena_size = heap->arena_size;
    uint32_t offset;

    /* Reject wrapped descriptors and ranges instead of reproducing stock's
     * unsigned-add wraparound for hostile inputs.  Valid G2 ranges are exact. */
    if(arena_size > UINT32_MAX - arena_start || start < arena_start) {
        return false;
    }
    offset = start - arena_start;
    if(offset > arena_size) {
        return false;
    }
    return length <= arena_size - offset;
}

void nema_buffer_invalidate(nema_buffer_t *buffer)
{
    const volatile struct open_cfw_g2_nema_heap_prefix *heap;
    am_hal_cachectrl_range_t range;

    if(buffer == NULL || buffer->size < 0) {
        return;
    }
    heap = select_heap(buffer->fd);
    if(heap->cacheable == 0U) {
        return;
    }

    range.ui32StartAddr = (uint32_t)buffer->base_phys;
    range.ui32Size = (uint32_t)buffer->size;
    if(!nema_buffer_is_within_pool(buffer->fd, range.ui32StartAddr, range.ui32Size)) {
        return;
    }

    (void)am_hal_cachectrl_dcache_invalidate(&range, false);
}
