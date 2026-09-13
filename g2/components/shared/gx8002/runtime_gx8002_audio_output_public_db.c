/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <gx_audio_out/gx_audio_out_v2.h>
extern int printf_(const char *, ...);
extern const char open_cfw_gx8002_aout_error_format[];
const char open_cfw_gx8002_aout_db_label[]="gx_audio_out_set_db";
typedef int (*output_db_callback)(void *, int16_t);
int open_cfw_gx8002_audio_out_set_db(int handle, int16_t db)
{
    void *dispatch=*(void *volatile *)0x2002734cu;
    if (!dispatch) {
        printf_(open_cfw_gx8002_aout_error_format,
                open_cfw_gx8002_aout_db_label,325);
        return -1;
    }
    output_db_callback callback=*(output_db_callback volatile *)((uintptr_t)dispatch+56);
    if (callback) return callback((void *)(uintptr_t)(uint32_t)handle,db);
    return 0;
}
