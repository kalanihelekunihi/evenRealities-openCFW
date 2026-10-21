/* Stock response state at 0x200740c8 and 128-byte encode buffer at 0x20071c48. */
#include <stdint.h>
__attribute__((used, section(".g2_sync_info_response_200740c8"), aligned(4)))
uint8_t audio_sync_info_response_200740c8[12];
__attribute__((used, section(".g2_sync_info_encode_buffer_20071c48"), aligned(4)))
uint8_t audio_sync_info_encode_buffer_20071c48[128];
_Static_assert(sizeof audio_sync_info_response_200740c8 == 12u, "response span");
_Static_assert(sizeof audio_sync_info_encode_buffer_20071c48 == 128u, "encode span");
