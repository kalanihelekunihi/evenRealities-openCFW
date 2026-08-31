/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_LVGL_AMBIQ_NEMA_BUFFER_HELPERS_HOST_CONFIG_H
#define OPEN_CFW_LVGL_AMBIQ_NEMA_BUFFER_HELPERS_HOST_CONFIG_H

#include <stdint.h>

struct test_nema_heap_prefix {
    uint32_t private_words[4];
    uint32_t arena_size;
    uint32_t arena_start;
    uint8_t cacheable;
};

extern struct test_nema_heap_prefix test_nema_render_heap;
extern struct test_nema_heap_prefix test_nema_assets_heap;
extern struct test_nema_heap_prefix test_nema_cpu_heap;

#define OPEN_CFW_G2_NEMA_RENDER_HEAP_ADDRESS ((uintptr_t)&test_nema_render_heap)
#define OPEN_CFW_G2_NEMA_ASSETS_HEAP_ADDRESS ((uintptr_t)&test_nema_assets_heap)
#define OPEN_CFW_G2_NEMA_CPU_HEAP_ADDRESS ((uintptr_t)&test_nema_cpu_heap)

#endif
