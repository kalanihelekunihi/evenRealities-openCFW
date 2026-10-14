/* Apollo SVC_Settings_UledCtrlCheck 0x46b238..0x46b333. Candidate. */
#include <stdint.h>
extern uint32_t audio_uart_command_pending(void); /* selected 0x4abe60 */
extern uint32_t audio_ota_transfer_active(void); /* selected 0x4487ac */
extern uint32_t display_driver_wear_detect_49eb96(void);
extern uint32_t audio_uart_case_status(void); /* native 0x4acad0 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="service.settings";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\settings\\service_settings.c";
static const char function[]="SVC_Settings_UledCtrlCheck";
static const char ota[]="OTA is going, jbd4010 ctrl not allowed";
static const char ota_compact[]="[service.settings]OTA is going, jbd4010 ctrl not allowed";
static const char wear[]="wear detect input not enabled, jbd4010 ctrl not allowed";
static const char wear_compact[]="[service.settings]wear detect input not enabled, jbd4010 ctrl not allowed";
static const char boxed[]="glasses in box, jbd4010 ctrl not allowed";
static const char boxed_compact[]="[service.settings]glasses in box, jbd4010 ctrl not allowed";
static void denied(uint32_t line,const char *message,const char *short_message) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(2u,module,path,function,line,message);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x08000000u,short_message,short_message);
}
uint32_t display_driver_dispatch_gate(void) {
    if(audio_uart_command_pending()==1u) return 1u;
    if(audio_ota_transfer_active()!=0u) {
        denied(0x45u,ota,ota_compact);return 0u;
    }
    if(display_driver_wear_detect_49eb96()==0u) {
        denied(0x4bu,wear,wear_compact);return 0u;
    }
    if(audio_uart_case_status()==1u) {
        denied(0x51u,boxed,boxed_compact);return 0u;
    }
    return 1u;
}
