#ifndef CODEC_RESPONSE_OFFLINE_H
#define CODEC_RESPONSE_OFFLINE_H
#include <stdint.h>
/* ARM packed message layout: header0..13, owned pointer14..17,
 * body length18..19, body CRC20..23, total wire length24..25. */
uint32_t codec_crc32(const uint8_t *,uint32_t,const uint32_t *previous);
int32_t codec_unpack(const uint8_t *,uint16_t,uint8_t message[26]);
void codec_message_free(uint8_t message[26]);
int32_t codec_response_read(uint8_t *,uint16_t,uint32_t ticks);
int32_t codec_read_uart_data(uint8_t *,uint16_t,uint16_t *,uint32_t ticks);
#endif
