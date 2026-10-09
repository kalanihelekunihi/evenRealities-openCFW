#ifndef AUDIO_CLOCK_MANAGER_OWNERSHIP_H
#define AUDIO_CLOCK_MANAGER_OWNERSHIP_H
#include <stdint.h>
/* Stock byte-narrowed ABI. Query helpers deliberately do not validate indices. */
uint32_t audio_clock_any(uint32_t clock);
uint32_t audio_clock_user(uint32_t clock,uint32_t user);
uint32_t audio_clock_count(uint32_t clock);
uint32_t audio_clock_set(uint32_t clock,uint32_t user,uint32_t requested);
uint32_t audio_xtal_status(uint8_t *status);
uint32_t audio_xtal_release(uint32_t user);
#endif
