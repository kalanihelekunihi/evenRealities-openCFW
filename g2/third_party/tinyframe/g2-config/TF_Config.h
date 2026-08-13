#ifndef OPEN_CFW_TINYFRAME_G2_CONFIG_H
#define OPEN_CFW_TINYFRAME_G2_CONFIG_H

#include <stdint.h>

/* Recovered from the official G2 2.2.6.10 Apollo-main image. */
#define TF_ID_BYTES 2
#define TF_LEN_BYTES 2
#define TF_TYPE_BYTES 2

#define TF_CKSUM_TYPE TF_CKSUM_CRC16
#define TF_USE_SOF_BYTE 1
#define TF_SOF_BYTE 0x01

typedef uint16_t TF_TICKS;
typedef uint8_t TF_COUNT;

#define TF_MAX_PAYLOAD_RX 0x6000
#define TF_SENDBUF_LEN 0x400

#define TF_MAX_ID_LST 128
#define TF_MAX_TYPE_LST 32
#define TF_MAX_GEN_LST 10

#define TF_PARSER_TIMEOUT_TICKS 100
#define TF_USE_MUTEX 0

/*
 * This is a port seam, not upstream TinyFrame. Production admission must bind
 * it to the reviewed G2 logger adapter without importing application policy
 * into the authenticated upstream snapshot.
 */
void open_cfw_tinyframe_error(const char *format, ...);
#define TF_Error(format, ...) \
    open_cfw_tinyframe_error((format), ##__VA_ARGS__)

#endif
