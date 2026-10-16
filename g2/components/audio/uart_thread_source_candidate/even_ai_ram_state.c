/* Bounded Apollo main EvenAI RAM spans observed in the authenticated payload.
 * These NOLOAD cells reserve observed access extents. Startup and total RAM
 * allocation boundaries require the final whole-image layout audit.
 */
#include <stdint.h>

uint8_t audio_even_ai_service_state_2006ed10[0x218]
    __attribute__((section(".bss.opencfw.evenai.service"), aligned(4), used));
uint8_t audio_even_ai_heartbeat_state_20074014[10]
    __attribute__((section(".bss.opencfw.evenai.heartbeat"), aligned(4), used));
uint32_t audio_even_ai_mutex_20074580
    __attribute__((section(".bss.opencfw.evenai.mutex"), aligned(4), used));
uint8_t audio_even_ai_config_state_20074974[3]
    __attribute__((section(".bss.opencfw.evenai.config"), aligned(1), used));
uint8_t audio_even_ai_last_frame[2]
    __attribute__((section(".bss.opencfw.evenai.last"), aligned(1), used));
uint8_t audio_even_ai_proto_message_200f5884[0x20c]
    __attribute__((section(".bss.opencfw.evenai.proto"), aligned(4), used));
uint8_t audio_even_ai_tx_buffer_2037c4a0[0x100]
    __attribute__((section(".bss.opencfw.evenai.tx"), aligned(4), used));

_Static_assert(sizeof(audio_even_ai_service_state_2006ed10) == 0x218u, "service extent");
_Static_assert(sizeof(audio_even_ai_heartbeat_state_20074014) == 10u, "heartbeat extent");
_Static_assert(sizeof(audio_even_ai_mutex_20074580) == 4u, "mutex cell extent");
_Static_assert(sizeof(audio_even_ai_config_state_20074974) == 3u, "config extent");
_Static_assert(sizeof(audio_even_ai_last_frame) == 2u, "last-frame extent");
_Static_assert(sizeof(audio_even_ai_proto_message_200f5884) == 0x20cu, "protobuf extent");
_Static_assert(sizeof(audio_even_ai_tx_buffer_2037c4a0) == 0x100u, "TX extent");
