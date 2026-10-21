#include <stdint.h>

/* Native ANCC cache RAM 0x2006ddd4; initializer clears 0x2fc bytes. */
uint8_t audio_ble_ancc_cache[0x2fc] __attribute__((aligned(4)));

/* Native ANCC registration pointer cells populated during profile init. */
uint8_t *audio_ble_ancc_controller;       /* 0x20074898 */
uint8_t *audio_ble_ancc_mode;             /* 0x2007489c */
uint8_t *audio_ble_ancc_service_context; /* 0x200748a0 */

/* Native connection tick RAM 0x200742f4. */
uint32_t audio_ble_ancc_connection_tick;
/* The BLE communication encryption path names this same native word. */
extern uint32_t audio_ble_encrypt_tick_200742f4
    __attribute__((alias("audio_ble_ancc_connection_tick")));
