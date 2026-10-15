/* Apollo S200 brightness context byte getter at 0x46bfe8. */
#include <stdint.h>

uint32_t display_driver_uled_type0_context_46bfe8(void) {
    return *(volatile const uint8_t *)(uintptr_t)0x20072da9u;
}
