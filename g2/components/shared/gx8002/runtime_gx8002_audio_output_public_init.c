/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern int printf_(const char *, ...);
typedef int (*output_init_callback)(uint32_t);
/* Linker-provided address of the separately source-defined dispatch object. */
extern const uint8_t open_cfw_gx8002_aout_default_dispatch[];
const char open_cfw_gx8002_aout_init_label[]="gx_audio_out_init";
const char open_cfw_gx8002_aout_error_format[]="[AOUT ERROR] %s %d\n";
int open_cfw_gx8002_audio_out_init(uint32_t mode)
{
    void *volatile *global=(void *volatile *)0x2002734cu;
    if (!*global) *global=(void *)open_cfw_gx8002_aout_default_dispatch;
    void *dispatch=*global;
    if (!dispatch) {
        printf_(open_cfw_gx8002_aout_error_format,
                open_cfw_gx8002_aout_init_label,377);
        return -1;
    }
    output_init_callback callback=*(output_init_callback volatile *)((uintptr_t)dispatch+4);
    if (callback) return callback(mode);
    return 0;
}
