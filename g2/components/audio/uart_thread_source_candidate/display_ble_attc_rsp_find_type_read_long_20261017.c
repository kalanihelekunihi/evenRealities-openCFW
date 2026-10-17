/* Cordio attcProcFindByTypeRsp 0x56c3b0 and attcProcReadLongRsp 0x56c454. */
#include <stdint.h>

typedef struct {
    uint16_t param;
    uint8_t event;
    uint8_t status;
    const uint8_t *value;
    uint16_t value_length;
    uint16_t handle;
    uint8_t continuing;
} audio_attc_read_event_t;

static uint16_t read16(const uint8_t *data)
{
    return (uint16_t)data[0] | ((uint16_t)data[1] << 8);
}

static void write16(uint8_t *data, uint16_t value)
{
    data[0] = (uint8_t)value;
    data[1] = (uint8_t)(value >> 8);
}

void audio_attc_rsp_find_type_56c3b0(uint8_t *ccb, uint16_t length,
                                     const uint8_t *packet,
                                     audio_attc_read_event_t *event)
{
    const uint8_t *cursor = packet + 9u;
    const uint8_t *end = packet + 8u + length;
    uint16_t next = read16(ccb + 0x12u);
    const uint16_t maximum = read16(ccb + 0x14u);
    while (cursor < end) {
        const uint16_t start_handle = read16(cursor);
        const uint16_t end_handle = read16(cursor + 2u);
        cursor += 4u;
        if (start_handle > end_handle || start_handle < next ||
            start_handle > maximum || next == 0u) {
            event->status = 0x73u;
            break;
        }
        next = end_handle == 0xffffu ? 0u : (uint16_t)(end_handle + 1u);
        if (cursor > end) {
            event->status = 0x73u;
            break;
        }
    }
    if (event->status == 0u && ccb[7u] == 1u) {
        if (next == 0u || next > maximum) {
            ccb[7u] = 0u;
        } else {
            write16(ccb + 0x12u, next);
            write16(ccb + 0x0cu, next);
        }
    }
}

void audio_attc_rsp_read_long_56c454(uint8_t *ccb, uint16_t length,
                                     const uint8_t *packet,
                                     audio_attc_read_event_t *event)
{
    (void)packet;
    if (ccb[7u] != 1u)
        return;
    const uint8_t *main_ccb = *(uint8_t **)ccb;
    const uint16_t mtu = read16(main_ccb + (uint32_t)ccb[0x28u] * 4u);
    if (length < mtu)
        ccb[7u] = 0u;
    else
        write16(ccb + 0x12u, (uint16_t)(read16(ccb + 0x12u) + event->value_length));
}
