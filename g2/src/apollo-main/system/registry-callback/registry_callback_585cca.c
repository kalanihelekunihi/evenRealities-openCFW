/* Native UI registration callback 0x585cca, 22 Thumb bytes. */
#include <stdint.h>

extern void audio_uart_registry_child_5872f4(uint32_t payload,uint32_t length);

uint32_t audio_uart_registry_callback_585cca(uint32_t event,
                                               uint32_t payload,
                                               uint32_t length) {
    if(event==0u) audio_uart_registry_child_5872f4(payload,length);
    return 0u;
}
