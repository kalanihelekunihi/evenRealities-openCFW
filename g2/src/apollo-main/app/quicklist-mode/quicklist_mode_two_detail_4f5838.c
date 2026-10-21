/* Apollo QuickList add-down path 0x4f5838..0x4f5a1b. */
#include <stdint.h>

extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t); /* 0x43c0e4 */
extern uint32_t audio_quicklist_select_records_4f5662(void *, uint32_t,
                                                       uint32_t *, uint32_t);
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t); /* 0x439be4 */
extern void audio_quicklist_copy_record_4f55e0(const void *, void *);
extern void audio_quicklist_aux_update_4f6328(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "quicklist.page";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\quicklist\\ui_quicklist_page.c";
static const char function[] = "handle_add_down";
static const char message[] = "Add down: %d items, total: %d";
static const char compact[] = "[quicklist.page]Add down: %d items, total: %d";

uint32_t audio_quicklist_mode_two_detail_4f5838(uint32_t detail) {
    (void)detail;
    uint8_t *const incoming = (uint8_t *)(uintptr_t)0x20367bd8u;
    uint8_t *const rows = (uint8_t *)(uintptr_t)0x2012a72cu;
    uint8_t *const scratch = (uint8_t *)(uintptr_t)0x2012d584u;
    uint8_t *const aux = (uint8_t *)(uintptr_t)0x20130654u;
    uint8_t *const removed = (uint8_t *)(uintptr_t)0x201303ccu;
    audio_uart_buffer_zero(incoming, 4640u, 0u);
    uint32_t selected = 0u;
    const uint32_t status = audio_quicklist_select_records_4f5662(incoming, 20u,
                                                                   &selected, 2u);
    if ((uint8_t)status != 0u)
        return (uint8_t)status;
    uint32_t old_count = *(volatile uint16_t *)(void *)rows;
    if (selected >= 1u) {
        if (selected + old_count >= 41u) {
            const uint32_t removed_rows = selected + old_count - 40u;
            for (uint32_t index = 0u; index < removed_rows; ++index) {
                const uint32_t id = *(volatile uint32_t *)(void *)(rows + 296u * index + 0x114u);
                const uint16_t aux_count = *(volatile uint16_t *)(void *)(aux + 0x280u);
                for (uint32_t position = 0u; position < aux_count; ++position) {
                    uint8_t *const entry = aux + 16u * position;
                    if (*(volatile uint32_t *)(void *)entry != id)
                        continue;
                    const uint16_t removed_count = *(volatile uint16_t *)(void *)(removed + 0x280u);
                    if (removed_count < 40u) {
                        uint8_t *const next = removed + 16u * removed_count;
                        *(volatile uint32_t *)(void *)next = id;
                        *(volatile uint32_t *)(void *)(next + 8u) =
                            *(volatile uint32_t *)(void *)(entry + 8u);
                        *(volatile uint32_t *)(void *)(next + 12u) =
                            *(volatile uint32_t *)(void *)(entry + 12u);
                        *(volatile uint16_t *)(void *)(removed + 0x280u) = (uint16_t)(removed_count + 1u);
                        for (uint32_t cursor = position; cursor + 1u < aux_count; ++cursor) {
                            uint8_t *const dst = aux + 16u * cursor;
                            const uint8_t *const src = dst + 16u;
                            for (uint32_t byte = 0u; byte < 16u; ++byte)
                                dst[byte] = src[byte];
                        }
                        *(volatile uint16_t *)(void *)(aux + 0x280u) = (uint16_t)(aux_count - 1u);
                    }
                    break;
                }
            }
            if (*(volatile uint16_t *)(void *)(removed + 0x280u) != 0u)
                audio_quicklist_aux_update_4f6328();
            old_count -= removed_rows;
            const uint32_t size = (uint16_t)old_count * 296u;
            (void)audio_queue_copy_bytes(scratch, rows + 8u + 296u * removed_rows, size);
            (void)audio_queue_copy_bytes(rows + 8u, scratch, size);
        }
        for (uint32_t index = 0u; index < selected; ++index)
            audio_quicklist_copy_record_4f55e0(incoming + 232u * index,
                                                rows + 8u + 296u * (old_count + index));
    }
    *(volatile uint8_t *)(uintptr_t)0x20075041u = 3u;
    *(volatile uint32_t *)(uintptr_t)0x20074e28u = selected;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 773u, message,
                           selected, (uint16_t)old_count);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10800000u, compact, compact,
                                    selected, (uint16_t)old_count);
    return 0u;
}
