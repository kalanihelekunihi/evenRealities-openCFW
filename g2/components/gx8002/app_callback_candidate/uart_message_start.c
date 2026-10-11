/* Native control-flow projection of XIP 0x10207adc..0x10207b32.
 * Lower call names identify ABI boundaries rather than guessed effects.
 * Callback identity is now a source relocation to the selected C provider.
 */
#include <stdint.h>
#include <stddef.h>
extern uint32_t *g2_codec_channel_lookup(uint32_t channel);
extern uint32_t g2_codec_queue_is_empty(void *queue); /* 0x10206ffc */
extern uint32_t g2_codec_queue_read(void *queue, void *destination); /* 0x10206fb0 */
extern uint32_t g2_codec_channel_stop(uint32_t channel); /* 0x10203664 */
extern uint32_t g2_codec_channel_timer_start(uint32_t timer); /* 0x102077a8 */
extern uint32_t g2_codec_channel_callback_set(uint32_t channel,
                                         uintptr_t callback, uint32_t argument); /* 0x10203630 */
extern uint32_t gx8002_xip_uart_send_callback_10207f08(uint32_t, uint32_t);
uint32_t g2_codec_uart_message_start(uint32_t channel_index)
{
    volatile uint32_t *const channel = g2_codec_channel_lookup(channel_index);
    if (channel == NULL) return UINT32_MAX;
    void *const queue = (uint8_t *)(uintptr_t)channel + 348;
    const uint32_t empty = g2_codec_queue_is_empty(queue);
    if (empty != 0) {
        channel[6] = 0;
        g2_codec_channel_stop(channel_index);
        return UINT32_MAX;
    }
    channel[6] = 1;
    (void)g2_codec_queue_read(queue, (uint8_t *)(uintptr_t)channel + 60);
    channel[93] = empty;
    const uint32_t timer = channel[94];
    g2_codec_channel_timer_start(timer);
    const uint32_t channel_number = channel[2];
    g2_codec_channel_callback_set(channel_number,
        (uintptr_t)gx8002_xip_uart_send_callback_10207f08, empty);
    return empty;
}

uint32_t gx8002_xip_uart_message_start_10207adc(uint32_t channel_index)
{
    return g2_codec_uart_message_start(channel_index);
}
