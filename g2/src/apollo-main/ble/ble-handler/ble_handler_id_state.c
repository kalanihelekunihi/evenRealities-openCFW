#include <stdint.h>

/* Native handler ID shared by message transport and connect request: 0x20074f8e. */
volatile uint8_t audio_ble_msgtx_handler_id
    __attribute__((section(".g2_ram_20074f8e")));
extern volatile uint8_t audio_ble_connect_event_handler
    __attribute__((alias("audio_ble_msgtx_handler_id")));
