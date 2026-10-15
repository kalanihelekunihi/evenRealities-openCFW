#include <stdint.h>

/* Five adjacent four-byte live records initialized by the BLE service handlers. */
uint8_t audio_ble_efs_handler_state[4] __attribute__((section(".g2_ram_200748a4")));
uint8_t audio_ble_ess_handler_state[4] __attribute__((section(".g2_ram_200748a8")));
uint8_t audio_ble_eus_handler_state[4] __attribute__((section(".g2_ram_200748ac")));
uint8_t audio_ble_nus_handler_state[4] __attribute__((section(".g2_ram_200748b0")));
uint8_t audio_ble_ota_handler_state[4] __attribute__((section(".g2_ram_200748b4")));
