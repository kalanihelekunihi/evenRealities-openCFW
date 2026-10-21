/* Native setting_handle_device_receive_info 0x466abc..0x466bec. */
#include <stdint.h>
extern void audio_setting_dispatch_type1_466bec(void *);
extern void audio_setting_dispatch_type2_466e1c(uint32_t);
extern void audio_setting_dispatch_type3_466ea2(uint32_t);
extern void audio_setting_dispatch_type4_466f28(void *);
extern void audio_setting_dispatch_type5_467134(uint32_t);
extern void audio_setting_dispatch_type6_46713e(uint32_t);
extern void audio_setting_dispatch_type8_4671a2(uint32_t);
extern void audio_setting_dispatch_type9_467206(void *);
extern void audio_setting_dispatch_type10_467308(void *);
extern void audio_setting_dispatch_type11_467540(void *);
extern void audio_setting_dispatch_type12_467c34(void *);
extern void SVC_Settings_SaveSettingConfigToKVCheck(void);
extern void audio_uart_ring_unpair_commit_hand_466016(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="setting";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\setting\\setting.c";
static const char function[]="setting_handle_device_receive_info";
static const char null_message[]="pMessage is NULL";
static const char null_short[]="[setting]pMessage is NULL";
static const char unknown[]="Unknown setting type: %d";
static const char unknown_short[]="[setting]Unknown setting type: %d";
static uint16_t load16(const uint8_t *p) {return (uint16_t)p[0]|((uint16_t)p[1]<<8);}
static uint32_t load32(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
void audio_setting_dispatch_message_466abc(uint8_t *message) {
    if(message==0) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,0x9du,null_message);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08000000u,null_short,null_short);
        return;
    }
    uint16_t type=load16(message+12u);
    uint8_t *field=message+16u;
    switch(type) {
    case 1u:audio_setting_dispatch_type1_466bec(field);break;
    case 2u:audio_setting_dispatch_type2_466e1c(load32(field));break;
    case 3u:audio_setting_dispatch_type3_466ea2(load32(field));break;
    case 4u:audio_setting_dispatch_type4_466f28(field);break;
    case 5u:audio_setting_dispatch_type5_467134(load32(field));break;
    case 6u:audio_setting_dispatch_type6_46713e(load32(field));break;
    case 7u:break;
    case 8u:audio_setting_dispatch_type8_4671a2(load32(field));break;
    case 9u:audio_setting_dispatch_type9_467206(field);break;
    case 10u:audio_setting_dispatch_type10_467308(field);break;
    case 11u:audio_setting_dispatch_type11_467540(field);break;
    case 12u:audio_setting_dispatch_type12_467c34(field);break;
    default:
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,0xe0u,unknown,type);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08400000u,unknown_short,unknown_short,type);
        break;
    }
    SVC_Settings_SaveSettingConfigToKVCheck();
    audio_uart_ring_unpair_commit_hand_466016();
}
