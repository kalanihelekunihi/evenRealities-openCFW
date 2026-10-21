/* Native WsfMsgDataAlloc 0x4bf990 and hciCoreConnByHandle 0x52a704. */
#include <stdint.h>
extern uint8_t audio_ble_hci_controller_state_20071478[];
extern void *audio_wsf_msg_alloc(uint16_t); /* selected WsfMsgAlloc 0x4bf99e */

void *audio_ble_hci_msg_data_alloc(uint16_t length, uint8_t prefix) {
    return audio_wsf_msg_alloc((uint16_t)(length+(uint8_t)prefix));
}
uint8_t *audio_ble_hci_conn_by_handle(uint16_t handle) {
    uint8_t *row=audio_ble_hci_controller_state_20071478;
    for(uint32_t i=0;i<3u;i++,row+=0x1cu) {
        uint16_t stored;
        __builtin_memcpy(&stored,row+0x10u,2u);
        if(stored==handle)return row;
    }
    return 0;
}
