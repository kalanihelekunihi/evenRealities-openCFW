/* Cordio attcSendReq at stock Main 0x531144. */
#include <stdint.h>

extern void audio_ble_attc_send_simple_530e30(uint8_t *);
extern void audio_ble_attc_send_continuing_530e64(uint8_t *);
extern void audio_ble_attc_send_mtu_530f08(uint8_t *);
extern void audio_ble_attc_send_write_cmd_531054(uint8_t *);
extern void audio_ble_attc_send_prepare_write_531088(uint8_t *);

typedef void (*audio_attc_send_handler_t)(uint8_t *);
static const audio_attc_send_handler_t handlers[17] = {
    0, audio_ble_attc_send_mtu_530f08,
    audio_ble_attc_send_continuing_530e64,
    audio_ble_attc_send_continuing_530e64,
    audio_ble_attc_send_continuing_530e64,
    audio_ble_attc_send_simple_530e30,
    audio_ble_attc_send_continuing_530e64,
    audio_ble_attc_send_simple_530e30,
    audio_ble_attc_send_continuing_530e64,
    audio_ble_attc_send_simple_530e30,
    audio_ble_attc_send_write_cmd_531054,
    audio_ble_attc_send_prepare_write_531088,
    audio_ble_attc_send_simple_530e30,
    0, 0, 0, audio_ble_attc_send_simple_530e30,
};

void audio_ble_attc_send_req_531144(uint8_t *ccb)
{
    const uint8_t request = ccb[6u];
    if (request < 17u && handlers[request] != 0)
        handlers[request](ccb);
}
