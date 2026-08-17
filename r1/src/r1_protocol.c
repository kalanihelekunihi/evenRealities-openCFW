#include "openr1/r1_protocol.h"

#include "openr1/r1_crc.h"

static void write_u16(uint8_t *output, uint16_t value) {
    output[0] = (uint8_t)value;
    output[1] = (uint8_t)(value >> 8u);
}

static void write_u32(uint8_t *output, uint32_t value) {
    output[0] = (uint8_t)value;
    output[1] = (uint8_t)(value >> 8u);
    output[2] = (uint8_t)(value >> 16u);
    output[3] = (uint8_t)(value >> 24u);
}

static uint16_t read_u16(const uint8_t *input) {
    return (uint16_t)((uint16_t)input[0] | (uint16_t)((uint16_t)input[1] << 8u));
}

static uint32_t read_u32(const uint8_t *input) {
    return (uint32_t)input[0]
        | ((uint32_t)input[1] << 8u)
        | ((uint32_t)input[2] << 16u)
        | ((uint32_t)input[3] << 24u);
}

static void copy_bytes(uint8_t *output, const uint8_t *input, size_t length) {
    for (size_t index = 0u; index < length; ++index) {
        output[index] = input[index];
    }
}

static uint16_t phone_checksum(const uint8_t *packet, size_t length) {
    uint8_t compact[9u];
    compact[0] = packet[0];
    compact[1] = packet[1];
    compact[2] = packet[2];
    compact[3] = packet[3];
    compact[4] = packet[5];
    compact[5] = packet[6];
    compact[6] = packet[7];
    compact[7] = packet[8];
    compact[8] = 0u;
    uint16_t crc = r1_crc16_ccitt(compact, sizeof compact);

    /* The primitive has a fixed initial value, so continue it inline over the payload. */
    for (size_t index = R1_MODEL_HEADER_LENGTH; index < length; ++index) {
        crc = (uint16_t)((crc >> 8u) | (uint16_t)(crc << 8u));
        crc ^= packet[index];
        crc ^= (uint16_t)((crc & UINT16_C(0x00ff)) >> 4u);
        crc ^= (uint16_t)(crc << 12u);
        crc ^= (uint16_t)((crc & UINT16_C(0x00ff)) << 5u);
    }
    return crc;
}

static uint16_t firmware_checksum(const uint8_t *packet, size_t length) {
    uint16_t crc = UINT16_C(0xffff);
    for (size_t index = 0u; index < length; ++index) {
        const uint8_t byte = (index == 10u || index == 11u) ? 0u : packet[index];
        crc ^= byte;
        for (uint8_t bit = 0u; bit < 8u; ++bit) {
            crc = (crc & 1u) != 0u
                ? (uint16_t)((crc >> 1u) ^ UINT16_C(0xa001))
                : (uint16_t)(crc >> 1u);
        }
    }
    return crc;
}

r1_error r1_model_encode(const r1_model *model, r1_checksum_scheme scheme,
                         uint8_t *output, size_t capacity, size_t *written) {
    if (model == NULL || output == NULL || written == NULL ||
        (model->payload_length > 0u && model->payload == NULL)) {
        return R1_ERROR_ARGUMENT;
    }
    if (model->payload_length > UINT16_MAX - R1_MODEL_HEADER_LENGTH) {
        return R1_ERROR_LENGTH;
    }
    const size_t length = R1_MODEL_HEADER_LENGTH + model->payload_length;
    if (capacity < length) {
        return R1_ERROR_CAPACITY;
    }
    output[0] = model->version;
    output[1] = model->module;
    output[2] = model->module_version;
    write_u16(output + 3u, model->serial);
    output[5] = model->status;
    output[6] = model->command;
    output[7] = model->subcommand;
    write_u16(output + 8u, (uint16_t)length);
    output[10] = 0u;
    output[11] = 0u;
    copy_bytes(output + R1_MODEL_HEADER_LENGTH, model->payload, model->payload_length);
    const uint16_t crc = scheme == R1_CHECKSUM_PHONE_COMPACT_CCITT
        ? phone_checksum(output, length)
        : firmware_checksum(output, length);
    write_u16(output + 10u, crc);
    *written = length;
    return R1_OK;
}

