/* Reconstructed from locked bootloader 0x4181e4 / 0x418a00.
 * Fixed-address kernel snapshot only; no physical timer assumption. */
#include <stdint.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
uint32_t expected_idle_ticks(void) {
 uint32_t other_ready = W(0x2002714c) != 0;
 uintptr_t current = W(0x20027134);
 if (W(current + 0x2c) != 0) return 0;
 if (W(0x20024870) >= 2) return 0;
 if (other_ready) return 0;
 return W(0x20027164) - W(0x20027148);
}
uint32_t confirm_sleep(void) {
 if (W(0x20026f5c) != 0) return 0;
 if (W(0x20027158) != 0) return 0;
 if (W(0x20027154) != 0) return 0;
 return W(0x20026f84) == W(0x20027144) - 1 ? 2 : 1;
}
