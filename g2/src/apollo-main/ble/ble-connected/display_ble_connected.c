/* Native ble_msgtx_isConnected 0x4780f8. */
#include <stdint.h>
extern volatile uint8_t audio_ble_connection_marker; /* RAM 0x20004542 */
/* Stock 0x4780F8 (ble_msgtx_isConnected) */
uint32_t audio_ble_is_connected(void) {return audio_ble_connection_marker==0xa3u;}
