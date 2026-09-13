/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <gx_audio_out/gx_audio_out_v2.h>
extern int printf_(const char *, ...);
extern const char open_cfw_gx8002_aout_error_format[];
const char open_cfw_gx8002_aout_cb_label[]="gx_audio_out_config_cb";
typedef int (*output_cb_callback)(void *, const volatile GX_AUDIO_OUT_CALLBACK *);
int open_cfw_gx8002_audio_out_config_cb(int handle, const volatile GX_AUDIO_OUT_CALLBACK *config)
{
    void *dispatch=*(void *volatile *)0x2002734cu;
    if (!dispatch) {
        printf_(open_cfw_gx8002_aout_error_format,
                open_cfw_gx8002_aout_cb_label,295);
        return -1;
    }
    output_cb_callback callback=*(output_cb_callback volatile *)((uintptr_t)dispatch+40);
    if (callback) return callback((void *)(uintptr_t)(uint32_t)handle,config);
    return 0;
}
