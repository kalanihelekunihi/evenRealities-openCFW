/* Native init_ui_modules 0x4425a6 clamps the ROM registration count to
 * 128 rows of 16 bytes before copying to RAM 0x20066230. */
#include <stdint.h>

uint8_t audio_uart_user_registry_rows[128][16];
_Static_assert(sizeof(audio_uart_user_registry_rows)==0x800u,"registry capacity");
