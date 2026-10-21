#ifndef AUDIO_HFRC_SYSPLL_H
#define AUDIO_HFRC_SYSPLL_H
#include <stdint.h>
void audio_hfrc_wait(volatile uint32_t *counter);
void audio_hfrc2_wait(volatile uint32_t *counter);
uint32_t audio_hfrc_request(uint32_t user),audio_hfrc_release(uint32_t user);
uint32_t audio_hfrc2_request(uint32_t user),audio_hfrc2_release(uint32_t user);
uint32_t audio_syspll_request(uint32_t user),audio_syspll_release(uint32_t user);
#endif
