/* Native conversate_ui_init 0x5b14ce..0x5b156b. */
#include <stdint.h>

extern uint32_t audio_conversate_ui_app_id_200743a0;
extern uint32_t audio_uart_page_43de82(uint32_t);
extern void audio_uart_page_43f4c0(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43f09a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44129e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44131c(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44146a(uint32_t, uint32_t, uint32_t);
extern void audio_conversate_ui_style_5b0ac4(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43dfa4(uint32_t, uint32_t);
extern void audio_conversate_timer_init_5b3cba(void);
extern void audio_terminal_list_anim_init_58966c(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui.c";
static const char function[] = "conversate_ui_init";
static const char message[] = "init completed";
static const char short_message[] = "[conversate.ui]init completed";

void audio_conversate_ui_start_5b14ce(uint32_t parent) {
    uint32_t root = audio_uart_page_43de82(parent);
    audio_conversate_ui_app_id_200743a0 = root;
    audio_uart_page_43f4c0(root, 0x240u, 0x120u);
    audio_uart_page_43f09a(root, 0u, 0u);
    audio_uart_page_44129e(root, 0u, 0u);
    audio_uart_page_44131c(root, 0u, 0u);
    audio_uart_page_44146a(root, 0u, 0u);
    audio_conversate_ui_style_5b0ac4(root, 0u, 0u);
    audio_uart_page_43dfa4(root, 0x70u);
    audio_conversate_timer_init_5b3cba();
    audio_terminal_list_anim_init_58966c();
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 429u, message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x10000000u, short_message, short_message);
}
