/* APP_BleSlaveAdvStartEvent native 0x46ee70. */
#include <stdint.h>
extern uint8_t *audio_ble_profile_connection_context; /* pointer cell 0x2007432c */
extern void *audio_wsf_msg_alloc(uint16_t);
extern void audio_wsf_msg_send(uint8_t,void *);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
void audio_ble_phone_advertising_restart(void) {
    uint8_t *message=(uint8_t *)audio_wsf_msg_alloc(12u);
    if(message==0) return;
    message[2]=0xb6u;
    *(uint16_t *)(void *)message=0xffu;
    audio_wsf_msg_send(audio_ble_profile_connection_context[0x56u],message);
    if(audio_log_level()&2u)
      audio_log_extended(3u,"ble.Slave",
        "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_peripheral.c",
        "APP_BleSlaveAdvStartEvent",0x28cu,"EVEN_SLAVE_ADV_AGAIN_EVT sent");
    if((audio_log_level()&1u)||(audio_log_level()&4u))
      (void)compressed_log_output(0x0c000000u,
        "[ble.Slave]EVEN_SLAVE_ADV_AGAIN_EVT sent",
        "[ble.Slave]EVEN_SLAVE_ADV_AGAIN_EVT sent");
}
