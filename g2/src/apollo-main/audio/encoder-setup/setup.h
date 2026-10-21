#ifndef OPENCFW_AUDIO_ENCODER_SETUP_OFFLINE_H
#define OPENCFW_AUDIO_ENCODER_SETUP_OFFLINE_H
#include <stdint.h>
/* Supplied memory must fit configuration-dependent state. No allocator/capacity check. */
void *audio_encoder_setup_selected(int hr, int duration_us, int codec_rate_hz,
                                  int pcm_rate_hz, void *memory);
void *audio_encoder_setup_standard(int duration_us, int codec_rate_hz,
                                  int pcm_rate_hz, void *memory);
/* Seven-word firmware config prefix; workspace starts at config+7, encoder handle at +6. */
void audio_encoder_reset_config(uint32_t *config);
#endif
