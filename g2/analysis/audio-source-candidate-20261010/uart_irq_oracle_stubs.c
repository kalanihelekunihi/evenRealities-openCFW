/* Fixture-only lower-entry boundaries. Never select into the audio archive. */
#include <stdint.h>
#define BOUNDARY __attribute__((naked,noinline,used))
BOUNDARY void uart_irq_delay_us(uint32_t n) { __asm__("bx lr"); }
