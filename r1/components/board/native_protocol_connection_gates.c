/* These predicates test connection-handle presence only. The historical name
 * "authenticated" does not establish authentication or authorization. */
#include <stdint.h>
extern volatile uint16_t r1_connection_field8,r1_connection_field10;
#define CONNECTION_GATE(name,field) \
uint32_t name(void) { \
    register uint32_t saved2 __asm__("r2"); \
    register uint32_t saved3 __asm__("r3"); \
    __asm__ volatile("" : "+r"(saved2), "+r"(saved3)); \
    uint32_t handle=field; \
    register uint32_t result __asm__("r0")=handle!=UINT16_MAX; \
    register uint32_t difference __asm__("r1")=handle-UINT16_MAX; \
    __asm__ volatile("" : "+r"(result), "+r"(difference), "+r"(saved2), "+r"(saved3)); \
    return result; \
}
CONNECTION_GATE(r1_authenticated_phone_connection_gate,r1_connection_field8)
CONNECTION_GATE(r1_peer_channel_b_valid,r1_connection_field10)
