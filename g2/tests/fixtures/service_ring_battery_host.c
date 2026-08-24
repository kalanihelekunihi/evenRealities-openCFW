#include <stdint.h>
#include <string.h>

host_ring_state host_state;
uint8_t host_message[12];
uint16_t host_service;
uint16_t host_length;
uint8_t host_flags;
uint8_t host_route;
int32_t host_result;

static int32_t capture(
    uint8_t route, uint16_t service, const void *message,
    uint16_t length, uint8_t flags
)
{
    host_route = route; host_service = service; host_length = length;
    host_flags = flags;
    if (length == sizeof(host_message)) memcpy(host_message, message, length);
    return host_result;
}
int32_t host_post_local(uint16_t s, const void *m, uint16_t l, uint8_t f)
{ return capture(1u, s, m, l, f); }
int32_t host_post_peer(uint16_t s, const void *m, uint16_t l, uint8_t f)
{ return capture(2u, s, m, l, f); }
