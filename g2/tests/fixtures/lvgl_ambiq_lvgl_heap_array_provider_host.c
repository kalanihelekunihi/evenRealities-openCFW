/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_heap_array_provider.h"

#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

static unsigned allocate_calls;
static unsigned free_calls;
static unsigned reallocate_calls;
static int fail_reallocate;

void * open_cfw_heap_array_test_allocate(size_t size)
{
    allocate_calls++;
    return malloc(size);
}

void open_cfw_heap_array_test_free(void * allocation)
{
    free_calls++;
    free(allocation);
}

void * open_cfw_heap_array_test_reallocate(void * allocation, size_t size)
{
    reallocate_calls++;
    if(fail_reallocate) return NULL;
    return realloc(allocation, size);
}

int main(void)
{
    uint8_t * zero_a = lv_malloc(0U);
    uint8_t * zero_b = lv_malloc_zeroed(0U);
    uint8_t * bytes;
    uint32_t initial[4] = {1U, 2U, 3U, 4U};
    uint32_t next = 5U;
    lv_array_t array = {
        .data = (uint8_t *)initial, .size = 3U, .capacity = 4U,
        .element_size = sizeof(uint32_t), .inner_alloc = false,
    };

    assert(zero_a == zero_b);
    assert(allocate_calls == 0U);
    lv_free(NULL);
    lv_free(zero_a);
    assert(free_calls == 0U);

    bytes = lv_malloc_zeroed(17U);
    assert(bytes != NULL && allocate_calls == 1U);
    for(unsigned i = 0; i < 17U; ++i) assert(bytes[i] == 0U);
    lv_free(bytes);
    assert(free_calls == 1U);

    assert(lv_array_push_back(&array, &next) == LV_RESULT_OK);
    assert(array.size == 4U && initial[3] == 5U);
    assert(lv_array_push_back(&array, &next) == LV_RESULT_INVALID);
    assert(reallocate_calls == 0U);

    array.data = malloc(4U * sizeof(uint32_t));
    assert(array.data != NULL);
    memcpy(array.data, initial, 4U * sizeof(uint32_t));
    array.inner_alloc = true;
    fail_reallocate = 1;
    assert(lv_array_push_back(&array, &next) == LV_RESULT_INVALID);
    assert(array.size == 4U && array.capacity == 4U);
    fail_reallocate = 0;
    assert(lv_array_push_back(&array, &next) == LV_RESULT_OK);
    assert(array.size == 5U && array.capacity == 8U);
    assert(((uint32_t *)array.data)[4] == 5U);
    assert(lv_array_push_back(&array, NULL) == LV_RESULT_OK);
    assert(((uint32_t *)array.data)[5] == 0U);

    /* Source aliasing a full allocation is rejected before realloc. */
    array.size = array.capacity;
    assert(lv_array_push_back(&array, array.data) == LV_RESULT_INVALID);

    array.size = UINT32_MAX;
    array.capacity = UINT32_MAX;
    array.element_size = UINT32_MAX;
    assert(lv_array_push_back(&array, &next) == LV_RESULT_INVALID);
    array.size = 6U;
    array.capacity = 8U;
    array.element_size = sizeof(uint32_t);
    lv_array_deinit(&array);
    assert(array.data == NULL && array.size == 0U && array.capacity == 0U);
    assert(free_calls == 2U);

    assert(lv_array_push_back(NULL, &next) == LV_RESULT_INVALID);
    array.data = (uint8_t *)initial;
    array.size = 0U;
    array.capacity = 1U;
    array.element_size = 0U;
    array.inner_alloc = false;
    assert(lv_array_push_back(&array, &next) == LV_RESULT_INVALID);
    lv_array_deinit(NULL);
    return 0;
}
