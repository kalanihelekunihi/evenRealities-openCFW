/* Apollo QuickList full-update path at 0x4f5718..0x4f5833. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_dashboard_ext_container_20074b9c[] __asm__("g2_dashboard_ext_container_20074b9c");
extern unsigned char g2ref_g2_quicklist_completed_201303cc[] __asm__("g2_quicklist_completed_201303cc");
extern unsigned char g2ref_g2_quicklist_event_fifo_20074e14[] __asm__("g2_quicklist_event_fifo_20074e14");
extern unsigned char g2ref_g2_quicklist_flag_20075041[] __asm__("g2_quicklist_flag_20075041");
extern unsigned char g2ref_g2_quicklist_page_active_20074e1c[] __asm__("g2_quicklist_page_active_20074e1c");
extern unsigned char g2ref_g2_quicklist_temp_cache_20130654[] __asm__("g2_quicklist_temp_cache_20130654");
extern unsigned char g2ref_g2_quicklist_ui_data_2012a72c[] __asm__("g2_quicklist_ui_data_2012a72c");
extern unsigned char g2ref_g2_quicklist_word_20074e28[] __asm__("g2_quicklist_word_20074e28");
extern unsigned char g2ref_g2_stock_ram_20101a18[] __asm__("g2_stock_ram_20101a18");

extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t); /* 0x43c0e4 */
extern void audio_quicklist_copy_record_4f55e0(const void *, void *);
extern void audio_quicklist_aux_update_4f6328(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "quicklist.page";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\quicklist\\ui_quicklist_page.c";
static const char function[] = "handle_full_update";
static const char message[] = "Full update: %d items";
static const char compact[] = "[quicklist.page]Full update: %d items";

uint32_t audio_quicklist_mode_one_4f5718(uint32_t detail) {
    (void)detail;
    uint8_t *const output = (uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_quicklist_ui_data_2012a72c);
    const uint8_t *const input = (const uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20101a18+0x4u);
    audio_uart_buffer_zero(output + 8u, 11840u, 0u);
    uint32_t count = 0u;
    if (*(const volatile uint8_t *)(const void *)(input + 0x1220u) != 0u) {
        for (uint32_t index = 0u; index < 20u && count < 40u; ++index) {
            const uint8_t *const item = input + 232u * index;
            if (*(const volatile uint8_t *)(const void *)(item + 228u) != 0u) {
                audio_quicklist_copy_record_4f55e0(item, output + 8u + 296u * count);
                ++count;
            }
        }
    }
    *(volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_quicklist_flag_20075041) = 1u;
    *(volatile uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_quicklist_word_20074e28) = (uint16_t)count;
    if (*(volatile uint16_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_quicklist_temp_cache_20130654+0x280u) != 0u &&
        *(volatile uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_quicklist_page_active_20074e1c) == 1u &&
        *(volatile uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_quicklist_event_fifo_20074e14) != 0u &&
        *(volatile uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_dashboard_ext_container_20074b9c) != 0u)
        audio_uart_buffer_zero((void *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_quicklist_temp_cache_20130654), 648u, 0u);
    if (*(volatile uint16_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_quicklist_completed_201303cc+0x280u) != 0u)
        audio_quicklist_aux_update_4f6328();
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 681u, message, (uint16_t)count);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10400000u, compact, compact, (uint16_t)count);
    return 0u;
}
