/* Bounded C ownership for two stock UI registry context pointers.
 * Rows 18 and 19 at 0x6a45d0/0x6a45e0 point at native RAM
 * 0x20003080/0x200030a0. Their event callbacks write a root pointer at +4.
 * Eight bytes is only the observed minimum, not the complete allocation. */
#include <stdint.h>

/* stock .data init word0 = registry id (0x10f / 0x10b) */
uint32_t audio_uart_registry_context_20003080[2] = {0x10fu, 0u};
uint32_t audio_uart_registry_context_200030a0[2] = {0x10bu, 0u};

_Static_assert(sizeof(audio_uart_registry_context_20003080) == 8u,
               "gray-screen observed context minimum");
_Static_assert(sizeof(audio_uart_registry_context_200030a0) == 8u,
               "production-test observed context minimum");
