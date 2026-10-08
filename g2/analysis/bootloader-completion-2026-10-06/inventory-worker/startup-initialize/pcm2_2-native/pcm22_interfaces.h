/* SPDX-License-Identifier: MIT
 * Recovered interfaces for locked bootloader f89a4c46; reconstruction, not
 * vendor originals. Caller scheduling/peripheral timing remains unverified.
 */
#ifndef OPENCFW_RECOVERED_PCM22_INTERFACES_H
#define OPENCFW_RECOVERED_PCM22_INTERFACES_H
#include <stdint.h>
typedef uint32_t (*opencfw_pcm22_sequence_fn)(uint32_t target_power,
    uint32_t current_power, uint32_t target_ton, uint32_t current_ton);
enum opencfw_pcm22_recovered_sequence {
    OPENCFW_PCM22_SEQUENCE_0=0, OPENCFW_PCM22_SEQUENCE_2=2,
    OPENCFW_PCM22_SEQUENCE_8=8, OPENCFW_PCM22_SEQUENCE_14=14,
    OPENCFW_PCM22_SEQUENCE_15=15, OPENCFW_PCM22_SEQUENCE_18=18, OPENCFW_PCM22_SEQUENCE_NOOP=24
};
enum opencfw_pcm22_pending_sequence {
    OPENCFW_PCM22_PENDING_2=2, OPENCFW_PCM22_PENDING_7=7,
    OPENCFW_PCM22_PENDING_NONE=26
};
#define OPENCFW_PCM22_CALLBACK_TABLE_ADDRESS UINT32_C(0x20000158)
#define OPENCFW_PCM22_PROFILE_ADDRESS UINT32_C(0x20026ba0)
#define OPENCFW_PCM22_PENDING_ADDRESS UINT32_C(0x2000055a)
#define OPENCFW_PCM22_TIMER_ENABLE_MASK UINT32_C(1)
#define OPENCFW_PCM22_TIMER_READY_MASK UINT32_C(0x40000000)
/* Stock timer compare is wait * 6; no milliseconds claim. */
void opencfw_pcm22_spot_timer_start(uint32_t wait);
void opencfw_pcm22_spot_timer_stop(void);
uint32_t opencfw_pcm22_icache_disable(void);
void opencfw_pcm22_sequence2b(void);
void opencfw_pcm22_sequence7b(void);
uint32_t opencfw_pcm22_timer_service(void);
uint32_t event_a_pcm22_transition_sequence_0(uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t event_a_pcm22_transition_sequence_2(uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t opencfw_spot_pcm22_transition14(uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t opencfw_spot_pcm22_transition18(uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t event_a_transition_sequence_24(uint32_t,uint32_t,uint32_t,uint32_t);
/* Selector15 preserves original R1=incoming fourth argument as high32.
 * Separate addon proof; not present in final370. */
uint64_t opencfw_spot_pcm22_transition15(uint32_t,uint32_t,uint32_t,uint32_t);
#endif
