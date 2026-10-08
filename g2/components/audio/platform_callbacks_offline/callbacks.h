#ifndef AUDIO_PLATFORM_CALLBACKS_OFFLINE_H
#define AUDIO_PLATFORM_CALLBACKS_OFFLINE_H
#include <stdint.h>
/* Offline reconstruction: fixed addresses belong only to the pinned OTA. */
uint32_t audio_platform_callbacks_initialize(void);
uint32_t audio_platform_early_control(uint32_t action, uint32_t enable, uint8_t *metadata);
uint32_t audio_platform_middle_control(uint32_t action, uint32_t enable, uint8_t *metadata);
uint32_t audio_platform_newer_control(uint32_t action, uint32_t enable, uint8_t *metadata);
uint32_t audio_platform_read_words(uint32_t kind,uint32_t word_offset,uint32_t word_count,uint32_t *destination);
uint32_t audio_platform_read_words_restricted(uint32_t kind,uint32_t word_offset,uint32_t word_count,uint32_t *destination);
uint32_t audio_platform_newer_initialize(void);
uint32_t audio_platform_get_revision(uint32_t *destination);
#endif
