#pragma once
#include <stdint.h>
uint32_t pcm21_boost_service(void);
uint32_t opencfw_spot_pcm22_transition6(uint32_t target,uint32_t current,uint32_t ton,uint32_t old_ton);
/* Internal reconstructed ABI. TON field units remain address-defined. */
