#include "openr1/r1_motion.h"

#include <limits.h>

static bool provider_complete(const r1_motion_provider_ops *provider) {
    return provider != NULL && provider->probe != NULL &&
           provider->configure != NULL && provider->read_fifo != NULL;
}

void r1_ring_stability_initialize(r1_ring_stability_state *state) {
    if (state != NULL) {
        *state = (r1_ring_stability_state){0};
    }
}

static bool raw_float_greater_than_positive(uint32_t raw, uint32_t threshold) {
    return (raw & UINT32_C(0x80000000)) == 0u && raw > threshold;
}

static bool raw_float_less_than_positive(uint32_t raw, uint32_t threshold) {
    return (raw & UINT32_C(0x80000000)) != 0u || raw < threshold;
}

r1_error r1_ring_stability_observe(
    r1_ring_stability_state *state, float smoothed_deviation,
    bool callback_registered, r1_ring_stability_result *result) {
    if (state == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *result = (r1_ring_stability_result){0};
    float *slot = &state->window[state->cursor];
    if (state->sample_count >= R1_RING_STABILITY_WINDOW) {
        state->window_sum -= *slot;
    }
    *slot = smoothed_deviation;
    state->window_sum += smoothed_deviation;
    state->cursor = (uint8_t)((state->cursor + 1u) & 7u);
    if (state->sample_count < R1_RING_STABILITY_WINDOW) {
        state->sample_count += 1u;
    }
    if (state->sample_count < R1_RING_STABILITY_WINDOW) {
        return R1_OK;
    }

    result->evaluated = true;
    const bool previous = state->detected;
    union {
        float value;
        uint32_t raw;
    } bits = {.value = smoothed_deviation};
    const uint32_t raw = bits.raw;
    if (raw_float_greater_than_positive(raw, UINT32_C(0x3d4ccccd))) {
        state->low_motion_count = 0u;
        state->detected = false;
    } else if (raw_float_less_than_positive(raw, UINT32_C(0x3e051eb8))) {
        state->low_motion_count = (uint16_t)(state->low_motion_count + 1u);
        if (state->low_motion_count >= R1_RING_STABILITY_DETECT_COUNT) {
            state->detected = true;
        }
    } else if (state->low_motion_count != 0u) {
        state->low_motion_count -= 1u;
        if (state->low_motion_count == 0u) {
            state->detected = false;
        }
    } else {
        state->detected = false;
    }
    result->state_changed = state->detected != previous;
    result->callback_requested = callback_registered;
    result->detected = state->detected;
    result->low_motion_count = state->low_motion_count;
    return R1_OK;
}

void r1_motion_adapter_initialize(r1_motion_adapter *adapter) {
    if (adapter == NULL) {
        return;
    }
    adapter->lis2dw12.ops = NULL;
    adapter->lis2dw12.context = NULL;
    adapter->bma456w.ops = NULL;
    adapter->bma456w.context = NULL;
    adapter->qma6100.ops = NULL;
    adapter->qma6100.context = NULL;
    adapter->selected = R1_MOTION_VARIANT_NONE;
    adapter->configured_rate_hz = 0u;
    adapter->configured = false;
}

r1_error r1_motion_adapter_bind(r1_motion_adapter *adapter,
                                 r1_motion_variant variant,
                                 const r1_motion_provider_ops *provider,
                                 void *provider_context) {
    if (adapter == NULL || !provider_complete(provider)) {
        return R1_ERROR_ARGUMENT;
    }
    if (adapter->configured) {
        return R1_ERROR_STATE;
    }
    r1_motion_provider *binding = NULL;
    if (variant == R1_MOTION_VARIANT_LIS2DW12) {
        binding = &adapter->lis2dw12;
    } else if (variant == R1_MOTION_VARIANT_BMA456W) {
        binding = &adapter->bma456w;
    } else if (variant == R1_MOTION_VARIANT_QMA6100) {
        binding = &adapter->qma6100;
    } else {
        return R1_ERROR_ARGUMENT;
    }
    binding->ops = provider;
    binding->context = provider_context;
    return R1_OK;
}

static r1_error select_provider(r1_motion_adapter *adapter,
                                r1_motion_provider *provider,
                                r1_motion_variant variant,
                                uint8_t expected_chip_id,
                                uint16_t requested_rate_hz,
                                bool continue_on_probe_failure) {
    if (!provider_complete(provider->ops)) {
        return continue_on_probe_failure ? R1_ERROR_UNSUPPORTED
                                         : R1_ERROR_STATE;
    }
    uint8_t chip_id = 0u;
    const r1_error probe_error =
        provider->ops->probe(provider->context, &chip_id);
    const bool identity_matches = variant == R1_MOTION_VARIANT_QMA6100
        ? (chip_id == R1_MOTION_QMA6100_CHIP_ID ||
           (chip_id & R1_MOTION_QMA6100P_ID_MASK) ==
               R1_MOTION_QMA6100P_ID_VALUE)
        : chip_id == expected_chip_id;
    if (probe_error != R1_OK || !identity_matches) {
        return continue_on_probe_failure ? R1_ERROR_UNSUPPORTED
                                         : (probe_error == R1_OK
                                                ? R1_ERROR_UNSUPPORTED
                                                : probe_error);
    }
    const r1_error configure_error =
        provider->ops->configure(provider->context, requested_rate_hz);
    if (configure_error != R1_OK) {
        return configure_error;
    }
    adapter->selected = variant;
    adapter->configured_rate_hz = requested_rate_hz;
    adapter->configured = true;
    return R1_OK;
}

r1_error r1_motion_adapter_configure(r1_motion_adapter *adapter,
                                      r1_motion_policy policy,
                                      uint16_t requested_rate_hz) {
    if (adapter == NULL || requested_rate_hz == 0u) {
        return R1_ERROR_ARGUMENT;
    }
    if (adapter->configured) {
        return R1_ERROR_STATE;
    }
    if (policy == R1_MOTION_POLICY_DISABLED) {
        return R1_ERROR_UNSUPPORTED;
    }
    if (policy == R1_MOTION_POLICY_FORCE_LIS2DW12) {
        return select_provider(adapter, &adapter->lis2dw12,
                               R1_MOTION_VARIANT_LIS2DW12,
                               R1_MOTION_LIS2DW12_CHIP_ID,
                               requested_rate_hz, false);
    }
    if (policy == R1_MOTION_POLICY_FORCE_BMA456W) {
        return select_provider(adapter, &adapter->bma456w,
                               R1_MOTION_VARIANT_BMA456W,
                               R1_MOTION_BMA456W_CHIP_ID,
                               requested_rate_hz, false);
    }
    if (policy == R1_MOTION_POLICY_FORCE_QMA6100) {
        return select_provider(adapter, &adapter->qma6100,
                               R1_MOTION_VARIANT_QMA6100,
                               R1_MOTION_QMA6100_CHIP_ID,
                               requested_rate_hz, false);
    }
    if (policy != R1_MOTION_POLICY_AUTO_LICENSED) {
        return R1_ERROR_ARGUMENT;
    }

    /* Exact stock priority: LIS2DW12, BMA456W, then QMA6100. */
    r1_error error = select_provider(adapter, &adapter->lis2dw12,
                                     R1_MOTION_VARIANT_LIS2DW12,
                                     R1_MOTION_LIS2DW12_CHIP_ID,
                                     requested_rate_hz, true);
    if (error == R1_OK) {
        return R1_OK;
    }
    if (error != R1_ERROR_UNSUPPORTED) {
        return error;
    }
    error = select_provider(adapter, &adapter->bma456w,
                            R1_MOTION_VARIANT_BMA456W,
                            R1_MOTION_BMA456W_CHIP_ID,
                            requested_rate_hz, true);
    if (error == R1_OK) {
        return R1_OK;
    }
    if (error != R1_ERROR_UNSUPPORTED) {
        return error;
    }
    return select_provider(adapter, &adapter->qma6100,
                           R1_MOTION_VARIANT_QMA6100,
                           R1_MOTION_QMA6100_CHIP_ID,
                           requested_rate_hz, true);
}

int16_t r1_motion_normalize_axis(int16_t raw_axis) {
    const int32_t value = raw_axis;
    if (value >= 0) {
        return (int16_t)(value / 4);
    }
    /* Match the Cortex-M arithmetic shift (round toward negative infinity)
     * without relying on implementation-defined signed right shift in C. */
    return (int16_t)(-(((-value) + 3) / 4));
}

static r1_motion_provider *selected_provider(r1_motion_adapter *adapter) {
    if (adapter->selected == R1_MOTION_VARIANT_LIS2DW12) {
        return &adapter->lis2dw12;
    }
    if (adapter->selected == R1_MOTION_VARIANT_BMA456W) {
        return &adapter->bma456w;
    }
    if (adapter->selected == R1_MOTION_VARIANT_QMA6100) {
        return &adapter->qma6100;
    }
    return NULL;
}

r1_error r1_motion_adapter_read_fifo(r1_motion_adapter *adapter,
                                      r1_motion_sample *samples,
                                      size_t capacity,
                                      size_t *sample_count) {
    if (adapter == NULL || samples == NULL || capacity == 0u ||
        sample_count == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *sample_count = 0u;
    if (!adapter->configured) {
        return R1_ERROR_STATE;
    }
    r1_motion_provider *provider = selected_provider(adapter);
    if (provider == NULL || !provider_complete(provider->ops)) {
        return R1_ERROR_UNSUPPORTED;
    }
    const size_t limit = capacity < R1_MOTION_FIFO_SAMPLE_LIMIT
        ? capacity : R1_MOTION_FIFO_SAMPLE_LIMIT;
    uint8_t raw[R1_MOTION_FIFO_SAMPLE_LIMIT * R1_MOTION_SAMPLE_BYTES];
    size_t count = 0u;
    const r1_error error = provider->ops->read_fifo(
        provider->context, raw, limit, &count);
    if (error != R1_OK) {
        return error;
    }
    if (count > limit) {
        return R1_ERROR_CAPACITY;
    }
    for (size_t index = 0u; index < count; ++index) {
        const size_t offset = index * R1_MOTION_SAMPLE_BYTES;
        const int16_t x = (int16_t)((uint16_t)raw[offset] |
                                    ((uint16_t)raw[offset + 1u] << 8u));
        const int16_t y = (int16_t)((uint16_t)raw[offset + 2u] |
                                    ((uint16_t)raw[offset + 3u] << 8u));
        const int16_t z = (int16_t)((uint16_t)raw[offset + 4u] |
                                    ((uint16_t)raw[offset + 5u] << 8u));
        samples[index].x = r1_motion_normalize_axis(x);
        samples[index].y = r1_motion_normalize_axis(y);
        samples[index].z = r1_motion_normalize_axis(z);
    }
    *sample_count = count;
    return R1_OK;
}

r1_error r1_motion_adapter_disable_double_tap(r1_motion_adapter *adapter) {
    if (adapter == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (!adapter->configured) {
        return R1_ERROR_STATE;
    }
    r1_motion_provider *provider = selected_provider(adapter);
    if (provider == NULL || provider->ops == NULL ||
        provider->ops->disable_double_tap == NULL) {
        return R1_ERROR_UNSUPPORTED;
    }
    return provider->ops->disable_double_tap(provider->context);
}

r1_motion_variant r1_motion_adapter_selected(const r1_motion_adapter *adapter) {
    return adapter == NULL ? R1_MOTION_VARIANT_NONE : adapter->selected;
}
