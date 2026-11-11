#include <stdint.h>

/* Native service-mode cell: 0x20075024. */
volatile uint8_t g2_audio_service_mode __attribute__((section(".g2_ram_20075024")));
extern volatile uint8_t audio_ble_ota_sync_status
    __attribute__((alias("g2_audio_service_mode")));
/* Same stock cell: role_get 0x45a578 writes it (strb @0x45a6c8, pool 0x45b0f4). */
extern volatile uint8_t audio_uart_device_role_cell
    __attribute__((alias("g2_audio_service_mode")));
