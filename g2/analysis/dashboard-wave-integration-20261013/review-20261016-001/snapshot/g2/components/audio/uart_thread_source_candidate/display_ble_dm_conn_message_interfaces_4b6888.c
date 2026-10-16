/* Cordio dmConnMsgHandler and dmConnUpdMsgHandler, stock Apollo Main.
 * CCB lookup, event gate, and child calls follow the registered Cordio source
 * and pinned Thumb bodies at 0x4b6888 and 0x4b6a16. */
#include <stdint.h>

extern void *dmConnCcbById(uint8_t);
extern void audio_ble_dm_conn_sm_execute_533ef4(void *, void *);
extern void audio_ble_dm_conn_upd_execute_4b6532(void *, void *);

void audio_ble_dm_conn_msg_handler_4b6888(void *message)
{
    uint8_t *m = (uint8_t *)message;
    void *ccb = dmConnCcbById(m[0u]);
    if (ccb != 0)
        audio_ble_dm_conn_sm_execute_533ef4(ccb, message);
}

void audio_ble_dm_conn_upd_msg_handler_4b6a16(void *message)
{
    uint8_t *m = (uint8_t *)message;
    uint8_t *ccb = (uint8_t *)dmConnCcbById(m[0u]);
    if (ccb != 0 && ccb[0x15u] == 3u)
        audio_ble_dm_conn_upd_execute_4b6532(ccb, message);
}
