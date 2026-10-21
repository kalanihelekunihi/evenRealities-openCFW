/* Native SVC_Settings_DumpSettingConfig 0x46b458. Diagnostics read the live
 * 0x20072da8 settings record; no settings value or startup state is invented.
 * Native's inherited extra register on the first no-format-argument banner
 * is not consumed by either authenticated format string. */
#include <stdint.h>
extern uint8_t audio_settings_config_live[];
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char*,const char*,const char*,uint32_t,const char*,...);
extern uint32_t compressed_log_output(uint32_t,const char*,const char*,...);
static const char module[]="service.settings";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\settings\\service_settings.c";
static const char function_name[]="SVC_Settings_DumpSettingConfig";
static const char *const extended[]={
 "========settings=========","record_version: %d","brightness_level: %d",
 "auto_brightness_enabled: %d","y_coordinate_level: %d","x_coordinate_level: %d",
 "head_up_switch: %d","head_up_angle: %d","wear_detection_switch: %d",
 "silent_mode_switch: %d","left_brightness_calibration_level: %d",
 "right_brightness_calibration_level: %d","head_up_angle_calibration: %d",
 "record_check: 0x%04x","terminal_mode: %d","als scale_q10: %d",
 "========================="};
static const char *const compact[]={
 "[service.settings]========settings=========","[service.settings]record_version: %d",
 "[service.settings]brightness_level: %d","[service.settings]auto_brightness_enabled: %d",
 "[service.settings]y_coordinate_level: %d","[service.settings]x_coordinate_level: %d",
 "[service.settings]head_up_switch: %d","[service.settings]head_up_angle: %d",
 "[service.settings]wear_detection_switch: %d","[service.settings]silent_mode_switch: %d",
 "[service.settings]left_brightness_calibration_level: %d",
 "[service.settings]right_brightness_calibration_level: %d",
 "[service.settings]head_up_angle_calibration: %d","[service.settings]record_check: 0x%04x",
 "[service.settings]terminal_mode: %d","[service.settings]als scale_q10: %d",
 "[service.settings]========================="};
static uint32_t word(const uint8_t *p) {return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static uint32_t half(const uint8_t *p) {return (uint32_t)p[0]|((uint32_t)p[1]<<8);}
void SVC_Settings_DumpSettingConfig(void) {
    const uint8_t *p=audio_settings_config_live;
    const uint8_t off[]={0,0,1,2,8,9,10,12,20,21,22,23,16,24,29,36,0};
    for(uint32_t i=0;i<17u;i++) {
        uint32_t v=0;
        if(i==7u||i==12u||i==15u) v=word(p+off[i]);
        else if(i==13u) v=half(p+off[i]);
        else if(i!=0u&&i!=16u) v=p[off[i]];
        if(audio_log_flags()&2u) {
            if(i==0u||i==16u) audio_log_extended(3u,module,source,function_name,0xaau+i,extended[i]);
            else audio_log_extended(3u,module,source,function_name,0xaau+i,extended[i],v);
        }
        if((audio_log_flags()&1u)||(audio_log_flags()&4u)) {
            uint32_t flags=(i==0u||i==16u)?0xc000000u:0xc400000u;
            if(i==0u||i==16u) (void)compressed_log_output(flags,compact[i],compact[i]);
            else (void)compressed_log_output(flags,compact[i],compact[i],v);
        }
    }
}
