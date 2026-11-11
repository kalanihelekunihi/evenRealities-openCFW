/* Native tpl_schedule_rx_timeout 0x4b8c44. The three-byte argument cell is
 * live transport RAM at 0x20074b04; its producer and full extent are open. */
#include <stdint.h>

extern uint8_t audio_tpl_timeout_ids[];
extern void audio_tpl_rx_next_packet_timeout(const uint8_t *);
extern uint32_t audio_event_loop_remove_delayed(void (*callback)(void));
extern uint32_t audio_event_loop_push_delayed(void (*callback)(void), void *, uint32_t);

/* Stock 0x4B8C44 (tpl_schedule_rx_timeout). The stock epilogue popped the
 * caller's R3 into R0; every caller (transport_protocol_rx.c) declares it
 * void, so it returns nothing. */
void tpl_schedule_rx_timeout_004b8c44(uint8_t service, uint8_t sync, uint8_t pipe)
{
    (void)audio_event_loop_remove_delayed((void (*)(void))audio_tpl_rx_next_packet_timeout);
    audio_tpl_timeout_ids[2] = service;
    audio_tpl_timeout_ids[0] = sync;
    audio_tpl_timeout_ids[1] = pipe;
    (void)audio_event_loop_push_delayed((void (*)(void))audio_tpl_rx_next_packet_timeout,
                                        audio_tpl_timeout_ids, 1500u);
}
