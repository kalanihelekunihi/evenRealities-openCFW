/* Cordio dmAdvGenConnCmpl 0x4b310a: synthetic enhanced completion. */
#include <stdint.h>

extern uint8_t audio_ble_dm_adv_control[];
extern void audio_ble_dm_dev_pass_hci_conn_4d29c2(void *event);

void audio_ble_dm_adv_gen_conn_complete_4b310a(uint8_t handle, uint8_t status)
{
    uint8_t event[36] = {0};
    event[2u] = 2u;
    event[3u] = status;
    event[4u] = status;
    event[8u] = 1u;
    event[9u] = audio_ble_dm_adv_control[0x31u + handle];
    for (uint32_t i = 0; i < 6u; ++i) {
        event[10u + i] = audio_ble_dm_adv_control[0x25u + 6u * handle + i];
    }
    audio_ble_dm_dev_pass_hci_conn_4d29c2(event);
}
