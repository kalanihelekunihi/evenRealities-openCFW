/* Native SVC_Settings_RequestLeftVersion 0x46ba02, 500-tick rate limit. */
#include <stdint.h>
extern uint8_t audio_settings_config_live[]; /* RAM 0x20072da8 */
extern uint32_t audio_settings_left_version_last_request_tick; /* RAM 0x20074994 */
extern uint8_t audio_uart_device_role_get(void); /* selected 0x45a568 */
extern uint32_t g2_flashdb_candidate_tick(void); /* selected osKernelGetTickCount 0x4490cc */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
extern int32_t audio_settings_send_peer_packet(uint16_t,const void *,uint32_t,uint32_t,uint32_t); /* 0x465480 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="service.settings";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\settings\\service_settings.c";
static const char function[]="SVC_Settings_RequestLeftVersion";
static const char request_message[]="request left version from slave";
static const char request_short[]="[service.settings]request left version from slave";
static const char fail_message[]="request left version send failed, ret=%d, will retry on next trigger";
static const char fail_short[]="[service.settings]request left version send failed, ret=%d, will retry on next trigger";
void audio_settings_request_left_version(void) {
    if(audio_uart_device_role_get()!=1u||audio_settings_config_live[0x44u]!=0u) return;
    uint32_t now=g2_flashdb_candidate_tick();
    uint32_t previous=audio_settings_left_version_last_request_tick;
    if(previous!=0u&&(uint32_t)(now-previous)<500u) return;
    uint8_t packet[48];
    audio_uart_buffer_zero(packet,48u,0u);
    packet[0]=3u;
    int32_t status=audio_settings_send_peer_packet(9u,packet,48u,0u,5u);
    if(status==0) {
        audio_settings_left_version_last_request_tick=now;
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,247u,request_message);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0c000000u,request_short,request_short);
    } else {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,243u,fail_message,status);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08400000u,fail_short,fail_short,status);
    }
}
