/* Native Cordio AttcReadByTypeReq at 0x56c4ee.  The allocator owns a
 * length+13 buffer; only the fields written by stock are initialized here. */
#include <stdint.h>
extern void *audio_ble_hci_msg_data_alloc(uint16_t,uint8_t); /* selected 0x4bf990 */
extern void audio_ble_attc_send_message_4b5640(uint8_t,uint16_t,uint8_t,void *,uint8_t);
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected 0x439be4 */
void *audio_ble_att_message_allocate_4b50ae(uint16_t length) {
    return audio_ble_hci_msg_data_alloc(length,0u);
}
void audio_ble_attc_read_by_type_56c4ee(uint8_t connection,uint16_t start,
                                          uint16_t end,uint8_t uuid_length,
                                          const uint8_t *uuid,uint32_t option) {
    uint8_t *packet=(uint8_t *)audio_ble_att_message_allocate_4b50ae((uint16_t)(uuid_length+13u));
    if(packet==0)return;
    *(uint16_t *)(void *)(packet+0u)=(uint16_t)(uuid_length+5u);
    *(uint16_t *)(void *)(packet+2u)=start;
    *(uint16_t *)(void *)(packet+4u)=end;
    packet[8u]=8u;
    (void)audio_queue_copy_bytes(packet+13u,uuid,uuid_length);
    audio_ble_attc_send_message_4b5640(connection,start,4u,packet,(uint8_t)option);
}
