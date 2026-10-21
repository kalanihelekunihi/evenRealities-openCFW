/* Native Conversate loading-page route 0x5b30c8..0x5b3249. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern uint8_t audio_conversate_machine_context_200e3aec[];
extern uint32_t audio_conversate_ui_app_id_200743a0;
extern uint32_t audio_uart_ring_primary_head_cell;
extern uint8_t audio_conversate_loading_text_200711dc[];
extern void *audio_conversate_reply_list_get_5b43e8(void);
extern void *audio_conversate_prep_note_get_5b4766(void);
extern void audio_uart_page_43ded4(uint32_t, uint32_t);
extern uint32_t audio_uart_page_43de82(uint32_t);
extern void audio_uart_page_43f4c0(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43f09a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44129e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44131c(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44146a(uint32_t, uint32_t, uint32_t);
extern void audio_conversate_display_style_5b22bc(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43dfa4(uint32_t, uint32_t);
extern uint32_t audio_lv_label_create_499416(uint32_t);
extern void audio_uart_page_43f6b8(uint32_t, uint32_t, uint32_t, uint32_t);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_44140e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44143e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44145a(uint32_t, uint32_t, uint32_t);
extern void audio_lv_label_mode_499678(uint32_t, uint32_t);
extern uint32_t audio_uart_page_460084(const char *);
extern uint32_t audio_uart_page_45fffe(const char *, uint32_t);
extern int32_t g2_audio_dump_snprintf(char *, uint32_t, const char *, ...);
extern void audio_lv_label_text_49942e(uint32_t, uint32_t);
extern void audio_uart_page_58c238(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *,
                                      const char *, ...);

static const char start_key[] = "ID_CONVERSATE_START";
static const char prep_name_key[] = "ID_CONVERSATE_PREP_NOTES_NAME";
static const char format[] = "%s";
static const char module[] = "conversate.ui";
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui_main_page.c";
static const char function[] = "conversate_ui_action_display_loading_page";
static const char already[] = "already in loading, return";
static const char already_short[] =
    "[conversate.ui]already in loading, return";

static uint32_t word(const volatile uint8_t *ui, uint32_t offset) {
    return *(const volatile uint32_t *)(const void *)(ui + offset);
}
static void put_word(volatile uint8_t *ui, uint32_t offset, uint32_t value) {
    *(volatile uint32_t *)(void *)(ui + offset) = value;
}

uint32_t audio_conversate_ui_route_5b30c8(uint32_t state, uint32_t value) {
    (void)value;
    volatile uint8_t *const ui = (volatile uint8_t *)(uintptr_t)
        ((uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u);
    const uint8_t *const replies = audio_conversate_reply_list_get_5b43e8();
    const uint8_t *const notes = audio_conversate_prep_note_get_5b4766();
    const char *selected = 0;
    if ((uint8_t)state == 3u) {
        if (audio_conversate_machine_context_200e3aec[0] == 1u) {
            if (*(const uint16_t *)(const void *)notes != 0u)
                selected = (const char *)(const void *)(notes + 2u);
        } else if (*(const uint16_t *)(const void *)replies != 0u) {
            const uint32_t index = word(ui, 0x84u);
            if (index != UINT32_MAX &&
                (int32_t)index < (int32_t)*(const uint16_t *)(const void *)replies)
                selected = (const char *)(const void *)(replies + index * 0x88u + 0xau);
        }
        audio_uart_page_43ded4(word(ui, 4u), 1u);
    } else if ((uint8_t)state == 0u) {
        if (*(const uint16_t *)(const void *)notes != 0u)
            selected = (const char *)(const void *)(notes + 2u);
    } else if ((uint8_t)state == 1u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module, source, function, 0x1deu, already);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x0c000000u, already_short,
                                        already_short);
        return 0u;
    }

    const uint32_t root = audio_uart_page_43de82(audio_conversate_ui_app_id_200743a0);
    put_word(ui, 0xcu, root);
    audio_uart_page_43f4c0(root, 0x240u, 0x120u);
    audio_uart_page_43f09a(root, 0u, 0u);
    audio_uart_page_44129e(root, 0u, 0u);
    audio_uart_page_44131c(root, 0u, 0u);
    audio_uart_page_44146a(root, 0u, 0u);
    audio_conversate_display_style_5b22bc(root, 0u, 0u);
    audio_uart_page_43dfa4(root, 0x10u);
    const uint32_t label = audio_lv_label_create_499416(root);
    audio_uart_page_43f4c0(label, 0x240u, 0x3fffffffu);
    audio_uart_page_43f6b8(label, 9u, 0u, 0u);
    const uint32_t color = audio_uart_page_44104c(0x00ffffffu);
    audio_uart_page_44140e(label, color, 0u);
    audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, 0u);
    audio_uart_page_44145a(label, 2u, 0u);
    audio_lv_label_mode_499678(label, 0u);

    uint32_t first_length = audio_uart_page_460084(start_key);
    const char *first = (const char *)(uintptr_t)
        audio_uart_page_45fffe(start_key, first_length);
    int32_t written = g2_audio_dump_snprintf(
        (char *)audio_conversate_loading_text_200711dc, 0xc8u, format, first);
    if (selected != 0) {
        audio_conversate_loading_text_200711dc[written] = '\n';
        const uint32_t start = (uint32_t)written + 1u;
        const uint32_t second_length = audio_uart_page_460084(prep_name_key);
        const char *second = (const char *)(uintptr_t)
            audio_uart_page_45fffe(prep_name_key, second_length);
        written = g2_audio_dump_snprintf(
            (char *)audio_conversate_loading_text_200711dc + start,
            0xc8u - start, second, selected) + (int32_t)start;
    }
    audio_conversate_loading_text_200711dc[written] = 0u;
    audio_lv_label_text_49942e(label,
        (uint32_t)(uintptr_t)audio_conversate_loading_text_200711dc);
    audio_uart_page_58c238(root, 0xfau, 0u);
    return 0u;
}
