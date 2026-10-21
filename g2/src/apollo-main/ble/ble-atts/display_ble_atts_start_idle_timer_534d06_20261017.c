/* Cordio server idle timer setup, stock 0x534d06..0x534d46. */
#include <stdint.h>

extern uint8_t audio_ble_att_cfg_ptr_200004b4[4];
extern uint8_t audio_ble_att_common_state[];
extern void audio_ble_dm_conn_set_idle(uint8_t, uint8_t, uint8_t);
extern void WsfTimerStartSec(void *, uint32_t);

void audio_ble_atts_start_idle_timer_534d06(uint8_t *ccb)
{
    const uint8_t *const config = (const uint8_t *)(uintptr_t)
        *(const uint32_t *)(const void *)audio_ble_att_cfg_ptr_200004b4;
    const uint32_t seconds = *(const uint32_t *)(const void *)config;
    if (seconds == 0u)
        return;
    uint8_t *const main_ccb = (uint8_t *)(uintptr_t)
        *(const uint32_t *)(const void *)(ccb + 0x10u);
    const uint8_t connection = main_ccb[0x0eu];
    audio_ble_dm_conn_set_idle(connection, 4u, 1u);
    ccb[0x20u] = audio_ble_att_common_state[0x60u];
    ccb[0x1eu] = 0x20u;
    *(uint16_t *)(void *)(ccb + 0x1cu) = connection;
    WsfTimerStartSec(ccb + 0x14u, seconds);
}
