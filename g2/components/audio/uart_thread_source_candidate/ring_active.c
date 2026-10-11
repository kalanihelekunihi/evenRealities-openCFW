/* Native central_is_ring_owner_side at 0x4a2914. */
#include <stdint.h>

extern uint8_t audio_uart_hand_side_get(void); /* 0x466518, byte at product +11 */
extern uint8_t audio_uart_device_role_get(void); /* 0x45a568 */

uint32_t audio_uart_ring_active(void) {
    uint8_t hand=audio_uart_hand_side_get();
    uint8_t role=audio_uart_device_role_get();
    return ((hand==1u && role==1u) || (hand==0u && role==2u)) ? 1u : 0u;
}
