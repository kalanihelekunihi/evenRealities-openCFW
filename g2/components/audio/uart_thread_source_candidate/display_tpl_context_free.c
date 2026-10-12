/* Native tpl_context_free 0x4b8ba2. The context is a 56-byte TPL row. */
#include <stdint.h>
extern uint32_t audio_event_loop_remove_delayed(void (*callback)(void)); /* selected 0x476ace */
extern void audio_tpl_rx_next_packet_timeout(const uint8_t *); /* native callback 0x4b8c6c */
extern void audio_file_heap_free(void *); /* selected native 0x474d16 */
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t); /* selected 0x43c0e4 */

void tpl_context_free_004b8ba2(uint8_t *context)
{
    if (context == 0 || context[0x30u] == 0u) return;
    (void)audio_event_loop_remove_delayed((void (*)(void))audio_tpl_rx_next_packet_timeout);
    uint32_t buffer;
    __builtin_memcpy(&buffer, context + 8u, 4u);
    if (buffer != 0u) {
        audio_file_heap_free((void *)(uintptr_t)buffer);
        buffer = 0u;
        __builtin_memcpy(context + 8u, &buffer, 4u);
    }
    context[0x30u] = 0u;
    audio_uart_buffer_zero(context, 0x32u, 0u);
}
