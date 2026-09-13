/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <gx_audio_in/gx_audio_in_v2.h>
typedef struct { uint32_t reserved0:28, bit28:1, reserved1:3; } threshold_control;
_Static_assert(sizeof(GX_AUDIO_IN_EVAD_THRESHOLD)==12,"EVAD threshold ABI");
/* Recovered package 0xda6c. Reject invalid selectors rather than the original
 * writes through a null peripheral base. Preserve ordered full-word stores. */
int open_cfw_gx8002_audio_evad_threshold(GX_AUDIO_IN_SOURCE source,GX_AUDIO_IN_EVAD_THRESHOLD threshold)
{
    volatile uint32_t *words;
    if (source==AUDIO_IN_SADC) words=(volatile uint32_t *)(uintptr_t)0xa0a00010u;
    else {
        if (source!=AUDIO_IN_PDM && source!=AUDIO_IN_I2S) return -1;
        words=(volatile uint32_t *)(uintptr_t)(0xa0a00010u+(uint32_t)source*16u);
        ((volatile threshold_control *)words)->bit28=0;
    }
    words[2]=threshold.evad_low_threshold;
    words[3]=threshold.evad_high_threshold;
    words[4]=threshold.evad_zcr_threshold;
    return 0;
}
