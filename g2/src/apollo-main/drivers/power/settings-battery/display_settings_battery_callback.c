/* Native SVC_Settings_BatteryCallback 0x46b3e4. */
#include <stdint.h>
extern uint8_t audio_settings_config_live[]; /* RAM 0x20072da8, >=64 bytes */
extern uint32_t audio_settings_charge_percent(void); /* native CHG_GetSoc 0x4ad8fa */
extern uint32_t audio_settings_is_charging(void); /* native CHG_GetIsCharging 0x4ad900 */
extern uint32_t audio_settings_notify_device_status(void); /* native 0x49be04 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="service.settings";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\settings\\service_settings.c";
static const char function[]="SVC_Settings_BatteryCallback";
static const char message[]="battery callback: data is NULL";
static const char short_message[]="[service.settings]battery callback: data is NULL";
void SVC_Settings_BatteryCallback(uint32_t event,void *data) {
    if(data==0) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(4u,module,path,function,116u,message);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x10000000u,short_message,short_message);
    } else if(event<=1u) {
        *(uint32_t *)(void *)(audio_settings_config_live+0x38u)=audio_settings_charge_percent();
        *(uint32_t *)(void *)(audio_settings_config_live+0x3cu)=audio_settings_is_charging();
        (void)audio_settings_notify_device_status();
    }
}
