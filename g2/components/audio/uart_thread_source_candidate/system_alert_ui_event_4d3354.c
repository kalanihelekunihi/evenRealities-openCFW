/* Native system_alert_ui_event_handler 0x4d3354. */
#include <stdint.h>
extern uint8_t audio_uart_registry_context_20003bd0[]; /* native RAM 0x20003bd0 */
uint32_t audio_system_alert_page_id_20003bcc
    __attribute__((section(".g2.ram.system_alert_page_id"),used,aligned(4)));
uint8_t audio_system_alert_active_20075025
    __attribute__((section(".g2.ram.system_alert_active"),used));
uint32_t audio_system_alert_parent_200749ec
    __attribute__((section(".g2.ram.system_alert_parent"),used,aligned(4)));
extern void audio_system_alert_page_init_4d2f48(uint32_t,uint32_t,uint32_t);
extern void audio_system_alert_page_update_4d30ba(uint32_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="system_alert";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\SystemAlert\\systemAlert.c";
static const char function[]="system_alert_ui_event_handler";
static const char start[]="system_alert_MainPage_init";
static const char start_compact[]="[system_alert]system_alert_MainPage_init";
static const char exit_message[]="UI_EVENT_TYPE_EXIT";
static const char exit_compact[]="[system_alert]UI_EVENT_TYPE_EXIT";

uint32_t audio_uart_registry_callback_4d3354(uint32_t event,uint32_t payload,
                                               uint32_t length,uint32_t context) {
    if(event==2u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(4u,module,path,function,0x134u,start);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x10000000u,start_compact,start_compact);
        audio_system_alert_page_init_4d2f48(context,payload,length);
        *(uint32_t *)(void *)(audio_uart_registry_context_20003bd0+4u)=audio_system_alert_parent_200749ec;
        audio_system_alert_active_20075025=1u;
        audio_system_alert_page_id_20003bcc=0xb4u;
    } else if(event==3u) {
        audio_system_alert_page_update_4d30ba(payload,length);
    } else if(event==5u) {
        audio_system_alert_active_20075025=0u;
        audio_system_alert_page_id_20003bcc=0xb4u;
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,0x14cu,exit_message);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0c000000u,exit_compact,exit_compact);
    }
    return 0u;
}
