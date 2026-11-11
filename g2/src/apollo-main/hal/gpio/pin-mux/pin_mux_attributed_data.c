/* Native Apollo Main literal targets for the mux source graph. This binds
 * pointer/address and immutable board words only; target RAM contents remain
 * live startup/runtime contracts. */
#include <stdint.h>
extern unsigned char g2ref_g2_stock_ram_20073320[] __asm__("g2_stock_ram_20073320"); /* Fix 44: stock owner of blob+offset access */
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_stock_ram_200001c8[] __asm__("g2_stock_ram_200001c8");
extern unsigned char g2ref_g2_stock_ram_20073298[] __asm__("g2_stock_ram_20073298");

volatile uint8_t *const audio_uart_mux_bitset=
    (volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20073320+0x4u); /* ROM 0x4c43dc */
const volatile uint8_t *const audio_uart_mux_capabilities=
    (const volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200001c8+0x4u); /* ROM 0x4c43e8 */
const uint32_t audio_uart_mux_group3_active_pin=3u; /* ROM 0x4c4678 -> 0x78ee34 */
const uint32_t audio_uart_mux_group3_idle_pin=3u;   /* ROM 0x4c467c -> 0x78ee38 */
volatile uint32_t *const audio_uart_mux_group4_power_word=
    (volatile uint32_t *)(uintptr_t)0x40004044u; /* ROM 0x4d3a08 */
