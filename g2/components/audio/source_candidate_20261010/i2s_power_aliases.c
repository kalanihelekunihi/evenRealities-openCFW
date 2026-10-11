#include "../i2s_power_offline/power.c"

/* Diagnostic callback imports the selected Apollo entries directly. */
__asm__(".global audio_i2s_power\n"
        ".set audio_i2s_power, audio_i2s_power_selected\n"
        ".global audio_i2s_uninit\n"
        ".set audio_i2s_uninit, audio_i2s_uninitialize_selected\n");
