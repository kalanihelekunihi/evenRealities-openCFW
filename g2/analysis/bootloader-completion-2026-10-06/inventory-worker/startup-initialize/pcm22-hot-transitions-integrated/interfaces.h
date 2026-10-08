#ifndef OPENCFW_PCM22_BOUNDED_TRANSITIONS_H
#define OPENCFW_PCM22_BOUNDED_TRANSITIONS_H
#include <stdint.h>
/* Private reconstruction ABI; firmware walker ignores callback R0.
 * profile=0x20026ba0; word=profile+4+4*target; no index validation.
 * word: VDDF[6:0], CORE[16:7], TEMPCO[20:17], VDDC[27:21].
 * target/current are profile indices, ton/old_ton TON state values.
 * selector11 raw R0 is target-word address; others return packed LV bytes.
 * Not a drop-in binary signature or public device-safe API. */
uint32_t opencfw_spot_pcm22_transition5(uint32_t target,uint32_t current,uint32_t ton,uint32_t old_ton);
uint32_t opencfw_spot_pcm22_transition11(uint32_t target,uint32_t current,uint32_t ton,uint32_t old_ton);
uint32_t opencfw_spot_pcm22_transition12(uint32_t target,uint32_t current,uint32_t ton,uint32_t old_ton);
uint32_t opencfw_spot_pcm22_transition21(uint32_t target,uint32_t current,uint32_t ton,uint32_t old_ton);
#endif
