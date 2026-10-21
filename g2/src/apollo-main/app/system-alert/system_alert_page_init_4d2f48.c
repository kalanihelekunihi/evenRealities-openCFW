/* Native system-alert MainPage initializer 0x4d2f48. */
#include <stdint.h>
extern uint32_t audio_system_alert_parent_200749ec;
uint32_t audio_system_alert_child_200749f0
    __attribute__((section(".g2.ram.system_alert_child"),used,aligned(4)));
extern uint32_t audio_uart_page_43de82(uint32_t);
extern void audio_uart_page_43f506(uint32_t,uint32_t);
extern void audio_uart_page_43f568(uint32_t,uint32_t);
extern void audio_uart_page_43f6b8(uint32_t,uint32_t,uint32_t,uint32_t);
extern void audio_uart_page_43dfa4(uint32_t,uint32_t);
extern void audio_uart_page_44e368(uint32_t,uint32_t);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_44127e(uint32_t,uint32_t,uint32_t);
extern void audio_uart_page_44129e(uint32_t,uint32_t,uint32_t);
extern void audio_uart_page_4412ec(uint32_t,uint32_t,uint32_t);
extern void audio_uart_page_44131c(uint32_t,uint32_t,uint32_t);
extern void audio_system_alert_page_style_4d2b9c(uint32_t,uint32_t,uint32_t);
extern uint8_t audio_uart_device_role_get(void);
extern void audio_uart_page_43f0e0(uint32_t,uint32_t);
extern void audio_uart_page_43f142(uint32_t,uint32_t);
extern void audio_uart_page_44e3ca(uint32_t,uint32_t);
extern void audio_uart_page_44146a(uint32_t,uint32_t,uint32_t);
extern void audio_uart_page_44120e(uint32_t,uint32_t,uint32_t);
extern void audio_uart_page_44121c(uint32_t,uint32_t,uint32_t);
extern void audio_uart_page_44122a(uint32_t,uint32_t,uint32_t);
extern void audio_uart_page_441238(uint32_t,uint32_t,uint32_t);

void audio_system_alert_page_init_4d2f48(uint32_t context,uint32_t payload,
                                          uint32_t length) {
    (void)payload;(void)length;
    uint32_t parent=audio_uart_page_43de82(context);
    audio_system_alert_parent_200749ec=parent;
    audio_uart_page_43f506(parent,0x3fffffffu);
    audio_uart_page_43f568(parent,0x28u);
    audio_uart_page_43f6b8(parent,2u,0u,0u);
    audio_uart_page_43dfa4(parent,0x2004u);
    audio_uart_page_44e368(parent,0u);
    uint32_t color=audio_uart_page_44104c(0u);
    audio_uart_page_44127e(parent,color,0u);
    audio_uart_page_44129e(parent,0xffu,0u);
    color=audio_uart_page_44104c(0u);
    audio_uart_page_4412ec(parent,color,0u);
    audio_uart_page_44131c(parent,0u,0u);
    audio_system_alert_page_style_4d2b9c(parent,0u,0u);

    uint32_t child=audio_uart_page_43de82(parent);
    audio_system_alert_child_200749f0=child;
    audio_uart_page_43f506(child,0x3fffffffu);
    audio_uart_page_43f568(child,0x28u);
    audio_uart_page_43f0e0(child,audio_uart_device_role_get()==1u?0u:0x10u);
    audio_uart_page_43f142(child,0u);
    audio_uart_page_44e368(child,0u);
    audio_uart_page_44e3ca(child,0xcu);
    audio_uart_page_44129e(child,0u,0u);
    audio_uart_page_44146a(child,10u,0u);
    color=audio_uart_page_44104c(0xffffffu);
    audio_uart_page_4412ec(child,color,0u);
    audio_uart_page_44131c(child,1u,0u);
    audio_uart_page_44120e(child,0u,0u);
    audio_uart_page_44121c(child,0u,0u);
    audio_uart_page_44122a(child,0xcu,0u);
    audio_uart_page_441238(child,0xcu,0u);
}
