/* Display-context registry getter, native 0x460106..0x460117 (literal 0x46011c).
 * Companion of audio_uart_display_context_set 0x460090 and the name lookup
 * 0x4600b4 (app/context-locale/display_context_locale.c): each registry entry
 * starts with its name string, compared with strcmp 0x46cacc by 0x4600b4.
 * Caller 0x443690. */
#include <stdint.h>
#include <stddef.h>

extern const void *audio_uart_display_context_active_cell; /* RAM 0x200746cc */

/* Name (first word) of the active context entry, or NULL when none is active. */
const char *display_context_active_name_get_460106(void)
{
    if (audio_uart_display_context_active_cell == NULL)
        return NULL;
    return *(const char *const *)audio_uart_display_context_active_cell;
}
