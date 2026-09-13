/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <gx_audio_out/gx_audio_out_v2.h>
extern int printf_(const char *, ...);
extern const char open_cfw_gx8002_aout_error_format[];
const char open_cfw_gx8002_aout_frame_label[]="gx_audio_out_push_frame";
typedef int (*output_frame_callback)(void *, const volatile GX_AUDIO_OUT_FRAME *);
int open_cfw_gx8002_audio_out_push_frame(int handle, const volatile GX_AUDIO_OUT_FRAME *config)
{
    void *dispatch=*(void *volatile *)0x2002734cu;
    if (!dispatch) {
        printf_(open_cfw_gx8002_aout_error_format,
                open_cfw_gx8002_aout_frame_label,305);
        return -1;
    }
    output_frame_callback callback=*(output_frame_callback volatile *)((uintptr_t)dispatch+44);
    if (callback) return callback((void *)(uintptr_t)(uint32_t)handle,config);
    return 0;
}
