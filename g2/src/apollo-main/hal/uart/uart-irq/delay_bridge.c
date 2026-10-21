/* ABI bridge to the source-backed Ambiq microsecond delay entry. */
#include <stdint.h>
extern void audio_delay_us(uint32_t);
void uart_irq_delay_us(uint32_t microseconds) { audio_delay_us(microseconds); }
