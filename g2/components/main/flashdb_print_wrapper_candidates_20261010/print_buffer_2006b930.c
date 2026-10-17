/* Stock Ambiq stdio print scratch at 0x2006b930. The pinned SDK default
 * AM_PRINTF_BUFSIZE is 1024; the known dump buffer starts at 0x2006bd30.
 * Formatter output is not globally capacity bounded and remains a gate. */
#include <stdint.h>

__attribute__((used, section(".g2_print_buffer_2006b930"), aligned(4)))
uint8_t g2_flashdb_print_buffer[1024];

_Static_assert(sizeof g2_flashdb_print_buffer == 1024u,
               "Ambiq stdio print scratch span");
