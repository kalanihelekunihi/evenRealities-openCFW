/* Cordio dmDevPassHciEvtToConn 0x4d29c2: selected connection interface. */
#include <stdint.h>

extern uint8_t audio_ble_dm_config[];

void audio_ble_dm_dev_pass_hci_conn_4d29c2(void *event)
{
    uintptr_t owner = 0u;
    for (uint32_t i = 0; i < sizeof owner; ++i) {
        owner |= (uintptr_t)audio_ble_dm_config[0x0cu + i] << (8u * i);
    }
    typedef void (*audio_ble_dm_conn_callback_t)(void *);
    const audio_ble_dm_conn_callback_t *callbacks =
        (const audio_ble_dm_conn_callback_t *)(uintptr_t)owner;
    callbacks[1u](event);
}
