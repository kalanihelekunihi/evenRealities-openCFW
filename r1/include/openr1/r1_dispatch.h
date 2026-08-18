#ifndef OPENR1_R1_DISPATCH_H
#define OPENR1_R1_DISPATCH_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_protocol.h"
#include "openr1/r1_state.h"

#define R1_MODULE_SYSTEM UINT8_C(0x01)
#define R1_COMMAND_SYSTEM UINT8_C(0x00)
#define R1_SYSTEM_SUBCOMMAND_DEVICE_STATUS UINT8_C(0x01)

#define R1_DISPATCH_RESPONSE_MAX 32u
#define R1_DISPATCH_MODEL_MAX 1100u
/* The recovered EUS worker owns a 50-record shared queue.  Dispatch results
 * must fit atomically because the runtime preflights the complete result
 * before admitting any fragment. */
#define R1_DISPATCH_FRAGMENT_MAX 50u
#define R1_LEGACY_COMMAND_WORKSPACE_SIZE 36u
#define R1_LEGACY_COMMAND_OPCODE_OFFSET 2u
#define R1_LEGACY_DEVICE_INFO_PREFIX_BYTES 4u
#define R1_LEGACY_DEVICE_INFO_RESPONSE_MAX 43u
#define R1_LEGACY_PRODUCT_BSN_BYTES 30u
#define R1_LEGACY_PRODUCT_SN_BYTES 30u
#define R1_ATI_CALIBRATION_RESPONSE_STATUS_DEFAULT 5u
#define R1_ATI_CALIBRATION_RESPONSE_STATUS_QUERY 6u
#define R1_TOUCH_SWITCH_PAYLOAD_SIZE 2u
#define R1_TOUCH_SWITCH_SELECTOR_PHONE 1u
#define R1_TOUCH_SWITCH_SELECTOR_GLASSES 2u
#define R1_TOUCH_SWITCH_SOURCE_GLASSES 0u

typedef enum {
    R1_LEGACY_COMMAND_ROUTE_NONE = 0,
    R1_LEGACY_COMMAND_ROUTE_0X11,
    R1_LEGACY_COMMAND_ROUTE_0X12,
    R1_LEGACY_COMMAND_ROUTE_0X21,
    R1_LEGACY_COMMAND_ROUTE_0X22,
    R1_LEGACY_COMMAND_ROUTE_0X23,
    R1_LEGACY_COMMAND_ROUTE_0X24,
    R1_LEGACY_COMMAND_ROUTE_0X34,
    R1_LEGACY_COMMAND_ROUTE_0X37,
    R1_LEGACY_COMMAND_ROUTE_0X40,
    R1_LEGACY_COMMAND_ROUTE_0X52,
    R1_LEGACY_COMMAND_ROUTE_0X53,
    R1_LEGACY_COMMAND_ROUTE_0X54,
    R1_LEGACY_COMMAND_ROUTE_0X55,
    R1_LEGACY_COMMAND_ROUTE_0X56,
    R1_LEGACY_COMMAND_ROUTE_0X57,
    R1_LEGACY_COMMAND_ROUTE_0X85,
    R1_LEGACY_COMMAND_ROUTE_PAIR_AUTH_0X88,
    R1_LEGACY_COMMAND_ROUTE_0X89,
    R1_LEGACY_COMMAND_ROUTE_0X8A,
    R1_LEGACY_COMMAND_ROUTE_0X91,
    R1_LEGACY_COMMAND_ROUTE_0X94,
    R1_LEGACY_COMMAND_ROUTE_0X95,
    R1_LEGACY_COMMAND_ROUTE_0XF2,
    R1_LEGACY_COMMAND_ROUTE_FACTORY_NOOP_0X10,
    R1_LEGACY_COMMAND_ROUTE_FACTORY_STATUS_0X8B
} r1_legacy_command_route;

typedef enum {
    R1_ATI_CALIBRATION_ACTION_NONE = 0,
    R1_ATI_CALIBRATION_ACTION_SET_RAW_PRINT_LEVEL,
    R1_ATI_CALIBRATION_ACTION_SEND_CONFIGURATION,
    R1_ATI_CALIBRATION_ACTION_QUERY_CALIBRATION,
    R1_ATI_CALIBRATION_ACTION_OPEN_TOUCH_SOURCE,
    R1_ATI_CALIBRATION_ACTION_CLOSE_TOUCH_SOURCE,
    R1_ATI_CALIBRATION_ACTION_READ_RING_SIZE
} r1_ati_calibration_action;

