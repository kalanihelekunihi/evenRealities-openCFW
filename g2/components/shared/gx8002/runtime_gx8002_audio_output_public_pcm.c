/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <gx_audio_out/gx_audio_out_v2.h>
extern int printf_(const char *, ...);
extern const char open_cfw_gx8002_aout_error_format[];
const char open_cfw_gx8002_aout_pcm_label[]="gx_audio_out_config_pcm";
typedef int (*output_pcm_callback)(void *, const volatile GX_AUDIO_OUT_PCM *);
int open_cfw_gx8002_audio_out_config_pcm(int handle, const volatile GX_AUDIO_OUT_PCM *config)
{
    void *dispatch=*(void *volatile *)0x2002734cu;
    if (!dispatch) {
        printf_(open_cfw_gx8002_aout_error_format,
                open_cfw_gx8002_aout_pcm_label,265);
        return -1;
    }
    output_pcm_callback callback=*(output_pcm_callback volatile *)((uintptr_t)dispatch+28);
    if (callback) return callback((void *)(uintptr_t)(uint32_t)handle,config);
    return 0;
}
