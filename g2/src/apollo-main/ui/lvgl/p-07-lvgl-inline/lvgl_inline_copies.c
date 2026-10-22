/* Out-of-line copies of LVGL 9.3 header `static inline` helpers, emitted by IAR
 * once per including translation unit (stock source tree
 * D:\01_workspace\s200_ap510b_iar_git\third_party\lvgl_v9.3\LVGL\src\...).
 *
 *   0x484380..0x48438c  lv_memzero              (src/stdlib/lv_string.h, in lv_draw.c)
 *   0x48890c..0x488918  lv_memzero              (src/stdlib/lv_string.h, in lv_draw_image.c)
 *
 * The lv_draw_label.c copies (lv_memzero 0x489ec8, lv_bidi_calculate_align
 * 0x489ed4, lv_text_is_marker 0x489ee0) come from the upstream lv_draw_label.c
 * unit compiled with -fno-inline.
 *
 * Bodies match the pinned upstream (third-party/upstream/lvgl @ 344c7c31). The
 * header functions cannot be added as standalone upstream units, so each stock
 * copy is anchored here under an address-suffixed name. */
#include <stdint.h>
#include <stddef.h>

/* lv_memset(dst, value, len), stock 0x454746 (name from existing g2/src units). */
extern void audio_uart_lv_basic_box_clear_454746(void *dst, uint32_t value, uint32_t len);

void lv_memzero_484380(void *dst, uint32_t len)
{
    audio_uart_lv_basic_box_clear_454746(dst, 0u, len);
}

void lv_memzero_48890c(void *dst, uint32_t len)
{
    audio_uart_lv_basic_box_clear_454746(dst, 0u, len);
}



