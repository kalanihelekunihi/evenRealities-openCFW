/* Cordio attsConnCback; stock Main 0x534aba, valid connection IDs. */
#include <stdint.h>
extern uint8_t audio_ble_atts_state[];
extern void audio_ble_atts_ccb_queue_cleanup_534cde(uint8_t *);
extern uint16_t audio_ble_dm_conn_check_idle_4b73a2(uint8_t);
extern void WsfTimerStop(void *);
void audio_ble_atts_conn_534aba(uint8_t *ccb, uint8_t *event)
{
    const uint8_t connection = ccb[0x0eu];
    if (connection == 0u)
        return;
    if (event[2u] == 0x28u) {
        for (uint8_t slot = 0u; slot < 3u; ++slot) {
            uint8_t *server = audio_ble_atts_state +
                ((uint32_t)connection - 1u) * 0xc0u + (uint32_t)slot * 0x40u;
            audio_ble_atts_ccb_queue_cleanup_534cde(server);
            if ((audio_ble_dm_conn_check_idle_4b73a2(connection) & 4u) != 0u)
                WsfTimerStop(server + 0x14u);
        }
    }
    uint8_t *interface = *(uint8_t **)(audio_ble_atts_state + 0x260u);
    void (*callback)(uint8_t *, uint8_t *) =
        *(void (**)(uint8_t *, uint8_t *))(interface + 12u);
    callback(ccb, event);
}