r1_error r1_model_decode(const uint8_t *bytes, size_t length, r1_checksum_scheme scheme,
                         r1_model *model) {
    if (bytes == NULL || model == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (length < R1_MODEL_HEADER_LENGTH || read_u16(bytes + 8u) != length) {
        return R1_ERROR_LENGTH;
    }
    const uint16_t observed = read_u16(bytes + 10u);
    const uint16_t expected = scheme == R1_CHECKSUM_PHONE_COMPACT_CCITT
        ? phone_checksum(bytes, length)
        : firmware_checksum(bytes, length);
    if (observed != expected) {
        return R1_ERROR_CHECKSUM;
    }
    model->version = bytes[0];
    model->module = bytes[1];
    model->module_version = bytes[2];
    model->serial = read_u16(bytes + 3u);
    model->status = bytes[5];
    model->command = bytes[6];
    model->subcommand = bytes[7];
    model->payload = bytes + R1_MODEL_HEADER_LENGTH;
    model->payload_length = length - R1_MODEL_HEADER_LENGTH;
    return R1_OK;
}

/* Exact sorted identifiers from the 20-entry production system table at
 * 0x0009a4cc.  Handler addresses deliberately do not cross this boundary. */
static const uint16_t eus_system_commands[] = {
    UINT16_C(0x0001), UINT16_C(0x0002), UINT16_C(0x0003),
    UINT16_C(0x0004), UINT16_C(0x0005), UINT16_C(0x0007),
    UINT16_C(0x0008), UINT16_C(0x0009), UINT16_C(0x000a),
    UINT16_C(0x000b), UINT16_C(0x000c), UINT16_C(0x000e),
    UINT16_C(0x000f), UINT16_C(0x0010), UINT16_C(0x0011),
    UINT16_C(0x0012), UINT16_C(0x007e), UINT16_C(0x007f),
    UINT16_C(0x0082), UINT16_C(0x0083),
};

r1_error r1_eus_ingress_plan_decode(uint16_t session, const uint8_t *packet,
                                    size_t length, r1_eus_ingress_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_eus_ingress_plan){
        .action = R1_EUS_INGRESS_REJECT_NULL_PACKET,
        .session = session,
    };
    if (packet == NULL) {
        return R1_OK;
    }
    if (length < R1_MODEL_HEADER_LENGTH) {
        plan->action = R1_EUS_INGRESS_REJECT_SHORT_PACKET;
        return R1_OK;
    }

    plan->module = packet[1];
    plan->module_version = packet[2];
    plan->serial = read_u16(packet + 3u);
    plan->status = packet[5];
    plan->command = packet[6];
    plan->subcommand = packet[7];
    plan->composite_key = ((uint32_t)plan->module << 16u)
        | ((uint32_t)plan->command << 8u) | plan->subcommand;

    if (packet[0] != R1_PROTOCOL_VERSION) {
        plan->action = R1_EUS_INGRESS_REJECT_PROTOCOL_VERSION;
    } else if (plan->module_version < R1_MODULE_VERSION) {
        plan->action = R1_EUS_INGRESS_REJECT_MODULE_VERSION;
    } else if (plan->module >= 4u && plan->module != UINT8_C(0x7f)) {
        plan->action = R1_EUS_INGRESS_REJECT_MODULE;
    } else if (plan->module == 1u) {
        plan->action = R1_EUS_INGRESS_DISPATCH_SYSTEM;
    } else if (plan->module == 2u) {
        plan->action = R1_EUS_INGRESS_DISPATCH_HEALTH;
    } else if (plan->module == UINT8_C(0x7f)) {
        plan->action = R1_EUS_INGRESS_DISPATCH_TESTABLE;
    } else {
        /* Production module-table slots zero and three are null. */
        plan->action = R1_EUS_INGRESS_REJECT_UNREGISTERED_MODULE;
    }
    return R1_OK;
}

