/* Apollo page-tree initialization 0x44d0f0..0x44d16d. */
#include <stdint.h>

extern void audio_uart_lv_mark_layout_43f648(void *);
extern void audio_uart_page_lock_44bde0(uint32_t);
extern void audio_uart_lv_theme_apply_482f8a(void *);
extern void audio_uart_page_descriptor_init_44d1fc(const void *, void *);
extern void audio_uart_page_style_refresh_44bc8c(void *, uint32_t, uint32_t);
extern void audio_uart_page_relayout_43ffa0(void *);
extern void *audio_uart_page_context_44d33a(void);
extern uint32_t audio_uart_page_needs_context_44d1cc(void *);
extern void audio_uart_page_attach_context_44d342(void *, void *);
extern void *audio_uart_page_overlay_44dca2(void *);
extern uint32_t audio_uart_lv_obj_event_451670(void *, uint32_t, void *);
extern void audio_uart_display_size_changed(void *);

void audio_uart_page_initialize_44d0f0(void *page) {
    if (page == 0)
        return;
    audio_uart_lv_mark_layout_43f648(page);
    audio_uart_page_lock_44bde0(0u);
    audio_uart_lv_theme_apply_482f8a(page);
    audio_uart_page_descriptor_init_44d1fc(*(const void *const *)page, page);
    audio_uart_page_lock_44bde0(1u);
    audio_uart_page_style_refresh_44bc8c(page, 0x000f0000u, 0xffu);
    audio_uart_page_relayout_43ffa0(page);
    void *const context = audio_uart_page_context_44d33a();
    if (context != 0 && audio_uart_page_needs_context_44d1cc(page) != 0u)
        audio_uart_page_attach_context_44d342(context, page);
    void *const overlay = audio_uart_page_overlay_44dca2(page);
    if (overlay != 0) {
        (void)audio_uart_lv_obj_event_451670(overlay, 0x2au, page);
        (void)audio_uart_lv_obj_event_451670(overlay, 0x2bu, page);
        audio_uart_display_size_changed(page);
    }
}
