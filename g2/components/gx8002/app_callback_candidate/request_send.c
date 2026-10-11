/* Complete control-flow C projection of XIP 0x102083bc..0x10208458.
 * Native instructions correct unsigned channel byte and low-halfword count
 * loads lost by historical decompilation. Typed queue/ROM/CRC/device lowers
 * remain external; this is not an implementation of their hardware effects.
 */
#include "request.h"
uint32_t *g2_codec_channel_lookup(uint32_t channel)
{
    if (channel == 0) {
        return (uint32_t *)(uintptr_t)UINT32_C(0x2002e050);
    }
    if (channel == 1) {
        return (uint32_t *)(uintptr_t)UINT32_C(0x2002e1cc);
    }
    return NULL;
}
extern uint32_t g2_codec_queue_is_full(void *queue); /* 0x10207008 */
extern uint32_t crc32(uint32_t seed, const unsigned char *data, unsigned int bytes);
uint32_t g2_codec_crc32(uint32_t seed, const void *data, uint32_t bytes)
{
    return crc32(seed, data, bytes);
}
extern void g2_codec_header_sync(void *header, uint32_t bytes); /* ROM 0x10025664 */
extern uint32_t g2_codec_queue_enqueue(void *queue, const void *request); /* ROM 0x100261b8 */
extern uint32_t g2_codec_uart_message_start(uint32_t channel); /* 0x10207adc */

uint32_t g2_codec_request_consume(g2_codec_request *request)
{
    volatile g2_codec_request *const header = request;
    const uint8_t channel_index = *(const volatile uint8_t *)((const uint8_t *)request + 20);
    uint32_t *const channel = g2_codec_channel_lookup(channel_index);
    if (channel == NULL || channel[3] == 0) {
        return UINT32_MAX;
    }
    if (header->count != 0 && header->payload == NULL) {
        return UINT32_MAX;
    }
    void *const queue = (uint8_t *)channel + 348;
    if (g2_codec_queue_is_full(queue) != 0) {
        return UINT32_MAX;
    }
    const uint8_t has_extra = header->flag != 0;
    const uint16_t low_count = *(const volatile uint16_t *)((const uint8_t *)request + 24);
    header->encoded_length = (uint16_t)(low_count + (has_extra ? 4u : 0u));
    if (header->prefix == 0) {
        header->prefix = channel[0];
    }
    if ((header->request_code & UINT16_C(0xff00)) != UINT16_C(0x200)) {
        volatile uint8_t *const sequence = (uint8_t *)channel + 20;
        const uint8_t old_sequence = *sequence;
        *sequence = (uint8_t)(old_sequence + 1u);
        header->sequence = old_sequence;
    }
    const uint32_t crc = g2_codec_crc32(0, request, 10);
    header->crc_low = (uint16_t)crc;
    header->crc_high = (uint16_t)(crc >> 16);
    g2_codec_header_sync(request, 16);
    if (g2_codec_queue_enqueue(queue, request) == 0) {
        return UINT32_MAX;
    }
    if (channel[6] == 0) {
        g2_codec_uart_message_start(*(const volatile uint8_t *)((const uint8_t *)channel + 8));
    }
    return 0;
}
