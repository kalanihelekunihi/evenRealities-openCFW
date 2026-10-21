#include <stdint.h>

extern void case_send(const uint8_t *payload, uint32_t length);

/* Stock 0x080068d0: copy the eight-byte literal and send its first five. */
void case_ack(uint32_t command)
{
    uint8_t reply[8] = {0u, 1u, 3u, 1u, 0u, 0u, 0u, 0u};
    reply[0] = (uint8_t)command;
    case_send(reply, 5u);
}
