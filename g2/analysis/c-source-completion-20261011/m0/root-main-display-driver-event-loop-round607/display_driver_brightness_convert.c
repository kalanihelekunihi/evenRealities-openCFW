/* Apollo brightness-to-current/luminance 0x46c410..0x46c501. Candidate. */
#include <stdint.h>
extern uint32_t display_driver_brightness_max_lum_46c23c(void); /* lower body pending */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="service.settings";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\settings\\service_settings.c";
static const char function[]="SVC_Settings_BrightnessLevelToLumAndCurrent";
static const char lum_text[]="Convert brightness level %d to lum %d, max_lum=%d";
static const char lum_compact[]="[service.settings]Convert brightness level %d to lum %d, max_lum=%d";
static const char current_text[]="Convert brightness level %d to current %d, lum=%d";
static const char current_compact[]="[service.settings]Convert brightness level %d to current %d, lum=%d";
uint32_t display_driver_case4_read(uint32_t brightness,uint32_t *current,uint32_t *luminance) {
    uint32_t level=brightness>100u?100u:brightness<2u?2u:brightness;
    uint32_t max_lum=display_driver_brightness_max_lum_46c23c();
    if(level<31u) {
        *current=0u;
        uint32_t delta=(uint32_t)(max_lum-333u);
        uint32_t numerator=(uint32_t)((level-2u)*delta+14u);
        uint32_t lum=numerator/28u+333u;
        *luminance=lum;
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,0x223u,lum_text,level,lum,max_lum);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0cc00000u,lum_compact,lum_compact,level,lum,max_lum);
    } else {
        uint32_t amperage=(uint32_t)(36u*level-1045u)/70u;
        *current=amperage;
        *luminance=max_lum;
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,0x22du,current_text,level,amperage,max_lum);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0cc00000u,current_compact,current_compact,level,amperage,max_lum);
    }
    return 0u;
}
