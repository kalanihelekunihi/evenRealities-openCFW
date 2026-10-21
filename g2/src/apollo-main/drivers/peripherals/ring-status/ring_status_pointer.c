/* Native ROM pointer DAT_0047d900 targets the packed status byte
 * 0x20075043. The RAM byte is owned by ux_ble_status.c. */
#include <stdint.h>

extern volatile uint8_t audio_ota_packed_status;
const volatile uint8_t *const audio_uart_ring_status_word =
    &audio_ota_packed_status;
