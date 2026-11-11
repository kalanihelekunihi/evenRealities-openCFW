/* Apollo QuickList storage-to-UI mode dispatch 0x4f5e18..0x4f5e7b. */
#include <stdint.h>
extern unsigned char g2ref_g2_stock_ram_20102c38[] __asm__("g2_stock_ram_20102c38"); /* Fix 44: stock owner of blob+offset access */
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_quicklist_ui_data_2012a72c[] __asm__("g2_quicklist_ui_data_2012a72c");
extern unsigned char g2ref_g2_stock_ram_20101a18[] __asm__("g2_stock_ram_20101a18");

extern uint32_t audio_quicklist_mode_one_4f5718(uint32_t);
extern uint32_t audio_quicklist_mode_two_4f5a1c(uint32_t);
extern uint32_t audio_quicklist_mode_two_detail_4f5838(uint32_t);
extern uint32_t audio_quicklist_mode_three_4f5c4c(uint32_t);

uint32_t audio_quicklist_refresh_ready_4f5e18(void) {
    const uint8_t mode = *(volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20102c38+0x6u);
    const uint8_t detail = *(volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_quicklist_ui_data_2012a72c+0x2e4du);
    uint32_t result;
    if (mode == 1u)
        result = audio_quicklist_mode_one_4f5718(detail);
    else if (mode == 2u) {
        if (detail == 2u)
            result = audio_quicklist_mode_two_detail_4f5838(detail);
        else
            result = audio_quicklist_mode_two_4f5a1c(detail);
    } else if (mode == 3u)
        result = audio_quicklist_mode_three_4f5c4c(3u);
    else
        result = 3u;
    *(volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_quicklist_ui_data_2012a72c+0x2e4cu) = mode;
    return (uint8_t)result;
}
