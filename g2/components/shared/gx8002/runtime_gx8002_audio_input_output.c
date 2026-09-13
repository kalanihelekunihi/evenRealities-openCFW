/* SPDX-License-Identifier: MIT */
/* Recovered configuration of _LvpAudioInSetOutput. */
#include <stddef.h>
#include <stdint.h>
#include <lvp_param.h>
extern void *open_cfw_gx8002_audio_input_buffer_addr(unsigned int);
extern unsigned int open_cfw_gx8002_audio_input_buffer_size(unsigned int);
extern LVP_AUDIO_IN_PARAM_CTRL *AudioInBoardGetParamCtrl(void);
extern int LvpGetPcmFrameSize(void);
_Static_assert(offsetof(LVP_AUDIO_IN_PARAM_CTRL, pcm0) == 124, "PCM0 ABI");
_Static_assert(offsetof(LVP_AUDIO_IN_PARAM_CTRL, pcm1) == 148, "PCM1 ABI");
_Static_assert(offsetof(LVP_AUDIO_IN_PARAM_CTRL, logfbank) == 172, "Logfbank ABI");
_Static_assert(offsetof(LVP_AUDIO_IN_PARAM_CTRL, i2s_out) == 192, "I2S ABI");
_Static_assert(offsetof(LVP_AUDIO_IN_PARAM_CTRL, spectrum) == 220, "Spectrum ABI");
void open_cfw_gx8002_audio_input_output(unsigned int source, unsigned int channel)
{
    uintptr_t buffer = (uintptr_t)open_cfw_gx8002_audio_input_buffer_addr(channel);
    unsigned int size = open_cfw_gx8002_audio_input_buffer_size(channel);
    LVP_AUDIO_IN_PARAM_CTRL *ctrl = AudioInBoardGetParamCtrl();
    unsigned int device = buffer & 0x0ffffff8u;
    if (channel == 1) {
        unsigned int track = ctrl->input_source_config[0].pcm_output_track;
        unsigned int per_channel = (source & 9) || !track ? size & ~127u : (size >> 8) << 7;
        unsigned int frames = source & 8 ? 1024 : 128;
        ctrl->pcm0.size = per_channel;
        ctrl->pcm0.left_buffer = device;
        if (source & 8) {
            ctrl->spectrum.buffer = device;
            ctrl->spectrum.size = size;
            ctrl->spectrum.frame_num = size >> 3;
            gx_audio_in_set_logfbank_enable(1, 1);
            gx_audio_in_set_output_spectrum(1, ctrl->spectrum);
        } else {
            ctrl->pcm0.right_buffer = track ? device + per_channel : 0;
            ctrl->pcm0.endian = 0;
        }
        ctrl->pcm0.frame_num = frames;
        gx_audio_in_set_output_pcm(1, ctrl->pcm0);
    } else if (channel == 2) {
        unsigned int track = ctrl->input_source_config[1].pcm_output_track;
        unsigned int per_channel = (source & 1) || !track ? size & ~127u : (size >> 8) << 7;
        int frames = LvpGetPcmFrameSize() / 64 * 64;
        ctrl->pcm1.size = per_channel;
        ctrl->pcm1.left_buffer = device;
        ctrl->pcm1.right_buffer = track ? device + per_channel : 0;
        ctrl->pcm1.endian = 0;
        ctrl->pcm1.frame_num = frames;
        gx_audio_in_set_output_pcm(2, ctrl->pcm1);
    } else if (channel == 4) {
        ctrl->logfbank.buffer = device;
        ctrl->logfbank.size = size;
        ctrl->logfbank.frame_num = 1;
        gx_audio_in_set_logfbank_enable(1, 1);
        gx_audio_in_set_output_logfbank(ctrl->logfbank);
    } else if (channel == 8) {
        gx_audio_in_set_output_i2s(ctrl->i2s_out);
        gx_audio_in_set_i2sout_mode(0);
    }
}
