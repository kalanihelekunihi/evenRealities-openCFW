#include "openr1/r1_wear.h"

#define R1_WEAR_MOTION_ON_VARIANCE 2000.0f
#define R1_WEAR_STATIONARY_VARIANCE 40.0f
#define R1_WEAR_GRAVITY_MEAN_MINIMUM 972.0f
#define R1_WEAR_GRAVITY_MEAN_MAXIMUM 1076.0f

void r1_wear_fusion_initialize(r1_wear_fusion *fusion) {
    if (fusion == NULL) {
        return;
    }
    fusion->state = R1_WEAR_FUSION_NOT_WORN;
    fusion->low_ir_decisions = 0u;
    fusion->stationary_decisions = 0u;
}

r1_error r1_wear_motion_statistics_compute(
    const r1_motion_sample *samples, size_t sample_count,
    r1_wear_motion_statistics *statistics) {
    if (samples == NULL || statistics == NULL ||
        sample_count < R1_WEAR_MINIMUM_MOTION_SAMPLES) {
        return R1_ERROR_ARGUMENT;
    }

    float sum_x = 0.0f;
    float sum_y = 0.0f;
    float sum_z = 0.0f;
    for (size_t index = 0u; index < sample_count; ++index) {
        sum_x += (float)samples[index].x;
        sum_y += (float)samples[index].y;
        sum_z += (float)samples[index].z;
    }
    const float count = (float)sample_count;
    statistics->mean_x = sum_x / count;
    statistics->mean_y = sum_y / count;
    statistics->mean_z = sum_z / count;

    float squared_x = 0.0f;
    float squared_y = 0.0f;
    float squared_z = 0.0f;
    for (size_t index = 0u; index < sample_count; ++index) {
        const float delta_x = (float)samples[index].x - statistics->mean_x;
        const float delta_y = (float)samples[index].y - statistics->mean_y;
        const float delta_z = (float)samples[index].z - statistics->mean_z;
        squared_x += delta_x * delta_x;
        squared_y += delta_y * delta_y;
        squared_z += delta_z * delta_z;
    }
    statistics->variance_x = squared_x / count;
    statistics->variance_y = squared_y / count;
    statistics->variance_z = squared_z / count;
    return R1_OK;
}

r1_error r1_wear_optical_range(
    const uint32_t *history, size_t history_count,
    bool previous_available, uint32_t previous,
    uint32_t *range) {
    if (range == NULL || history_count > R1_WEAR_IR_HISTORY_CAPACITY ||
        (history_count != 0u && history == NULL) ||
        (history_count == 0u && !previous_available)) {
        return R1_ERROR_ARGUMENT;
    }

    uint32_t minimum;
    uint32_t maximum;
    size_t index = 0u;
    if (history_count != 0u) {
        minimum = history[0];
        maximum = history[0];
        index = 1u;
    } else {
        minimum = previous;
        maximum = previous;
    }
    for (; index < history_count; ++index) {
        if (history[index] < minimum) {
            minimum = history[index];
        }
        if (history[index] > maximum) {
            maximum = history[index];
        }
    }
    if (previous_available) {
        if (previous < minimum) {
            minimum = previous;
        }
        if (previous > maximum) {
            maximum = previous;
        }
    }
    *range = maximum - minimum;
    return R1_OK;
}

r1_error r1_wear_optical_history_update(
    r1_wear_optical_history *history,
    const uint32_t *values, size_t value_count) {
    if (history == NULL ||
        history->count > R1_WEAR_IR_HISTORY_CAPACITY ||
        value_count > R1_WEAR_IR_HISTORY_CAPACITY ||
        (value_count != 0u && values == NULL)) {
        return R1_ERROR_ARGUMENT;
    }

    if (history->count != 0u) {
        history->previous = history->values[history->count - 1u];
        /* The recovered range helper treats a zero previous sample as absent. */
        history->previous_available = history->previous != 0u;
    }
    history->count = (uint8_t)value_count;
    for (size_t index = 0u; index < value_count; ++index) {
        history->values[index] = values[index];
    }
    return R1_OK;
}

void r1_wear_raw_hr_probe_plan(
    bool subscription_active, bool timeout_active,
    r1_wear_probe_plan *plan) {
    if (plan == NULL) {
        return;
    }
    *plan = (r1_wear_probe_plan){
        .subscribe_raw_hr = !subscription_active,
        .raw_hr_timeout = timeout_active
            ? R1_WEAR_TIMEOUT_RESTART : R1_WEAR_TIMEOUT_START,
    };
}

void r1_wear_adt_status_plan(
    uint8_t status, bool charging, bool subscription_active,
    bool timeout_active, r1_wear_probe_plan *plan) {
    if (plan == NULL) {
        return;
    }
    *plan = (r1_wear_probe_plan){0};
    if (charging || status == 1u) {
        plan->teardown_probe = true;
        return;
    }
    if (status == 0u && !subscription_active) {
        plan->subscribe_adt = true;
        plan->start_adt_timeout = !timeout_active;
    }
}

bool r1_wear_sleep_status_update(
    uint8_t *current_status, uint8_t new_status,
    uint8_t *pending_decision) {
    if (current_status == NULL || pending_decision == NULL) {
        return false;
    }
    const bool cleared = new_status == 1u && *current_status == 0u;
    if (cleared) {
        *pending_decision = 0u;
    }
    *current_status = new_status;
    return cleared;
}

static bool motion_exceeds_wear_on_threshold(
    const r1_wear_motion_statistics *motion) {
    return motion != NULL &&
        (motion->variance_x > R1_WEAR_MOTION_ON_VARIANCE ||
         motion->variance_y > R1_WEAR_MOTION_ON_VARIANCE ||
         motion->variance_z > R1_WEAR_MOTION_ON_VARIANCE);
}

