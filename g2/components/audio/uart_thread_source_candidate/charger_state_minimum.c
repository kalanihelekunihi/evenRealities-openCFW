/* Minimum observed live charger state at 0x20073b30.
 * Native getters read the SOC word at +0x10 and signed charging byte +0x14.
 * The complete product allocation and startup state remain unknown. */
#include <stdint.h>

uint8_t audio_charger_state[0x15]
    __attribute__((section(".g2_ram_20073b30")));
