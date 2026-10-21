/* Native Cordio AttcReadReq 0x4b575a and AttcWriteReq 0x4b579c. */
#include <stdint.h>
extern void *audio_ble_att_message_allocate_4b50ae(uint16_t);
extern void audio_ble_attc_send_message_4b5640(uint8_t,uint16_t,uint8_t,void *,uint8_t);
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);

void audio_ble_attc_read_request(uint8_t connection,uint16_t handle) {
    uint8_t *packet=(uint8_t *)audio_ble_att_message_allocate_4b50ae(11u);
    if(packet==0)return;
    packet[0]=3u;packet[1]=0u;
    packet[8]=10u;packet[9]=(uint8_t)handle;packet[10]=(uint8_t)(handle>>8);
    audio_ble_attc_send_message_4b5640(connection,handle,5u,packet,0u);
}

void audio_ble_attc_write_request(uint8_t connection,uint16_t handle,
                                   uint16_t length,const uint8_t *value) {
    uint8_t *packet=(uint8_t *)audio_ble_att_message_allocate_4b50ae((uint16_t)(length+11u));
    if(packet==0)return;
    const uint16_t payload_length=(uint16_t)(length+3u);
    packet[0]=(uint8_t)payload_length;packet[1]=(uint8_t)(payload_length>>8);
    packet[8]=0x12u;packet[9]=(uint8_t)handle;packet[10]=(uint8_t)(handle>>8);
    (void)audio_queue_copy_bytes(packet+11u,value,length);
    audio_ble_attc_send_message_4b5640(connection,handle,9u,packet,0u);
}

void audio_ble_attc_find_info_request_4b571e(uint8_t connection,uint16_t start,
                                               uint16_t end,uint8_t option) {
    uint8_t *packet=(uint8_t *)audio_ble_att_message_allocate_4b50ae(13u);
    if(packet==0)return;
    packet[0]=5u;packet[1]=0u;
    packet[2]=(uint8_t)start;packet[3]=(uint8_t)(start>>8);
    packet[4]=(uint8_t)end;packet[5]=(uint8_t)(end>>8);
    packet[8]=4u;
    audio_ble_attc_send_message_4b5640(connection,start,2u,packet,option);
}
