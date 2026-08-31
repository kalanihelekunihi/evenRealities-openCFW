/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_nema_buffer_helpers_host_config.h"
#include "../../third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_nema_buffer_helpers.h"

#include <stddef.h>
#include <stdint.h>

#include "am_hal_cachectrl.h"

struct test_nema_heap_prefix test_nema_render_heap;
struct test_nema_heap_prefix test_nema_assets_heap;
struct test_nema_heap_prefix test_nema_cpu_heap;

static uint32_t invalidate_calls;
static am_hal_cachectrl_range_t last_range;
static bool last_clean;

uint32_t am_hal_cachectrl_dcache_invalidate(am_hal_cachectrl_range_t *range, bool clean)
{
    ++invalidate_calls;
    last_range = *range;
    last_clean = clean;
    return 0U;
}

void test_nema_helpers_reset(void)
{
    test_nema_render_heap = (struct test_nema_heap_prefix){{0U}, 0x1000U, 0x20010000U, 1U};
    test_nema_assets_heap = (struct test_nema_heap_prefix){{0U}, 0x2000U, 0x60000000U, 0U};
    test_nema_cpu_heap = (struct test_nema_heap_prefix){{0U}, 0x0800U, 0x20020000U, 1U};
    invalidate_calls = 0U;
    last_range = (am_hal_cachectrl_range_t){0U, 0U};
    last_clean = true;
}

void test_nema_helpers_set_heap(uint32_t index, uint32_t start, uint32_t size, uint32_t cacheable)
{
    struct test_nema_heap_prefix *heap = index == 1U ? &test_nema_assets_heap :
                                                index == 2U ? &test_nema_cpu_heap :
                                                              &test_nema_render_heap;
    heap->arena_start = start;
    heap->arena_size = size;
    heap->cacheable = cacheable != 0U;
}

uint32_t test_nema_helpers_within(int32_t pool, uint32_t start, uint32_t length)
{
    return nema_buffer_is_within_pool(pool, start, length) ? 1U : 0U;
}

void test_nema_helpers_invalidate(int32_t pool, uint32_t start, int32_t size)
{
    nema_buffer_t buffer = {
        .size = size,
        .fd = pool,
        .base_virt = (void *)(uintptr_t)start,
        .base_phys = (uintptr_t)start,
    };
    nema_buffer_invalidate(&buffer);
}

void test_nema_helpers_invalidate_null(void)
{
    nema_buffer_invalidate(NULL);
}

uint32_t test_nema_helpers_call_count(void) { return invalidate_calls; }
uint32_t test_nema_helpers_last_start(void) { return last_range.ui32StartAddr; }
uint32_t test_nema_helpers_last_size(void) { return last_range.ui32Size; }
uint32_t test_nema_helpers_last_clean(void) { return last_clean ? 1U : 0U; }