r1_wear_action r1_wear_fusion_observe_on(
    r1_wear_fusion *fusion, const r1_wear_on_observation *observation) {
    if (fusion == NULL || observation == NULL ||
        fusion->state != R1_WEAR_FUSION_NOT_WORN) {
        return R1_WEAR_ACTION_NONE;
    }

    bool suspected = false;
    if (observation->optical_history_available) {
        const bool range_qualified = !observation->optical_baseline_available ||
            observation->optical_range >= R1_WEAR_IR_RANGE_MINIMUM;
        suspected = range_qualified &&
            observation->optical_latest > R1_WEAR_IR_THRESHOLD;
    } else {
        suspected = motion_exceeds_wear_on_threshold(observation->motion);
    }
    if (!suspected) {
        return R1_WEAR_ACTION_NONE;
    }
    fusion->state = R1_WEAR_FUSION_SUSPECTED_WORN;
    fusion->low_ir_decisions = 0u;
    fusion->stationary_decisions = 0u;
    return R1_WEAR_ACTION_STATE_CHANGED;
}

static bool stationary_table_candidate(
    const r1_wear_motion_statistics *motion) {
    if (motion == NULL) {
        return false;
    }
    const float absolute_mean_y = motion->mean_y < 0.0f
        ? -motion->mean_y : motion->mean_y;
    return absolute_mean_y > R1_WEAR_GRAVITY_MEAN_MINIMUM &&
        absolute_mean_y < R1_WEAR_GRAVITY_MEAN_MAXIMUM &&
        motion->variance_x < R1_WEAR_STATIONARY_VARIANCE &&
        motion->variance_y < R1_WEAR_STATIONARY_VARIANCE &&
        motion->variance_z < R1_WEAR_STATIONARY_VARIANCE;
}

static r1_wear_action clear_or_preserve_suspected(
    r1_wear_fusion *fusion, uint8_t sleep_status) {
    fusion->low_ir_decisions = 0u;
    fusion->stationary_decisions = 0u;
    if (sleep_status == 1u) {
        return R1_WEAR_ACTION_NONE;
    }
    fusion->state = R1_WEAR_FUSION_NOT_WORN;
    return (r1_wear_action)(R1_WEAR_ACTION_STOP_LIVING_PROBE |
                            R1_WEAR_ACTION_STATE_CHANGED);
}

r1_wear_action r1_wear_fusion_observe_off(
    r1_wear_fusion *fusion, const r1_wear_off_observation *observation) {
    if (fusion == NULL || observation == NULL ||
        fusion->state != R1_WEAR_FUSION_SUSPECTED_WORN) {
        return R1_WEAR_ACTION_NONE;
    }

    const uint32_t elapsed = observation->current_tick -
        observation->living_tick;
    if (elapsed <= R1_WEAR_LIVING_WINDOW_TICKS) {
        fusion->state = observation->living_status == 1u
            ? R1_WEAR_FUSION_LIVING_CONFIRMED
            : R1_WEAR_FUSION_NOT_WORN;
        fusion->low_ir_decisions = 0u;
        fusion->stationary_decisions = 0u;
        return (r1_wear_action)(R1_WEAR_ACTION_STOP_LIVING_PROBE |
                                R1_WEAR_ACTION_STATE_CHANGED);
    }

    r1_wear_action action = observation->living_probe_active
        ? R1_WEAR_ACTION_NONE : R1_WEAR_ACTION_START_LIVING_PROBE;

    if (observation->optical_history_available &&
        observation->optical_latest < R1_WEAR_IR_THRESHOLD) {
        if (fusion->low_ir_decisions < R1_WEAR_LOW_IR_DECISIONS) {
            ++fusion->low_ir_decisions;
        }
        if (fusion->low_ir_decisions >= R1_WEAR_LOW_IR_DECISIONS) {
            const r1_wear_action transition = clear_or_preserve_suspected(
                fusion, observation->sleep_status);
            if ((transition & R1_WEAR_ACTION_STOP_LIVING_PROBE) != 0) {
                action = transition;
            }
            return (r1_wear_action)(action | transition);
        }
    } else {
        fusion->low_ir_decisions = 0u;
    }

    if (stationary_table_candidate(observation->motion)) {
        if (fusion->stationary_decisions < R1_WEAR_STATIONARY_DECISIONS) {
            ++fusion->stationary_decisions;
        }
        if (fusion->stationary_decisions >= R1_WEAR_STATIONARY_DECISIONS) {
            const r1_wear_action transition = clear_or_preserve_suspected(
                fusion, observation->sleep_status);
            if ((transition & R1_WEAR_ACTION_STOP_LIVING_PROBE) != 0) {
                action = transition;
            }
            return (r1_wear_action)(action | transition);
        }
    } else {
        fusion->stationary_decisions = 0u;
    }
    return action;
}

bool r1_wear_fusion_is_confirmed(const r1_wear_fusion *fusion) {
    return fusion != NULL &&
        fusion->state == R1_WEAR_FUSION_LIVING_CONFIRMED;
}

r1_wear_state r1_wear_notification_state(r1_wear_fusion_state state) {
    return state == R1_WEAR_FUSION_NOT_WORN
        ? R1_WEAR_NOT_WORN : R1_WEAR_WORN;
}

r1_wear_state r1_wear_explicit_query_state(r1_wear_fusion_state state) {
    if (state == R1_WEAR_FUSION_NOT_WORN) {
        return R1_WEAR_NOT_WORN;
    }
    if (state == R1_WEAR_FUSION_SUSPECTED_WORN) {
        return R1_WEAR_WORN;
    }
    return R1_WEAR_UNKNOWN;
}
