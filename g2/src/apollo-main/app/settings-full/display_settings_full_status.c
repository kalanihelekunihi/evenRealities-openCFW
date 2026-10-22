/* Native setting_build_full_status_package 0x49b4da, 104-byte layout. */
#include <stdint.h>
extern uint8_t audio_settings_config_live[]; /* RAM 0x20072da8, >=0x4f bytes */
extern uint8_t audio_settings_last_message_state[]; /* RAM 0x20072608 */
extern const uint8_t audio_settings_right_version_text[11]; /* ROM 0x78b7bc */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
extern void *audio_settings_copy_text(void *,const void *,uint32_t); /* selected 0x44b5a0 */
extern void audio_settings_request_left_version(void); /* native 0x46ba02 */
extern uint32_t audio_settings_unread_message_count(void); /* native 0x4974d4 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="pb_service_setting";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_setting\\pb_service_setting.c";
static const char function[]="setting_build_full_status_package";
static const char null_message[]="pPackage is NULL";
static const char null_short[]="[pb_service_setting]pPackage is NULL";
static const char auto_message[]="auto_brightness_switch:%d, auto_brightness_level:%d, y_coordinate_level:%d, x_coordinate_level:%d";
static const char auto_short[]="[pb_service_setting]auto_brightness_switch:%d, auto_brightness_level:%d, y_coordinate_level:%d, x_coordinate_level:%d";
static const char left_empty[]="left version empty, request from slave";
static const char left_empty_short[]="[pb_service_setting]left version empty, request from slave";
static const char version_message[]="left_version: %s, right_version: %s";
static const char version_short[]="[pb_service_setting]left_version: %s, right_version: %s";
static const char head_message[]="head_up_switch:%d, head_up_angle:%d, head_up_angle_calibration:%d";
static const char head_short[]="[pb_service_setting]head_up_switch:%d, head_up_angle:%d, head_up_angle_calibration:%d";
static const char device_message[]="device_is_running:%d, battery_level:%d, charge_status:%d, silent_mode_switch:%d";
static const char device_short[]="[pb_service_setting]device_is_running:%d, battery_level:%d, charge_status:%d, silent_mode_switch:%d";
static const char unread_message[]="unread_message_count: %d";
static const char unread_short[]="[pb_service_setting]unread_message_count: %d";
static uint16_t half(const uint8_t *p) {return (uint16_t)p[0]|((uint16_t)p[1]<<8);}
static uint32_t word(const uint8_t *p) {return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void store32(uint8_t *p,uint32_t v) {p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);p[2]=(uint8_t)(v>>16);p[3]=(uint8_t)(v>>24);}
/* Stock 0x49B4DA (setting_build_full_status_package) */
uint32_t audio_settings_build_full_status(uint8_t *packet) {
    if(packet==0) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,171u,null_message);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04000000u,null_short,null_short);
        return 0u;
    }
    audio_uart_buffer_zero(packet,104u,0u);
    packet[0]=2u;
    packet[8]=4u;
    if(half(audio_settings_last_message_state+8u)==4u)
        packet[12]=audio_settings_last_message_state[12];
    uint8_t *config=audio_settings_config_live;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,191u,auto_message,config[2],config[1],config[8],config[9]);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x11000000u,auto_short,auto_short,config[2],config[1],config[8],config[9]);
    store32(packet+0x60u,config[2]);
    store32(packet+0x10u,config[1]);
    store32(packet+0x14u,config[8]);
    store32(packet+0x18u,config[9]);
    (void)audio_settings_copy_text(packet+0x28u,audio_settings_right_version_text,11u);
    uint8_t *left_version=config+0x44u;
    if(left_version[0]==0u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,209u,left_empty);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08000000u,left_empty_short,left_empty_short);
        audio_settings_request_left_version();
    } else (void)audio_settings_copy_text(packet+0x1cu,left_version,11u);
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,216u,version_message,packet+0x1cu,packet+0x28u);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10800000u,version_short,version_short,packet+0x1cu,packet+0x28u);
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,219u,head_message,config[10],word(config+0x0cu),word(config+0x10u));
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10c00000u,head_short,head_short,config[10],word(config+0x0cu),word(config+0x10u));
    store32(packet+0x34u,config[10]);
    store32(packet+0x38u,word(config+0x0cu));
    store32(packet+0x40u,config[0x14u]);
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,225u,device_message,word(config+0x34u),word(config+0x38u),word(config+0x3cu),config[0x15u]);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x11000000u,device_short,device_short,word(config+0x34u),word(config+0x38u),word(config+0x3cu),config[0x15u]);
    store32(packet+0x44u,word(config+0x34u));
    store32(packet+0x48u,word(config+0x38u));
    store32(packet+0x4cu,word(config+0x3cu));
    store32(packet+0x50u,config[0x15u]);
    store32(packet+0x54u,config[0x16u]);
    store32(packet+0x58u,config[0x17u]);
    store32(packet+0x5cu,word(config+0x40u));
    uint32_t unread=audio_settings_unread_message_count();
    store32(packet+0x64u,unread);
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,241u,unread_message,unread);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10400000u,unread_short,unread_short,unread);
    return 1u;
}
