/* Three small handlers in the native UI registration table. */
#include <stdint.h>

extern void audio_uart_registry_child_466412(uint32_t payload,uint32_t length);
extern void audio_uart_registry_child_4c548c(uint32_t payload,uint16_t length);

uint32_t audio_uart_registry_callback_46687c(uint32_t event,
                                               uint32_t payload,
                                               uint32_t length) {
    if(event==5u) audio_uart_registry_child_466412(payload,length);
    return 0u;
}

uint32_t audio_uart_registry_callback_5f9ff8(uint32_t unused,
                                               uint32_t payload,
                                               uint32_t length) {
    (void)unused;
    audio_uart_registry_child_4c548c(payload,(uint16_t)length);
    return 0u;
}
