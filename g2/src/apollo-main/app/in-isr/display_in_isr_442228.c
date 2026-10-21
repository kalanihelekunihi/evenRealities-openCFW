/* Apollo Main ISR query, native 0x442228..0x442237.
 * The stock instructions read IPSR and return whether it is nonzero. */
#include <stdint.h>

uint32_t audio_uart_display_in_isr_442228(void) {
    uint32_t ipsr;
    __asm__ volatile("mrs %0, ipsr" : "=r"(ipsr));
    return ipsr != 0u;
}
