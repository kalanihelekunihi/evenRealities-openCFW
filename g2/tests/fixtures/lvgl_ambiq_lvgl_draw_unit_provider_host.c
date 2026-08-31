/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_draw_unit_provider.h"
#include "src/core/lv_global.h"

#include <assert.h>
#include <limits.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

lv_global_t lv_global;

static unsigned allocation_calls;
static size_t last_allocation_size;
static int fail_allocation;

void * lv_malloc_zeroed(size_t size)
{
    allocation_calls++;
    last_allocation_size = size;
    if(fail_allocation) return NULL;
    return calloc(1U, size);
}

static void assert_extension_zeroed(const lv_draw_unit_t * unit, size_t size)
{
    const uint8_t * bytes = (const uint8_t *)unit;
    for(size_t i = sizeof(*unit); i < size; i++) assert(bytes[i] == 0U);
}

int main(void)
{
    const size_t extended_size = sizeof(lv_draw_unit_t) + 37U;
    lv_draw_unit_t * first;
    lv_draw_unit_t * second;

    memset(&lv_global, 0, sizeof(lv_global));

    assert(lv_draw_create_unit(0U) == NULL);
    assert(lv_draw_create_unit(sizeof(lv_draw_unit_t) - 1U) == NULL);
    assert(allocation_calls == 0U);
    assert(lv_global.draw_info.unit_head == NULL);
    assert(lv_global.draw_info.unit_cnt == 0U);

    lv_global.draw_info.unit_cnt = (uint32_t)INT32_MAX;
    assert(lv_draw_create_unit(sizeof(lv_draw_unit_t)) == NULL);
    assert(allocation_calls == 0U);
    assert(lv_global.draw_info.unit_head == NULL);
    assert(lv_global.draw_info.unit_cnt == (uint32_t)INT32_MAX);
    lv_global.draw_info.unit_cnt = 0U;

    fail_allocation = 1;
    assert(lv_draw_create_unit(extended_size) == NULL);
    assert(allocation_calls == 1U && last_allocation_size == extended_size);
    assert(lv_global.draw_info.unit_head == NULL);
    assert(lv_global.draw_info.unit_cnt == 0U);
    fail_allocation = 0;

    first = lv_draw_create_unit(extended_size);
    assert(first != NULL);
    assert(first->next == NULL);
    assert(first->name == NULL);
    assert(first->idx == 1);
    assert(first->dispatch_cb == NULL);
    assert(first->evaluate_cb == NULL);
    assert(first->wait_for_finish_cb == NULL);
    assert(first->delete_cb == NULL);
    assert_extension_zeroed(first, extended_size);
    assert(lv_global.draw_info.unit_head == first);
    assert(lv_global.draw_info.unit_cnt == 1U);

    second = lv_draw_create_unit(sizeof(lv_draw_unit_t));
    assert(second != NULL);
    assert(second->next == first);
    assert(second->idx == 2);
    assert(lv_global.draw_info.unit_head == second);
    assert(lv_global.draw_info.unit_cnt == 2U);

    free(second);
    free(first);
    return 0;
}
