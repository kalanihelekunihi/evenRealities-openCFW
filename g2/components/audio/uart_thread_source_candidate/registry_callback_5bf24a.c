/* Registry row 0x109, native 0x5bf24a: empty receive callback. */
#include <stdint.h>

uint32_t audio_uart_registry_callback_5bf24a(uint32_t event,
                                               const void *payload,
                                               uint32_t length) {
    (void)event;
    (void)payload;
    (void)length;
    return 0u;
}
