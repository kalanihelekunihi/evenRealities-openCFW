/* Native setting type-2 Y 0x466e1c and type-3 X 0x466ea2 routes. */
#include <stdint.h>
extern uint8_t *audio_settings_get_config_46b44c(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern uint32_t audio_log_wake_allowed(void);
extern uint32_t audio_uart_service_mode(void);
extern void audio_setting_display_start_466890(void);
extern void audio_dashboard_auto_close_reset_49c0dc(void);
extern void audio_uart_master_input_event(uint32_t,uint32_t,uint32_t,uint32_t);
static const char module[]="setting";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\setting\\setting.c";
static const char y_function[]="setting_handle_y_coordinate_setting";
static const char x_function[]="setting_handle_x_coordinate_setting";
static const char y_message[]="set y_coordinate_level = %d";
static const char x_message[]="set x_coordinate_level = %d";
static const char y_compact[]="[setting]set y_coordinate_level = %d";
static const char x_compact[]="[setting]set x_coordinate_level = %d";
static void display_update(void) {
    if(audio_log_wake_allowed()==0u) {
        if((uint8_t)audio_uart_service_mode()==1u)
            audio_setting_display_start_466890();
    } else {
        audio_dashboard_auto_close_reset_49c0dc();
    }
}
void audio_setting_dispatch_type2_466e1c(uint32_t value) {
    audio_settings_get_config_46b44c()[8]=(uint8_t)value;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,y_function,0x12cu,y_message,value);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c400000u,y_compact,y_compact,value);
    display_update();
    if((uint8_t)audio_uart_service_mode()==1u)
        audio_uart_master_input_event(6u,0x0bu,value,0u);
}
void audio_setting_dispatch_type3_466ea2(uint32_t value) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,x_function,0x14au,x_message,value);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c400000u,x_compact,x_compact,value);
    audio_settings_get_config_46b44c()[9]=(uint8_t)value;
    display_update();
    if((uint8_t)audio_uart_service_mode()==1u)
        audio_uart_master_input_event(6u,0x0cu,value,0u);
}
