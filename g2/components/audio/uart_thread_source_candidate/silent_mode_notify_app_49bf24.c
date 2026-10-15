/* Native notify_silent_mode_to_app 0x49bf24. */
#include <stdint.h>
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern uint32_t audio_settings_notify_common(uint8_t *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="pb_service_setting";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_setting\\pb_service_setting.c";
static const char function[]="notify_silent_mode_to_app";
static const char message[]="just notify silent mode to app = %d";
static const char compact[]="[pb_service_setting]just notify silent mode to app = %d";

void audio_silent_mode_notify_app(uint32_t enabled) {
    uint8_t packet[104];
    audio_uart_buffer_zero(packet,104u,0u);
    packet[0]=3u;
    packet[8]=5u;
    packet[12]=2u;
    packet[16]=(uint8_t)enabled;
    packet[17]=0u;
    packet[18]=0u;
    packet[19]=0u;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,0x1bdu,message,(uint8_t)enabled);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10400000u,compact,compact,(uint8_t)enabled);
    (void)audio_settings_notify_common(packet);
}
