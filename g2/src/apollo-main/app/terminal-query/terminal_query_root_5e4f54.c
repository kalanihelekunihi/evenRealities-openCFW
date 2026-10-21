/* Terminal query dialog root/panel constructor, stock 0x5e4f54..0x5e5059. */
#include <stdint.h>
extern uint32_t audio_uart_device_role_get(void);
extern void *audio_uart_page_43de82(void *);
extern void audio_uart_page_43f4c0(void *,uint32_t,uint32_t);
extern void audio_uart_page_43f6b8(void *,uint32_t,uint32_t,uint32_t);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_44127e(void *,uint32_t,uint32_t);
extern void audio_uart_page_44129e(void *,uint32_t,uint32_t);
extern void audio_uart_page_44131c(void *,uint32_t,uint32_t);
extern void audio_uart_page_44146a(void *,uint32_t,uint32_t);
extern void audio_terminal_ui_theme_5e47cc(void *,uint32_t,uint32_t);
extern void audio_uart_page_43dfa4(void *,uint32_t);
extern void audio_uart_page_43f506(void *,uint32_t);
extern void audio_uart_page_4412ec(void *,uint32_t,uint32_t);

void *audio_terminal_query_root_5e4f54(void *parent,uint32_t mode) {
    const uint32_t shift=audio_uart_device_role_get()==1u?(uint32_t)-8:8u;
    void *outer=audio_uart_page_43de82(parent);
    audio_uart_page_43f4c0(outer,0x23cu,0x3fffffffu);
    const uint8_t narrowed=(uint8_t)mode;
    audio_uart_page_43f6b8(outer,narrowed==1u?2u:5u,0u,
                           narrowed==1u?0u:(uint32_t)-10);
    audio_uart_page_44127e(outer,audio_uart_page_44104c(0u),0u);
    audio_uart_page_44129e(outer,0xffu,0u);
    audio_uart_page_44131c(outer,0u,0u);
    audio_uart_page_44146a(outer,0u,0u);
    audio_terminal_ui_theme_5e47cc(outer,0u,0u);
    audio_uart_page_43dfa4(outer,0x10u);
    void *inner=audio_uart_page_43de82(outer);
    audio_uart_page_43f506(inner,0x22cu);
    audio_uart_page_43f6b8(inner,2u,shift,0u);
    audio_uart_page_44127e(inner,audio_uart_page_44104c(0u),0u);
    audio_uart_page_44129e(inner,0xffu,0u);
    audio_uart_page_44131c(inner,1u,0u);
    audio_uart_page_4412ec(inner,audio_uart_page_44104c(0x00ffffffu),0u);
    audio_uart_page_44146a(inner,6u,0u);
    audio_terminal_ui_theme_5e47cc(inner,0u,0u);
    audio_uart_page_43dfa4(inner,0x10u);
    return inner;
}
