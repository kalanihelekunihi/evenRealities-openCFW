/* SPDX-License-Identifier: MIT
 * Native audio-board accessors 0x10203004/0x1020300c and log initializer
 * 0x10203024. The first two bind existing selected product source providers.
 */
#include <stdint.h>

extern uint32_t g2_codec_audio_board_get(void);
extern int32_t g2_codec_audio_board_gain(int32_t);
extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);

const uint32_t *gx8002_xip_audio_board_get_10203004(void)
{
    return (const uint32_t *)(uintptr_t)g2_codec_audio_board_get();
}

int32_t gx8002_xip_audio_board_gain_1020300c(int32_t gain)
{
    return g2_codec_audio_board_gain(gain);
}

void gx8002_xip_audio_board_initialize_10203024(void)
{
    gx8002_xip_tws_publish_10206c24(
        "[AB]dmic          [%d Channel]\n", 2u);
    const uint16_t *board =
        (const uint16_t *)(uintptr_t)g2_codec_audio_board_get();
    uint32_t gain = (board[0x20u / 2u] & 0x1ffu) >> 6u;
    int32_t db = gx8002_xip_audio_board_gain_1020300c((int32_t)gain);
    gx8002_xip_tws_publish_10206c24(
        "[AB]dmic Ain_gain:[%d dB]\n", db);
}
