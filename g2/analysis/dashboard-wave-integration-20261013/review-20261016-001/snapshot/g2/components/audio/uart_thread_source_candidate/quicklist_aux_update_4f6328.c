/* Apollo QuickList completed-UID batch sender, 0x4f6328..0x4f657d.
 * Packet fields and RAM addresses are bound to the authenticated Main image.
 */
#include <stdint.h>

extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t); /* 0x43c0e4 */
extern uint32_t audio_quicklist_send_completed_5591b0(uint32_t, const void *);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "quicklist.page";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\quicklist\\ui_quicklist_page.c";
static const char function[] = "quicklist_send_completed_uids";
static const char empty_message[] = "No completed UIDs to send";
static const char empty_compact[] = "[quicklist.page]No completed UIDs to send";
static const char start_message[] = "Sending %d completed UIDs in %d batches";
static const char start_compact[] = "[quicklist.page]Sending %d completed UIDs in %d batches";
static const char fail_message[] = "Failed to send completed UIDs batch %d, result: %d";
static const char fail_compact[] = "[quicklist.page]Failed to send completed UIDs batch %d, result: %d";
static const char done_message[] = "Successfully sent completed UIDs batch %d (%d items)";
static const char done_compact[] = "[quicklist.page]Successfully sent completed UIDs batch %d (%d items)";

uint32_t audio_quicklist_aux_update_4f6328(void) {
    uint8_t *const completed = (uint8_t *)(uintptr_t)0x201303ccu;
    const uint32_t count = *(volatile uint16_t *)(uintptr_t)0x2013064cu;
    if (count == 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(4u, module, path, function, 1218u, empty_message);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x10000000u, empty_compact, empty_compact);
        return 0u;
    }

    const uint32_t batches = (count + 19u) / 20u;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 1234u, start_message,
                           count, batches);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10800000u, start_compact, start_compact,
                                    count, batches);

    uint32_t offset = 0u;
    for (uint32_t batch = 0u; batch < batches; ++batch) {
        const uint32_t remaining = count - offset;
        const uint32_t items = remaining < 21u ? remaining : 20u;
        uint8_t packet[0x1230];
        audio_uart_buffer_zero(packet, sizeof packet, 0u);
        packet[0] = 3u;
        packet[1] = (uint8_t)count;
        *(uint16_t *)(void *)(packet + 2u) = (uint16_t)items;
        packet[0x1228u] = 0u;
        for (uint32_t index = 0u; index < items; ++index) {
            const uint8_t *const entry = completed + (offset + index) * 16u;
            uint8_t *const record = packet + 8u + index * 232u;
            *(uint32_t *)(void *)(record + 0u) = *(volatile uint32_t *)(const void *)(entry + 0u);
            *(uint32_t *)(void *)(record + 4u) = 0u;
            *(uint32_t *)(void *)(record + 8u) = 1u;
            *(uint32_t *)(void *)(record + 16u) = *(volatile uint32_t *)(const void *)(entry + 8u);
            *(uint32_t *)(void *)(record + 20u) = *(volatile uint32_t *)(const void *)(entry + 12u);
            record[24u] = 0u;
            record[228u] = 0u;
        }
        const uint32_t result = audio_quicklist_send_completed_5591b0(0u, packet);
        if (result != 0u) {
            if ((audio_log_flags() & 2u) != 0u)
                audio_log_extended(1u, module, path, function, 1265u, fail_message,
                                   batch, result);
            if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
                (void)compressed_log_output(0x04800000u, fail_compact, fail_compact,
                                            batch, result);
            return UINT32_MAX;
        }
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(4u, module, path, function, 1269u, done_message,
                               batch, items);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x10800000u, done_compact, done_compact,
                                        batch, items);
        offset += items;
    }
    audio_uart_buffer_zero(completed, 0x288u, 0u);
    return 0u;
}
