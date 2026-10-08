#ifndef OPENCFW_PCM22_PRODUCERS_OFFLINE_H
#define OPENCFW_PCM22_PRODUCERS_OFFLINE_H
#include <stdint.h>
/* Includes the sealed sequence2 and fixed-width pending-state interface. */
#include "../transition_timer_offline/transition.h"
void pcm22_sequence_7(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_sequence_21(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
uint32_t pcm22_icache_enable(void);
uint32_t pcm22_icache_disable(void);
void pcm22_sequence_8(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_sequence_9(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_sequence_20(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_sequence_10(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_sequence_12(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_sequence_14(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_sequence_15(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_sequence_16(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_sequence_17(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_sequence_19(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_sequence_0(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_sequence_1(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_sequence_3(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_sequence_4(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_sequence_5(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_sequence_6(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_sequence_11(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_sequence_13(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_sequence_18(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_sequence_22(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_sequence_23(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_sequence_24(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_sequence_25(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_sequence_26(uint32_t next,uint32_t old,uint32_t ton,uint32_t old_ton);
void pcm22_registered_timer_service(void);
void pcm22_timer15_vector_handler(void);
uint32_t pcm22_registered_post_low_to_high(void);
void pcm22_ton_adjust(uint32_t ton,uint32_t profile);
#endif
