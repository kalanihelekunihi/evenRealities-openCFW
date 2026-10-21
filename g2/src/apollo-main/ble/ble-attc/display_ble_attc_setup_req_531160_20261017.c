/* Cordio attcSetupReq at stock Main 0x531160. */
#include <stdint.h>

extern void audio_ble_attc_send_req_531144(uint8_t *);

void audio_ble_attc_setup_req_531160(uint8_t *ccb, const uint8_t *message)
{
    for (uint32_t index = 0u; index < 12u; ++index)
        ccb[4u + index] = message[index];

    const uint8_t *packet = *(const uint8_t *const *)(message + 4u);
    const uint8_t *parameters = packet;
    if (message[2u] == 11u)
        parameters = *(const uint8_t *const *)packet;
    for (uint32_t index = 0u; index < 8u; ++index)
        ccb[0x10u + index] = parameters[index];

    audio_ble_attc_send_req_531144(ccb);
}
