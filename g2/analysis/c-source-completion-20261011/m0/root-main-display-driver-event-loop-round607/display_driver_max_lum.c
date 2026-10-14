/* Apollo settings maximum luminance 0x46c23c..0x46c3ff. Candidate. */
#include <stdint.h>
extern void audio_uart_checksum_copy(void *,const void *,uint32_t); /* selected 0x439c04 */
extern uint8_t *display_driver_brightness_ratio_cell_4af73a(uint32_t); /* getter pending */
extern uint8_t audio_uart_device_role_get(void); /* selected 0x45a568 */
extern uint8_t audio_settings_config_live[]; /* selected SRAM 0x20072da8 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const float ratios[11]={
 0x1.1f268ap-1f,0x1.3bd152p-1f,0x1.5714fep-1f,0x1.702416p-1f,
 0x1.876b32p-1f,0x1.9e802ep-1f,0x1.b3c462p-1f,0x1.c790dcp-1f,
 0x1.db4b52p-1f,0x1.ecf776p-1f,0x1.000000p+0f};
_Static_assert(sizeof ratios==44u,"ROM ratio table size");
static const char module[]="service.settings";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\settings\\service_settings.c";
static const char function[]="SVC_Settings_GetMaxLum";
static const char index_text[]="brightness_ratio_index: %d";
static const char index_compact[]="[service.settings]brightness_ratio_index: %d";
static const char role_text[]="GetMaxLum: role not ready(%d), force calibration_level=0 to avoid wrong-eye dimming";
static const char role_compact[]="[service.settings]GetMaxLum: role not ready(%d), force calibration_level=0 to avoid wrong-eye dimming";
static const char final_text[]="GetMaxLum: eye=%s panel_current=%d ratio_idx=%d cal=%d max_lum=%d";
static const char final_compact[]="[service.settings]GetMaxLum: eye=%s panel_current=%d ratio_idx=%d cal=%d max_lum=%d";
uint32_t display_driver_brightness_max_lum_46c23c(void) {
    float local[11];
    audio_uart_checksum_copy(local,ratios,44u);
    uint8_t raw=*display_driver_brightness_ratio_cell_4af73a(5u);
    uint32_t index=(uint8_t)(raw-5u);
    if(index>=11u) index=10u;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,0x1ecu,index_text,index);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10400000u,index_compact,index_compact,index);
    uint8_t role=audio_uart_device_role_get();
    uint32_t cal=0;
    const char *eye="?";
    if(role==1u) {cal=audio_settings_config_live[0x17u];eye="R";}
    else if(role==2u) {cal=audio_settings_config_live[0x16u];eye="L";}
    else {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,0x1f8u,role_text,role);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08400000u,role_compact,role_compact,role);
    }
    if(cal>=11u) cal=10u;
    uint32_t reduction=(2100u*cal)/10u;
    float adjusted=local[index]*7100.0f-(float)reduction;
    uint32_t max_lum=(uint32_t)adjusted;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0x204u,final_text,eye,raw,index,cal,max_lum);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0d400000u,final_compact,final_compact,eye,raw,index,cal,max_lum);
    return max_lum;
}
