#ifndef OPENCFW_PCM22_TRANSITION_TIMER_OFFLINE_H
#define OPENCFW_PCM22_TRANSITION_TIMER_OFFLINE_H
#include <stdint.h>
/* Stock state at20004540 has a one-byte footprint, independent of host enum ABI. */
typedef uint8_t pcm22_pending_sequence;
#define PCM22_PENDING_2 ((pcm22_pending_sequence)2)
#define PCM22_PENDING_7 ((pcm22_pending_sequence)7)
#define PCM22_PENDING_NONE ((pcm22_pending_sequence)26)
void pcm22_sequence_2(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_sequence_2_complete(void);
void pcm22_sequence_7_complete(void);
void pcm22_boost_completion(void);
void pcm22_timer_stop(void);
void pcm22_sequence_21_complete(void);
uint32_t pcm22_post_low_to_high(void);
#endif
