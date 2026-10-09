#ifndef AUDIO_TIMER_DAEMON_ORDER_H
#define AUDIO_TIMER_DAEMON_ORDER_H
#include <stdint.h>
uint32_t audio_timer_next_expiry(uint32_t *list_empty);
uint32_t audio_timer_sample_time(uint32_t *lists_switched);
void audio_timer_expired(uint32_t expiry,uint32_t now);
void audio_timer_process_or_block(uint32_t expiry,uint32_t list_empty);
/* Infinite stock task body. Offline tests stop at a real callback/block boundary
 * or next-iteration entry; no synthetic callback/blocking return is supplied. */
void audio_timer_daemon(void *unused);
#endif
