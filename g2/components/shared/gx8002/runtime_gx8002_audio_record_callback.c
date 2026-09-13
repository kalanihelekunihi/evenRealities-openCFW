/* SPDX-License-Identifier: MIT */
/* Adapted from NationalChip _LvpAudioInRecordDefaultCallback,
 * lvp/common/lvp_audio_in.c at 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5.
 * Copyright (C) 2001-2020 NationalChip Co., Ltd.
 * See NATIONALCHIP-STREAM-NOTICE.txt. Stock enables hardware logfbank and
 * FFT VAD, with an invalid-VAD threshold of 25. Not yet admitted. */
#include <stdint.h>
#include <stddef.h>
#include <lvp_context.h>

typedef struct {
    unsigned pcm_read_index, pcm_write_index, start_ctx_index, delayed_fft_vad;
    unsigned last_fft_vad:4, standby_startup_flag:4, reserve:24;
} AUDIO_RECORD_CTRL;
AUDIO_RECORD_CTRL open_cfw_gx8002_audio_record_control __attribute__((section(".bss.audio_record_control")));
int (*open_cfw_gx8002_audio_record_handler)(int, void *) __attribute__((section(".bss.audio_record_handler")));
int open_cfw_gx8002_audio_record_invalid_vad __attribute__((section(".bss.audio_record_invalid_vad")));
extern int LvpAudioInQueryFFTVad(unsigned *);
extern LVP_CONTEXT_HEADER *LvpGetContextHeader(void);
extern int LvpGetLogfbankFrameNumPerChannel(void);
extern int LvpGetPcmFrameNumPerContext(void);
extern int LvpGetContextNum(void);
extern int LvpGetContextGap(void);
_Static_assert(sizeof(AUDIO_RECORD_CTRL)==20,"audio control ABI");
_Static_assert(offsetof(LVP_CONTEXT_HEADER,pcm_frame_num_per_context)==36,"frame count ABI");
_Static_assert(offsetof(LVP_CONTEXT_HEADER,logfbank_dim_per_frame)==108,"feature dimension ABI");

int open_cfw_gx8002_audio_record_callback(unsigned channel,unsigned *sdc_addr)
{
    AUDIO_RECORD_CTRL *ctrl=&open_cfw_gx8002_audio_record_control;
    if (channel & 4) {
        int vad=LvpAudioInQueryFFTVad(&sdc_addr[2]);
        ctrl->last_fft_vad=vad;
        LVP_CONTEXT_HEADER *header=LvpGetContextHeader();
        unsigned size=header->logfbank_dim_per_frame*header->pcm_frame_num_per_context*2;
        int index=sdc_addr[2]/size;
        int count=LvpGetLogfbankFrameNumPerChannel()/LvpGetPcmFrameNumPerContext();
        if (ctrl->standby_startup_flag) {
            ctrl->standby_startup_flag=0;
            ctrl->pcm_write_index=index+2;
            ctrl->pcm_read_index=index+2;
            ctrl->start_ctx_index=index;
            ctrl->last_fft_vad=1;
            ctrl->delayed_fft_vad=1;
        }
        while (ctrl->pcm_write_index%count!=(unsigned)index) {
            if (ctrl->pcm_write_index>(unsigned)LvpGetContextNum() &&
                ctrl->pcm_write_index-ctrl->pcm_read_index>=(unsigned)(LvpGetContextNum()-LvpGetContextGap()))
                break;
            if (vad || ctrl->pcm_write_index <= (unsigned)(LvpGetLogfbankFrameNumPerChannel()/LvpGetPcmFrameNumPerContext())) {
                ctrl->delayed_fft_vad=1;
                open_cfw_gx8002_audio_record_invalid_vad=0;
            } else {
                ++open_cfw_gx8002_audio_record_invalid_vad;
                ctrl->delayed_fft_vad=open_cfw_gx8002_audio_record_invalid_vad<25;
            }
            open_cfw_gx8002_audio_record_handler(ctrl->pcm_write_index,&sdc_addr[2]);
            ++ctrl->pcm_write_index;
        }
    }
    return 0;
}
