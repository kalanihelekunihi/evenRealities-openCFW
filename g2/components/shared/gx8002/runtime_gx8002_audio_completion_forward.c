/* SPDX-License-Identifier: MIT */
/* Recovered package 0x180e4. The volatile callback is loaded even when private_data
 * is zero; callback result is ignored. Matches upstream _SnpuCallback; uses the authenticated GRUS callback declaration. */
#include <driver/gx_snpu.h>
_Static_assert(sizeof(GX_SNPU_STATE)==4,"state ABI word");
_Static_assert(sizeof(GX_SNPU_CALLBACK)==4,"callback pointer width");
extern GX_SNPU_CALLBACK volatile open_cfw_gx8002_audio_completion_callback;
int open_cfw_gx8002_audio_completion_forward(int module_id,GX_SNPU_STATE state,void *private_data)
{
    GX_SNPU_CALLBACK callback=open_cfw_gx8002_audio_completion_callback;
    if (callback && private_data) callback(module_id,state,private_data);
    return 0;
}
