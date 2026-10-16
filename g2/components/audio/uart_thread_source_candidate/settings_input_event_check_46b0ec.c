/* Native SVC_Settings_InputEventCheck 0x46b0ec..0x46b238, wear gate 0x49eb96. */
#include <stdint.h>
extern uint32_t audio_uart_command_pending(void); /* stock 0x4abe60 */
extern uint32_t audio_ota_transfer_active(void); /* stock 0x4487ac */
extern uint32_t audio_wear_detect_get_enable_49ead8(void);
extern volatile uint32_t audio_uart_lcd_status_cell;
extern uint32_t audio_uart_case_status(void); /* stock 0x4acad0 */
extern uint8_t *audio_settings_get_config_46b44c(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="service.settings";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\settings\\service_settings.c";
static const char function[]="SVC_Settings_InputEventCheck";
static const char ota[]="OTA is going, input event not allowed";
static const char ota_short[]="[service.settings]OTA is going, input event not allowed";
static const char wear[]="wear detect input not enabled, input event not allowed";
static const char wear_short[]="[service.settings]wear detect input not enabled, input event not allowed";
static const char in_box[]="glasses in box, input event not allowed";
static const char in_box_short[]="[service.settings]glasses in box, input event not allowed";
static const char silent[]="silent mode, input event not allowed";
static const char silent_short[]="[service.settings]silent mode, input event not allowed";
__attribute__((noinline)) uint32_t audio_wear_input_enabled_49eb96(void) {
    if(audio_wear_detect_get_enable_49ead8()==0u)return 1u;
    return audio_uart_lcd_status_cell==2u;
}
static uint32_t denied(uint32_t line,const char *message,const char *short_message) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(2u,module,path,function,line,message);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x08000000u,short_message,short_message);
    return 0u;
}
uint32_t audio_wear_child_46b0ec(void) {
    if(audio_uart_command_pending()==1u)return 1u;
    if(audio_ota_transfer_active()!=0u)return denied(0x24u,ota,ota_short);
    if(audio_wear_input_enabled_49eb96()==0u)return denied(0x2au,wear,wear_short);
    if(audio_uart_case_status()==1u)return denied(0x30u,in_box,in_box_short);
    if(audio_settings_get_config_46b44c()[0x15u]==1u)
        return denied(0x36u,silent,silent_short);
    return 1u;
}
