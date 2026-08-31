/* SPDX-License-Identifier: MIT */
/*
 * Copyright (c) 2025 LVGL Kft
 *
 * Bounded LVGL 9.3 heap and array compatibility provider for the retained
 * Ambiq draw objects.  Valid-input behavior follows LVGL commit
 * 344c7c318047b7348e1be8572a9fd4260c251cfa.  The custom allocator boundary
 * is the already source-owned, synchronized G2 heap facade; malformed array
 * state and arithmetic overflow fail without mutating the descriptor.
 */

#include "lvgl_ambiq_lvgl_heap_array_provider.h"

#include <stdint.h>

typedef void * (*open_cfw_lvgl_heap_allocate_fn)(unsigned int size);
typedef void (*open_cfw_lvgl_heap_free_fn)(void * allocation);
typedef void * (*open_cfw_lvgl_heap_reallocate_fn)(void * allocation,
                                                    unsigned int size);

#ifndef OPEN_CFW_LVGL_HEAP_ALLOCATE
#define OPEN_CFW_LVGL_HEAP_ALLOCATE(size) \
    (((open_cfw_lvgl_heap_allocate_fn)0x00474CD3U)((unsigned int)(size)))
#endif

#ifndef OPEN_CFW_LVGL_HEAP_FREE
#define OPEN_CFW_LVGL_HEAP_FREE(allocation) \
    (((open_cfw_lvgl_heap_free_fn)0x00474D17U)((allocation)))
#endif

#ifndef OPEN_CFW_LVGL_HEAP_REALLOCATE
#define OPEN_CFW_LVGL_HEAP_REALLOCATE(allocation, size) \
    (((open_cfw_lvgl_heap_reallocate_fn)0x00474D55U)( \
        (allocation), (unsigned int)(size)))
#endif

/* LVGL's zero-size allocation is a stable, non-heap byte. */
static uint8_t zero_mem;

static void byte_copy(uint8_t * destination, const uint8_t * source,
                      uint32_t byte_count)
{
    uint32_t index;

    for(index = 0U; index < byte_count; ++index) destination[index] = source[index];
}

static void byte_zero(uint8_t * destination, uint32_t byte_count)
{
    uint32_t index;

    for(index = 0U; index < byte_count; ++index) destination[index] = 0U;
}

void * lv_malloc(size_t size)
{
    if(size == 0U) return &zero_mem;
    if(size > UINT32_MAX) return NULL;
    return OPEN_CFW_LVGL_HEAP_ALLOCATE(size);
}

void * lv_malloc_zeroed(size_t size)
{
    uint8_t * allocation;

    if(size == 0U) return &zero_mem;
    if(size > UINT32_MAX) return NULL;
    allocation = (uint8_t *)OPEN_CFW_LVGL_HEAP_ALLOCATE(size);
    if(allocation != NULL) byte_zero(allocation, (uint32_t)size);
    return allocation;
}

void lv_free(void * data)
{
    if(data == NULL || data == &zero_mem) return;
    OPEN_CFW_LVGL_HEAP_FREE(data);
}

void lv_array_deinit(lv_array_t * array)
{
    if(array == NULL) return;
    if(array->data != NULL) {
        if(array->inner_alloc) lv_free(array->data);
        array->data = NULL;
    }
    array->size = 0U;
    array->capacity = 0U;
}

lv_result_t lv_array_push_back(lv_array_t * array, const void * element)
{
    uint32_t offset;
    uint32_t allocation_size;
    uintptr_t data_address;
    uintptr_t element_address;
    uint8_t * destination;

    if(array == NULL || array->data == NULL || array->element_size == 0U ||
       array->size > array->capacity) {
        return LV_RESULT_INVALID;
    }
    if(array->element_size != 0U &&
       array->size > UINT32_MAX / array->element_size) {
        return LV_RESULT_INVALID;
    }
    offset = array->size * array->element_size;
    data_address = (uintptr_t)array->data;
    if(data_address > UINTPTR_MAX - offset ||
       data_address + offset > UINTPTR_MAX - array->element_size) {
        return LV_RESULT_INVALID;
    }

    /* LVGL specifies memcpy semantics: reject an overlapping source. */
    if(element != NULL && array->element_size != 0U) {
        element_address = (uintptr_t)element;
        if(element_address > UINTPTR_MAX - array->element_size) {
            return LV_RESULT_INVALID;
        }
        if(element_address < data_address + offset + array->element_size &&
           element_address + array->element_size > data_address + offset) {
            return LV_RESULT_INVALID;
        }
    }

    if(array->size == array->capacity) {
        uint32_t new_capacity;
        uint8_t * resized;

        if(!array->inner_alloc || array->capacity > UINT32_MAX - LV_ARRAY_DEFAULT_CAPACITY) {
            return LV_RESULT_INVALID;
        }
        new_capacity = array->capacity + LV_ARRAY_DEFAULT_CAPACITY;
        if(array->element_size != 0U &&
           new_capacity > UINT32_MAX / array->element_size) {
            return LV_RESULT_INVALID;
        }
        allocation_size = new_capacity * array->element_size;

        /* A source inside the old allocation could be invalidated by realloc. */
        if(element != NULL && array->element_size != 0U) {
            uint32_t old_size = array->capacity * array->element_size;
            element_address = (uintptr_t)element;
            if(element_address >= data_address &&
               element_address - data_address < old_size) {
                return LV_RESULT_INVALID;
            }
        }
        resized = (uint8_t *)OPEN_CFW_LVGL_HEAP_REALLOCATE(
            array->data, allocation_size);
        if(resized == NULL) return LV_RESULT_INVALID;
        array->data = resized;
        array->capacity = new_capacity;
        data_address = (uintptr_t)resized;
        if(data_address > UINTPTR_MAX - offset ||
           data_address + offset > UINTPTR_MAX - array->element_size) {
            return LV_RESULT_INVALID;
        }
    }

    destination = (uint8_t *)(data_address + offset);
    if(element != NULL) {
        byte_copy(destination, (const uint8_t *)element, array->element_size);
    }
    else {
        byte_zero(destination, array->element_size);
    }
    array->size++;
    return LV_RESULT_OK;
}
