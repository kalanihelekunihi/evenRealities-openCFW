/* Native HCI ACL connection selection and transport 0x52a72e/0x52a76c/
 * 0x53013c/0x530d34. 0x52ae14 and 0x530d68 both point at live 0x20071478. */
#include <stdint.h>
extern uint8_t audio_ble_hci_controller_state_20071478[];
extern uint32_t audio_ble_hci_driver_write(uint32_t,uint16_t,const void *);

uint16_t audio_ble_hci_get_buf_size(void) {
    uint8_t *p=audio_ble_hci_controller_state_20071478+0x7eu;
    return (uint16_t)((uint16_t)p[0]|((uint16_t)p[1]<<8));
}

uint8_t *audio_ble_hci_next_conn_fragment(void) {
    uint8_t *record=audio_ble_hci_controller_state_20071478;
    for(uint32_t i=0u;i<3u;i++,record+=0x1cu) {
        if(!(record[0x10u]==0xffu&&record[0x11u]==0xffu)&&record[0x16u]!=0u)
            return record;
    }
    return 0;
}

uint16_t audio_ble_hci_transport_send_acl(void *record,const void *packet) {
    (void)record;
    const uint8_t *p=(const uint8_t *)packet;
    uint16_t size=(uint16_t)((uint16_t)p[2u]|((uint16_t)p[3u]<<8));
    size=(uint16_t)(size+4u);
    return audio_ble_hci_driver_write(2u,size,p)==size?size:0u;
}

uint32_t audio_ble_hci_send_acl_data(void *record,void *packet) {
    uint8_t *conn=(uint8_t *)record;
    if(audio_ble_hci_transport_send_acl(record,packet)==0u)return 0u;
    conn[0x19u]=(uint8_t)(conn[0x19u]+1u);
    uint8_t *state=audio_ble_hci_controller_state_20071478;
    if(state[0x82u]!=0u)state[0x82u]=(uint8_t)(state[0x82u]-1u);
    return 1u;
}
