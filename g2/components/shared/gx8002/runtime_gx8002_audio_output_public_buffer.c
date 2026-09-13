/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern int printf_(const char *, ...);
extern const char open_cfw_gx8002_aout_error_format[];
const char open_cfw_gx8002_aout_buffer_label[]="gx_audio_out_config_buffer";
typedef int (*output_buffer_callback)(int, const volatile uint32_t *);
int open_cfw_gx8002_audio_out_config_buffer(int handle, const volatile uint32_t *config)
{
    void *dispatch=*(void *volatile *)0x2002734cu;
    if (!dispatch) {
        printf_(open_cfw_gx8002_aout_error_format,
                open_cfw_gx8002_aout_buffer_label,255);
        return -1;
    }
    output_buffer_callback callback=*(output_buffer_callback volatile *)((uintptr_t)dispatch+24);
    if (callback) return callback(handle,config);
    return 0;
}
