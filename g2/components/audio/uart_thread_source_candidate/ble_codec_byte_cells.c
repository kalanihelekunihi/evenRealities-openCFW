#include <stdint.h>

/* Source-owned cells whose native byte addresses are recorded in their callers. */
uint8_t audio_ble_flash_mode __attribute__((section(".g2_ram_20074f62")));
uint8_t audio_ble_profile_handler_id __attribute__((section(".g2_ram_20074f8a")));
extern uint8_t audio_ble_discovery_handler_id_20074f8a
    __attribute__((alias("audio_ble_profile_handler_id")));
volatile uint8_t audio_ble_fast_mode_throttle_enabled
    __attribute__((section(".g2_ram_20074f90")));
volatile uint8_t audio_ble_connect_request_pending
    __attribute__((section(".g2_ram_20074f91")));
volatile uint8_t audio_ble_device_manager_queue_errors
    __attribute__((section(".g2_ram_20074fb2")));
uint8_t audio_uart_font_flash_mode __attribute__((section(".g2_ram_20074fb8")));
uint8_t audio_uart_font_flash_sleep __attribute__((section(".g2_ram_20074fb9")));
uint8_t g2_pdm_alternate_initialized __attribute__((section(".g2_ram_20074fba")));
uint8_t g2_pdm_production_initialized __attribute__((section(".g2_ram_20074fbb")));
volatile uint8_t audio_ble_ota_sync_enabled
    __attribute__((section(".g2_ram_20074ff3")));
