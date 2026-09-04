/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room Quicklist record storage matched to the authenticated G2 object
 * at 0x0058D51C..0x0058DAE3.  The public structures pin every resident ABI
 * offset used by the stock callers.
 */
#include "quicklist_data_manager.h"

#define OPEN_CFW_STATIC_ASSERT(name, condition) \
    typedef char open_cfw_static_assert_##name[(condition) ? 1 : -1]

OPEN_CFW_STATIC_ASSERT(input_record_size,
                       sizeof(open_cfw_quicklist_input_record) == 232U);
OPEN_CFW_STATIC_ASSERT(record_size,
                       sizeof(open_cfw_quicklist_record) == 232U);
OPEN_CFW_STATIC_ASSERT(state_size,
                       sizeof(open_cfw_quicklist_state) == 0x1238U);

#ifndef OPEN_CFW_QUICKLIST_STATE
#define OPEN_CFW_QUICKLIST_STATE \
    (*(open_cfw_quicklist_state *volatile *)0x0058D9C0U)
#endif

typedef uint32_t (*open_cfw_quicklist_epoch_function)(void);
#ifndef OPEN_CFW_QUICKLIST_EPOCH_NOW
#define OPEN_CFW_QUICKLIST_EPOCH_NOW() \
    (((open_cfw_quicklist_epoch_function)0x0044A1C7U)())
#endif

static void open_cfw_quicklist_zero(void *destination, uint32_t bytes)
{
    uint8_t *output = (uint8_t *)destination;
    uint32_t index;
    for (index = 0U; index < bytes; ++index) {
        output[index] = 0U;
    }
}

#if !defined(OPEN_CFW_QUICKLIST_INITIALIZE_ONLY) && \
    !defined(OPEN_CFW_QUICKLIST_APPEND_ONLY)
static void open_cfw_quicklist_copy_bytes(
    void *destination,
    const void *source,
    uint32_t bytes
)
{
    uint8_t *output = (uint8_t *)destination;
    const uint8_t *input = (const uint8_t *)source;
    uint32_t index;
    for (index = 0U; index < bytes; ++index) {
        output[index] = input[index];
    }
}
#endif

#if !defined(OPEN_CFW_QUICKLIST_INITIALIZE_ONLY) && \
    !defined(OPEN_CFW_QUICKLIST_APPEND_ONLY)
int open_cfw_quicklist_record_copy(
    const open_cfw_quicklist_input_record *source,
    open_cfw_quicklist_record *destination
)
{
    uint16_t length;
    if (source == (const open_cfw_quicklist_input_record *)0 ||
        destination == (open_cfw_quicklist_record *)0) {
        return OPEN_CFW_QUICKLIST_INVALID_ARGUMENT;
    }

    open_cfw_quicklist_zero(destination, sizeof(*destination));
    destination->id = source->id;
    destination->index = source->index;
    destination->flags = source->flags;
    destination->icon = source->icon;
    destination->action = source->action;
    destination->continuation = source->continuation;
    length = source->text_length < 201U ? source->text_length : 200U;
    destination->text_length = length;
    open_cfw_quicklist_copy_bytes(destination->text, source->text, length);
    destination->text[length] = '\0';
    return OPEN_CFW_QUICKLIST_OK;
}
#endif

#if !defined(OPEN_CFW_QUICKLIST_COPY_ONLY) && \
    !defined(OPEN_CFW_QUICKLIST_APPEND_ONLY)
int open_cfw_quicklist_data_initialize(
    const open_cfw_quicklist_input_record *record
)
{
    open_cfw_quicklist_state *state = OPEN_CFW_QUICKLIST_STATE;
    int result;
    if (record == (const open_cfw_quicklist_input_record *)0 ||
        state == (open_cfw_quicklist_state *)0) {
        return OPEN_CFW_QUICKLIST_INVALID_ARGUMENT;
    }

    open_cfw_quicklist_zero(state->records, sizeof(state->records));
    result = open_cfw_quicklist_record_copy(record, &state->records[0]);
    if (result != OPEN_CFW_QUICKLIST_OK) {
        return result;
    }
    state->records[0].valid = 1U;
    state->expected_records = 1U;
    state->received_records = 1U;
    state->message_type = 3U;
    state->updated_epoch = OPEN_CFW_QUICKLIST_EPOCH_NOW();
    state->reserved_122c = 0U;
    return OPEN_CFW_QUICKLIST_OK;
}
#endif

#if !defined(OPEN_CFW_QUICKLIST_COPY_ONLY) && \
    !defined(OPEN_CFW_QUICKLIST_INITIALIZE_ONLY)
int open_cfw_quicklist_data_append(const open_cfw_quicklist_packet *packet)
{
    open_cfw_quicklist_state *state = OPEN_CFW_QUICKLIST_STATE;
    uint32_t count;
    uint32_t index;
    if (packet == (const open_cfw_quicklist_packet *)0 ||
        state == (open_cfw_quicklist_state *)0) {
        return OPEN_CFW_QUICKLIST_INVALID_ARGUMENT;
    }

    count = packet->record_count < 21U ? packet->record_count : 20U;
    if (packet->expected_records == 0U) {
        open_cfw_quicklist_zero(state, sizeof(*state));
    } else if (count != 0U) {
        if (packet->records[0].index == 0U) {
            open_cfw_quicklist_zero(state, sizeof(*state));
        }
        if ((uint32_t)state->received_records + count > 20U) {
            return OPEN_CFW_QUICKLIST_CAPACITY_EXCEEDED;
        }
        for (index = 0U; index < count; ++index) {
            open_cfw_quicklist_record *destination;
            if (packet->records[index].index >= 20U) {
                continue;
            }
            destination = &state->records[state->received_records + index];
            if (open_cfw_quicklist_record_copy(
                    &packet->records[index], destination) ==
                OPEN_CFW_QUICKLIST_OK) {
                destination->valid = 1U;
            }
        }
    }

    state->expected_records = packet->expected_records;
    state->received_records =
        (uint8_t)((uint32_t)state->received_records + count);
    state->message_type = packet->message_type;
    state->updated_epoch = OPEN_CFW_QUICKLIST_EPOCH_NOW();
    state->reserved_122c = 0U;
    return state->received_records < state->expected_records
        ? OPEN_CFW_QUICKLIST_MORE
        : OPEN_CFW_QUICKLIST_OK;
}
#endif
