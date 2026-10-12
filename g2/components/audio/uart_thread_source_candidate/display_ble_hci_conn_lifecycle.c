/* Native hciCoreConnAlloc/Free 0x52a67c/0x52a6b0 and open/close wrappers. */
#include <stdint.h>
extern uint8_t audio_ble_hci_controller_state_20071478[]; /* live connection rows */
extern void audio_ble_wsf_message_free(void *); /* selected WsfMsgFree */
extern void audio_ble_hci_tx_ready(uint8_t); /* native 0x52a79e */
static uint16_t rd16(const uint8_t *p) {uint16_t v;__builtin_memcpy(&v,p,2u);return v;}
static uint32_t rd32(const uint8_t *p) {uint32_t v;__builtin_memcpy(&v,p,4u);return v;}
static void wr16(uint8_t *p,uint16_t v) {__builtin_memcpy(p,&v,2u);}
static void wr32(uint8_t *p,uint32_t v) {__builtin_memcpy(p,&v,4u);}
void audio_ble_hci_conn_alloc(uint16_t handle) {
    uint8_t *row=audio_ble_hci_controller_state_20071478;
    for(uint32_t i=0;i<3u;i++,row+=0x1cu) {
        if(rd16(row+0x10u)!=0xffffu)continue;
        wr16(row+0x10u,handle);
        row[0x17u]=0u;row[0x18u]=0u;row[0x19u]=0u;
        return;
    }
}
void audio_ble_hci_conn_free(uint16_t handle) {
    uint8_t *row=audio_ble_hci_controller_state_20071478;
    for(uint32_t i=0;i<3u;i++,row+=0x1cu) {
        if(rd16(row+0x10u)!=handle)continue;
        uint32_t queue=rd32(row);
        if(queue!=0u) {audio_ble_wsf_message_free((void *)(uintptr_t)queue);wr32(row,0u);}
        row[0x16u]=0u;
        uint32_t fragment=rd32(row+8u);
        if(fragment!=0u) {audio_ble_wsf_message_free((void *)(uintptr_t)fragment);wr32(row+8u,0u);}
        wr16(row+0x10u,0xffffu);
        audio_ble_hci_tx_ready(row[0x19u]);
        return;
    }
}
void audio_ble_hci_conn_open(uint16_t handle) {audio_ble_hci_conn_alloc(handle);}
void audio_ble_hci_conn_close(uint16_t handle) {audio_ble_hci_conn_free(handle);}
