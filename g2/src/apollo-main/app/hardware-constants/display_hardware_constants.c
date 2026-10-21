/* Apollo MAIN s200 v2.2.6.10 ROM literal-backed display register bases.
 * Each value is read from the authenticated OTA at the address in comment. */
#include <stdint.h>

volatile uint8_t *const audio_uart_display_board_mmio =
    (volatile uint8_t *)(uintptr_t)0x2006f548u; /* 0x44d320 */
volatile uint8_t *const audio_uart_display_engine_mmio =
    (volatile uint8_t *)(uintptr_t)0x40008000u; /* 0x471ed0 */
const uint32_t audio_uart_display_format_mask = 0x0001ff00u; /* 0x471ecc */
volatile uint32_t *const audio_uart_display_enable_word =
    (volatile uint32_t *)(uintptr_t)0x40008060u; /* 0x471edc */
volatile uint8_t *const audio_uart_display_pin_low =
    (volatile uint8_t *)(uintptr_t)0xe000ed18u; /* 0x442cd0 */
volatile uint8_t *const audio_uart_display_pin_high =
    (volatile uint8_t *)(uintptr_t)0xe000e400u; /* 0x442ccc */
volatile uint32_t *const audio_uart_display_pin_set =
    (volatile uint32_t *)(uintptr_t)0xe000e100u; /* 0x442cc8 */
