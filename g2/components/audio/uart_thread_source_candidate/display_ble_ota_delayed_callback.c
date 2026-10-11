/* Native OTA delayed reset callback 0x4bdb38, referenced by ROM 0x4bde24. */
#include <stdint.h>
extern uint8_t audio_ble_ota_handler_state[4];
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern void *audio_wsf_msg_alloc(uint16_t);
extern void audio_wsf_msg_send(uint8_t,void *);
static const char module[]="profile.ota";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\profiles\\ota\\profile_ota.c";
static const char function[]="_evenOtaReset";
static const char message[]="evenOta_reset_board";
static const char short_message[]="[profile.ota]evenOta_reset_board";
void audio_ble_ota_delayed_callback(void) {
    if(audio_log_level()&2u)
        audio_log_extended(4u,module,path,function,0x43u,message);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x10000000u,short_message,short_message);
    uint8_t *event=(uint8_t *)audio_wsf_msg_alloc(12u);
    if(event) {
        event[2]=0xa0u;
        *(uint16_t *)(void *)event=(uint16_t)audio_ble_ota_handler_state[0];
        audio_wsf_msg_send(audio_ble_ota_handler_state[1],event);
    }
}
