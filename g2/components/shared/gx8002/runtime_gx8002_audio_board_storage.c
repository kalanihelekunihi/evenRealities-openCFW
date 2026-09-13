/* SPDX-License-Identifier: MIT */
/* Recovered deployed settings expressed with the pinned NationalChip SDK types.
 * Buffers and frame counts begin at zero and are populated by initialization. */
#include <lvp_param.h>
LVP_AUDIO_IN_PARAM_CTRL open_cfw_audio_board_state = {
    .input_source = AUDIO_IN_PDM,
    .input_source_config = {
        { .pga_gain=24, .audio_in_gain=AUDIO_IN_GAIN_12dB, .dc_enable=1,
          .pcm_output_track=TRACK_MONO, .evad={.state_valid_enable=1} },
        { .pga_gain=24, .audio_in_gain=AUDIO_IN_GAIN_12dB, .dc_enable=1,
          .pcm_output_track=TRACK_STEREO, .evad={.state_valid_enable=1} },
        { .pga_gain=24, .audio_in_gain=AUDIO_IN_GAIN_12dB, .dc_enable=1,
          .pcm_output_track=TRACK_MONO, .evad={.state_valid_enable=1} },
    },
    .output_channel = {.pcm1=1, .logfbank=1},
    .sadc = {.pga_enable=1},
    .pdm = {.clk=AUDIO_IN_PDM_1M},
    .i2s_in = {
        .i2s = {.pcm_length=PCM_LENGTH_16BIT, .data_format=DATA_FORMAT_I2S,
                .clk_mode=CLK_MODE_MASTER, .bclk_sel=BCLK_MODE_64FS,
                .i2s_fs=SAMPLE_RATE_16K},
        .fsync_mode=FSYNC_MODE_SHORT,
    },
    .pcm0 = {.endian=ENDIAN_LITTLE_16BIT, .source=PCM_SOURCE_I2SIN},
    .pcm1 = {.endian=ENDIAN_LITTLE_16BIT, .source=PCM_SOURCE_PDM},
    .logfbank = {.endian=ENDIAN_LITTLE_16BIT, .source=LOGFBANK_SOURCE_PDM_LEFT},
    .i2s_out = {
        .i2s = {.pcm_length=PCM_LENGTH_16BIT, .data_format=DATA_FORMAT_I2S,
                .clk_mode=CLK_MODE_MASTER, .bclk_sel=BCLK_MODE_64FS,
                .i2s_fs=SAMPLE_RATE_16K},
        .left_source=I2S_SOURCE_PDM_LEFT, .right_source=I2S_SOURCE_PDM_RIGHT,
    },
    .spectrum = {.endian=ENDIAN_LITTLE_16BIT, .source=LOGFBANK_SOURCE_PDM_LEFT},
};
_Static_assert(sizeof(open_cfw_audio_board_state)==240, "Audio board state extent");
