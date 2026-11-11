/* Apollo session selector row construction, stock 0x5ecd06..0x5ece48. */
#include <stdint.h>

extern uint32_t audio_uart_ring_secondary_head_cell;
extern void *audio_uart_page_43de82(void *);
extern void audio_uart_page_43f4c0(void *,uint32_t,uint32_t);
extern void audio_uart_page_48ba78(void *,uint32_t);
extern void audio_uart_page_48ba92(void *,uint32_t,uint32_t,uint32_t);
extern void audio_uart_page_43dfa4(void *,uint32_t);
extern void audio_uart_page_44129e(void *,uint32_t,uint32_t);
extern void lv_obj_set_style_border_width(void *,uint32_t,uint32_t);
extern void audio_uart_page_44132a(void *,uint32_t,uint32_t);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_4412ec(void *,uint32_t,uint32_t);
extern void audio_uart_page_44130c(void *,uint32_t,uint32_t);
extern void lv_obj_set_style_radius(void *,uint32_t,uint32_t);
extern void lv_obj_set_style_pad_top(void *,uint32_t,uint32_t);
extern void lv_obj_set_style_pad_bottom(void *,uint32_t,uint32_t);
extern void lv_obj_set_style_pad_left(void *,uint32_t,uint32_t);
extern void lv_obj_set_style_pad_right(void *,uint32_t,uint32_t);
extern void audio_uart_page_441254(void *,uint32_t,uint32_t);
extern void *audio_terminal_voice_anim_create_597e90(void *);
extern void audio_terminal_session_row_icon_5eccc2(void *,uint32_t,uint32_t);
extern void audio_uart_page_44127e(void *,uint32_t,uint32_t);
extern void audio_uart_page_4413ce(void *,uint32_t,uint32_t);
extern void *audio_uart_page_499416(void *);
extern void audio_uart_page_49942e(void *,const char *);
extern void audio_uart_page_441180(void *,uint32_t,uint32_t);
extern void audio_uart_page_4411aa(void *,uint32_t,uint32_t);
extern void audio_uart_page_layout_499678(void *,uint32_t);
extern void audio_uart_page_44140e(void *,uint32_t,uint32_t);
extern void audio_uart_page_44143e(void *,uint32_t,uint32_t);
extern void audio_uart_page_44145a(void *,uint32_t,uint32_t);

void *audio_terminal_session_row_factory_5ecd06(void *parent,const char *name,
                                                 uint32_t kind,uint32_t mode) {
    void *row=audio_uart_page_43de82(parent);
    audio_uart_page_43f4c0(row,0x3fffffffu,40u);
    audio_uart_page_48ba78(row,0u);
    audio_uart_page_48ba92(row,0u,2u,2u);
    audio_uart_page_43dfa4(row,0x10u);
    audio_uart_page_44129e(row,0u,0u);
    lv_obj_set_style_border_width(row,1u,0u);
    audio_uart_page_44132a(row,15u,0u);
    audio_uart_page_4412ec(row,audio_uart_page_44104c(0x00ffffffu),0u);
    audio_uart_page_44130c(row,0u,0u);
    lv_obj_set_style_radius(row,6u,0u);
    lv_obj_set_style_pad_top(row,0u,0u);
    lv_obj_set_style_pad_bottom(row,0u,0u);
    lv_obj_set_style_pad_left(row,12u,0u);
    lv_obj_set_style_pad_right(row,12u,0u);
    audio_uart_page_441254(row,8u,0u);

    void *icon=audio_terminal_voice_anim_create_597e90(row);
    audio_terminal_session_row_icon_5eccc2(icon,(uint8_t)kind,(uint8_t)mode);
    audio_uart_page_44127e(icon,audio_uart_page_44104c(0u),0u);
    audio_uart_page_44129e(icon,0xffu,0u);
    audio_uart_page_4413ce(icon,0x33u,0u);

    void *label=audio_uart_page_499416(row);
    audio_uart_page_49942e(label,name);
    audio_uart_page_441180(label,500u,0u);
    audio_uart_page_4411aa(label,40u,0u);
    audio_uart_page_layout_499678(label,1u);
    audio_uart_page_44140e(label,audio_uart_page_44104c(0x00333333u),0u);
    audio_uart_page_44143e(label,audio_uart_ring_secondary_head_cell,0u);
    audio_uart_page_44145a(label,1u,0u);
    return row;
}
