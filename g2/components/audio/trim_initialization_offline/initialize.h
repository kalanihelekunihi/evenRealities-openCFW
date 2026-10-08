#pragma once
#include <stdint.h>
uint32_t pcm_variant_initialize(void);
uint32_t pcm_capture_trim_block(void); /* reconstruction of bounded parent block */
uint32_t pcm_early_initialize_noop(void);
uint32_t pcm_middle_reset_noop(void);
