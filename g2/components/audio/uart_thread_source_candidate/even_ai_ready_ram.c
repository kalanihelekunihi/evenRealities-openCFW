/* Bounded live RAM used by stock EvenAI async update 0x4e20f2.
 * Startup values and complete allocation extents remain separate gates.
 */
#include <stdint.h>

uint8_t audio_even_ai_ready_state_2006f138[0x218]
    __attribute__((section(".bss.opencfw.evenai.ready.state"), aligned(4), used));
uint32_t audio_even_ai_text_stream_handle_20074c04
    __attribute__((section(".bss.opencfw.evenai.text.handle"), aligned(4), used));
uint8_t audio_even_ai_text_pending_200f39b4[0x400]
    __attribute__((section(".bss.opencfw.evenai.text.pending"), aligned(4), used));
uint8_t audio_even_ai_text_merged_200f3db4[0x400]
    __attribute__((section(".bss.opencfw.evenai.text.merged"), aligned(4), used));

_Static_assert(sizeof(audio_even_ai_ready_state_2006f138) == 0x218u, "ready state");
_Static_assert(sizeof(audio_even_ai_text_stream_handle_20074c04) == 4u, "text handle");
_Static_assert(sizeof(audio_even_ai_text_pending_200f39b4) == 0x400u, "pending text");
_Static_assert(sizeof(audio_even_ai_text_merged_200f3db4) == 0x400u, "merged text");
