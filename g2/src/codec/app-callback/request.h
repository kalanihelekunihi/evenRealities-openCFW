#ifndef OPENCFW_CODEC_REQUEST_CANDIDATE_H
#define OPENCFW_CODEC_REQUEST_CANDIDATE_H
#include <stddef.h>
#include <stdint.h>
typedef struct {
    uint32_t prefix;
    uint16_t request_code;
    uint8_t sequence;
    uint8_t flag;
    uint16_t encoded_length;
    uint16_t crc_low;
    uint16_t crc_high;
    uint16_t unowned_0e;
    const uint8_t *payload;
    uint32_t channel;
    uint32_t count;
} g2_codec_request;
_Static_assert(offsetof(g2_codec_request, request_code) == 4, "request code offset");
_Static_assert(offsetof(g2_codec_request, flag) == 7, "flag offset");
_Static_assert(offsetof(g2_codec_request, encoded_length) == 8, "length offset");
_Static_assert(offsetof(g2_codec_request, crc_low) == 10, "CRC low offset");
_Static_assert(offsetof(g2_codec_request, crc_high) == 12, "CRC high offset");
_Static_assert(offsetof(g2_codec_request, payload) == 16, "payload offset");
_Static_assert(offsetof(g2_codec_request, channel) == 20, "channel offset");
_Static_assert(offsetof(g2_codec_request, count) == 24, "count offset");
_Static_assert(sizeof(g2_codec_request) == 28, "request size");
uint32_t g2_codec_request_consume(g2_codec_request *request);
#endif
