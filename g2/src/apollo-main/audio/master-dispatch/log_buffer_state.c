/* Observed Apollo logger storage; initial contents and startup are still open.
 * The EasyLogger singleton (RAM 0x20070be8) and line buffer log_buf
 * (RAM 0x2006bd30) are the statics `elog` and `log_buf` of the upstream
 * EasyLogger elog.c unit and are no longer defined here. */
#include <stdint.h>

volatile uint32_t g2_audio_log_ring_state[4]
    __attribute__((section(".g2_ram_200004c8")));
