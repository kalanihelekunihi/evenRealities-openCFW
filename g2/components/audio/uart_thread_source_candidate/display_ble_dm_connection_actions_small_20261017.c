/* Four bounded Cordio DM connection actions from the stock Main image.
 * The byte offsets below are confirmed by the stock call sites; lower
 * providers retain separate source and layout gates. */
#include <stdint.h>

extern void audio_ble_dm_conn_open_536a28(uint8_t, uint8_t, const uint8_t *);
extern void audio_ble_hci_create_conn_cancel_52b0a4(void);
extern void audio_ble_dm_dev_pass_priv_4b2ea6(uint8_t, uint8_t,
                                                uint32_t, uint32_t);
extern void audio_ble_hci_conn_update_52af40(uint16_t, const uint8_t *);
extern void audio_ble_dm_adv_start_directed_4ba6d4(uint8_t, uint16_t,
                                                     uint8_t, const uint8_t *);

void audio_ble_dm_action_536a86(const uint8_t *ccb, const uint8_t *msg)
{
    (void)ccb;
    audio_ble_dm_conn_open_536a28(msg[4], msg[17], msg + 11);
}

void audio_ble_dm_action_55bc5c(const uint8_t *ccb, const uint8_t *msg)
{
    (void)ccb;
    (void)msg;
    audio_ble_hci_create_conn_cancel_52b0a4();
    audio_ble_dm_dev_pass_priv_4b2ea6(14u, 1u, 0u, 0u);
}

void audio_ble_dm_action_55bc70(const uint8_t *ccb, const uint8_t *msg)
{
    const uint16_t handle = (uint16_t)ccb[12] | ((uint16_t)ccb[13] << 8);
    audio_ble_hci_conn_update_52af40(handle, msg + 4);
}

void audio_ble_dm_action_536ac8(const uint8_t *ccb, const uint8_t *msg)
{
    (void)ccb;
    const uint16_t duration = (uint16_t)msg[8] | ((uint16_t)msg[9] << 8);
    audio_ble_dm_adv_start_directed_4ba6d4(msg[6], duration, msg[17],
                                            msg + 11);
}
