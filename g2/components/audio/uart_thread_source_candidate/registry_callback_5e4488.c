/* Apollo registry callback 0x5e4488, row 0x30.
 * Native RAM locations 0x2010f4cc and 0x2010fd1c require final placement. */
#include <stdint.h>

extern uint8_t audio_registry_ring_connect_buffer[]; /* native 0x2010f4cc */
extern uint8_t audio_registry_ring_connect_state;    /* native 0x2010fd1c */
extern uint32_t audio_registry_ring_connect_enter_5e438e(uint32_t event);
extern uint32_t audio_registry_ring_connect_parse_5ce990(const void *,uint16_t,
                                                          uint8_t *);
extern uint32_t audio_registry_ring_connect_notify_5ceaec(uint8_t *,uint32_t);
extern uint32_t audio_registry_ring_connect_check_5e4604(const uint8_t *);
extern void audio_registry_ring_connect_leave_5e43be(void);

uint32_t audio_uart_registry_callback_5e4488(uint32_t event,
                                               const void *payload,
                                               uint32_t length) {
    (void)audio_registry_ring_connect_enter_5e438e(event);
    if(event==0u) {
        uint32_t status=audio_registry_ring_connect_parse_5ce990(
            payload,(uint16_t)length,audio_registry_ring_connect_buffer);
        if(status==13u) audio_registry_ring_connect_state=0u;
        else if(status!=0u) audio_registry_ring_connect_state=1u;
        else audio_registry_ring_connect_state=
            (uint8_t)(audio_registry_ring_connect_check_5e4604(
                audio_registry_ring_connect_buffer)!=0u);
        (void)audio_registry_ring_connect_notify_5ceaec(
            &audio_registry_ring_connect_state,audio_registry_ring_connect_buffer[1]);
    }
    audio_registry_ring_connect_leave_5e43be();
    return 0u;
}
