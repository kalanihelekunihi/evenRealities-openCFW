/* Cordio data length callback record at Apollo Main 0x4b6ab8. */
#include <stdint.h>

extern uint8_t audio_dm_connection_records[];

void audio_ble_dm_conn2_act_data_len_change_4b6ab8(void *ccb, void *message)
{
    const uint8_t *c = (const uint8_t *)ccb;
    const uint8_t *m = (const uint8_t *)message;
    uint8_t evt[16];
    evt[0u] = c[0x10u];
    evt[1u] = 0u;
    evt[2u] = 0x41u;
    evt[3u] = 0u;
    evt[4u] = c[0x0cu];
    evt[5u] = c[0x0du];
    for (unsigned i = 0u; i < 8u; ++i)
        evt[6u + i] = m[6u + i];
    void (*callback)(void *) =
        *(void (**)(void *))(void *)(audio_dm_connection_records + 0x9cu);
    callback(evt);
}
