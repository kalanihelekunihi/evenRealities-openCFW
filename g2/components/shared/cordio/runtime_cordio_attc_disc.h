/* SPDX-License-Identifier: Apache-2.0 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_ATTC_DISC_H
#define OPEN_CFW_RUNTIME_CORDIO_ATTC_DISC_H

#include <stddef.h>
#include <stdint.h>

#include "runtime_cordio_attc_proc.h"

enum {
    OPEN_CFW_ATTC_DISC_UUID16_LENGTH = 2U,
    OPEN_CFW_ATTC_DISC_UUID128_LENGTH = 16U,
    OPEN_CFW_ATTC_DISC_UUID128 = 0x01U,
    OPEN_CFW_ATTC_DISC_REQUIRED = 0x02U,
    OPEN_CFW_ATTC_DISC_DESCRIPTOR = 0x04U,
    OPEN_CFW_ATTC_DISC_INDEX_NONE = 0xFFU,
    OPEN_CFW_ATTC_DISC_HANDLE_START = 1U,
    OPEN_CFW_ATTC_DISC_HANDLE_MAX = 0xFFFFU,
    OPEN_CFW_ATTC_DISC_PRIMARY_SERVICE_UUID = 0x2800U,
    OPEN_CFW_ATTC_DISC_FIND_FORMAT_UUID16 = 1U,
    OPEN_CFW_ATTC_DISC_FIND_FORMAT_UUID128 = 2U,
    OPEN_CFW_ATTC_DISC_FIND_PAIR_UUID16 = 4U,
    OPEN_CFW_ATTC_DISC_FIND_PAIR_UUID128 = 18U,
    OPEN_CFW_ATTC_DISC_CHAR_PAIR_UUID16 = 7U,
    OPEN_CFW_ATTC_DISC_CHAR_PAIR_UUID128 = 21U,
    OPEN_CFW_ATTC_DISC_INCLUDE_PAIR_UUID16 = 8U,
    OPEN_CFW_ATTC_DISC_INCLUDE_PAIR_UUID128 = 22U,
    OPEN_CFW_ATTC_DISC_EVENT_FIND_INFO = 2U,
    OPEN_CFW_ATTC_DISC_EVENT_FIND_TYPE = 3U,
    OPEN_CFW_ATTC_DISC_EVENT_READ_TYPE = 4U,
    OPEN_CFW_ATTC_DISC_SUCCESS = 0U,
    OPEN_CFW_ATTC_DISC_ERROR_NOT_FOUND = 0x0AU,
    OPEN_CFW_ATTC_DISC_ERROR_INVALID_RESPONSE = 0x73U,
    OPEN_CFW_ATTC_DISC_ERROR_UNDEFINED = 0x75U,
    OPEN_CFW_ATTC_DISC_ERROR_REQUIRED_NOT_FOUND = 0x76U,
    OPEN_CFW_ATTC_DISC_CONTINUING = 0x79U,
};

struct open_cfw_cordio_attc_discovery_characteristic {
    uint8_t *uuid;
    uint8_t settings;
};

struct open_cfw_cordio_attc_discovery_configuration {
    const uint8_t *value;
    uint8_t value_length;
    uint8_t handle_index;
};

struct open_cfw_cordio_attc_discovery_control_block {
    struct open_cfw_cordio_attc_discovery_characteristic **characteristics;
    uint16_t *handles;
    struct open_cfw_cordio_attc_discovery_configuration *configuration;
    uint8_t characteristic_count;
    uint8_t configuration_count;
    uint16_t service_start_handle;
    uint16_t service_end_handle;
    uint8_t characteristic_index;
    uint8_t end_handle_index;
};

#ifndef OPEN_CFW_ATTC_DISC_PRODUCTION
extern uint8_t open_cfw_cordio_attc_discovery_characteristic_uuid[2];
extern uint8_t open_cfw_cordio_attc_discovery_include_uuid[2];
#endif

uint8_t open_cfw_cordio_att_uuid_compare_16_to_128(
    const uint8_t *uuid16, const uint8_t *uuid128
);

uint8_t open_cfw_cordio_attc_discovery_uuid_compare(
    struct open_cfw_cordio_attc_discovery_characteristic *,
    uint8_t *, uint8_t
);
uint8_t open_cfw_cordio_attc_discovery_verify(
    struct open_cfw_cordio_attc_discovery_control_block *
);
uint8_t open_cfw_cordio_attc_discovery_descriptors(
    uint8_t, struct open_cfw_cordio_attc_discovery_control_block *
);
void open_cfw_cordio_attc_discovery_process_descriptor_pair(
    struct open_cfw_cordio_attc_discovery_control_block *, uint8_t, uint8_t *
);
uint8_t open_cfw_cordio_attc_discovery_process_descriptor(
    struct open_cfw_cordio_attc_discovery_control_block *,
    struct open_cfw_cordio_att_event *
);
void open_cfw_cordio_attc_discovery_process_characteristic_declaration(
    struct open_cfw_cordio_attc_discovery_control_block *, uint8_t, uint8_t *
);
uint8_t open_cfw_cordio_attc_discovery_process_characteristic(
    struct open_cfw_cordio_attc_discovery_control_block *,
    struct open_cfw_cordio_att_event *
);
uint8_t open_cfw_cordio_attc_discovery_configuration_next(
    uint8_t, struct open_cfw_cordio_attc_discovery_control_block *
);
void open_cfw_cordio_attc_discovery_process_included_service(
    struct open_cfw_cordio_attc_discovery_control_block *, uint8_t, uint8_t *
);
void open_cfw_cordio_attc_discover_service(
    uint8_t, struct open_cfw_cordio_attc_discovery_control_block *,
    uint8_t, uint8_t *
);
uint8_t open_cfw_cordio_attc_complete_service_discovery(
    struct open_cfw_cordio_attc_discovery_control_block *,
    struct open_cfw_cordio_att_event *
);
void open_cfw_cordio_attc_start_characteristic_discovery(
    uint8_t, struct open_cfw_cordio_attc_discovery_control_block *
);
uint8_t open_cfw_cordio_attc_complete_characteristic_discovery(
    struct open_cfw_cordio_attc_discovery_control_block *,
    struct open_cfw_cordio_att_event *
);
void open_cfw_cordio_attc_start_included_service_discovery(
    uint8_t, struct open_cfw_cordio_attc_discovery_control_block *
);
uint8_t open_cfw_cordio_attc_complete_included_service_discovery(
    struct open_cfw_cordio_attc_discovery_control_block *,
    struct open_cfw_cordio_att_event *
);
uint8_t open_cfw_cordio_attc_start_configuration(
    uint8_t, struct open_cfw_cordio_attc_discovery_control_block *
);
uint8_t open_cfw_cordio_attc_complete_configuration(
    uint8_t, struct open_cfw_cordio_attc_discovery_control_block *
);
uint8_t open_cfw_cordio_attc_resume_configuration(
    uint8_t, struct open_cfw_cordio_attc_discovery_control_block *
);

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(struct open_cfw_cordio_attc_discovery_characteristic)
    == 8U, "G2 ATTC discovery characteristic ABI");
_Static_assert(sizeof(struct open_cfw_cordio_attc_discovery_configuration)
    == 8U, "G2 ATTC discovery configuration ABI");
_Static_assert(sizeof(struct open_cfw_cordio_attc_discovery_control_block)
    == 20U, "G2 ATTC discovery control-block ABI");
_Static_assert(offsetof(struct open_cfw_cordio_attc_discovery_control_block,
    service_start_handle) == 14U, "G2 ATTC discovery service-start offset");
_Static_assert(offsetof(struct open_cfw_cordio_attc_discovery_control_block,
    characteristic_index) == 18U, "G2 ATTC discovery index offset");
#endif

#endif
