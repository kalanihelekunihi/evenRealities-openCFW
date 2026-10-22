/* Apollo page-manager container event callback 0x45f914..0x45fa70.
 * Product-private child selectors are retained as explicit imports. */
#include <stdint.h>

extern uint32_t audio_uart_page_event_code_450286(const void *);
extern uint32_t audio_uart_display_audio_is_active_45fcb2(void *);
extern uint32_t audio_uart_display_audio_gate_event_45fbe6(void *, void *);
extern void audio_uart_display_audio_queue_45f58c(void *, uint32_t);
extern void *audio_uart_display_audio_current_45f8e6(void *);
extern void audio_uart_display_audio_activate_45f60e(void *, uint32_t);
extern void *audio_uart_display_audio_find_45f840(void *, uint32_t);
extern void audio_uart_display_audio_complete_45f73a(void *, void *);
extern void *audio_uart_display_audio_handler_a_45f6a8(void *);
extern void *audio_uart_display_audio_handler_b_45f66a(void *);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t, const char *, const char *,
    const char *, uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *,
    const char *, ...);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
        ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static void gate_warn(uint32_t code) {
    static const char module[] = "page.mgr";
    static const char path[] =
        "D:\\01_workspace\\s200_ap510b_iar_git\\framework\\page_manager\\page_manager.c";
    static const char function[] = "page_manager_container_event_cb";
    static const char message[] = "enqueue page event failed, code=0x%X";
    static const char compact[] = "[page.mgr]enqueue page event failed, code=0x%X";
    if ((audio_log_level() & 2u) != 0u)
        audio_log_extended(2u, module, path, function, 0x481u, message, code);
    if ((audio_log_level() & 1u) != 0u || (audio_log_level() & 4u) != 0u)
        (void)compressed_log_output(0x08400000u, compact, compact, code);
}
static void callback_if_present(void *handler, void *page,
                                uint32_t code, void *event) {
    if (handler == 0) return;
    uint32_t call = get32((uint8_t *)handler + 24u);
    if (call != 0u)
        ((void (*)(void *, void *, uint32_t, void *))(uintptr_t)call)(
            handler, page, code, event);
}

/* Stock 0x0045F910 (page_manager_container_event_cb; body at 0x45f914 after 4 pad bytes) */
void audio_uart_page_event_45f914(void *event) {
    if (event == 0) return;
    uint8_t *e = (uint8_t *)event;
    uint8_t *page = (uint8_t *)(uintptr_t)get32(e + 12u);
    if (page == 0) return;
    uint32_t code = audio_uart_page_event_code_450286(event);
    if (page[0xe8u] != 0u || audio_uart_display_audio_is_active_45fcb2(page) != 0u) {
        if (code == 0x3cu || code == 0x3du || code == 0x3eu) {
            if (audio_uart_display_audio_gate_event_45fbe6(page, event) != 0u)
                return;
            gate_warn(code);
            return;
        }
    }
    uint8_t *parameter = (uint8_t *)(uintptr_t)get32(e + 16u);
    switch (code) {
    case 0x3cu:
        if (parameter != 0 && get32(parameter) != 0u)
            audio_uart_display_audio_queue_45f58c(page, get32(parameter));
        return;
    case 0x3du: {
        uint8_t *current = (uint8_t *)audio_uart_display_audio_current_45f8e6(page);
        if (current != 0)
            audio_uart_display_audio_activate_45f60e(page, get32(current));
        return;
    }
    case 0x3eu:
        if (parameter != 0) {
            uint32_t id = get32(parameter);
            if (id != 0u) {
                uint8_t *entry = (uint8_t *)audio_uart_display_audio_find_45f840(page, id);
                if (entry != 0 && entry[11u] == 1u)
                    audio_uart_display_audio_complete_45f73a(page, entry);
                else
                    audio_uart_display_audio_queue_45f58c(page, id);
            }
        }
        return;
    case 0x40u:
        callback_if_present(audio_uart_display_audio_handler_a_45f6a8(page),
                            page, code, event);
        callback_if_present(audio_uart_display_audio_handler_b_45f66a(page),
                            page, code, event);
        return;
    default:
        callback_if_present(audio_uart_display_audio_current_45f8e6(page),
                            page, code, event);
        return;
    }
}
