/* Apollo audio animation ready callback, stock 0x45ecca..0x45ed4c. */
#include <stdint.h>

extern void *audio_uart_display_audio_find_owner_45fcd2(void *);
extern void audio_uart_display_audio_finalize(void);
extern void audio_uart_display_audio_dispatch_45fd06(void *);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *,
                                       const char *, ...);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
        ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}

static void missing_owner_warning(void) {
    static const char module[] = "page.mgr";
    static const char path[] =
        "D:\\01_workspace\\s200_ap510b_iar_git\\framework\\page_manager\\page_manager.c";
    static const char function[] = "page_anim_ready_cb";
    static const char message[] =
        "Cannot get manager pointer in animation complete callback";
    static const char compact[] =
        "[page.mgr]Cannot get manager pointer in animation complete callback";
    if ((audio_log_level() & 2u) != 0u)
        audio_log_extended(2u, module, path, function, 0x55u, message);
    if ((audio_log_level() & 1u) != 0u || (audio_log_level() & 4u) != 0u)
        (void)compressed_log_output(0x08000000u, compact, compact);
}

/* Stock 0x0045ECCA (page anim ready callback) */
void audio_uart_display_anim_finish_c_45eccb(void *descriptor) {
    uint8_t *page = (uint8_t *)(uintptr_t)get32((const uint8_t *)descriptor);
    uint8_t *entry = (uint8_t *)(uintptr_t)get32(page + 16u);
    entry[28] = 1u;
    uint8_t *owner = (uint8_t *)audio_uart_display_audio_find_owner_45fcd2(page);
    uint32_t callback = get32(entry + 24u);
    if (callback != 0u) {
        ((void (*)(void *, void *, uint32_t, uint32_t))(uintptr_t)callback)(
            entry, owner, 0x4du, 0u);
    }
    audio_uart_display_audio_finalize();
    if (owner != 0) {
        owner[0xe8u] = 0u;
        audio_uart_display_audio_dispatch_45fd06(owner);
    } else {
        missing_owner_warning();
    }
}