typedef struct {
    bool calibration_available;
    uint8_t calibration_first;
    uint8_t calibration_second;
    uint8_t ring_size;
} r1_ati_calibration_observation;

typedef struct {
    r1_ati_calibration_action action;
    uint32_t event_flags;
    uint32_t configuration_word_1;
    uint32_t configuration_word_2;
    uint8_t action_argument_0;
    uint8_t action_argument_1;
    uint8_t response_status;
    uint8_t response_update_length;
    uint8_t response_update[2];
} r1_ati_calibration_plan;

typedef enum {
    R1_TOUCH_SWITCH_ACTION_NONE = 0,
    R1_TOUCH_SWITCH_ACTION_PHONE_DIAGNOSTIC,
    R1_TOUCH_SWITCH_ACTION_OPEN_GLASSES_SOURCE,
    R1_TOUCH_SWITCH_ACTION_CLOSE_GLASSES_SOURCE
} r1_touch_switch_action;

/* Side-effect-free, hardened form of the recovered system touchSwitch
 * handler at 0x00084874.  The response intent precedes the optional source-0
 * touch action; phone and unknown selectors do not change touch state. */
typedef struct {
    bool send_empty_success_response;
    r1_touch_switch_action action;
    uint8_t selector;
    uint8_t switch_value;
    uint8_t touch_source;
} r1_touch_switch_handler_plan;

typedef enum {
    R1_ROLE_UNASSIGNED = 0,
    R1_ROLE_PHONE = 1,
    R1_ROLE_GLASSES = 2
} r1_peer_role;

typedef struct {
    bool encrypted;
    bool bonded;
    bool authorized;
    r1_peer_role role;
} r1_session;

typedef struct {
    uint8_t models[R1_DISPATCH_RESPONSE_MAX][R1_DISPATCH_MODEL_MAX];
    size_t lengths[R1_DISPATCH_RESPONSE_MAX];
    size_t count;
} r1_dispatch_result;

typedef struct {
    uint8_t product_bsn[R1_LEGACY_PRODUCT_BSN_BYTES];
    uint8_t product_bsn_length;
    uint8_t product_sn[R1_LEGACY_PRODUCT_SN_BYTES];
    uint8_t product_sn_length;
    uint8_t temperature_calibration[6u];
    uint8_t accelerometer_calibration[6u];
    uint8_t configuration_byte_0x70;
    uint32_t configuration_word_0x74;
    uint8_t configuration_byte_0x78;
    uint8_t device_identity[20u];
} r1_legacy_device_info_sources;

typedef struct {
    uint8_t bytes[R1_LEGACY_DEVICE_INFO_RESPONSE_MAX];
    size_t length;
} r1_legacy_device_info_response;

r1_error r1_dispatch(r1_device_state *state, r1_session *session,
                     const r1_model *request, r1_dispatch_result *result);
r1_error r1_legacy_command_route_frame(
    const uint8_t *frame, size_t frame_length, uint8_t *workspace,
    size_t workspace_length, r1_legacy_command_route *route);
r1_error r1_factory_legacy_command_route_frame(
    const uint8_t *frame, size_t frame_length, uint8_t *workspace,
    size_t workspace_length, r1_legacy_command_route *route);
r1_error r1_legacy_device_info_build(
    const uint8_t request_prefix[R1_LEGACY_DEVICE_INFO_PREFIX_BYTES],
    const r1_legacy_device_info_sources *sources,
    r1_legacy_device_info_response *response);
r1_error r1_ati_calibration_plan_command(
    uint8_t subcommand, uint8_t argument_0, uint8_t argument_1,
    const r1_ati_calibration_observation *observation,
    r1_ati_calibration_plan *plan);
r1_error r1_touch_switch_handler_plan_decode(
    const uint8_t *payload, size_t payload_length,
    r1_touch_switch_handler_plan *plan);

#endif
