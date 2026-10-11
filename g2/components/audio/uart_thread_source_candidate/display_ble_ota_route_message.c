/* Native Cordio OTA route-message producer 0x4b6c82. */
#include <stdint.h>
extern void *audio_wsf_msg_alloc(uint16_t);
extern void audio_wsf_msg_send(uint8_t,void *);
extern uint8_t audio_ble_ota_route_context[]; /* live struct 0x20073b78 */
void audio_ble_ota_connection_route(uint32_t channel,uint8_t connection,uint32_t subtype) {
    uint8_t *message=(uint8_t *)audio_wsf_msg_alloc(0x24u);
    if(!message)return;
    *(uint16_t *)(void *)message=(uint16_t)connection;
    message[2]=0x19u;
    message[4]=(uint8_t)subtype;
    message[3]=message[4];
    message[5]=(uint8_t)channel;
    audio_wsf_msg_send(audio_ble_ota_route_context[12],message);
}
