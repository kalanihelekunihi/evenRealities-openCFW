#ifndef OPENR1_R1_NV_RECOVERY_H
#define OPENR1_R1_NV_RECOVERY_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_protocol.h"

#define R1_NV_RECOVERY_BODY_BYTES 116u
#define R1_NV_RECOVERY_CONFIG_BYTES 124u
#define R1_NV_RECOVERY_POWER_BYTES 4u

#define R1_NV_RECOVERY_CHANGED_CONFIG UINT8_C(0x01)
#define R1_NV_RECOVERY_CHANGED_POWER UINT8_C(0x02)
#define R1_NV_RECOVERY_CHANGED_RING_SIZE UINT8_C(0x04)

/*
 * Product-owned state split across the recovered nv_r1, power, and r_size
 * records. This API plans bounded internal recovery only. The normal BLE
 * nvRecover command remains deliberately unavailable.
 */
typedef struct {
    uint8_t config[R1_NV_RECOVERY_CONFIG_BYTES];
    uint8_t power[R1_NV_RECOVERY_POWER_BYTES];
    uint8_t ring_size;
} r1_nv_recovery_state;

typedef struct {
    r1_nv_recovery_state state;
    uint8_t changed_records;
} r1_nv_recovery_result;

bool r1_nv_recovery_build_body(
    const r1_nv_recovery_state *state,
    uint8_t body[R1_NV_RECOVERY_BODY_BYTES]);

r1_error r1_nv_recovery_merge(
    const r1_nv_recovery_state *current,
    const uint8_t *body,
    size_t body_length,
    uint16_t expected_crc,
    r1_nv_recovery_result *result);

#endif
