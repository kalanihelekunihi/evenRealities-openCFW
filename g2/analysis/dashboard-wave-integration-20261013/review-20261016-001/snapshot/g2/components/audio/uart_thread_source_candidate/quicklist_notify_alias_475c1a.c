/* QuickList's native 0x475c1a call targets the existing BLE notification body. */
#include <stdint.h>

extern uint32_t audio_settings_notify_ble(uint8_t, uint8_t, const void *, uint32_t);

uint32_t audio_ring_pb_tx_ble_475c1a(uint32_t type, uint32_t command,
                                     const void *payload, uint32_t length) {
    return audio_settings_notify_ble((uint8_t)type, (uint8_t)command,
                                     payload, length);
}
