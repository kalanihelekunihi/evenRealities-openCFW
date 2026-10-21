/* Native WearDetect_GetEnable 0x49ead8 and WearDetect_SetEnable 0x49eb1e. */
#include <stdint.h>
extern uint8_t *audio_settings_get_config_46b44c(void);
extern volatile uint32_t audio_uart_lcd_status_cell;
extern uint32_t audio_wear_detect_handle_status_change_49ebb6(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="wear.detect";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\ux\\ux_wear_detect\\ux_wear_detect.c";
static const char function[]="WearDetect_SetEnable";
static const char message[]="wear detect enable=%d";
static const char short_message[]="[wear.detect]wear detect enable=%d";
uint32_t audio_wear_detect_get_enable_49ead8(void) {
    return audio_settings_get_config_46b44c()[0x14u];
}
void audio_wear_detect_set_enable_49eb1e(uint32_t requested) {
    uint32_t enable=(uint8_t)requested;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0x42u,message,enable);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c400000u,short_message,short_message,enable);
    if(enable!=audio_wear_detect_get_enable_49ead8()) {
        audio_settings_get_config_46b44c()[0x14u]=enable;
        audio_wear_detect_handle_status_change_49ebb6((uint8_t)audio_uart_lcd_status_cell);
    }
}
