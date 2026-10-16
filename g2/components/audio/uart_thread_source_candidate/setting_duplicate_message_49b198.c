/* Native setting_is_duplicate_message 0x49b198..0x49b1f8. */
#include <stdint.h>
extern uint32_t audio_settings_last_received_magic_20074868;
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="pb_service_setting";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_setting\\pb_service_setting.c";
static const char function[]="setting_is_duplicate_message";
static const char message[]="Duplicate message detected, magic_random = %d";
static const char short_message[]="[pb_service_setting]Duplicate message detected, magic_random = %d";
uint32_t audio_setting_is_duplicate_message_49b198(uint32_t magic) {
    if(magic!=audio_settings_last_received_magic_20074868) {
        audio_settings_last_received_magic_20074868=magic;
        return 0u;
    }
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(2u,module,path,function,0x52u,message,magic);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x08400000u,short_message,short_message,magic);
    return 1u;
}
