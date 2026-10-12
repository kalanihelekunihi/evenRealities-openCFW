/* Native Apollo Main literal targets for the mux source graph. This binds
 * pointer/address and immutable board words only; target RAM contents remain
 * live startup/runtime contracts. */
#include <stdint.h>

volatile uint8_t *const audio_uart_mux_bitset=
    (volatile uint8_t *)(uintptr_t)0x20073324u; /* ROM 0x4c43dc */
const volatile uint8_t *const audio_uart_mux_capabilities=
    (const volatile uint8_t *)(uintptr_t)0x200001ccu; /* ROM 0x4c43e8 */
const uint32_t audio_uart_mux_group3_active_pin=3u; /* ROM 0x4c4678 -> 0x78ee34 */
const uint32_t audio_uart_mux_group3_idle_pin=3u;   /* ROM 0x4c467c -> 0x78ee38 */
volatile uint32_t *const audio_uart_mux_group4_power_word=
    (volatile uint32_t *)(uintptr_t)0x40004044u; /* ROM 0x4d3a08 */
