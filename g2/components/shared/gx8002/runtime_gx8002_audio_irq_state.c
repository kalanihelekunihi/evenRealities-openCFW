/* SPDX-License-Identifier: MIT */
/* Shared audio input state, populated by gx_audio_in_init and used by IRQ. */
#include <stdint.h>
#include <gx_audio_in/gx_audio_in_v2.h>
struct audio_runtime {
    uint32_t input,output;
    GX_AUDIO_IN_CONFIG_CB config;
    GX_AUDIO_IN_RECORD_CB record;
    GX_AUDIO_IN_UPDATE_CB update;
    GX_AUDIO_IN_ENGVAD_CB engvad;
    GX_AUDIO_IN_FFTVAD_CB fftvad;
};
_Static_assert(sizeof(struct audio_runtime)==28,"Audio runtime ABI");
volatile struct audio_runtime open_cfw_gx8002_audio_runtime
    __attribute__((section(".bss.audio_irq_runtime")));
