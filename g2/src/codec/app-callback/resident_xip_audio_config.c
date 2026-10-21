/* SPDX-License-Identifier: MIT
 * Native XIP audio-input product configuration 0x10207234..0x10207391.
 * Board descriptor contents are an input from the selected board provider.
 */
#include <stdint.h>

extern void gx8002_xip_audio_board_initialize_10203024(void);
extern const uint32_t *gx8002_xip_audio_board_get_10203004(void);
extern void gx8002_xip_audio_input_sadc_10203e18(uint32_t);
extern void gx8002_xip_audio_input_pdm_10203e7c(uint32_t);
extern void gx8002_xip_audio_input_i2s_10203ec8(
    uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);
extern void gx8002_xip_audio_set_input_channel_10203f70(uint32_t, uint32_t, uint32_t);
extern void gx8002_xip_audio_pga_gain_102042d4(uint32_t);
extern void gx8002_xip_audio_set_i2s_clock_10204320(uint32_t);
extern void gx8002_xip_audio_set_i2sin_mode_10204330(uint32_t);
extern void gx8002_xip_audio_set_dc_enable_10204350(uint32_t, uint32_t);
extern void gx8002_xip_audio_set_rough_gain_102043ac(uint32_t, uint32_t);
extern void gx8002_xip_audio_set_evad_enable_102043fc(
    uint32_t, uint32_t, uint32_t, uint32_t);
extern void gx8002_xip_audio_set_evad_threshold_102044e0(
    uint32_t, uint32_t, uint32_t, uint32_t);
extern void gx8002_xip_audio_set_fftvad_enable_10204570(
    uint32_t, uint32_t, uint32_t);
extern uint32_t gx8002_xip_tws_frames_per_channel_10206f74(void);
extern void gx8002_xip_audio_input_output_10207070(uint32_t, uint32_t);

uint32_t gx8002_xip_audio_input_config_10207234(void)
{
    gx8002_xip_audio_board_initialize_10203024();
    const uint32_t *board = gx8002_xip_audio_board_get_10203004();
    const uint32_t channels = board[0];
    const uint8_t *bytes = (const uint8_t *)board;
    if ((channels & 1u) != 0u) {
        gx8002_xip_audio_set_dc_enable_10204350(1u, (bytes[5] >> 2u) & 1u);
        gx8002_xip_audio_set_evad_threshold_102044e0(
            1u, board[5], board[6], board[7]);
        gx8002_xip_audio_set_evad_enable_102043fc(
            1u, board[2], board[3], board[4]);
        gx8002_xip_audio_input_sadc_10203e18(board[0x17]);
        gx8002_xip_audio_pga_gain_102042d4(board[1] & 0x3fu);
        gx8002_xip_audio_set_rough_gain_102043ac(
            1u, (board[1] & 0x1ffu) >> 6u);
    }
    if ((channels & 2u) != 0u) {
        gx8002_xip_audio_set_dc_enable_10204350(2u, (bytes[0x21] >> 2u) & 1u);
        gx8002_xip_audio_set_evad_threshold_102044e0(
            2u, board[0xc], board[0xd], board[0xe]);
        gx8002_xip_audio_set_evad_enable_102043fc(
            2u, board[9], board[10], board[0xb]);
        gx8002_xip_audio_set_rough_gain_102043ac(
            2u, (board[8] & 0x1ffu) >> 6u);
        gx8002_xip_audio_input_pdm_10203e7c(board[0x18]);
        gx8002_xip_audio_set_input_channel_10203f70(2u, 0u, 1u);
    }
    if ((channels & 4u) != 0u) {
        gx8002_xip_audio_set_dc_enable_10204350(4u, (bytes[0x3d] >> 2u) & 1u);
        gx8002_xip_audio_set_evad_threshold_102044e0(
            4u, board[0x13], board[0x14], board[0x15]);
        gx8002_xip_audio_set_evad_enable_102043fc(
            4u, board[0x10], board[0x11], board[0x12]);
        gx8002_xip_audio_set_rough_gain_102043ac(
            4u, (board[0xf] & 0x1ffu) >> 6u);
        gx8002_xip_audio_set_i2s_clock_10204320(3u);
        gx8002_xip_audio_input_i2s_10203ec8(
            board[0x19], board[0x1a], board[0x1b],
            board[0x1c], board[0x1d], board[0x1e]);
        gx8002_xip_audio_set_input_channel_10203f70(4u, 1u, 0u);
        gx8002_xip_audio_set_i2sin_mode_10204330(0u);
    }
    const uint32_t output_mask = board[0x16];
    if ((output_mask & 1u) != 0u)
        gx8002_xip_audio_input_output_10207070(channels, 1u);
    if ((output_mask & 2u) != 0u)
        gx8002_xip_audio_input_output_10207070(channels, 2u);
    if ((output_mask & 4u) != 0u)
        gx8002_xip_audio_input_output_10207070(channels, 4u);
    if ((output_mask & 8u) != 0u)
        gx8002_xip_audio_input_output_10207070(channels, 8u);
    gx8002_xip_audio_set_fftvad_enable_10204570(
        1u, 0u, gx8002_xip_tws_frames_per_channel_10206f74());
    return 0u;
}
