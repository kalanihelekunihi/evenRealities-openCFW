/* SPDX-License-Identifier: MIT
 * Exact stock-address lower wrappers used in experimental command routing.
 * Stock tail-branches to the provider and leaves the provider's residual R0.
 * Every caller chain (binary_*_candidate / gpio_a1 -> *_known_dispatch ->
 * case_{legacy,binary}_command_candidate) ends in callers that discard the
 * result, so these return 0.
 */
#include <stdint.h>

extern void case_send(const uint8_t *payload, uint32_t length);
extern void case_ack(uint32_t command);
extern void log_hex_buffer(const uint8_t *bytes, uint32_t length);
extern void case_control_a(uint32_t enable);

#define SEND_WRAPPER(name) \
    uint32_t name(const uint8_t *payload, uint32_t length) \
    { case_send(payload, length); return 0u; }
#define ACK_WRAPPER(name) \
    uint32_t name(uint32_t command) { case_ack(command); return 0u; }

SEND_WRAPPER(case_binary_14_send)
SEND_WRAPPER(case_binary_local_send)
SEND_WRAPPER(case_binary_send51)
SEND_WRAPPER(case_binary_send5f)
ACK_WRAPPER(case_binary_3e_ack)
ACK_WRAPPER(case_binary_3f_ack)
ACK_WRAPPER(case_binary_56_ack)
ACK_WRAPPER(case_binary_local_ack)

uint32_t case_binary_5e_hex(const uint8_t *bytes, uint32_t length)
{
    log_hex_buffer(bytes, length);
    return 0u;
}

uint32_t case_legacy_gpio_bit0(uint32_t value)
{
    case_control_a(value);
    return 0u;
}
