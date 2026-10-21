/* Minimum C-owned storage for the native loading-page text at 0x200711dc.
 * The formatter receives a 200-byte capacity; the route can subsequently
 * write at index 200. Exact stock allocation and oversized-return behavior
 * remain open, so final placement must not use this as a size proof.
 */
#include <stdint.h>

__attribute__((used, section(".bss.g2_conversate_loading_text_200711dc")))
uint8_t audio_conversate_loading_text_200711dc[201];
