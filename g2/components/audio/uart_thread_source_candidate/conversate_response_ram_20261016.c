/* Stock Conversate frame at 0x200f4808 and encoded buffer at 0x2037c2a0. */
#include <stdint.h>
__attribute__((used, section(".g2_conversate_response_frame_200f4808"), aligned(4)))
uint8_t audio_conversate_response_frame_200f4808[4012];
__attribute__((used, section(".g2_conversate_response_encoded_2037c2a0"), aligned(4)))
uint8_t audio_conversate_response_encoded_2037c2a0[256];
_Static_assert(sizeof audio_conversate_response_frame_200f4808 == 4012u,
               "Conversate response frame span");
_Static_assert(sizeof audio_conversate_response_encoded_2037c2a0 == 256u,
               "Conversate encode buffer span");
