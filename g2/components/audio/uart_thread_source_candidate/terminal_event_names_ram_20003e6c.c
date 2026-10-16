/* Stock terminal event-name lookup reads thirteen pointers at 0x20003e6c.
 * The observed extent is source-owned; startup contents remain unproven. */
#include <stdint.h>

const char *audio_terminal_event_names[13]
    __attribute__((section(".bss.opencfw.terminal.event_names"), aligned(4), used));

_Static_assert(sizeof audio_terminal_event_names == 52u,
               "terminal event-name pointer extent");
