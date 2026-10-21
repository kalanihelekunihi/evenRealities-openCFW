/* Diagnostic codec control at 0x53ca11 is the already reconstructed
 * type-0 watchdog message emitter. Preserve its entry and publisher call. */
#include "../../drivers/power/watchdog-callback/watchdog.c"

__asm__(".global audio_codec_control\n"
        ".set audio_codec_control, audio_watchdog_emit_type0\n");
