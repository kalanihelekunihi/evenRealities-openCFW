/* Apollo MAIN s200 v2.2.6.10 Nema ring descriptor at 0x20073db0.
 * Five accessed words end at the next identified RAM object, 0x20073dc4.
 * Native startup zeroes this span; absolute placement remains a linker gate. */
#include <stdint.h>

volatile uint32_t audio_uart_nema_ring_descriptor[5];

_Static_assert(sizeof(audio_uart_nema_ring_descriptor) == 20u,
               "Nema ring descriptor extent");
