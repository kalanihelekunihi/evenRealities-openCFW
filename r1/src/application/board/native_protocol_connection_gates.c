/* These predicates test connection-handle presence only. The historical name
 * "authenticated" does not establish authentication or authorization. */
#include <stdint.h>
extern volatile uint16_t r1_connection_field8,r1_connection_field10;
#define CONNECTION_GATE(name,field) \
uint32_t name(void) { return field!=UINT16_MAX; }
CONNECTION_GATE(r1_authenticated_phone_connection_gate,r1_connection_field8)
CONNECTION_GATE(r1_peer_channel_b_valid,r1_connection_field10)
