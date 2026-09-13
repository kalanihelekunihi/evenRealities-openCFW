/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern int printf_(const char *, ...);
extern const char open_cfw_gx8002_aout_error_format[];
const char open_cfw_gx8002_aout_exit_label[]="gx_audio_out_exit";
typedef int (*output_exit_callback)(void);
int open_cfw_gx8002_audio_out_exit(void)
{
    void *dispatch=*(void *volatile *)0x2002734cu;
    if (!dispatch) {
        printf_(open_cfw_gx8002_aout_error_format,
                open_cfw_gx8002_aout_exit_label,387);
        return -1;
    }
    output_exit_callback callback=*(output_exit_callback volatile *)((uintptr_t)dispatch+8);
    if (callback) return callback();
    return 0;
}
