/* Native tpl_schedule_rx_timeout 0x4b8c44. The three-byte argument cell is
 * live transport RAM at 0x20074b04; its producer and full extent are open. */
#include <stdint.h>

extern uint8_t audio_tpl_timeout_ids[];
extern void audio_tpl_rx_next_packet_timeout(const uint8_t *);
extern uint32_t audio_event_loop_remove_delayed(void (*callback)(void));
extern uint32_t audio_event_loop_push_delayed(void (*callback)(void), void *, uint32_t);

void audio_tpl_schedule_rx_timeout_body(uint32_t service, uint32_t sync,
                                        uint32_t pipe)
{
    (void)audio_event_loop_remove_delayed((void (*)(void))audio_tpl_rx_next_packet_timeout);
    audio_tpl_timeout_ids[2] = (uint8_t)service;
    audio_tpl_timeout_ids[0] = (uint8_t)sync;
    audio_tpl_timeout_ids[1] = (uint8_t)pipe;
    (void)audio_event_loop_push_delayed((void (*)(void))audio_tpl_rx_next_packet_timeout,
                                        audio_tpl_timeout_ids, 1500u);
}

/* The original pop returns the incoming fourth register word in R0. */
__attribute__((naked)) uint32_t tpl_schedule_rx_timeout_004b8c44(
    uint8_t service __attribute__((unused)), uint8_t sync __attribute__((unused)),
    uint8_t pipe __attribute__((unused)), uint32_t inherited __attribute__((unused)))
{
    __asm__ volatile(
        "push {r3, r4, r5, r6, r7, lr}\n"
        "bl audio_tpl_schedule_rx_timeout_body\n"
        "pop {r0, r4, r5, r6, r7, pc}\n");
}
