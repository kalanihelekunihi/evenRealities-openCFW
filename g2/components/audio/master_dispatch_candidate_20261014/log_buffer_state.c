/* Observed Apollo logger storage; initial contents and startup are still open. */
#include <stdint.h>

volatile uint32_t g2_audio_log_ring_state[4]
    __attribute__((section(".g2_ram_200004c8")));

/* audio_dump_hex reads byte 0xf1; this is an observed slice, not a full map. */
uint8_t g2_audio_dump_log_state[0xf2]
    __attribute__((section(".g2_ram_20070be8")));

char g2_audio_dump_buffer[1024]
    __attribute__((section(".g2_ram_2006bd30")));
