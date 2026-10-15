/* Native _xip_font_configure 0x46d29a workspace and state cells.
 * The external XIP font records remain at hardware addresses, not C data. */
#include <stdint.h>

__attribute__((section(".noinit.ring_config_workspace"),aligned(8)))
uint8_t audio_uart_ring_config_workspace[0x5000]; /* native 0x20324600 */
uint8_t audio_uart_ring_config_name[16];           /* native 0x20073e94 */
uint8_t audio_uart_ring_config_idle;               /* native 0x20074fe3 */

_Static_assert(sizeof(audio_uart_ring_config_workspace)==0x5000u,"glyph workspace");
