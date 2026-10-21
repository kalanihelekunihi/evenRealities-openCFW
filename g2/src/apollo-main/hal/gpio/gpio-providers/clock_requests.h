#pragma once
#include <stdint.h>
void audio_clock_reference_update(uint32_t reference);
void audio_clock_requests_update(uint32_t mux_index,uint32_t sources);
