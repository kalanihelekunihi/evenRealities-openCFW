/* Native setting_notify_device_status_to_app 0x49be04. */
#include <stdint.h>
extern uint8_t audio_uart_device_role_get(void); /* selected 0x45a568 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* 0x48949c -> selected 0x43c0e4 */
extern uint32_t audio_settings_build_full_status(uint8_t *); /* native 0x49b4da */
extern uint32_t audio_settings_notify_common(uint8_t *); /* native 0x49bbfc */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="pb_service_setting";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_setting\\pb_service_setting.c";
static const char function[]="setting_notify_device_status_to_app";
static const char not_master[]="not master role, not send";
static const char not_master_short[]="[pb_service_setting]not master role, not send";
static const char build_failed[]="Failed to build status package";
static const char build_failed_short[]="[pb_service_setting]Failed to build status package";
uint32_t audio_settings_notify_device_status(void) {
    if(audio_uart_device_role_get()!=1u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(4u,module,path,function,400u,not_master);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x10000000u,not_master_short,not_master_short);
        return 0u;
    }
    uint8_t packet[104];
    audio_uart_buffer_zero(packet,104u,0u);
    if(audio_settings_build_full_status(packet)==0u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,407u,build_failed);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04000000u,build_failed_short,build_failed_short);
        return 43u;
    }
    return audio_settings_notify_common(packet);
}
