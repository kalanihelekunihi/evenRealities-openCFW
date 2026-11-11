/* Native _xip_font_configure 0x46d29a workspace and state cells.
 * The external XIP font records remain at hardware addresses, not C data. */
#include <stdint.h>

/* Fix 43 (RAM-init, 2026-11-01): native 0x20324600 is inside the stock SSRAM
 * startup zero range (reaches 0x2037ce44), so stock cstartup clears this glyph
 * workspace at boot. Holding it in .noinit left it uninitialised: zero in the
 * Renode simulator, random on hardware. Plain zero-init (.bss) so the g2c
 * region table clears it at boot, matching stock. */
__attribute__((aligned(8)))
uint8_t audio_uart_ring_config_workspace[0x5000]; /* native 0x20324600 */
uint8_t audio_uart_ring_config_name[16];           /* native 0x20073e94 */
uint8_t audio_uart_ring_config_idle;               /* native 0x20074fe3 */

_Static_assert(sizeof(audio_uart_ring_config_workspace)==0x5000u,"glyph workspace");
