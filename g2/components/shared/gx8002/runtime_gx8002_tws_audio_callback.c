/* SPDX-License-Identifier: MIT */
/* Adapted from NationalChip _LvpAudioInRecordCallback, lvp/lvp_mode_tws.c
 * at 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5. Copyright (C) 2001-2020
 * NationalChip Co., Ltd. See NATIONALCHIP-TWS-NOTICE.txt.
 * Stock differences: accepts index zero, no index subtraction, mic-frame
 * helper loop, noise judgement and standby enabled. Not yet qualified. */
#include <lvp_context.h>
extern int LvpGetContext(unsigned,LVP_CONTEXT **,unsigned *);
extern short *LvpGetMicFrame(LVP_CONTEXT *,unsigned,unsigned);
extern void *LvpGetContextHeader(void);
#include <lvp_queue.h>
#include <lvp_app_core.h>
extern int LvpAudioInGetDelayedFFTVad(void);
extern int LvpAuidoInQueryEnvNoise(LVP_CONTEXT *);
extern void open_cfw_gx8002_tws_standby_loop(void);
extern int LvpKwsRun(LVP_CONTEXT *);
extern int printf(const char *,...);
extern const char open_cfw_gx8002_tws_audio_message[];
extern struct {
    LVP_QUEUE queue;
    unsigned char buffer[56];
    unsigned state,countdown,last_vad;
} open_cfw_gx8002_tws_audio_state;
int open_cfw_gx8002_tws_audio_callback(int index,void *private_data)
{
    (void)private_data;
    if (index>=0) {
        LVP_CONTEXT *context;unsigned size;
        LvpGetContext((unsigned)index,&context,&size);
        context->ctx_index=(unsigned)index;
        context->G_vad=0;
        int vad=LvpAudioInGetDelayedFFTVad();
        LVP_CONTEXT_HEADER *header=context->ctx_header;
        for (unsigned mic=0;mic<header->mic_num;++mic)
            LvpGetMicFrame(context,mic,0);
        LvpAuidoInQueryEnvNoise(context);
        if (context->ctx_header->fft_vad_en) {
            header=(LVP_CONTEXT_HEADER *)LvpGetContextHeader();
            context->fft_vad=context->ctx_index<=header->logfbank_frame_num_per_channel/header->pcm_frame_num_per_context ? 1 : vad;
        } else context->fft_vad=1;
        open_cfw_gx8002_tws_standby_loop();
        if (context->fft_vad) {
            open_cfw_gx8002_tws_audio_state.state=2;
            open_cfw_gx8002_tws_audio_state.countdown=50;
        }
        LvpKwsRun(context);
        unsigned report_interval=15;
        __asm__("" : "+r"(report_interval)); /* Retain compact hardware division. */
        if (context->ctx_index%report_interval==0 || open_cfw_gx8002_tws_audio_state.last_vad!=context->fft_vad) {
            printf(open_cfw_gx8002_tws_audio_message,context->ctx_index,context->fft_vad,context->env_noise,0);
            if (open_cfw_gx8002_tws_audio_state.last_vad!=context->fft_vad)
                open_cfw_gx8002_tws_audio_state.last_vad=context->fft_vad;
        }
        APP_EVENT event={.event_id=91,.ctx_index=context->ctx_index};
        LvpTriggerAppEvent(&event);
    }
    return 0;
}
