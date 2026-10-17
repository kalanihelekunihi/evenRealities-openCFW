/* Selected locale table with all five function slots C-relocated.
 * Two data pointer fields remain stock values pending source ownership. */
#include "display_ring_locale_dispatch_table.h"

extern uint32_t audio_uart_locale_ascii_lowercase_4d4368(uint32_t);
extern uint32_t audio_uart_locale_ascii_uppercase_4d436c(uint32_t);
extern uint32_t audio_uart_locale_ascii_alpha_4d436e(uint32_t);
extern uint32_t audio_uart_locale_ascii_space_4d4384(uint32_t);
extern uint32_t audio_uart_locale_ascii_lower_4d4398(uint32_t);

__attribute__((section(".data.opencfw.ring.locale_dispatch"), aligned(4), used))
volatile audio_uart_locale_dispatch_table audio_uart_ring_locale_dispatch_200044c0 = {
    .prefix = {0x0078f6d0u, 1u, 0x20004488u, 0u,
               (uintptr_t)&audio_uart_locale_ascii_alpha_4d436e,
               0u, (uintptr_t)&audio_uart_locale_ascii_lowercase_4d4368, 0u},
    .space = audio_uart_locale_ascii_space_4d4384,
    .after_space = (uintptr_t)&audio_uart_locale_ascii_uppercase_4d436c,
    .lower = audio_uart_locale_ascii_lower_4d4398
};
