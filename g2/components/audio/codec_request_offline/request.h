#ifndef CODEC_REQUEST_OFFLINE_H
#define CODEC_REQUEST_OFFLINE_H
#include <stdint.h>
/* No capacity argument exists in stock packer; caller must provide backing storage.
 * Normal payload limits: 16 without CRC, 12 with CRC. Malformed length wrapping
 * is preserved for evidence and is not a safe application-facing API. */
int32_t codec_pack(uint16_t,uint16_t,const uint8_t *,uint16_t,uint8_t,uint8_t *,uint16_t *);
int32_t codec_uart_tx(const uint8_t *,uint32_t);
int32_t codec_send(uint16_t,uint16_t,const uint8_t *,uint16_t,uint8_t);
uint32_t codec_channel_tx(uint32_t,const uint8_t *,uint32_t);
#endif
