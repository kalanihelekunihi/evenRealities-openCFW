/* Native system_alert_ReflashEventHandler 0x4d30ba. */
#include <stdint.h>
extern uint32_t audio_system_alert_parent_200749ec;
extern uint32_t audio_system_alert_child_200749f0;
extern uint32_t audio_system_alert_page_id_20003bcc;
extern uint8_t audio_system_alert_active_20075025;
extern uint32_t audio_system_alert_message_notify; /* native RAM 0x200749f4 */
uint32_t audio_system_alert_font_200746e0
    __attribute__((section(".g2.ram.system_alert_font"),used,aligned(4)));
extern const uint8_t audio_system_alert_icon_disconnect_7747e4[];
extern const uint8_t audio_system_alert_icon_connect_772928[];
extern void audio_uart_page_44d878(uint32_t);
extern uint32_t audio_uart_page_498668(uint32_t);
extern void audio_uart_page_498680(uint32_t,const void *);
extern void audio_uart_page_43f506(uint32_t,uint32_t);
extern void audio_uart_page_43f568(uint32_t,uint32_t);
extern void audio_uart_page_43f0e0(uint32_t,uint32_t);
extern void audio_uart_page_43f142(uint32_t,uint32_t);
extern void audio_uart_page_43ded4(uint32_t,uint32_t);
extern void audio_uart_page_43dfa4(uint32_t,uint32_t);
extern uint32_t audio_uart_page_499416(uint32_t);
extern uint32_t audio_uart_page_460084(const char *);
extern uint32_t audio_uart_page_45fffe(const char *,uint32_t);
extern void audio_uart_page_49942e(uint32_t,uint32_t);
extern void audio_uart_page_44143e(uint32_t,uint32_t,uint32_t);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_44140e(uint32_t,uint32_t,uint32_t);
extern uint8_t audio_uart_device_role_get(void);
extern void audio_uart_page_43f6b8(uint32_t,uint32_t,uint32_t,uint32_t);
extern void audio_uart_page_43f66c(uint32_t);
extern void audio_system_alert_close_464c36(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="system_alert";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\SystemAlert\\systemAlert.c";
static const char function[]="system_alert_ReflashEventHandler";
static const char start[]="system_alert_ReflashEventHandler";
static const char start_compact[]="[system_alert]system_alert_ReflashEventHandler";
static const char unknown[]="unknown system alert event type: %d";
static const char unknown_compact[]="[system_alert]unknown system alert event type: %d";
static const char disconnect[]="ID_GENERAL_RING_DISCONNECT";
static const char connect[]="ID_GENERAL_RING_CONNECT";

void audio_system_alert_page_update_4d30ba(const uint8_t *payload,uint32_t length) {
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(4u,module,path,function,0xd4u,start);
    if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10000000u,start_compact,start_compact);
    if(payload!=0 && length!=0u) {
        const uint8_t event=payload[0];
        if(event==5u) {
            audio_system_alert_active_20075025=0u;
            audio_system_alert_page_id_20003bcc=0xb4u;
            audio_system_alert_close_464c36(0x21u,0u,0u,0u);
        } else {
            if((audio_log_flags()&2u)!=0u)
                audio_log_extended(2u,module,path,function,0xdfu,unknown,event);
            if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
                (void)compressed_log_output(0x08400000u,unknown_compact,unknown_compact,event);
        }
        return;
    }
    const uint8_t mode=(uint8_t)audio_system_alert_message_notify;
    if(mode!=1u && mode!=2u)return;
    const uint32_t child=audio_system_alert_child_200749f0;
    audio_uart_page_44d878(child);
    uint32_t image=audio_uart_page_498668(child);
    audio_uart_page_498680(image,mode==1u?
        audio_system_alert_icon_disconnect_7747e4:audio_system_alert_icon_connect_772928);
    audio_uart_page_43f506(image,0x18u);
    audio_uart_page_43f568(image,0x18u);
    audio_uart_page_43f0e0(image,0u);
    audio_uart_page_43f142(image,8u);
    audio_uart_page_43ded4(image,0x10000u);
    audio_uart_page_43dfa4(image,0x10u);
    uint32_t label=audio_uart_page_499416(child);
    const char *key=mode==1u?disconnect:connect;
    uint32_t text=audio_uart_page_460084(key);
    text=audio_uart_page_45fffe(key,text);
    audio_uart_page_49942e(label,text);
    audio_uart_page_43f506(label,0x3fffffffu);
    audio_uart_page_43f568(label,0x3fffffffu);
    audio_uart_page_43f0e0(label,0x24u);
    audio_uart_page_43f142(label,6u);
    audio_uart_page_43ded4(label,0x10000u);
    audio_uart_page_43dfa4(label,0x10u);
    audio_uart_page_44143e(label,audio_system_alert_font_200746e0,0u);
    const uint32_t color=audio_uart_page_44104c(0xffffffu);
    audio_uart_page_44140e(label,color,0u);
    if(audio_uart_device_role_get()==1u)
        audio_uart_page_43f6b8(child,9u,0u,0u);
    audio_uart_page_43f6b8(audio_system_alert_parent_200749ec,2u,0u,0u);
    audio_uart_page_43f66c(audio_system_alert_parent_200749ec);
}
