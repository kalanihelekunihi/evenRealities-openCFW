/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room G2 touch sensing, calibration, gesture, and ACT/ALR/WOT policy.
 * MSCLP register actions are explicit callbacks; this file has no direct
 * hardware, sleep, flash, or reset access.
 */
#include "runtime_touch_sensing.h"

int open_cfw_touch_msc_scan(const uint32_t *descriptors,
                            size_t descriptor_stride_words,
                            size_t channel_count, uint16_t *maximum,
                            const open_cfw_touch_scan_port *port)
{
    size_t channel;
    size_t word;
    uint32_t local[6];
    uint16_t sample;

    if (descriptors == NULL || maximum == NULL || port == NULL ||
        port->program_channel == NULL || port->run_conversion == NULL ||
        port->read_result == NULL || descriptor_stride_words < 6U) {
        return 4;
    }
    *maximum = 0U;
    for (channel = 0U; channel < channel_count; ++channel) {
        for (word = 0U; word < 6U; ++word) {
            local[word] = descriptors[channel * descriptor_stride_words + word];
        }
        local[5] = (local[5] & 0xC000FFCAUL) | 0x00FF0004UL;
        local[3] = 0x00FF0063UL;
        local[4] = 0x00400064UL;
        if (port->program_channel(port->context, local) == 0 ||
            port->run_conversion(port->context, 0x06D9U) == 0) {
            return 4;
        }
        sample = port->read_result(port->context, channel);
        if (sample > *maximum) {
            *maximum = sample;
        }
    }
    return 0;
}

open_cfw_touch_power_state open_cfw_touch_power_transition(
    open_cfw_touch_power_state state, open_cfw_touch_power_event event)
{
    if (state == OPEN_CFW_TOUCH_POWER_ACT &&
        event == OPEN_CFW_TOUCH_POWER_EVENT_INACTIVE) {
        return OPEN_CFW_TOUCH_POWER_ALR;
    }
    if (state == OPEN_CFW_TOUCH_POWER_ALR &&
        event == OPEN_CFW_TOUCH_POWER_EVENT_ALARM_EXPIRED) {
        return OPEN_CFW_TOUCH_POWER_WOT;
    }
    if (state == OPEN_CFW_TOUCH_POWER_WOT &&
        event == OPEN_CFW_TOUCH_POWER_EVENT_TOUCH) {
        return OPEN_CFW_TOUCH_POWER_ACT;
    }
    if (state == OPEN_CFW_TOUCH_POWER_WOT &&
        event == OPEN_CFW_TOUCH_POWER_EVENT_ALERT) {
        return OPEN_CFW_TOUCH_POWER_ALR;
    }
    return state;
}

void open_cfw_touch_gesture_init(open_cfw_touch_gesture_state *state,
                                 uint16_t long_press_ms,
                                 uint16_t swipe_threshold)
{
    if (state == NULL) {
        return;
    }
    state->press_position = 0;
    state->last_position = 0;
    state->press_duration_ms = 0U;
    state->long_press_ms = long_press_ms == 0U ? 1U : long_press_ms;
    state->swipe_threshold = swipe_threshold == 0U ? 1U : swipe_threshold;
    state->fast_clicks = 0U;
    state->pressed = 0U;
}

open_cfw_touch_gesture open_cfw_touch_gesture_press(
    open_cfw_touch_gesture_state *state, int16_t position)
{
    if (state == NULL) {
        return OPEN_CFW_TOUCH_GESTURE_NONE;
    }
    state->press_position = position;
    state->last_position = position;
    state->press_duration_ms = 0U;
    state->pressed = 1U;
    return OPEN_CFW_TOUCH_GESTURE_NONE;
}

open_cfw_touch_gesture open_cfw_touch_gesture_release(
    open_cfw_touch_gesture_state *state, int16_t position,
    uint16_t duration_ms, int fast_click)
{
    int32_t delta;

    if (state == NULL || state->pressed == 0U) {
        return OPEN_CFW_TOUCH_GESTURE_NONE;
    }
    state->pressed = 0U;
    state->last_position = position;
    state->press_duration_ms = duration_ms;
    if (fast_click != 0) {
        if (state->fast_clicks < 5U) {
            ++state->fast_clicks;
        }
        if (state->fast_clicks == 5U) {
            state->fast_clicks = 0U;
            return OPEN_CFW_TOUCH_GESTURE_FIVE_FAST_CLICKS;
        }
    } else {
        state->fast_clicks = 0U;
    }
    if (duration_ms >= state->long_press_ms) {
        return OPEN_CFW_TOUCH_GESTURE_LONG_PRESS;
    }
    delta = (int32_t)position - (int32_t)state->press_position;
    if (delta >= (int32_t)state->swipe_threshold) {
        return OPEN_CFW_TOUCH_GESTURE_RIGHT;
    }
    if (delta <= -(int32_t)state->swipe_threshold) {
        return OPEN_CFW_TOUCH_GESTURE_LEFT;
    }
    return OPEN_CFW_TOUCH_GESTURE_NONE;
}

uint16_t open_cfw_touch_calibration_threshold(uint16_t maximum,
                                              uint16_t baseline,
                                              uint16_t margin)
{
    uint32_t threshold = maximum > baseline ? maximum : baseline;
    threshold += margin;
    return threshold > UINT16_MAX ? UINT16_MAX : (uint16_t)threshold;
}
