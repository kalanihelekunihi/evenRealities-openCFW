/* Apollo PageManager_SetAnimationMode, stock 0x45fe10..0x45fe86. */
#include <stdint.h>

extern uint8_t *audio_uart_display_page_manager; /* RAM 0x20074858 */
extern void *audio_uart_display_audio_find_45f840(void *, uint32_t);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "page.mgr";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\framework\\page_manager\\page_manager.c";
static const char function[] = "PageManager_SetAnimationMode";
static const char message[] = "set animation mode failed, manager is null";
static const char compact[] =
    "[page.mgr]set animation mode failed, manager is null";

uint32_t audio_uart_display_audio_set_mode_child_45fe10(
    void *manager, uint32_t id, uint32_t mode) {
    if (manager == 0 || id == 0u) return 0u;
    uint8_t *entry = (uint8_t *)audio_uart_display_audio_find_45f840(manager, id);
    if (entry == 0) return 0u;
    entry[10] = (uint8_t)mode;
    return 1u;
}

uint32_t audio_uart_display_audio_set_mode_45fe32(uint32_t id, uint32_t mode) {
    if (audio_uart_display_page_manager != 0)
        return audio_uart_display_audio_set_mode_child_45fe10(
            audio_uart_display_page_manager, id, (uint8_t)mode);
    if ((audio_log_level() & 2u) != 0u)
        audio_log_extended(1u, module, path, function, 0x70fu, message);
    if ((audio_log_level() & 1u) != 0u || (audio_log_level() & 4u) != 0u)
        (void)compressed_log_output(0x04000000u, compact, compact);
    return 0u;
}
