/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

static struct open_cfw_quicklist_state_tag *host_state_pointer;
static uint32_t host_epoch;
#define OPEN_CFW_QUICKLIST_STATE \
    (*(open_cfw_quicklist_state **)&host_state_pointer)
#define OPEN_CFW_QUICKLIST_EPOCH_NOW() (host_epoch)
#include "../../components/apollo_main/core_overlay/quicklist_data_manager.c"

static void require(int condition)
{
    if (!condition) {
        abort();
    }
}

int main(void)
{
    open_cfw_quicklist_state state;
    open_cfw_quicklist_input_record initial;
    uint8_t packet_storage[
        sizeof(open_cfw_quicklist_packet) +
        2U * sizeof(open_cfw_quicklist_input_record)
    ];
    open_cfw_quicklist_packet *packet =
        (open_cfw_quicklist_packet *)packet_storage;
    open_cfw_quicklist_record output;

    memset(&state, 0xA5, sizeof(state));
    memset(&initial, 0, sizeof(initial));
    host_state_pointer = (struct open_cfw_quicklist_state_tag *)&state;
    host_epoch = 0x12345678U;
    initial.id = 7U;
    initial.index = 0U;
    initial.icon = 11U;
    initial.action = 13U;
    initial.text_length = 5U;
    memcpy(initial.text, "alpha", 5U);
    initial.continuation = 1U;

    require(open_cfw_quicklist_record_copy(0, &output) == 2);
    require(open_cfw_quicklist_record_copy(&initial, 0) == 2);
    require(open_cfw_quicklist_data_initialize(&initial) == 0);
    require(state.received_records == 1U && state.expected_records == 1U);
    require(state.message_type == 3U && state.updated_epoch == host_epoch);
    require(state.records[0].valid == 1U);
    require(state.records[0].text_length == 5U);
    require(strcmp(state.records[0].text, "alpha") == 0);

    memset(packet_storage, 0, sizeof(packet_storage));
    packet->message_type = 2U;
    packet->expected_records = 3U;
    packet->record_count = 2U;
    packet->records[0] = initial;
    packet->records[0].index = 1U;
    packet->records[0].text_length = 4U;
    memcpy(packet->records[0].text, "beta", 4U);
    packet->records[1] = initial;
    packet->records[1].index = 2U;
    packet->records[1].text_length = 5U;
    memcpy(packet->records[1].text, "gamma", 5U);
    host_epoch = 0x87654321U;
    require(open_cfw_quicklist_data_append(packet) == 0);
    require(state.received_records == 3U && state.expected_records == 3U);
    require(strcmp(state.records[1].text, "beta") == 0);
    require(strcmp(state.records[2].text, "gamma") == 0);
    require(state.updated_epoch == host_epoch);

    packet->expected_records = 21U;
    packet->record_count = 20U;
    require(open_cfw_quicklist_data_append(packet) == 4);
    require(open_cfw_quicklist_data_append(0) == 2);

    initial.text_length = 300U;
    memset(initial.text, 'x', 201U);
    require(open_cfw_quicklist_record_copy(&initial, &output) == 0);
    require(output.text_length == 200U && output.text[200] == '\0');
    return 0;
}
