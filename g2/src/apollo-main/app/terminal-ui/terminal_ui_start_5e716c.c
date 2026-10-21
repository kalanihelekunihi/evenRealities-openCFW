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
extern void audio_uart_page_44131c(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44133a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_441378(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_441386(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44146a(uint32_t, uint32_t, uint32_t);
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
    audio_uart_page_44131c(root, 0u, 0u);
    audio_uart_page_44133a(root, 0u, 0u);
    audio_uart_page_441378(root, 0u, 0u);
    audio_uart_page_441386(root, 0u, 0u);
    audio_uart_page_44146a(root, 0u, 0u);
    audio_terminal_ui_theme_5e47cc(root, 0u, 0u);
    audio_uart_page_441246(root, 0u, 0u);
    audio_terminal_list_anim_init_58966c();
}
