/* Apollo Main input unlink 0x44df60..0x44df7f and its immediate
 * flag accessors 0x452f0c..0x452f17, 0x452fec..0x452ff9. */
#include <stdint.h>

extern void audio_uart_lv_input_clear_452f26(void *, void *);

uint32_t audio_uart_lv_input_has_activity_452f0c(const void *input) {
    return input == 0 ? 0u : *((const uint8_t *)input + 8u);
}

void audio_uart_lv_input_set_reset_452fec(void *input) {
    if (input != 0) {
        uint8_t *bytes = (uint8_t *)input;
        bytes[0x0bu] = (uint8_t)(bytes[0x0bu] | 8u);
    }
}

void audio_uart_lv_input_unlink_44df60(void *input, void *object) {
    if ((uint8_t)audio_uart_lv_input_has_activity_452f0c(input) != 0u)
        audio_uart_lv_input_set_reset_452fec(input);
    audio_uart_lv_input_clear_452f26(input, object);
}
