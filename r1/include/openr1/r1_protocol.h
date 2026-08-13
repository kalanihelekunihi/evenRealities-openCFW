#ifndef OPENR1_R1_PROTOCOL_H
#define OPENR1_R1_PROTOCOL_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define R1_MODEL_HEADER_LENGTH 12u
#define R1_FRAGMENT_HEADER_LENGTH 5u
#define R1_FRAGMENT_PAYLOAD_MAX 239u
#define R1_BLE_VALUE_MAX 244u
#define R1_SEQUENCE_MAX 16u
#define R1_LOGICAL_INBOUND_MAX 4063u
#define R1_LOGICAL_SAFE_OUTBOUND_MAX 4062u
#define R1_FRAGMENT_COUNT_MAX 17u
#define R1_PB_FRAGMENT_HEADER_LENGTH 6u
#define R1_PB_FRAGMENT_PAYLOAD_MAX 238u
#define R1_PB_LOGICAL_MAX 4096u
#define R1_PB_FRAGMENT_COUNT_MAX 18u
#define R1_PROTOCOL_VERSION 100u
#define R1_MODULE_VERSION 100u

typedef enum {
    R1_OK = 0,
    R1_ERROR_ARGUMENT,
    R1_ERROR_CAPACITY,
    R1_ERROR_LENGTH,
    R1_ERROR_SEQUENCE,
    R1_ERROR_CHECKSUM,
    R1_ERROR_STATE,
    R1_ERROR_UNSUPPORTED,
    R1_ERROR_UNAUTHORIZED
} r1_error;

typedef enum {
    R1_CHECKSUM_PHONE_COMPACT_CCITT = 0,
    R1_CHECKSUM_FIRMWARE_FULL_MODBUS = 1
} r1_checksum_scheme;

typedef struct {
    uint8_t version;
    uint8_t module;
    uint8_t module_version;
    uint16_t serial;
    uint8_t status;
    uint8_t command;
    uint8_t subcommand;
    const uint8_t *payload;
    size_t payload_length;
} r1_model;

typedef struct {
    uint8_t bytes[R1_BLE_VALUE_MAX];
    size_t length;
} r1_fragment;

typedef struct {
    r1_fragment fragments[R1_FRAGMENT_COUNT_MAX];
    size_t count;
} r1_fragment_set;

/* The recovered pb_tran path is distinct from the five-byte EUS framing
 * above: it appends a one-byte channel after the common sequence/CRC fields. */
typedef struct {
    r1_fragment fragments[R1_PB_FRAGMENT_COUNT_MAX];
    size_t count;
} r1_pb_fragment_set;

typedef struct {
    uint8_t bytes[R1_LOGICAL_INBOUND_MAX];
    size_t length;
    uint32_t expected_crc;
    uint8_t next_sequence;
    uint8_t first_sequence;
    size_t fragment_count;
    bool active;
} r1_reassembler;

typedef enum {
    R1_REASSEMBLY_WAITING = 0,
    R1_REASSEMBLY_COMPLETE,
    R1_REASSEMBLY_REJECTED
} r1_reassembly_status;

typedef struct {
    uint8_t status;
    uint8_t module;
    uint8_t command;
    uint8_t subcommand;
    uint16_t serial;
} r1_response_header;

typedef enum {
    R1_RESPONSE_SENT = 0,
    R1_RESPONSE_ENCODE_FAILED = 1,
    R1_RESPONSE_INVALID_ARGUMENT = 2,
    R1_RESPONSE_ALLOCATION_FAILED = 3,
    R1_RESPONSE_TRANSPORT_FAILED = 4,
    R1_RESPONSE_NO_ACTIVE_LINK = 5
} r1_response_result;

typedef void *(*r1_protocol_allocate_fn)(void *context, size_t bytes);
typedef void (*r1_protocol_release_fn)(void *context, void *allocation);
typedef int (*r1_protocol_send_fn)(
    void *context, uint16_t session, const uint8_t *bytes, size_t length);

r1_error r1_model_encode(const r1_model *model, r1_checksum_scheme scheme,
                         uint8_t *output, size_t capacity, size_t *written);
r1_error r1_model_decode(const uint8_t *bytes, size_t length, r1_checksum_scheme scheme,
                         r1_model *model);
r1_error r1_fragment_message(const uint8_t *logical, size_t length, r1_fragment_set *output);
r1_error r1_pb_fragment_message(uint8_t channel, const uint8_t *logical,
                                size_t length, r1_pb_fragment_set *output);
void r1_reassembler_reset(r1_reassembler *state);
r1_reassembly_status r1_reassembler_feed(r1_reassembler *state,
                                         const uint8_t *fragment, size_t length,
                                         r1_error *error);
r1_response_result r1_protocol_send_response(
    uint16_t session, bool primary_link_available, bool secondary_link_available,
    const r1_response_header *header, uint8_t module_version,
    uint16_t *next_generated_serial,
    const uint8_t *payload, size_t payload_length,
    r1_protocol_allocate_fn allocate, r1_protocol_release_fn release,
    r1_protocol_send_fn send, void *context);

#endif
