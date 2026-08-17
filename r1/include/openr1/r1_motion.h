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
#define R1_MOTION_QMA6100_CHIP_ID UINT8_C(0xFA)
#define R1_MOTION_QMA6100P_ID_MASK UINT8_C(0xF0)
#define R1_MOTION_QMA6100P_ID_VALUE UINT8_C(0x90)
#define R1_MOTION_SAMPLE_BYTES 6u
#define R1_MOTION_FIFO_SAMPLE_LIMIT 31u
#define R1_MOTION_BATCH_SAMPLE_LIMIT 30u
#define R1_MOTION_BATCH_SAMPLES_BYTES \
    (R1_MOTION_BATCH_SAMPLE_LIMIT * R1_MOTION_SAMPLE_BYTES)
#define R1_MOTION_BATCH_COUNT_OFFSET R1_MOTION_BATCH_SAMPLES_BYTES
#define R1_MOTION_BATCH_RESERVED_OFFSET 182u
#define R1_MOTION_BATCH_TIMESTAMP_OFFSET 184u
#define R1_MOTION_BATCH_BYTES 188u
#define R1_RING_STABILITY_WINDOW 8u
#define R1_RING_STABILITY_DETECT_COUNT 600u

typedef enum {
    R1_MOTION_VARIANT_NONE = 0,
    R1_MOTION_VARIANT_LIS2DW12,
    R1_MOTION_VARIANT_BMA456W,
    R1_MOTION_VARIANT_QMA6100
} r1_motion_variant;

typedef enum {
    R1_MOTION_POLICY_DISABLED = 0,
    R1_MOTION_POLICY_AUTO_LICENSED,
    R1_MOTION_POLICY_FORCE_LIS2DW12,
    R1_MOTION_POLICY_FORCE_BMA456W,
    R1_MOTION_POLICY_FORCE_QMA6100
} r1_motion_policy;

typedef struct {
    int16_t x;
    int16_t y;
    int16_t z;
} r1_motion_sample;

typedef struct {
    int16_t x;
    int16_t y;
    int16_t z;
} r1_motion_axis_calibration;

typedef struct {
    uint8_t axis_enabled[3];
    uint8_t threshold[3];
    uint8_t duration;
    uint8_t quiet;
    uint8_t shock;
    uint8_t tap_mode;
    uint8_t int1_route_set_mask;
    uint8_t return_value;
} r1_lis2dw12_double_tap_enable_plan;

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
    r1_motion_provider qma6100;
    r1_motion_variant selected;
    uint16_t configured_rate_hz;
    bool configured;
} r1_motion_adapter;

typedef struct {
    float window[R1_RING_STABILITY_WINDOW];
    float window_sum;
    uint8_t cursor;
    uint16_t sample_count;
    uint16_t low_motion_count;
    bool detected;
} r1_ring_stability_state;

typedef struct {
    bool evaluated;
    bool state_changed;
    bool callback_requested;
    bool detected;
    uint16_t low_motion_count;
} r1_ring_stability_result;

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
r1_lis2dw12_double_tap_enable_plan
r1_lis2dw12_double_tap_enable_plan_build(void);
r1_motion_variant r1_motion_adapter_selected(const r1_motion_adapter *adapter);
int16_t r1_motion_normalize_axis(int16_t raw_axis);
r1_error r1_motion_batch_encode(
    const r1_motion_sample *samples, size_t sample_count,
    const r1_motion_axis_calibration *calibration,
    bool calibration_in_progress, uint32_t timestamp_ticks,
    uint8_t *destination, size_t destination_length);
void r1_ring_stability_initialize(r1_ring_stability_state *state);
r1_error r1_ring_stability_observe(
    r1_ring_stability_state *state, float smoothed_deviation,
    bool callback_registered, r1_ring_stability_result *result);

#endif
