#ifndef R1_GAP_SERVICE_H
#define R1_GAP_SERVICE_H

#include <stdbool.h>
#include <stdint.h>

void r1_cordio_gap_service_init(void);
void r1_cordio_gap_service_set_ccc_sink(
    bool (*sink)(uint8_t conn_id, uint16_t handle, uint16_t value));
bool r1_cordio_gap_name_set(const uint8_t *name, uint16_t length);
bool r1_cordio_gap_name_read(uint8_t *destination, uint16_t capacity,
                             uint16_t *actual);
void r1_cordio_gap_appearance_set(uint16_t appearance);
uint16_t r1_cordio_gap_appearance_get(void);
void r1_cordio_gap_ppcp_set(const uint8_t params[8]);
void r1_cordio_gap_ppcp_get(uint8_t params[8]);
bool r1_cordio_ccc_register(uint16_t handle, uint16_t range,
                            uint8_t security_level);
void r1_cordio_ccc_freeze(void);
bool r1_cordio_atts_is_ccc(uint16_t handle);
uint16_t r1_cordio_ccc_enabled(uint8_t conn_id, uint16_t handle);
void r1_cordio_ccc_retain(uint8_t conn_id);
void r1_cordio_ccc_new_connection(uint8_t conn_id);
bool r1_cordio_ccc_export(uint8_t conn_id, bool recent, uint8_t flags,
                          uint8_t *data, uint16_t capacity,
                          uint16_t *actual);
bool r1_cordio_ccc_restore(uint8_t conn_id, uint8_t flags,
                           const uint8_t *data, uint16_t length);
/* Snapshot a Cordio server attribute while its WSF database is locked.
 * Returns 0 on success, 1 if absent, 2 for an offset past the value. */
uint8_t r1_cordio_atts_value_snapshot(uint8_t conn_id, uint16_t handle,
                                      uint16_t offset, uint8_t *destination,
                                      uint16_t capacity, uint16_t *actual);

#endif
