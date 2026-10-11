/* Apollo timer wait and public queue unlock both enter 0x441f88.
 * Preserve the full pinned queue unlock source and direct entry. */
#include "../timer_wake_providers_offline/unlock.c"

__asm__(".global audio_timer_wait_unlock\n"
        ".set audio_timer_wait_unlock, audio_public_queue_unlock\n");
