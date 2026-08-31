/* SPDX-License-Identifier: MIT */
/*
 * Copyright (c) 2025 LVGL Kft
 *
 * Exact OS-enabled lv_draw_dispatch_request transcription from authenticated
 * LVGL commit 344c7c318047b7348e1be8572a9fd4260c251cfa.  LVGL intentionally
 * signals the shared draw condition twice so that both the draw thread and a
 * concurrently waiting renderer can observe a request.
 */

#include <stddef.h>
#include <stdint.h>

#include "lvgl_ambiq_lvgl_draw_dispatch_provider.h"
#include "src/core/lv_global.h"
#include "src/draw/lv_draw_private.h"
#include "src/osal/lv_os.h"

#if LV_USE_OS != LV_OS_FREERTOS
#error "G2 draw-dispatch admission requires the recovered FreeRTOS LVGL ABI"
#endif

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(offsetof(lv_draw_global_info_t, sync) == 12U,
               "G2 draw synchronization offset changed");
#endif

void lv_draw_dispatch_request(void)
{
    lv_thread_sync_t * sync = &LV_GLOBAL_DEFAULT()->draw_info.sync;

    (void)lv_thread_sync_signal(sync);
    (void)lv_thread_sync_signal(sync);
}
