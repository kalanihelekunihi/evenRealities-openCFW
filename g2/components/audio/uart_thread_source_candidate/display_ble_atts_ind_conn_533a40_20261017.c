/* Cordio attsIndConnCback; stock Main 0x533a40, valid connection IDs. */
#include <stdint.h>
extern uint8_t audio_ble_atts_state[];
extern void WsfTimerStop(void *);
extern void audio_ble_atts_ind_ntf_callback_53394c(uint8_t, uint8_t *, uint8_t);
void audio_ble_atts_ind_conn_533a40(uint8_t *ccb, const uint8_t *event)
{
    if (event[2u] != 0x28u)
        return;
    const uint8_t connection = ccb[0x0eu];
    if (connection == 0u)
        return;
    const uint8_t status =
        (uint8_t)((event[3u] == 0u ? event[8u] : event[3u]) - 0x60u);
    for (uint8_t slot = 0u; slot < 3u; ++slot) {
        uint8_t *server = audio_ble_atts_state +
            ((uint32_t)connection - 1u) * 0xc0u + (uint32_t)slot * 0x40u;
        const uint16_t pending = (uint16_t)server[0x26u] |
            ((uint16_t)server[0x27u] << 8);
        if (pending != 0u) {
            WsfTimerStop(server);
            server[0x26u] = 0u;
            server[0x27u] = 0u;
        }
        audio_ble_atts_ind_ntf_callback_53394c(connection, server, status);
    }
}
