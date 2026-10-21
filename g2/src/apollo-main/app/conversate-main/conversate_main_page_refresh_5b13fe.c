/* Apollo Main Conversate list count and oldest-tag deletion 0x5b0c18, 0x5b13fe. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern uint32_t audio_uart_lv_child_count_44ddea(uint32_t);
extern uint32_t audio_terminal_ui_object_valid_43e2ea(uint32_t);
extern uint32_t audio_lv_child_44dce2(uint32_t, uint32_t);
extern void audio_uart_page_delete_event_filter_44d7b8(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui.c";
static const char function[] = "conversate_ui_tag_data_delete";
static const char count_message[] =
    "UI button count: %d, delete oldest button when exceed max";
static const char count_compact[] =
    "[conversate.ui]UI button count: %d, delete oldest button when exceed max";
static const char skip_message[] = "Skip tag delete: current mode is selected";
static const char skip_compact[] =
    "[conversate.ui]Skip tag delete: current mode is selected";

static volatile uint8_t *ui_state(void) {
    return (volatile uint8_t *)(uintptr_t)(
        (uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u);
}

static uint32_t word(const volatile uint8_t *state, uint32_t offset) {
    return *(const volatile uint32_t *)(const void *)(state + offset);
}

uint32_t audio_conversate_ui_list_count_5b0c18(void) {
    const uint32_t list = word(ui_state(), 0x64u);
    return list == 0u ? 0u : audio_uart_lv_child_count_44ddea(list);
}

void audio_conversate_ui_main_page_refresh_5b13fe(void) {
    volatile uint8_t *const ui = ui_state();
    uint32_t count = audio_conversate_ui_list_count_5b0c18();
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 0x18bu,
                           count_message, count);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x10400000u, count_compact, count_compact, count);
    const uint32_t list = word(ui, 0x64u);
    if (list == 0u || audio_terminal_ui_object_valid_43e2ea(list) == 0u) return;
    if (ui[0x96u] != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module, path, function, 0x192u, skip_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x10000000u, skip_compact, skip_compact);
        return;
    }
    while (count > 20u) {
        const uint32_t child = audio_lv_child_44dce2(list, count - 1u);
        if (child != 0u && audio_terminal_ui_object_valid_43e2ea(child) != 0u)
            audio_uart_page_delete_event_filter_44d7b8(child);
        --count;
    }
}
