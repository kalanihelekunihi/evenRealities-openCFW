/* SPDX-License-Identifier: MIT */
/* Recovered board configuration callback using pinned SDK field types. */
#include <lvp_param.h>
extern int AudioInBoardInit(void);
extern LVP_AUDIO_IN_PARAM_CTRL *AudioInBoardGetParamCtrl(void);
extern void open_cfw_gx8002_audio_input_output(unsigned int, unsigned int);
extern int LvpGetLogfbankFrameNumPerChannel(void);
int open_cfw_gx8002_audio_input_config(void)
{
    AudioInBoardInit();
    LVP_AUDIO_IN_PARAM_CTRL *ctrl = AudioInBoardGetParamCtrl();
    unsigned int source = ctrl->input_source;
    if (source & 1) {
        gx_audio_in_set_dc_enable(1, ctrl->input_source_config[0].dc_enable);
        gx_audio_in_set_evad_threshold(1, ctrl->input_source_config[0].evad_threshold);
        gx_audio_in_set_evad_enable(1, ctrl->input_source_config[0].evad);
        gx_audio_in_set_input_sadc(ctrl->sadc);
        gx_audio_in_set_pga_gain(ctrl->input_source_config[0].pga_gain);
        gx_audio_in_set_rough_gain(1, ctrl->input_source_config[0].audio_in_gain);
    }
    if (source & 2) {
        gx_audio_in_set_dc_enable(2, ctrl->input_source_config[1].dc_enable);
        gx_audio_in_set_evad_threshold(2, ctrl->input_source_config[1].evad_threshold);
        gx_audio_in_set_evad_enable(2, ctrl->input_source_config[1].evad);
        gx_audio_in_set_rough_gain(2, ctrl->input_source_config[1].audio_in_gain);
        gx_audio_in_set_input_pdm(ctrl->pdm);
        gx_audio_in_set_input_channel(2, 0, 1);
    }
    if (source & 4) {
        gx_audio_in_set_dc_enable(4, ctrl->input_source_config[2].dc_enable);
        gx_audio_in_set_evad_threshold(4, ctrl->input_source_config[2].evad_threshold);
        gx_audio_in_set_evad_enable(4, ctrl->input_source_config[2].evad);
        gx_audio_in_set_rough_gain(4, ctrl->input_source_config[2].audio_in_gain);
        gx_audio_in_set_i2s_clock(3);
        gx_audio_in_set_input_i2s(ctrl->i2s_in);
        gx_audio_in_set_input_channel(4, 1, 0);
        gx_audio_in_set_i2sin_mode(0);
    }
    LVP_AUDIO_IN_CHANNEL outputs = ctrl->output_channel;
    if (outputs.pcm0) open_cfw_gx8002_audio_input_output(source, 1);
    if (outputs.pcm1) open_cfw_gx8002_audio_input_output(source, 2);
    if (outputs.logfbank) open_cfw_gx8002_audio_input_output(source, 4);
    if (outputs.i2s) open_cfw_gx8002_audio_input_output(source, 8);
    gx_audio_in_set_fftvad_enable(1, 0, LvpGetLogfbankFrameNumPerChannel());
    return 0;
}
