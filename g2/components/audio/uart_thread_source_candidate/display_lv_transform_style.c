/* Native Main 0x43ef2a/34/3e and 0x43f07e/8c style accessors. */
#include <stdint.h>
extern uint32_t audio_uart_lv_style_property_44bdea(void *,uint32_t,uint32_t);
int32_t audio_uart_lv_transform_angle_43ef2a(void *object,uint32_t selector) {
    return (int32_t)audio_uart_lv_style_property_44bdea(object,selector,0x70u);
}
uint32_t audio_uart_lv_transform_pivot_x_43ef34(void *object,uint32_t selector) {
    return audio_uart_lv_style_property_44bdea(object,selector,0x71u);
}
uint32_t audio_uart_lv_transform_pivot_y_43ef3e(void *object,uint32_t selector) {
    return audio_uart_lv_style_property_44bdea(object,selector,0x72u);
}
int32_t audio_uart_lv_transform_scale_x_43f07e(void *object,uint32_t selector) {
    int32_t value=(int32_t)audio_uart_lv_style_property_44bdea(object,selector,0x6eu);
    return value<1?1:value;
}
int32_t audio_uart_lv_transform_scale_y_43f08c(void *object,uint32_t selector) {
    int32_t value=(int32_t)audio_uart_lv_style_property_44bdea(object,selector,0x6fu);
    return value<1?1:value;
}
