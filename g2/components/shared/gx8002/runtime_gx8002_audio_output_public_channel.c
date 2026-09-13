/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <gx_audio_out/gx_audio_out_v2.h>
extern int printf_(const char *, ...);
extern const char open_cfw_gx8002_aout_error_format[];
const char open_cfw_gx8002_aout_channel_label[]="gx_audio_out_set_channel";
typedef int (*output_channel_callback)(void *, GX_AUDIO_OUT_CHANNEL);
int open_cfw_gx8002_audio_out_set_channel(int handle, GX_AUDIO_OUT_CHANNEL channel)
{
    void *dispatch=*(void *volatile *)0x2002734cu;
    if (!dispatch) {
        printf_(open_cfw_gx8002_aout_error_format,
                open_cfw_gx8002_aout_channel_label,365);
        return -1;
    }
    output_channel_callback callback=*(output_channel_callback volatile *)((uintptr_t)dispatch+72);
    if (callback) return callback((void *)(uintptr_t)(uint32_t)handle,channel);
    return 0;
}
