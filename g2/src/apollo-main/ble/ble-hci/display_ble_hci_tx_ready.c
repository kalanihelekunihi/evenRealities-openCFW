/* Native hciCoreTxReady 0x52a79e; live HCI ACL credit/queue state. */
#include <stdint.h>
extern uint8_t audio_ble_hci_controller_state_20071478[];
extern void *audio_ble_wsf_message_peek(void *,uint8_t *); /* selected 0x4bfa00 */
extern void *audio_ble_wsf_message_dequeue(void *,uint8_t *); /* selected 0x4bf9ec */
extern void audio_ble_wsf_message_free(void *); /* selected 0x4bf9b0 */
extern uint8_t *audio_ble_hci_conn_by_handle(uint16_t); /* selected 0x52a704 */
extern uint32_t audio_ble_hci_tx_acl_continue(void *); /* native 0x52a8b0 */
extern uint32_t audio_ble_hci_tx_acl_start(void *,uint16_t,void *); /* native 0x52a850 */
extern void audio_ble_hci_tx_acl_complete(void *,void *); /* native 0x52a936 */
static uint16_t rd16(const uint8_t *p) {return (uint16_t)((uint16_t)p[0]|((uint16_t)p[1]<<8));}
uint64_t audio_ble_hci_tx_ready_body(uint8_t credit,uint32_t unused,
                                     uint32_t scratch,uint32_t high) {
    (void)unused;(void)high;
    uint8_t *state=audio_ble_hci_controller_state_20071478;
    uint8_t sent=0u;
    if(credit!=0u) {
        state[0x82u]=(uint8_t)(state[0x82u]+credit);
        if(state[0x82u]>state[0x83u])state[0x82u]=state[0x83u];
    }
    while(state[0x82u]!=0u) {
        if(audio_ble_hci_tx_acl_continue(0)!=0u)continue;
        uint8_t *queue=state+0x70u;
        uint8_t handler;
        uint8_t *message=(uint8_t *)audio_ble_wsf_message_peek(queue,&handler);
        if(message==0)break;
        scratch=(scratch&~0xffu)|handler;
        uint16_t handle=rd16(message);
        uint16_t length=rd16(message+2u);
        uint8_t *conn=audio_ble_hci_conn_by_handle(handle);
        if(conn==0) {
            void *removed=audio_ble_wsf_message_dequeue(queue,&handler);
            scratch=(scratch&~0xffu)|handler;
            audio_ble_wsf_message_free(removed);
        } else {
            if(audio_ble_hci_tx_acl_start(conn,length,message)!=1u)break;
            (void)audio_ble_wsf_message_dequeue(queue,&handler);
            scratch=(scratch&~0xffu)|handler;
            audio_ble_hci_tx_acl_complete(conn,message);
            sent=1u;
        }
    }
    return ((uint64_t)scratch<<32)|sent;
}
__attribute__((naked)) uint64_t audio_ble_hci_tx_ready(uint8_t credit) {
    __asm volatile("b audio_ble_hci_tx_ready_body");
}
