/* SPDX-License-Identifier: MIT */
#include "lvgl_ambiq_lvgl_draw_dispatch_provider.h"
#include "src/core/lv_global.h"
#include "src/osal/lv_os.h"

#include <assert.h>
#include <stddef.h>
#include <string.h>

lv_global_t lv_global;

static unsigned signal_calls;
static lv_thread_sync_t * observed_sync[2];

lv_result_t lv_thread_sync_signal(lv_thread_sync_t * sync)
{
    assert(signal_calls < 2U);
    observed_sync[signal_calls++] = sync;
    return signal_calls == 1U ? LV_RESULT_INVALID : LV_RESULT_OK;
}

int main(void)
{
    lv_thread_sync_t * expected;

    memset(&lv_global, 0xA5, sizeof(lv_global));
    expected = &lv_global.draw_info.sync;
    lv_draw_dispatch_request();

    assert(signal_calls == 2U);
    assert(observed_sync[0] == expected);
    assert(observed_sync[1] == expected);
    return 0;
}
