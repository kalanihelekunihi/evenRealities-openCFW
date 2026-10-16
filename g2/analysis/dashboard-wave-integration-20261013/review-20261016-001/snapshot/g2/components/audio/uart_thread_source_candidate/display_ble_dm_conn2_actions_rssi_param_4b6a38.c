/* Cordio secondary HCI callback records, native 0x4b6a38 and 0x4b6a6e. */
#include <stdint.h>

extern uint8_t audio_dm_connection_records[]; /* native dmConnCb 0x200712a4 */

static uint16_t u16(const uint8_t *p)
{
    return (uint16_t)p[0] | ((uint16_t)p[1] << 8u);
}

static void put16(uint8_t *p, uint16_t value)
{
    p[0] = (uint8_t)value;
    p[1] = (uint8_t)(value >> 8u);
}

static void emit(uint8_t *event)
{
    void (*callback)(void *) =
        *(void (**)(void *))(void *)(audio_dm_connection_records + 0x9cu);
    callback(event);
}

void audio_ble_dm_conn2_act_rssi_read_4b6a38(void *ccb, void *message)
{
    const uint8_t *c = (const uint8_t *)ccb;
    const uint8_t *m = (const uint8_t *)message;
    uint8_t evt[12];
    put16(evt, c[0x10u]);
    evt[2u] = 0x39u;
    evt[3u] = m[4u];
    evt[4u] = m[4u];
    put16(evt + 6u, u16(c + 0x0cu));
    evt[8u] = m[8u];
    emit(evt);
}

void audio_ble_dm_conn2_act_remote_conn_param_req_4b6a6e(void *ccb, void *message)
{
    const uint8_t *c = (const uint8_t *)ccb;
    const uint8_t *m = (const uint8_t *)message;
    uint8_t evt[16];
    put16(evt, c[0x10u]);
    evt[2u] = 0x40u;
    evt[3u] = 0u;
    put16(evt + 4u, u16(c + 0x0cu));
    for (unsigned i = 0u; i < 4u; ++i)
        put16(evt + 6u + i * 2u, u16(m + 6u + i * 2u));
    emit(evt);
}
