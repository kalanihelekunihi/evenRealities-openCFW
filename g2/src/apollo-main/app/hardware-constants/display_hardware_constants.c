/* Apollo MAIN s200 v2.2.6.10 ROM literal-backed display register bases.
 * Each value is read from the authenticated OTA at the address in comment. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_audio_uart_display_lv_root[] __asm__("audio_uart_display_lv_root");

volatile uint8_t *const audio_uart_display_board_mmio =
    (volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_audio_uart_display_lv_root); /* 0x44d320 */
volatile uint8_t *const audio_uart_display_pin_low =
    (volatile uint8_t *)(uintptr_t)0xe000ed18u; /* 0x442cd0 */
volatile uint8_t *const audio_uart_display_pin_high =
    (volatile uint8_t *)(uintptr_t)0xe000e400u; /* 0x442ccc */
volatile uint32_t *const audio_uart_display_pin_set =
    (volatile uint32_t *)(uintptr_t)0xe000e100u; /* 0x442cc8 */
