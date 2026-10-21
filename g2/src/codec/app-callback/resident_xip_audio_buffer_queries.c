/* SPDX-License-Identifier: MIT
 * Native XIP 0x10206e6c/78/84/90, 0x10206f5c/90,
 * 0x10207024/4c. All six literal-pool words at 0x10206e74,
 * 0x10206e80, 0x10206e8c, 0x10206e98, 0x10206f70, and
 * 0x10206f98 are 0x20027b60 in the authenticated XIP image.
 * Header fields remain runtime/product inputs at that SRAM address.
 */
#include <stdint.h>

static volatile const uint32_t *const audio_header =
    (volatile const uint32_t *)(uintptr_t)UINT32_C(0x20027b60);

uint32_t gx8002_xip_mic_buffer_addr_10206e6c(void)
{
    return audio_header[0x50u / 4u];
}

uint32_t gx8002_xip_mic_buffer_size_10206e78(void)
{
    return audio_header[0x54u / 4u];
}

uint32_t gx8002_xip_logfbank_buffer_addr_10206e84(void)
{
    return audio_header[0x70u / 4u];
}

uint32_t gx8002_xip_logfbank_buffer_size_10206e90(void)
{
    return audio_header[0x74u / 4u];
}

uint32_t gx8002_xip_pcm_frame_size_10206f5c(void)
{
    return (audio_header[0x1cu / 4u] * audio_header[0x20u / 4u]) / 1000u;
}

uint32_t gx8002_xip_mic_channel_count_10206f90(void)
{
    return audio_header[8u / 4u];
}

uint32_t gx8002_xip_audio_input_buffer_size_10207024(uint32_t input)
{
    if (input == 2u)
        return (gx8002_xip_mic_buffer_size_10206e78() /
                gx8002_xip_mic_channel_count_10206f90()) * 2u;
    if (input == 4u)
        return gx8002_xip_logfbank_buffer_size_10206e90();
    return 0u;
}

uint32_t gx8002_xip_audio_input_buffer_addr_1020704c(uint32_t input)
{
    /* The native body calls board_get first; preserve its observable call. */
    extern const uint32_t *gx8002_xip_audio_board_get_10203004(void);
    (void)gx8002_xip_audio_board_get_10203004();
    if (input == 4u)
        return gx8002_xip_logfbank_buffer_addr_10206e84();
    if (input == 1u || input == 2u)
        return gx8002_xip_mic_buffer_addr_10206e6c();
    return 0u;
}
