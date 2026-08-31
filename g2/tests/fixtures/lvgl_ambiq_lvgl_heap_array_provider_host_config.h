/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_LVGL_HEAP_ARRAY_HOST_CONFIG_H
#define OPEN_CFW_LVGL_HEAP_ARRAY_HOST_CONFIG_H

#include <stddef.h>

void * open_cfw_heap_array_test_allocate(size_t size);
void open_cfw_heap_array_test_free(void * allocation);
void * open_cfw_heap_array_test_reallocate(void * allocation, size_t size);

#define OPEN_CFW_LVGL_HEAP_ALLOCATE(size) \
    open_cfw_heap_array_test_allocate((size))
#define OPEN_CFW_LVGL_HEAP_FREE(allocation) \
    open_cfw_heap_array_test_free((allocation))
#define OPEN_CFW_LVGL_HEAP_REALLOCATE(allocation, size) \
    open_cfw_heap_array_test_reallocate((allocation), (size))

#endif
