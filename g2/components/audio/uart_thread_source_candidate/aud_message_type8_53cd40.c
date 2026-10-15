/* Stock Apollo aud_send_message_type8 0x53cd40. */
#include <stdint.h>

extern void audio_aud_message_dispatch_53c638(const void *); /* native 0x53c638 */

void audio_aud_send_message_type8_53cd40(uint8_t value) {
    uint32_t message[3] = {8u, 1u, value};
    audio_aud_message_dispatch_53c638(message);
}
