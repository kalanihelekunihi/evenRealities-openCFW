/* SPDX-License-Identifier: MIT
 * Bounded reconstructed PCM2.2 selector interfaces; not the full table.
 */
#ifndef OPENCFW_STARTUP_PCM22_SEQUENCES_H
#define OPENCFW_STARTUP_PCM22_SEQUENCES_H
#include <stdint.h>
/* R0/R1 preserve the observed two-word result, not a generic success code. */
uint64_t opencfw_spot_pcm22_transition3(uint32_t,uint32_t,uint32_t,uint32_t);
uint64_t opencfw_spot_pcm22_transition17(uint32_t,uint32_t,uint32_t,uint32_t);
uint64_t opencfw_spot_pcm22_transition1(uint32_t,uint32_t,uint32_t,uint32_t);
#endif
