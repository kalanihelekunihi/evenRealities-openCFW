/* Production-test (PDT) screen helpers: distortion 0x5cf2b4..0x5cf32f,
 * gray-screen 0x5cf67a..0x5cf67d, production-test 0x5cf7ee..0x5cf7f1.
 * The screen-event builders themselves are in
 * drivers/display/distortion-screen, app/gray-screen and
 * drivers/display/production-test. */
#include <stdint.h>

/* LVGL 9.3 lv_obj_set_style_pad_{left,right,top,bottom} (props 0x12, 0x13,
 * 0x10, 0x11), native 0x44122a/0x441238/0x44120e/0x44121c. */
extern void audio_uart_page_44122a(void *object, uint32_t value, uint32_t selector);
extern void audio_uart_page_441238(void *object, uint32_t value, uint32_t selector);
extern void audio_uart_page_44120e(void *object, uint32_t value, uint32_t selector);
extern void audio_uart_page_44121c(void *object, uint32_t value, uint32_t selector);

/* Out-of-line copy of LVGL's static inline lv_obj_set_style_pad_all emitted
 * in the distortion-test unit (same body as 0x45ec7c). */
void semantic_zero_four_object_styles(void *object, uint32_t value, uint32_t selector) {
    audio_uart_page_44122a(object, value, selector);
    audio_uart_page_441238(object, value, selector);
    audio_uart_page_44120e(object, value, selector);
    audio_uart_page_44121c(object, value, selector);
}

/* Page-registry "available" callbacks: each PDT page is always enabled.
 * The distortion one is defined once, as
 * semantic_distortion_predicate_true_5cf32c in
 * drivers/display/distortion-screen/distortion_screen_event_5cf330.c. */

uint32_t semantic_gray_screen_predicate_true(void) {
    return 1;
}

uint32_t semantic_production_test_predicate_true(void) {
    return 1;
}
