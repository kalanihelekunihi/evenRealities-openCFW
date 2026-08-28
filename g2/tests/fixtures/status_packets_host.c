/*
 * SPDX-License-Identifier: MIT
 *
 * Native host oracle for the three eight-byte status-packet reporters.
 */

unsigned int open_cfw_test_status_packet_lens_values[2];
unsigned int open_cfw_test_status_packet_lens_calls;
unsigned char open_cfw_test_status_packet_state;
unsigned int open_cfw_test_status_packet_send_calls;
unsigned int open_cfw_test_status_packet_command;
unsigned int open_cfw_test_status_packet_size;
unsigned int open_cfw_test_status_packet_option;
int open_cfw_test_status_packet_send_result;
unsigned char open_cfw_test_status_packet_payload[8];

static unsigned int open_cfw_test_status_packet_lens_side(void)
{
    unsigned int index = open_cfw_test_status_packet_lens_calls;

    open_cfw_test_status_packet_lens_calls = index + 1U;
    return open_cfw_test_status_packet_lens_values[index & 1U];
}

static int open_cfw_test_status_packet_send(
    unsigned int command,
    const void *payload,
    unsigned int size,
    unsigned int option
)
{
    const unsigned char *bytes = (const unsigned char *)payload;
    unsigned int index;

    open_cfw_test_status_packet_send_calls += 1U;
    open_cfw_test_status_packet_command = command;
    open_cfw_test_status_packet_size = size;
    open_cfw_test_status_packet_option = option;
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_status_packet_payload[index] = bytes[index];
    }
    return open_cfw_test_status_packet_send_result;
}

#define OPEN_CFW_STATUS_PACKETS_LENS_SIDE() \
    open_cfw_test_status_packet_lens_side()
#define OPEN_CFW_STATUS_PACKETS_STATE \
    open_cfw_test_status_packet_state
#define OPEN_CFW_STATUS_PACKETS_SEND(command, payload, size, option) \
    open_cfw_test_status_packet_send((command), (payload), (size), (option))
#include "../../components/apollo_main/core_overlay/status_packets.c"
