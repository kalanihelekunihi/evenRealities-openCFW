/* Native hciCmdSend 0x52ae5e and WsfMsgPeek 0x4bfa00. */
#include <stdint.h>
extern uint8_t audio_ble_hci_cmd_state_20073a90[]; /* live */
extern void audio_wsf_msg_enqueue(void *,uint8_t,void *); /* selected WsfMsgEnq */
extern void *audio_ble_wsf_message_dequeue(void *,uint8_t *); /* selected WsfMsgDeq */
extern void audio_ble_wsf_message_free(void *); /* selected WsfMsgFree */
extern void audio_ble_hci_timer_start_sec(void *,uint32_t); /* native 0x52a4b8 */
extern uint32_t audio_ble_hci_transport_send_cmd(const void *); /* native 0x530166 */

static uint16_t rd16(const uint8_t *p) {return (uint16_t)((uint16_t)p[0]|((uint16_t)p[1]<<8));}
static void wr16(uint8_t *p,uint16_t v) {__builtin_memcpy(p,&v,2u);}
void *audio_ble_wsf_message_peek(void *queue,uint8_t *handler) {
    uint8_t *head=*(uint8_t **)queue;
    if(head==0)return 0;
    *handler=head[4u];
    return head+8u;
}
uint64_t audio_ble_hci_cmd_send_body(void *message,uint32_t unused,
                                     uint32_t scratch,uint32_t high) {
    (void)unused;(void)high;
    uint8_t *state=audio_ble_hci_cmd_state_20073a90;
    uint8_t *queue=state+0x10u;
    if(message!=0)audio_wsf_msg_enqueue(queue,0u,message);
    if(state[0x1au]!=0u) {
        uint8_t handler;
        uint8_t *next=(uint8_t *)audio_ble_wsf_message_peek(queue,&handler);
        if(next!=0) {
            scratch=(scratch&~0xffu)|handler;
            wr16(state+0x18u,rd16(next));
            audio_ble_hci_timer_start_sec(state,10u);
            if(audio_ble_hci_transport_send_cmd(next)==1u) {
                (void)audio_ble_wsf_message_dequeue(queue,&handler);
                scratch=(scratch&~0xffu)|handler;
                state[0x1au]--;
                audio_ble_wsf_message_free(next);
                return ((uint64_t)scratch<<32)|1u;
            }
        }
    }
    return (uint64_t)scratch<<32;
}
__attribute__((naked)) uint64_t audio_ble_hci_cmd_send(void *message) {
    __asm volatile("b audio_ble_hci_cmd_send_body");
}
