/* Relocatable C implementation of the two accessed locale callback slots.
 * Other stock pointer fields retain their observed values pending ownership. */
#include "display_ring_locale_dispatch_table.h"

extern uint32_t audio_uart_locale_ascii_space_4d4384(uint32_t);
extern uint32_t audio_uart_locale_ascii_lower_4d4398(uint32_t);

__attribute__((section(".data.opencfw.ring.locale_dispatch"), aligned(4), used))
volatile audio_uart_locale_dispatch_table audio_uart_ring_locale_dispatch_200044c0 = {
    .prefix = {0x0078f6d0u, 1u, 0x20004488u, 0u,
               0x004d436fu, 0u, 0x004d4369u, 0u},
    .space = audio_uart_locale_ascii_space_4d4384,
    .after_space = 0x004d436du,
    .lower = audio_uart_locale_ascii_lower_4d4398
};
