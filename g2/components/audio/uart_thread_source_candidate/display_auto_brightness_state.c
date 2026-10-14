/* Apollo MAIN s200 v2.2.6.10 auto-brightness cells within the authenticated
 * zero-initializer range 0x20004558..0x20075047. Absolute RAM placement
 * remains a linker contract. */
#include <stdint.h>

volatile uint8_t audio_uart_auto_brightness_enabled_cell; /* 0x20072daa */
volatile uint32_t audio_uart_auto_brightness_profile_cell; /* 0x20072dac */
