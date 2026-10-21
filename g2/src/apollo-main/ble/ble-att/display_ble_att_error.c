/* Native Cordio ATT error wrapper 0x533934 and callback packet 0x4b5074. */
#include <stdint.h>
extern uint8_t audio_ble_att_runtime[]; /* live struct 0x200610ac */
static void put_half(uint8_t *p,uint16_t v) {p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);}
void audio_ble_att_report_error(uint8_t connection,uint8_t event,uint16_t attribute,
                                uint8_t reason,uint16_t extra) {
    void (*callback)(void *);
    __builtin_memcpy(&callback,audio_ble_att_runtime+0x58u,sizeof(callback));
    if(!callback)return;
    uint8_t packet[16]; /* Native leaves bytes 4..7 and 13 as stack scratch. */
    put_half(packet,connection);
    packet[2]=event;
    packet[3]=reason;
    put_half(packet+8u,0u);
    put_half(packet+10u,attribute);
    packet[12]=0u;
    put_half(packet+14u,extra);
    callback(packet);
}
void audio_ble_att_send_error(uint8_t connection,uint16_t attribute,uint8_t reason) {
    audio_ble_att_report_error(connection,0x12u,attribute,reason,0u);
}
