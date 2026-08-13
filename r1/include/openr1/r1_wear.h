#ifndef OPENR1_R1_WEAR_H
#define OPENR1_R1_WEAR_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_motion.h"
#include "openr1/r1_state.h"

/*
 * Clean-room R1 wear-fusion policy.
 *
 * Motion and optical samples are supplied by provider adapters.  This module
 * deliberately does not subscribe to a sensor topic, operate a Goodix
 * algorithm, or own a timer.  It returns requested lifecycle actions to the
 * platform integration layer instead.
 */
#define R1_WEAR_MINIMUM_MOTION_SAMPLES 10u
#define R1_WEAR_IR_HISTORY_CAPACITY 5u
#define R1_WEAR_IR_RANGE_MINIMUM UINT32_C(100000)
#define R1_WEAR_IR_THRESHOLD UINT32_C(9050000)
#define R1_WEAR_LIVING_WINDOW_TICKS UINT32_C(0x800)
#define R1_WEAR_LOW_IR_DECISIONS 5u
#define R1_WEAR_STATIONARY_DECISIONS 60u

typedef enum {
    R1_WEAR_FUSION_NOT_WORN = 0,
    R1_WEAR_FUSION_SUSPECTED_WORN = 1,
    R1_WEAR_FUSION_LIVING_CONFIRMED = 2
} r1_wear_fusion_state;

typedef struct {
    float mean_x;
    float mean_y;
    float mean_z;
    float variance_x;
    float variance_y;
    float variance_z;
} r1_wear_motion_statistics;

typedef enum {
    R1_WEAR_ACTION_NONE = 0,
    R1_WEAR_ACTION_START_LIVING_PROBE = 1u << 0,
    R1_WEAR_ACTION_STOP_LIVING_PROBE = 1u << 1,
    R1_WEAR_ACTION_STATE_CHANGED = 1u << 2
} r1_wear_action;

typedef struct {
    r1_wear_fusion_state state;
    uint8_t low_ir_decisions;
    uint8_t stationary_decisions;
} r1_wear_fusion;

typedef struct {
    bool optical_history_available;
    bool optical_baseline_available;
    uint32_t optical_latest;
    uint32_t optical_range;
    const r1_wear_motion_statistics *motion;
} r1_wear_on_observation;

typedef struct {
    uint32_t current_tick;
    uint32_t living_tick;
    uint8_t living_status;
    uint8_t sleep_status;
    bool living_probe_active;
    bool optical_history_available;
    uint32_t optical_latest;
    const r1_wear_motion_statistics *motion;
} r1_wear_off_observation;

void r1_wear_fusion_initialize(r1_wear_fusion *fusion);
r1_error r1_wear_motion_statistics_compute(
    const r1_motion_sample *samples, size_t sample_count,
    r1_wear_motion_statistics *statistics);
r1_error r1_wear_optical_range(
    const uint32_t *history, size_t history_count,
    bool previous_available, uint32_t previous,
    uint32_t *range);
r1_wear_action r1_wear_fusion_observe_on(
    r1_wear_fusion *fusion, const r1_wear_on_observation *observation);
r1_wear_action r1_wear_fusion_observe_off(
    r1_wear_fusion *fusion, const r1_wear_off_observation *observation);
bool r1_wear_fusion_is_confirmed(const r1_wear_fusion *fusion);
r1_wear_state r1_wear_notification_state(r1_wear_fusion_state state);
r1_wear_state r1_wear_explicit_query_state(r1_wear_fusion_state state);

#endif
