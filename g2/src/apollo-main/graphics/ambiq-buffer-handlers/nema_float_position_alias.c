/* The Ambiq mask path and selected display driver both call native 0x5228b0. */
extern void display_driver_nema_float_translate_5228b0(float, float)
    __attribute__((pcs("aapcs-vfp")));
void audio_uart_nema_float_position_5228b0(float x, float y)
    __attribute__((pcs("aapcs-vfp")));
void audio_uart_nema_float_position_5228b0(float x, float y) {
    display_driver_nema_float_translate_5228b0(x, y);
}
