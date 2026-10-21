/* Cordio dmConnUpdateCback at stock Main 0x56e4f8.
 * The event's byte 5 is not initialized by the stock routine. */
#include <stdint.h>

extern uint8_t audio_ble_dm_conn_rows_200712a4[];

void audio_ble_dm_slave_update_response_56e4f8(const uint8_t *ccb,
                                                 uint8_t reason)
{
    uint8_t event[8];
    event[0] = ccb[16];
    event[1] = 0u;
    event[2] = 0x29u;
    event[3] = reason;
    event[4] = reason;
    event[6] = ccb[12];
    event[7] = ccb[13];
    uintptr_t raw = (uintptr_t)audio_ble_dm_conn_rows_200712a4[0x9cu] |
                    ((uintptr_t)audio_ble_dm_conn_rows_200712a4[0x9du] << 8u) |
                    ((uintptr_t)audio_ble_dm_conn_rows_200712a4[0x9eu] << 16u) |
                    ((uintptr_t)audio_ble_dm_conn_rows_200712a4[0x9fu] << 24u);
    ((void (*)(void *))raw)(event);
}
