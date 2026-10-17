/* 27-word calibration table filled by audio_platform_newer_initialize. */
#include <stdint.h>

__attribute__((section(".bss.opencfw.audio.voltage_routes"), used))
volatile uint32_t g2_audio_voltage_routes[27];

_Static_assert(sizeof(g2_audio_voltage_routes) == 108, "voltage route table extent");
