/* Stock Terminal row image position, color and source selectors. */
#include <stdint.h>
extern unsigned char g2ref_audio_terminal_asset_7733a8[] __asm__("audio_terminal_asset_7733a8"); /* Fix 49: stock flash word owner */
extern unsigned char g2ref_audio_terminal_query_image_770890[] __asm__("audio_terminal_query_image_770890"); /* Fix 49: stock flash word owner */
extern unsigned char g2ref_audio_terminal_result_icon_773258[] __asm__("audio_terminal_result_icon_773258"); /* Fix 49: stock flash word owner */

extern uint32_t audio_terminal_row_image_hint_5ea4f0(uint32_t index, uint32_t item);

uint32_t audio_terminal_image_y_5ea2b0(void) {
    return 6u; /* (0x1c - 0x10) / 2 */
}

uint32_t audio_terminal_row_color_5ea2f2(uint32_t item) {
    if (item == 0u)
        return 0u;
    uint8_t kind = *(const uint8_t *)(const void *)(uintptr_t)item;
    return kind == 1u || kind == 3u ? 1u : 0u;
}

uint32_t audio_terminal_row_image_5ea524(uint32_t index, uint32_t item) {
    const uint8_t *record = (const uint8_t *)(uintptr_t)item;
    uint8_t kind = record[1];
    if (kind == 1u)
        return (uint32_t)(uintptr_t)g2ref_audio_terminal_asset_7733a8;
    if (kind == 2u)
        return (uint32_t)(uintptr_t)g2ref_audio_terminal_query_image_770890;
    if (kind != 0u)
        return 0u;
    if (audio_terminal_row_image_hint_5ea4f0((uint16_t)index, item) != 0u ||
        audio_terminal_row_color_5ea2f2(item) != 0u)
        return (uint32_t)(uintptr_t)g2ref_audio_terminal_result_icon_773258;
    return 0u;
}
