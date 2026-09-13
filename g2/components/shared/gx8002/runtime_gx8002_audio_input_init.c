/* SPDX-License-Identifier: MIT */
/* Recovered LvpAudioInInit; callback layout from the pinned SDK. */
#include <stddef.h>
#include <driver/gx_audio_in.h>
extern void *memset(void *, int, size_t);
extern int open_cfw_gx8002_audio_input_config(void);
extern int open_cfw_gx8002_audio_input_record(GX_AUDIO_IN_CHANNEL, unsigned int *);
extern int open_cfw_gx8002_audio_input_update(GX_AUDIO_IN_CHANNEL, unsigned int *);
_Static_assert(sizeof(GX_AUDIO_IN_CONFIG) == 20, "Callback ABI");
int open_cfw_gx8002_audio_input_init(unsigned int callback)
{
    memset((void *)0x2002ecb0, 0, 20);
    GX_AUDIO_IN_CONFIG config;
    config.record_callback = open_cfw_gx8002_audio_input_record;
    config.config_callback = open_cfw_gx8002_audio_input_config;
    config.update_callback = open_cfw_gx8002_audio_input_update;
    config.engvad_callback = 0;
    config.fftvad_callback = 0;
    int result = gx_audio_in_init(config);
    *(volatile unsigned int *)0x2002dfa0 = callback;
    return result;
}
