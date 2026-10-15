/* Apollo semantic_terminal_state_allows_runtime_event, native 0x5e8276. */
#include <stdint.h>

uint8_t audio_terminal_state_allows_runtime_event(uint32_t state) {
    switch((uint8_t)state) {
    case 0:case 2:case 7:case 11:case 12:return 1u;
    default:return 0u;
    }
}
