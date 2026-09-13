/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern int printf_(const char *, ...);
extern const char open_cfw_gx8002_aout_error_format[];
const char open_cfw_gx8002_aout_alloc_label[]="gx_audio_out_alloc_playback";
typedef void *(*output_alloc_callback)(unsigned int);
int open_cfw_gx8002_audio_out_alloc_playback(unsigned char route)
{
    void *dispatch=*(void *volatile *)0x2002734cu;
    if (!dispatch) {
        printf_(open_cfw_gx8002_aout_error_format,
                open_cfw_gx8002_aout_alloc_label,234);
        return -1;
    }
    output_alloc_callback callback=*(output_alloc_callback volatile *)dispatch;
    if (callback) return (int)(intptr_t)callback(route);
    return 0;
}
