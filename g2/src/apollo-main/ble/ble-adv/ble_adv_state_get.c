/* Native dmConnGetAdvState 0x46ef60, used by communication handler.
 * 0x46f43c is an authenticated literal pointer to live RAM 0x20074f8d. */
#include <stdint.h>
extern volatile uint8_t audio_ble_slave_adv_stop_flag_20074f8d;
uint32_t audio_ble_connection_get(void) {
    return audio_ble_slave_adv_stop_flag_20074f8d;
}
