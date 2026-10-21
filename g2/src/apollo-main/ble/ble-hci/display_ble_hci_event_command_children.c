/* Native hciEvtProcessCmdStatus 0x56b150 and hciCoreNumCmplPkts 0x530c08. */
#include <stdint.h>
extern uint8_t audio_ble_hci_stack_state_20073870[]; /* live 0x20073870 */
extern uint8_t audio_ble_hci_controller_state_20071478[]; /* live 0x20071478 */
extern uint8_t *audio_ble_hci_conn_by_handle(uint16_t); /* selected 0x52a704 */
extern void audio_ble_hci_cmd_status_failure(uint32_t,uint32_t); /* 0x56b100 */
extern void audio_ble_hci_cmd_receive_complete(uint32_t); /* 0x52aef8 */
extern void audio_ble_hci_tx_ready(uint8_t); /* 0x52a79e */

static uint16_t rd16(const uint8_t *p) { return (uint16_t)((uint16_t)p[0]|((uint16_t)p[1]<<8)); }
static uint32_t rd32(const uint8_t *p) { uint32_t v;__builtin_memcpy(&v,p,4u);return v; }
void audio_ble_hci_event_cmd_status(const void *parameters) {
    const uint8_t *p=(const uint8_t *)parameters;
    if(p[0]!=0u)audio_ble_hci_cmd_status_failure(p[0],rd16(p+2u));
    audio_ble_hci_cmd_receive_complete(p[1]);
}
void audio_ble_hci_num_complete_packets(const void *parameters) {
    const uint8_t *p=(const uint8_t *)parameters;
    uint8_t rows=*p++;
    uint8_t total=0u;
    for(uint8_t i=0;i<rows;i++,p+=4u) {
        uint16_t handle=rd16(p);
        uint8_t count=p[2];
        uint8_t *conn=audio_ble_hci_conn_by_handle(handle);
        if(conn==0)continue;
        conn[0x19u]=(uint8_t)(conn[0x19u]-count);
        conn[0x18u]=(uint8_t)(conn[0x18u]-count);
        total=(uint8_t)(total+count);
        if(conn[0x17u]!=0u && conn[0x18u]<=audio_ble_hci_controller_state_20071478[0x81u]) {
            conn[0x17u]=0u;
            uint32_t callback=rd32(audio_ble_hci_stack_state_20073870+0x14u);
            ((void (*)(uint32_t,uint32_t))(uintptr_t)callback)(handle,0u);
        }
    }
    audio_ble_hci_tx_ready(total);
}
