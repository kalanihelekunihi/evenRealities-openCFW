/* Cordio attsMsgCback, stock 0x534c42..0x534c8a.
 * Control-block offsets follow authenticated stock load operands. */
#include <stdint.h>

extern uint8_t audio_ble_atts_state[];
extern void audio_ble_dm_conn_set_idle(uint8_t, uint8_t, uint8_t);
extern void audio_ble_atts_database_hash_update_534d46(void *);

typedef void (*audio_atts_msg_handler_t)(void *);

static audio_atts_msg_handler_t audio_atts_load_handler(const void *address)
{
    uintptr_t value = *(const uint32_t *)address;
    return (audio_atts_msg_handler_t)value;
}

void audio_ble_atts_msg_534c42(void *message)
{
    uint8_t *const msg = (uint8_t *)message;
    const uint8_t event = msg[2];
    if (event == 0x20u) {
        audio_ble_dm_conn_set_idle((uint8_t)*(uint16_t *)msg, 4u, 0u);
    } else if (event < 0x23u) {
        const uintptr_t interface = *(const uint32_t *)(const void *)
            (audio_ble_atts_state + 0x260u);
        audio_atts_load_handler((const void *)(interface + 8u))(message);
    } else if (event == 0x23u) {
        audio_atts_load_handler(audio_ble_atts_state + 0x264u)(message);
    } else if (event == 0x24u) {
        audio_ble_atts_database_hash_update_534d46(message);
    }
}
