/* Stock Terminal UI root creation 0x5e716c. */
#include <stdint.h>

extern uint32_t audio_terminal_display_queue_handle; /* stock RAM 0x20074a90 */
extern uint32_t audio_uart_page_43de82(uint32_t);
extern void audio_uart_page_43dfa4(uint32_t, uint32_t);
extern void audio_uart_page_43f4c0(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43f09a(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_44127e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44129e(uint32_t, uint32_t, uint32_t);
extern void lv_obj_set_style_border_width(uint32_t, uint32_t, uint32_t);
extern void lv_obj_set_style_outline_width(uint32_t, uint32_t, uint32_t);
extern void lv_obj_set_style_outline_pad(uint32_t, uint32_t, uint32_t);
extern void lv_obj_set_style_shadow_width(uint32_t, uint32_t, uint32_t);
extern void lv_obj_set_style_radius(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_441246(uint32_t, uint32_t, uint32_t);
extern void audio_terminal_ui_theme_5e47cc(uint32_t, uint32_t, uint32_t);
extern void audio_terminal_list_anim_init_58966c(void);

void audio_terminal_ui_start_5e716c(void) {
    uint32_t root = audio_uart_page_43de82(0u);
    audio_terminal_display_queue_handle = root;
    audio_uart_page_43dfa4(root, 0x370u);
    audio_uart_page_43f4c0(root, 0x240u, 0x120u);
    audio_uart_page_43f09a(root, 0u, 0u);
    audio_uart_page_44127e(root, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44129e(root, 0xffu, 0u);
    lv_obj_set_style_border_width(root, 0u, 0u);
    lv_obj_set_style_outline_width(root, 0u, 0u);
    lv_obj_set_style_outline_pad(root, 0u, 0u);
    lv_obj_set_style_shadow_width(root, 0u, 0u);
    lv_obj_set_style_radius(root, 0u, 0u);
    audio_terminal_ui_theme_5e47cc(root, 0u, 0u);
    audio_uart_page_441246(root, 0u, 0u);
    audio_terminal_list_anim_init_58966c();
}
