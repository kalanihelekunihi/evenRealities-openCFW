#include <stdint.h>

/* Native BLE communication state 0x200727f0; observed handler byte +0x56. */
uint8_t audio_ble_comm_state[0x57] __attribute__((aligned(4)));

/* Native BLE WSF thread state 0x20004068; semaphore handle at +0x14. */
uint8_t audio_ble_wsf_thread_state[0x18] __attribute__((aligned(4)));
