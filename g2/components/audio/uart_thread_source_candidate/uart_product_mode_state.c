/* Minimum native-observed productMode state at 0x200038f0.
 * Native 0x4abe66 writes byte 0; native 0x4abe60 reads byte 1.
 * The full generated object extent and startup values remain unknown. */
#include <stdint.h>

volatile uint8_t g2_uart_product_mode_state[2]
    __attribute__((section(".g2_ram_200038f0")));
