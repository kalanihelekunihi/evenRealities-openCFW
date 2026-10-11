/* SPDX-License-Identifier: MIT
 * Native XIP 0x10207070..0x10207231. Control flow and record layout
 * correspond to pinned NationalChip lvp/common/lvp_audio_in.c
 * _LvpAudioInSetOutput; register/stack argument placement checked against
 * authenticated native disassembly. Board record remains runtime product
 * input. Output engine bodies are separate genuine lower contracts.
 */
#include <stdint.h>
#include "resident_xip_audio_output_types.h"

extern const uint32_t *gx8002_xip_audio_board_get_10203004(void);
extern uint32_t gx8002_xip_audio_input_buffer_addr_1020704c(uint32_t);
extern uint32_t gx8002_xip_audio_input_buffer_size_10207024(uint32_t);
extern uint32_t gx8002_xip_pcm_frame_size_10206f5c(void);
extern uint32_t gx8002_xip_audio_set_logfbank_enable_1020452c(uint32_t, uint32_t);
extern uint32_t gx8002_xip_audio_set_i2sout_mode_10204340(uint32_t);
extern int32_t gx8002_xip_audio_output_pcm_10203fa8(uint32_t, gx8002_pcm_output);
extern int32_t gx8002_xip_audio_output_logfbank_10204080(gx8002_logfbank_output);
extern int32_t gx8002_xip_audio_output_spectrum_1020412c(uint32_t, gx8002_spectrum_output);
extern int32_t gx8002_xip_audio_output_i2s_10204228(gx8002_i2s_output);

static gx8002_pcm_output pcm_record(volatile uint32_t *board, uint32_t offset)
{
    volatile uint32_t *p = board + offset / 4u;
    gx8002_pcm_output v = {p[0], p[1], p[2], p[3], p[4], p[5]};
    return v;
}

void gx8002_xip_audio_input_output_10207070(uint32_t source, uint32_t channel)
{
    uint32_t buffer = gx8002_xip_audio_input_buffer_addr_1020704c(channel);
    uint32_t size = gx8002_xip_audio_input_buffer_size_10207024(channel);
    volatile uint32_t *board = (volatile uint32_t *)(uintptr_t)
        gx8002_xip_audio_board_get_10203004();
    volatile uint8_t *bytes = (volatile uint8_t *)(void *)board;

    if (channel == 1u) {
        uint32_t stereo = (bytes[5] >> 3u) & 1u;
        uint32_t channel_size =
            ((source & 9u) == 0u && stereo != 0u)
            ? (size >> 8u) << 7u : size & ~UINT32_C(127);
        uint32_t left = buffer & ~UINT32_C(7);
        board[0x84u / 4u] = channel_size;
        board[0x7cu / 4u] = left;
        if ((source & 8u) == 0u) {
            board[0x80u / 4u] = stereo != 0u ? left + channel_size : 0u;
            board[0x8cu / 4u] = 0u;
        } else {
            board[0xe0u / 4u] = size;
            board[0xdcu / 4u] = left;
            board[0xe4u / 4u] = size >> 3u;
            (void)gx8002_xip_audio_set_logfbank_enable_1020452c(1u, 1u);
            gx8002_spectrum_output spectrum = {
                board[0xdcu / 4u], board[0xe0u / 4u], board[0xe4u / 4u],
                board[0xe8u / 4u], board[0xecu / 4u]
            };
            (void)gx8002_xip_audio_output_spectrum_1020412c(1u, spectrum);
        }
        board[0x88u / 4u] = (source & 8u) != 0u ? 0x400u : 0x80u;
        (void)gx8002_xip_audio_output_pcm_10203fa8(
            1u, pcm_record(board, 0x7cu));
        return;
    }
    if (channel == 2u) {
        uint32_t stereo = (bytes[0x21u] >> 3u) & 1u;
        uint32_t channel_size =
            ((source & 1u) == 0u && stereo != 0u)
            ? (size >> 8u) << 7u : size & ~UINT32_C(127);
        int32_t frame = (int32_t)gx8002_xip_pcm_frame_size_10206f5c();
        if (frame < 0) frame += 63;
        uint32_t left = buffer & ~UINT32_C(7);
        board[0x9cu / 4u] = channel_size;
        board[0xa4u / 4u] = 0u;
        board[0xa0u / 4u] = (uint32_t)frame & ~UINT32_C(63);
        board[0x94u / 4u] = left;
        board[0x98u / 4u] = stereo != 0u ? left + channel_size : 0u;
        (void)gx8002_xip_audio_output_pcm_10203fa8(
            2u, pcm_record(board, 0x94u));
        return;
    }
    if (channel == 4u) {
        board[0xacu / 4u] = buffer & ~UINT32_C(7);
        board[0xb0u / 4u] = size;
        board[0xb4u / 4u] = 1u;
        (void)gx8002_xip_audio_set_logfbank_enable_1020452c(1u, 1u);
        gx8002_logfbank_output logfbank = {
            board[0xacu / 4u], board[0xb0u / 4u], board[0xb4u / 4u],
            board[0xb8u / 4u], board[0xbcu / 4u]
        };
        (void)gx8002_xip_audio_output_logfbank_10204080(logfbank);
        return;
    }
    if (channel == 8u) {
        gx8002_i2s_output i2s = {{
            board[0xc0u / 4u], board[0xc4u / 4u], board[0xc8u / 4u],
            board[0xccu / 4u], board[0xd0u / 4u], board[0xd4u / 4u],
            board[0xd8u / 4u]
        }};
        (void)gx8002_xip_audio_output_i2s_10204228(i2s);
        (void)gx8002_xip_audio_set_i2sout_mode_10204340(0u);
    }
}
