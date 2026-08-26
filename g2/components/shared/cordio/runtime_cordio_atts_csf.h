/* SPDX-License-Identifier: Apache-2.0 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_ATTS_CSF_H
#define OPEN_CFW_RUNTIME_CORDIO_ATTS_CSF_H

#include <stddef.h>
#include <stdint.h>

enum {
    OPEN_CFW_ATTS_CSF_CONNECTIONS = 3U,
    OPEN_CFW_ATTS_CSF_ROBUST_CACHING = 0x01U,
    OPEN_CFW_ATTS_CSF_ALL_FEATURES = 0x07U,
    OPEN_CFW_ATTS_CSF_CHANGE_AWARE = 0U,
    OPEN_CFW_ATTS_CSF_CHANGE_PENDING_AWARE = 1U,
    OPEN_CFW_ATTS_CSF_CHANGE_AWARE_DB_READ_PENDING = 2U,
    OPEN_CFW_ATTS_CSF_CHANGE_UNAWARE = 3U,
    OPEN_CFW_ATTS_CSF_ATT_SUCCESS = 0x00U,
    OPEN_CFW_ATTS_CSF_ATT_ERR_LENGTH = 0x0DU,
    OPEN_CFW_ATTS_CSF_ATT_ERR_UNLIKELY = 0x0EU,
    OPEN_CFW_ATTS_CSF_ATT_ERR_DATABASE_OUT_OF_SYNC = 0x12U,
    OPEN_CFW_ATTS_CSF_ATT_ERR_VALUE_NOT_ALLOWED = 0x13U,
    OPEN_CFW_ATTS_CSF_PDU_MTU_REQ = 0x02U,
    OPEN_CFW_ATTS_CSF_PDU_READ_TYPE_REQ = 0x08U,
    OPEN_CFW_ATTS_CSF_PDU_VALUE_CNF = 0x1EU,
    OPEN_CFW_ATTS_CSF_PDU_COMMAND_MASK = 0x40U,
    OPEN_CFW_ATTS_CSF_GATT_SERVICE_CHANGED_HANDLE = 0x12U,
    OPEN_CFW_ATTS_CSF_DATABASE_HASH_UUID = 0x2B2AU,
    OPEN_CFW_ATTS_CSF_READ_TYPE_UUID_OFFSET = 13U
};

struct open_cfw_cordio_atts_csf_record {
    uint8_t csf;
    uint8_t change_aware_state;
};

typedef void (*open_cfw_cordio_atts_csf_write_callback_t)(
    uint8_t connection_id,
    uint8_t change_aware_state,
    uint8_t *csf
);

struct open_cfw_cordio_atts_csf_control_block {
    struct open_cfw_cordio_atts_csf_record records[
        OPEN_CFW_ATTS_CSF_CONNECTIONS
    ];
    uint8_t reserved[2];
    open_cfw_cordio_atts_csf_write_callback_t write_callback;
    uint8_t is_hash_updating;
};

extern struct open_cfw_cordio_atts_csf_control_block
    open_cfw_cordio_atts_csf_control_block;

void open_cfw_cordio_atts_check_pending_database_hash_read_response(void);

void open_cfw_cordio_atts_csf_set_hash_update_status(uint8_t is_updating);
uint8_t open_cfw_cordio_atts_csf_get_hash_update_status(void);
uint8_t open_cfw_cordio_atts_csf_is_client_change_aware(
    uint8_t connection_id,
    uint16_t attribute_handle
);
uint8_t open_cfw_cordio_atts_csf_act_client_state(
    uint16_t connection_index,
    uint8_t opcode,
    uint8_t *packet
);
void open_cfw_cordio_atts_csf_set_clients_change_awareness_state(
    uint8_t connection_id,
    uint8_t state
);
void open_cfw_cordio_atts_csf_connection_open(
    uint8_t connection_id,
    uint8_t change_aware_state,
    uint8_t *csf
);
void open_cfw_cordio_atts_csf_register(
    open_cfw_cordio_atts_csf_write_callback_t callback
);
uint8_t open_cfw_cordio_atts_csf_write_features(
    uint8_t connection_id,
    uint16_t offset,
    uint16_t value_length,
    uint8_t *value
);
void open_cfw_cordio_atts_csf_get_features(
    uint8_t connection_id,
    uint8_t *output,
    uint8_t output_length
);
uint8_t open_cfw_cordio_atts_csf_get_change_aware_state(
    uint8_t connection_id
);

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(
    sizeof(struct open_cfw_cordio_atts_csf_record) == 2U,
    "G2 ATTS CSF record size"
);
_Static_assert(
    offsetof(struct open_cfw_cordio_atts_csf_control_block, write_callback)
        == 8U,
    "G2 ATTS CSF callback offset"
);
_Static_assert(
    offsetof(struct open_cfw_cordio_atts_csf_control_block, is_hash_updating)
        == 12U,
    "G2 ATTS CSF hash-update offset"
);
#endif

#endif
