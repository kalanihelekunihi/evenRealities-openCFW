/* Native UI registration callback 0x48e484 (16 Thumb bytes).
 * r0 is ignored; r1 becomes child r0, low half of r2 becomes child r1. */
#include <stdint.h>

extern void audio_uart_registry_child_497960(uint32_t payload,uint16_t length);

uint32_t audio_uart_registry_callback_48e484(uint32_t unused,
                                               uint32_t payload,
                                               uint32_t length) {
    (void)unused;
    audio_uart_registry_child_497960(payload,(uint16_t)length);
    return 0u;
}
