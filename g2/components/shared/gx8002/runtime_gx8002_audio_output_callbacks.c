/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <gx_audio_out/gx_audio_out_v2.h>
_Static_assert(sizeof(GX_AUDIO_OUT_CALLBACK)==8,"Output callback ABI");
/* Package e8a4. Absent callbacks leave existing registrations intact. */
int open_cfw_gx8002_aout_config_cb(void *handle,
                                 const volatile GX_AUDIO_OUT_CALLBACK *callbacks)
{
    uintptr_t state=(uintptr_t)handle;
    GX_AUDIO_OUT_FRAME_CB frame=callbacks->new_frame_callback;
    if (frame) {
        volatile uint32_t *irq=(volatile uint32_t *)0xa0b00008u;
        *irq=*irq|1u;
        *(GX_AUDIO_OUT_FRAME_CB volatile *)(state+40)=frame;
        *(volatile uint8_t *)(state+27)=1;
    }
    GX_AUDIO_OUT_FRAME_OVER_CB over=callbacks->frame_over_callback;
    if (over) {
        *(GX_AUDIO_OUT_FRAME_OVER_CB volatile *)(state+44)=over;
        *(volatile uint8_t *)(state+26)=0;
    }
    return 0;
}