r1_error r1_eus_system_dispatch_plan_build(
    uint8_t command, uint8_t subcommand, r1_eus_system_dispatch_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    const uint16_t key = (uint16_t)(((uint16_t)command << 8u) | subcommand);
    *plan = (r1_eus_system_dispatch_plan){
        .registered = false,
        .packed_command = key,
        .registration_index = UINT8_MAX,
    };

    size_t lower = 0u;
    size_t upper = sizeof eus_system_commands / sizeof eus_system_commands[0];
    while (lower < upper) {
        const size_t middle = lower + (upper - lower) / 2u;
        if (eus_system_commands[middle] < key) {
            lower = middle + 1u;
        } else {
            upper = middle;
        }
    }
    if (lower < sizeof eus_system_commands / sizeof eus_system_commands[0]
            && eus_system_commands[lower] == key) {
        plan->registered = true;
        plan->registration_index = (uint8_t)lower;
    }
    return R1_OK;
}

r1_error r1_fragment_message(const uint8_t *logical, size_t length, r1_fragment_set *output) {
    if (output == NULL || (length > 0u && logical == NULL)) {
        return R1_ERROR_ARGUMENT;
    }
    if (length > R1_LOGICAL_SAFE_OUTBOUND_MAX) {
        return R1_ERROR_LENGTH;
    }
    const size_t first = length / R1_FRAGMENT_PAYLOAD_MAX;
    if (first > R1_SEQUENCE_MAX) {
        return R1_ERROR_SEQUENCE;
    }
    output->count = first + 1u;
    const uint32_t crc = r1_crc32_castagnoli(logical, length);
    size_t offset = 0u;
    for (size_t index = 0u; index < output->count; ++index) {
        r1_fragment *fragment = &output->fragments[index];
        const size_t sequence = first - index;
        const size_t remaining = length - offset;
        const size_t payload_length = remaining < R1_FRAGMENT_PAYLOAD_MAX
            ? remaining : R1_FRAGMENT_PAYLOAD_MAX;
        fragment->bytes[0] = (uint8_t)sequence;
        write_u32(fragment->bytes + 1u, crc);
        if (payload_length > 0u) {
            copy_bytes(fragment->bytes + R1_FRAGMENT_HEADER_LENGTH,
                       logical + offset, payload_length);
        }
        fragment->length = R1_FRAGMENT_HEADER_LENGTH + payload_length;
        offset += payload_length;
    }
    return offset == length ? R1_OK : R1_ERROR_STATE;
}

r1_error r1_pb_fragment_message(uint8_t channel, const uint8_t *logical,
                                size_t length, r1_pb_fragment_set *output) {
    if (output == NULL || (length > 0u && logical == NULL)) {
        return R1_ERROR_ARGUMENT;
    }
    if (length > R1_PB_LOGICAL_MAX) {
        return R1_ERROR_LENGTH;
    }
    const size_t first = length / R1_PB_FRAGMENT_PAYLOAD_MAX;
    output->count = first + 1u;
    const uint32_t crc = r1_crc32_castagnoli(logical, length);
    size_t offset = 0u;
    for (size_t index = 0u; index < output->count; ++index) {
        r1_fragment *fragment = &output->fragments[index];
        const size_t remaining = length - offset;
        const size_t payload_length = remaining < R1_PB_FRAGMENT_PAYLOAD_MAX
            ? remaining : R1_PB_FRAGMENT_PAYLOAD_MAX;
        fragment->bytes[0] = (uint8_t)(first - index);
        write_u32(fragment->bytes + 1u, crc);
        fragment->bytes[5] = channel;
        if (payload_length > 0u) {
            copy_bytes(fragment->bytes + R1_PB_FRAGMENT_HEADER_LENGTH,
                       logical + offset, payload_length);
        }
        fragment->length = R1_PB_FRAGMENT_HEADER_LENGTH + payload_length;
        offset += payload_length;
    }
    return offset == length ? R1_OK : R1_ERROR_STATE;
}

void r1_reassembler_reset(r1_reassembler *state) {
    if (state == NULL) {
        return;
    }
    state->length = 0u;
    state->expected_crc = 0u;
    state->next_sequence = 0u;
    state->first_sequence = 0u;
    state->fragment_count = 0u;
    state->active = false;
}

static r1_reassembly_status reject(r1_reassembler *state, r1_error *error,
                                   r1_error reason) {
    r1_reassembler_reset(state);
    if (error != NULL) {
        *error = reason;
    }
    return R1_REASSEMBLY_REJECTED;
}

