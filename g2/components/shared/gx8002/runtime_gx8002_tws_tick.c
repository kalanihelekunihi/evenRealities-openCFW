/* SPDX-License-Identifier: MIT */
/* Adapted from NationalChip _TwsModeTick in lvp/lvp_mode_tws.c,
 * commit 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5.
 * Copyright (C) 2001-2020 NationalChip Co., Ltd.
 * See NATIONALCHIP-TWS-NOTICE.txt. Recovered MAX decoder and standby config;
 * player, voiceprint, cascade, hybrid switching and idle control absent. */
#include <stddef.h>
#include <lvp_context.h>
#include <lvp_queue.h>
#include <lvp_app_core.h>
extern struct {
    LVP_QUEUE queue;
    unsigned char buffer[56];
    volatile int standby;
} open_cfw_gx8002_tws_tick_state;
_Static_assert(offsetof(__typeof__(open_cfw_gx8002_tws_tick_state),standby)==76,"standby ABI");
extern int LvpDoMaxDecoder(LVP_CONTEXT *);
extern int LvpAudioInUpdateReadIndex(int);
extern int LvpPmuSuspendIsLocked(void);
extern int LvpPmuSuspend(int);
typedef struct { unsigned module_id; LVP_CONTEXT *context; } TWS_MODULE_INFO;
_Static_assert(sizeof(TWS_MODULE_INFO)==8,"module ABI");
_Static_assert(sizeof(APP_EVENT)==8,"event ABI");
_Static_assert(offsetof(LVP_CONTEXT,ctx_index)==8,"context index ABI");
void open_cfw_gx8002_tws_tick(void)
{
    TWS_MODULE_INFO info={0};
    if (LvpQueueGet(&open_cfw_gx8002_tws_tick_state.queue,(unsigned char *)&info)) {
        if (info.module_id==256) {
            LvpDoMaxDecoder(info.context);
            LvpAudioInUpdateReadIndex(1);
        }
        if (info.context->kws) {
            APP_EVENT event={.event_id=info.context->kws,.ctx_index=info.context->ctx_index};
            LvpTriggerAppEvent(&event);
        }
    }
    if (open_cfw_gx8002_tws_tick_state.standby==4 && !LvpPmuSuspendIsLocked())
        LvpPmuSuspend(13);
}
