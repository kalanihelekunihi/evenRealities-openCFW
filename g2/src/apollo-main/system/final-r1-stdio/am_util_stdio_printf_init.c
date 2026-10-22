/* AmbiqSuite R3.2.0 utils/am_util_stdio.c am_util_stdio_printf_init (BSD-3-Clause,
 * Ambiq Micro), native 0x472c7c..0x472c84; literal 0x47345c -> RAM 0x200742f0.
 *
 * The rest of the stock am_util_stdio translation unit (0x472c84..0x47346x)
 * is the selected hand copy g2/src/apollo-main/system/log/main-formatter/format.c,
 * which reads the same g_pfnCharPrint cell by address. Stock callers pass the
 * shell output hook (0x5415c2) or NULL (am_bsp low-power path). */
#include <stdint.h>

/* g_pfnCharPrint, RAM 0x200742f0 (defined in app/board-callback). */
extern volatile uint32_t audio_uart_stdio_print_char_cell_200742f0;

void log_output_hook_set_472c7c(void (*hook)(const char *text));

void log_output_hook_set_472c7c(void (*hook)(const char *text))
{
    audio_uart_stdio_print_char_cell_200742f0 = (uint32_t)(uintptr_t)hook;
}
