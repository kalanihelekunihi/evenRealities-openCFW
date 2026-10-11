/* Diagnostic codec control at 0x53ca11 is the already reconstructed
 * type-0 watchdog message emitter. Preserve its entry and publisher call. */
#include "../watchdog_callback_offline/watchdog.c"

__asm__(".global audio_codec_control\n"
        ".set audio_codec_control, audio_watchdog_emit_type0\n");
