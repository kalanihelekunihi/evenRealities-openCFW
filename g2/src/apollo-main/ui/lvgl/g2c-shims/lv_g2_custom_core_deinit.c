// SPDX-License-Identifier: MIT
/*
 * G2 compilable-C campaign: LVGL v9.3 custom-stdlib core and teardown hooks.
 *
 * Stock G2 2.2.6.10 builds LVGL with LV_USE_STDLIB_MALLOC == LV_STDLIB_CUSTOM;
 * lv_malloc_core/lv_free_core/lv_realloc_core alias the firmware pool
 * (audio_uart_lv_pool_*_4843xx). The stock image never tears LVGL down, so the
 * linker discarded lv_deinit and everything it alone reaches. Upstream
 * lv_init.c/lv_mem.c (compiled whole here) still reference the hooks below.
 * They are openCFW completions, not recovered stock bodies: the monitor
 * reports "unknown", the self-test passes, and teardown is a no-op because the
 * firmware's draw/decoder/span state lives for the life of the device.
 */
#include "lvgl.h"
#include "src/stdlib/lv_mem.h"

void lv_mem_init(void);

void lv_mem_deinit(void)
{
    /* The firmware pool is static and is never returned. */
}

void lv_mem_monitor_core(lv_mem_monitor_t * mon_p)
{
    lv_memzero(mon_p, sizeof(*mon_p));
}

lv_result_t lv_mem_test_core(void)
{
    return LV_RESULT_OK;
}

void lv_draw_deinit(void) {}
void lv_draw_sw_deinit(void) {}
void lv_image_decoder_deinit(void) {}
void lv_span_stack_deinit(void) {}