r1_reassembly_status r1_reassembler_feed(r1_reassembler *state,
                                         const uint8_t *fragment, size_t length,
                                         r1_error *error) {
    if (error != NULL) {
        *error = R1_OK;
    }
    if (state == NULL || fragment == NULL) {
        return reject(state, error, R1_ERROR_ARGUMENT);
    }
    if (length < R1_FRAGMENT_HEADER_LENGTH || length > R1_BLE_VALUE_MAX) {
        return reject(state, error, R1_ERROR_LENGTH);
    }
    const uint8_t sequence = fragment[0];
    const uint32_t crc = read_u32(fragment + 1u);
    const size_t payload_length = length - R1_FRAGMENT_HEADER_LENGTH;
    if (sequence > R1_SEQUENCE_MAX || payload_length > R1_FRAGMENT_PAYLOAD_MAX) {
        return reject(state, error, R1_ERROR_SEQUENCE);
    }
    if (!state->active) {
        state->length = 0u;
        state->fragment_count = 0u;
        state->active = true;
        state->expected_crc = crc;
        state->first_sequence = sequence;
        state->next_sequence = sequence;
    }
    if (crc != state->expected_crc || sequence != state->next_sequence) {
        return reject(state, error, R1_ERROR_SEQUENCE);
    }
    if (state->length + payload_length > sizeof state->bytes) {
        return reject(state, error, R1_ERROR_CAPACITY);
    }
    copy_bytes(state->bytes + state->length,
               fragment + R1_FRAGMENT_HEADER_LENGTH, payload_length);
    state->length += payload_length;
    state->fragment_count += 1u;
    if (sequence != 0u) {
        state->next_sequence = (uint8_t)(sequence - 1u);
        return R1_REASSEMBLY_WAITING;
    }
    if (state->fragment_count != (size_t)state->first_sequence + 1u ||
        r1_crc32_castagnoli(state->bytes, state->length) != state->expected_crc) {
        return reject(state, error, R1_ERROR_CHECKSUM);
    }
    state->active = false;
    return R1_REASSEMBLY_COMPLETE;
}

/* Recovered R1 final-response orchestration. Link selection, allocation, and
 * BLE transmission are injected provider seams; framing remains in this file. */
r1_response_result r1_protocol_send_response(
    uint16_t session, bool primary_link_available, bool secondary_link_available,
    const r1_response_header *header, uint8_t module_version,
    uint16_t *next_generated_serial,
    const uint8_t *payload, size_t payload_length,
    r1_protocol_allocate_fn allocate, r1_protocol_release_fn release,
    r1_protocol_send_fn send, void *context) {
    if (header == NULL || allocate == NULL || release == NULL || send == NULL
        || (payload_length != 0u && payload == NULL) || header->module > 3u
        || (((header->status & 1u) == 0u) && next_generated_serial == NULL)) {
        return R1_RESPONSE_INVALID_ARGUMENT;
    }
    if (!primary_link_available && !secondary_link_available) {
        return R1_RESPONSE_NO_ACTIVE_LINK;
    }
    if (payload_length > UINT16_MAX - R1_MODEL_HEADER_LENGTH) {
        return R1_RESPONSE_ENCODE_FAILED;
    }

    const size_t encoded_length = R1_MODEL_HEADER_LENGTH + payload_length;
    uint8_t *encoded = allocate(context, encoded_length);
    if (encoded == NULL) {
        return R1_RESPONSE_ALLOCATION_FAILED;
    }
    const uint16_t serial = (header->status & 1u) != 0u
        ? header->serial : (*next_generated_serial)++;
    const r1_model model = {
        R1_PROTOCOL_VERSION,
        header->module,
        module_version,
        serial,
        header->status,
        header->command,
        header->subcommand,
        payload,
        payload_length,
    };
    size_t written = 0u;
    const r1_error error = r1_model_encode(
        &model, R1_CHECKSUM_FIRMWARE_FULL_MODBUS,
        encoded, encoded_length, &written);
    if (error != R1_OK) {
        release(context, encoded);
        return error == R1_ERROR_ARGUMENT
            ? R1_RESPONSE_INVALID_ARGUMENT : R1_RESPONSE_ENCODE_FAILED;
    }
    const int transport_error = send(context, session, encoded, written);
    release(context, encoded);
    return transport_error == 0
        ? R1_RESPONSE_SENT : R1_RESPONSE_TRANSPORT_FAILED;
}
