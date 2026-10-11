/* Native 0x46be7c and 0x448e34: changed-settings CRC and event request. */
#include <stdint.h>
extern uint8_t audio_settings_config_live[]; /* 26-byte CRC prefix, larger RAM object at 0x20072da8 */
extern uint8_t *audio_settings_config_previous; /* pointer cell RAM 0x20003700 */
extern uint32_t g2_audio_log_event_handle; /* shared handle cell RAM 0x20074570 */
extern uint32_t g2_log_event_set_task(uint32_t,uint32_t); /* selected CMSIS 0x4495e4 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="service.settings";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\settings\\service_settings.c";
static const char function[]="SVC_Settings_SaveSettingConfigToKVCheck";
static const char message[]="setting config changed, send kv write event";
static const char short_message[]="[service.settings]setting config changed, send kv write event";

/* Stock table at 0x6c0b50 is the non-reflected CCITT 0x1021 recurrence. */
static uint16_t crc16_24(const uint8_t *bytes) {
    uint16_t crc=0xffffu;
    for(unsigned i=0;i<24u;i++) {
        crc^=(uint16_t)bytes[i]<<8;
        for(unsigned bit=0;bit<8u;bit++)
            crc=(uint16_t)((crc<<1)^((crc&0x8000u)?0x1021u:0u));
    }
    return crc;
}
void audio_settings_signal_save(void) {
    uint32_t event=g2_audio_log_event_handle;
    if(event!=0) (void)g2_log_event_set_task(event,4u);
}
void SVC_Settings_SaveSettingConfigToKVCheck(void) {
    uint16_t crc=crc16_24(audio_settings_config_live);
    audio_settings_config_live[24]=(uint8_t)crc;
    audio_settings_config_live[25]=(uint8_t)(crc>>8);
    uint8_t *previous=audio_settings_config_previous;
    uint16_t old=(uint16_t)previous[24]|((uint16_t)previous[25]<<8);
    if(old!=crc) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(4u,module,path,function,341u,message);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x10000000u,short_message,short_message);
        audio_settings_signal_save();
    }
}
