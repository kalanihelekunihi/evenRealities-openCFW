#ifndef R1_GATTS_DATABASE_CORDIO_H
#define R1_GATTS_DATABASE_CORDIO_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef bool (*r1_gatts_write_sink_t)(uint8_t conn_id, uint16_t handle,
    uint8_t uuid_type, uint16_t uuid, uint8_t opcode,
    const uint8_t *data, uint16_t length, bool authorize);
void r1_cordio_gatts_database_bind(void *(*allocate)(size_t),
                                   void (*release)(void *),
                                   r1_gatts_write_sink_t write_sink);

enum { R1_GATTS_DB_OK = 0, R1_GATTS_DB_INVALID = 1,
       R1_GATTS_DB_NO_MEM = 2, R1_GATTS_DB_BAD_STATE = 3 };

typedef struct {
    uint16_t service_handle;
    uint16_t nordic_uuid;
    uint8_t nordic_uuid_type;
    const uint8_t *uuid;
    uint8_t uuid_length;
    uint8_t properties;
    uint8_t read_security;
    uint8_t write_security;
    uint8_t ccc_security;
    uint8_t variable_length;
    uint8_t write_authorize;
    uint16_t max_length;
    uint16_t initial_length;
    const uint8_t *initial_value;
} r1_gatts_characteristic_spec_t;

/* UUID is the 2- or 16-byte little-endian ATT service value. */
uint8_t r1_cordio_gatts_service_add(uint8_t type, const uint8_t *uuid,
                                     uint8_t uuid_length, uint16_t *handle);
uint8_t r1_cordio_gatts_characteristic_add(
    const r1_gatts_characteristic_spec_t *spec, uint16_t *value_handle,
    uint16_t *ccc_handle);
uint8_t r1_cordio_gatts_authorize_reply(uint8_t conn_id,
                                        uint8_t att_status, uint8_t update,
                                        uint16_t offset, const uint8_t *data,
                                        uint16_t length);
void r1_cordio_gatts_clear_pending(uint8_t conn_id);
bool r1_cordio_gatts_hvx_details(uint16_t value_handle, uint16_t *ccc_handle,
                                uint8_t *properties, uint16_t *max_length);
void r1_cordio_gatts_tx_clear(uint8_t conn_id);
bool r1_cordio_gatts_tx_complete(uint8_t conn_id, uint16_t handle,
                                  uint8_t status);

#endif
