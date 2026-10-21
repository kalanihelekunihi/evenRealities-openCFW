/* Apollo QuickList modify path 0x4f5c4c..0x4f5e11. */
#include <stdint.h>

extern void audio_quicklist_copy_record_4f55e0(const void *, void *);
extern int32_t audio_quicklist_find_record_4f5636(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "quicklist.page";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\quicklist\\ui_quicklist_page.c";
static const char function[] = "handle_modify";
static const char message[] = "Modify: total: %d";
static const char compact[] = "[quicklist.page]Modify: total: %d";

uint32_t audio_quicklist_mode_three_4f5c4c(uint32_t detail) {
    (void)detail;
    const uint8_t *const input = (const uint8_t *)(uintptr_t)0x20101a1cu;
    uint8_t *const rows = (uint8_t *)(uintptr_t)0x2012a72cu;
    volatile uint8_t *const state = (volatile uint8_t *)(uintptr_t)0x20075041u;
    volatile uint32_t *const count_word = (volatile uint32_t *)(uintptr_t)0x20074e28u;
    *state = 4u;
    *count_word = 0u;
    if (*(const volatile uint8_t *)(const void *)(input + 0x1220u) == 0u)
        return 5u;
    const uint16_t old_count = *(volatile uint16_t *)(void *)rows;
    uint32_t inserted = 0u;
    uint32_t matched = 0u;
    uint32_t missing = 0u;
    if (old_count == 0u) {
        for (uint32_t index = 0u; index < 20u && inserted < 40u; ++index) {
            const uint8_t *const item = input + 232u * index;
            if (*(const volatile uint8_t *)(const void *)(item + 228u) != 0u) {
                audio_quicklist_copy_record_4f55e0(item, rows + 8u + 296u * inserted);
                ++inserted;
            }
        }
        *state = 1u;
        matched = inserted;
    } else {
        for (uint32_t index = 0u; index < 20u; ++index) {
            const uint8_t *const item = input + 232u * index;
            if (*(const volatile uint8_t *)(const void *)(item + 228u) == 0u)
                continue;
            const uint32_t id = *(const volatile uint32_t *)(const void *)item;
            const int32_t slot = audio_quicklist_find_record_4f5636(id);
            if (slot >= 0) {
                audio_quicklist_copy_record_4f55e0(item, rows + 8u + 296u * (uint32_t)slot);
                ++matched;
            } else {
                *state = 2u;
                ++missing;
                if (old_count < 40u) {
                    for (uint32_t move = old_count; move > 0u; --move) {
                        uint8_t *const destination = rows + 8u + 296u * move;
                        const uint8_t *const source = destination - 296u;
                        for (uint32_t byte = 0u; byte < 296u; ++byte)
                            destination[byte] = source[byte];
                    }
                    ++inserted;
                }
                audio_quicklist_copy_record_4f55e0(item, rows + 8u);
            }
        }
    }
    if (*state == 4u || *state == 1u)
        *count_word = matched;
    else if (*state == 2u)
        *count_word = missing;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 983u, message,
                           (uint16_t)inserted);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10400000u, compact, compact,
                                    (uint16_t)inserted);
    return 0u;
}
