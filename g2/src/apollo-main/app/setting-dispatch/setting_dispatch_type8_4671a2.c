/* Native setting type-8 advanced-feature route 0x4671a2..0x467206. */
#include <stdint.h>
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern uint32_t audio_uart_service_mode(void); /* stock 0x45a570 */
extern void audio_system_alert_close_464c36(uint32_t,uint32_t,uint32_t,uint32_t);
static const char module[]="setting";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\setting\\setting.c";
static const char function[]="setting_handle_advanced_setting";
static const char message[]="advanced_setting is valid, kill_all_feature = %d";
static const char compact[]="[setting]advanced_setting is valid, kill_all_feature = %d";
void audio_setting_dispatch_type8_4671a2(uint32_t value) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,0x1d6u,message,value);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10400000u,compact,compact,value);
    if(value==1u && (uint8_t)audio_uart_service_mode()==1u)
        audio_system_alert_close_464c36(0u,0u,0u,0u);
}
