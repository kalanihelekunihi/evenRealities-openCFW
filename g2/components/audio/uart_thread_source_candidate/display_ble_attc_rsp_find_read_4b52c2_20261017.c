/* Cordio attcProcFindOrReadRsp; stock Main entry 0x4b52c2. */
#include <stdint.h>

static uint16_t read16(const uint8_t *p)
{
    return (uint16_t)p[0] | ((uint16_t)p[1] << 8);
}

void audio_attc_rsp_find_read_4b52c2(uint8_t *ccb, uint16_t len,
                                      const uint8_t *packet, uint8_t *event)
{
    const uint8_t *p = packet + 9u;
    const uint8_t *end = packet + 8u + len;
    uint8_t param_len;
    if (ccb[6] == 2u) {
        param_len = (*p++ == 1u) ? 2u : 16u;
    } else if (ccb[6] == 4u) {
        param_len = (uint8_t)(*p++ - 2u);
    } else {
        param_len = (uint8_t)(*p++ - 4u);
    }
    uint16_t next = read16(ccb + 0x12u);
    while (p < end) {
        uint16_t handle = read16(p);
        p += 2u;
        if (handle == 0u || next == 0u || handle < next ||
            handle > read16(ccb + 0x14u)) {
            event[3] = 0x73u;
            break;
        }
        if (ccb[6] == 8u) {
            const uint16_t previous = handle;
            handle = read16(p);
            p += 2u;
            if (handle == 0u || handle < previous || handle < next ||
                handle > read16(ccb + 0x14u)) {
                event[3] = 0x73u;
                break;
            }
        }
        next = (uint16_t)(handle + 1u);
        p += param_len;
        if (p > end) {
            event[3] = 0x73u;
            break;
        }
    }
    if (event[3] == 0u && ccb[7] == 1u) {
        if (next == 0u || next == (uint32_t)read16(ccb + 0x14u) + 1u) {
            ccb[7] = 0u;
        } else {
            ccb[0x12] = (uint8_t)next;
            ccb[0x13] = (uint8_t)(next >> 8);
            ccb[0x0c] = (uint8_t)next;
            ccb[0x0d] = (uint8_t)(next >> 8);
        }
    }
}
