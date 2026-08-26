/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Production-routed G2 Cordio ATT client-supported-features implementation.
 * Behavior follows the public Packetcraft r20.05--r20.05c source route while
 * preserving the recovered three-connection G2 control-block ABI.
 */

#include "runtime_cordio_atts_csf.h"

#if !defined(OPEN_CFW_ATTS_CSF_SET_HASH_ONLY) && \
    !defined(OPEN_CFW_ATTS_CSF_GET_HASH_ONLY) && \
    !defined(OPEN_CFW_ATTS_CSF_IS_AWARE_ONLY) && \
    !defined(OPEN_CFW_ATTS_CSF_ACT_STATE_ONLY) && \
    !defined(OPEN_CFW_ATTS_CSF_SET_STATE_ONLY) && \
    !defined(OPEN_CFW_ATTS_CSF_CONN_OPEN_ONLY) && \
    !defined(OPEN_CFW_ATTS_CSF_REGISTER_ONLY) && \
    !defined(OPEN_CFW_ATTS_CSF_WRITE_ONLY) && \
    !defined(OPEN_CFW_ATTS_CSF_GET_FEATURES_ONLY) && \
    !defined(OPEN_CFW_ATTS_CSF_GET_STATE_ONLY)
#define OPEN_CFW_ATTS_CSF_BUILD_ALL 1
#endif

#ifdef OPEN_CFW_ATTS_CSF_PRODUCTION
#define OPEN_CFW_ATTS_CSF_CB \
    (*(struct open_cfw_cordio_atts_csf_control_block *)0x20073E04U)
#else
#define OPEN_CFW_ATTS_CSF_CB open_cfw_cordio_atts_csf_control_block
#endif

#if defined(OPEN_CFW_ATTS_CSF_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_CSF_SET_HASH_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_csf_set_hash_update_status(uint8_t is_updating)
{
    uint8_t index;

    if (OPEN_CFW_ATTS_CSF_CB.is_hash_updating == is_updating) {
        return;
    }
    OPEN_CFW_ATTS_CSF_CB.is_hash_updating = is_updating;
    if (is_updating == 0U) {
        open_cfw_cordio_atts_check_pending_database_hash_read_response();
        return;
    }
    for (index = 0U; index < OPEN_CFW_ATTS_CSF_CONNECTIONS; index++) {
        if (OPEN_CFW_ATTS_CSF_CB.records[index].change_aware_state
            == OPEN_CFW_ATTS_CSF_CHANGE_AWARE_DB_READ_PENDING) {
            OPEN_CFW_ATTS_CSF_CB.records[index].change_aware_state =
                OPEN_CFW_ATTS_CSF_CHANGE_PENDING_AWARE;
        }
    }
}
#endif

#if defined(OPEN_CFW_ATTS_CSF_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_CSF_GET_HASH_ONLY)
__attribute__((used, noinline))
uint8_t open_cfw_cordio_atts_csf_get_hash_update_status(void)
{
    return OPEN_CFW_ATTS_CSF_CB.is_hash_updating;
}
#endif

#if defined(OPEN_CFW_ATTS_CSF_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_CSF_IS_AWARE_ONLY)
__attribute__((used, noinline))
uint8_t open_cfw_cordio_atts_csf_is_client_change_aware(
    uint8_t connection_id,
    uint16_t attribute_handle
)
{
    struct open_cfw_cordio_atts_csf_record *record;

    if (connection_id == 0U) {
        return 0U;
    }
    record = &OPEN_CFW_ATTS_CSF_CB.records[connection_id - 1U];

    if (((record->csf & OPEN_CFW_ATTS_CSF_ROBUST_CACHING) != 0U)
        && (record->change_aware_state == OPEN_CFW_ATTS_CSF_CHANGE_UNAWARE)
        && (attribute_handle
            != OPEN_CFW_ATTS_CSF_GATT_SERVICE_CHANGED_HANDLE)) {
        return 0U;
    }
    return 1U;
}
#endif

#if defined(OPEN_CFW_ATTS_CSF_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_CSF_ACT_STATE_ONLY)
__attribute__((used, noinline))
uint8_t open_cfw_cordio_atts_csf_act_client_state(
    uint16_t connection_index,
    uint8_t opcode,
    uint8_t *packet
)
{
    struct open_cfw_cordio_atts_csf_record *record;
    uint16_t uuid;
    uint8_t error = OPEN_CFW_ATTS_CSF_ATT_SUCCESS;

    if ((opcode == OPEN_CFW_ATTS_CSF_PDU_MTU_REQ)
        || (opcode == OPEN_CFW_ATTS_CSF_PDU_VALUE_CNF)) {
        return error;
    }
    record = &OPEN_CFW_ATTS_CSF_CB.records[connection_index];
    if (record->change_aware_state == OPEN_CFW_ATTS_CSF_CHANGE_UNAWARE) {
        if ((opcode & OPEN_CFW_ATTS_CSF_PDU_COMMAND_MASK) == 0U) {
            record->change_aware_state =
                OPEN_CFW_ATTS_CSF_CHANGE_PENDING_AWARE;
        }
        if (((opcode & OPEN_CFW_ATTS_CSF_PDU_COMMAND_MASK) != 0U)
            || ((record->csf & OPEN_CFW_ATTS_CSF_ROBUST_CACHING) != 0U)) {
            error = OPEN_CFW_ATTS_CSF_ATT_ERR_DATABASE_OUT_OF_SYNC;
        }
    } else if (record->change_aware_state
        == OPEN_CFW_ATTS_CSF_CHANGE_PENDING_AWARE) {
        if ((opcode & OPEN_CFW_ATTS_CSF_PDU_COMMAND_MASK) == 0U) {
            record->change_aware_state = OPEN_CFW_ATTS_CSF_CHANGE_AWARE;
            if (OPEN_CFW_ATTS_CSF_CB.write_callback != NULL) {
                OPEN_CFW_ATTS_CSF_CB.write_callback(
                    (uint8_t)(connection_index + 1U),
                    record->change_aware_state,
                    &record->csf
                );
            }
        } else {
            error = OPEN_CFW_ATTS_CSF_ATT_ERR_DATABASE_OUT_OF_SYNC;
        }
    }
    if (opcode == OPEN_CFW_ATTS_CSF_PDU_READ_TYPE_REQ) {
        uuid = (uint16_t)packet[OPEN_CFW_ATTS_CSF_READ_TYPE_UUID_OFFSET]
            | ((uint16_t)packet[OPEN_CFW_ATTS_CSF_READ_TYPE_UUID_OFFSET + 1U]
                << 8);
        if (uuid == OPEN_CFW_ATTS_CSF_DATABASE_HASH_UUID) {
            error = OPEN_CFW_ATTS_CSF_ATT_SUCCESS;
            if (OPEN_CFW_ATTS_CSF_CB.is_hash_updating != 0U) {
                record->change_aware_state =
                    OPEN_CFW_ATTS_CSF_CHANGE_AWARE_DB_READ_PENDING;
            }
        }
    }
    return error;
}
#endif

