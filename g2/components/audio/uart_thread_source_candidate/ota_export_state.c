#include <stdint.h>

/* Native export buffer begins at 0x20072730; two checked clear paths use 0x60 bytes. */
uint8_t audio_ble_ota_export_state[0x60]
    __attribute__((section(".g2_ram_20072730")));

/* The log path reads the first byte of this same native allocation. */
extern volatile uint8_t g2_audio_log_transport_alt
    __attribute__((alias("audio_ble_ota_export_state")));
extern volatile uint8_t audio_ota_transfer_flag
    __attribute__((alias("audio_ble_ota_export_state")));
