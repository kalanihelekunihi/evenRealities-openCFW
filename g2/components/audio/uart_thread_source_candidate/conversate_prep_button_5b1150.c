/* Apollo Main Conversate prep-notes button factory, 0x5b1150..0x5b12b9. */
#include <stdint.h>

extern uint32_t audio_uart_ring_primary_head_cell; /* native 0x200746dc */
extern uint32_t audio_uart_page_43de82(uint32_t);
extern void audio_uart_page_43f4c0(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_48ba78(uint32_t, uint32_t);
extern void audio_uart_page_48ba92(uint32_t, uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44146a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_441254(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44122a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_441238(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44131c(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44130c(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44129e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44132a(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_4412ec(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43dfa4(uint32_t, uint32_t);
extern uint32_t audio_lv_image_create_498668(uint32_t);
extern void audio_lv_image_source_498680(uint32_t, uint32_t);
extern void audio_uart_page_44127e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_4413ce(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_lv_label_create_499416(uint32_t);
extern void audio_lv_label_text_49942e(uint32_t, uint32_t);
extern void audio_uart_page_44143e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_441180(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_4411aa(uint32_t, uint32_t, uint32_t);
extern void audio_lv_label_mode_499678(uint32_t, uint32_t);
extern void audio_uart_page_44145a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44140e(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui.c";
static const char function[] = "conversate_ui_button_create";
static const char message[] = "Button(%s) create completed";
static const char compact[] = "[conversate.ui]Button(%s) create completed";

uint32_t audio_conversate_prep_button_create_5b1150(uint32_t parent,
                                                     uint32_t image,
                                                     uint32_t label_text,
                                                     uint32_t ignored) {
    (void)ignored;
    const uint32_t button = audio_uart_page_43de82(parent);
    audio_uart_page_43f4c0(button, 0x3fffffffu, 0x28u);
    audio_uart_page_48ba78(button, 0u);
    audio_uart_page_48ba92(button, 0u, 2u, 2u);
    audio_uart_page_44146a(button, 6u, 0u);
    audio_uart_page_441254(button, 8u, 0u);
    audio_uart_page_44122a(button, 12u, 0u);
    audio_uart_page_441238(button, 12u, 0u);
    audio_uart_page_44131c(button, 1u, 0u);
    audio_uart_page_44130c(button, 0u, 0u);
    audio_uart_page_44129e(button, 0u, 0u);
    audio_uart_page_44132a(button, 15u, 0u);
    audio_uart_page_4412ec(button, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_43dfa4(button, 0x10u);
    const uint32_t picture = audio_lv_image_create_498668(button);
    audio_lv_image_source_498680(picture, image);
    audio_uart_page_44127e(picture, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44129e(picture, 0xffu, 0u);
    audio_uart_page_4413ce(picture, 0x33u, 0u);
    const uint32_t label = audio_lv_label_create_499416(button);
    audio_lv_label_text_49942e(label, label_text);
    audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, 0u);
    audio_uart_page_441180(label, 0x186u, 0u);
    audio_uart_page_4411aa(label, 0x1cu, 0u);
    audio_lv_label_mode_499678(label, 1u);
    audio_uart_page_44145a(label, 1u, 0u);
    audio_uart_page_44140e(label, audio_uart_page_44104c(0x444444u), 0u);
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 0x15bu, message, label_text);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x10400000u, compact, compact, label_text);
    return button;
}
