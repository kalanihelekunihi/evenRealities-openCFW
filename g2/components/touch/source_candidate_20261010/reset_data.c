#include <stdint.h>

/* Locked reset-copy initializer, corroborated by vendor system_cat2.c's
 * 24 MHz default-clock formulas. Runtime SystemInit updates are separate. */
#define TOUCH_RESET_CLOCK_HZ 24000000u
#define TOUCH_CEIL_DIV(n, d) (((n) + (d) - 1u) / (d))
#define TOUCH_RESET_KHZ TOUCH_CEIL_DIV(TOUCH_RESET_CLOCK_HZ, 1000u)
#define TOUCH_RESET_MHZ TOUCH_CEIL_DIV(TOUCH_RESET_CLOCK_HZ, 1000000u)
_Static_assert(TOUCH_RESET_KHZ == 24000u, "reset kHz");
_Static_assert(TOUCH_RESET_MHZ == 24u, "reset MHz");
_Static_assert(32768u * TOUCH_RESET_KHZ == 0x2ee00000u, "reset 32k scale");

uint32_t cy_delay32kMs = 32768u * TOUCH_RESET_KHZ;
uint8_t cy_delayFreqMhz = (uint8_t)TOUCH_RESET_MHZ;
uint32_t cy_delayFreqKhz = TOUCH_RESET_KHZ;
