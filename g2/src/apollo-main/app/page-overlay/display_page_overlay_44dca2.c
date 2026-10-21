/* Apollo page overlay pointer lookup 0x44dca2..0x44dce1. The native
 * duplicate non-null check leaves the diagnostic arm unreachable. */
#include <stdint.h>

void *audio_uart_page_overlay_44dca2(const void *object) {
    if (object == 0)
        return 0;
    return *(void *const *)(const void *)((const uint8_t *)object + 4u);
}
