/* Stock Terminal interrupt-confirm scroll action 0x5e6cb8 and child 0x5ec73c. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern void audio_terminal_status_apply_list_5ec3c0(uint32_t state);
extern void audio_terminal_status_publish_5e5498(uint32_t overlay,
                                                   uint32_t focused_index);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "terminal.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_ui.c";
static const char function[] = "terminal_ui_action_interrupt_confirm_scroll";
static const char message[] = "interrupt confirm scroll: state=%d sel=%u";
static const char short_message[] =
    "[terminal.ui]interrupt confirm scroll: state=%d sel=%u";

static uint32_t word(uint32_t offset) {
    return *(const uint32_t *)(const void *)(audio_terminal_ui_state_base + offset);
}

__attribute__((noinline)) void audio_terminal_toggle_view_5ec73c(void) {
    if (word(0x230u) == 0u || word(0x238u) == 0u || word(0x23cu) == 0u)
        return;
    audio_terminal_status_apply_list_5ec3c0(
        (uint32_t)(uintptr_t)audio_terminal_ui_state_base);
    uint32_t focused = audio_terminal_ui_state_base[0x278u] == 1u ? 0u : 1u;
    audio_terminal_status_publish_5e5498(1u, focused);
}

int32_t audio_terminal_ui_action_5e6cb8(uint32_t old_state,
                                         uint32_t event_payload) {
    if (word(0x230u) == 0u)
        return 0;
    uint8_t selected = event_payload == 1u ? 1u : 0u;
    if (audio_terminal_ui_state_base[0x278u] == selected)
        return 0;
    audio_terminal_ui_state_base[0x278u] = selected;
    audio_terminal_toggle_view_5ec73c();
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, 0x6abu,
                           message, (uint8_t)old_state, selected);
    if ((audio_log_flags() & 1u) != 0u ||
        (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0c800000u, short_message,
                                    short_message, (uint8_t)old_state,
                                    selected);
    return 0;
}
