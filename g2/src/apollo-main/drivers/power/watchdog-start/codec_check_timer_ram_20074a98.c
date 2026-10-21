/* Stock Apollo codec-audio watchdog timer handle cell at 0x20074a98. */
#include <stdint.h>

void *g2_audio_codec_check_timer
    __attribute__((section(".bss.opencfw.audio.codec_check_timer"),
                   used, aligned(4)));

_Static_assert(sizeof(g2_audio_codec_check_timer) == 4u,
               "Apollo timer handle pointer width");
