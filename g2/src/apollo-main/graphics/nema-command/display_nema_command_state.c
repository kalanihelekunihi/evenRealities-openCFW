/* Apollo MAIN s200 v2.2.6.10 Nema command state.
 * Six BSS words end at the next identified object, 0x20073c08.
 * The last-submission sentinel is in the authenticated decompressed
 * 0x20000000 initializer image. Final placement remains a linker gate. */
#include <stdint.h>

volatile uint32_t audio_uart_nema_command_state_20073bf0[6]; /* 0x20073bf0 */
volatile uint32_t audio_uart_nema_last_submission = UINT32_MAX; /* 0x20002e08 */

_Static_assert(sizeof(audio_uart_nema_command_state_20073bf0) == 24u,
               "Nema command-state extent");
