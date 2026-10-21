/* Cordio attsIndMsgCback, selected stock body 0x533bcc..0x533c4c.
 * Timeout branch in this image ends after connection lookup. */
#include <stdint.h>

extern uint8_t *audio_ble_att_registration_lookup(uint8_t, uint8_t);
extern void WsfMsgFree(void *);
extern uint8_t audio_ble_atts_pend_ind_ntf_5338ac(uint8_t *, void *);
extern void audio_ble_atts_exec_callback_533934(uint8_t, uint16_t, uint8_t);
extern void audio_ble_atts_setup_msg_5339ac(uint8_t *, uint8_t, uint8_t, void *);
extern void audio_ble_att_decode_msg_param_4b50fe(uint16_t, uint8_t *, uint8_t *);

void audio_ble_atts_ind_msg_533bcc(void *message)
{
    uint8_t *const msg = (uint8_t *)message;
    uint8_t *const packet = (uint8_t *)(uintptr_t)
        *(const uint32_t *)(const void *)(msg + 4u);
    if (msg[2] == 0x21u) {
        const uint8_t connection = (uint8_t)*(const uint16_t *)(const void *)msg;
        uint8_t *const ccb = audio_ble_att_registration_lookup(connection, msg[8]);
        if (ccb == 0) {
            WsfMsgFree(packet);
        } else if (audio_ble_atts_pend_ind_ntf_5338ac(ccb, packet) != 0u) {
            const uint16_t handle = *(const uint16_t *)(const void *)(packet + 2u);
            audio_ble_atts_exec_callback_533934(connection, handle, 0x72u);
            WsfMsgFree(packet);
        } else {
            audio_ble_atts_setup_msg_5339ac(ccb, connection, msg[8], packet);
        }
    } else if (msg[2] == 0x22u) {
        uint8_t connection = 0u;
        uint8_t slot = 0u;
        audio_ble_att_decode_msg_param_4b50fe(
            *(const uint16_t *)(const void *)msg, &connection, &slot);
        *(uint16_t *)(void *)msg = connection;
        (void)audio_ble_att_registration_lookup(connection, slot);
    }
}
