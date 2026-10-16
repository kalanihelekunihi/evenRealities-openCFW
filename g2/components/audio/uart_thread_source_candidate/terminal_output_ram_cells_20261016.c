/* Source-owned stock Terminal output RAM cells. */
#include <stdint.h>

uint32_t audio_terminal_output_payload_20074a94
    __attribute__((section(".bss.opencfw.terminal.output_payload"), used, aligned(4)));
uint8_t audio_terminal_output_active_2007502c
    __attribute__((section(".bss.opencfw.terminal.output_active"), used, aligned(1)));
uint8_t audio_terminal_output_mode_2007502d
    __attribute__((section(".bss.opencfw.terminal.output_mode"), used, aligned(1)));

_Static_assert(sizeof audio_terminal_output_payload_20074a94 == 4u,
               "stock output payload cell");
_Static_assert(sizeof audio_terminal_output_active_2007502c == 1u,
               "stock output active cell");
_Static_assert(sizeof audio_terminal_output_mode_2007502d == 1u,
               "stock output mode cell");
