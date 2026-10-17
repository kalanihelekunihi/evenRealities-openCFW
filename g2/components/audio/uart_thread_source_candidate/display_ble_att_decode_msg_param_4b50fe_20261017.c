/* Cordio attDecodeMsgParam, stock 0x4b50fe..0x4b511e. */
#include <stdint.h>

void audio_ble_att_decode_msg_param_4b50fe(uint16_t encoded,
                                             uint8_t *connection,
                                             uint8_t *slot)
{
    *slot = (uint8_t)(encoded % 3u);
    *connection = (uint8_t)(encoded / 3u);
}
