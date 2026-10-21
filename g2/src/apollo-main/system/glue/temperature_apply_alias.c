/* Original early PCM temperature adjustment entry under its caller name. */
#include "../../audio/early-pcm/early-pcm-pending/pending.c"

__asm__(".global stock_temperature_apply\n"
        ".set stock_temperature_apply, pcm_hardware_temperature\n");
