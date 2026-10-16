/* Terminal ASR result-area constructor, stock 0x5ebff8..0x5ec18f. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern uint32_t audio_uart_ring_secondary_head_cell;
extern const uint8_t audio_terminal_result_icon_773258;
extern void audio_uart_page_44122a(void *,uint32_t,uint32_t);
extern void audio_uart_page_441238(void *,uint32_t,uint32_t);
extern void audio_uart_page_44120e(void *,uint32_t,uint32_t);
extern void audio_uart_page_441246(void *,uint32_t,uint32_t);
extern void audio_uart_page_43f506(void *,uint32_t);
extern void audio_uart_page_44d878(void *);
extern void audio_uart_page_441270(void *,uint32_t,uint32_t);
extern void audio_uart_page_43f568(void *,uint32_t);
extern void *audio_uart_page_498668(void *);
extern void audio_uart_page_498680(void *,const void *);
extern void audio_uart_page_43ded4(void *,uint32_t);
extern void audio_uart_page_4411e4(void *,uint32_t,uint32_t);
extern void *audio_uart_page_499416(void *);
extern void audio_uart_page_43f09a(void *,uint32_t,uint32_t);
extern void audio_uart_page_49942e(void *,const char *);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_44140e(void *,uint32_t,uint32_t);
extern void audio_uart_page_44143e(void *,uint32_t,uint32_t);
extern void audio_uart_page_44e3ca(void *,uint32_t);
extern void audio_uart_page_44e368(void *,uint32_t);
extern void audio_uart_page_43f66c(void *);
extern void audio_terminal_status_apply_layout_5ebc9e(uint32_t,uint32_t);
extern int32_t audio_uart_lv_scroll_bottom_44e4bc(void *);
extern void audio_uart_lv_scroll_dispatch_44e884(void *,int32_t,int32_t,uint32_t);

static const char send_text[]="Send";
static const char cancel_text[]="Cancel";
static uint32_t word(uint32_t offset) {
    const uint8_t *p=audio_terminal_ui_state_base+offset;
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static void store_word(uint32_t offset,uint32_t value) {
    uint8_t *p=audio_terminal_ui_state_base+offset;
    p[0]=(uint8_t)value;p[1]=(uint8_t)(value>>8);
    p[2]=(uint8_t)(value>>16);p[3]=(uint8_t)(value>>24);
}

void audio_terminal_ui_result_area_prepare_5ebff8(void) {
    uint32_t root=word(0x1f4u),title=word(0x1fcu),footer=word(0x200u);
    if (root==0u || title==0u || footer==0u)return;
    void *r=(void *)(uintptr_t)root;
    void *f=(void *)(uintptr_t)footer;
    audio_uart_page_44122a(r,8u,0u);
    audio_uart_page_441238(r,8u,0u);
    audio_uart_page_44120e(r,8u,0u);
    audio_uart_page_441246(r,4u,0u);
    audio_uart_page_43f506((void *)(uintptr_t)title,0x208u);
    audio_uart_page_44d878(f);
    audio_uart_page_43f506(f,0x208u);
    audio_uart_page_441270(f,0x14u,0u);
    const uint8_t *font=(const uint8_t *)(uintptr_t)audio_uart_ring_secondary_head_cell;
    uint32_t font_height=(uint32_t)font[12]|((uint32_t)font[13]<<8)|
                ((uint32_t)font[14]<<16)|((uint32_t)font[15]<<24);
    uint32_t desired=(font_height<<1)+18u;
    if ((int32_t)desired<40)desired=40u;
    audio_uart_page_43f568(f,desired);
    void *icon=audio_uart_page_498668(r);
    store_word(0x208u,(uint32_t)(uintptr_t)icon);
    audio_uart_page_498680(icon,&audio_terminal_result_icon_773258);
    audio_uart_page_43ded4(icon,0x20000u);
    audio_uart_page_4411e4(icon,0u,0u);
    void *send=audio_uart_page_499416(f);
    store_word(0x20cu,(uint32_t)(uintptr_t)send);
    audio_uart_page_43f09a(send,0u,8u);
    audio_uart_page_49942e(send,send_text);
    audio_uart_page_44140e(send,audio_uart_page_44104c(0x00ffffffu),0u);
    audio_uart_page_44143e(send,audio_uart_ring_secondary_head_cell,0u);
    void *cancel=audio_uart_page_499416(f);
    store_word(0x210u,(uint32_t)(uintptr_t)cancel);
    audio_uart_page_43f09a(cancel,0u,font_height+10u);
    audio_uart_page_49942e(cancel,cancel_text);
    audio_uart_page_44140e(cancel,audio_uart_page_44104c(0x00333333u),0u);
    audio_uart_page_44143e(cancel,audio_uart_ring_secondary_head_cell,0u);
    store_word(0x204u,0u);
    audio_uart_page_44e3ca(r,12u);
    audio_uart_page_44e368(r,0u);
    audio_terminal_ui_state_base[0x278u]=0u;
    audio_uart_page_43f66c(r);
    audio_terminal_status_apply_layout_5ebc9e((uint32_t)(uintptr_t)audio_terminal_ui_state_base,0u);
    int32_t bottom=audio_uart_lv_scroll_bottom_44e4bc(r);
    if (bottom>=1)
        audio_uart_lv_scroll_dispatch_44e884(r,0,-bottom,0u);
}
