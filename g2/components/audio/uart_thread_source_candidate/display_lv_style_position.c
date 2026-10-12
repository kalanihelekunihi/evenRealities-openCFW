/* Native LVGL position getters 0x44b870/0x44b866 call the same authenticated
 * property fetcher with property IDs 2/1 and forward its R0 result. */
#include <stdint.h>
extern uint32_t audio_uart_lv_style_property_44bdea(void *,uint32_t,uint32_t);
uint32_t audio_uart_lv_style_position_a_44b870(void *object,uint32_t selector) {
    return audio_uart_lv_style_property_44bdea(object,selector,2u);
}
uint32_t audio_uart_lv_style_position_b_44b866(void *object,uint32_t selector) {
    return audio_uart_lv_style_property_44bdea(object,selector,1u);
}
