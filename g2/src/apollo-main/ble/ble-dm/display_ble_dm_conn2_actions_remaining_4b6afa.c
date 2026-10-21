/* Five Cordio secondary HCI callback actions at Apollo Main 0x4b6afa..0x4b6c22. */
#include <stdint.h>

extern uint8_t audio_dm_connection_records[];

static void put16(uint8_t *p, uint16_t value)
{
    p[0u] = (uint8_t)value;
    p[1u] = (uint8_t)(value >> 8u);
}

static void emit(uint8_t *event)
{
    void (*callback)(void *) =
        *(void (**)(void *))(void *)(audio_dm_connection_records + 0x9cu);
    callback(event);
}

static void header(uint8_t *out, const uint8_t *ccb, uint8_t event, uint8_t status)
{
    put16(out, ccb[0x10u]);
    out[2u] = event;
    out[3u] = status;
}

void audio_ble_dm_conn2_act_write_auth_to_cmpl_4b6afa(void *ccb, void *message)
{
    const uint8_t *m = (const uint8_t *)message;
    uint8_t evt[12];
    header(evt, (const uint8_t *)ccb, 0x42u, 0u);
    evt[4u] = m[4u];
    evt[6u] = m[6u];
    evt[7u] = m[7u];
    emit(evt);
}

void audio_ble_dm_conn2_act_auth_to_expired_4b6b28(void *ccb, void *message)
{
    const uint8_t *m = (const uint8_t *)message;
    uint8_t evt[8];
    header(evt, (const uint8_t *)ccb, 0x43u, 0u);
    evt[4u] = m[4u];
    evt[5u] = m[5u];
    emit(evt);
}

void audio_ble_dm_conn2_act_read_remote_features_cmpl_4b6b50(
    void *ccb, void *message)
{
    uint8_t *c = (uint8_t *)ccb;
    const uint8_t *m = (const uint8_t *)message;
    uint8_t evt[16];
    for (unsigned i = 0u; i < 4u; ++i)
        c[0x28u + i] = m[8u + i];
    c[0x2cu] = 1u;
    header(evt, c, 0x57u, 0u);
    evt[4u] = m[4u];
    evt[6u] = m[6u];
    evt[7u] = m[7u];
    for (unsigned i = 0u; i < 8u; ++i)
        evt[8u + i] = m[8u + i];
    emit(evt);
}

void audio_ble_dm_conn2_act_read_remote_ver_info_cmpl_4b6bac(
    void *ccb, void *message)
{
    const uint8_t *m = (const uint8_t *)message;
    uint8_t evt[16];
    header(evt, (const uint8_t *)ccb, 0x58u, 0u);
    evt[4u] = m[4u];
    evt[6u] = m[6u];
    evt[7u] = m[7u];
    evt[8u] = m[8u];
    evt[10u] = m[10u];
    evt[11u] = m[11u];
    evt[12u] = m[12u];
    evt[13u] = m[13u];
    emit(evt);
}

void audio_ble_dm_conn2_act_req_peer_sca_4b6bee(void *ccb, void *message)
{
    const uint8_t *c = (const uint8_t *)ccb;
    const uint8_t *m = (const uint8_t *)message;
    uint8_t evt[12];
    header(evt, c, 0x69u, m[4u]);
    evt[4u] = m[4u];
    evt[6u] = c[0x0cu];
    evt[7u] = c[0x0du];
    evt[8u] = m[8u];
    emit(evt);
}
