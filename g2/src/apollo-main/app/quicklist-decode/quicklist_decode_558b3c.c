/* Native APP_DecodePbRxQuicklistData at 0x558b3c. The state owner and the
 * two storage operations remain explicit until their product layout is known. */
#include <stdint.h>

extern uint32_t audio_quicklist_store_one(const void *item);
extern uint32_t audio_quicklist_store_many(const void *items);

/* Native command byte is 0x200f624c; item/command payload starts at +8.
 * Its 0x1238-byte decode buffer is cleared by the native frame parser. */
uint8_t audio_quicklist_rx_state[0x1238];

uint32_t audio_quicklist_decode_558b3c(void) {
    uint32_t result = 3u;
    uint8_t command = audio_quicklist_rx_state[0];
    const void *payload = audio_quicklist_rx_state + 8u;
    if (command == 1u) {
        result = audio_quicklist_store_one(payload);
    } else if (command == 2u) {
        result = audio_quicklist_store_many(payload);
    } else if (command == 3u) {
        result = 0u;
    }
    return result;
}
