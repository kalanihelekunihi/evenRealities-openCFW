/* SPDX-License-Identifier: MIT */
/* TWS diagnostic VAD history immediately follows state/countdown. */
#include <stdint.h>
uint32_t open_cfw_gx8002_tws_audio_last_vad
    __attribute__((section(".bss.tws_audio_last_vad")));
_Static_assert(sizeof(open_cfw_gx8002_tws_audio_last_vad)==4,"TWS VAD ABI");
