/* Native SilentMode_SetStatus 0x4691bc. */
#include <stdint.h>
extern uint8_t *audio_settings_get_config_46b44c(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="silent_mode";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\Silent_Mode\\silent_mode.c";
static const char function[]="SilentMode_SetStatus";
static const char failure[]="Failed to get settings";
static const char compact[]="[silent_mode]Failed to get settings";

/* Stock 0x4691BC (SilentMode_SetStatus) */
void audio_silent_mode_set_status(uint32_t enabled) {
    uint8_t *config=audio_settings_get_config_46b44c();
    if(config==0) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,0x4cu,failure);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04000000u,compact,compact);
        return;
    }
    config[0x15u]=(uint8_t)((uint8_t)enabled!=0u);
}
