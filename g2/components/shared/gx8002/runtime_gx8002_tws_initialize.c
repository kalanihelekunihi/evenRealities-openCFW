/* SPDX-License-Identifier: MIT */
/* Adapted from NationalChip lvp_kws lvp/lvp_mode_tws.c at
 * 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5.
 * Copyright (C) 2001-2020 NationalChip Co., Ltd
 * See NATIONALCHIP-TWS-NOTICE.txt. Recovered MAX decoder and standby configuration. */
#include <lvp_mode.h>
#include <common/lvp_queue.h>
#include <driver/gx_snpu.h>
#include <stddef.h>
#include <tws-upstream-interfaces.h>
extern void LvpInitMaxKws(void);
extern int open_cfw_gx8002_tws_snpu_callback(int, GX_SNPU_STATE, void *);
extern int open_cfw_gx8002_tws_audio_callback(int, void *);
extern int printf(const char *, ...);
extern const char open_cfw_gx8002_tws_init_error[];
extern struct {
    LVP_QUEUE queue;
    unsigned char buffer[56];
    volatile int standby_state;
    volatile int countdown;
} open_cfw_gx8002_tws_state;
_Static_assert(sizeof(LVP_QUEUE) == 20, "queue size");
_Static_assert(offsetof(__typeof__(open_cfw_gx8002_tws_state), standby_state) == 76, "standby offset");
_Static_assert(offsetof(__typeof__(open_cfw_gx8002_tws_state), countdown) == 80, "countdown offset");
int open_cfw_gx8002_tws_init(LVP_MODE_TYPE previous)
{
    LvpQueueInit(&open_cfw_gx8002_tws_state.queue,
                 open_cfw_gx8002_tws_state.buffer, 56, 8);
    LvpInitMaxKws();
    GX_WAKEUP_SOURCE start = gx_pmu_get_wakeup_source();
    LvpKwsInit(open_cfw_gx8002_tws_snpu_callback, start);
    if (previous != LVP_MODE_INIT_FLAG || start < 2) {
        if (LvpAudioInInit(open_cfw_gx8002_tws_audio_callback)) {
            printf(open_cfw_gx8002_tws_init_error);
            return -1;
        }
    } else {
        LvpAudioInStandbyToStartup();
    }
    open_cfw_gx8002_tws_state.standby_state = 2;
    open_cfw_gx8002_tws_state.countdown = 50;
    return 0;
}
