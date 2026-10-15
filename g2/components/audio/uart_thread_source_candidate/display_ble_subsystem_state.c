/* Minimum source-owned appMaster state: ten 15-byte records followed by
 * live bytes through offset 0x9d. The original allocation extent is open. */
#include <stdint.h>

volatile uint8_t audio_ble_subsystem_state_20071670[0x9eu]
    __attribute__((section(".bss.g2.ram.ble_subsystem_state")));
