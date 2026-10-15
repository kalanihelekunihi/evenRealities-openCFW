/* Apollo UX_GetSystemBLEStatus 0x47d8ce and shared RAM 0x20075043. */
#include <stdint.h>

volatile uint8_t audio_ota_packed_status
    __attribute__((section(".g2_ram_20075043")));
/* Earlier selected sources use this name for the same native byte. */
extern volatile uint8_t g2_audio_log_transport_bits
    __attribute__((alias("audio_ota_packed_status")));

uint8_t audio_ux_get_system_ble_status(void) {
    return (uint8_t)((audio_ota_packed_status&0x0cu)==0x0cu);
}
