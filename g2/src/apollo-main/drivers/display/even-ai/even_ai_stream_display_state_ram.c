/* Bounded stock streaming-display state clear extent, 0x20073a1c..0x20073a3c. */
#include <stdint.h>

uint8_t audio_even_ai_stream_display_state_20073a1c[0x20]
    __attribute__((section(".bss.opencfw.evenai.stream_display"), aligned(4), used));

_Static_assert(sizeof(audio_even_ai_stream_display_state_20073a1c) == 0x20u,
               "stock stream display clear extent");
