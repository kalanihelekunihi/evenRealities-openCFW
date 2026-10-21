/* Native 0x4b9984: cancel the shared delayed callback, then release each
 * active row in the authenticated four-by-56-byte TPL context pool. */
#include <stdint.h>

extern uint8_t audio_tpl_contexts[4u * 56u];
extern uint32_t audio_event_loop_remove_delayed(void (*callback)(void));
extern void audio_tpl_rx_next_packet_timeout(const uint8_t *);
extern void tpl_context_free_004b8ba2(uint8_t *);

void tpl_reset_receive_contexts_004b9984(void)
{
    (void)audio_event_loop_remove_delayed((void (*)(void))audio_tpl_rx_next_packet_timeout);
    for (uint32_t i = 0u; i < 4u; ++i) {
        uint8_t *row = audio_tpl_contexts + i * 56u;
        if (row[0x30u] != 0u) tpl_context_free_004b8ba2(row);
    }
}
