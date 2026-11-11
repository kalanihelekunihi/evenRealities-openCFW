/* Apollo QuickList record ID lookup at 0x4f5636..0x4f5661. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_quicklist_ui_data_2012a72c[] __asm__("g2_quicklist_ui_data_2012a72c");

int32_t audio_quicklist_find_record_4f5636(uint32_t id) {
    const volatile uint8_t *const rows = (const volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_quicklist_ui_data_2012a72c);
    const uint16_t count = *(const volatile uint16_t *)(const void *)rows;
    for (uint32_t index = 0u; index < count; ++index) {
        const uint32_t candidate = *(const volatile uint32_t *)(const void *)(
            rows + 296u * index + 0x114u);
        if (candidate == id)
            return (int32_t)index;
    }
    return -1;
}
