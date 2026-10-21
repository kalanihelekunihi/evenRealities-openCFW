/* Native silent_mode_common_data_handler 0x46949a. */
#include <stdint.h>

uint8_t audio_silent_mode_ui_status
    __attribute__((section(".g2.ram.silent_mode_ui_status"),used)); /* 0x2007501d */
uint8_t audio_silent_mode_change_from_app
    __attribute__((section(".g2.ram.silent_mode_change_from_app"),used)); /* 0x2007501e */

extern uint8_t audio_silent_mode_status_get(void); /* 0x46919e */
extern void audio_silent_mode_notify_app(uint32_t enabled); /* native notify_silent_mode_to_app */
extern void audio_silent_mode_set_status(uint32_t enabled); /* 0x4691bc */
extern uint8_t audio_uart_device_role_get(void); /* 0x45a568 */
extern uint32_t audio_system_alert_command_45a8ee(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="silent_mode";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\Silent_Mode\\silent_mode.c";
static const char function[]="silent_mode_common_data_handler";
static const char message[]="Silent mode operation: current=%d, target=%d, change_status_from_app:%d";
static const char compact[]="[silent_mode]Silent mode operation: current=%d, target=%d, change_status_from_app:%d";

uint32_t audio_uart_registry_callback_46949a(uint32_t event,const uint8_t *payload,
                                               uint32_t length,uint32_t unused) {
    (void)unused;
    if(event!=4u || payload==0 || length==0u) return 0u;
    const uint8_t requested=payload[0];
    const uint8_t current=audio_silent_mode_status_get();
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,0xbdu,message,
                           current,requested,audio_silent_mode_change_from_app);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10c00000u,compact,compact,
                                    current,requested,audio_silent_mode_change_from_app);
    if(requested==1u && current==0u) {
        audio_silent_mode_ui_status=1u;
        audio_silent_mode_notify_app(1u);
    } else if(requested==0u && current==1u) {
        audio_silent_mode_ui_status=0u;
        audio_silent_mode_set_status(0u);
    } else return 0u;
    if(audio_uart_device_role_get()==1u)
        (void)audio_system_alert_command_45a8ee(0x10au,0u,0u,500u);
    return 0u;
}
