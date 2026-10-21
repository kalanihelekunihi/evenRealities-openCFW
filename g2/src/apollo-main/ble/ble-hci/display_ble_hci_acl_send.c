/* Native HciSendAclData 0x52ad04. HCI controller state and stack callbacks
 * are existing typed live RAM objects with selected producer routines. */
#include <stdint.h>
extern uint8_t audio_ble_hci_controller_state_20071478[];
extern uint8_t audio_ble_hci_stack_state_20073870[];
extern uint8_t *audio_ble_hci_conn_by_handle(uint16_t);
extern void audio_ble_wsf_message_free(void *);
extern void WsfMsgEnq(void *,uint8_t,void *);
extern uint16_t WsfQueueCount(const void *);
extern void audio_ble_hci_tx_ready(uint8_t);
extern uint16_t audio_ble_hci_get_buf_size(void);
static uint16_t rd16(const uint8_t *p){return (uint16_t)p[0]|((uint16_t)p[1]<<8);}
static uint32_t rd32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
void HciSendAclData(void *packet_void){
    uint8_t *packet=(uint8_t *)packet_void;
    const uint16_t handle=rd16(packet);
    const uint16_t length=rd16(packet+2u);
    uint8_t *conn=audio_ble_hci_conn_by_handle(handle);
    if(conn==0){audio_ble_wsf_message_free(packet);return;}
    uint8_t *state=audio_ble_hci_controller_state_20071478;
    uint8_t *queue=state+0x70u;
    WsfMsgEnq(queue,0u,packet);
    if(WsfQueueCount(queue)==1u&&state[0x82u]!=0u)audio_ble_hci_tx_ready(0u);
    const uint16_t buffer_size=audio_ble_hci_get_buf_size();
    const int32_t extra=(int32_t)(uint32_t)length-1;
    conn[0x18u]=(uint8_t)((int32_t)conn[0x18u]+extra/(int32_t)buffer_size+1);
    if(state[0x80u]<=conn[0x18u]&&conn[0x17u]==0u){
        conn[0x17u]=1u;
        const uint32_t callback=rd32(audio_ble_hci_stack_state_20073870+0x14u);
        ((void (*)(uint16_t,uint8_t))(uintptr_t)callback)(handle,1u);
    }
}
