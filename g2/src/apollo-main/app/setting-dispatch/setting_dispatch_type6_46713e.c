/* Native setting type-6 silent-mode route 0x46713e..0x4671a2. */
#include <stdint.h>
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern void audio_silent_mode_set_from_app_46921c(uint32_t);
static const char module[]="setting";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\setting\\setting.c";
static const char function[]="setting_handle_silent_mode_setting";
static const char message[]="[Setting] Handle silent mode from APP: %s";
static const char short_message[]="[setting][Setting] Handle silent mode from APP: %s";
void audio_setting_dispatch_type6_46713e(uint32_t value) {
    const char *state=value!=0u?"ON":"OFF";
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0x1beu,message,state);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c400000u,short_message,short_message,state);
    audio_silent_mode_set_from_app_46921c((uint8_t)value);
}
