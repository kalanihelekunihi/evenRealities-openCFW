/* Native service settings auto brightness open/close 0x46c01c/0x46c0e8. */
#include <stdint.h>
extern uint32_t audio_uart_command_pending(void); /* selected productModeGet 0x4abe60 */
extern uint8_t audio_uart_device_role_get(void); /* selected 0x45a568 */
extern volatile uint8_t audio_uart_auto_brightness_enabled_cell; /* RAM 0x20072daa */
extern int32_t HUB_Open(uint8_t func_type); /* 0x4a6d58 */
extern int32_t HUB_Close(uint8_t func_type); /* 0x4a6dca */
extern uint32_t audio_log_flags(void); /* selected 0x43d0ce */
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...); /* selected 0x43d574 */
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...); /* selected 0x43ce9e */
static const char module[]="service.settings";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\settings\\service_settings.c";
static const char open_function[]="SVC_Settings_AutoBrightnessOpen";
static const char close_function[]="SVC_Settings_AutoBrightnessClose";
static const char disabled[]="auto brightness disabled";
static const char open_wrong_role[]="not master role, not open auto brightness";
static const char close_wrong_role[]="not master role, not close auto brightness";
static const char disabled_short[]="[service.settings]auto brightness disabled";
static const char open_wrong_role_short[]="[service.settings]not master role, not open auto brightness";
static const char close_wrong_role_short[]="[service.settings]not master role, not close auto brightness";
static void log_message(const char *function,uint32_t line,
                        const char *full,const char *short_text) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,line,full);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10000000u,short_text,short_text);
}
uint32_t SVC_Settings_AutoBrightnessOpen(void) {
    if(audio_uart_command_pending()==1u) return 0;
    if(audio_uart_auto_brightness_enabled_cell==0u) {
        log_message(open_function,390u,disabled,disabled_short);
        return 0;
    }
    if(audio_uart_device_role_get()==1u) {
        (void)HUB_Open(4u);
    } else {
        log_message(open_function,395u,open_wrong_role,open_wrong_role_short);
    }
    return 0;
}
uint32_t SVC_Settings_AutoBrightnessClose(void) {
    if(audio_uart_command_pending()==1u) return 0;
    if(audio_uart_device_role_get()==1u) {
        (void)HUB_Close(4u);
    } else {
        log_message(close_function,410u,close_wrong_role,close_wrong_role_short);
    }
    return 0;
}
