/* Native setting type-12 app-control route 0x467c34..0x467d52. */
#include <stdint.h>
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern uint32_t audio_log_wake_allowed(void);
extern uint32_t audio_uart_service_mode(void);
extern void audio_setting_display_start_466890(void);
static const char module[]="setting";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\setting\\setting.c";
static const char function[]="setting_handle_app_control_device";
static const char null_message[]="control_data is NULL";
static const char null_compact[]="[setting]control_data is NULL";
static const char received[]="Received app control device, turn_on_device=%d";
static const char received_compact[]="[setting]Received app control device, turn_on_device=%d";
static const char start[]="Device not running, start background app";
static const char start_compact[]="[setting]Device not running, start background app";
static const char running[]="Device already running, ignore turn_on request";
static const char running_compact[]="[setting]Device already running, ignore turn_on request";
static void log_line(uint8_t level,uint32_t line,const char *message,
                     const char *compact,uint32_t mask,uint32_t value,uint32_t with_value) {
    if((audio_log_flags()&2u)!=0u) {
        if(with_value!=0u)audio_log_extended(level,module,path,function,line,message,value);
        else audio_log_extended(level,module,path,function,line,message);
    }
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u) {
        if(with_value!=0u)(void)compressed_log_output(mask,compact,compact,value);
        else (void)compressed_log_output(mask,compact,compact);
    }
}
void audio_setting_dispatch_type12_467c34(const uint32_t *control_data) {
    if(control_data==0) {
        log_line(2u,0x2b3u,null_message,null_compact,0x08000000u,0u,0u);
        return;
    }
    uint32_t turn_on=*control_data;
    log_line(4u,0x2b7u,received,received_compact,0x10400000u,turn_on,1u);
    if(turn_on!=1u)return;
    if(audio_log_wake_allowed()==0u) {
        if((uint8_t)audio_uart_service_mode()!=1u)return;
        log_line(3u,0x2bdu,start,start_compact,0x0c000000u,0u,0u);
        audio_setting_display_start_466890();
    } else {
        log_line(4u,0x2c1u,running,running_compact,0x10000000u,0u,0u);
    }
}
