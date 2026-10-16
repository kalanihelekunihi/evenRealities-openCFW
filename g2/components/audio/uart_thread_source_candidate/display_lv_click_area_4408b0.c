/* Stock LVGL click area, 0x4408b0..0x4408d5. */
#include <stdint.h>

extern void audio_uart_lv_area_copy_43ee94(void *, const void *);
extern void audio_uart_lv_area_expand_450b98(void *, int32_t, int32_t);

void audio_uart_lv_get_click_area_4408b0(const void *object, void *area) {
    const uint8_t *bytes = (const uint8_t *)object;
    audio_uart_lv_area_copy_43ee94(area, bytes + 0x14u);
    const uint8_t *special =
        (const uint8_t *)(uintptr_t)*(const uint32_t *)(const void *)(bytes + 8u);
    if (special != 0) {
        const int32_t pad =
            *(const int32_t *)(const void *)(special + 0x28u);
        audio_uart_lv_area_expand_450b98(area, pad, pad);
    }
}
