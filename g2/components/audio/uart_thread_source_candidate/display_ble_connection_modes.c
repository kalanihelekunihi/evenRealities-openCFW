/* Apollo Main compressed SRAM record 0x75d3f4 initializes the requested
 * and current connection modes at 0x20004541 and 0x20004542. Native RAM
 * placement and surrounding bytes remain linker/layout gates. */
#include <stdint.h>

volatile uint8_t audio_ble_requested_conn_mode = 0xa4u;
volatile uint8_t audio_ble_current_conn_mode = 0xa4u;
/* ble_msgtx_isConnected reads this same native byte at 0x20004542. */
__asm__(".global audio_ble_connection_marker\n"
        ".set audio_ble_connection_marker,audio_ble_current_conn_mode");
