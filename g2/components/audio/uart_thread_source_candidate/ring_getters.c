/* Native direct product-state getters at 0x466518 and 0x45a568. */
#include <stdint.h>

extern const volatile uint8_t *const audio_uart_hand_context; /* DAT_004667ec */
extern volatile uint8_t audio_uart_device_role_cell; /* *DAT_0045b0f4 */

uint8_t audio_uart_hand_side_get(void) {
    return audio_uart_hand_context[11];
}

uint8_t audio_uart_device_role_get(void) {
    return audio_uart_device_role_cell;
}
