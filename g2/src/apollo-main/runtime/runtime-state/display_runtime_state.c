/* Apollo MAIN s200 v2.2.6.10 display runtime cells in the authenticated
 * zero-initializer range 0x20004558..0x20075047. Absolute RAM placement
 * remains a linker contract. */
#include <stdint.h>

_Static_assert(sizeof(void *) == sizeof(uint32_t), "Apollo pointer width");

/* Both source paths identify RAM0x200744cc and store a pointer there. */
void *audio_uart_display_driver_interface; /* 0x200744cc */
extern uint32_t g2_display_state_cell
    __attribute__((alias("audio_uart_display_driver_interface")));

uint32_t audio_uart_display_audio_handle; /* 0x200744d0 */
volatile uint32_t audio_uart_user_registry_count; /* 0x200744d4 */
uint32_t audio_uart_display_active; /* 0x200744d8 */
uint32_t audio_uart_display_mode; /* 0x200744dc */
uint32_t audio_uart_display_background; /* 0x200744e0 */
