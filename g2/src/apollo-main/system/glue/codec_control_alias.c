/* Builds drivers/power/watchdog-callback/watchdog.c (audio_watchdog_tick, stock
 * 0x53C2A4). The diagnostic codec control at 0x53ca11 is the type-0 message
 * emitter 0x53ca10; audio_codec_control is now an alias of
 * audio_app_stream_enable_53ca10 in audio/audio-app/audio_app_setup_children_20261016.c. */
#include "../../drivers/power/watchdog-callback/watchdog.c"