#if defined(OPEN_CFW_ATTS_CSF_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_CSF_SET_STATE_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_csf_set_clients_change_awareness_state(
    uint8_t connection_id,
    uint8_t state
)
{
    uint8_t index;

    if (connection_id == 0U) {
        for (index = 0U; index < OPEN_CFW_ATTS_CSF_CONNECTIONS; index++) {
            if (OPEN_CFW_ATTS_CSF_CB.records[index].change_aware_state
                == OPEN_CFW_ATTS_CSF_CHANGE_AWARE_DB_READ_PENDING) {
                OPEN_CFW_ATTS_CSF_CB.records[index].change_aware_state =
                    OPEN_CFW_ATTS_CSF_CHANGE_PENDING_AWARE;
            } else {
                OPEN_CFW_ATTS_CSF_CB.records[index].change_aware_state = state;
            }
        }
    } else {
        OPEN_CFW_ATTS_CSF_CB.records[connection_id - 1U]
            .change_aware_state = state;
    }
}
#endif

#if defined(OPEN_CFW_ATTS_CSF_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_CSF_CONN_OPEN_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_csf_connection_open(
    uint8_t connection_id,
    uint8_t change_aware_state,
    uint8_t *csf
)
{
    struct open_cfw_cordio_atts_csf_record *record;

    if (connection_id == 0U) {
        return;
    }
    record = &OPEN_CFW_ATTS_CSF_CB.records[connection_id - 1U];

    if (csf != NULL) {
        record->change_aware_state = change_aware_state;
        record->csf = csf[0];
    } else {
        record->csf = 0U;
        record->change_aware_state = 0U;
    }
}
#endif

#if defined(OPEN_CFW_ATTS_CSF_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_CSF_REGISTER_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_csf_register(
    open_cfw_cordio_atts_csf_write_callback_t callback
)
{
    OPEN_CFW_ATTS_CSF_CB.write_callback = callback;
}
#endif

#if defined(OPEN_CFW_ATTS_CSF_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_CSF_WRITE_ONLY)
__attribute__((used, noinline))
uint8_t open_cfw_cordio_atts_csf_write_features(
    uint8_t connection_id,
    uint16_t offset,
    uint16_t value_length,
    uint8_t *value
)
{
    struct open_cfw_cordio_atts_csf_record *record;
    uint8_t new_csf;

    (void)offset;
    if (connection_id == 0U) {
        return OPEN_CFW_ATTS_CSF_ATT_ERR_UNLIKELY;
    }
    record = &OPEN_CFW_ATTS_CSF_CB.records[connection_id - 1U];
    if (value_length > 1U) {
        return OPEN_CFW_ATTS_CSF_ATT_ERR_LENGTH;
    }
    new_csf = value[0] & OPEN_CFW_ATTS_CSF_ALL_FEATURES;
    if ((record->csf > 0U) && (new_csf == 0U)) {
        return OPEN_CFW_ATTS_CSF_ATT_ERR_VALUE_NOT_ALLOWED;
    }
    record->csf |= new_csf;
    if (OPEN_CFW_ATTS_CSF_CB.write_callback != NULL) {
        OPEN_CFW_ATTS_CSF_CB.write_callback(
            connection_id,
            record->change_aware_state,
            &record->csf
        );
    }
    return OPEN_CFW_ATTS_CSF_ATT_SUCCESS;
}
#endif

#if defined(OPEN_CFW_ATTS_CSF_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_CSF_GET_FEATURES_ONLY)
__attribute__((used, noinline))
void open_cfw_cordio_atts_csf_get_features(
    uint8_t connection_id,
    uint8_t *output,
    uint8_t output_length
)
{
    if ((connection_id != 0U) && (output_length == 1U)) {
        output[0] = OPEN_CFW_ATTS_CSF_CB.records[connection_id - 1U].csf;
    }
}
#endif

#if defined(OPEN_CFW_ATTS_CSF_BUILD_ALL) || \
    defined(OPEN_CFW_ATTS_CSF_GET_STATE_ONLY)
__attribute__((used, noinline))
uint8_t open_cfw_cordio_atts_csf_get_change_aware_state(
    uint8_t connection_id
)
{
    if (connection_id == 0U) {
        return OPEN_CFW_ATTS_CSF_CHANGE_UNAWARE;
    }
    return OPEN_CFW_ATTS_CSF_CB.records[connection_id - 1U]
        .change_aware_state;
}
#endif
