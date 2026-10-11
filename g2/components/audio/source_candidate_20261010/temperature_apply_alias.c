/* Original early PCM temperature adjustment entry under its caller name. */
#include "../early_pcm_pending_offline/pending.c"

__asm__(".global stock_temperature_apply\n"
        ".set stock_temperature_apply, pcm_hardware_temperature\n");
