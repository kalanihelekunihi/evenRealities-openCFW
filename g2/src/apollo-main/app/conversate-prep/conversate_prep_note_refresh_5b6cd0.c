/* Apollo Main prep-note refresh 0x5b6cd0..0x5b6f8d, including style helper 0x5b69d4. */
#include <stdint.h>

extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern uint32_t audio_uart_ring_primary_head_cell;
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern void audio_terminal_display_status_44ea04(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44d878(uint32_t);
extern void audio_uart_page_43ded4(uint32_t, uint32_t);
extern uint32_t audio_conversate_prep_note_finish_5b476a(void);
extern uint32_t audio_conversate_prep_note_line_count_5b4770(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern uint32_t audio_uart_page_43de82(uint32_t);
extern void audio_uart_page_43f4c0(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43f09a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44129e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44131c(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44146a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43dfa4(uint32_t, uint32_t);
extern uint32_t audio_uart_page_499416(uint32_t);
extern void audio_uart_page_44144c(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_layout_499678(uint32_t, uint32_t);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_44140e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44143e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44145a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44122a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_441238(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44120e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44121c(uint32_t, uint32_t, uint32_t);
extern void audio_conversate_prep_note_pool_bind_5b6ac0(uint32_t);
extern void audio_uart_page_43f66c(uint32_t);
extern void audio_conversate_prep_note_pool_show_5b6b58(uint32_t);
extern void audio_uart_page_58c238(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(uint32_t, uint32_t);

static const char module[] = "conversate.prep";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui_prep_note_page.c";
static const char function[] = "conversate_ui_prep_note_sync_content";
static const char not_ready[] =
    "prep note content not ready, keep expand page empty";
static const char not_ready_compact[] =
    "[conversate.prep]prep note content not ready, keep expand page empty";
static const char empty[] =
    "prep note content ready but line layout is empty";
static const char empty_compact[] =
    "[conversate.prep]prep note content ready but line layout is empty";
static const char virtual_lines[] =
    "prep note virtual view lines=%u visible=%u pool=%u";
static const char virtual_lines_compact[] =
    "[conversate.prep]prep note virtual view lines=%u visible=%u pool=%u";

static uint32_t word(const volatile uint8_t *bytes, uint32_t offset) {
    return *(const volatile uint32_t *)(const void *)(bytes + offset);
}
static void put_word(volatile uint8_t *bytes, uint32_t offset, uint32_t value) {
    *(volatile uint32_t *)(void *)(bytes + offset) = value;
}

void audio_conversate_prep_note_style_5b69d4(
    uint32_t object, uint32_t value, uint32_t selector) {
    audio_uart_page_44122a(object, value, selector);
    audio_uart_page_441238(object, value, selector);
    audio_uart_page_44120e(object, value, selector);
    audio_uart_page_44121c(object, value, selector);
}

uint32_t audio_conversate_prep_note_refresh_5b6cd0(uint32_t animate) {
    volatile uint8_t *const ui = (volatile uint8_t *)(uintptr_t)(
        (uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u);
    const uint32_t note = word(ui, 0x24u);
    const uint32_t expanded = word(ui, 0x2cu);
    if (note == 0u || expanded == 0u) return UINT32_MAX;
    ui[0x60u] = 0u;
    ui[0x61u] = 0u;
    put_word(ui, 0x28u, 0u);
    audio_uart_buffer_zero((void *)(uintptr_t)(ui + 0x30u), 0x30u, 0u);
    audio_terminal_display_status_44ea04(note, 0u, 0u);
    audio_uart_page_44d878(note);
    audio_uart_page_43ded4(note, 1u);
    audio_uart_page_43ded4(expanded, 1u);
    if (audio_conversate_prep_note_finish_5b476a() == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, path, function, 0xdau, not_ready);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x08000000u,
                                        not_ready_compact, not_ready_compact);
        return 0u;
    }
    const uint32_t count = (uint16_t)audio_conversate_prep_note_line_count_5b4770();
    if (count == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, path, function, 0xe0u, empty);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x08000000u,
                                        empty_compact, empty_compact);
        return 0u;
    }
    const uint32_t height = count * 28u < 0xe0u ? 0xe0u : count * 28u;
    const uint32_t virtual_page = audio_uart_page_43de82(note);
    audio_uart_page_43f4c0(virtual_page, 0x220u, height);
    audio_uart_page_43f09a(virtual_page, 0u, 0u);
    audio_uart_page_44129e(virtual_page, 0u, 0u);
    audio_uart_page_44131c(virtual_page, 0u, 0u);
    audio_uart_page_44146a(virtual_page, 0u, 0u);
    audio_conversate_prep_note_style_5b69d4(virtual_page, 0u, 0u);
    audio_uart_page_43dfa4(virtual_page, 0x10u);
    put_word(ui, 0x28u, virtual_page);
    for (uint32_t i = 0; i < 12u; ++i) {
        const uint32_t label = audio_uart_page_499416(virtual_page);
        put_word(ui, 0x30u + i * 4u, label);
        audio_uart_page_43f4c0(label, 0x220u, 28u);
        audio_uart_page_44144c(label, 0u, 0u);
        audio_uart_page_layout_499678(label, 4u);
        const uint32_t white = audio_uart_page_44104c(0x00ffffffu);
        audio_uart_page_44140e(label, white, 0u);
        audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, 0u);
        audio_uart_page_44145a(label, 1u, 0u);
        audio_conversate_prep_note_style_5b69d4(label, 0u, 0u);
    }
    audio_conversate_prep_note_pool_bind_5b6ac0(0u);
    audio_uart_page_43f66c(note);
    audio_conversate_prep_note_pool_show_5b6b58(0u);
    audio_uart_page_43dfa4(note, 1u);
    if ((uint8_t)animate != 0u)
        audio_uart_page_58c238(note, 200u, 0u);
    if (audio_uart_lv_obj_has_flag_43e0e0(expanded, 1u) == 0u &&
            (uint8_t)animate != 0u)
        audio_uart_page_58c238(expanded, 200u, 0u);
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 0x10du,
                           virtual_lines, count, 8u, 12u);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x0cc00000u,
                                    virtual_lines_compact, virtual_lines_compact,
                                    count, 8u, 12u);
    return 0u;
}
