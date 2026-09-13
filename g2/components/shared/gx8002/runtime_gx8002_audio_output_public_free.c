/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern int printf_(const char *, ...);
extern const char open_cfw_gx8002_aout_error_format[];
const char open_cfw_gx8002_aout_free_label[]="gx_audio_out_free";
typedef int (*output_free_callback)(void *);
int open_cfw_gx8002_audio_out_free(int handle)
{
    void *dispatch=*(void *volatile *)0x2002734cu;
    if (!dispatch) {
        printf_(open_cfw_gx8002_aout_error_format,
                open_cfw_gx8002_aout_free_label,245);
        return -1;
    }
    output_free_callback callback=*(output_free_callback volatile *)((uintptr_t)dispatch+20);
    if (callback) return callback((void *)(uintptr_t)(uint32_t)handle);
    return 0;
}
