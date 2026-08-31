/* SPDX-License-Identifier: MIT */

#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#if OPEN_CFW_SW_MASK_REFERENCE
#include "src/core/lv_global.h"
lv_global_t lv_global;
#else
#include "src/draw/ambiq/lvgl_ambiq_sw_mask_compat.h"
#endif

union allocation_header {
    max_align_t alignment;
    struct {
        size_t size;
        uint32_t magic;
    } fields;
};

#define ALLOCATION_MAGIC UINT32_C(0x4d41534b)
#if defined(__GNUC__)
#define HOST_EXPORT __attribute__((visibility("default")))
#else
#define HOST_EXPORT
#endif

static size_t allocation_attempts;
static size_t allocations_live;
static size_t bytes_live;
static size_t peak_bytes;
static size_t fail_at_attempt = SIZE_MAX;

static void * host_allocate(size_t size, int clear)
{
    union allocation_header * header;
    if(allocation_attempts++ == fail_at_attempt) return NULL;
    if(size > SIZE_MAX - sizeof(*header)) return NULL;
    header = clear ? calloc(1, sizeof(*header) + size) :
                     malloc(sizeof(*header) + size);
    if(header == NULL) return NULL;
    header->fields.size = size;
    header->fields.magic = ALLOCATION_MAGIC;
    allocations_live++;
    bytes_live += size;
    if(bytes_live > peak_bytes) peak_bytes = bytes_live;
    return header + 1;
}

void * lv_malloc(size_t size)
{
    return host_allocate(size, 0);
}

void * lv_malloc_zeroed(size_t size)
{
    return host_allocate(size, 1);
}

void lv_free(void * pointer)
{
    union allocation_header * header;
    if(pointer == NULL) return;
    header = (union allocation_header *)pointer - 1;
    if(header->fields.magic != ALLOCATION_MAGIC) abort();
    header->fields.magic = 0;
    allocations_live--;
    bytes_live -= header->fields.size;
    free(header);
}

void lv_memset(void * destination, uint8_t value, size_t length)
{
    (void)memset(destination, value, length);
}

void * lv_memcpy(void * destination, const void * source, size_t length)
{
    return memcpy(destination, source, length);
}

void * lv_memmove(void * destination, const void * source, size_t length)
{
    return memmove(destination, source, length);
}

int lv_memcmp(const void * left, const void * right, size_t length)
{
    return memcmp(left, right, length);
}

int32_t lv_area_get_width(const lv_area_t * area)
{
    return area->x2 - area->x1 + 1;
}

int32_t lv_area_get_height(const lv_area_t * area)
{
    return area->y2 - area->y1 + 1;
}

HOST_EXPORT void open_cfw_test_mask_allocator_reset(size_t fail_at)
{
    allocation_attempts = 0;
    peak_bytes = bytes_live;
    fail_at_attempt = fail_at;
}

HOST_EXPORT size_t open_cfw_test_mask_allocation_attempts(void)
{
    return allocation_attempts;
}

HOST_EXPORT size_t open_cfw_test_mask_allocations_live(void)
{
    return allocations_live;
}

HOST_EXPORT size_t open_cfw_test_mask_bytes_live(void)
{
    return bytes_live;
}

HOST_EXPORT size_t open_cfw_test_mask_peak_bytes(void)
{
    return peak_bytes;
}

HOST_EXPORT int open_cfw_test_mask_render(int32_t x1, int32_t y1,
                              int32_t x2, int32_t y2,
                              int32_t radius, int inverse,
                              int32_t line_x, int32_t line_y,
                              int32_t length, uint8_t seed,
                              uint8_t * output)
{
    lv_area_t rectangle = {x1, y1, x2, y2};
    lv_draw_sw_mask_radius_param_t parameter;
    lv_draw_sw_mask_res_t result;

    if(length > 0 && output != NULL) memset(output, seed, (size_t)length);
    memset(&parameter, 0xa5, sizeof(parameter));
    lv_draw_sw_mask_radius_init(&parameter, &rectangle, radius, inverse != 0);
    if(parameter.dsc.cb == NULL) return -1;
    result = parameter.dsc.cb(output, line_x, line_y, length, &parameter);
    lv_draw_sw_mask_free_param(&parameter);
#if OPEN_CFW_SW_MASK_REFERENCE
    lv_draw_sw_mask_cleanup();
    memset(&lv_global, 0, sizeof(lv_global));
#endif
    return (int)result;
}

HOST_EXPORT int open_cfw_test_mask_null_and_double_free(void)
{
    lv_area_t rectangle = {0, 0, 7, 7};
    lv_draw_sw_mask_radius_param_t parameter;
    lv_draw_sw_mask_common_dsc_t not_radius;

    lv_draw_sw_mask_radius_init(NULL, &rectangle, 4, false);
    lv_draw_sw_mask_radius_init(&parameter, NULL, 4, false);
    lv_draw_sw_mask_free_param(NULL);
    lv_draw_sw_mask_free_param(&parameter);
    lv_draw_sw_mask_free_param(&parameter);
    memset(&not_radius, 0, sizeof(not_radius));
    not_radius.type = LV_DRAW_SW_MASK_TYPE_LINE;
    lv_draw_sw_mask_free_param(&not_radius);
    return allocations_live == 0 ? 0 : -1;
}
