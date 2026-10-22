/* Native UI registration callback 0x585cca, 22 Thumb bytes. */
#include <stdint.h>

extern int32_t navigation_data_dispatch(const uint8_t *data, uint32_t len); /* 0x5872f4 */

uint32_t audio_uart_registry_callback_585cca(uint32_t event,
                                               uint32_t payload,
                                               uint32_t length) {
    if(event==0u) (void)navigation_data_dispatch((const uint8_t *)(uintptr_t)payload,length);
    return 0u;
}
