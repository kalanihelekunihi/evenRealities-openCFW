#ifndef OPENR1_R1_MOTION_H
#define OPENR1_R1_MOTION_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_protocol.h"

/*
 * Product-side motion-provider selector and sample normalizer.
 *
 * Bosch and ST register behavior remains in the pinned upstream drivers.
 * This boundary owns only the recovered R1 probe order, accepted identities,
 * six-byte sample bound, requested-rate policy, and the common arithmetic
 * right shift applied by the stock BMA456W and LIS2DW12 wrappers.
 */
#define R1_MOTION_BMA456W_CHIP_ID UINT8_C(0x16)
#define R1_MOTION_LIS2DW12_CHIP_ID UINT8_C(0x44)
#define R1_MOTION_SAMPLE_BYTES 6u
#define R1_MOTION_FIFO_SAMPLE_LIMIT 31u

typedef enum {
    R1_MOTION_VARIANT_NONE = 0,
    R1_MOTION_VARIANT_LIS2DW12,
    R1_MOTION_VARIANT_BMA456W
} r1_motion_variant;

typedef enum {
    R1_MOTION_POLICY_DISABLED = 0,
    R1_MOTION_POLICY_AUTO_LICENSED,
    R1_MOTION_POLICY_FORCE_LIS2DW12,
    R1_MOTION_POLICY_FORCE_BMA456W
} r1_motion_policy;

typedef struct {
    int16_t x;
    int16_t y;
    int16_t z;
} r1_motion_sample;

typedef struct {
    r1_error (*probe)(void *context, uint8_t *chip_id);
    r1_error (*configure)(void *context, uint16_t requested_rate_hz);
    r1_error (*read_fifo)(void *context, uint8_t *raw_samples,
                          size_t maximum_samples, size_t *sample_count);
    r1_error (*disable_double_tap)(void *context);
} r1_motion_provider_ops;

typedef struct {
    const r1_motion_provider_ops *ops;
    void *context;
} r1_motion_provider;

typedef struct {
    r1_motion_provider lis2dw12;
    r1_motion_provider bma456w;
    r1_motion_variant selected;
    uint16_t configured_rate_hz;
    bool configured;
} r1_motion_adapter;

void r1_motion_adapter_initialize(r1_motion_adapter *adapter);
r1_error r1_motion_adapter_bind(r1_motion_adapter *adapter,
                                 r1_motion_variant variant,
                                 const r1_motion_provider_ops *provider,
                                 void *provider_context);
r1_error r1_motion_adapter_configure(r1_motion_adapter *adapter,
                                      r1_motion_policy policy,
                                      uint16_t requested_rate_hz);
r1_error r1_motion_adapter_read_fifo(r1_motion_adapter *adapter,
                                      r1_motion_sample *samples,
                                      size_t capacity,
                                      size_t *sample_count);
r1_error r1_motion_adapter_disable_double_tap(r1_motion_adapter *adapter);
r1_motion_variant r1_motion_adapter_selected(const r1_motion_adapter *adapter);
int16_t r1_motion_normalize_axis(int16_t raw_axis);

#endif
